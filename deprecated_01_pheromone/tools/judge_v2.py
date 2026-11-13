"""Judge defense v2 (spec items 8 to 11). Reads saved manifests of the two confirmation roots.

Writes results/real/v2/verdict.json. Criteria are in prereg/defense_v2_lockout.md and are not
changed here. The verdict file holds the sha256 of this script (rules/measurement.md 4.1).

Item 8  metric        G(2) = F(2, on) - F(2, off), seeds 11-30, paired bootstrap, 95 % interval
Item 9  threshold     lower bound of the G(2) interval > 0
Item 10 contrast      main: v2 on vs off. Attribution: picked t_lock vs 0 at (2, on), with interval.
                      d = 1 and 4 are reported only, with no pass or fail.
Item 11 failure       G(2) interval includes 0, or the d = 0 cost interval has upper bound < 0
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

import schema as S
from g2_stats import G2Row, N_BOOT, g2_rows, paired_diff_interval
from run_results import PROJECT, sha256_hex
from v2_common import (CONFIRM_CELLS, CONFIRM_ROOT, CONFIRM_SEEDS, CONTROL_ROOT, PREREG, VERDICT,
                       load_pick, read_food)

Food = dict[tuple[int, int], dict[int, float]]  # (d, defense) -> {seed: food}


def load_arm(root: Path, t_lock: int) -> Food:
    """Food by cell for one root. Stops unless the root is exactly 8 cells x seeds 11-30 at t_lock."""
    raw = read_food(root)
    expected = {(t_lock, d, f, s) for d, f in CONFIRM_CELLS for s in CONFIRM_SEEDS}
    if set(raw) != expected:
        raise SystemExit(f"stop: {root.name} is not the {len(expected)} runs of t_lock={t_lock}. "
                         f"missing {len(expected - set(raw))}, extra {len(set(raw) - expected)}")
    food: Food = defaultdict(dict)
    for (_t, d, f, s), (value, _runid) in raw.items():
        food[(d, f)][s] = float(value)
    return food


def row_dict(r: G2Row) -> dict:
    return {"d": r.d, "n_seeds": r.n_seeds, "F_off": r.f_off, "F_on": r.f_on,
            "G": r.gain, "G_lo": r.gain_lo, "G_hi": r.gain_hi}


def main() -> int:
    picked = load_pick()
    if picked == 0:
        raise SystemExit("stop: pick is 0, kill rule (spec 12): nothing to judge")
    v2, ctl = load_arm(CONFIRM_ROOT, picked), load_arm(CONTROL_ROOT, 0)
    rows = {r.d: r for r in g2_rows(v2, S.DETRACTOR_COUNTS)}
    ctl_rows = {r.d: r for r in g2_rows(ctl, S.DETRACTOR_COUNTS)}
    g2, cost = rows[2], rows[0]
    seeds = list(CONFIRM_SEEDS)  # same order in both arms, so the bootstrap pairs on seed
    a = np.array([v2[(2, 1)][s] for s in seeds])
    b = np.array([ctl[(2, 1)][s] for s in seeds])
    attr, attr_lo, attr_hi = paired_diff_interval(a, b)

    threshold_pass = bool(g2.gain_lo > 0)                       # item 9
    g2_includes_zero = bool(g2.gain_lo <= 0 <= g2.gain_hi)      # item 11, first condition
    cost_failure = bool(cost.gain_hi < 0)                       # item 11, second condition
    failure = g2_includes_zero or cost_failure
    # Pass needs the threshold and no failure condition. A G(2) interval wholly below 0 fails
    # the threshold without "including 0", so it is not a pass either.
    verdict = "pass" if threshold_pass and not failure else "fail"
    out = {
        "verdict": verdict,
        "if_fail": "report v2 as null (spec 11)" if verdict == "fail" else None,
        "picked_t_lock": picked,
        "n_seeds": g2.n_seeds,
        "bootstrap": {"resamples": N_BOOT, "interval": "95 % percentile, paired on seed"},
        "item_8_metric_G2": {"G": g2.gain, "lo": g2.gain_lo, "hi": g2.gain_hi,
                             "F_off": g2.f_off, "F_on": g2.f_on, "n_seeds": g2.n_seeds},
        "item_9_threshold_pass": threshold_pass,
        "item_10_contrast": {
            "main_v2_on_vs_off_G2": {"G": g2.gain, "lo": g2.gain_lo, "hi": g2.gain_hi},
            "attribution_picked_vs_lock0_at_d2_on": {"diff": attr, "lo": attr_lo, "hi": attr_hi,
                                                      "F_picked": float(a.mean()), "F_lock0": float(b.mean())},
            "reported_only": {f"d{d}": row_dict(rows[d]) for d in (1, 4)},
            "lock0_control_G": {f"d{d}": row_dict(ctl_rows[d]) for d in (0, 1, 2, 4)},
        },
        "item_11_failure": {
            "G2_interval_includes_0": g2_includes_zero,
            "d0_cost_interval_upper_below_0": cost_failure,
            "d0_cost": {"cost": cost.gain, "lo": cost.gain_lo, "hi": cost.gain_hi},
            "triggered": failure,
        },
        "criterion_file": str(PREREG.relative_to(PROJECT)),
        "roots": [str(CONFIRM_ROOT.relative_to(PROJECT)), str(CONTROL_ROOT.relative_to(PROJECT))],
        "judge_code_sha256": sha256_hex(Path(__file__).resolve()),  # rules/measurement.md 4.1
    }
    VERDICT.parent.mkdir(parents=True, exist_ok=True)
    VERDICT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"verdict={verdict} G(2)={g2.gain:.2f} [{g2.gain_lo:.2f}, {g2.gain_hi:.2f}] "
          f"d0 cost={cost.gain:.2f} [{cost.gain_lo:.2f}, {cost.gain_hi:.2f}] "
          f"attribution={attr:.2f} [{attr_lo:.2f}, {attr_hi:.2f}]")
    print(f"wrote {VERDICT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
