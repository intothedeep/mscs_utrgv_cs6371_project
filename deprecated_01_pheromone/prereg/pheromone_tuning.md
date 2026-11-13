# Pre-registration: pheromone tuning (D-007, M2)

Commit this file before the first tuning run (`rules/measurement.md` 1). Do not edit it after.

| Line | Value |
| --- | --- |
| Metric | Mean `food_collected` over seeds 101, 102, 103. Runs: d = 0, defense off. One metric only. |
| Threshold | A round beats the best earlier round only with a strictly higher mean. No margin: D-007 has no noise estimate for 3 seeds. A tie goes to the earlier round. |
| Contrast | Round k against the best of rounds 1 to k - 1. Round 1 is the start values (half-life 60 s, `λ_dep` 0.077). Rounds 2 and 3 change one value, from half-life 30, 60, 120 s and `λ_dep` 0.05, 0.077, 0.115. |
| Failure condition | No round beats round 1. Then round 1 values freeze, and the report says tuning gave no gain. At most 3 rounds. |

- Runs: `tools/make_tuning.py --round k --run`, one core, sequential (D-013).
- Pick: `tools/tuning_pick.py` writes `results/real/tuning/tuning_pick.json`.
- Seeds 1 to 10 are never used here. Picked values are never re-tuned with detractor runs.
