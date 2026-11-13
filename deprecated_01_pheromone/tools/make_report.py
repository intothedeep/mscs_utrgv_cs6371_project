"""Stage reports and the summary page from saved outputs only.

Usage: make_report.py --phase mvp1 | mvp2 | mvp3   (stages of mvp2, mvp3: report_mvp2.py, report_mvp3.py)
Reads manifests, check_log.txt, analyze_log.txt, summary.csv and g2_stats.csv.
No number is typed here. A stage with no saved output is reported as skipped and
the script goes on.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import schema as S  # noqa: E402
from analyze import LOG_FILE, STATS_FILE, SUMMARY_FILE, load_runs  # noqa: E402
from report_html import Stage, index_page, stage_page, table  # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent
RUNS_ROOT = PROJECT / "mock" / "runs"
RESULTS = PROJECT / "results" / "mock"
OUT = RESULTS / "mvp1"
CHECK_LOG = RESULTS / "check_log.txt"
CHART = "g2_recovered_share_MOCK.png"
BAR_COLORS = ("#4c78a8", "#f58518")
NAN = float("nan")
MAX_FAIL_ROWS = 50


# ---- pure helpers ----------------------------------------------------------------

def num(v: float, digits: int = 2) -> str:
    return "n/a" if v != v else f"{v:.{digits}f}"


def interval(lo: float, hi: float) -> str:
    return f"[{num(lo)}, {num(hi)}]"


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else NAN


def parse_check_log(text: str) -> tuple[tuple[int, int, int] | None, list[list[str]]]:
    summary = re.search(r"^SUMMARY runs=(\d+) failed=(\d+) problems=(\d+)$", text, re.M)
    fails = [list(m.groups()) for m in re.finditer(
        r"^FAIL run=(\S+) file=(\S+) column=(\S+): (.*)$", text, re.M)]
    return (tuple(map(int, summary.groups())) if summary else None), fails  # type: ignore[arg-type]


def cell_means(runs: list[dict]) -> dict[tuple[int, int], tuple[int, float, float]]:
    cells: dict = defaultdict(list)
    for r in runs:
        cells[(r["d"], r["defense"])].append(r)
    return {k: (len(v), mean([r["food"] for r in v]), mean([r["wasted"] for r in v]))
            for k, v in sorted(cells.items())}


def generate_verdict(means: dict, wasted_d0_max: float) -> str:
    off = [means[(d, 0)][1] for d in S.DETRACTOR_COUNTS if (d, 0) in means]
    gains = [means[(d, 1)][1] - means[(d, 0)][1] for d in S.DETRACTOR_COUNTS
             if d > 0 and (d, 0) in means and (d, 1) in means]
    bad = []
    if any(b >= a for a, b in zip(off, off[1:])):
        bad.append("food does not fall as d grows")
    if any(g <= 0 for g in gains):
        bad.append("defense gains nothing at some d")
    if wasted_d0_max != 0:
        bad.append("wasted robot-seconds is not 0 at d = 0")
    if bad:
        return "Bad: " + ", ".join(bad) + ". The mock chart may be empty."
    return "Good: loss grows with d and defense wins part back. Wasted time is 0 at d = 0."


# ---- figures ---------------------------------------------------------------------

def bar_figure(path: Path, title: str, labels: list[str], series: dict[str, list[float]],
               xlabel: str, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 4.2), layout="constrained")
    width = 0.8 / len(series)
    for k, (name, vals) in enumerate(series.items()):
        xs = [i + (k - (len(series) - 1) / 2) * width for i in range(len(labels))]
        ax.bar(xs, vals, width=width, color=BAR_COLORS[k % len(BAR_COLORS)], label=name)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if len(series) > 1:  # legend below the axes, clear of the title
        fig.legend(loc="outside lower center", ncol=len(series))
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---- stages ----------------------------------------------------------------------

def skipped(key: str, title: str, what: str, why: str, reason: str) -> Stage:
    return Stage(key, title, what, why, "none", "none", "none", "none",
                 f"skipped: {reason}", "", "")


def img(src: str, alt: str) -> str:
    return f'<img src="{src}" alt="{alt}">'


def generate_stage() -> Stage:
    n_cells = len(S.DETRACTOR_COUNTS) * len(S.DEFENSES) * len(S.SEEDS)
    what = f"Write {n_cells} MOCK runs (fake data) that follow the log schema."
    why = ("Milestone M1 shows the shape and the flow on mock data first. "
           "That serves goals G1 and G2 before any real pipeline exists.")
    key, title = "generate", "Stage 1: generate mock runs"
    try:
        runs = load_runs(RUNS_ROOT)
    except SystemExit as err:
        return Stage(key, title, what, why, "none", "none", "none", "none",
                     f"failed: {err}", "", "")
    if not runs:
        return skipped(key, title, what, why, f"no run folder under {RUNS_ROOT.relative_to(PROJECT)}")
    means = cell_means(runs)
    files = [p for p in RUNS_ROOT.glob("*/*") if p.is_file()]
    megabytes = sum(p.stat().st_size for p in files) / 1e6
    wasted_d0 = max([r["wasted"] for r in runs if r["d"] == 0], default=NAN)
    foods = [m[1] for m in means.values()]
    OUT.mkdir(parents=True, exist_ok=True)
    labels = [f"d = {d}" for d in S.DETRACTOR_COUNTS]
    bar_figure(OUT / "generate_fig.png", "MOCK DATA: mean food collected per cell", labels,
               {f"defense {'on' if f else 'off'}": [means.get((d, f), (0, NAN, NAN))[1]
                                                    for d in S.DETRACTOR_COUNTS]
                for f in S.DEFENSES},
               "detractors added to the 20 honest robots (d)", "mean food_collected")
    rows = [[str(d), "on" if f else "off", str(n), num(food, 1), num(wasted, 1)]
            for (d, f), (n, food, wasted) in means.items()]
    return Stage(
        key, title, what, why,
        "No input data. Every value is generated (fake) by tools/make_mock_runs.py.",
        f"{len(runs)} run folders under mock/runs/. {len(files)} files, {megabytes:.1f} MB.",
        f"Mean food_collected per cell runs from {num(min(foods), 1)} to {num(max(foods), 1)}. "
        f"Largest wasted_robot_seconds at d = 0: {num(wasted_d0, 1)}.",
        generate_verdict(means, wasted_d0), f"ran ({len(runs)} runs found)",
        img("generate_fig.png", "Mean food per cell, MOCK DATA"),
        table(["d", "defense", "runs", "mean food_collected", "mean wasted_robot_seconds"], rows))


def check_stage() -> Stage:
    what = "Check every mock run against the schema in tools/schema.py."
    why = ("A renamed column or a missing file must stop the flow here. "
           "Milestone M1 needs the check to pass on the mock runs.")
    key, title = "check", "Stage 2: check the runs"
    if not CHECK_LOG.is_file():
        return skipped(key, title, what, why, f"{CHECK_LOG.relative_to(PROJECT)} not found. "
                       "Run check_runs.py with --log first")
    text = CHECK_LOG.read_text()
    summary, fails = parse_check_log(text)
    if summary is None:
        return Stage(key, title, what, why, "none", "none", "none", "none",
                     "failed: the check log has no SUMMARY line", "", "")
    runs, failed, problems = summary
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "check_fig.png", "MOCK DATA: schema check per run", ["passed", "failed"],
               {"runs": [runs - failed, failed]}, "check result", "number of runs")
    rows = fails[:MAX_FAIL_ROWS] or [["none", "", "", "no problem found"]]
    verdict = ("Good: every run passes the check." if problems == 0 else
               f"Bad: {failed} runs fail. First problem: {' '.join(fails[0])}.")
    return Stage(
        key, title, what, why, f"{runs} run folders under mock/runs/ (generated, fake).",
        f"{CHECK_LOG.relative_to(PROJECT)}, {len(text.splitlines())} lines.",
        f"runs {runs}, failed {failed}, problems {problems}.", verdict, "ran",
        img("check_fig.png", "Runs passed and failed"),
        table(["run", "file", "column", "message"], rows))


def read_stats(path: Path) -> list[dict]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def analyze_stage() -> Stage:
    what = "Compute the recovered loss share R(d) with 95 % intervals and draw the G2 chart."
    why = ("Goal G2 is this chart. On mock data it shows that the flow and the "
           "numbers fit together.")
    key, title = "analyze", "Stage 3: analyze and draw the G2 chart"
    needed = [RESULTS / n for n in (STATS_FILE, SUMMARY_FILE, LOG_FILE, CHART)]
    absent = [p.name for p in needed if not p.is_file()]
    if absent:
        return skipped(key, title, what, why,
                       f"{', '.join(absent)} not found in {RESULTS.relative_to(PROJECT)}. "
                       "Run analyze.py first")
    stats = read_stats(RESULTS / STATS_FILE)
    n_runs = len(read_stats(RESULTS / SUMMARY_FILE))
    log = (RESULTS / LOG_FILE).read_text()
    cells = re.search(r"^CELLS expected=(\d+) present=(\d+) missing=(\d+)", log, re.M)
    by_d = {int(r["d"]): r for r in stats}
    parts, rows, unresolved = [], [], []
    for d in S.DETRACTOR_COUNTS:
        r = by_d.get(d)
        if r is None:
            continue
        f = {k: (float(v) if k not in ("resolved", "note") else v) for k, v in r.items()}
        rows.append([str(d), r["n_seeds"], num(f["f_off"], 1), num(f["f_on"], 1),
                     f"{num(f['loss'])} {interval(f['loss_lo'], f['loss_hi'])}",
                     f"{num(f['gain'])} {interval(f['gain_lo'], f['gain_hi'])}",
                     f"{num(f['share'])} {interval(f['share_lo'], f['share_hi'])}", r["note"]])
        if d == 0:
            parts.append(f"defense cost F(0, on) - F(0, off) = {num(f['gain'])}")
        elif r["resolved"] == "True":
            parts.append(f"R({d}) = {num(f['share'])} {interval(f['share_lo'], f['share_hi'])}")
        else:
            unresolved.append(d)
            parts.append(f"R({d}) not reported ({r['note']})")
    verdict = ("Good: the loss is resolved at every d > 0, so R(d) has intervals."
               if not unresolved else
               f"Bad: R(d) is missing for d = {', '.join(map(str, unresolved))}.")
    present = f"{cells.group(2)} of {cells.group(1)} cells" if cells else "cells unknown"
    return Stage(
        key, title, what, why,
        f"{n_runs} manifests from mock/runs/ ({present}). Generated (fake) data.",
        f"{SUMMARY_FILE} ({n_runs} rows), {STATS_FILE}, {CHART}, {LOG_FILE}.",
        "; ".join(parts) + ".", verdict, "ran",
        img(f"../{CHART}", "G2 recovered loss share, MOCK DATA"),
        table(["d", "seeds", "F(d, off)", "F(d, on)", "loss L(d) [95 %]",
               "gain G(d) [95 %]", "share R(d) [95 %]", "note"], rows))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phase", required=True, choices=["mvp1", "mvp2", "mvp3"])
    args = ap.parse_args(argv)
    if args.phase == "mvp2":
        from report_mvp2 import run_phase  # late import: report_mvp2 uses helpers from this file
        return run_phase()
    if args.phase == "mvp3":
        from report_mvp3 import run_phase as run_mvp3
        return run_mvp3()
    OUT.mkdir(parents=True, exist_ok=True)
    stages = [generate_stage(), check_stage(), analyze_stage()]
    for i, s in enumerate(stages, 1):
        (OUT / f"{s.key}.html").write_text(stage_page(s, i, len(stages)))
    ran = sum(1 for s in stages if s.status.startswith("ran"))
    intro = (f"Milestone M1 (minimum viable product 1) runs every stage on mock data. "
             f"{ran} of {len(stages)} stages ran. All numbers come from saved outputs.")
    extras = [(CHART, f"../{CHART}"), (SUMMARY_FILE, f"../{SUMMARY_FILE}"),
              (STATS_FILE, f"../{STATS_FILE}")]
    (OUT / "index.html").write_text(index_page("MVP1 summary: mock end to end", intro, stages, extras))
    print("\n".join(f"{s.key}: {s.status}" for s in stages))
    print(f"wrote {OUT / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
