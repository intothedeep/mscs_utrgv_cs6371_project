"""Defense diagnostics from saved runs (decisions/2026-11-11_fable_defense_v2.md, task M4).

Usage: defense_diagnostics.py [root] [--seeds a-b] [--out FILE]
Default root runs/sweep, seeds 1-10, out results/real/defense_diagnostics.csv. Works on any sweep root.
Reads manifest.json, events.csv and robots.csv of the chosen run of each cell. Honest robots only.

Why: the v3 defense saved false-trail time but not food. These rows show where the time went.
Output: long CSV, one row per (d, defense, metric). Per-run means are over the runs of the cell.

Metrics
  gap_abort_to_follow_mean_s   mean seconds from a cone_abort to the same robot's next follow_start
  gap_abort_to_follow_le5_share  share of those gaps that are 5 s or less
  gap_abort_no_follow_per_run  cone_aborts with no later follow_start in the run (left out of the gap)
  false_follow_before_s / _after_s  FOLLOW seconds on a false trail (false_share >= 0.5) per run,
                               before / after the robot learned the nearest active decoy
  cone_abort_on_false_trail / _off_false_trail  cone_abort events per run by the false_share of the
                               robot's robots.csv row of that second
  time_<STATE>_s               honest robot-seconds per run in each state
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import schema as S
from analyze import load_runs, select_cells
from run_results import PROJECT
from sweep_params import parse_seeds

FALSE_SHARE = 0.5       # same cut as the wasted-time metric (DESIGN 4.1)
LEARN_RADIUS_M = 1.0    # a suspect_add within this of a decoy counts as learning it (Fable: 1.0 m)
GAP_SHORT_S = 5.0
DEFAULT_OUT = PROJECT / "results" / "real" / "defense_diagnostics.csv"
COLUMNS = ("d", "defense", "metric", "value", "n", "unit")


def _read(path: Path) -> list[dict]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def abort_gaps(events: list[dict]) -> tuple[list[float], int]:
    """Seconds from each cone_abort to the same robot's next follow_start. Second: aborts with none."""
    starts: dict[str, list[int]] = defaultdict(list)
    for e in events:
        if e[S.COL_EVENT] == "follow_start":
            starts[e[S.COL_ROBOT]].append(int(e[S.COL_TICK]))
    gaps, open_ended = [], 0
    for e in events:
        if e[S.COL_EVENT] != "cone_abort":
            continue
        tick = int(e[S.COL_TICK])
        later = [t for t in starts[e[S.COL_ROBOT]] if t > tick]
        if later:
            gaps.append((min(later) - tick) / S.TICKS_PER_SECOND)
        else:
            open_ended += 1
    return gaps, open_ended


def learned_ticks(events: list[dict], decoys: list[list[float]]) -> dict[tuple[str, int], int]:
    """(robot, decoy index) -> first tick of a suspect_add within LEARN_RADIUS_M of that decoy."""
    first: dict[tuple[str, int], int] = {}
    for e in events:
        if e[S.COL_EVENT] != "suspect_add":
            continue
        for i, (dx, dy) in enumerate(decoys):
            if math.hypot(float(e["x"]) - dx, float(e["y"]) - dy) <= LEARN_RADIUS_M:
                key = (e[S.COL_ROBOT], i)
                first[key] = min(first.get(key, 10**9), int(e[S.COL_TICK]))
    return first


def run_metrics(manifest: dict, events: list[dict], robots: list[dict]) -> dict[str, float]:
    """All per-run numbers of one run. Counts and seconds, summed over the run."""
    n_used = manifest[S.K_LAYOUT][S.L_NUSED]
    decoys = manifest[S.K_LAYOUT][S.L_DECOYS][:n_used]  # D-009: the first n_used decoys are active
    learned = learned_ticks(events, decoys)
    honest = [r for r in robots if r[S.COL_ROLE] == "honest"]
    share_at = {(int(r[S.COL_TICK]), r[S.COL_ROBOT]): float(r["false_share"]) for r in honest}
    out: Counter = Counter()
    for r in honest:
        out[f"time_{r[S.COL_STATE]}_s"] += 1  # robots.csv holds one row per robot per second
        if r[S.COL_STATE] != "FOLLOW" or float(r["false_share"]) < FALSE_SHARE or not decoys:
            continue
        x, y, tick = float(r["x"]), float(r["y"]), int(r[S.COL_TICK])
        nearest = min(range(len(decoys)), key=lambda i: math.hypot(x - decoys[i][0], y - decoys[i][1]))
        after = learned.get((r[S.COL_ROBOT], nearest), 10**9) <= tick
        out["false_follow_after_s" if after else "false_follow_before_s"] += 1
    for e in events:
        if e[S.COL_EVENT] != "cone_abort":
            continue
        second = int(e[S.COL_TICK]) // S.TICKS_PER_SECOND * S.TICKS_PER_SECOND  # row of that second
        share = share_at.get((second, e[S.COL_ROBOT]))
        if share is not None:
            out["cone_abort_on_false_trail" if share >= FALSE_SHARE else "cone_abort_off_false_trail"] += 1
    return dict(out)


def diagnose(root: Path, seeds: tuple[int, ...]) -> list[list]:
    runs = load_runs(root)
    if not runs:
        raise SystemExit(f"stop: no run manifest under {root}")
    chosen = select_cells(runs, seeds)["chosen"]
    per_cell: dict[tuple[int, int], list[dict[str, float]]] = defaultdict(list)
    gaps_cell: dict[tuple[int, int], list[float]] = defaultdict(list)
    open_cell: dict[tuple[int, int], int] = defaultdict(int)
    for (d, defense, _seed), run in sorted(chosen.items()):
        folder = root / run["runid"]
        manifest = json.loads((folder / S.MANIFEST_FILE).read_text())
        events, robots = _read(folder / S.EVENTS_FILE), _read(folder / S.ROBOTS_FILE)
        per_cell[(d, defense)].append(run_metrics(manifest, events, robots))
        gaps, open_ended = abort_gaps(events)
        gaps_cell[(d, defense)].extend(gaps)
        open_cell[(d, defense)] += open_ended
    rows: list[list] = []
    for (d, defense), metrics in sorted(per_cell.items()):
        n = len(metrics)
        names = sorted({k for m in metrics for k in m})
        for name in names:  # a run without the key had none of it: that is 0
            rows.append([d, defense, name, f"{sum(m.get(name, 0) for m in metrics) / n:.3f}", n,
                         "s per run" if name.endswith("_s") else "events per run"])
        gaps = gaps_cell[(d, defense)]
        if gaps:  # pooled over all aborts of the cell
            rows.append([d, defense, "gap_abort_to_follow_mean_s", f"{sum(gaps) / len(gaps):.3f}",
                         len(gaps), "s per abort"])
            rows.append([d, defense, "gap_abort_to_follow_le5_share",
                         f"{sum(g <= GAP_SHORT_S for g in gaps) / len(gaps):.3f}", len(gaps), "share"])
        rows.append([d, defense, "gap_abort_no_follow_per_run", f"{open_cell[(d, defense)] / n:.3f}", n,
                     "events per run"])
    return rows


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", type=Path, nargs="?", default=PROJECT / "runs" / "sweep")
    ap.add_argument("--seeds", type=parse_seeds, default=S.SEEDS, metavar="a-b")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    if not args.root.is_dir():
        raise SystemExit(f"stop: {args.root} is not a folder")
    rows = diagnose(args.root, args.seeds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
