"""Pick the pheromone setting by D-007 from saved tuning runs (M2-07). Reads manifests only.

Usage: tuning_pick.py
Prints the mean food_collected per round and writes results/real/tuning/tuning_pick.json.
Metric: mean food_collected over seeds 101 to 103. A tie goes to the earlier round.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from run_results import PROJECT, sha256_hex
from tuning_rounds import best_round, read_rounds

ROOT = PROJECT / "runs" / "tuning"
OUT = PROJECT / "results" / "real" / "tuning" / "tuning_pick.json"
CRITERION = "prereg/pheromone_tuning.md"


def main() -> int:
    rounds = read_rounds(ROOT)
    if any(r["mean_food"] is None for r in rounds.values()):
        raise SystemExit("stop: a round lacks one of the seeds 101 to 103")
    best = best_round(rounds)
    for k, r in rounds.items():
        mark = "  <- picked" if k == best else ""
        print(f"round {k}: half_life_s={r['config'][0]:g} lambda_dep={r['config'][1]:g} "
              f"mean food_collected={r['mean_food']:.2f}{mark}")
    verdict = {
        "rule": "D-007: highest mean food_collected, d = 0, defense off, seeds 101 to 103; tie to the earlier round",
        "picked_round": best,
        "half_life_s": rounds[best]["config"][0],
        "lambda_dep": rounds[best]["config"][1],
        "rounds": [{"round": k, "half_life_s": r["config"][0], "lambda_dep": r["config"][1],
                    "food_by_seed": {str(s): f for s, f in sorted(r["foods"].items())},
                    "mean_food": r["mean_food"], "runids": r["runids"]} for k, r in rounds.items()],
        "criterion_file": CRITERION,
        "pick_code_sha256": sha256_hex(Path(__file__).resolve()),  # rules/measurement.md 4.1
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(verdict, indent=2) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
