"""Judge M7, scalability (prereg/scale.md). Reads the saved runs of runs/m7_scale/ only.

Writes results/real/scale/verdict.json and contrast.csv. Criteria are in the prereg and are not changed
here. The verdict file holds the sha256 of this script (rules/measurement.md 4.1).

  metric     per arm in v3, v5 and seed s: g_N(s) = (F(d10, arm, s) - F(d10, off, s)) / N, d10 = 2 at N 20, 4 at N 40
             D = mean over seeds 401-430 of g_40(s) - g_20(s). Paired percentile bootstrap on seed,
             10,000 resamples, 95 % (g2_stats.paired_diff_interval)
  threshold  the interval excludes 0: "scales better" (above) or "scales worse" (below), else "not resolved"
  failure    mean F(0, off) / N at N = 40 below half of N = 20 = "confounded by congestion". It wins
  reported   d = 0 cost per robot (F(0, arm) - F(0, off)) / N, wrong source suspects per robot
             (events.csv suspect_add, failure_analysis sus_cls_src)
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

from failure_analysis import run_metrics
from g2_stats import N_BOOT, paired_diff_interval
from run_results import PROJECT, sha256_hex
from v7_common import (ARM_ORDER, BEST_ARM, CONFIRM_BASE, CONFIRM_SEEDS, D10, NS, PREREG, RESULTS, VERDICT, cell_root,
                       cells, read_scale_runs, require_prereg)

ON_ARMS = tuple(a for a in ARM_ORDER if a != "off")
CONGESTION_RATIO = 0.5  # prereg: F(0, off) per robot at N = 40 below half of N = 20
LO_N, HI_N = NS


def interval_word(lo: float, hi: float) -> str:
    return "scales better" if lo > 0 else ("scales worse" if hi < 0 else "not resolved")


def diff_stats(at_n20: np.ndarray, at_n40: np.ndarray) -> dict[str, float]:
    """N 40 minus N 20, one value per seed in the same seed order (paired on seed)."""
    mean, lo, hi = paired_diff_interval(at_n40, at_n20)
    return {"diff": mean, "lo": lo, "hi": hi}


def main() -> int:
    require_prereg()
    runs = {(arm, n): read_scale_runs(cell_root(CONFIRM_BASE, arm, n), arm, n) for arm in ARM_ORDER for n in NS}
    for (arm, n), got in runs.items():
        expected = {(d, s) for d in cells(n) for s in CONFIRM_SEEDS}
        if set(got) != expected:
            raise SystemExit(f"stop: root {arm}_n{n} is not the {len(expected)} confirm runs. "
                             f"missing {len(expected - set(got))}, extra {len(set(got) - expected)}")
    food = {(arm, n, d): np.array([runs[(arm, n)][(d, s)][0] for s in CONFIRM_SEEDS], dtype=float)
            for arm in ARM_ORDER for n in NS for d in cells(n)}

    off0 = {n: food[("off", n, 0)].mean() / n for n in NS}
    ratio = float(off0[HI_N] / off0[LO_N])
    confounded = ratio < CONGESTION_RATIO

    gain, cost, arm_word = {}, {}, {}
    for arm in ON_ARMS:
        g = {n: (food[(arm, n, D10[n])] - food[("off", n, D10[n])]) / n for n in NS}
        c = {n: (food[(arm, n, 0)] - food[("off", n, 0)]) / n for n in NS}
        stats = diff_stats(g[LO_N], g[HI_N])
        gain[arm] = {"G_per_robot_mean": {f"n{n}": float(g[n].mean()) for n in NS},
                     "G_per_robot_per_seed": {f"n{n}": g[n].tolist() for n in NS}, **stats,
                     "diff_per_seed": (g[HI_N] - g[LO_N]).tolist()}
        cost[arm] = {"cost_per_robot_mean": {f"n{n}": float(c[n].mean()) for n in NS}, **diff_stats(c[LO_N], c[HI_N])}
        arm_word[arm] = interval_word(stats["lo"], stats["hi"])
        print(f"{arm}: G/N n20={g[LO_N].mean():.3f} n40={g[HI_N].mean():.3f} "
              f"diff={stats['diff']:.3f} [{stats['lo']:.3f}, {stats['hi']:.3f}] {arm_word[arm]}")

    sus: dict[tuple[str, int, int], np.ndarray] = {}  # per robot, per seed; failure_analysis reads the run folders
    for arm in ON_ARMS:
        for n in NS:
            for d in cells(n):
                sus[(arm, n, d)] = np.array([run_metrics(runs[(arm, n)][(d, s)][1]).get("sus_cls_src", 0.0) / n
                                             for s in CONFIRM_SEEDS])
    suspects = {arm: {f"n{n}_d{d}": float(sus[(arm, n, d)].mean()) for n in NS for d in cells(n)} for arm in ON_ARMS}
    suspects_diff = {arm: {f"d{k}": diff_stats(sus[(arm, LO_N, dl)], sus[(arm, HI_N, dh)]) for k, (dl, dh) in
                           {"0": (0, 0), "10pct": (D10[LO_N], D10[HI_N])}.items()}
                     for arm in ON_ARMS}

    word = "confounded by congestion" if confounded else "; ".join(f"{a} {arm_word[a]}" for a in ON_ARMS)
    out = {
        "verdict": word,
        "arm_verdict": arm_word,
        "best_arm": BEST_ARM,
        "congestion": {"rule": "mean F(0, off) / N at N = 40 below half of N = 20",
                       "F0_off_per_robot": {f"n{n}": float(off0[n]) for n in NS}, "ratio": ratio,
                       "threshold": CONGESTION_RATIO, "triggered": confounded},
        "metric_G_per_robot": gain,
        "d0_cost_per_robot": cost,
        "wrong_source_suspects_per_robot_mean": suspects,
        "wrong_source_suspects_n40_minus_n20": suspects_diff,
        "bootstrap": {"resamples": N_BOOT, "interval": "95 % percentile, paired on seed (seed s at N 20 with seed s at N 40)"},
        "n_seeds": len(CONFIRM_SEEDS), "seeds": [CONFIRM_SEEDS[0], CONFIRM_SEEDS[-1]],
        "d10": {f"n{n}": D10[n] for n in NS},
        "criterion_file": str(PREREG.relative_to(PROJECT)),
        "root": str(CONFIRM_BASE.relative_to(PROJECT)),
        "judge_code_sha256": sha256_hex(Path(__file__).resolve()),  # rules/measurement.md 4.1
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "contrast.csv").open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(("arm", "n", "d", "n_seeds", "F_mean", "F_per_robot", "wrong_source_suspects_per_robot"))
        for arm in ARM_ORDER:
            for n in NS:
                for d in cells(n):
                    s = f"{sus[(arm, n, d)].mean():.4f}" if arm in ON_ARMS else ""
                    w.writerow((arm, n, d, len(CONFIRM_SEEDS), f"{food[(arm, n, d)].mean():.4f}",
                                f"{food[(arm, n, d)].mean() / n:.4f}", s))
    VERDICT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"verdict={word}  F(0,off)/N ratio={ratio:.2f} (threshold {CONGESTION_RATIO})")
    print(f"wrote {VERDICT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
