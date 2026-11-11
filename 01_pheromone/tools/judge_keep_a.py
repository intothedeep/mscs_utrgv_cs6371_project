"""Judge keep-A from saved runs (D-010, M2). Reads manifests only.

Usage: judge_keep_a.py
Pass = arm 1 mean >= 1.2 x arm 2 mean AND arm 1 > arm 2 on all 3 seeds (104 to 106).
Writes results/real/judgement/verdict.json. Exits nonzero when a run is missing or not complete.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import schema as S
from run_results import PROJECT, load_manifests, run_food, sha256_hex

ROOT = PROJECT / "runs" / "judgement"
OUT = PROJECT / "results" / "real" / "judgement" / "verdict.json"
CRITERION = "prereg/keep_a_judgement.md"
SEEDS = (104, 105, 106)
RATIO = 1.2


def food_by_arm() -> dict[str, dict[int, int]]:
    arms: dict[str, dict[int, int]] = {"1": {}, "2": {}}
    for m in load_manifests(ROOT):
        arm, seed = m[S.K_PARAMS].get("arm"), int(m[S.K_PARAMS][S.P_SEED])
        if arm not in arms or seed in arms[arm]:
            raise SystemExit(f"stop: unexpected or duplicate run {m[S.K_RUNID]}")
        arms[arm][seed] = run_food(m)
    for arm, foods in arms.items():
        if set(foods) != set(SEEDS):
            raise SystemExit(f"stop: arm {arm} has seeds {sorted(foods)}, expected {list(SEEDS)}")
    return arms


def main() -> int:
    arms = food_by_arm()
    mean1 = sum(arms["1"].values()) / len(SEEDS)
    mean2 = sum(arms["2"].values()) / len(SEEDS)
    wins = {str(s): arms["1"][s] > arms["2"][s] for s in SEEDS}
    passed = mean1 >= RATIO * mean2 and all(wins.values())
    verdict = {
        "rule": "D-010: arm 1 mean >= 1.2 x arm 2 mean AND arm 1 > arm 2 on all 3 seeds",
        "seeds": list(SEEDS),
        "arm1_food_by_seed": {str(s): arms["1"][s] for s in SEEDS},
        "arm2_food_by_seed": {str(s): arms["2"][s] for s in SEEDS},
        "arm1_mean": mean1, "arm2_mean": mean2, "ratio_threshold": RATIO,
        "arm1_above_arm2_by_seed": wins,
        "pass": passed,
        "criterion_file": CRITERION,
        "judge_code_sha256": sha256_hex(Path(__file__).resolve()),  # rules/measurement.md 4.1
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(verdict, indent=2) + "\n")
    print(f"arm1 mean={mean1:.2f} arm2 mean={mean2:.2f} per-seed wins={wins} pass={passed}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
