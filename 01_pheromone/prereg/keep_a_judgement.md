# Pre-registration: keep-A judgement (D-010, M2)

Commit this file before the first judgement run (`rules/measurement.md` 1). Do not edit it after.
The judgement runs once. There is no retry.

| Line | Value |
| --- | --- |
| Metric | Mean `food_collected` per arm over seeds 104, 105, 106. Runs: d = 0, defense off, values from `tuning_pick.json`. |
| Threshold | Arm 1 mean is at least 1.2 times arm 2 mean. 1.2 is a planning threshold, not derived from noise (D-010). |
| Contrast | Arm 1: pheromone on. Arm 2: `follow_enabled="false"` (`θ_on` infinite, no following). Same seeds, paired. |
| Failure condition | Arm 1 is not above arm 2 on all 3 seeds, or the mean ratio is below 1.2. Then strategy A fails and B replaces it (D-010). |

- Runs: `tools/make_judgement.py --run`, 6 runs, one core, sequential (D-013).
- Verdict: `tools/judge_keep_a.py` writes `results/real/judgement/verdict.json`.
