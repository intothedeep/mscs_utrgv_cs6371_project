"""MVP2 stage reports: make_report.py --phase mvp2 (M2-10).

Saved outputs only: manifests, CSVs, logs, tuning_pick.json, verdict.json. No number is
typed here. A stage with no saved output is reported as skipped and the script goes on.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import schema as S  # noqa: E402
from analyze import LOG_FILE, STATS_FILE, SUMMARY_FILE  # noqa: E402
from make_report import bar_figure, img, interval, num, parse_check_log, read_stats, skipped  # noqa: E402
from report_html import Stage, index_page, stage_page, table  # noqa: E402
from run_results import PROJECT, load_manifests, sha256_hex  # noqa: E402

__all__ = ["run_phase"]

SRC = PROJECT / "src"
RESULTS = PROJECT / "results" / "real"
OUT = RESULTS / "mvp2"
RUNS = PROJECT / "runs"
SMOKE = RUNS / "smoke"
CHECK_LOG = RESULTS / "check_log.txt"
PICK = RESULTS / "tuning" / "tuning_pick.json"
VERDICT = RESULTS / "judgement" / "verdict.json"
CHART = "g2_recovered_share.png"
LIBS = ("build/controllers/pheromone_forager/libpheromone_forager.*",
        "build/loop_functions/pheromone_loop_functions/libpheromone_loop_functions.*")


def failed(key: str, title: str, what: str, why: str, reason: str) -> Stage:
    return Stage(key, title, what, why, "none", "none", "none", "none", f"failed: {reason}", "", "")


def build_stage() -> Stage:
    key, title = "build", "Stage 1: build src/"
    what = "Build the controller and the loop functions with cmake and make."
    why = "Milestone M2 needs real code before any real run. That serves goal G1."
    libs = [p for pattern in LIBS for p in sorted(SRC.glob(pattern))]
    if len(libs) < len(LIBS):
        return skipped(key, title, what, why, "a built library is missing under src/build/")
    kb = [p.stat().st_size / 1024 for p in libs]
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "build_fig.png", "Built libraries", [p.name for p in libs],
               {"size": kb}, "library", "size (KB)")
    rows = [[p.name, f"{k:.0f}", sha256_hex(p)[:12]] for p, k in zip(libs, kb)]
    return Stage(key, title, what, why, "Sources under src/ (C++17, ARGoS 3.0.0-beta59).",
                 f"{len(libs)} libraries under src/build/.", "; ".join(f"{r[0]} {r[1]} KB" for r in rows) + ".",
                 "Good: both libraries exist. The build itself ran in the main session.",
                 "ran (libraries found; compiler output is not saved)",
                 img("build_fig.png", "Library sizes"), table(["library", "size (KB)", "sha256[:12]"], rows))


def generate_stage() -> Stage:
    key, title = "generate", "Stage 2: generate the .argos files"
    what = "tools/make_sweep.py writes one .argos file per run from the headless template."
    why = "Every real run needs its own seed, run folder and git stamp (DESIGN section 4)."
    roots = {"smoke": SMOKE, "tuning": RUNS / "tuning", "judgement": RUNS / "judgement"}
    counts = {name: len(load_manifests(root)) for name, root in roots.items()}
    files = len(list((SRC / "experiments" / "generated").glob("*.argos")))
    if files == 0:
        return skipped(key, title, what, why, "no file in src/experiments/generated/")
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "generate_fig.png", "Runs with a manifest, by runs root", list(counts),
               {"runs": list(counts.values())}, "runs root", "number of runs")
    result = f"{files} .argos files. Runs with a manifest: " + ", ".join(f"{k} {v}" for k, v in counts.items()) + "."
    return Stage(key, title, what, why, "pheromone_headless.template.argos.",
                 f"{files} files in src/experiments/generated/.", result,
                 "Good: smoke run has a manifest." if counts["smoke"] else "Bad: no smoke run has a manifest yet.",
                 "ran", img("generate_fig.png", "Runs per root"),
                 table(["runs root", "runs with manifest"], [[k, str(v)] for k, v in counts.items()]))


def run_stage() -> Stage:
    key, title = "run", "Stage 3: headless run"
    what = "Run argos3 headless on the generated file. One run writes one folder under runs/smoke/."
    why = "The real forager and the real grid must collect food and write the log schema."
    manifests = load_manifests(SMOKE)
    if not manifests:
        return skipped(key, title, what, why, "no run under runs/smoke/")
    rows, events = [], Counter()
    for m in manifests:
        folder = SMOKE / m[S.K_RUNID]
        with (folder / S.EVENTS_FILE).open(newline="") as fh:
            ev = Counter(r[S.COL_EVENT] for r in csv.DictReader(fh))
        events.update(ev)
        met = m[S.K_METRICS]
        rows.append([m[S.K_RUNID], str(met[S.M_FOOD]), num(met[S.M_WASTED], 1), str(met[S.M_TICKS]),
                     str(met[S.M_COMPLETE]), str(ev["pickup"]), str(ev["drop"])])
    with (SMOKE / manifests[0][S.K_RUNID] / S.TICKS_FILE).open(newline="") as fh:
        ticks = list(csv.DictReader(fh))
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.5, 4.2), layout="constrained")
    ax.plot([int(r[S.COL_TICK]) for r in ticks], [int(r[S.COL_FOOD]) for r in ticks])
    ax.set_xlabel("tick (10 per second)")
    ax.set_ylabel("food_collected (cumulative)")
    fig.suptitle(f"Smoke run {manifests[0][S.K_RUNID]}")
    fig.savefig(OUT / "run_fig.png", dpi=150)
    plt.close(fig)
    first = manifests[0][S.K_METRICS]
    bad = [name for name, ok in (("food_collected is 0", first[S.M_FOOD] > 0), ("no pickup event", events["pickup"] > 0),
                                 ("no drop event", events["drop"] > 0)) if not ok]
    return Stage(key, title, what, why, "Generated .argos file(s). Real simulation, no recorded data.",
                 f"{len(manifests)} run folder(s) under runs/smoke/.",
                 f"food_collected {first[S.M_FOOD]}, ticks {first[S.M_TICKS]}, pickup {events['pickup']}, drop {events['drop']}.",
                 "Good: food was collected and pickup and drop were logged." if not bad else "Bad: " + ", ".join(bad) + ".",
                 "ran", img("run_fig.png", "Food over time"),
                 table(["runid", "food", "wasted s", "ticks", "complete", "pickups", "drops"], rows))


def check_stage() -> Stage:
    key, title = "check", "Stage 4: check the run"
    what = "check_runs.py checks the smoke run against tools/schema.py, unchanged since M1."
    why = "The real log must satisfy the same schema as the mock (DESIGN section 5)."
    if not CHECK_LOG.is_file():
        return skipped(key, title, what, why, f"{CHECK_LOG.relative_to(PROJECT)} not found. Run check_runs.py with --log")
    text = CHECK_LOG.read_text()
    summary, fails = parse_check_log(text)
    if summary is None:
        return failed(key, title, what, why, "the check log has no SUMMARY line")
    runs, bad, problems = summary
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "check_fig.png", "Schema check per run", ["passed", "failed"],
               {"runs": [runs - bad, bad]}, "check result", "number of runs")
    rows = fails[:50] or [["none", "", "", "no problem found"]]
    return Stage(key, title, what, why, f"{runs} run folder(s) under runs/smoke/.",
                 f"{CHECK_LOG.relative_to(PROJECT)}, {len(text.splitlines())} lines.",
                 f"runs {runs}, failed {bad}, problems {problems}.",
                 "Good: every run passes." if problems == 0 else f"Bad: first problem {' '.join(fails[0])}.",
                 "ran", img("check_fig.png", "Runs passed and failed"), table(["run", "file", "column", "message"], rows))


def analyze_stage() -> Stage:
    key, title = "analyze", "Stage 5: analyze"
    what = "analyze.py reads the smoke root and lists the cells it still lacks."
    why = "A partial root must not crash the analysis. It must say what is missing."
    needed = [RESULTS / n for n in (SUMMARY_FILE, STATS_FILE, LOG_FILE, CHART)]
    absent = [p.name for p in needed if not p.is_file()]
    if absent:
        return skipped(key, title, what, why, f"{', '.join(absent)} not found in results/real/. Run analyze.py first")
    cells = re.search(r"^CELLS expected=(\d+) present=(\d+) missing=(\d+)", (RESULTS / LOG_FILE).read_text(), re.M)
    if not cells:
        return failed(key, title, what, why, "the analyze log has no CELLS line")
    expected, present, missing = map(int, cells.groups())
    stats = read_stats(RESULTS / STATS_FILE)
    rows = [[r["d"], r["n_seeds"], num(float(r["f_off"]), 1), num(float(r["f_on"]), 1),
             f"{num(float(r['share']))} {interval(float(r['share_lo']), float(r['share_hi']))}", r["note"]] for r in stats]
    ok = missing == expected - present
    return Stage(key, title, what, why, f"{len(read_stats(RESULTS / SUMMARY_FILE))} manifest(s) from runs/smoke/.",
                 f"{SUMMARY_FILE}, {STATS_FILE}, {CHART}, {LOG_FILE} in results/real/.",
                 f"cells expected {expected}, present {present}, missing {missing}.",
                 "Good: missing = expected - present, no crash." if ok else "Bad: the cell counts do not add up.",
                 "ran", img(f"../{CHART}", "G2 chart, partial data"),
                 table(["d", "seeds", "F(d, off)", "F(d, on)", "share R(d) [95 %]", "note"], rows))


def qt_stage() -> Stage:
    key, title = "qt_view", "Stage 6: Qt view"
    what = "The owner runs pheromone_qt.argos and saves two screenshots: trails forming and fading."
    why = "The Vision demo shows true trails in a green tint. M2 must show them on screen."
    shots = sorted(OUT.glob("qt_*.png")) if OUT.is_dir() else []
    if not shots:
        return skipped(key, title, what, why, "no qt_*.png screenshot in results/real/mvp2/")
    rows = [[p.name, f"{p.stat().st_size / 1024:.0f}"] for p in shots]
    return Stage(key, title, what, why, "Live Qt run (owner), no saved data.", f"{len(shots)} screenshot(s).",
                 f"{len(shots)} screenshot(s): " + ", ".join(p.name for p in shots) + ".",
                 "Good: two or more screenshots." if len(shots) >= 2 else "Bad: M2 exit 6 needs two screenshots.",
                 "ran", "".join(img(p.name, p.stem) for p in shots), table(["file", "size (KB)"], rows))


def tuning_stage() -> Stage:
    key, title = "tuning", "Stage 7: pheromone tuning (D-007)"
    what = "Up to 3 rounds on seeds 101 to 103. Pick the round with the highest mean food_collected."
    why = "The pheromone values freeze before the keep-A judgement and before any detractor run."
    if not PICK.is_file():
        return skipped(key, title, what, why, "results/real/tuning/tuning_pick.json not found")
    pick = json.loads(PICK.read_text())
    rounds = pick["rounds"]
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "tuning_fig.png", "Mean food_collected per tuning round", [f"round {r['round']}" for r in rounds],
               {"mean food": [r["mean_food"] for r in rounds]}, "round", "mean food_collected (3 seeds)")
    rows = [[str(r["round"]), f"{r['half_life_s']:g}", f"{r['lambda_dep']:g}",
             ", ".join(f"{s}: {f}" for s, f in r["food_by_seed"].items()), num(r["mean_food"])] for r in rounds]
    return Stage(key, title, what, why, "Real runs, d = 0, defense off, seeds 101 to 103 (runs/tuning/).",
                 "results/real/tuning/tuning_pick.json.",
                 f"picked round {pick['picked_round']}: half_life_s {pick['half_life_s']:g}, lambda_dep {pick['lambda_dep']:g}.",
                 "Bad: no round beat round 1 (D-007 failure condition)." if pick["picked_round"] == 1 and len(rounds) > 1
                 else f"Good: round {pick['picked_round']} has the highest mean.",
                 "ran", img("tuning_fig.png", "Mean food per round"),
                 table(["round", "half-life (s)", "lambda_dep", "food by seed", "mean food"], rows))


def judgement_stage() -> Stage:
    key, title = "judgement", "Stage 8: keep-A judgement (D-010)"
    what = "Compare pheromone on (arm 1) with no following (arm 2) on seeds 104 to 106."
    why = "Strategy A stays only if following the trails brings food (D-010)."
    if not VERDICT.is_file():
        return skipped(key, title, what, why, "results/real/judgement/verdict.json not found")
    v = json.loads(VERDICT.read_text())
    seeds = [str(s) for s in v["seeds"]]
    OUT.mkdir(parents=True, exist_ok=True)
    bar_figure(OUT / "judgement_fig.png", "food_collected per seed and arm", [f"seed {s}" for s in seeds],
               {"arm 1 pheromone on": [v["arm1_food_by_seed"][s] for s in seeds],
                "arm 2 no following": [v["arm2_food_by_seed"][s] for s in seeds]}, "seed", "food_collected")
    rows = [[s, str(v["arm1_food_by_seed"][s]), str(v["arm2_food_by_seed"][s]), str(v["arm1_above_arm2_by_seed"][s])]
            for s in seeds]
    return Stage(key, title, what, why, "Real runs, d = 0, defense off, seeds 104 to 106 (runs/judgement/).",
                 "results/real/judgement/verdict.json.",
                 f"arm 1 mean {num(v['arm1_mean'])}, arm 2 mean {num(v['arm2_mean'])}, threshold {v['ratio_threshold']}.",
                 "Good: pass, keep strategy A." if v["pass"] else "Bad: fail, switch to strategy B (D-010).",
                 "ran", img("judgement_fig.png", "Food per seed and arm"),
                 table(["seed", "arm 1 food", "arm 2 food", "arm 1 above arm 2"], rows))


def safe(stage_fn: Callable[[], Stage]) -> Stage:
    """A stage that cannot read its saved output is reported failed. The others still run."""
    try:
        return stage_fn()
    except (SystemExit, KeyError, ValueError, OSError, json.JSONDecodeError) as err:
        name = stage_fn.__name__.removesuffix("_stage")
        return failed(name, name, "", "", repr(err))


def run_phase() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    stages = [safe(f) for f in (build_stage, generate_stage, run_stage, check_stage, analyze_stage,
                                qt_stage, tuning_stage, judgement_stage)]
    for i, s in enumerate(stages, 1):
        (OUT / f"{s.key}.html").write_text(stage_page(s, i, len(stages)))
    ran = sum(1 for s in stages if s.status.startswith("ran"))
    intro = (f"Milestone M2 (minimum viable product 2) makes the honest forager and the pheromone grid real. "
             f"{ran} of {len(stages)} stages ran. All numbers come from saved outputs.")
    extras = [(CHART, f"../{CHART}"), (SUMMARY_FILE, f"../{SUMMARY_FILE}"), (STATS_FILE, f"../{STATS_FILE}"),
              ("tuning_pick.json", "../tuning/tuning_pick.json"), ("verdict.json", "../judgement/verdict.json")]
    (OUT / "index.html").write_text(index_page("MVP2 summary: real slice, 0 detractors", intro, stages, extras))
    print("\n".join(f"{s.key}: {s.status}" for s in stages))
    print(f"wrote {OUT / 'index.html'}")
    return 0
