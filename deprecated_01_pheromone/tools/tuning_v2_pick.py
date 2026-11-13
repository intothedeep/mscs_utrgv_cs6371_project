"""Pick t_lock from the saved v2 tuning runs (spec items 5, 6). Reads manifests only.

Writes results/real/tuning_v2/pick.json. Metric: seed mean of food(d=2, on) + food(d=0, on),
seeds 107 to 116. Highest wins. A tie goes to the smaller t_lock.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from run_results import PROJECT, sha256_hex
from v2_common import PICK, PREREG, T_LOCKS, TUNE_CELLS, TUNE_ROOT, TUNE_SEEDS, read_food


def main() -> int:
    food = read_food(TUNE_ROOT)
    expected = {(t, d, f, s) for t in T_LOCKS for d, f in TUNE_CELLS for s in TUNE_SEEDS}
    if set(food) != expected:
        missing, extra = sorted(expected - set(food)), sorted(set(food) - expected)
        raise SystemExit(f"stop: tuning_v2 is not the 80 expected runs. missing {len(missing)} "
                         f"{missing[:3]}, extra {len(extra)} {extra[:3]}")
    rows = []
    for t in T_LOCKS:
        by_seed = {s: sum(food[(t, d, f, s)][0] for d, f in TUNE_CELLS) for s in TUNE_SEEDS}
        rows.append({"t_lock": t, "metric_by_seed": {str(s): v for s, v in by_seed.items()},
                     "metric_mean": sum(by_seed.values()) / len(by_seed),
                     "food_mean_by_cell": {f"d{d}_def{f}": sum(food[(t, d, f, s)][0] for s in TUNE_SEEDS)
                                           / len(TUNE_SEEDS) for d, f in TUNE_CELLS},
                     "runids": sorted(food[(t, d, f, s)][1] for d, f in TUNE_CELLS for s in TUNE_SEEDS)})
    # T_LOCKS is ascending, and max() keeps the first of equal values: the tie goes to the smaller t_lock.
    best = max(rows, key=lambda r: r["metric_mean"])
    for r in rows:
        print(f"t_lock={r['t_lock']:>2} mean F(2,on)+F(0,on)={r['metric_mean']:.2f}"
              f"{'  <- picked' if r is best else ''}")
    out = {"rule": "spec 6: highest seed mean of food(d=2,on)+food(d=0,on), seeds 107-116; tie to smaller t_lock",
           "picked_t_lock": best["t_lock"], "candidates": rows,
           "criterion_file": str(PREREG.relative_to(PROJECT)),
           "pick_code_sha256": sha256_hex(Path(__file__).resolve())}  # rules/measurement.md 4.1
    PICK.parent.mkdir(parents=True, exist_ok=True)
    PICK.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {PICK}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
