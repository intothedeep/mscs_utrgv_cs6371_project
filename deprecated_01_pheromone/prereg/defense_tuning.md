# Pre-registration: defense tuning (D-011, M3)

Commit this file and `defense_candidates.json` before the first defense tuning run (`rules/measurement.md` 1).
Do not edit them after. The pheromone values are frozen (D-016) and are not tuned here.

| Line | Value |
| --- | --- |
| Metric | Mean `food_collected` over seeds 101, 102, 103. Runs: d = 2, defense on. This is the mean `F(2, on)`. One metric only. |
| Threshold | A round beats the best earlier round only with a strictly higher mean. No margin: D-011 has no noise estimate for 3 seeds. A tie goes to the earlier round. |
| Contrast | Round k against the best of rounds 1 to k - 1. Round 1 is the start values (`r_suspect` 0.4 m, `α_cone` 15°, `d_cone` 1.0 m, `t_end` 15 s). Rounds 2 and 3 change one value, to an alternate in `defense_candidates.json`. |
| Failure condition | No round beats round 1. Then round 1 values freeze, and the report says defense tuning gave no gain. At most 3 rounds. |

- Runs: `tools/make_tuning.py --defense --round k --run`, one core, sequential (D-013).
- Pick: `tools/tuning_pick.py --defense` writes `results/real/defense_tuning/defense_pick.json`.
- Seeds 1 to 10 are never used here. Picked values freeze in a D-row before the 80-run sweep.
