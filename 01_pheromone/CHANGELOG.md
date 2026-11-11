# CHANGELOG: code versions of the real pipeline

`code_version` is a constant in `src/loop_functions/pheromone_loop_functions/pheromone_loop_functions_log.cpp`.
Raise it by hand with a row here (`rules/measurement.md` 2.1, 2.2).

| Version | Date | What changed | Runs affected |
| --- | --- | --- | --- |
| v1 | 2026-11-11 | First real pipeline: honest forager, pheromone grid, food field, run logger. No detractors, no defense | none before it |

Invariance evidence: v1 is the first version, so no older run exists to protect.
Later rows must add the evidence here (hash, or a re-run of a fixed seed that gives the same `food_collected`).
