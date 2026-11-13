"""One report per stage and one index page, from saved outputs only (rules/answering.md 3).

Usage: report.py --phase mvp1
Reads: manifests under mock/runs, results/mock/runs.csv, results/mock/mvp1/check.log
(check_runs.py --log), results/mock/S3 (analyze.py outputs), results/mock/bench/bench.csv.
Writes: results/mock/mvp1/index.html, stage_<n>_<name>_MOCK.html, fig_stage_<name>_MOCK.png.
A stage whose saved output is absent is reported as skipped with the reason. The script goes on.
No number is typed here. Every number is read from a saved file.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from html import escape
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt

import analyze
import report_html as H
import run_io
import schema as S
from plot_style import SERIES_COLOR, title_of

PROJECT = Path(__file__).resolve().parent.parent
THEME = PROJECT.parents[1] / ".claude" / "skills" / "html-theme" / "theme.css"
PHASE_KIND = {"mvp1": S.KIND_MOCK}
EVAL_SET = "S3"
SUMMARY = re.compile(r"SUMMARY runs=(\d+) failed=(\d+) problems=(\d+)")
MISSING = re.compile(r"SUMMARY .*missing=(\d+)")


@dataclass
class Stage:
    key: str
    title: str
    what: str
    why: str
    status: str = "ran"          # ran or skipped
    reason: str = ""
    input: str = ""
    output: str = ""
    result: list[str] = field(default_factory=list)
    note: str = ""               # one line: what was good or bad in the output
    table: tuple[list[str], list[list[str]], str] | None = None   # header, rows, caption
    figure: tuple[str, str] | None = None                          # path from the page, caption


@dataclass
class Paths:
    phase: str
    kind: str
    suffix: str

    @property
    def runs(self) -> Path:
        return PROJECT / self.kind / "runs"

    @property
    def results(self) -> Path:
        return PROJECT / "results" / self.kind

    @property
    def out(self) -> Path:
        return self.results / self.phase

    def eval_file(self, stem: str, ext: str) -> Path:
        return self.results / EVAL_SET / f"{stem}{self.suffix}.{ext}"


def skipped(key: str, title: str, what: str, why: str, reason: str) -> Stage:
    return Stage(key, title, what, why, status="skipped", reason=reason)


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT))


def num(row: dict[str, str], column: str, spec: str) -> str:
    """One saved cell formatted. An empty cell (no S1 runs for the noise line) shows n/a."""
    return format(float(row[column]), spec) if row[column] != "" else "n/a"


def expected_runs(sets: set[str]) -> dict[tuple[str, str], int]:
    """Runs per (set, arm) that schema.SET_CELLS fixes, for the sets that exist."""
    return {(s, arm): len(S.DISTRIBUTIONS) * len(S.SET_CELLS[s][1])
            for s in sorted(sets) if s in S.SET_CELLS for arm in S.SET_CELLS[s][0]}


def bar_figure(labels: list[str], values: list[float], ylabel: str, title: str, path: Path,
               is_mock: bool) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.6), layout="constrained")
    bars = ax.bar(labels, values, color=SERIES_COLOR, edgecolor="black", linewidth=0.4)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v, f"{v:g}", ha="center", va="bottom", fontsize=8)
    ax.set_ylim(0, max(values + [1]) * 1.18)
    ax.set_ylabel(ylabel)
    ax.set_title(title_of(title, is_mock))
    fig.savefig(path)
    plt.close(fig)


# ---- stage readers ---------------------------------------------------------------

def stage_mock_runs(p: Paths) -> Stage:
    what = "Write fake runs in the real run layout."
    why = "M1 exit 1: the flow needs input before any real pipeline exists (MVP ladder)."
    if not p.runs.is_dir():
        return skipped("mock_runs", "Mock runs", what, why, f"{rel(p.runs)} does not exist")
    manifests = [run_io.read_manifest(d) for d in run_io.find_run_dirs(p.runs)]
    counts = Counter((m[S.K.set], m[S.K.arm]) for m in manifests)
    want = expected_runs({s for s, _ in counts})
    rows = [[s, a, str(n), str(want.get((s, a), 0))] for (s, a), n in sorted(counts.items())]
    n_mock = sum(m[S.K.mock] == 1 for m in manifests)
    n_bad = sum(r[2] != r[3] for r in rows) + (n_mock != len(manifests))
    fig = p.out / "fig_stage_mock_runs_MOCK.png"
    p.out.mkdir(parents=True, exist_ok=True)
    bar_figure([f"{s} {a}" for (s, a) in sorted(counts)], [counts[k] for k in sorted(counts)],
               "Runs on disk", "Runs per set and arm", fig, True)
    return Stage(
        "mock_runs", "Mock runs", what, why,
        input="No input data. The generator invents every value (generated, not simulated).",
        output=f"{len(manifests)} run folders under {rel(p.runs)}, {len(S.RUN_FILES)} files each.",
        result=[f"{len(manifests)} runs, {n_mock} with mock = 1."],
        note=("Good: every set and arm has the run count that schema.SET_CELLS fixes."
              if not n_bad else f"Bad: {n_bad} set, arm or mock flag differs from schema."),
        table=([S.C.set, S.C.arm, "runs", "expected"], rows, "Runs on disk against the expected count."),
        figure=(fig.name, f"Runs per set and arm. Why: a missing run would break the paired "
                f"analysis. Source: {rel(p.runs)}"))


def stage_check(p: Paths) -> Stage:
    what = "Check every run folder against the schema."
    why = "M1 exit 2: no later stage may read a run that breaks the contract."
    log = p.out / "check.log"
    if not log.is_file():
        return skipped("check", "Run check", what, why,
                       f"{rel(log)} is absent. Run check_runs.py with --log {rel(log)}")
    lines = log.read_text().splitlines()
    m = SUMMARY.search(log.read_text())
    if m is None:
        return skipped("check", "Run check", what, why, f"{rel(log)} has no SUMMARY line")
    runs, failed, problems = map(int, m.groups())
    fig = p.out / "fig_stage_check_MOCK.png"
    p.out.mkdir(parents=True, exist_ok=True)
    bar_figure(["passed", "failed"], [runs - failed, failed], "Runs", "Run check result", fig, True)
    fails = [ln for ln in lines if ln.startswith("FAIL")][:5]
    return Stage(
        "check", "Run check", what, why,
        input=f"{runs} run folders (generated, mock).", output=f"Log {rel(log)}.",
        result=[f"{runs - failed} of {runs} runs passed, {problems} problems."],
        note=("Good: no run breaks the schema." if problems == 0
              else f"Bad: {failed} runs fail. First lines are in the table."),
        table=(["log line"], [[ln] for ln in (fails or ["no FAIL line"])],
               "Failure lines of the check (first 5)."),
        figure=(fig.name, f"Runs that passed and failed the check. Why: the analysis trusts "
                f"only checked runs. Source: {rel(log.parent)}"))


def stage_collect(p: Paths) -> Stage:
    what = "Collect one runs.csv row per run."
    why = "M1 exit 3: runs.csv is the single source of every number in the report."
    path = p.results / "runs.csv"
    if not path.is_file():
        return skipped("collect", "Collect runs.csv", what, why, f"{rel(path)} does not exist")
    rows = analyze.read_runs(path)
    header = list(rows[0]) if rows else []
    by_key: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        by_key.setdefault((r[S.C.set], r[S.C.arm]), []).append(float(r[S.C.collected]))
    want = expected_runs({s for s, _ in by_key})
    table_rows = [[s, a, str(len(v)), str(want.get((s, a), 0)), f"{sum(v) / len(v):.1f}"]
                  for (s, a), v in sorted(by_key.items())]
    fig = p.out / "fig_stage_collect_MOCK.png"
    p.out.mkdir(parents=True, exist_ok=True)
    keys = sorted(by_key)
    bar_figure([f"{s} {a}" for s, a in keys], [round(sum(by_key[k]) / len(by_key[k]), 1) for k in keys],
               "Mean items collected", "Mean collected per set and arm", fig, True)
    same_header = tuple(header) == S.RUNS_COLUMNS
    return Stage(
        "collect", "Collect runs.csv", what, why,
        input=f"{len(rows)} run rows read from run folders (generated, mock).",
        output=f"{rel(path)}, {len(rows)} rows, {len(header)} columns.",
        result=[f"{len(rows)} rows. The header {'equals' if same_header else 'differs from'} "
                "schema.RUNS_COLUMNS."],
        note=("Good: the header matches the schema and every cell count matches."
              if same_header and all(r[2] == r[3] for r in table_rows)
              else "Bad: the header or a cell count differs from the schema."),
        table=([S.C.set, S.C.arm, "rows", "expected", "mean collected"], table_rows,
               "Rows per set and arm, and the mean of collected."),
        figure=(fig.name, f"Mean items collected per set and arm. Why: a wrong mean here would "
                f"carry into every verdict. Source: {rel(path.parent)}"))


def stage_analyze(p: Paths) -> Stage:
    what = f"Compare qmap with cpfa on set {EVAL_SET}, paired by seed, one verdict per distribution."
    why = "M1 exit 4: proves the statistics and the verdict rule run end to end."
    needed = [p.eval_file("improvement", "csv"), p.eval_file("verdict", "json"),
              p.eval_file("analyze_log", "txt"), p.eval_file("fig_boxplot_3dist", "png")]
    absent = [rel(f) for f in needed if not f.is_file()]
    if absent:
        return skipped("analyze", "Analysis", what, why, "saved output absent: " + ", ".join(absent))
    with needed[0].open(newline="") as fh:
        imp = list(csv.DictReader(fh))
    log = needed[2].read_text()
    words = Counter(r["verdict"] for r in imp)
    miss = MISSING.search(log)
    n_missing = int(miss[1]) if miss else None
    rows = [[r[S.C.distribution], r["n_pairs"], f"{num(r, 'improvement_pct', '+.1f')} %",
             f"[{num(r, 'ci_low', '+.1f')}, {num(r, 'ci_high', '+.1f')}]", r["verdict"],
             num(r, "wilcoxon_p", ".1e"), num(r, "holm_p", ".1e"), num(r, "detectable_diff", ".1f")]
            for r in imp]
    verdict_words = ", ".join(f"{w} {n}" for w, n in sorted(words.items()))
    note = (f"Good: all 3 verdict words appear ({verdict_words})." if len(words) == 3
            else f"Bad: {len(words)} verdict words appear ({verdict_words}).")
    note += f" Missing cells: {n_missing if n_missing is not None else 'unknown'}."
    return Stage(
        "analyze", "Analysis", what, why,
        input=f"{rel(p.results / 'runs.csv')}, set {EVAL_SET}: {sum(int(r['n_pairs']) for r in imp)} "
              "pairs (generated, mock).",
        output="improvement, verdict, log and 3 figures under " + rel(needed[0].parent) + ".",
        result=[f"{r[S.C.distribution]}: {r['verdict']}, {num(r, 'improvement_pct', '+.1f')} % "
                f"[{num(r, 'ci_low', '+.1f')}, {num(r, 'ci_high', '+.1f')}]" for r in imp],
        note=note,
        table=([S.C.distribution, "pairs", "improvement", "95 % interval", "verdict",
                "Wilcoxon p", "Holm p", "detectable (items)"], rows,
               "The 3 verdicts are separate, one per distribution. "
               "Wilcoxon p, Holm p and detectable size never enter "
               "the verdict."),
        figure=(f"../{EVAL_SET}/{needed[3].name}",
                "Items collected per distribution, qmap against cpfa, with improvement and 95 % "
                "interval above each pair. Why: the verdict rule reads exactly this interval. "
                f"Source: {rel(needed[0].parent)}"))


def stage_cost(p: Paths) -> Stage:
    what = "Chart query cost against arena size."
    why = "M2: the benchmark answers goal G1 (server cost stays small as arenas grow)."
    bench = p.results / "bench" / "bench.csv"
    if not bench.is_file():
        return skipped("cost_vs_arena", "Cost against arena size", what, why,
                       f"{rel(bench)} does not exist (benchmark not built yet)")
    return skipped("cost_vs_arena", "Cost against arena size", what, why,
                   f"{rel(bench)} exists but no chart reader is built in MVP1")


STAGES = {"mvp1": (stage_mock_runs, stage_check, stage_collect, stage_analyze, stage_cost)}


# ---- pages -----------------------------------------------------------------------

def stage_page(n: int, s: Stage, theme: str, is_mock: bool) -> str:
    fields = [("What", s.what), ("Why", s.why), ("Input data", s.input or "none"),
              ("Output data", s.output or "none"), ("Result", " | ".join(s.result) or "none"),
              ("Result note", s.note or "none"),
              ("Status", s.status + (f": {s.reason}" if s.reason else ""))]
    lead = s.note if s.status == "ran" else f"Skipped. {s.reason}"
    body = [f"<p><b>{escape(lead)}</b></p>",
            H.table(["field", "value"], [[k, v] for k, v in fields], f"Stage {n} report.", (0, 1))]
    if s.figure:
        body.append(H.figure(s.figure[0], s.figure[1], s.title))
    if s.table:
        header, rows, caption = s.table
        body.append(H.table(header, rows, caption, text_cols=tuple(range(len(header)))
                            if len(header) == 1 else ()))
    return H.page(f"Stage {n}: {s.title}", theme, "\n".join(body), is_mock)


def index_page(stages: list[tuple[Stage, str]], phase: str, theme: str, is_mock: bool) -> str:
    rows = [[str(i), f'<a href="{name}">{escape(s.title)}</a>', s.status,
             s.note if s.status == "ran" else s.reason] for i, (s, name) in enumerate(stages, 1)]
    body = [H.table(["stage", "report", "status", "result note"], rows,
                    f"Stage reports of phase {phase}.", text_cols=(3,), raw_cols=(1,))]
    return H.page(f"Minimum viable product 1 (MVP1): stage reports ({phase})", theme,
                  "\n".join(body), is_mock)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phase", required=True, choices=sorted(PHASE_KIND))
    args = ap.parse_args(argv)
    if not THEME.is_file():
        print(f"refused: theme file {THEME} is missing")
        return 1
    kind = PHASE_KIND[args.phase]
    is_mock = kind == S.KIND_MOCK
    p = Paths(args.phase, kind, analyze.MOCK_SUFFIX if is_mock else "")
    theme = THEME.read_text()
    p.out.mkdir(parents=True, exist_ok=True)
    done: list[tuple[Stage, str]] = []
    for n, reader in enumerate(STAGES[args.phase], 1):
        stage = reader(p)
        name = f"stage_{n}_{stage.key}{p.suffix}.html"
        (p.out / name).write_text(stage_page(n, stage, theme, is_mock))
        done.append((stage, name))
        print(f"stage {n} {stage.key}: {stage.status}" + (f" ({stage.reason})" if stage.reason else ""))
    (p.out / "index.html").write_text(index_page(done, args.phase, theme, is_mock))
    print(f"wrote {len(done)} stage reports and {rel(p.out / 'index.html')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
