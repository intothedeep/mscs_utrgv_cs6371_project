"""M6 travel-time margin from saved logs (DECISIONS.md D-048 D1, DESIGN_M6.md §3.2, §4, §10 D1).

Usage: OMP_NUM_THREADS=1 timeout 300 uv run python tools/m6_margin.py [--out FILE]
Reads manifest.json and events.csv of runs/sweep_v2_lock0, d = 0, defense off, seeds 11-30 (20 runs).
numpy and stdlib only. No model, no simulation. Writes results/real/m6_margin.csv.
Prints one line: MARGIN p95=<x> n=<n> (primary variant and proxy).

Check (DESIGN_M6 §3.2): a follow_start at (t0, p0) opens a check. Any pickup by the same robot closes it.
  expected = |p0 - end| / 0.10 m/s + t_end (15 s) + est_extra_s (0 here, no feedback in the off logs)
  ratio    = (pickup tick - t0) / TPS / expected
  margin   = p95 of ratio over pickup-ending episodes, rounded up to 0.1 (numpy linear percentile)

The trail end `end` comes from the owner grid, which the v4 logs do not have. Three proxies:
  pick   (primary) the follower's own pickup position (the trail end it actually reached)
  near   the live honest trail end (a pickup by any honest robot, age <= 339 s at t0) nearest p0
  far    the live honest trail end farthest from p0
  The provisional end is one of the live ends, so near and far bracket the true expected time.
  near and far fall back to `pick` when no end is live. near gives the tightest deadline (conservative).
The printed MARGIN is the rounded p95 margin, not the raw percentile (the CSV holds p95).
Logs cannot tell a re-follow of the same trail (no new check) from a new trail (new check). Two variants:
  each   (primary) every follow_start opens a check, closed by the robot's next pickup
  first  only the first follow_start since the robot's last drop (or run start) opens a check
Peaks between follow_start and pickup are allowed (the END_SEARCH path that t_end covers).

Miss shares
  ep    over pickup-ending episodes with the deadline inside the run
  all   over all opened checks whose outcome is known inside the run. A check with no pickup before
        its deadline is a miss. With no later pickup at all, `end` is unknown: the farthest source
        centre is used (longest deadline, so the miss count is a lower bound). A check whose deadline
        passes the last tick with no pickup before it is censored and counted apart.

Output columns: scope, variant, proxy, seed, robot, t0, t_pick, dist_m, expected_s, actual_s, ratio, metric, value
  scope episode  one row per pickup-ending episode (proxy pick, near and far)
  scope summary  metric = n, p50, p90, p95, p99, margin_p95, miss_ep_<m>, miss_all_<m>, n_all, n_censored
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

from failure_analysis import PROJECT, TPS, read_events, select_runs

__all__ = ["main"]

ROOT = "runs/sweep_v2_lock0"
SEEDS = range(11, 31)
N_RUNS = 20
SPEED_MPS = 0.10          # DESIGN_M6 Table 3, reference speed = max_speed
T_END_S = 15.0            # DESIGN_M6 Table 1 row 6
EXTRA_S = 0.0             # est_extra_s starts at 0 (DESIGN_M6 §3.1)
EXPIRY_S = 339.0          # trail record expiry (DESIGN_M6 §3.1)
FIXED_MARGIN = 1.5        # D-048 fallback
PRIMARY = ("each", "pick")
VARIANTS = ("each", "first")
PROXIES = ("pick", "near", "far")
QUANTS = (50, 90, 95, 99)
DEFAULT_OUT = PROJECT / "results" / "real" / "m6_margin.csv"
COLUMNS = ("scope", "variant", "proxy", "seed", "robot", "t0", "t_pick", "dist_m", "expected_s",
           "actual_s", "ratio", "metric", "value")


def check_params(params: dict) -> float:
    """Assert the run matches the DESIGN_M6 constants. Returns t_end in s."""
    speed = float(params["controller_wheel_turning_max_speed"]) / 100.0  # cm/s in the controller
    t_end = float(params["controller_pheromone_t_end"])
    if abs(speed - SPEED_MPS) > 1e-9 or abs(t_end - T_END_S) > 1e-9:
        raise SystemExit(f"manifest speed {speed} m/s or t_end {t_end} s differs from DESIGN_M6")
    return t_end


def expected_s(p0: tuple[float, float], end: tuple[float, float]) -> float:
    return math.hypot(p0[0] - end[0], p0[1] - end[1]) / SPEED_MPS + T_END_S + EXTRA_S


def live_end(t0: int, p0: tuple[float, float], pick_xy: tuple[float, float], all_picks: list,
             proxy: str) -> tuple[float, float]:
    """Live honest trail end nearest ('near') or farthest ('far') from p0. Falls back to the pickup point."""
    live = [(x, y) for t, x, y in all_picks if t < t0 and (t0 - t) <= EXPIRY_S * TPS]
    if not live:
        return pick_xy
    pick = min if proxy == "near" else max
    return pick(live, key=lambda p: math.hypot(p[0] - p0[0], p[1] - p0[1]))


def checks(events: list, variant: str) -> list[dict]:
    """Opened checks: robot, t0, p0, and the robot's next pickup (tick, xy) or None."""
    by_robot: dict[str, list] = defaultdict(list)
    for e in events:
        by_robot[e[1]].append(e)
    out = []
    for rid, evs in by_robot.items():
        armed = True  # 'first': a check opens only on the first follow_start since the last drop
        for i, (t, _r, ev, x, y) in enumerate(evs):
            if ev == "drop":
                armed = True
            if ev != "follow_start" or (variant == "first" and not armed):
                continue
            armed = False
            nxt = next((f for f in evs[i + 1:] if f[2] == "pickup"), None)
            out.append({"rid": rid, "t0": t, "p0": (x, y),
                        "pick": (nxt[0], (nxt[3], nxt[4])) if nxt else None})
    return out


def run_rows(seed: int, folder: Path) -> tuple[list, dict]:
    """Episode rows and per-(variant, proxy) raw lists for one run."""
    m = json.loads((folder / "manifest.json").read_text())
    check_params(m["params"])
    n_ticks = int(m["metrics"]["ticks"])
    sources = m["layout"]["sources"]
    events = read_events(folder / "events.csv")
    all_picks = [(t, x, y) for t, _r, ev, x, y in events if ev == "pickup"]
    rows: list = []
    acc: dict = defaultdict(lambda: {"ratio": [], "open": []})
    for variant in VARIANTS:
        for c in checks(events, variant):
            for proxy in PROXIES:
                key = (variant, proxy)
                if c["pick"] is None:
                    far = max(sources, key=lambda s: math.hypot(s[0] - c["p0"][0], s[1] - c["p0"][1]))
                    acc[key]["open"].append((c["t0"], expected_s(c["p0"], far), None))
                    continue
                t_pick, pick_xy = c["pick"]
                end = pick_xy if proxy == "pick" else live_end(c["t0"], c["p0"], pick_xy, all_picks, proxy)
                exp_s = expected_s(c["p0"], end)
                act_s = (t_pick - c["t0"]) / TPS
                acc[key]["open"].append((c["t0"], exp_s, act_s))
                acc[key]["ratio"].append(act_s / exp_s)
                rows.append(["episode", variant, proxy, seed, c["rid"], c["t0"], t_pick,
                             f"{math.hypot(c['p0'][0] - end[0], c['p0'][1] - end[1]):.4f}",
                             f"{exp_s:.3f}", f"{act_s:.1f}", f"{act_s / exp_s:.4f}", "", ""])
    for key in acc:
        acc[key]["n_ticks"] = n_ticks
    return rows, acc


def miss_shares(opened: list, n_ticks: int, margin: float) -> tuple[int, int, int, int, int]:
    """(misses_ep, n_ep, misses_all, n_all, censored) at one margin. Deadlines in ticks from t0."""
    m_ep = n_ep = m_all = n_all = cens = 0
    for t0, exp_s, act_s in opened:
        deadline = t0 + margin * exp_s * TPS
        late = act_s is None or t0 + act_s * TPS > deadline
        if late and deadline > n_ticks:
            cens += 1
            continue
        n_all += 1
        m_all += late
        if act_s is not None:
            n_ep += 1
            m_ep += late
    return m_ep, n_ep, m_all, n_all, cens


def summary(variant: str, proxy: str, runs: list[dict]) -> tuple[list, float, int]:
    ratios = np.array([r for run in runs for r in run["ratio"]])
    qs = {q: float(np.percentile(ratios, q)) for q in QUANTS}  # numpy default: linear interpolation
    margin = math.ceil(qs[95] * 10 - 1e-9) / 10
    base = ["summary", variant, proxy, "", "", "", "", "", "", "", ""]
    rows = [base + ["n", len(ratios)]]
    rows += [base + [f"p{q}", f"{v:.4f}"] for q, v in qs.items()]
    rows.append(base + ["margin_p95", f"{margin:.1f}"])
    for name, mg in (("1.5", FIXED_MARGIN), ("p95", margin)):
        tot = [0, 0, 0, 0, 0]
        for run in runs:
            for i, v in enumerate(miss_shares(run["open"], run["n_ticks"], mg)):
                tot[i] += v
        rows.append(base + [f"miss_ep_{name}", f"{tot[0] / tot[1]:.4f}" if tot[1] else "nan"])
        rows.append(base + [f"miss_all_{name}", f"{tot[2] / tot[3]:.4f}" if tot[3] else "nan"])
        rows.append(base + [f"n_all_{name}", tot[3]])
        rows.append(base + [f"n_censored_{name}", tot[4]])
    return rows, margin, len(ratios)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    runs = {s: f for (d, de, s), f in select_runs(PROJECT / ROOT, SEEDS).items() if d == 0 and de == 0}
    if len(runs) != N_RUNS:
        print(f"expected {N_RUNS} runs (d 0, defense 0, seeds 11-30), found {len(runs)}", file=sys.stderr)
        return 1
    rows: list = []
    per_key: dict = defaultdict(list)
    for seed, folder in sorted(runs.items()):
        ep_rows, acc = run_rows(seed, folder)
        rows.extend(ep_rows)
        for key, val in acc.items():
            per_key[key].append(val)
    result = {}
    for variant in VARIANTS:
        for proxy in PROXIES:
            s_rows, margin, n = summary(variant, proxy, per_key[(variant, proxy)])
            rows.extend(s_rows)
            result[(variant, proxy)] = (margin, n)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        w.writerows(rows)
    for key, (mg, n) in result.items():
        print(f"{key[0]}/{key[1]}: margin {mg:.1f} n {n}", file=sys.stderr)
    margin, n = result[PRIMARY]
    print(f"MARGIN p95={margin:.1f} n={n}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
