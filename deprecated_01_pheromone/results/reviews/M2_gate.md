# M2 gate review: MVP2 real slice, 0 detractors

- Reviewer: `reviewer` agent, 2026-11-11. Gate review 1 for M2 (PLAN line shows `cycle 0/2; recovery 0/2`).
- Target: `01_pheromone/` at submodule commit `f3d6c73`. Saved runs: `runs/smoke/` (1), `runs/tuning/` (9), `runs/judgement/` (6).
- Verdict: **ISSUE**. 2 blocking issues (I-1, I-2), 13 minor. Both blocking issues are document and evidence work. No C++ defect blocks M2.
- The real slice works: 16 real runs pass the unchanged check, the D-007 and D-010 rules were applied exactly, and the pre-registrations were committed before the runs.
- The repository moved during this review. Commits `b3f32b3` (11:26:16) and `5884cf4` (11:26:44) added M3 code, the defense tuning and D-018. At 11:27 `runs/sweep/` held 40 run folders.
- Every file reviewed here was compared with `f3d6c73` by line count or hash. Paths written `f3d6c73:<path>` have a later version on disk.
- I-4 and I-5 do not block M2, but the running M3 sweep depends on both. Decide them now.

## What was run in this review

| Command (form: `OMP_NUM_THREADS=1 timeout 300 uv run python ...`) | Result |
| --- | --- |
| `tools/check_runs.py runs/smoke` | exit 0, `SUMMARY runs=1 failed=0 problems=0` |
| `tools/check_runs.py runs/tuning` | exit 0, `SUMMARY runs=9 failed=0 problems=0` |
| `tools/check_runs.py runs/judgement` | exit 0, `SUMMARY runs=6 failed=0 problems=0` |
| Read-only cross-check of the 16 saved run folders (scratchpad script, CSV and JSON only) | see "Cross-check of saved logs" |

- Not run here (outside the allowed runs): cmake, make, `argos3`, `analyze.py`, `make_report.py`, a browser render of the pages.
- Both Qt frames were opened and viewed.

## M2 exit criteria

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Main session builds `src/` with no error | met, evidence thin | Both libraries existed at review start (`libpheromone_forager.dylib`, `libpheromone_loop_functions.so`, built 11:13). `src/build/cmake.log` ends clean. The `make` output is not saved (I-9) |
| 2 | `make_sweep.py --cell 0,0,1 --root runs/smoke` writes one `.argos`. One headless run writes `runs/smoke/<runid>/` | met | `src/experiments/generated/20261111-111329_d0_def0_s1.argos`, `runs/smoke/20261111-111329_d0_def0_s1/` (4 files) |
| 3 | `check_runs.py runs/smoke` exits 0 with `check_runs.py` and `schema.py` unchanged since M1 | met, one note | Re-run here, exit 0. `check_runs.py` has no commit after `9c96d69`. `schema.py` changed once, in the M1 fix commit `8ac7e2c` (`STATES_DETRACTOR` gets `WAIT_DECOY`, M1 I-8). No column, event or manifest key changed (I-10) |
| 4 | `food_collected` > 0. `events.csv` has `pickup` and `drop` rows | met | Manifest: `food_collected` 85. Events: 92 `pickup`, 85 `drop` |
| 5 | `analyze.py runs/smoke` lists 79 missing cells and exits 0 | met | `results/real/analyze_log.txt` at `f3d6c73`: `CELLS expected=80 present=1 missing=79`, 79 `MISSING` lines, `OUTPUT` line written |
| 6 | Owner runs `pheromone_qt.argos`: green trails form and fade (two screenshots under `results/real/mvp2/`) | **not met as written** | The main session captured the frames headless (`src/experiments/generated/qt_capture_mvp2.argos`: `length` 240, `autoplay`, `frame_grabbing`). No D-row covers the change of runner. Forming is visible in `qt_t060s.png` and `qt_t210s.png`. Fading is not shown by a before and after of one place (I-1) |
| 7 | D-007 tuning rounds ran into `runs/tuning/`. `tuning_pick.json` exists. pm wrote the freeze D-row | met | 9 complete runs, 3 rounds. `results/real/tuning/tuning_pick.json`. `DECISIONS.md` D-016 |
| 8 | 6 D-010 runs in `runs/judgement/`. `verdict.json` exists. Keep-A D-row by 2026-11-17 | met | 6 complete runs. `results/real/judgement/verdict.json` (`pass` true). `DECISIONS.md` D-017, dated 2026-11-11 |
| 9 | `make_report.py --phase mvp2` writes the stage reports and `results/real/mvp2/index.html` | met, with I-8 | 8 stage pages and `index.html`, all committed. The Qt stage page holds wrong text and a wrong number (I-8) |

## Checks the dispatch asked for

| Check | Status | Evidence |
| --- | --- | --- |
| C++ headers equal `schema.py` | met | `run_logger.cpp:11-15` against `tools/schema.py:40-58`. All three headers of all 16 runs pass `check_runs.py`. Mock and real headers are equal (one mock run diffed against the smoke run) |
| Manifest keys equal `schema.py` | met, one type note | `run_logger.cpp:107-128` against `schema.py:70-80`. Real `wasted_robot_seconds` is written as `0` (JSON integer), the mock writes `0.0` (I-10) |
| Pre-registration committed before the runs | met | `prereg/pheromone_tuning.md` and `prereg/keep_a_judgement.md`: first commit `e6c889b` at 11:13:55. First tuning runid 11:14:16. First judgement runid 11:14:48. Tuning manifests carry `git_commit` `8ac7e2c`, judgement manifests `de08597`. Both descend from `e6c889b`. `git_dirty` false on all 15 |
| Freeze before the judgement | met | D-016 in commit `de08597` at 11:14:46. Judgement runids start 11:14:48 and carry that commit |
| D-007 followed exactly | met | Round 1 (60 s, 0.077) mean 88.00. Round 2 (120 s, 0.077) and round 3 (60 s, 0.05) each change one value from the best round, both from the candidate lists, mean 81.67 each. Pick round 1. 3 rounds. Numbers read from `tuning_pick.json`. `pick_code_sha256` equals the sha256 of `f3d6c73:tools/tuning_pick.py` |
| D-010 followed exactly | met | Arm 1 mean 85.33, arm 2 mean 32.33, threshold 1.2, arm 1 above arm 2 on 104, 105, 106. One judgement, 6 runs, values from `tuning_pick.json`. Arm 2 is `follow_enabled="false"` (`f3d6c73:.../pheromone_forager.cpp:69-71`). `judge_code_sha256` equals the sha256 of `tools/judge_keep_a.py`. `f3d6c73:tools/make_judgement.py:35-36` refuses a second judgement |
| Tuning and judgement seeds never overlap 1 to 10 | met | Manifests: tuning 101 to 103, judgement 104 to 106. `f3d6c73:tools/tuning_rounds.py:21` and `f3d6c73:tools/make_judgement.py:23` fix the seeds. No script takes a seed argument. Only the smoke run uses seed 1, as exit 2 defines |
| Only the intended values differ across runs | met | Across the 16 manifests only `seed`, `half_life_s`, `lambda_dep`, `follow_enabled`, `round` and `arm` differ. `code_sha` is the same pair in all 16 |
| Sources match the libraries that ran | met by timing | Libraries built 11:13:24 to 11:13:26. The `src/` content was committed in `e6c889b` 29 s later. Runs after that commit report `git_dirty` false. The smoke manifest reports `git_dirty` true (I-11) |

## Cross-check of saved logs (all 16 runs)

| Check | Result |
| --- | --- |
| `ticks.csv` 6000 rows, ticks 1 to 6000 | 16 of 16 |
| `robots.csv` 12,000 rows (20 robots x 600 s, ticks 10 to 6000) | 16 of 16 |
| `n_rest` + `n_search` + `n_follow` + `n_end` + `n_return` = 20 on every tick | 16 of 16, 0 bad rows |
| `food_collected` on tick t equals the count of `drop` events up to t | 16 of 16, 0 bad rows |
| `pickup` and `drop` alternate per robot, starting with `pickup` | 16 of 16 |
| Every `drop` has x < -1.0. Every `pickup` lies within 0.25 m of a source centre | 16 of 16 |
| `carrying` = 1 only in state `RETURN`. No `REST` row outside the nest | 16 of 16 |
| `wasted_robot_seconds`, `pher_false_sum`, `false_share` all 0 at d = 0 | 16 of 16 |
| Arm 2 runs have 0 `follow_start` events and 0 FOLLOW ticks | 3 of 3 |
| One layout per seed | 7 seeds, 1 layout each |

## Static acceptance criteria

Line numbers in `src/` and `tools/` are those of `f3d6c73`.

| Task | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| M2-01 | DESIGN §6 files exist. C++17, `find_package(ARGoS)` | met | `src/CMakeLists.txt:17-22` |
| M2-01 | Two targets. Qt user functions guarded by `ARGOS_QTOPENGL_FOUND` | met | `controllers/pheromone_forager/CMakeLists.txt:1`, `loop_functions/pheromone_loop_functions/CMakeLists.txt:13-32` |
| M2-01 | Header declares `SPheromoneReading`, `SDepositRequest`, food struct, getters | met | `pheromone_forager.h:27-50`, `:77-85` |
| M2-01 | Both `.argos`: 10 ticks per second, `length` 600, 5 x 5 x 2 m, 20 `hb_` robots. Headless has no `<visualization>` | met | `pheromone_headless.template.argos:11-13`, `:54`, `:75-76`. `diff` of the two files: seed, `repaint_every`, visualization block only |
| M2-02 | Grid 40 x 40, 0.10 m, two layers, `Evaporate`, `Deposit`, `Probe` | met | `pheromone_grid.h:14-43` |
| M2-02 | Factor from the half-life. 3 x 3 deposit with max-merge | met | `pheromone_grid.cpp:7-10`, `:36-50` |
| M2-02 | 3 sources and 2 decoys drawn, first `n_decoys` used | met, with I-4 | `food_field.cpp:18-47` |
| M2-02 | Source band, radius, 1.5 m decoy gap, source never empties | met | `food_field.h:22-25`, `food_field.cpp:28-31`, `:49-55`. Saved layouts: smallest decoy to source gap 1.50 m |
| M2-02 | No simulator header in either module | met | Both files include standard headers only |
| M2-03 | `PreStep` evaporates, pickup, drop, reading. Ring of 8 at 0.15 m, 45° from the heading | met | `pheromone_loop_functions.cpp:122-163` |
| M2-03 | `PostStep` applies the request into the role layer. No deposit inside the nest | met, with I-7 | `pheromone_loop_functions.cpp:165-175` |
| M2-03 | Nest test `x < -1.0` by position. Ground sensor not read | met | `pheromone_loop_functions.cpp:133`, `pheromone_forager.cpp:96-97`, `:180-183`. No ground sensor in the `.argos` files |
| M2-03 | Floor colors. `SetChanged()` every `repaint_every` ticks in Qt only | met | `pheromone_loop_functions.cpp:19-24`, `:93-107`, `:177-178`. Template value 0 |
| M2-03 | `layout` category seeded with the run seed | met, one note | `pheromone_loop_functions.cpp:58-61`. Runs ran, so the category works on beta59 (I-13) |
| M2-03 | Black cylinder on carrying robots | met | `pheromone_qt_user_functions.cpp:10-15`. Visible in both frames |
| M2-04 | 5 states and LEDs (END_SEARCH magenta, DESIGN Table 2a) | met | `pheromone_forager_states.cpp:13-40` |
| M2-04 | RETURN on pickup in SEARCH, FOLLOW, END_SEARCH, or `t_search` over | met | `pheromone_forager.cpp:147-155` |
| M2-04 | Valid and invalid peaks go to END_SEARCH. Low reading goes to SEARCH | met, with I-5 | `pheromone_forager_states.cpp:84-99` |
| M2-04 | Deposit `A_max · exp(-λ_dep · τ)` while carrying, outside the nest | met | `pheromone_forager_states.cpp:131-138` |
| M2-04 | Table 2 values from `<params>`. One attribute disables FOLLOW | met | `pheromone_forager.cpp:56-71` |
| M2-04 | Getters for state, peak flag, follow-start flag. No layer split, creator or role read | met | `pheromone_forager.h:77-85`. The controller holds no grid or id access |
| M2-05 | 4 files, exact headers, `mock` = 0 | met | `run_logger.cpp:11-15`, `:73`, `:108`. Check passes on 16 runs |
| M2-05 | `ticks.csv` per tick with state counts. `robots.csv` per robot per second with `false_share` | met | `pheromone_loop_functions_log.cpp:43`, `:56-76` |
| M2-05 | Events `pickup`, `drop`, `follow_start`, `peak` | met | `pheromone_loop_functions.cpp:138`, `:143`, `pheromone_loop_functions_log.cpp:77-80` |
| M2-05 | `wasted_robot_seconds` per DESIGN §4.1. `metrics` from the last row. `complete` false if stopped early | met by code read | `pheromone_loop_functions_log.cpp:61-71`, `run_logger.cpp:125-128`. The d > 0 branch and the early-stop branch did not run in M2 |
| M2-05 | `code_version` constant. `CHANGELOG.md` one table with `v1` | met | `pheromone_loop_functions_log.cpp:16`, `f3d6c73:CHANGELOG.md` |
| M2-05 | Manifest copies `git_commit`, `git_dirty`, `code_sha`, all params | met | `run_info_reader.cpp:23-53`. Smoke manifest lists 33 params |
| M2-06 | `--cell --root` writes one `.argos` from the template | met | `tools/make_sweep.py:67-92` |
| M2-06 | Seed, runid, folder, git stamp, sha256[:12] of both libraries. Exit nonzero on a missing library | met | `tools/make_sweep.py:34-47`, `:83-87` |
| M2-07 | Pre-registration has the 4 lines | met | `prereg/pheromone_tuning.md` |
| M2-07 | `make_tuning.py --round k` writes 3 files, seeds 101 to 103. `--run` runs them | met | `tools/make_tuning.py:57-67` |
| M2-07 | Rounds 2 and 3 refuse more than one change or a value outside the candidates | met by code read | `tools/make_tuning.py:36-46`. The refusal never ran |
| M2-07 | `tuning_pick.py` reads saved runs, tie to the earlier round, writes the pick | met | `tools/tuning_rounds.py:49-57`, `tools/tuning_pick.py` |
| M2-07 | One at a time, one core, `timeout 300`. Seeds 1 to 10 refused | met by construction | `tools/run_argos.py:14-27`. No seed argument exists |
| M2-08 | Pre-registration has the 4 lines and is committed before the runs | met | `prereg/keep_a_judgement.md`, commit `e6c889b` |
| M2-08 | 6 files, values from the pick, exit nonzero without the pick | met | `tools/make_judgement.py:32-47` |
| M2-08 | Judge reads saved runs. Pass rule as D-010 | met | `tools/judge_keep_a.py:38-41` |
| M2-08 | `verdict.json` fields | met | Per-seed values, both means, `pass`, `criterion_file`, `judge_code_sha256` all present |
| M2-09 | README sections and commands with folders and roots. Arm-2 attribute named | met | `f3d6c73:README.md` sections 1 to 6, the arm-2 line in section 6 |
| M2-10 | 8 stage reports, 8 fields, figure, table, from saved outputs | met, with I-8 | `results/real/mvp2/*.html`, `*_fig.png` |
| M2-10 | `index.html` links the reports, `tuning_pick.json`, `verdict.json` | met | `results/real/mvp2/index.html` "Other files" |

## State machine against DESIGN §3.2 (code read at `f3d6c73`)

| Item | Status | Where |
| --- | --- | --- |
| Evaporation: factor 0.5^(1 / (half-life x ticks per second)), once per tick, both layers | correct | `pheromone_grid.cpp:7-10`, `:23-28`, `pheromone_loop_functions.cpp:160` |
| Deposit: 3 x 3 cells, max-merge, layer by id prefix, robot position outside the nest | correct. Footprint reaches one cell row inside the nest (I-7) | `pheromone_grid.cpp:36-50`, `pheromone_loop_functions.cpp:172-174` |
| Probe: centre plus 8 points, counter-clockwise from the heading. The controller steers to index x 45° | correct, the two sides agree | `pheromone_loop_functions.cpp:149-155`, `pheromone_forager_states.cpp:101` |
| Nest test: `x < edge` in the loop functions and in the controller, same value in both `.argos` blocks | correct | `pheromone_loop_functions.cpp:133`, `pheromone_forager.cpp:180-183` |
| Pickup and drop: honest only, `else if` so one per tick, source never empties | correct. Confirmed by the log cross-check | `pheromone_loop_functions.cpp:131-145` |
| Wasted time: FOLLOW with `false_share` ≥ 0.5, or END_SEARCH within 0.5 m of an active decoy. Integer ticks, divided once | correct by read. Not exercised at d = 0 | `pheromone_loop_functions_log.cpp:56-71`, `:84` |
| FOLLOW entry: best probe > `θ_on` and > `here` + `δ_up` | correct | `pheromone_forager_states.cpp:57-68` |
| Peak: flat for `t_peak` goes to END_SEARCH. Low for `t_peak` goes to SEARCH | correct | `pheromone_forager_states.cpp:79-99` |
| Valid peak: `t_follow_min` and `here` ≥ 2 x `here_entry` | matches the DESIGN text. The rise test is empty when `here_entry` is 0 (I-5) | `pheromone_forager_states.cpp:93-94` |
| RETURN: drive to the nest centre | differs. The robot rests when it crosses the nest edge (I-6) | `pheromone_forager_states.cpp:119-127` |

## MVP ladder checks

| Check | Status | Evidence |
| --- | --- | --- |
| L1 schema is the single contract | PASS, notes | Mock and real were diffed: equal CSV headers, equal manifest key set apart from the open `params` set. `check_runs.py` unchanged. `schema.py` changed only by the M1 fix. Notes in I-10 |
| L2 no pipeline before the flow ran on mocks | PASS | The real slice fills the flow the mock demonstrated (run folder, check, analyze). The tuning and judgement scripts read manifests only. They are decision tools of D-007 and D-010, not a new stage of the flow. They had no mock run. Recorded here, not raised |
| L3 mock is unmistakable and isolated | PASS | `grep -i mock src/`: only the header column and the constants `0` and `false`. No real-path tool reads `mock/`. Real output is under `results/real/`. The mock chart stamp is readable now (`results/mock/g2_recovered_share_MOCK.png`, viewed) |
| L4 a phase opens only when the previous exit is closed | ISSUE | M1 side: closed in substance (stamp readable, `results/reviews/M1_evidence/breakage2_mixed_mock.txt` exit 1, PLAN and DESIGN lines match D-014, D-015 logged). No second review artifact exists (I-3). M3 side: M3 was built, tuned, frozen (D-018) and its sweep started while this gate was open, with no D-row for the early start (I-2) |

## Hierarchy checks

| Check | Status | Evidence |
| --- | --- | --- |
| H1 trace | PASS, stale lines | Mission block in `PLAN.md:7-17` and `DESIGN.md:7-17`. Every M2 task tags `→ M2`. Counters within bounds. Stale lines in I-3 |
| H2 decisions logged | ISSUE | D-016 and D-017 exist with saved-file evidence and were written before dependent work. Root `CLAUDE.md:21-22` supports D-013 and the delegation. Two choices have no row: the change of runner for exit 6 (I-1) and the early start of M3 (I-2) |

## Issues

| ID | Severity | Class and route | Where | What | Fix suggestion |
| --- | --- | --- | --- | --- | --- |
| I-1 | blocking | hierarchy (H2) and exit 6. `product-manager` writes, main session captures | `PLAN.md:102`, `PLAN.md:224`, `results/real/mvp2/qt_t060s.png`, `qt_t210s.png` | Exit 6 names the owner as runner. The main session captured the frames headless. No D-row logs that choice. The two frames show a trail forming and widening. Neither shows a painted place turning pale again | Log a D-row for the headless capture (runner, why, rejected: owner run). Rewrite exit 6 to match it. Add evidence of fading: a third frame of a place whose trail went stale, or a plot of one cell from saved logs. Loosening an exit criterion is the owner's line (`rules/core.md`), so the row must cite the delegation in root `CLAUDE.md:22` |
| I-2 | blocking | ladder (L4), `system-architect` answers, `product-manager` logs | commits `b3f32b3`, `5884cf4`, `DECISIONS.md` D-018, `runs/defense_tuning/`, `runs/sweep/` (40 folders at 11:27) | M3 opened before the M2 gate closed. Same shape as M1 I-4, but further: defense tuning ran and froze, and the G1 sweep is running. No D-row logs the early start. `tools/tuning_pick.py` also changed, so `pick_code_sha256` in `tuning_pick.json` matches only the `f3d6c73` version | Log a D-row as D-015 did. Architect states which M3 results stand if I-4, I-5 or I-6 change the code (see those rows). Do not regenerate `tuning_pick.json` with the changed script |
| I-3 | minor | hierarchy (H1), `product-manager`. DESIGN lines to `system-architect` | `PLAN.md:152`, `PLAN.md:159`, `PLAN.md:15`, `DESIGN.md:16-17`, `DESIGN.md:340`, `results/reviews/M1_gate.md:5` | M2-07 and M2-08 are still `[ ]` although their gate ran. The M1 line reads `cycle 0/2` after one review and a fix round. DESIGN Constraints and Table 5 predate D-013. `M1_gate.md` still reads ISSUE and no second review artifact exists | Tick the two tasks. Set the M1 and M2 cycle counters. Align the DESIGN lines with D-013. Append a closing note to `M1_gate.md` that names the evidence files |
| I-4 | minor for M2. Affects the M3 runs now in progress | reasoning, `system-architect` | `food_field.cpp:21-40` | No gap is required between the two decoys. In the 7 saved layouts (seeds 1, 101 to 106) the decoy centres are 0.07 to 0.53 m apart, with radius 0.25 m. So d = 2 and d = 4 may use what is in effect one decoy. D-009 rejected "1 shared decoy" for that reason. The D-018 freeze and the running sweep use this layout code | Check decoy distances in the sweep manifests for seeds 1 to 10 first. If they also coincide, decide by D-row: add a decoy to decoy gap (then re-run defense tuning and the sweep), or keep it and state in the report that d = 2 and d = 4 use one decoy spot. Sources are drawn first, so d = 0 results stay valid either way |
| I-5 | minor for M2. Affects M3-02 suspects | reasoning, `system-architect` | `pheromone_forager_states.cpp:62`, `:93-94`, `DESIGN.md:134` | `here >= 2 * here_entry` is always true when the robot enters FOLLOW from a blank cell (`here_entry` = 0). Entry from beside a 0.30 m trail may be the common case. Then validity is `t_follow_min` only, and R5 false suspects are not held back as DESIGN intends | Measure the share of `here_entry` = 0 at `follow_start`, and the R5 false-positive count, from saved runs. If it is high, define the reference so it cannot be 0 (for example the best probe at entry), by D-row |
| I-6 | minor | implementation, `developer`. DESIGN wording to `system-architect` | `pheromone_forager_states.cpp:119-127`, `DESIGN.md:139` | A robot rests the moment it is inside the nest edge. Mean x of resting robots after tick 1000 is -1.01 to -1.03 with following on. Resting robots line up on the nest border, in the path of returning robots. DESIGN says "drive to nest centre" | Keep driving for a set depth after the drop, or state in DESIGN that resting at the edge is intended. A code change here alters food counts in every cell, so decide before more sweep time is spent |
| I-7 | minor | implementation note, `developer` | `pheromone_grid.cpp:41-49`, `pheromone_loop_functions.cpp:172` | The nest guard tests the robot position. The 3 x 3 footprint still writes one cell row (0.10 m) inside the nest | Skip cells whose centre is inside the nest, or note it under R4 |
| I-8 | minor | implementation, `developer` | `tools/report_mvp2.py:168-177`, `results/real/mvp2/qt_view.html` | The Qt page says the owner ran a live Qt run. Its table lists 6677 KB for each frame. The saved PNGs are 48 KB and 49 KB, 900 x 674 px. The page was built before the frames were replaced | State the real method (headless capture, `length` 240). Re-run `make_report.py --phase mvp2` after I-1 so the numbers are read from the final files |
| I-9 | minor | hierarchy (evidence), main session | exit 1, `results/real/mvp2/build.html` | The build is shown by library files only. The `make` output is not saved | Save the `make` output with its exit code under `results/real/` at each build |
| I-10 | minor | ladder note (L1), `system-architect` | `tools/schema.py:65`, `DESIGN.md:160-163`, `f3d6c73:tools/make_tuning.py:62`, `tools/judge_keep_a.py:26`, `f3d6c73:tools/run_results.py:21-22`, `run_logger.cpp:17-22` | `WAIT_DECOY` is in `schema.py` but not in DESIGN. The manifest param keys `round`, `arm` and the two tuned keys are read by tools but named outside `schema.py`. Real manifests write `wasted_robot_seconds` as `0`, the mock as `0.0` | Name `WAIT_DECOY` in DESIGN §3.3. Move the param key names into `schema.py`. Leave the number format unless a reader needs the type |
| I-11 | minor | implementation note, main session | `runs/smoke/20261111-111329_d0_def0_s1/manifest.json` | The smoke run has `git_dirty` true and `git_commit` `ee4de02`. It ran 26 s before the commit that holds its code. Its `code_sha` equals the later runs | Commit before a gate smoke run. No re-run is needed for M2 |
| I-12 | minor | reasoning note, `data-analyst` | `prereg/pheromone_tuning.md`, `prereg/keep_a_judgement.md` | Neither threshold comes from a noise estimate (`rules/measurement.md` §1). Both files say so. Round 1 seeds span 80 to 98 while rounds differ by 6.33 in the mean | No change to the M2 verdicts. The final report states this limit for both tuning steps |
| I-13 | low | reasoning note, `system-architect` | `pheromone_loop_functions.cpp:58` | The `layout` category uses the same seed as the `argos` category. Whether its stream then equals the first `argos` generator was not verified | Confirm in the ARGoS source that the streams differ, or seed with a fixed offset. Decide with I-4, since both change the layout |
| I-14 | low | implementation note, `developer` | `pheromone_loop_functions.cpp:77-82` | `Reset()` clears the grid and counters but not the logger. A GUI reset with a `<logger>` node would append to the same files | Close and reopen the logger in `Reset()`, or refuse `<logger>` together with a visualization |
| I-15 | low | not checked | `results/real/mvp2/*.html` | No browser render in this review (outside the allowed runs). Text and figures were read from the files | Main session renders `index.html` once per `rules/answering.md` §3 |

## To close the gate

1. pm logs the two D-rows (I-1 runner change, I-2 early M3 start). Architect answers I-2.
2. Main session adds the fading evidence for exit 6 (I-1). Developer fixes the Qt page text (I-8). Main session re-runs `make_report.py --phase mvp2`.
3. pm ticks M2-07 and M2-08 and sets the counters (I-3).
4. Architect decides I-4, I-5 and I-6 now. They do not block M2, but each can force a re-run of M3 runs.
5. Second gate review (cycle 2 of 2) reads the new D-rows, the fading evidence and the rebuilt Qt page.
