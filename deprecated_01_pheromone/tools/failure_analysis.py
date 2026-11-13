"""Failure analysis of the defense from saved runs (results/real/failure_analysis.md).

Usage: failure_analysis.py [--out FILE]
Reads manifest.json, events.csv and robots.csv under three roots. numpy and stdlib only.
No model, no simulation. Writes one long CSV (default results/real/failure_analysis.csv).

Roots and seeds
  v3      runs/sweep            seeds 1-10   (t_lock absent = 0)
  lock10  runs/sweep_v2         seeds 11-30  (t_lock 10)
  lock0   runs/sweep_v2_lock0   seeds 11-30  (t_lock 0, v4 = v3 by the invariance check)
A duplicate (root, d, defense, seed) keeps the latest complete runid (DESIGN 4.2 cell check).

Output columns: scope, root, d, defense, seed, metric, value, lo, hi, n
  scope run       one value per run
  scope cell      mean over the seeds of the cell (lo, hi empty)
  scope contrast  paired difference over seeds with a 95 % bootstrap interval (g2_stats rules)
  scope dose      exploratory per-seed slope and correlation at d = 0 (no interval)

Per-run metrics (honest robots only)
  food, wasted_s                       manifest metrics
  n_<event>                            event counts
  Stored suspect point: the controller stores m_cPeakPos (the robot's position at its peak), but the
  suspect_add row logs the robot's position 15 s later (pheromone_forager_states.cpp EndSearch,
  pheromone_loop_functions_log.cpp). So every suspect metric uses the robot's last peak event.
  sus_src_le040/055/065/100            stored point within 0.40 / 0.55 / 0.65 / 1.00 m of a source centre
                                       (0.40 = r_suspect mask covers the centre, 0.55 = disc reachable from
                                        the END_SEARCH radius 0.30 m, 0.65 = mask touches the disc)
  sus_cls_src, sus_cls_dec, sus_other  exclusive class: nearest landmark (source or active decoy) within
                                       1.00 m is a source / a decoy, or none within 1.00 m
  pk_src_pickup/suspect/neither        peaks within 1.00 m of a source, by outcome in the END_SEARCH
                                       window (peak tick + t_end + 1 s): same robot picks up, adds a
                                       suspect, or neither (invalid peak, no food)
  pkdist_<outcome>, pkcrowd_<outcome>  mean peak-to-source-centre distance, and mean other honest robots
                                       within 0.5 m of that source over the window seconds
  carry_s                              honest robot-seconds with carrying = 1
  abort_true_trail, abort_false_trail  cone_abort by robots.csv false_share (< or >= 0.5)
  abort_pos_src_le150                  cone_abort position within 1.50 m of a source centre
  abort_trig_src/dec/other/none        reconstructed trigger suspect (see below) near a source,
                                       near an active decoy, near neither, or no stored point in d_cone
  fs_to_pickup/peak/abort/next/end     outcome of each follow_start: the first of pickup, peak,
                                       cone_abort, a new follow_start, or run end
  abort_to_pickup_s_mean               mean s from cone_abort to the same robot's next pickup
  abort_pickup_le30_share              share of cone_aborts with a pickup by the same robot within 30 s
  abort_to_follow_s_mean               mean s from cone_abort to the same robot's next follow_start
  time_<STATE>_s                      honest robot-seconds per state

Trigger reconstruction (not logged by the controller, so this is a model of its memory):
each robot's memory is rebuilt from its own suspect_add events (stored at its last peak) with r_merge and n_mem from the
manifest (merge = count-weighted centroid, oldest dropped). At a cone_abort the trigger is the
stored point nearest the robot within d_cone. Heading is not used (robots.csv has 1 s rows).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from g2_stats import paired_diff_interval

PROJECT = Path(__file__).resolve().parent.parent
ROOTS = {"v3": ("runs/sweep", range(1, 11)),
         "lock10": ("runs/sweep_v2", range(11, 31)),
         "lock0": ("runs/sweep_v2_lock0", range(11, 31))}
DEFAULT_OUT = PROJECT / "results" / "real" / "failure_analysis.csv"
COLUMNS = ("scope", "root", "d", "defense", "seed", "metric", "value", "lo", "hi", "n")
TPS = 10
NEAR_M = 1.0          # Fable's cut for "near a source" (decisions/2026-11-11_fable_defense_v2.md)
SUSPECT_CUTS = (0.40, 0.55, 0.65, 1.00)
CROWD_M = 0.5
FALSE_SHARE = 0.5     # DESIGN 4.1


def _dist(x: float, y: float, pts: list) -> float:
    return min((math.hypot(x - p[0], y - p[1]) for p in pts), default=math.inf)


def _nearest(x: float, y: float, pts: list) -> int:
    return min(range(len(pts)), key=lambda i: math.hypot(x - pts[i][0], y - pts[i][1]))


def select_runs(root: Path, seeds: range) -> dict[tuple[int, int, int], Path]:
    """(d, defense, seed) -> run folder. Latest complete runid wins (runids start with a timestamp)."""
    chosen: dict[tuple[int, int, int], tuple[str, Path]] = {}
    for mf in sorted(root.glob("*/manifest.json")):
        m = json.loads(mf.read_text())
        p = m["params"]
        key = (int(p["n_det"]), int(p["defense"]), int(p["seed"]))
        if key[2] not in seeds or not m["metrics"]["complete"]:
            continue
        if key not in chosen or m["runid"] > chosen[key][0]:
            chosen[key] = (m["runid"], mf.parent)
    return {k: v[1] for k, v in chosen.items()}


def read_events(path: Path) -> list[tuple[int, str, str, float, float]]:
    with path.open(newline="") as fh:
        r = csv.reader(fh)
        next(r)
        return [(int(t), rid, ev, float(x), float(y)) for t, rid, ev, x, y in r if rid.startswith("hb_")]


def read_robots(path: Path) -> dict[int, dict[str, tuple[float, float, str, float, int]]]:
    """tick -> robot -> (x, y, state, false_share, carrying), honest robots only."""
    out: dict[int, dict[str, tuple[float, float, str, float, int]]] = defaultdict(dict)
    with path.open(newline="") as fh:
        r = csv.reader(fh)
        h = {c: i for i, c in enumerate(next(r))}
        it, ir, il, ix, iy, ist, ifs, ica = (h[c] for c in ("tick", "robot_id", "role", "x", "y", "state",
                                                            "false_share", "carrying"))
        for row in r:
            if row[il] == "honest":
                out[int(row[it])][row[ir]] = (float(row[ix]), float(row[iy]), row[ist], float(row[ifs]),
                                              int(row[ica]))
    return out


def _row_at(robots: dict, tick: int) -> dict:
    second = max(TPS, tick // TPS * TPS)  # robots.csv rows start at tick 10, one per second
    return robots.get(second, {})


def _crowd(robots: dict, tick: int, src: list, rid: str) -> int:
    return sum(1 for o, (x, y, *_rest) in _row_at(robots, tick).items()
               if o != rid and math.hypot(x - src[0], y - src[1]) <= CROWD_M)


def peak_outcomes(events: list, robots: dict, sources: list, t_end_s: float) -> dict[str, float]:
    """Peaks within NEAR_M of a source, split by what the same robot does in the END_SEARCH window."""
    by_robot: dict[str, list] = defaultdict(list)
    for e in events:
        by_robot[e[1]].append(e)
    window = int((t_end_s + 1.0) * TPS)
    dist: dict[str, list[float]] = defaultdict(list)
    crowd: dict[str, list[float]] = defaultdict(list)
    for rid, evs in by_robot.items():
        for i, (t, _r, ev, x, y) in enumerate(evs):
            if ev != "peak" or _dist(x, y, sources) > NEAR_M:
                continue
            nxt = next((f[2] for f in evs[i + 1:] if f[0] <= t + window and f[2] in ("pickup", "suspect_add")),
                       None)
            cls = {"pickup": "pickup", "suspect_add": "suspect"}.get(nxt, "neither")
            src = sources[_nearest(x, y, sources)]
            dist[cls].append(math.hypot(x - src[0], y - src[1]))
            ticks = range(t, t + int(t_end_s * TPS) + 1, TPS)
            crowd[cls].append(float(np.mean([_crowd(robots, k, src, rid) for k in ticks])))
    out: dict[str, float] = {}
    for cls in ("pickup", "suspect", "neither"):
        out[f"pk_src_{cls}"] = float(len(dist[cls]))
        out[f"pkdist_{cls}"] = float(np.mean(dist[cls])) if dist[cls] else math.nan
        out[f"pkcrowd_{cls}"] = float(np.mean(crowd[cls])) if crowd[cls] else math.nan
    return out


def follow_outcomes(events: list) -> Counter:
    """Outcome of each follow_start: the robot's next pickup, peak, cone_abort or follow_start."""
    by_robot: dict[str, list] = defaultdict(list)
    for e in events:
        by_robot[e[1]].append(e)
    out: Counter = Counter()
    names = {"pickup": "fs_to_pickup", "peak": "fs_to_peak", "cone_abort": "fs_to_abort",
             "follow_start": "fs_to_next"}
    for evs in by_robot.values():
        for i, e in enumerate(evs):
            if e[2] != "follow_start":
                continue
            nxt = next((f[2] for f in evs[i + 1:] if f[2] in names), None)
            out[names[nxt] if nxt else "fs_to_end"] += 1
    return out


def abort_followups(events: list) -> dict[str, float]:
    by_robot: dict[str, list] = defaultdict(list)
    for e in events:
        by_robot[e[1]].append(e)
    to_pick, to_follow, le30, n = [], [], 0, 0
    for evs in by_robot.values():
        for i, e in enumerate(evs):
            if e[2] != "cone_abort":
                continue
            n += 1
            pick = next((f[0] for f in evs[i + 1:] if f[2] == "pickup"), None)
            fol = next((f[0] for f in evs[i + 1:] if f[2] == "follow_start"), None)
            if pick is not None:
                to_pick.append((pick - e[0]) / TPS)
                le30 += (pick - e[0]) <= 30 * TPS
            if fol is not None:
                to_follow.append((fol - e[0]) / TPS)
    nan = math.nan
    return {"abort_to_pickup_s_mean": float(np.mean(to_pick)) if to_pick else nan,
            "abort_pickup_le30_share": le30 / n if n else nan,
            "abort_to_follow_s_mean": float(np.mean(to_follow)) if to_follow else nan}


def abort_triggers(events: list, params: dict, sources: list, decoys: list) -> Counter:
    """Rebuild each robot's suspect memory and classify the stored point behind each cone_abort."""
    r_merge = float(params.get("controller_defense_r_merge", 0.3))
    n_mem = int(params.get("controller_defense_n_mem", 16))
    d_cone = float(params.get("controller_defense_d_cone", 1.0))
    mem: dict[str, list[list[float]]] = defaultdict(list)  # [cx, cy, count]
    last_peak: dict[str, tuple[float, float]] = {}
    out: Counter = Counter()
    for _t, rid, ev, x, y in events:
        pts = mem[rid]
        if ev == "peak":
            last_peak[rid] = (x, y)
        elif ev == "suspect_add":
            x, y = last_peak.get(rid, (x, y))  # the controller stores the peak, not this position
            near = [p for p in pts if math.hypot(x - p[0], y - p[1]) <= r_merge]
            if near:
                p = min(near, key=lambda q: math.hypot(x - q[0], y - q[1]))
                p[0], p[1], p[2] = (p[0] * p[2] + x) / (p[2] + 1), (p[1] * p[2] + y) / (p[2] + 1), p[2] + 1
            else:
                pts.append([x, y, 1])
                if len(pts) > n_mem:
                    pts.pop(0)
        elif ev == "cone_abort":
            cand = [p for p in pts if math.hypot(x - p[0], y - p[1]) <= d_cone]
            if not cand:
                out["abort_trig_none"] += 1
                continue
            p = min(cand, key=lambda q: math.hypot(x - q[0], y - q[1]))
            ds, dd = _dist(p[0], p[1], sources), _dist(p[0], p[1], decoys)
            if min(ds, dd) > NEAR_M:
                out["abort_trig_other"] += 1
            else:  # exclusive: the nearer landmark wins
                out["abort_trig_src" if ds <= dd else "abort_trig_dec"] += 1
    return out


def run_metrics(folder: Path) -> dict[str, float]:
    m = json.loads((folder / "manifest.json").read_text())
    lay = m["layout"]
    sources, decoys = lay["sources"], lay["decoys"][:lay["n_decoys_used"]]
    events = read_events(folder / "events.csv")
    robots = read_robots(folder / "robots.csv")
    out: Counter = Counter({"food": m["metrics"]["food_collected"],
                            "wasted_s": m["metrics"]["wasted_robot_seconds"]})
    for rows in robots.values():
        for _x, _y, state, _f, carrying in rows.values():
            out[f"time_{state}_s"] += 1
            out["carry_s"] += carrying
    last_peak: dict[str, tuple[float, float]] = {}
    for t, rid, ev, x, y in events:
        out[f"n_{ev}"] += 1
        if ev == "peak":
            last_peak[rid] = (x, y)
        elif ev == "suspect_add":
            px, py = last_peak.get(rid, (x, y))  # stored point = the robot's last peak
            ds, dd = _dist(px, py, sources), _dist(px, py, decoys)
            for cut in SUSPECT_CUTS:
                out[f"sus_src_le{int(cut * 100):03d}"] += ds <= cut
            if min(ds, dd) > NEAR_M:
                out["sus_other"] += 1
            else:
                out["sus_cls_src" if ds <= dd else "sus_cls_dec"] += 1
        elif ev == "cone_abort":
            out["abort_pos_src_le150"] += _dist(x, y, sources) <= 1.5
            row = _row_at(robots, t).get(rid)
            if row is not None:
                out["abort_false_trail" if row[3] >= FALSE_SHARE else "abort_true_trail"] += 1
    out.update(follow_outcomes(events))
    out.update(abort_triggers(events, m["params"], sources, decoys))
    res = {k: float(v) for k, v in out.items()}
    res.update(abort_followups(events))
    res.update(peak_outcomes(events, robots, sources,
                             float(m["params"].get("controller_pheromone_t_end", 15))))
    return res


def _contrast(rows: list, name: str, a: dict, b: dict, metric: str, d: int) -> None:
    seeds = sorted(set(a) & set(b))
    if not seeds:
        return
    va = np.array([a[s].get(metric, 0.0) for s in seeds])
    vb = np.array([b[s].get(metric, 0.0) for s in seeds])
    if np.isnan(va).any() or np.isnan(vb).any():
        return
    mean, lo, hi = paired_diff_interval(va, vb)
    rows.append(["contrast", name, d, "", "", metric, f"{mean:.3f}", f"{lo:.3f}", f"{hi:.3f}", len(seeds)])


def _dose(rows: list, name: str, on: dict, off: dict, metric: str) -> None:
    seeds = sorted(set(on) & set(off))
    y = np.array([on[s]["food"] - off[s]["food"] for s in seeds])
    x = np.array([on[s].get(metric, 0.0) for s in seeds])
    if len(seeds) < 3 or x.std() == 0:
        return
    slope = float(np.cov(x, y, ddof=1)[0, 1] / x.var(ddof=1))
    r = float(np.corrcoef(x, y)[0, 1])
    rows.append(["dose", name, 0, 1, "", f"slope_cost_per_{metric}", f"{slope:.4f}", "", "", len(seeds)])
    rows.append(["dose", name, 0, 1, "", f"r_cost_vs_{metric}", f"{r:.3f}", "", "", len(seeds)])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--roots", default=",".join(ROOTS), help="comma list of " + ",".join(ROOTS))
    args = ap.parse_args(argv)
    data: dict[str, dict[tuple[int, int], dict[int, dict[str, float]]]] = {}
    rows: list[list] = []
    for name in args.roots.split(","):
        rel, seeds = ROOTS[name]
        cells: dict[tuple[int, int], dict[int, dict[str, float]]] = defaultdict(dict)
        for (d, de, s), folder in sorted(select_runs(PROJECT / rel, seeds).items()):
            met = run_metrics(folder)
            cells[(d, de)][s] = met
            rows.extend(["run", name, d, de, s, k, f"{v:.4f}", "", "", 1] for k, v in sorted(met.items()))
        for (d, de), by_seed in sorted(cells.items()):
            for k in sorted({k for m in by_seed.values() for k in m}):
                vals = [m.get(k, 0.0) for m in by_seed.values()]
                vals = [v for v in vals if not math.isnan(v)]
                if vals:
                    rows.append(["cell", name, d, de, "", k, f"{np.mean(vals):.4f}", "", "", len(vals)])
        data[name] = cells
        print(f"{name}: {sum(len(v) for v in cells.values())} runs", file=sys.stderr)
    paired = ("food", "n_pickup", "carry_s", "n_follow_start", "time_RETURN_s", "time_SEARCH_s", "time_FOLLOW_s",
              "time_END_SEARCH_s", "wasted_s")
    for name, cells in data.items():  # defense on minus off, per d, same root
        for d in (0, 1, 2, 4):
            for metric in paired:
                if (d, 0) in cells and (d, 1) in cells:
                    _contrast(rows, f"{name}:on-off", cells[(d, 1)], cells[(d, 0)], metric, d)
        if (0, 1) in cells:
            for metric in ("sus_src_le100", "n_cone_abort", "abort_trig_src"):
                _dose(rows, name, cells[(0, 1)], cells[(0, 0)], metric)
    if "lock10" in data and "lock0" in data:  # what the lockout itself adds, defense on, per d
        for d in (0, 1, 2, 4):
            for metric in paired + ("n_cone_abort", "sus_src_le100", "abort_to_pickup_s_mean"):
                _contrast(rows, "lock10-lock0:on", data["lock10"].get((d, 1), {}),
                          data["lock0"].get((d, 1), {}), metric, d)
    if "v3" in data and "lock0" in data:  # d = 0 cost on 30 seeds of v3-equal code (invariance check)
        on = {**data["v3"][(0, 1)], **data["lock0"][(0, 1)]}
        off = {**data["v3"][(0, 0)], **data["lock0"][(0, 0)]}
        _contrast(rows, "v3+lock0:on-off", on, off, "food", 0)
        _dose(rows, "v3+lock0", on, off, "sus_src_le100")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
