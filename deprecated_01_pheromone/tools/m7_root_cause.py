"""Root cause of the M7 scaling result (task M7-04, results/real/scale/root_cause.md). Saved runs only.

Usage: m7_root_cause.py [--arms off,v3,v5] [--ns 20,40] [--out FILE]
Reads manifest.json, events.csv, robots.csv and ticks.csv of runs/m7_scale/<arm>_n<N>/. numpy and stdlib.
No model, no simulation. Writes one long CSV (default results/real/scale/root_cause.csv) and prints a summary.
--arms and --ns only split the work if one pass hits the 300 s limit. A partial pass writes run and cell rows
to root_cause_part_<arms>_n<ns>.csv and never overwrites root_cause.csv. Contrasts need both N and the off arm.

Columns: scope, arm, n, d, seed, metric, value, lo, hi, n_seeds
  d is the level: d0 (no detractor) or d10 (2 at N 20, 4 at N 40)
  scope run       one value per run
  scope cell      mean over the 30 seeds (lo, hi empty)
  scope contrast  n "40-20": paired N 40 minus N 20 on seed, 95 % bootstrap (g2_stats.paired_diff_interval)
  scope delta     arm minus off on the same seed, per honest robot (d_<metric>). Cell mean, then a contrast row
  scope split     (d) G/N = R * L/N. R = mean G / mean L. R_n20, R_n40, R_diff, drop_from_L, drop_from_R,
                  one seed bootstrap index for all terms (drop_from_L + drop_from_R = the G/N drop)
  scope dd        v5-v3: v5 drop minus v3 drop (paired on seed). v5/v3: act_share ratio of means, N 40 minus 20
  scope check     verdict.json reprint, layout pairing, and the N 20 k2t10 d 2 / d 4 rows of v5/g2_stats.csv

Per-run metrics, honest robots. _pr = per honest robot, _prd = per honest robot per active decoy, _pd = per decoy
  food                         manifest food_collected
  pickup_pr, carry_pr          pickups, carrying seconds
  ffollow_pr, tfollow_pr       FOLLOW seconds with false_share >= 0.5 / below (robots.csv, 1 s rows)
  search_pr                    SEARCH seconds
  pk_dec_prd                   peaks whose nearest landmark within 1 m is a decoy (exposure, also with defense off)
  pk_src_pr                    peaks whose nearest landmark within 1 m is a source
  src_fail_share               d0 only: share of near-source peaks with no pickup in t_end + 1 s (peak_outcomes)
  crowd_src_fail, crowd_src_ok d0 only: other honest robots within 0.5 m of the source, failed / successful peaks
  det_reach_pd                 detractor decoy_reach events per decoy (trail refresh rate)
  pher_false_pd, pher_true     ticks.csv mean pher_false_sum per decoy, mean pher_true_sum
Defense arms only (k = confirm_k of the arm; stored point = the robot's last peak, as v5_mechanism):
  sus_src_pr, sus_dec_prd      stored failures at a source / at a decoy
  act_src_pr, act_dec_prd      calls where Count reaches k (v5_mechanism.replay_k), class at the centroid
  fail1_share, fail2_share     per decoy, robots with >= 1 / >= 2 stored failures there, / N. Mean over decoys
  act_share                    per decoy, robots with an activation there by run end, / N
  cover_time                   per decoy, sum over robots of (T - first activation) / T, / N. Censored at T = 0 share
  t_first_act_s                per decoy, first activation by any robot, seconds. T if none (censored)
  abort_pr, abort_src_pr, abort_dec_pr   cone_aborts, by class of the nearest ACTIVE point within d_cone
  abort_none_pr                cone_aborts with no active point within d_cone (replay check, should be near 0)
  abort_true_pr                every cone_abort with false_share < 0.5 at that second (a true trail)
  lock_true_s_pr               t_lock * abort_true_pr: upper bound of lockout seconds after a true-trail abort
  abort_to_pickup_s            failure_analysis.abort_followups
  replay_ok                    1 if the replay holds ticks.csv suspects_total at every row and equals replay_k
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path

import numpy as np

from failure_analysis import FALSE_SHARE, TPS, abort_followups, peak_outcomes, read_events, read_robots
from g2_stats import BOOT_SEED, N_BOOT, paired_diff_interval
from v5_killcheck import classify
from v5_mechanism import held_matches, replay_k, stored_points
from v6_common import ARMS
from v7_common import ARM_ORDER, CONFIRM_BASE, CONFIRM_SEEDS, NS, RESULTS, VERDICT, cell_root, read_scale_runs

DEFAULT_OUT = RESULTS / "root_cause.csv"
COLUMNS = ("scope", "arm", "n", "d", "seed", "metric", "value", "lo", "hi", "n_seeds")
LEVELS = ("d0", "d10")
DELTA_METRICS = ("food", "ffollow_pr", "pickup_pr", "carry_pr", "search_pr")
V5_G2 = RESULTS.parent / "v5" / "g2_stats.csv"  # N 20, seeds 221-260: k2t10 at d 2 (1 per decoy) and d 4 (2 per decoy)


def replay_robot(evs: list, k: int, r_merge: float, n_mem: int, d_cone: float
                 ) -> tuple[list, list, list]:
    """One robot's memory in event order. Same merge loop as v5_mechanism.replay_k.

    Returns activations (tick, x, y), each cone_abort as (tick, active point (x, y) or None),
    and the (insert, evict) spans for held_matches.
    """
    held: list[dict] = []
    acts: list[tuple[int, float, float]] = []
    trig: list[tuple[int, tuple[float, float] | None]] = []
    spans: list[list] = []
    last_peak: tuple[float, float] | None = None
    for t, _rid, ev, x, y in evs:
        if ev == "peak":
            last_peak = (x, y)
        elif ev == "suspect_add":
            px, py = last_peak or (x, y)
            for p in held:
                if math.hypot(p["x"] - px, p["y"] - py) <= r_merge:
                    c = p["count"]
                    p["x"], p["y"], p["count"] = (p["x"] * c + px) / (c + 1), (p["y"] * c + py) / (c + 1), c + 1
                    if p["count"] == k:
                        acts.append((t, p["x"], p["y"]))
                    break
            else:
                span = [t, None]
                held.append({"x": px, "y": py, "count": 1, "span": span})
                spans.append(span)
                if k == 1:
                    acts.append((t, px, py))
                if len(held) > n_mem:
                    held.pop(0)["span"][1] = t
        elif ev == "cone_abort":
            cand = [p for p in held if p["count"] >= k and math.hypot(x - p["x"], y - p["y"]) <= d_cone]
            p = min(cand, key=lambda q: math.hypot(x - q["x"], y - q["y"])) if cand else None
            trig.append((t, (p["x"], p["y"]) if p else None))
    return acts, trig, [(a, b) for a, b in spans]


def detractor_reach(path: Path) -> list[tuple[float, float]]:
    with path.open(newline="") as fh:
        r = csv.reader(fh)
        next(r)
        return [(float(x), float(y)) for _t, rid, ev, x, y in r if rid.startswith("dt_") and ev == "decoy_reach"]


def tick_means(path: Path) -> tuple[float, float]:
    f, t, n = 0.0, 0.0, 0
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            f, t, n = f + float(row["pher_false_sum"]), t + float(row["pher_true_sum"]), n + 1
    return f / n, t / n


def decoy_index(cls: str) -> int | None:
    return int(cls[3:]) if cls.startswith("dec") else None


def run_metrics(folder: Path, arm: str) -> tuple[dict[str, float], tuple]:
    """Per-run metrics (module doc) and the layout, for the pairing check."""
    m = json.loads((folder / "manifest.json").read_text())
    p, lay = m["params"], m["layout"]
    n = int(p["n_honest"])
    sources, decoys = lay["sources"], lay["decoys"][:lay["n_decoys_used"]]
    n_dec, T = len(decoys), int(m["metrics"]["ticks"])
    events = read_events(folder / "events.csv")
    robots = read_robots(folder / "robots.csv")
    out: dict[str, float] = {"food": float(m["metrics"]["food_collected"])}
    acc: dict[str, float] = defaultdict(float)
    for rows in robots.values():
        for _x, _y, state, fs, carrying in rows.values():
            acc["carry"] += carrying
            acc["search"] += state == "SEARCH"
            if state == "FOLLOW":
                acc["ffollow" if fs >= FALSE_SHARE else "tfollow"] += 1
    by_robot: dict[str, list] = defaultdict(list)
    for e in events:
        by_robot[e[1]].append(e)
        if e[2] == "pickup":
            acc["pickup"] += 1
        elif e[2] == "peak":
            cls = classify(e[3], e[4], sources, decoys)
            acc["pk_dec" if cls.startswith("dec") else ("pk_src" if cls == "src" else "pk_other")] += 1
    for key in ("carry", "search", "ffollow", "tfollow", "pickup", "pk_src"):
        out[f"{key}_pr"] = acc[key] / n
    if not n_dec:  # crowding is read at d0 only (the slow part of a run)
        pko = peak_outcomes(events, robots, sources, float(p["controller_pheromone_t_end"]))
        n_pk = pko["pk_src_pickup"] + pko["pk_src_suspect"] + pko["pk_src_neither"]
        out["src_fail_share"] = 1 - pko["pk_src_pickup"] / n_pk if n_pk else math.nan
        fail_c = [(pko[f"pk_src_{c}"], pko[f"pkcrowd_{c}"]) for c in ("suspect", "neither") if pko[f"pk_src_{c}"]]
        out["crowd_src_fail"] = sum(a * b for a, b in fail_c) / sum(a for a, _ in fail_c) if fail_c else math.nan
        out["crowd_src_ok"] = pko["pkcrowd_pickup"]
    pf, pt = tick_means(folder / "ticks.csv")
    out["pher_true"] = pt
    if n_dec:
        out["pk_dec_prd"] = acc["pk_dec"] / (n * n_dec)
        out["det_reach_pd"] = len(detractor_reach(folder / "events.csv")) / n_dec
        out["pher_false_pd"] = pf / n_dec
    if ARMS[arm].defense:
        out.update(defense_metrics(by_robot, robots, p, sources, decoys, n, T, folder))
    return out, (tuple(map(tuple, sources)), tuple(map(tuple, decoys)))


def defense_metrics(by_robot: dict, robots: dict, p: dict, sources: list, decoys: list, n: int, T: int,
                    folder: Path) -> dict[str, float]:
    k = int(float(p["controller_defense_confirm_k"]))
    r_merge, n_mem = float(p["controller_defense_r_merge"]), int(p["controller_defense_n_mem"])
    d_cone, t_lock = float(p["controller_defense_d_cone"]), float(p["controller_defense_t_lock"])
    n_dec = len(decoys)
    acc: dict[str, float] = defaultdict(float)
    fails: dict[int, list[int]] = defaultdict(list)    # decoy -> per robot failure counts
    first_act: dict[int, list[int]] = defaultdict(list)  # decoy -> per robot first activation tick
    spans: list = []
    same = True
    stored = stored_points([e for evs in by_robot.values() for e in evs])
    for rid, evs in by_robot.items():
        acts, trig, sp = replay_robot(evs, k, r_merge, n_mem, d_cone)
        spans += sp
        same &= acts == replay_k(stored.get(rid, []), k, r_merge, n_mem)[0]
        per_dec: dict[int, int] = defaultdict(int)
        for _t, x, y in stored.get(rid, []):
            cls = classify(x, y, sources, decoys)
            acc["sus_src" if cls == "src" else ("sus_dec" if cls.startswith("dec") else "sus_other")] += 1
            if (j := decoy_index(cls)) is not None:
                per_dec[j] += 1
        for j, c in per_dec.items():
            fails[j].append(c)
        act_dec: dict[int, int] = {}
        for t, x, y in acts:
            cls = classify(x, y, sources, decoys)
            acc["act_src" if cls == "src" else ("act_dec" if cls.startswith("dec") else "act_other")] += 1
            if (j := decoy_index(cls)) is not None and j not in act_dec:
                act_dec[j] = t
        for j, t in act_dec.items():
            first_act[j].append(t)
        for t, pt in trig:
            acc["abort"] += 1
            if pt is None:
                acc["abort_none"] += 1  # no active point in d_cone: the replay missed a trigger
            else:
                cls = classify(pt[0], pt[1], sources, decoys)
                acc["abort_src" if cls == "src" else ("abort_dec" if cls.startswith("dec") else "abort_oth")] += 1
            row = robots.get(max(TPS, t // TPS * TPS), {}).get(rid)
            if row is not None and row[3] < FALSE_SHARE:
                acc["abort_true"] += 1
    out = {f"{key}_pr": acc[key] / n
           for key in ("sus_src", "act_src", "abort", "abort_src", "abort_dec", "abort_none", "abort_true")}
    out["lock_true_s_pr"] = t_lock * out["abort_true_pr"]
    out.update(abort_followups([e for evs in by_robot.values() for e in evs]))
    out["abort_to_pickup_s"] = out.pop("abort_to_pickup_s_mean")
    out.pop("abort_pickup_le30_share")
    out.pop("abort_to_follow_s_mean")
    out["replay_ok"] = float(same and held_matches(spans, folder / "ticks.csv"))
    if n_dec:
        js = range(n_dec)
        out["sus_dec_prd"] = acc["sus_dec"] / (n * n_dec)
        out["act_dec_prd"] = acc["act_dec"] / (n * n_dec)
        out["fail1_share"] = float(np.mean([len(fails[j]) / n for j in js]))
        out["fail2_share"] = float(np.mean([sum(c >= 2 for c in fails[j]) / n for j in js]))
        out["act_share"] = float(np.mean([len(first_act[j]) / n for j in js]))
        out["cover_time"] = float(np.mean([sum(T - t for t in first_act[j]) / T / n for j in js]))
        out["t_first_act_s"] = float(np.mean([min(first_act[j], default=T) / TPS for j in js]))
    return out


def split_terms(g20: np.ndarray, loss20: np.ndarray, g40: np.ndarray, loss40: np.ndarray) -> dict[str, float]:
    """G/N = R * L/N on means. R = mean G / mean L. drop_from_L + drop_from_R = mean G40 - mean G20 exactly."""
    l20, l40 = loss20.mean(), loss40.mean()
    r20, r40 = g20.mean() / l20, g40.mean() / l40
    return {"R_n20": r20, "R_n40": r40, "R_diff": r40 - r20,
            "drop_from_L": r20 * (l40 - l20), "drop_from_R": (r40 - r20) * l40}


def paired_boot(fn: Callable[..., dict[str, float]], *arrays: np.ndarray) -> dict[str, tuple[float, float, float]]:
    """Point value and 95 % percentile interval of every term of fn, one seed index for all arrays and terms."""
    point = fn(*arrays)
    idx = np.random.default_rng(BOOT_SEED).integers(0, len(arrays[0]), size=(N_BOOT, len(arrays[0])))
    draws = [fn(*(a[i] for a in arrays)) for i in idx]
    out = {}
    for k, v in point.items():
        lo, hi = np.nanpercentile([d[k] for d in draws], [2.5, 97.5])
        out[k] = (float(v), float(lo), float(hi))
    return out


def share_ratio(v5_20: np.ndarray, v3_20: np.ndarray, v5_40: np.ndarray, v3_40: np.ndarray) -> dict[str, float]:
    """(a) the k = 2 part: v5 act_share / v3 act_share (ratio of means), N 40 minus N 20."""
    r20, r40 = v5_20.mean() / v3_20.mean(), v5_40.mean() / v3_40.mean()
    return {"act_share_v5_over_v3_n20": r20, "act_share_v5_over_v3_n40": r40, "act_share_v5_over_v3_diff": r40 - r20}


def series(data: dict, arm: str, n: int, lvl: str, metric: str) -> np.ndarray:
    return np.array([data[(arm, n, lvl)][s].get(metric, math.nan) for s in CONFIRM_SEEDS])


def fmt(v: float | None) -> str:
    return "" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.4f}"


def contrast_row(rows: list, scope: str, arm: str, metric: str, lvl: str, a20: np.ndarray, a40: np.ndarray) -> None:
    ok = ~(np.isnan(a20) | np.isnan(a40))
    if ok.sum() < 3:
        return
    mean, lo, hi = paired_diff_interval(a40[ok], a20[ok])
    rows.append([scope, arm, "40-20", lvl, "", metric, fmt(mean), fmt(lo), fmt(hi), int(ok.sum())])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arms", default=",".join(ARM_ORDER))
    ap.add_argument("--ns", default=",".join(map(str, NS)))
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    arms, ns = args.arms.split(","), [int(x) for x in args.ns.split(",")]
    full = set(arms) == set(ARM_ORDER) and set(ns) == set(NS)
    if args.out is None:  # a partial pass never overwrites the full output
        args.out = DEFAULT_OUT if full else RESULTS / f"root_cause_part_{'-'.join(arms)}_n{'-'.join(map(str, ns))}.csv"
    data: dict[tuple[str, int, str], dict[int, dict[str, float]]] = defaultdict(dict)
    layouts: dict[tuple[bool, int], set] = defaultdict(set)
    rows: list[list] = []
    for arm in arms:
        for n in ns:
            runs = read_scale_runs(cell_root(CONFIRM_BASE, arm, n), arm, n)
            for (d, s), (_food, folder) in sorted(runs.items()):
                if s not in CONFIRM_SEEDS:
                    continue
                lvl = "d0" if d == 0 else "d10"
                met, lay = run_metrics(folder, arm)
                layouts[(d > 0, s)].add(lay)
                data[(arm, n, lvl)][s] = met
                rows.extend(["run", arm, n, lvl, s, k, fmt(v), "", "", 1] for k, v in sorted(met.items()))
            print(f"{arm} n{n}: {len(runs)} runs", file=sys.stderr)
    for (arm, n, lvl), by_seed in sorted(data.items()):
        for k in sorted({k for m in by_seed.values() for k in m}):
            v = series(data, arm, n, lvl, k)
            rows.append(["cell", arm, n, lvl, "", k, fmt(float(np.nanmean(v))), "", "", int((~np.isnan(v)).sum())])
    bad_layout = sum(len(v) > 1 for v in layouts.values())
    rows.append(["check", "", "", "", "", "layout_differs_n20_n40", bad_layout, "", "", len(layouts)])
    if set(NS) <= set(ns):
        for arm in arms:
            for lvl in LEVELS:
                keys = sorted({k for s in data[(arm, 20, lvl)].values() for k in s})
                for k in keys:
                    contrast_row(rows, "contrast", arm, k, lvl, series(data, arm, 20, lvl, k), series(data, arm, 40, lvl, k))
        if "off" in arms:
            summary(rows, data, [a for a in arms if a != "off"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(rows)
    print(f"layout differs between N 20 and N 40 on {bad_layout} of {len(layouts)} (d level, seed) pairs")
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


def summary(rows: list, data: dict, on_arms: list[str]) -> None:
    """Delta, split, dd and check rows, and the printed summary."""
    verdict = json.loads(VERDICT.read_text())
    g: dict[tuple[str, int], np.ndarray] = {}
    for arm in on_arms:
        for lvl in LEVELS:
            for k in DELTA_METRICS:
                dl = {n: (series(data, arm, n, lvl, k) - series(data, "off", n, lvl, k)) / (n if k == "food" else 1)
                      for n in NS}
                for n in NS:
                    rows.append(["delta", arm, n, lvl, "", f"d_{k}", fmt(float(np.mean(dl[n]))), "", "", len(dl[n])])
                contrast_row(rows, "delta", arm, f"d_{k}", lvl, dl[20], dl[40])
                if k == "food" and lvl == "d10":
                    g.update({(arm, n): dl[n] for n in NS})
        if arm in verdict["metric_G_per_robot"]:
            ref = verdict["metric_G_per_robot"][arm]
            dev = max(abs(g[(arm, n)].mean() - ref["G_per_robot_mean"][f"n{n}"]) for n in NS)
            rows.append(["check", arm, "", "d10", "", "G_pr_max_abs_dev_vs_verdict", fmt(dev), "", "", 30])
    loss = {n: (series(data, "off", n, "d0", "food") - series(data, "off", n, "d10", "food")) / n for n in NS}
    for n in NS:
        rows.append(["split", "off", n, "d10", "", "L_pr", fmt(float(loss[n].mean())), "", "", 30])
    contrast_row(rows, "split", "off", "L_pr", "d10", loss[20], loss[40])
    print("(d) loss per robot L/N:", ", ".join(f"n{n} {loss[n].mean():.3f}" for n in NS))
    for arm in on_arms:
        terms = paired_boot(split_terms, g[(arm, 20)], loss[20], g[(arm, 40)], loss[40])
        for k, (v, lo, hi) in terms.items():
            rows.append(["split", arm, "40-20", "d10", "", k, fmt(v), fmt(lo), fmt(hi), 30])
        print(f"{arm}: G/N n20 {g[(arm, 20)].mean():.3f} n40 {g[(arm, 40)].mean():.3f}. "
              + ". ".join(f"{k} {v:.3f} [{lo:.3f}, {hi:.3f}]" for k, (v, lo, hi) in terms.items()))
    if {"v3", "v5"} <= set(on_arms):
        sh = paired_boot(share_ratio, *(series(data, a, n, "d10", "act_share") for n in NS for a in ("v5", "v3")))
        for k, (v, lo, hi) in sh.items():
            rows.append(["dd", "v5/v3", "40-20", "d10", "", k, fmt(v), fmt(lo), fmt(hi), 30])
            print(f"(a) {k}: {v:.3f} [{lo:.3f}, {hi:.3f}]")
        dd5, dd3 = g[("v5", 40)] - g[("v5", 20)], g[("v3", 40)] - g[("v3", 20)]
        mean, lo, hi = paired_diff_interval(dd5, dd3)
        rows.append(["dd", "v5-v3", "40-20", "d10", "", "G_pr_drop", fmt(mean), fmt(lo), fmt(hi), 30])
        print(f"(e) v5 drop minus v3 drop: {mean:.3f} [{lo:.3f}, {hi:.3f}]")
    with V5_G2.open(newline="") as fh:  # N 20 only, other seeds: 1 against 2 detractors per decoy
        for row in csv.DictReader(fh):
            if row["arm"] == "k2t10" and row["d"] in ("2", "4"):
                rows.append(["check", "v5_N20_seeds221-260", 20, f"d{row['d']}", "", "G_pr",
                             fmt(float(row["gain"]) / 20), fmt(float(row["gain_lo"]) / 20),
                             fmt(float(row["gain_hi"]) / 20), int(row["n_seeds"])])
                rows.append(["check", "v5_N20_seeds221-260", 20, f"d{row['d']}", "", "L_pr",
                             fmt(float(row["loss"]) / 20), fmt(float(row["loss_lo"]) / 20),
                             fmt(float(row["loss_hi"]) / 20), int(row["n_seeds"])])
                rows.append(["check", "v5_N20_seeds221-260", 20, f"d{row['d']}", "", "R_share",
                             fmt(float(row["share"])), fmt(float(row["share_lo"])), fmt(float(row["share_hi"])),
                             int(row["n_seeds"])])
                print(f"(b) N 20, k2t10, d {row['d']}: G/N {float(row['gain']) / 20:.3f}, "
                      f"L/N {float(row['loss']) / 20:.3f}, R {float(row['share']):.3f}")
    for arm in on_arms:
        for lvl in LEVELS:
            for k in ("act_share", "fail2_share", "cover_time", "act_src_pr", "abort_true_pr", "abort_none_pr",
                      "replay_ok"):
                v = {n: series(data, arm, n, lvl, k) for n in NS}
                if not np.isnan(v[20]).all():
                    print(f"{arm} {lvl} {k}: n20 {np.nanmean(v[20]):.3f} n40 {np.nanmean(v[40]):.3f}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
