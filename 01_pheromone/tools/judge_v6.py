"""Judge the M6 ID arm (prereg/defense_id_arm.md). Reads saved manifests and sidecars of runs/m6_confirm/ only.

Writes results/real/id_arm/verdict.json, contrast.csv and isolation.csv. Criteria are in the prereg and are not
changed here. The verdict file holds the sha256 of this script (rules/measurement.md 4.1).

  metric     delta = F(2, id) - F(2, best no-ID arm), seeds 321-360, paired percentile bootstrap, 10,000 resamples, 95 %
             (the best no-ID arm is named in the prereg before any M6 run)
  threshold  the interval excludes 0 = "differs", else "not resolved". No win line
  failure    D4: more than 20 of 40 seeds at d = 2 where no detractor has an `isolate` event
             = "adapted arm did not function". It wins over the other two words
  reported   F per arm and d, detractors and honest robots isolated per run (isolation.csv)
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

from g2_stats import N_BOOT, paired_diff_interval
from run_results import PROJECT, sha256_hex
from v6_common import (ARM_ORDER, CONFIRM_ROOT, CONFIRM_SEEDS, DS, PREREG, RESULTS, VERDICT, arm_root,
                       prereg_values, read_arm_runs, read_margin)
from v6_sidecar import SIDECAR_FILE, read_sidecar, run_isolation

N_FAIL = 20  # D-048 D4: "most seeds" = more than 20 of 40


def main() -> int:
    best, margin, eps = prereg_values()
    if abs(margin - read_margin()) > 1e-9:
        raise SystemExit(f"stop: prereg margin {margin} differs from the saved margin file ({read_margin()})")
    runs = {arm: read_arm_runs(arm_root(CONFIRM_ROOT, arm), arm, margin) for arm in ARM_ORDER}
    expected = {(d, s) for d in DS for s in CONFIRM_SEEDS}
    for arm, got in runs.items():
        if set(got) != expected:
            raise SystemExit(f"stop: root {arm} is not the {len(expected)} confirm runs. "
                             f"missing {len(expected - set(got))}, extra {len(set(got) - expected)}")
    food = {arm: {d: np.array([runs[arm][(d, s)][0] for s in CONFIRM_SEEDS], dtype=float) for d in DS} for arm in ARM_ORDER}

    iso = {(d, s): {"seed": s, "d": d, **run_isolation(read_sidecar(runs["id"][(d, s)][1] / SIDECAR_FILE))}
           for d in DS for s in CONFIRM_SEEDS}
    n_no_isolation = sum(iso[(2, s)]["det_isolated"] == 0 for s in CONFIRM_SEEDS)
    did_not_function = n_no_isolation > N_FAIL

    delta_per_seed = food["id"][2] - food[best][2]
    mean, lo, hi = paired_diff_interval(food["id"][2], food[best][2])
    word = "did not function" if did_not_function else ("differs" if lo > 0 or hi < 0 else "not resolved")
    out = {
        "verdict": word,
        "best_no_id_arm": best,
        "metric_delta2": {"delta": mean, "lo": lo, "hi": hi, "F_id": float(food["id"][2].mean()),
                          "F_best": float(food[best][2].mean()), "delta_per_seed": delta_per_seed.tolist()},
        "bootstrap": {"resamples": N_BOOT, "interval": "95 % percentile, paired on seed"},
        "failure": {"rule": "D4: more than 20 of 40 seeds at d = 2 with 0 detractors isolated (event isolate)",
                    "seeds_with_no_detractor_isolated": int(n_no_isolation), "triggered": did_not_function},
        "n_seeds": len(CONFIRM_SEEDS), "seeds": [CONFIRM_SEEDS[0], CONFIRM_SEEDS[-1]],
        "frozen": {"margin": margin, "eps_m": eps, "min_pts": 2},
        "contrast_F_mean": {arm: {f"d{d}": float(food[arm][d].mean()) for d in DS} for arm in ARM_ORDER},
        "isolation_mean_per_run": {f"d{d}": {k: float(np.mean([iso[(d, s)][k] for s in CONFIRM_SEEDS]))
                                             for k in ("det_isolated", "honest_isolated", "det_isolated_at_end")} for d in DS},
        "criterion_file": str(PREREG.relative_to(PROJECT)),
        "root": str(CONFIRM_ROOT.relative_to(PROJECT)),
        "judge_code_sha256": sha256_hex(Path(__file__).resolve()),  # rules/measurement.md 4.1
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (RESULTS / "contrast.csv").open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(("arm", "d", "n_seeds", "F_mean"))
        w.writerows((arm, d, len(CONFIRM_SEEDS), f"{food[arm][d].mean():.4f}") for arm in ARM_ORDER for d in DS)
    cols = ("d", "seed", "n_detractors", "det_isolated", "det_isolated_at_end", "honest_isolated", "first_det_isolate_s")
    with (RESULTS / "isolation.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(iso[k] for k in sorted(iso))
    VERDICT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"verdict={word} delta(2)={mean:.2f} [{lo:.2f}, {hi:.2f}] best={best} "
          f"seeds with no detractor isolated={n_no_isolation}/{len(CONFIRM_SEEDS)}")
    print(f"wrote {VERDICT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
