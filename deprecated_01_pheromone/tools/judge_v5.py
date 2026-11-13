"""Judge defense v5 (prereg/defense_v5.md). Reads saved manifests of runs/v5_confirm/ only.

Writes results/real/v5/g2_stats.csv (every on-arm against off) and verdict.json. Criteria are in the
prereg and are not changed here. The verdict file holds the sha256 of this script (rules/measurement.md 4.1).
Pass logic is copied from judge_v2.py, on the primary arm k2t10, seeds 221-260:

  metric     G(2) = F(2, k2t10) - F(2, off), paired percentile bootstrap, 10,000 resamples, 95 %
  threshold  lower bound of the G(2) interval > 0
  failure    the G(2) interval includes 0, or the d = 0 cost F(0, k2t10) - F(0, off) has upper bound < 0
  reported   main effects at d = 0 and d = 2: E_k, E_t and the interaction I (no pass or fail)
"""
from __future__ import annotations

import csv
import dataclasses
import json
import sys
from pathlib import Path

import numpy as np

from g2_stats import G2Row, N_BOOT, g2_rows, paired_diff_interval
from run_results import PROJECT, sha256_hex
from v5_common import (ARMS, CONFIRM_ROOT, CONFIRM_SEEDS, DS, OFF, PREREG, PRIMARY, RESULTS, VERDICT,
                       arm_food, read_food)

Food = dict[tuple[int, int], dict[int, float]]  # (d, defense) -> {seed: food}
EFFECT_DS = (0, 2)


def vs_off(off: Food, on: Food) -> Food:
    """off cells (d, 0) and one on-arm's cells (d, 1) in one table, the shape g2_rows reads."""
    return {**off, **on}


def row_dict(r: G2Row) -> dict:
    return {"d": r.d, "n_seeds": r.n_seeds, "F_off": r.f_off, "F_on": r.f_on,
            "G": r.gain, "G_lo": r.gain_lo, "G_hi": r.gain_hi}


def seed_values(food: Food, d: int, defense: int) -> np.ndarray:
    return np.array([food[(d, defense)][s] for s in CONFIRM_SEEDS])  # one seed order, so the bootstrap pairs


def interval(a: np.ndarray, b: np.ndarray) -> dict:
    diff, lo, hi = paired_diff_interval(a, b)
    return {"diff": diff, "lo": lo, "hi": hi}


def main_effects(arms: dict[str, Food], d: int) -> dict:
    f = {name: seed_values(food, d, 1) for name, food in arms.items() if name != OFF}
    return {"E_k": interval((f["k2t0"] + f["k2t10"]) / 2, (f["k1t0"] + f["k1t10"]) / 2),
            "E_t": interval((f["k1t10"] + f["k2t10"]) / 2, (f["k1t0"] + f["k2t0"]) / 2),
            "I": interval(f["k2t10"] - f["k1t10"], f["k2t0"] - f["k1t0"])}


def main() -> int:
    raw = read_food(CONFIRM_ROOT)
    expected = {(k, t, d, de, s) for de, k, t in ARMS.values() for d in DS for s in CONFIRM_SEEDS}
    if set(raw) != expected:
        raise SystemExit(f"stop: {CONFIRM_ROOT.name} is not the {len(expected)} confirm runs. "
                         f"missing {len(expected - set(raw))}, extra {len(set(raw) - expected)}")
    arms = {name: arm_food(raw, name, CONFIRM_SEEDS) for name in ARMS}
    rows = {name: {r.d: r for r in g2_rows(vs_off(arms[OFF], arms[name]), DS)} for name in ARMS if name != OFF}
    g2, cost = rows[PRIMARY][2], rows[PRIMARY][0]

    threshold_pass = bool(g2.gain_lo > 0)
    g2_includes_zero = bool(g2.gain_lo <= 0 <= g2.gain_hi)
    cost_failure = bool(cost.gain_hi < 0)
    failure = g2_includes_zero or cost_failure
    # Pass needs the threshold and no failure condition (as judge_v2.py).
    verdict = "pass" if threshold_pass and not failure else "fail"
    out = {
        "verdict": verdict,
        "if_fail": "report v5 as null and run M5-09" if verdict == "fail" else None,
        "primary_arm": PRIMARY,
        "n_seeds": g2.n_seeds,
        "seeds": [CONFIRM_SEEDS[0], CONFIRM_SEEDS[-1]],
        "bootstrap": {"resamples": N_BOOT, "interval": "95 % percentile, paired on seed"},
        "metric_G2": {"G": g2.gain, "lo": g2.gain_lo, "hi": g2.gain_hi, "F_off": g2.f_off, "F_on": g2.f_on},
        "threshold_pass": threshold_pass,
        "failure": {"G2_interval_includes_0": g2_includes_zero,
                    "d0_cost_interval_upper_below_0": cost_failure,
                    "d0_cost": {"cost": cost.gain, "lo": cost.gain_lo, "hi": cost.gain_hi},
                    "triggered": failure},
        "contrast": {"main_k2t10_vs_off": {f"d{d}": row_dict(rows[PRIMARY][d]) for d in DS},
                     "main_effects": {f"d{d}": main_effects(arms, d) for d in EFFECT_DS},
                     "reported_only_other_arms": {a: {f"d{d}": row_dict(r[d]) for d in DS}
                                                  for a, r in rows.items() if a != PRIMARY}},
        "per_seed_food": {name: {f"d{d}": [arms[name][(d, ARMS[name][0])][s] for s in CONFIRM_SEEDS]
                                 for d in DS} for name in ARMS},
        "criterion_file": str(PREREG.relative_to(PROJECT)),
        "root": str(CONFIRM_ROOT.relative_to(PROJECT)),
        "judge_code_sha256": sha256_hex(Path(__file__).resolve()),  # rules/measurement.md 4.1
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    fields = ("arm", *(f.name for f in dataclasses.fields(G2Row)))
    with (RESULTS / "g2_stats.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for name, by_d in rows.items():
            w.writerows({"arm": name, **dataclasses.asdict(by_d[d])} for d in DS)
    VERDICT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"verdict={verdict} G(2)={g2.gain:.2f} [{g2.gain_lo:.2f}, {g2.gain_hi:.2f}] "
          f"d0 cost={cost.gain:.2f} [{cost.gain_lo:.2f}, {cost.gain_hi:.2f}]")
    print(f"wrote {VERDICT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
