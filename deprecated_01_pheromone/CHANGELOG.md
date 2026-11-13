# CHANGELOG: code versions of the real pipeline

`code_version` is a constant in `src/loop_functions/pheromone_loop_functions/pheromone_loop_functions_log.cpp`.
Raise it by hand with a row here (`rules/measurement.md` 2.1, 2.2).

| Version | Date | What changed | Runs affected |
| --- | --- | --- | --- |
| v1 | 2026-11-11 | First real pipeline: honest forager, pheromone grid, food field, run logger. No detractors, no defense | none before it |
| v2 | 2026-11-11 | M3: detractor states (GO_DECOY, WAIT_DECOY, RETURN_LAY), defense rule (suspect list, mask, cone), events `decoy_reach`, `suspect_add`, `cone_abort`, `suspects_total`. New controller params `decoy_reach_m`, `t_wait`, `probe_radius_m`, `<defense>` | Runs with `code_version` v1 (smoke, tuning, judgement). Their d = 0, defense off path is meant to be unchanged |
| v3 | 2026-11-11 | M2 gate fixes: layout redraw when no decoy spot fits (D-019), decoy-to-decoy gap 1.0 m (D-020), valid peak needs `here` at least 2 x max(`here_entry`, `theta_on`) (D-021), no deposit in cells whose centre is inside the nest (I-7), `Reset()` closes the run log (I-14) | Every run with `code_version` v1 or v2. Layouts of seeds that broke the new gap change, and deposits near the nest change, so v3 results are not comparable with v1 or v2 results. The D-018 defense freeze and sweep runs made under v2 need a decision |
| v4 | 2026-11-11 | Defense v2 (D-028): FOLLOW-entry lockout `t_lock` seconds after a `cone_abort`, controller param `<defense t_lock>`, default 0. No new event or column | none by itself. With `t_lock` = 0 v4 must equal v3 (invariance check below). v3 runs in `runs/sweep` stay valid for the G2 answer (D-026) |
| v5 | 2026-11-11 | Defense v5 (D-039, D-047): confirm-twice. Controller param `<defense confirm_k>`, default 1. A suspect point acts (mask, cone, FOLLOW-entry test) only when `Count >= confirm_k`. `AddSuspect` unchanged. No new event or column | none by itself. With `confirm_k` = 1 and `t_lock` = 0 v5 must equal v4 (invariance below). v3 and v4 runs stay valid. Do not mix v4 and v5 runs in one root |
| v6 | 2026-11-11 | ID arm, "adapted arm" of TAROS 2024 (D-040, D-048, `DESIGN_M6.md`). New `<pheromone defense_mode="off\|v3\|v5\|id">` (absent = legacy = v4 behavior) and `id_margin`. New pure modules `owner_grid`, `trail_store`, `trail_clusters` (DBSCAN, no library), `id_defense`, `id_arm`, `defense_log`. `CPheromoneGrid::Deposit` takes an optional `p_won` (default null) and gains `CellIndexOf`, `ValueAt`, `ZeroCell`. Sidecar `defense_log.csv` in id mode only. No controller file, `schema.py` or schema column changes | none by itself. With `defense_mode` off or v3, `ticks.csv`, `robots.csv` and `events.csv` must equal the saved runs byte for byte, and the manifest differs only in code version, hashes, runid and the new `defense_mode` param (invariance below). v3, v4 and v5 runs stay valid. Do not mix v5 and v6 runs in one root |

Invariance for v6 (to be done before any M6 run, `tools/confirm_v6.py --stage invariance --run`): re-run `off` d = 0 seed 11 and `v3` d = 0 and d = 2 seed 11 with the frozen values into `runs/invariance_v6/`. Reference runs: `d0_def0_s11` of `runs/sweep_v2_lock0` (v4 code) and `d0_def1_s11`, `d2_def1_s11` of `runs/invariance_v5` (v5 code). The three CSV files must be byte equal and `metrics` must equal. The new code draws no random number and runs only in id mode. Result: PASS on 2026-11-11 (3 of 3 jobs byte equal, session log, `runs/invariance_v6/`).

Invariance for v5 (to be done before any M5 run, `tools/confirm_v5.py --stage invariance --run`): re-run `20261111-115700_d0_def1_s11` and `20261111-115700_d2_def1_s11` of `runs/sweep_v2_lock0` with `confirm_k` = 1, `t_lock` = 0 and the frozen values, into `runs/invariance_v5/`. `food_collected` and `events.csv` row counts must equal the saved v4 values, and params must equal except `confirm_k`. The new check adds no random draw, so the RNG order is the same. Result: PASS on 2026-11-11 (food 76 = 76 and 45 = 45, event rows equal, `runs/invariance_v5/`).

Invariance for v4 (to be done before any v2 run): re-run `d2_def1_s1` and `d0_def0_s1` of `runs/sweep` with `t_lock` = 0. `food_collected` must equal the saved v3 value. The lock adds no random draw, so the RNG order is the same.

Invariance check for v2 (done 2026-11-11: PASS, seed 101 food 86 equals v1 round 1, `runs/x_v2_invariance/`):

| Check | Expected |
| --- | --- |
| Re-run d = 0, defense off, seed 101 with the frozen values | `food_collected` equals the v1 round 1 value in `results/real/tuning/tuning_pick.json` |

Why it should hold: with the defense off, `IsConeHit()` is false and no extra random draw happens in the honest path.
If the numbers differ, v1 results are not comparable with v2 sweep runs. Report it before the sweep.

Invariance for v3: not expected. I-4 and I-7 change layouts and the pheromone near the nest, so d = 0 food can differ from v1.
Do not mix v2 and v3 runs in one sweep root. The architect decides which M3 results stand.
