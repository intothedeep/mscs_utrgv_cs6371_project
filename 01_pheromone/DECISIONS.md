> Completed items live in `_archive/` (cold storage, do not read unless
> investigating history). This doc holds the active + planned log only.

# Decisions: 01_pheromone

- Owner rule: Fable picks the best option and logs it here (repo-root `CLAUDE.md`, 2026-11-10).

| ID | Date | Decision | Why (line served) | Rejected | Decided by | Evidence | Supersedes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | 2026-11-10 | Build the rank 1 project: pheromone foraging under misleading trails | Mission | ranks 2 to 10 (lower score) | owner | `../site/en/projects/pheromone-misleading-trails.html` | none |
| D-002 | 2026-11-10 | Main session builds and runs 1-seed smoke runs per gate. Owner runs the full sweep | Constraints | build only (no gate demo), owner runs all (slow gates), local sweep (breaks no-local-execution) | owner | repo-root `CLAUDE.md` Execution | none |
| D-003 | 2026-11-10 | Folder `01_pheromone/` | Constraints | `01_feromon` (non-standard spelling) | owner | this folder | none |
| D-004 | 2026-11-10 | Mission, Vision, G1, G2 as in `PLAN.md` mission block | Mission | effect-size goal "defense recovers N %" (N has no basis, invites moving the bar), DBSCAN reimplementation goal (does not fit 2 weeks), "implement attack and defense" as mission (a mission must not finish) | Fable (owner-delegated) | `PLAN.md` | none |
