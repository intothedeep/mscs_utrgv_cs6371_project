"""Mechanism check of defense v5, seeds 201-210 (DESIGN_M5 section 3). Reads saved runs only. Reported, no pick.

Reads the 40 runs of runs/v5_check/ (arms k2t10 and k1t10, cells (d 0, on) and (d 2, on)).
Writes results/real/v5/mechanism.csv (one row per run) and mechanism.md (means per cell).
Per run, honest robots, events.csv in file order:
  stored point   for a suspect_add of robot r: (x, y) of r's last peak row before it
  sus_cls_*      suspect_add rows whose stored point is a source / a decoy (failure_analysis.run_metrics)
  act_cls_*      replay of each robot's stored points (the AddSuspect loop, confirm_k as a parameter):
                 the calls where Count reaches confirm_k, classified at the centroid after that call
  replay_exact   replayed held points summed over robots equal ticks.csv suspects_total at every row
The replay check catches a wrong merge-or-append decision only. It does not prove act_cls_*.
Never compare act_* with the legacy sus_cls_* numbers: the definitions differ.
"""
from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

import schema as S
from failure_analysis import read_events
from run_results import load_manifests
from v5_common import ARMS, CHECK_ROOT, CHECK_SEEDS, PRIMARY, RESULTS, read_food
from v5_killcheck import classify

COLUMNS = ("runid", "arm", "d", "seed", "sus_cls_src", "sus_cls_dec", "act_cls_src", "act_cls_dec",
           "n_cone_abort", "food", "replay_exact")
CHECK_ARMS = (PRIMARY, "k1t10")
CHECK_D = (0, 2)
Point = tuple[int, float, float]  # (tick, x, y)


def tally(counts: dict[str, int], cls: str) -> None:
    """Count a point of class 'src', 'dec<j>' or 'other' as source or decoy. Other is not counted."""
    if cls != "other":
        counts["src" if cls == "src" else "dec"] += 1


def replay_k(points: list[Point], k: int, r_merge: float, n_mem: int
             ) -> tuple[list[Point], list[tuple[int, int | None]]]:
    """One robot's memory, same loop as AddSuspect (first point in insertion order within r_merge).

    Returns the activations (tick, centroid x, y after the call where Count reaches k) and, per
    stored point, (insert tick, evict tick or None) for the held-count series.
    """
    held: list[dict] = []
    acts: list[Point] = []
    spans: list[list] = []
    for t, x, y in points:
        for p in held:
            if math.hypot(p["x"] - x, p["y"] - y) <= r_merge:
                c = p["count"]
                p["x"], p["y"], p["count"] = (p["x"] * c + x) / (c + 1), (p["y"] * c + y) / (c + 1), c + 1
                if p["count"] == k:
                    acts.append((t, p["x"], p["y"]))
                break
        else:
            span = [t, None]
            held.append({"x": x, "y": y, "count": 1, "span": span})
            spans.append(span)
            if k == 1:
                acts.append((t, x, y))
            if len(held) > n_mem:
                held.pop(0)["span"][1] = t
    return acts, [(a, b) for a, b in spans]


def stored_points(events: list) -> dict[str, list[Point]]:
    """robot -> stored points in file order: the last peak position before each suspect_add."""
    last_peak: dict[str, tuple[float, float]] = {}
    out: dict[str, list[Point]] = defaultdict(list)
    for t, rid, ev, x, y in events:
        if ev == "peak":
            last_peak[rid] = (x, y)
        elif ev == "suspect_add":
            px, py = last_peak.get(rid, (x, y))
            out[rid].append((t, px, py))
    return out


def held_matches(spans: list[tuple[int, int | None]], ticks_path: Path) -> bool:
    """Held points summed over robots equal suspects_total at every ticks.csv row."""
    delta: dict[int, int] = defaultdict(int)
    for t_in, t_out in spans:
        delta[t_in] += 1
        if t_out is not None:
            delta[t_out] -= 1
    held, pending = 0, sorted(delta)
    with ticks_path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            tick = int(row[S.COL_TICK])
            while pending and pending[0] <= tick:
                held += delta[pending.pop(0)]
            if held != int(row["suspects_total"]):
                return False
    return True


def run_row(folder: Path, arm: str, d: int, seed: int, m: dict) -> list:
    lay, params = m[S.K_LAYOUT], m[S.K_PARAMS]
    sources, decoys = lay[S.L_SOURCES], lay[S.L_DECOYS][:lay[S.L_NUSED]]
    k = ARMS[arm][1]
    r_merge, n_mem = float(params["controller_defense_r_merge"]), int(params["controller_defense_n_mem"])
    events = read_events(folder / S.EVENTS_FILE)
    sus = {"src": 0, "dec": 0}
    act = {"src": 0, "dec": 0}
    spans: list[tuple[int, int | None]] = []
    for pts in stored_points(events).values():
        for _t, x, y in pts:
            cls = classify(x, y, sources, decoys)
            tally(sus, cls)
        acts, sp = replay_k(pts, k, r_merge, n_mem)
        spans += sp
        for _t, x, y in acts:
            cls = classify(x, y, sources, decoys)
            tally(act, cls)
    n_abort = sum(1 for e in events if e[2] == "cone_abort")
    exact = held_matches(spans, folder / S.TICKS_FILE)
    return [m[S.K_RUNID], arm, d, seed, sus["src"], sus["dec"], act["src"], act["dec"], n_abort,
            m[S.K_METRICS][S.M_FOOD], int(exact)]


def write_md(rows: list[list], path: Path) -> None:
    col = {c: i for i, c in enumerate(COLUMNS)}
    lines = ["# Defense v5 mechanism check, seeds 201-210", "",
             "Reported only, no value is picked. Source: `runs/v5_check/`, `tools/v5_mechanism.py`.",
             "act_* counts calls where Count reaches confirm_k. sus_* counts every failure. "
             "Do not compare act_* with the legacy sus_cls numbers.", "",
             "| d | arm | n | sus_src | sus_dec | act_src | act_dec | cone_abort | food | replay inexact |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    by: dict[tuple, list] = defaultdict(list)
    for r in rows:
        by[(r[col["d"]], r[col["arm"]])].append(r)
    for (d, arm), rs in sorted(by.items()):
        mean = lambda name: np.mean([r[col[name]] for r in rs])
        inexact = sum(1 for r in rs if not r[col["replay_exact"]])
        lines.append(f"| {d} | {arm} | {len(rs)} | {mean('sus_cls_src'):.2f} | {mean('sus_cls_dec'):.2f} | "
                     f"{mean('act_cls_src'):.2f} | {mean('act_cls_dec'):.2f} | {mean('n_cone_abort'):.2f} | "
                     f"{mean('food'):.2f} | {inexact} |")
    lines += ["", "Paired mean per seed, k2t10 minus k1t10:", "", "| d | metric | mean difference |", "| --- | --- | --- |"]
    for d, name in ((0, "act_cls_src"), (2, "act_cls_dec")):
        a = {r[col["seed"]]: r[col[name]] for r in by[(d, PRIMARY)]}
        b = {r[col["seed"]]: r[col[name]] for r in by[(d, "k1t10")]}
        lines.append(f"| {d} | {name} | {np.mean([a[s] - b[s] for s in sorted(a)]):.2f} |")
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    raw = read_food(CHECK_ROOT)
    expected = {(ARMS[a][1], ARMS[a][2], d, 1, s) for a in CHECK_ARMS for d in CHECK_D for s in CHECK_SEEDS}
    if set(raw) != expected:
        raise SystemExit(f"stop: {CHECK_ROOT.name} is not the {len(expected)} check runs. "
                         f"missing {len(expected - set(raw))}, extra {len(set(raw) - expected)}")
    by_key = {(ARMS[a][1], ARMS[a][2]): a for a in CHECK_ARMS}
    rows = []
    for m in sorted(load_manifests(CHECK_ROOT), key=lambda m: m[S.K_RUNID]):
        p = m[S.K_PARAMS]
        arm = by_key[(int(float(p["controller_defense_confirm_k"])), int(float(p["controller_defense_t_lock"])))]
        rows.append(run_row(CHECK_ROOT / m[S.K_RUNID], arm, int(p[S.P_NDET]), int(p[S.P_SEED]), m))
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "mechanism.csv").open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(rows)
    write_md(rows, RESULTS / "mechanism.md")
    inexact = sum(1 for r in rows if not r[-1])
    print(f"wrote {len(rows)} runs to {RESULTS}. replay inexact: {inexact}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
