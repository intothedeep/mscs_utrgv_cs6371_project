"""Pick a tuning setting from saved tuning runs. Reads manifests only.

Usage: tuning_pick.py              pheromone, D-007: writes results/real/tuning/tuning_pick.json
       tuning_pick.py --defense    defense, D-011: writes results/real/defense_tuning/defense_pick.json
Prints the mean food_collected per round. Metric: mean food_collected over seeds 101 to 103
(defense: mean F(2, on)). A tie goes to the earlier round.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from run_results import PROJECT, sha256_hex
from tuning_rounds import PHEROMONE, Rule, best_round, load_defense_rule, read_rounds

RESULTS = PROJECT / "results" / "real"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--defense", action="store_true")
    args = ap.parse_args(argv)
    if args.defense:
        rule: Rule = load_defense_rule()
        root, out = PROJECT / "runs" / "defense_tuning", RESULTS / "defense_tuning" / "defense_pick.json"
        rule_text = ("D-011: highest mean F(2, on), d = 2, defense on, seeds 101 to 103; "
                     "tie to the earlier round")
        criterion = "prereg/defense_tuning.md"
    else:
        rule = PHEROMONE
        root, out = PROJECT / "runs" / "tuning", RESULTS / "tuning" / "tuning_pick.json"
        rule_text = ("D-007: highest mean food_collected, d = 0, defense off, seeds 101 to 103; "
                     "tie to the earlier round")
        criterion = "prereg/pheromone_tuning.md"
    rounds = read_rounds(root, rule)
    if any(r["mean_food"] is None for r in rounds.values()):
        raise SystemExit("stop: a round lacks one of the seeds 101 to 103")
    best = best_round(rounds)
    for k, r in rounds.items():
        values = " ".join(f"{n}={c:g}" for n, c in zip(rule.names, r["config"]))
        print(f"round {k}: {values} mean food_collected={r['mean_food']:.2f}"
              f"{'  <- picked' if k == best else ''}")
    verdict = {
        "rule": rule_text,
        "picked_round": best,
        **{n: c for n, c in zip(rule.names, rounds[best]["config"])},
        "rounds": [{"round": k, **{n: c for n, c in zip(rule.names, r["config"])},
                    "food_by_seed": {str(s): f for s, f in sorted(r["foods"].items())},
                    "mean_food": r["mean_food"], "runids": r["runids"]} for k, r in rounds.items()],
        "criterion_file": criterion,
        "pick_code_sha256": sha256_hex(Path(__file__).resolve()),  # rules/measurement.md 4.1
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(verdict, indent=2) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
