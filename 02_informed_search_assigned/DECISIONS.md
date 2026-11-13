> Completed items live in `_archive/` (cold storage, do not read unless
> investigating history). This doc holds the active + planned log only.

# Decisions: 02_informed_search_assigned

- Owner rule: Fable picks the best option and logs it here (repo-root `CLAUDE.md`, 2026-11-12).

| ID | Date | Decision | Why (line served) | Rejected | Decided by | Evidence | Supersedes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | 2026-11-12 | Build Final Project 2 in `02_informed_search_assigned/`. Baseline is `Collision_Free_CPFA` commit `9480f2e`, cloned to `vendor/` and never edited | Constraints | edit the vendor clone in place (breaks invariance check) | owner (folder name), Fable (layout) | `README.md` | none |
| D-002 | 2026-11-12 | Main session builds and runs locally: one core, `timeout`, sequential, all evaluation runs included | Constraints | owner runs all (slow gates), smoke only | owner | repo-root `CLAUDE.md` Execution | none |
| D-003 | 2026-11-12 | Mission: find ground no robot has searched, so the swarm collects more in 12 minutes. Keep server cost small as swarms and arenas grow | Mission | architect draft without the score (grade is ranked by score) | Fable, owner-delegated | DESIGN.md §0, assignment PDF p. 3 | none |
| D-004 | 2026-11-12 | Vision: one page shows 3-distribution box plots with % improvement over original CPFA and its interval, a query-cost vs arena-size chart beside the student grid, and a cause for each failure | Vision | none | Fable, owner-delegated | DESIGN.md §0 hand-back | none |
| D-005 | 2026-11-12 | Goals G1 to G3 and RQ1 to RQ3 as drafted by the architect (benchmark by 11-21, 300 evaluation runs and verdict by 11-27) | Goal | none | Fable, owner-delegated | DESIGN.md §0 hand-back | none |
| D-006 | 2026-11-12 | F1: nest radius XML 0.25 (effective 0.456 m) is the primary set. XML 0.137 (effective 0.25 m) runs as a full sensitivity set | Goal (G2) | one reading only (risk: professor means the other) | Fable, owner-delegated | DESIGN.md §2 F1 | none |
| D-007 | 2026-11-12 | F2: keep resource respawn on pickup in both arms, as the baseline does | Constraints (vendor unchanged) | disable respawn (changes the professor's baseline) | Fable, owner-delegated | DESIGN.md §2 F2 | none |
| D-008 | 2026-11-12 | F3: one CPFA parameter set (the 10x10 xml set) for all distributions and both arms | Goal (G2, fair comparison) | per-distribution sets (no powerlaw set exists in the repo) | Fable, owner-delegated | DESIGN.md §2 F3 | none |
| D-009 | 2026-11-12 | F4: tune only the new method's parameters on tuning seeds. The 7 CPFA values stay fixed. Touching them gives the baseline the same budget | Goal (G2, fairness) | re-tune CPFA for our arm only | Fable, owner-delegated | DESIGN.md §2 F4 | none |
| D-010 | 2026-11-12 | Algorithm: option B, region quadtree with availability summaries and reservation. Option A (fine grid) stays as fallback behind the same interface | Strategy | A primary (memory grows with area), C (no completeness bound, highest risk) | Fable, owner-delegated | DESIGN.md §3.5 | none |
| D-011 | 2026-11-12 | Statistics in numpy only (paired bootstrap CI decides; Wilcoxon in a table, implemented in numpy). No SciPy dependency | Constraints (KISS) | add SciPy | Fable, owner-delegated | DESIGN.md §6.7 | none |
| D-012 | 2026-11-12 | G1 verdict at 80 m only (the professor's example scale). Larger arenas are reported, not judged | G1 | judge "80 m and larger" (more ways to fail on sizes the assignment never names) | Fable, owner-delegated | DESIGN.md §5.2 | none |
| D-013 | 2026-11-12 | Accept pm proposal: `tools/collect_runs.py` builds `runs.csv` from run folders | G2 | analysis reads run folders directly (duplicates parsing in every tool) | Fable, owner-delegated | PLAN.md Open items | none |
| D-014 | 2026-11-12 | Accept pm proposal: the vendor arm writes header-only `queries.csv` and `points.csv`, so every run has the same file set | G2 (one schema) | arm-specific file sets (checks branch per arm) | Fable, owner-delegated | PLAN.md Open items | none |
