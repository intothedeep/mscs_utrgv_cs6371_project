# Project-end review: 01_pheromone (M8-04, also the gates M3-08, M4-07, M5-10, M6-09, M7-05)

- Reviewer: `reviewer` agent, 2026-11-11. Gate review 1 for M3 to M8 (PLAN lines show `cycle 0/2; recovery 0/2`).
- Target: `01_pheromone/` at submodule commit `d34a3de` (2026-11-11 16:04:06), clean working tree.
- Verdict: **ISSUE**. 0 defects in the measured results. 3 exit criteria are not met as written (P-1, P-2, P-3). 14 minor issues and notes.
- The science checks pass. Every pre-registration was committed before its first run. No confirm seed block was reused. Every verdict re-derives from the saved runs. 29 of 32 sampled report rows (over 100 values) match their source files, 1 is rounded, 1 is not verified and 1 is a stale sentence.
- ISSUE here means document and evidence work. It does not mean an invalid result.
- This file covers the reviewer part of the project-end review. `system-architect` and `data-analyst` report separately.

## What was run in this review

| Command (form: `OMP_NUM_THREADS=1 timeout 300 uv run python ...`) | Result |
| --- | --- |
| `tools/check_runs.py runs/v5_confirm` | exit 0, `SUMMARY runs=800 failed=0 problems=0` |
| `tools/check_runs.py runs/m6_confirm/id` | exit 0, `SUMMARY runs=160 failed=0 problems=0` |
| `tools/check_runs.py runs/m7_scale/v5_n40` | exit 0, `SUMMARY runs=60 failed=0 problems=0` |
| Scratchpad script `rederive.py`: reads manifests of 26 run roots, calls `tools/g2_stats.paired_diff_interval` | see "Verdict re-derivation" and "Seed blocks" |
| Scratchpad script `g2chk.py`: calls `tools/g2_stats.g2_rows` on `runs/v5_confirm` and `runs/sweep_v2` | intervals equal the verdict files to every printed digit |
| `git log`, `git show --stat`, `stat`, `grep`, `shasum` | read only |

- Not run: `argos3`, cmake, make, any judge or report script, a browser render.
- Disclosure: two early read-only scans used bare `python3` (manifest and JSON reads). `rules/development/python.md` §1 asks for `uv run python`. Later runs used the right form.
- Four demo frames were opened and viewed (`results/real/mvp3/demo/d2_def0_10.png`, `d2_def0_19.png`).
- The root `CLAUDE.md` was re-read from disk. Its lines 20 to 23 hold the local-run permission, the Fable delegation and the root-cause rule.

## Milestone gates

| Gate | Exit criterion (TASKS.md) | Status | Evidence |
| --- | --- | --- | --- |
| M3 | 1. Smoke d = 2, defense on, passes the check, has `decoy_reach` and `suspect_add` | met, seed differs | `runs/smoke/20261111-113131_d2_def1_s6`: 18 `decoy_reach`, 61 `suspect_add`, `results/real/check_log.txt` 0 failed. The criterion names seed 1 (P-14) |
| M3 | 2. Defense tuning ran, `defense_pick.json`, freeze D-row before the sweep | met | `runs/defense_tuning/` 9 runs on v3, D-018, D-025 |
| M3 | 3. `check_runs.py runs/sweep` exits 0 on 80 complete runs | met | `results/real/check_sweep_log.txt` `runs=80 failed=0`. Manifests: 8 cells x seeds 1 to 10, all v3, one commit `af3c7cf`, `git_dirty` false |
| M3 | 4. `g2_recovered_share.png` with 95 % bars | met | file exists, `results/real/g2_stats.csv` 4 rows |
| M3 | 5. Qt demo frames at d = 2, off and on, with a trail turning pale | met | 21 and 22 frames under `results/real/mvp3/demo/`. Frame 19 shows the right-hand red trail paler than frame 10 |
| M3 | 6. MVP3 stage reports and `results/index.html` | met | `results/real/mvp3/*.html` (6 stage pages), `results/index.html` |
| M3 | Schema re-check (M3-08) | met | `schema.py`: one change since M1 (`8ac7e2c`, `WAIT_DECOY`, M1 fix). `check_runs.py`: unchanged through M6, one change at M7 (P-5) |
| M3 | M2 I-1 and I-2 closed (M3-08) | met | I-1: D-022 plus the fade frames above. I-2: D-023 and the full v3 chain rerun D-025 |
| M4 | 1. v4 invariance with `t_lock` 0 | met | `runs/invariance_v4/`: 8 of 8 cells equal `runs/sweep` seed 1 (food 56, 52, 32, 37, 24, 27, 27, 22) |
| M4 | 2. `pick.json`, freeze D-row before confirmation | met in part | `results/real/tuning_v2/pick.json` picks 10 s. No freeze D-row (P-8) |
| M4 | 3. Check exits 0 on both roots, 160 runs each | met | `results/real/check_sweep_v2.txt`, `check_sweep_v2_lock0.txt`, both `failed=0`. Manifests: seeds 11 to 30, v4 |
| M4 | 4. `results/real/v2/verdict.json` exists | met | verdict `fail`, D-033 |
| M4 | 5. Final report has the defense v2 section (M4-06) | **not met as written** | The section exists (`results/report.html:130`). 4 static criteria of M4-06 are missing (P-1) |
| M5 | 1. `v5_killcheck.md` states "go v5" or "switch to A'" | **not met as written** | `results/real/v5_killcheck.md:8` still reads `[TBD]`. The CSV holds the answer: 1.70 [1.20, 2.20] against 7.2 (P-2) |
| M5 | 2. v5 invariance on 2 cells | met | `runs/invariance_v5/` 2 runs, `CHANGELOG.md:17` (76 = 76, 45 = 45) |
| M5 | 3. Mechanism table, seeds 201 to 210 | met | `results/real/v5/mechanism.md`, 40 runs in `runs/v5_check/` |
| M5 | 4. Check exits 0 on 800 runs, seeds 221 to 260 | met | re-run here, exit 0 |
| M5 | 5. `verdict.json` with prereg path and judge sha256 | met | sha256 equals `tools/judge_v5.py` on disk |
| M5 | 6. Root-cause memo on fail, RQ1 cites the verdict | met | verdict pass. `results/real/v5/root_cause.md` says "not required". `RQ.md:11` |
| M6 | 1. Arm check, seeds 301 to 310 | met | `results/real/id_arm/arm_check.csv`: 2 of 2 detractors isolated at d = 2 in 10 of 10 seeds |
| M6 | 2. Check exits 0 on the confirm root | met, count differs | 5 roots x 160 = 800 runs, not 640 (D-052 adds k1t10). `runs/m6_confirm/id` re-run here, exit 0. Other 4 roots: saved `check_*.txt`, `failed=0` |
| M6 | 3. `verdict.json` with one of the three words | met | "differs" |
| M6 | 4. Root-cause memo on fail, RQ2 cites the verdict | met | not a fail. `results/real/id_arm/root_cause.md`, `RQ.md:12` |
| M7 | 1. Check exits 0 on 360 runs, seeds 401 to 430 | met | 6 roots x 60. `runs/m7_scale/v5_n40` re-run here, exit 0. Other 5: saved `check_*.txt`, `failed=0` |
| M7 | 2. `verdict.json` with the congestion check | met | ratio 0.6117, threshold 0.5, not triggered |
| M7 | 3. Root-cause memo, RQ3 cites the verdict | met | `results/real/scale/root_cause.md` (method committed in `c3ddab3` with `[TBD]` cells, 16 s before `root_cause.csv` was written). `RQ.md:13` |
| M8 | 1. T-E table, 7 rows and 5 columns | met in substance | `research/cost_of_trust.md` Table 1: 8 rows, 7 data columns. Path and shape differ from the criterion (P-13) |
| M8 | 2. Report opens with one comparison chart, one failure section per failed verdict | **not met as written** | Failure sections F1, F2, F3 exist and link the memos. The page opens with text. The comparison chart first appears at `results/report.html:208`. M8-02 is still `[~]` (P-3) |
| M8 | 3. G3: 3 of 3 verdict files, a memo per fail | met | 3 committed verdict files. M7 memo exists. M5 and M6 hold one-line memos |
| M8 | 4. Slides outline | met | `results/slides_outline.md`, 12 slides, each names a figure or table |

## Dispatch checks

### 1. Pre-registration before the first run

Times are the prereg commit time against the first manifest write time of the block. Runids are generation times and are not used here (800 `v5_confirm` runids span 20 s).

| Prereg file | Commit | First run of its block (manifest write) | Run `git_commit`, `git_dirty` | Status |
| --- | --- | --- | --- | --- |
| `pheromone_tuning.md`, `keep_a_judgement.md` | `e6c889b` 11:13:55 | `runs/x_v2_tuning` 11:14:18 | `8ac7e2c`, false | met |
| `defense_tuning.md`, `defense_candidates.json` | `b3f32b3` 11:26:16 | `runs/x_v2_defense_tuning` 11:26:23 | `b3f32b3`, false | met |
| `defense_v2_lockout.md` | `c8d79f2` 11:51:20 | `runs/tuning_v2` 11:51:50 | `c8d79f2`, false | met |
| `defense_v5.md` | `80c96e2` 12:40:47 | `runs/v5_check` 12:41:03, `runs/v5_confirm` 12:42:21 | `80c96e2` and `0751b55`, false | met |
| `defense_id_arm.md` | `ac9bb34` 13:01:00 | `runs/m6_check/id` 13:01:03, `runs/m6_confirm` 13:01:37 | `ac9bb34` and later, false | met, 3 s margin |
| `scale.md` | `0d917b5` 13:05:46 | `runs/m7_scale` 13:19:38 | `c4a6f79`, `ab0b7eb`, false | met |

- Every prereg file has exactly one commit. None was edited after its runs.
- Runs before a prereg commit are the exempt kinds only: invariance reruns (`runs/invariance_v5` 12:40:57 is after the commit anyway) and seed 900 smoke runs (`runs/m6_smoke` 13:00:09).
- Method files for the kill check, the margin and the M7 root cause were committed with `[TBD]` cells before their CSV files were written (`372d834` 12:28:34 against 12:28:37, `f775fb6` 12:44:01 against 12:59:39, `c3ddab3` 13:43:14 against 13:43:30).
- D-050 was committed at 12:55:23, before the M5 verdict file (12:59:20). D-053 was committed at 13:02:03, before the M6 verdict file (13:19:05).

### 2. Seed blocks (D-043)

| Block | Roots that hold it | Status |
| --- | --- | --- |
| 201 to 210 | `runs/v5_check` only | used once |
| 221 to 260 | `runs/v5_confirm` only, 20 cells x 40 seeds, no duplicate cell | used once |
| 301 to 310 | `runs/m6_check/id` only | used once |
| 321 to 360 | `runs/m6_confirm/{off,v3,k1t10,v5,id}` only, 4 cells x 40 seeds each | used once |
| 401 to 430 | `runs/m7_scale/*` only, 2 cells x 30 seeds each | used once |
| 11 to 30 | `runs/sweep_v2`, `runs/sweep_v2_lock0` (both in the prereg). Seed 11 also in `invariance_v5`, `invariance_v6` (exempt reruns) | used once for confirmation |
| 211 to 220, 311 to 320 | none | unused |
| 900 | `runs/m6_smoke`, `runs/m7_smoke` | throwaway, report only |

- Note: seeds 1 to 10, 101 to 103 and 104 to 106 were run again on v3 after the v2 code fixes. The old runs sit in `runs/x_*`. D-019, D-020 and D-025 log it. Both keep-A judgements passed.

### 3. Verdict re-derivation

Food values were read from the run manifests, not from the verdict files. Intervals come from the project function with its fixed seed.

| Verdict file | Prereg rule | Re-derived | In the file | Verdict by the rule |
| --- | --- | --- | --- | --- |
| `judgement/verdict.json` | arm 1 mean at least 1.2 x arm 2, and above on 3 of 3 seeds | 75.67 against 27.67, ratio 2.73, 3 of 3 | same | pass, correct |
| `v2/verdict.json` | G(2) lower bound above 0. Fail if the d = 0 cost upper bound is below 0 | G(2) 4.05 [0.85, 7.25]. Cost −6.7 [−9.7, −3.85] | same | fail, correct. The cost rule fires |
| `v5/verdict.json` | same form, arm k2t10, seeds 221 to 260 | G(2) 2.75 [0.40, 4.975]. Cost 0.125 [−0.975, 1.15] | same | pass, correct |
| `v5/verdict.json` main effects | reported only | E_k 3.0625 [1.5375, 4.625] and −2.7875 [−4.475, −1.1625]. E_t −0.2375 [−1.3375, 0.825] and 0.9625 [−0.4128, 2.3628] | same | D-057 is right: E_t includes 0 at both d |
| `id_arm/verdict.json` | interval of F(2, id) − F(2, k1t10) excludes 0. Failure if more than 20 seeds have no detractor isolated | 4.375 [2.25, 6.45]. `isolation.csv`: 0 seeds at d = 2 with 0 isolated | same | "differs", correct |
| `scale/verdict.json` | interval of g_40 − g_20 excludes 0, per arm. Congestion if the ratio is below 0.5 | v5 −0.2458 [−0.4108, −0.085]. v3 −0.1458 [−0.3175, 0.0234]. Ratio 0.6117 | same | "v5 scales worse, v3 not resolved", correct |

- D-052 holds: mean F(2) on seeds 221 to 260 is k1t10 46.1, k1t0 45.625, k2t10 43.8.
- `judge_code_sha256` equals the sha256 of the judge script on disk in 5 of 5 verdict files.
- All confirm manifests are `complete` with 6000 ticks. One code hash pair per block.

### 4. Report numbers against source files

Each row is one value or one value with its interval. All were read from `results/report.html` and compared with the named file.

| # | Report value | Source | Status |
| --- | --- | --- | --- |
| 1 | RQ1 cost 0.125 [−0.975, 1.15] | `v5/verdict.json` `failure.d0_cost` | match |
| 2 | RQ1 gain 2.75 [0.40, 4.975] | `v5/verdict.json` `metric_G2` | match |
| 3 | k1t10 gain 5.05 [2.025, 7.975] | `v5/verdict.json` | match |
| 4 | RQ2 4.375 [2.25, 6.45] | `id_arm/verdict.json` | match |
| 5 | Honest isolated 9.05, 10.25, 15.925, 15.6 | `id_arm/verdict.json` | match |
| 6 | RQ3 0.273, 0.0275, −0.246 [−0.411, −0.085] | `scale/verdict.json` | match |
| 7 | Cost per robot diff −0.010 [−0.056, 0.036] | `scale/verdict.json` | match |
| 8 | R(2) 0.07 [−0.02, 0.15] | `real/g2_stats.csv` | match |
| 9 | Table 2, 4 rows (75.8, 73.9, 57.4, 56.5, 18.4, 42.1, 44.4, 33.7, 38.3, 39.2, 37.5) | `real/g2_stats.csv` | match |
| 10 | v2 gain 4.05 [0.85, 7.25], cost −6.7 [−9.7, −3.85] | `v2/verdict.json` | match |
| 11 | Control cost −6.15 [−8.25, −4.05], attribution 1.7 [−1.0, 4.45] | `v2/verdict.json` | match |
| 12 | Table 4 (11.90, 1.80, 4.80, 0.30, 36.60, 18.80, 27.60, 3.70) | `v5/mechanism.md` | match |
| 13 | Table 5, 12 cells | `v5/verdict.json` | match |
| 14 | Table 6, 6 cells | `v5/verdict.json` `main_effects` | match |
| 15 | Table 7, 16 cells | `real/final/arm_contrasts.csv`, manifests | match |
| 16 | Defense-off food 81.4, 58.3, 43.85, 32.625 | `id_arm/verdict.json` | match |
| 17 | Table 9 (0.2083, 0.0625, 0.2733, 0.0275, both intervals) | `scale/verdict.json` | match |
| 18 | Table 10, 12 values | `scale/verdict.json` | match |
| 19 | Congestion 3.9533, 2.4183, 0.6117 | `scale/verdict.json` | match |
| 20 | Kill check 1.70 [1.20, 2.20] against 7.2 | `real/v5_killcheck.csv:98420` | match |
| 21 | Margin 5.4, distance 0.3 m | `real/m6_margin.csv:13432`, `prereg/defense_id_arm.md:11-12` | match |
| 22 | 30-seed cost −4.73 [−6.70, −2.80] | `real/failure_analysis.md:12` | match |
| 23 | 14.45 of 14.6, 102.55 of 102.6, 9.7 (66 %), 12.8 (89 %) | `real/failure_analysis.md:15-16, 135` | match |
| 24 | Pickups −7.2 [−9.35, −5.2], 2.14 against 1.48, 0.41 m against 0.32 m | `real/failure_analysis.md:136-138` | match |
| 25 | Lockout alone +3.25 [0.9, 5.55], 14 to 18 % | `real/failure_analysis.md:105, 80-81` | match |
| 26 | M7 cause: 3.55 to 1.98, 0.244 to 0.126, −0.118, +12.29, −0.210 | `scale/root_cause.md:161-173` | match |
| 27 | M7 cause: −0.766, −0.107, −0.139, −7.18, −0.100, 0.247 to 0.011, 0.140 to 0.023 | `scale/root_cause.md:141-145, 169, 239, 244` | match |
| 28 | Fixed N gain per robot 0.138 and 0.250 | `scale/root_cause.md:197` | match |
| 29 | "57 decisions, D-001 to D-057" | `DECISIONS.md` | match |
| 30 | "within 0.6 s" | `real/failure_analysis.md:84` gives 0.59 to 0.71 s | rounded, see P-10 |
| 31 | Figure 7 caption: the v5 interval at 40 robots includes 0 | not in `scale/verdict.json` | not verified, see P-16 |
| 32 | "The memo is stale on those cells" (`report.html:319`) | `research/cost_of_trust.md:67-71` now holds them | mismatch, see P-10 |

- `results/slides_outline.md`: its numbers on slides 5 to 11 were read and equal the report.
- `research/cost_of_trust.md` Table 2: 5 rows equal `arm_contrasts.csv` and `id_arm/verdict.json`.

### 5. Root-cause memo for every fail or "scales worse"

| Result | Memo | Status |
| --- | --- | --- |
| v3 null (G2, seeds 1 to 10) | `results/real/failure_analysis.md` | present |
| v2 FAIL (D-033) | `results/real/failure_analysis.md` | present, 6 candidates with verdicts |
| M5 PASS | `results/real/v5/root_cause.md` | one line, "not required" |
| M6 "differs" | `results/real/id_arm/root_cause.md` | one line, "not required" |
| M7 "v5 scales worse" | `results/real/scale/root_cause.md`, D-056 | present, 6 candidates, states its own limit |

### 6. Schema contract

- The 3 allowed checks exit 0 (table above).
- `tools/schema.py` has no change since `8ac7e2c`. No column, event or manifest key changed in M3 to M7.
- `tools/check_runs.py` changed once, in `0d917b5` (M7). See P-5.
- The M6 sidecar `defense_log.csv` sits beside the 4 schema files and is not checked. `DESIGN_M6.md:205-206` planned this.

### 7. Build

- `src/build/controllers/pheromone_forager/libpheromone_forager.dylib` (143,160 bytes, built 12:59).
- `src/build/loop_functions/pheromone_loop_functions/libpheromone_loop_functions.so` (256,912 bytes, built 12:59).
- Their sha256 prefixes are `8c08ff75e914` and `62c04f70734e`. These equal `code_sha` in every M6 and M7 manifest.
- `src/build/cmake.log` holds one CMake deprecation warning and no error. The `make` output is not saved (same as M2 I-9).
- No rebuild was done.

## MVP ladder checks

| Check | Status | Evidence |
| --- | --- | --- |
| L1 schema is the single contract | ISSUE, minor | `schema.py` unchanged. `check_runs.py` was changed to read `n_honest` from the manifest for the M7 runs, with no D-row and no DESIGN §4 line (P-5) |
| L2 no pipeline before the flow ran on mocks | ISSUE, minor | M5 and M7 add no stage. M6 adds a sidecar stage. `DESIGN_M6.md:230` asks for a mock sidecar first. `tools/make_mock_sidecar.py` exists. No saved mock output or stage report shows it ran (P-6) |
| L3 mock is unmistakable and isolated | PASS | `mock/` holds `runs/` with `MOCK_` runids only. No real-path tool reads `mock/`. `tools/v6_arm_table.py:46` refuses to write mock data outside `mock/` |
| L4 a phase opens only when the previous exit is closed | ISSUE, minor | M4 opened under D-032. M5 to M8 opened and finished while the M3 and M4 gates were open. M8-04 was dispatched while M8-02 is `[~]`, against `PLAN.md:71` (P-7) |

## Hierarchy checks

| Check | Status | Evidence |
| --- | --- | --- |
| H1 trace | ISSUE, minor | Mission block in `PLAN.md:7-25`. `DESIGN_M5.md:6`, `DESIGN_M6.md:9` quote it. `DESIGN.md:9` quotes the old mission (known, `PLAN.md:83`). Every M3 to M8 task tags its milestone. Milestones trace to S1 or S2 and to G1 to G3 or an RQ. Counters within bounds, but stale. No `budget:` line. Stale lines in P-4 and P-9 |
| H2 decisions logged | ISSUE, minor | D-026 to D-057 cover the choices since the M2 gate, each with a line served and a saved-file path. Gaps: no freeze D-row for the `t_lock` pick, the D-025 row was committed after the rerun it covers, no row for the `check_runs.py` change (P-5, P-8) |

## Issues

| ID | Severity | Class and route | Where | What | Fix suggestion |
| --- | --- | --- | --- | --- | --- |
| P-1 | medium | implementation, `developer`. AC wording to `product-manager` | `TASKS.md:227-234`, `results/report.html:130-160` | M4 exit 5 is not met as written. The v2 section lacks the label "post-hoc design, confirmed on new seeds", the two figures from `defense_diagnostics.csv` (time per state, abort-to-refollow gap) and the pairing limit (R11). The "not met with v3" wording refers to the old Vision (D-035) | Add the label, the two figures and the R11 line through the report script. pm rewrites the stale Vision criterion |
| P-2 | medium | implementation, `data-analyst` or main session | `results/real/v5_killcheck.md:8`, `:73` (18 `[TBD]`). `results/real/m6_margin.md:3`, `:78` (14 `[TBD]`) | M5 exit 1 is not met as written. Both memos still hold placeholders. D-046 and the M6 prereg rest on numbers that exist only in the CSV files and the session output | Fill both memos from `v5_killcheck.csv` and `m6_margin.csv`. Copy the script's verdict line |
| P-3 | medium | implementation, `developer` and main session | `results/report.html:30`, `:208`. `TASKS.md:371`, `:381`. `PLAN.md:71` | M8 exit 2 is not met as written. The page opens with text and the comparison chart comes at Figure 4. M8-02 is still in progress, and the plan says M8-04 waits for it. No saved browser render exists | Move one comparison chart to the top, or pm rewrites "opens with". Render once per `rules/answering.md` §3, then tick M8-02 |
| P-4 | medium | hierarchy (H1), `product-manager` | `TASKS.md:284-287`, `:330-332`. `PLAN.md:20-25`, `:70`. `DESIGN.md:9` | Living docs are stale. M5-09 and M6-08 say the "not required" memos do not exist. Both exist and are committed. Open counts in the stub follow that. Cycle counters for M3 to M8 read 0/2 after this review | Tick M5-09 and M6-08. Update the stub counts. Set the counters to 1/2. Architect updates the DESIGN mission quote |
| P-5 | minor | ladder (L1), `system-architect`. D-row to `product-manager` | `tools/check_runs.py:27-29`, `:152`. `tools/schema.py:27`. `DESIGN.md:195` | The validator now reads the honest count from the manifest param `n_honest`. The key is not named in `schema.py` or DESIGN §4. No D-row logs the change. Old runs still pass (default 20) | Name `n_honest` in `schema.py` and DESIGN §4. Log one D-row |
| P-6 | minor | ladder (L2), `system-architect` answers, main session saves evidence | `DESIGN_M6.md:230`, `tools/make_mock_sidecar.py` | The design asks for a mock sidecar run before real code. No saved output shows it | Save the mock arm-check output under `mock/`, or state in STATUS that the step was skipped and why |
| P-7 | minor | ladder (L4), `product-manager` | `PLAN.md:20-25`, `:71` | M5 to M8 ran with the M3 and M4 gates open. D-032 covers M4 only. This review was dispatched before M8-02 closed | Log one D-row for the order, as D-015 and D-023 did |
| P-8 | minor | hierarchy (H2), `product-manager` | `TASKS.md:193`, `DECISIONS.md:34` | No freeze D-row before the v2 confirmation. The D-025 row was committed at 11:37:39, after the v3 chain rerun (11:31 to 11:34) | Note only. Write rows before dependent work in later tracks |
| P-9 | minor | hierarchy (H1), `product-manager` | `DECISIONS.md:66`, `RQ.md:11-13`, `STATUS.md:56-61`, `PLAN.md:14-15`, `:70`, `TASKS.md:372`, `research/cost_of_trust.md` row S-CT-16 | Lines are dated 2026-11-12. Their commits and the machine clock say 2026-11-11 | Correct the dates in place |
| P-10 | minor | implementation, `developer` | `results/report.html:319`, `:134` | The Table 12 note says the memo lacks the M6 gain cells. `research/cost_of_trust.md:67-71` holds them. "within 0.6 s" rounds a source range of 0.59 to 0.71 s | Drop the stale sentence. Write "about 0.6 to 0.7 s" |
| P-11 | minor | implementation, `developer` | `results/report.html:445`, `prereg/scale.md:41` | The seed table lists seed 900 for M6 smoke only. M7 smoke used it too. Invariance reruns on seeds 1 and 11 are not listed | Add both lines |
| P-12 | minor | implementation, `sonnet-writer` | `results/slides_outline.md:9`, `RQ.md:13` | Slide 1 writes "v5 scales worse (yes)". The RQ3 answer is "no" | Write the three answers as yes, differs, no |
| P-13 | minor | hierarchy, `product-manager` | `TASKS.md:370`, `:377-378`, `PLAN.md:41-64` | M8 exit 1 names `results/real/te_table.md` with 7 rows and 5 columns. The table is `research/cost_of_trust.md` Table 1 with 8 rows and 7 data columns | Rewrite the exit line and add the path to Fixed paths |
| P-14 | minor | hierarchy, `product-manager` | `TASKS.md:138`, `:298`, `:326`, `prereg/defense_id_arm.md:22`, `:31` | M3 exit 1 names seed 1, the saved smoke run is seed 6. M6 exit 2 names 640 runs, 800 ran (D-052). The prereg lists 5 arms in line 22 and 4 roots in line 31 | Rewrite the two exit lines. Do not edit the prereg. Note the root list in the report limits |
| P-15 | minor | implementation, `developer` | `results/report.html:427` | "named by rule before the data existed" is exact for D-053 only. D-050 was committed while the M5 confirm runs were being written (12:42 to 12:58), before the verdict. Its rule selects on M5 data by design and M6 tests on fresh seeds | Write "before the M5 verdict was computed" for D-050 |
| P-16 | note | reasoning, `data-analyst` | `results/report.html:286`, `:255`, `results/real/id_arm/arm_check.csv` | The Figure 7 caption claim (v5 interval at 40 robots includes 0) has no value in `scale/verdict.json`. Figure 6 groups are read by eye. In the arm check the id arm isolates 16 to 19 of 20 honest robots in 9 of 10 seeds at d = 2 | Cite a saved value for the caption or drop it. Confirm that the id-arm gain reading holds with that isolation level |
| P-17 | low | not checked | `results/report.html`, `results/index.html` | No browser render in this review (outside the allowed runs). `src/build` has no saved `make` output | Main session renders the report once. Save `make` output at the next build |

- Source-citation check on `research/cost_of_trust.md`: 23 distinct `[S-...]` IDs, each resolves to one Sources row. No `[CONFLICT]` or `[UNVERIFIED]` tag. 7 open questions are listed.

## To close

1. `developer` fixes the report (P-1, P-3, P-10, P-11, P-15). Main session regenerates and renders it once.
2. `data-analyst` or the main session fills the two `[TBD]` memos from their CSV files (P-2).
3. `product-manager` ticks M5-09 and M6-08, updates the stub, counters and dates, and rewrites the 4 stale exit lines (P-4, P-9, P-13, P-14). It logs the D-rows of P-5 and P-7.
4. `system-architect` names `n_honest` in the schema and answers P-6.
5. `sonnet-writer` fixes slide 1 (P-12).
6. A second review (cycle 2 of 2) reads the rebuilt report, the two filled memos and the updated living docs. No run needs to be repeated.
