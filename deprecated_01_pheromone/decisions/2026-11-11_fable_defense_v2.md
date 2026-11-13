# Fable decision after the null v3 defense (2026-11-11, owner-delegated)

Note: Fable aggregated saved `runs/sweep` logs with a scratch script (light analysis of saved outputs). The diagnostic numbers below are not saved outputs yet. Task M4 regenerates them as `results/real/defense_diagnostics.csv`.

## Why saved time does not become food (Fable diagnostics, defense on, mean per run)
| Diagnostic | d=1 | d=2 | d=4 |
| --- | --- | --- | --- |
| Gap from `cone_abort` to the same robot's next `follow_start` | 0.7 s | 0.6 s | 0.6 s |
| Share of gaps ≤ 5 s | 99 % | 99 % | 98 % |
| False-trail FOLLOW time before / after learning that decoy | 438 / 587 s | 765 / 848 s | 755 / 1061 s |
| `cone_abort` on / off false trail | 167 / 100 | 265 / 141 | 290 / 107 |
- `TryEnterFollow()` checks the cone with the current yaw only. `Follow()` turns 90°, and the gate opens again.
- Saved time goes to SEARCH. True-trail FOLLOW is unchanged.
- At d=0 with defense on, 13.3 of 13.7 `suspect_add` per run lie within 1.0 m of a real source (low precision).

## Decisions
- D-026: v3 80-run result is the G2 answer. Not edited. (Rejected: replacing G2 numbers with v2.)
- D-027: open defense v2 as ONE added arm, milestone M4 → S1 → Vision, cycle 0/2. One approach only.
- D-028: v2 mechanism = FOLLOW-entry lockout `t_lock` after `cone_abort`. Rejected: range-and-bearing sharing (drops no-communication premise, spreads wrong suspects), cautionary pheromone layer (third grid layer, refresh rates indistinguishable), trail freshness (needs identity or communication).
- D-029: v2 confirmation seeds 11-30. Tuning seeds 107-116. Criteria committed to `prereg/` before runs.
- D-030: v2 runs in new roots with code version v4. `def` stays 0/1. Seed range by CLI option. No schema change.
- D-031: main session runs v2 multi-seed runs locally, one core (named run, extends D-013).
- D-032: v2 does not block M3-04, M3-06, M2 fixes or the M3 gate. End date 2026-11-21.

## Defense v2 spec (lockout)
1. After `cone_abort`, `TryEnterFollow()` returns false for `t_lock` s. The robot turns 90° and wanders.
2. `t_lock` candidates 0 (v3 behavior), 5, 10, 20 s.
3. Other defense values stay at D-018. No new event or column. `t_lock` goes into manifest params only.
4. Invariance: v4 with `t_lock` = 0 reproduces saved v3 runs (e.g. `d2_def1_s1`, `d0_def0_s1` food).
5. Tuning: seeds 107-116, cells (d=2, on) and (d=0, on), 4 values, 80 runs.
6. Tuning metric: seed mean of food(d=2,on) + food(d=0,on). Highest wins. Tie goes to the smaller `t_lock`.
7. Confirmation: seeds 11-30, 8 cells, `runs/sweep_v2/` 160 runs. Control `runs/sweep_v2_lock0/` (`t_lock` = 0) 160 runs. Same v4 code.
8. Metric: G(2) = F(2,on) − F(2,off), seeds 11-30, paired bootstrap 10,000, 95 % interval.
9. Threshold: G(2) interval lower bound > 0.
10. Contrast: main = v2 on vs off. Attribution = picked `t_lock` vs 0, reported with interval. d=1, 4 reported only.
11. Failure: G(2) interval includes 0, or the d=0 cost interval upper bound < 0. Then v2 is reported as null.
12. Kill: tuning picks 0 → stop without confirmation. Seeds 11-30 are used once. 2 gate cycles, end 2026-11-21.
13. Expected ceiling (estimate): about 5 food, R(2) ≈ 0.15. Pass probability is not high.

## Report framing
- Headline is v3: the defense cut false-trail time by 28-30 %. Recovered food is below the 10-seed resolution (all R(d) intervals include 0).
- Do not write "the defense is useless". The result is about v3 as implemented.
- Two figures: time per state (END_SEARCH and false FOLLOW move to SEARCH), and the abort-to-refollow gap (0.6 s).
- Vision line stays. Write "not met with v3".
- v2 goes in its own section, marked "post-hoc design, confirmed on new seeds". Pass or fail uses the same format.
- Limits table: wrong suspects (13.7 per run at d=0), crowding (R10), decoy count (D-009), pairing limit (R11).
