"""M5 step-0 kill check for defense v5 (confirm-twice), from saved logs only (results/real/v5_killcheck.md).

Usage: v5_killcheck.py [--out FILE]
Reads manifest.json, events.csv and robots.csv. numpy and stdlib only. No model, no simulation.
Writes one long CSV (default results/real/v5_killcheck.csv) and prints the verdict line.

Question (decisions/2026-11-11_fable_tracks.md, M5 step 0):
  d = 0: how many confirmed (count >= 2) wrong points per run would private confirm-twice memory make?
  d = 2: per decoy, how many robots fail twice there, and when?
  Kill rule (Fable, pre-registered): mean confirmed source points per d = 0 run > 7.2 -> switch to A'.

Roots
  off_lock0  runs/sweep_v2_lock0  def 0, seeds 11-30  primary (the defense-off runs; sweep_v2 def 0 is the same set)
  off_v3     runs/sweep           def 0, seeds 1-10   supplementary, outside the kill rule
  on_lock0   runs/sweep_v2_lock0  def 1, seeds 11-30  calibration only: suspect_add is ground truth there

Failure = a peak with no pickup by the same robot within t_end (+ SLACK ticks). Peaks whose window runs past
the run end are dropped. The point is the peak position (the controller stores m_cPeakPos).
Validity (only a valid peak calls AddSuspect; the off logs carry no flag), rebuilt per peak:
  dur    peak tick - the robot's last follow_start tick >= t_follow_min * TPS   (exact)
  valid  dur, and robots.csv here(peak second) >= 2 * max(here(follow_start second), theta_on)  (1 s rows)
Variants: all (every failed peak, upper bound), dur, valid (primary).
Memory replay copies AddSuspect (pheromone_forager_defense.cpp): first point in insertion order within r_merge,
count-weighted centroid, oldest dropped past n_mem. Every kept failure enters memory, not only near sources.
Policy A: point active at count 2. Policy Aprime: also a pickup by the same robot within r_merge clears a
pending (count 1) point. Aprime is context only, outside the kill rule.
Class of a point: nearest landmark (source or active decoy) within 1.0 m of the centroid at activation
(same rule as sus_cls_src in failure_analysis.py).

Output columns: scope, root, d, seed, variant, item, metric, value, lo, hi, n
  scope point   one row per (run, robot, point) and metric, policy A and Aprime
  scope decoy   per (run, decoy)
  scope run     per run
  scope cell    mean over seeds, 95 % bootstrap interval (10,000 resamples, rng seed 0)
  scope cell_decoy  decoy times (first_fail_s, first_confirm_s, t2_mean_s, gap_mean_s): mean over the
                (seed, decoy) pairs that have a value; n = "pairs with a value / all pairs"
  scope calib   on_lock0 d = 0: predicted validity against observed suspect_add, per run, variant|subset
                (subset no_mask = peaks before the robot's first suspect_add); calib_sum = summed over runs
  point metrics count, t_first_s, t_second_s, t_out_s, cleared, active (0/1), cls (at activation, else final)
  run metrics   fail_src_k1, pts_<kind> (distinct robot points), act_<kind>, fail3plus_<kind>, act_<kind>_s
  scope check   off_lock0 against sweep_v2 def 0: food equal per (d, seed)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from failure_analysis import NEAR_M, PROJECT, TPS, read_events, select_runs

DEFAULT_OUT = PROJECT / "results" / "real" / "v5_killcheck.csv"
KILL_LINE = 7.2          # Fable, M5: half of 14.45 wrong suspects per d = 0 run (failure_analysis.md Table 3)
K_CONFIRM = 2            # D-039: k = 2, fixed
N_PRIMARY = 20           # off_lock0 d = 0, seeds 11-30
SLACK = 2                # ticks; the timeout fires at t_end * TPS or one tick later
VARIANTS = ("all", "dur", "valid")
POLICIES = ("A", "Aprime")
PRIMARY = ("valid", "A")
UPPER = ("all", "A")
ROOTS = {"off_lock0": ("runs/sweep_v2_lock0", range(11, 31), 0),
         "off_v3": ("runs/sweep", range(1, 11), 0),
         "on_lock0": ("runs/sweep_v2_lock0", range(11, 31), 1)}
COLUMNS = ("scope", "root", "d", "seed", "variant", "item", "metric", "value", "lo", "hi", "n")


def read_here(path: Path) -> dict[int, dict[str, float]]:
    """tick -> robot -> raw pheromone reading `here`, honest robots only (1 s rows)."""
    out: dict[int, dict[str, float]] = defaultdict(dict)
    with path.open(newline="") as fh:
        r = csv.reader(fh)
        h = {c: i for i, c in enumerate(next(r))}
        for row in r:
            if row[h["role"]] == "honest":
                out[int(row[h["tick"]])][row[h["robot_id"]]] = float(row[h["here"]])
    return out


def _here_at(here: dict, tick: int, rid: str) -> float | None:
    return here.get(max(TPS, tick // TPS * TPS), {}).get(rid)


def classify(x: float, y: float, sources: list, decoys: list) -> str:
    """'src', 'dec<j>' or 'other': nearest landmark within NEAR_M, a tie goes to the source."""
    ds = min((math.hypot(x - p[0], y - p[1]) for p in sources), default=math.inf)
    dd = [math.hypot(x - p[0], y - p[1]) for p in decoys]
    j = int(np.argmin(dd)) if dd else -1
    if min(ds, dd[j] if dd else math.inf) > NEAR_M:
        return "other"
    return "src" if not dd or ds <= dd[j] else f"dec{j}"


def peak_records(events: list, here: dict, params: dict, n_ticks: int) -> list[dict]:
    """One record per peak whose END_SEARCH window ends inside the run."""
    end = int(float(params["controller_pheromone_t_end"]) * TPS)
    min_follow = int(float(params["controller_pheromone_t_follow_min"]) * TPS)
    theta_on = float(params["controller_pheromone_theta_on"])
    by_robot: dict[str, list] = defaultdict(list)
    for e in events:
        by_robot[e[1]].append(e)
    recs = []
    for rid, evs in by_robot.items():
        last_follow = None
        first_sus = min((f[0] for f in evs if f[2] == "suspect_add"), default=math.inf)
        for i, (t, _r, ev, x, y) in enumerate(evs):
            if ev == "follow_start":
                last_follow = t
            if ev != "peak" or t + end + SLACK > n_ticks:
                continue
            later = [f for f in evs[i + 1:] if f[0] <= t + end + SLACK]
            # The timeout fires at t + end (hb_3 sample: peak 3567, follow_start 3718), so a later pickup
            # comes after AddSuspect. SLACK applies to matching suspect_add only.
            picked = any(f[2] == "pickup" and f[0] <= t + end for f in later)
            suspect = any(f[2] == "suspect_add" and abs(f[0] - (t + end)) <= SLACK for f in later)
            dur = last_follow is not None and t - last_follow >= min_follow
            h_pk = _here_at(here, t, rid)
            h_in = _here_at(here, last_follow, rid) if last_follow is not None else None
            valid = dur and h_pk is not None and h_in is not None and h_pk >= 2.0 * max(h_in, theta_on)
            recs.append({"rid": rid, "t": t, "x": x, "y": y, "t_fail": t + end, "failed": not picked,
                         "all": True, "dur": dur, "valid": valid, "suspect": suspect,
                         "no_mask": t < first_sus})  # defense-on runs: memory empty, reading unmasked
    return recs


def replay(fails: list, pickups: list, r_merge: float, n_mem: int, clear: bool) -> list[dict]:
    """One robot's private memory over time. Returns every point it ever held."""
    stream = sorted([(f["t_fail"], 0, f["x"], f["y"]) for f in fails] +
                    [(t, 1, x, y) for t, x, y in pickups])
    held: list[dict] = []
    gone: list[dict] = []
    for t, kind, x, y in stream:
        if kind == 1:
            if clear:
                for p in [p for p in held if p["count"] < K_CONFIRM and
                          math.hypot(p["x"] - x, p["y"] - y) <= r_merge]:
                    held.remove(p)
                    p["t_out"], p["cleared"] = t, 1
                    gone.append(p)
            continue
        for p in held:  # AddSuspect: first match in insertion order, not the nearest
            if math.hypot(p["x"] - x, p["y"] - y) <= r_merge:
                c = p["count"]
                p["x"], p["y"], p["count"] = (p["x"] * c + x) / (c + 1), (p["y"] * c + y) / (c + 1), c + 1
                if p["count"] == K_CONFIRM:
                    p["t_second"], p["ax"], p["ay"] = t, p["x"], p["y"]
                break
        else:
            held.append({"x": x, "y": y, "count": 1, "t_first": t, "t_second": None, "t_out": None,
                         "cleared": 0})
            if len(held) > n_mem:
                old = held.pop(0)
                old["t_out"] = t
                gone.append(old)
    return gone + held


def run_rows(root: str, d: int, seed: int, folder: Path) -> tuple[list, dict]:
    """Rows for one run, and its per-run metrics keyed by (variant, policy)."""
    m = json.loads((folder / "manifest.json").read_text())
    params, lay = m["params"], m["layout"]
    sources, decoys = lay["sources"], lay["decoys"][:lay["n_decoys_used"]]
    n_ticks = int(m["metrics"]["ticks"])
    events = read_events(folder / "events.csv")
    recs = peak_records(events, read_here(folder / "robots.csv"), params, n_ticks)
    r_merge = float(params["controller_defense_r_merge"])
    n_mem = int(params["controller_defense_n_mem"])
    pickups: dict[str, list] = defaultdict(list)
    for t, rid, ev, x, y in events:
        if ev == "pickup":
            pickups[rid].append((t, x, y))
    rows, per_run = [], {}
    if root.startswith("on_"):  # calibration: predicted validity of failed peaks against suspect_add
        failed = [r for r in recs if r["failed"]]
        # Subset no_mask: peaks before the robot's first suspect_add. The controller tests the masked
        # reading, robots.csv logs the raw one, so only this subset tests the rebuild cleanly.
        for subset, pool in (("all_peaks", failed), ("no_mask", [r for r in failed if r["no_mask"]])):
            for v in VARIANTS:
                for name, pred, obs in (("tp", 1, 1), ("fp", 1, 0), ("fn", 0, 1), ("tn", 0, 0)):
                    cnt = sum(1 for r in pool if bool(r[v]) == bool(pred) and bool(r["suspect"]) == bool(obs))
                    rows.append(["calib", root, d, seed, f"{v}|{subset}", "", name, cnt, "", "", 1])
        obs = sum(1 for r in failed if r["suspect"] and classify(r["x"], r["y"], sources, decoys) == "src")
        rows.append(["calib", root, d, seed, "observed", "", "suspect_src", obs, "", "", 1])
        return rows, per_run
    for v in VARIANTS:
        kept = [r for r in recs if r["failed"] and r[v]]
        n_fail_src = sum(1 for r in kept if classify(r["x"], r["y"], sources, decoys) == "src")
        for pol in POLICIES:
            met: dict[str, float] = defaultdict(float)
            met["fail_src_k1"] = n_fail_src  # k = 1 prediction, comparable to sus_cls_src
            dec: dict[str, dict] = {f"dec{j}": {"r1": set(), "r2": set(), "t2": [], "gap": []}
                                    for j in range(len(decoys))}
            for r in kept:
                c = classify(r["x"], r["y"], sources, decoys)
                if c in dec:
                    dec[c]["r1"].add(r["rid"])
                    dec[c].setdefault("first_fail", r["t_fail"])
                    dec[c]["first_fail"] = min(dec[c]["first_fail"], r["t_fail"])
            for rid in sorted({r["rid"] for r in kept}):
                pts = replay([r for r in kept if r["rid"] == rid], pickups[rid], r_merge, n_mem, pol == "Aprime")
                for k, p in enumerate(pts):
                    active = p["t_second"] is not None
                    # Class at activation if confirmed, else at the final centroid.
                    cls = classify(p["ax"], p["ay"], sources, decoys) if active else \
                        classify(p["x"], p["y"], sources, decoys)
                    kind = "src" if cls == "src" else "dec" if cls.startswith("dec") else "other"
                    item = f"{rid}#{k}"
                    for name, val in (("count", p["count"]), ("t_first_s", p["t_first"] / TPS),
                                      ("t_second_s", p["t_second"] / TPS if active else ""),
                                      ("t_out_s", p["t_out"] / TPS if p["t_out"] else ""),
                                      ("cleared", p["cleared"]), ("active", int(active)), ("cls", cls)):
                        rows.append(["point", root, d, seed, f"{v}/{pol}", item, name, val, "", "", 1])
                    met["cleared"] += p["cleared"]
                    met[f"pts_{kind}"] += 1  # distinct (robot, location) points, pending or confirmed
                    if not active:
                        met["pending_end"] += p["t_out"] is None
                        continue
                    met[f"act_{kind}"] += 1
                    met[f"fail3plus_{kind}"] += p["count"] - K_CONFIRM
                    met[f"act_{kind}_s"] += ((p["t_out"] or n_ticks) - p["t_second"]) / TPS
                    if cls in dec:
                        dec[cls]["r2"].add(rid)
                        dec[cls]["t2"].append(p["t_second"] / TPS)
                        dec[cls]["gap"].append((p["t_second"] - p["t_first"]) / TPS)
            for j, (name, s) in enumerate(dec.items()):
                vals = {"robots_ge1": len(s["r1"]), "robots_ge2": len(s["r2"]),
                        "first_fail_s": s["first_fail"] / TPS if "first_fail" in s else math.nan,
                        "first_confirm_s": min(s["t2"]) if s["t2"] else math.nan,
                        "t2_mean_s": float(np.mean(s["t2"])) if s["t2"] else math.nan,
                        "gap_mean_s": float(np.mean(s["gap"])) if s["gap"] else math.nan}
                for k, val in vals.items():
                    rows.append(["decoy", root, d, seed, f"{v}/{pol}", name, k, f"{val:.4f}", "", "", 1])
                    if k.startswith("robots_"):  # counts average per decoy; times go to scope cell_decoy
                        met[f"dec_{k}"] += val / len(dec)
            per_run[(v, pol)] = dict(met)
            rows.extend(["run", root, d, seed, f"{v}/{pol}", "", k, f"{val:.4f}", "", "", 1]
                        for k, val in sorted(met.items()))
    return rows, per_run


def boot(vals: list[float]) -> tuple[float, float, float]:
    a = np.array([v for v in vals if not math.isnan(v)])
    if a.size == 0:
        return math.nan, math.nan, math.nan
    idx = np.random.default_rng(0).integers(0, a.size, (10_000, a.size))
    lo, hi = np.percentile(a[idx].mean(axis=1), [2.5, 97.5])
    return float(a.mean()), float(lo), float(hi)


def check_same_off(rows: list) -> None:
    """off_lock0 and sweep_v2 def 0 should be the same runs: compare food per (d, seed)."""
    a = select_runs(PROJECT / "runs/sweep_v2_lock0", range(11, 31))
    b = select_runs(PROJECT / "runs/sweep_v2", range(11, 31))
    keys = sorted(k for k in set(a) & set(b) if k[1] == 0)
    food = lambda f: json.loads((f / "manifest.json").read_text())["metrics"]["food_collected"]
    diff = sum(food(a[k]) != food(b[k]) for k in keys)
    rows.append(["check", "off_lock0|sweep_v2", "", "", "", "", "food_mismatch_runs", diff, "", "", len(keys)])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    rows: list[list] = []
    cells: dict[tuple, list[dict]] = defaultdict(list)
    for root, (rel, seeds, defense) in ROOTS.items():
        n = 0
        for (d, de, s), folder in sorted(select_runs(PROJECT / rel, seeds).items()):
            if de != defense or d not in (0, 2) or (root.startswith("on_") and d != 0):
                continue
            r, per_run = run_rows(root, d, s, folder)
            rows.extend(r)
            for key, met in per_run.items():
                cells[(root, d, key)].append(met)
            n += 1
        print(f"{root}: {n} runs", file=sys.stderr)
    for (root, d, (v, pol)), mets in sorted(cells.items()):
        for k in sorted({k for m in mets for k in m}):
            mean, lo, hi = boot([m.get(k, 0.0) for m in mets])
            rows.append(["cell", root, d, "", f"{v}/{pol}", "", k, f"{mean:.4f}", f"{lo:.4f}", f"{hi:.4f}",
                         len(mets)])
    by_decoy: dict[tuple, list[float]] = defaultdict(list)  # times: mean over (seed, decoy) pairs that have one
    for r in rows:
        if r[0] == "decoy" and r[6].endswith("_s"):
            by_decoy[(r[1], r[2], r[4], r[6])].append(float(r[7]))
    for (root, d, var, k), vals in sorted(by_decoy.items()):
        mean, lo, hi = boot(vals)
        n_has = sum(1 for x in vals if not math.isnan(x))
        rows.append(["cell_decoy", root, d, "", var, "", k, f"{mean:.4f}", f"{lo:.4f}", f"{hi:.4f}",
                     f"{n_has}/{len(vals)}"])
    sums: dict[tuple, list[float]] = defaultdict(list)  # calibration counts summed over runs
    for r in rows:
        if r[0] == "calib":
            sums[(r[1], r[2], r[4], r[6])].append(float(r[7]))
    for (root, d, var, k), vals in sorted(sums.items()):
        rows.append(["calib_sum", root, d, "", var, "", k, f"{sum(vals):.0f}", "", "", len(vals)])
    check_same_off(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")
    n_prim = len(cells.get(("off_lock0", 0, PRIMARY), []))
    prim = boot([m.get("act_src", 0.0) for m in cells.get(("off_lock0", 0, PRIMARY), [])])
    upper = boot([m.get("act_src", 0.0) for m in cells.get(("off_lock0", 0, UPPER), [])])
    if n_prim != N_PRIMARY or math.isnan(prim[0]) or math.isnan(upper[0]):  # fail closed
        print(f"NO VERDICT: off_lock0 d=0 has {n_prim} runs (need {N_PRIMARY}) or a non-finite mean")
        return 1
    over = (prim[0] > KILL_LINE, upper[0] > KILL_LINE)
    verdict = ("switch to A'" if all(over) else "proceed with A (k = 2)" if not any(over)
               else "STRADDLE: primary and upper bound fall on opposite sides of 7.2, Fable decides")
    print(f"VERDICT n={n_prim} d=0 confirmed wrong points per run: primary (valid) {prim[0]:.2f} "
          f"[{prim[1]:.2f}, {prim[2]:.2f}], upper (all) {upper[0]:.2f} [{upper[1]:.2f}, {upper[2]:.2f}], "
          f"line > {KILL_LINE} -> {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
