"""MVP3 stage reports and the results page: make_report.py --phase mvp3 (M3-07).

Saved outputs only: manifests, CSVs, logs, defense_pick.json, frames. No number is typed
here. A stage with no saved output is reported as skipped and the script goes on.
Also writes results/index.html (G1, G2, links) and results/README.md (every file in results/).
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from html import escape

import schema as S
from analyze import LOG_FILE, STATS_FILE, SUMMARY_FILE, load_runs
from cell_report import EVENTS_FILE, NOTES
from make_report import bar_figure, img, interval, num, parse_check_log, read_stats, skipped
from report_html import Stage, index_page, page, stage_page, table
from report_mvp2 import failed, safe
from run_results import PROJECT, load_manifests

__all__ = ["run_phase"]

RESULTS_ALL = PROJECT / "results"
RESULTS = RESULTS_ALL / "real"
OUT = RESULTS / "mvp3"
DEMO = OUT / "demo"
RUNS = PROJECT / "runs"
CHECK_LOG = RESULTS / "check_sweep_log.txt"
DEFENSE_PICK = RESULTS / "defense_tuning" / "defense_pick.json"
CHART = "g2_recovered_share.png"
CELL_CHARTS = ("food_by_cell.png", "wasted_by_cell.png")
TOTAL_RUNS = len(S.DETRACTOR_COUNTS) * len(S.DEFENSES) * len(S.SEEDS)  # 80, from the schema
DEFENSE_NAMES = ("r_suspect", "alpha_cone_deg", "d_cone", "t_end")


def event_counts(folder_name: str, root_name: str) -> Counter:
    with (RUNS / root_name / folder_name / S.EVENTS_FILE).open(newline="") as fh:
        return Counter(r[S.COL_EVENT] for r in csv.DictReader(fh))


def smoke_stage() -> Stage:
    key, title = "smoke", "Stage 1: detractor smoke run"
    what = "One run at d = 2, defense on, seed 1, headless."
    why = "Detractors and the defense must run before any tuning or sweep (M3 exit 1)."
    found = [m for m in load_manifests(RUNS / "smoke")
             if (m[S.K_PARAMS][S.P_NDET], m[S.K_PARAMS][S.P_DEFENSE]) == (2, 1)]
    if not found:
        return skipped(key, title, what, why, "no run with d = 2 and defense on under runs/smoke/")
    m = sorted(found, key=lambda x: x[S.K_RUNID])[-1]
    ev, met = event_counts(m[S.K_RUNID], "smoke"), m[S.K_METRICS]
    names = ("decoy_reach", "suspect_add", "cone_abort", "pickup", "drop")
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "smoke_fig.png", "Events in the smoke run", list(names), {"events": [ev[n] for n in names]},
               "event", "count")
    bad = [n for n in ("decoy_reach", "suspect_add") if ev[n] == 0]
    return Stage(key, title, what, why, "Generated .argos file, d = 2, defense on, seed 1.",
                 f"runs/smoke/{m[S.K_RUNID]}/ (4 files).",
                 f"food_collected {met[S.M_FOOD]}, wasted_robot_seconds {num(met[S.M_WASTED], 1)}, "
                 + ", ".join(f"{n} {ev[n]}" for n in names[:3]) + ".",
                 "Good: decoy_reach and suspect_add rows exist." if not bad else f"Bad: no {', '.join(bad)} row.",
                 "ran", img("smoke_fig.png", "Smoke events"),
                 table(["runid", "complete", *names], [[m[S.K_RUNID], str(met[S.M_COMPLETE]), *(str(ev[n]) for n in names)]]))


def defense_tuning_stage() -> Stage:
    key, title = "defense_tuning", "Stage 2: defense tuning (D-011)"
    what = "Up to 3 rounds at d = 2, defense on, seeds 101 to 103. Pick the round with the highest mean food."
    why = "The defense values freeze before the 80-run sweep. Tuning on sweep seeds would fit the result."
    if not DEFENSE_PICK.is_file():
        return skipped(key, title, what, why, "results/real/defense_tuning/defense_pick.json not found")
    pick = json.loads(DEFENSE_PICK.read_text())
    rounds = pick["rounds"]
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "defense_tuning_fig.png", "Mean food_collected per defense round", [f"round {r['round']}" for r in rounds],
               {"mean food": [r["mean_food"] for r in rounds]}, "round", "mean F(2, on), 3 seeds")
    rows = [[str(r["round"]), *(f"{r[n]:g}" for n in DEFENSE_NAMES),
             ", ".join(f"{s}: {f}" for s, f in r["food_by_seed"].items()), num(r["mean_food"])] for r in rounds]
    picked = ", ".join(f"{n} {pick[n]:g}" for n in DEFENSE_NAMES)
    return Stage(key, title, what, why, "Real runs, d = 2, defense on, seeds 101 to 103 (runs/defense_tuning/).",
                 "results/real/defense_tuning/defense_pick.json.", f"picked round {pick['picked_round']}: {picked}.",
                 "Bad: no round beat round 1 (D-011 failure condition)." if pick["picked_round"] == 1 and len(rounds) > 1
                 else f"Good: round {pick['picked_round']} has the highest mean.",
                 "ran", img("defense_tuning_fig.png", "Mean food per round"),
                 table(["round", *DEFENSE_NAMES, "food by seed", "mean food"], rows))


def sweep_stage() -> Stage:
    key, title = "sweep", "Stage 3: the 80-run sweep (G1)"
    what = "make_sweep.py --sweep --run: d 0, 1, 2, 4 x defense off, on x seeds 1 to 10, one core."
    why = "Goal G1 needs 80 logged runs with food collected and wasted robot-seconds."
    runs = load_runs(RUNS / "sweep") if (RUNS / "sweep").is_dir() else []
    if not runs:
        return skipped(key, title, what, why, "no run under runs/sweep/")
    done = {(r["d"], r["defense"], r["seed"]) for r in runs if r["complete"] is True}
    rows, per_cell = [], []
    for d in S.DETRACTOR_COUNTS:
        for f in S.DEFENSES:
            n = sum(1 for k in done if k[:2] == (d, f))
            per_cell.append(n)
            rows.append([str(d), "on" if f else "off", f"{n} of {len(S.SEEDS)}"])
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "sweep_fig.png", "Complete runs per cell", [f"d={d} {'on' if f else 'off'}" for d in S.DETRACTOR_COUNTS
                                                                for f in S.DEFENSES], {"complete runs": per_cell},
               "cell (d, defense)", "complete runs of 10")
    return Stage(key, title, what, why, "Frozen values from tuning_pick.json and defense_pick.json.",
                 f"{len(runs)} run folders under runs/sweep/.", f"{len(done)} of {TOTAL_RUNS} cells have a complete run.",
                 "Good: all cells complete." if len(done) == TOTAL_RUNS else f"Bad: {TOTAL_RUNS - len(done)} cells lack a complete run.",
                 "ran", img("sweep_fig.png", "Complete runs per cell"), table(["d", "defense", "complete runs"], rows))


def check_stage() -> Stage:
    key, title = "check", "Stage 4: check the sweep"
    what = "check_runs.py checks every run of runs/sweep/ against tools/schema.py."
    why = "G1 counts only runs that pass the same schema the mock used."
    if not CHECK_LOG.is_file():
        return skipped(key, title, what, why, f"{CHECK_LOG.relative_to(PROJECT)} not found. Run check_runs.py with --log")
    text = CHECK_LOG.read_text()
    summary, fails = parse_check_log(text)
    if summary is None:
        return failed(key, title, what, why, "the check log has no SUMMARY line")
    runs, bad, problems = summary
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "check_fig.png", "Schema check per run", ["passed", "failed"], {"runs": [runs - bad, bad]},
               "check result", "number of runs")
    rows = fails[:50] or [["none", "", "", "no problem found"]]
    return Stage(key, title, what, why, f"{runs} run folders under runs/sweep/.", f"{CHECK_LOG.relative_to(PROJECT)}.",
                 f"runs {runs}, failed {bad}, problems {problems}.",
                 "Good: every run passes." if problems == 0 else f"Bad: first problem {' '.join(fails[0])}.",
                 "ran", img("check_fig.png", "Runs passed and failed"), table(["run", "file", "column", "message"], rows))


def analyze_stage() -> Stage:
    key, title = "analyze", "Stage 5: analyze (G2)"
    what = "analyze.py computes R(d) with 95 % intervals, per-cell charts and event counts."
    why = "Goal G2 is the recovered loss share. The cell charts show where the loss and the gain come from."
    needed = [RESULTS / n for n in (SUMMARY_FILE, STATS_FILE, LOG_FILE, CHART, EVENTS_FILE, *CELL_CHARTS)]
    absent = [p.name for p in needed if not p.is_file()]
    if absent:
        return skipped(key, title, what, why, f"{', '.join(absent)} not found in results/real/. Run analyze.py first")
    stats = read_stats(RESULTS / STATS_FILE)
    cells = re.search(r"^CELLS expected=(\d+) present=(\d+) missing=(\d+)", (RESULTS / LOG_FILE).read_text(), re.M)
    parts, rows, unresolved = [], [], []
    for r in stats:
        d, f = int(r["d"]), {k: float(v) for k, v in r.items() if k not in ("resolved", "note")}
        rows.append([r["d"], r["n_seeds"], num(f["f_off"], 1), num(f["f_on"], 1),
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
    with (RESULTS / EVENTS_FILE).open(newline="") as fh:
        ev = list(csv.reader(fh))
    verdict = ("Good: the loss is resolved at every d > 0, so R(d) has intervals." if not unresolved else
               f"Bad: R(d) is missing for d = {', '.join(map(str, unresolved))}.")
    present = f"{cells.group(2)} of {cells.group(1)} cells" if cells else "cells unknown"
    figs = img(f"../{CHART}", "G2 chart") + "".join(img(f"../{n}", n) for n in CELL_CHARTS)
    tables = (table(["d", "seeds", "F(d, off)", "F(d, on)", "loss L(d) [95 %]", "gain G(d) [95 %]",
                     "share R(d) [95 %]", "note"], rows)
              + table(ev[0], ev[1:]) + table(["note"], [[n] for n in NOTES]))
    return Stage(key, title, what, why, f"{len(read_stats(RESULTS / SUMMARY_FILE))} manifests from runs/sweep/ ({present}).",
                 f"{SUMMARY_FILE}, {STATS_FILE}, {EVENTS_FILE}, {CHART}, {', '.join(CELL_CHARTS)}.",
                 "; ".join(parts) + ".", verdict, "ran", figs, tables)


def demo_stage() -> Stage:
    key, title = "demo", "Stage 6: Qt demo, d = 2"
    what = "Frames from the Qt demo at d = 2, defense off and on (capture by make_demo.py --capture)."
    why = "The Vision is one demo that shows the defense winning back lost food."
    shots = sorted(DEMO.glob("d*_def*_*.png")) if DEMO.is_dir() else []
    if not shots:
        return skipped(key, title, what, why, "no frame in results/real/mvp3/demo/")
    show = []
    for defense in S.DEFENSES:
        mine = [p for p in shots if f"_def{defense}_" in p.name]
        show += [mine[0], mine[len(mine) // 2], mine[-1]] if len(mine) >= 3 else mine
    rows = [[p.name, f"{p.stat().st_size / 1024:.0f}"] for p in shots]
    return Stage(key, title, what, why, "Live Qt run (headless frame grabbing), seed 1, frozen values.",
                 f"{len(shots)} frames in results/real/mvp3/demo/.", f"{len(shots)} frames. First, middle and last of each arm are shown.",
                 "Good: both arms have frames." if len({p.name.split('_')[1] for p in shots}) == 2 else "Bad: one arm has no frame.",
                 "ran", "".join(img(f"demo/{p.name}", p.stem) for p in show), table(["file", "size (KB)"], rows))


def results_page(stages: list[Stage]) -> None:
    """results/index.html: G1 and G2 first, read from summary.csv and g2_stats.csv."""
    g1 = "G1: no summary.csv yet."
    summary = RESULTS / SUMMARY_FILE
    if summary.is_file():
        with summary.open(newline="") as fh:
            rows = [r for r in csv.DictReader(fh) if r["complete"] == "True" and r[S.COL_MOCK] == "0"]
        cells = {(r[S.P_NDET], r[S.P_DEFENSE], r[S.P_SEED]) for r in rows}
        g1 = f"G1: {len(cells)} of {TOTAL_RUNS} runs logged and complete."
    g2 = ["G2: no g2_stats.csv yet."]
    if (RESULTS / STATS_FILE).is_file():
        g2 = [(f"R({r['d']}) = {num(float(r['share']))} {interval(float(r['share_lo']), float(r['share_hi']))}"
               if r["resolved"] == "True" else f"R({r['d']}) not reported ({r['note']})")
              for r in read_stats(RESULTS / STATS_FILE) if int(r["d"]) > 0]
    links = [(f"real/mvp3/{s.key}.html", s.title) for s in stages] + [
        ("real/mvp3/index.html", "MVP3 summary"), ("real/mvp2/index.html", "MVP2 page (real slice)"),
        ("mock/mvp1/index.html", "MVP1 page (mock end to end)"), (f"real/{CHART}", "G2 chart"),
        ("real/mvp3/demo/", "Qt demo frames"), ("README.md", "File list")]
    body = (f"<h1>Pheromone foraging under misleading trails: results</h1>\n"
            f'<div class="panel"><p class="label">Goals</p><p>{escape(g1)}</p><p>{escape("; ".join(g2))}.</p></div>\n'
            f'<div class="panel fig">{img(f"real/{CHART}", "G2 chart")}</div>\n'
            f'<div class="panel"><p class="label">Pages</p><ul>'
            + "".join(f'<li><a href="{escape(h)}">{escape(t)}</a></li>' for h, t in links) + "</ul></div>")
    (RESULTS_ALL / "index.html").write_text(page("Results", body, theme_href="assets/theme.css"))


def write_file_list() -> None:
    """results/README.md: every file under results/, with its size."""
    kinds = {".html": "page", ".png": "figure", ".csv": "table", ".json": "saved verdict or pick",
             ".txt": "log", ".css": "theme", ".md": "text"}
    files = sorted(p for p in RESULTS_ALL.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    lines = ["# results/: file list", "", "Written by `tools/make_report.py --phase mvp3`. Open `index.html` first.", "",
             "| File | Kind | Size (KB) |", "| --- | --- | --- |"]
    for p in sorted({*files, RESULTS_ALL / "README.md"}):
        size = p.stat().st_size / 1024 if p.exists() else 0.0
        lines.append(f"| `{p.relative_to(RESULTS_ALL)}` | {kinds.get(p.suffix, 'file')} | {size:.0f} |")
    (RESULTS_ALL / "README.md").write_text("\n".join(lines) + "\n")


def run_phase() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    stages = [safe(f) for f in (smoke_stage, defense_tuning_stage, sweep_stage, check_stage, analyze_stage, demo_stage)]
    for i, s in enumerate(stages, 1):
        (OUT / f"{s.key}.html").write_text(stage_page(s, i, len(stages)))
    ran = sum(1 for s in stages if s.status.startswith("ran"))
    intro = (f"Milestone M3 (minimum viable product 3) adds detractors, the defense and the 80-run sweep. "
             f"{ran} of {len(stages)} stages ran. All numbers come from saved outputs.")
    extras = [(CHART, f"../{CHART}"), (SUMMARY_FILE, f"../{SUMMARY_FILE}"), (STATS_FILE, f"../{STATS_FILE}"),
              (EVENTS_FILE, f"../{EVENTS_FILE}"), ("defense_pick.json", "../defense_tuning/defense_pick.json")]
    (OUT / "index.html").write_text(index_page("MVP3 summary: detractors, defense, sweep", intro, stages, extras))
    results_page(stages)
    write_file_list()
    print("\n".join(f"{s.key}: {s.status}" for s in stages))
    print(f"wrote {OUT / 'index.html'}, {RESULTS_ALL / 'index.html'}, {RESULTS_ALL / 'README.md'}")
    return 0
