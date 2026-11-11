# CHANGELOG: code versions of the real pipeline

`code_version` is a constant in `src/loop_functions/pheromone_loop_functions/pheromone_loop_functions_log.cpp`.
Raise it by hand with a row here (`rules/measurement.md` 2.1, 2.2).

| Version | Date | What changed | Runs affected |
| --- | --- | --- | --- |
| v1 | 2026-11-11 | First real pipeline: honest forager, pheromone grid, food field, run logger. No detractors, no defense | none before it |
| v2 | 2026-11-11 | M3: detractor states (GO_DECOY, WAIT_DECOY, RETURN_LAY), defense rule (suspect list, mask, cone), events `decoy_reach`, `suspect_add`, `cone_abort`, `suspects_total`. New controller params `decoy_reach_m`, `t_wait`, `probe_radius_m`, `<defense>` | Runs with `code_version` v1 (smoke, tuning, judgement). Their d = 0, defense off path is meant to be unchanged |

Invariance check for v2 (to be done at the M3 gate, not yet done):

| Check | Expected |
| --- | --- |
| Re-run d = 0, defense off, seed 101 with the frozen values | `food_collected` equals the v1 round 1 value in `results/real/tuning/tuning_pick.json` |

Why it should hold: with the defense off, `IsConeHit()` is false and no extra random draw happens in the honest path.
If the numbers differ, v1 results are not comparable with v2 sweep runs. Report it before the sweep.
