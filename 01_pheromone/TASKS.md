> Split from `PLAN.md` (rules/docs.md §1). The PLAN.md stub is the truth if
> the two disagree; update both in the same edit.

# Tasks: 01_pheromone

Mission block, task format and fixed paths: [PLAN.md](./PLAN.md).

## M1: MVP1 shape (mock end-to-end, by 2026-11-13)

### M1 exit (runnable, runner: main session under D-012)

1. `tools/make_mock_runs.py` writes 80 run folders under `mock/runs/`. Every runid starts `MOCK_`.
2. `tools/check_runs.py mock/runs` exits 0.
3. `tools/analyze.py mock/runs` writes `results/mock/g2_recovered_share_MOCK.png` and `results/mock/summary.csv`.
4. Breakage 1: a scratchpad copy of one run with one `ticks.csv` column renamed makes `check_runs.py` exit nonzero and name the column.
5. Breakage 2: a scratchpad root with one `"mock": true` and one `"mock": false` manifest makes `analyze.py` exit nonzero.
6. `tools/make_report.py --phase mvp1` writes 3 stage reports and `results/mock/mvp1/index.html`.
- Form for each run: `OMP_NUM_THREADS=1 timeout 300 uv run python ...` (D-012).

### Tactic: schema first, mock fills it (kill: a column the mock cannot fill without changing DESIGN §4)

- [x] M1-01 → M1: Python project files and `.gitignore`
  - Static: `01_pheromone/pyproject.toml` per `rules/development/python.md`: `[tool.uv] python-downloads = "never"`, dependencies numpy and matplotlib only.
  - Static: `.gitignore` ignores `01_pheromone/runs/`, `01_pheromone/src/experiments/generated/` and `01_pheromone/mock/runs/` (D-014). `prereg/` and `results/` are not ignored.
  - Gate: main session runs `uv sync` once before M1 exit 1.
- [x] M1-02 → M1: `tools/schema.py` and `tools/check_runs.py` (U1)
  - Static: `schema.py` defines `SCHEMA_VERSION = 1` and the column lists of DESIGN Table 3 and Table 4, in that order.
  - Static: `schema.py` lists the 7 event names of Table 4 and the `manifest.json` keys of DESIGN §4.
  - Static: `check_runs.py <root>` checks per run: 4 files present, exact headers, `ticks.csv` 6000 rows when `complete` is true, `mock` column constant and equal to manifest `mock`.
  - Static: it checks `metrics` equals the last `ticks.csv` row, and runid matches `<YYYYMMDD-HHMMSS>_d<k>_def<0|1>_s<seed>` with prefix `MOCK_` exactly when `mock` is true.
  - Static: it exits nonzero on any failure and prints run, file and column. Column names live only in `schema.py` (grep: no column literal in `check_runs.py`).
  - Gate: M1 exit 2 and 4.
- [x] M1-03 → M1: `tools/make_mock_runs.py` (U2)
  - Static: writes only under `mock/runs/`. A different output path makes it exit nonzero before writing.
  - Static: 80 runs = d in 0, 1, 2, 4 x defense 0, 1 x seeds 1 to 10. Runid prefix `MOCK_`. `mock` = 1 in `ticks.csv`, `"mock": true` in the manifest.
  - Static: imports columns from `schema.py`. Fixed generator seed, so two runs give identical files.
  - Static: `robots.csv` has one row per robot per second, with 20 + d robots (D-005).
  - Static: `wasted_robot_seconds` is 0 in every d = 0 run (DESIGN §4.1). Mock means show a loss at d > 0 and a partial gain with defense on, so the chart is not empty.
  - Gate: M1 exit 1 and 2.
- [x] M1-04 → M1: `tools/analyze.py` (U3, DESIGN §4.2)
  - Static: computes `F(d, def)`, `L(d)`, `G(d)`, `R(d)` as ratio of means. Bootstrap: 10,000 resamples of the seed index, paired across cells, 95 % percentile.
  - Static: writes "loss not resolved at d" and skips `R(d)` when the `L(d)` interval contains 0. Reports `F(0, on) - F(0, off)` as defense cost.
  - Static: cell check lists missing cells and duplicates (keeps the latest complete run). Missing cells do not stop the script.
  - Static: mixing guard stops on mixed `mock` values. Mock output goes to `results/mock/`, real to `results/real/`.
  - Static: a mock chart has "MOCK DATA" in its title and a `_MOCK.png` file name. `summary.csv` has one row per run.
  - Gate: M1 exit 3 and 5.
- [x] M1-05 → M1: `tools/make_report.py` (stage reports and summary page)
  - Static: `--phase mvp1` reads saved outputs only (manifests, CSVs, check and analyze logs). No number is typed into the script.
  - Static: one report per stage (generate, check, analyze) with the 8 fields of `.claude/CLAUDE.md` "System build phasing", one figure and one table.
  - Static: `index.html` links every report and uses `skills/html-theme/theme.css`.
  - Static: a stage with no saved output is reported as skipped with the reason, and the script continues.
  - Gate: M1 exit 6.

## M2: MVP2 real slice, 0 detractors (by 2026-11-17)

### M2 exit (runnable)

1. Main session builds `src/` (cmake, make) with no error.
2. Main session smoke: `make_sweep.py --cell 0,0,1 --root runs/smoke` writes one `.argos`. One headless run writes `runs/smoke/<runid>/`.
3. `check_runs.py runs/smoke` exits 0 with `check_runs.py` and `schema.py` unchanged since M1.
4. That run has `food_collected` > 0, and `events.csv` has `pickup` and `drop` rows.
5. `analyze.py runs/smoke` lists 79 missing cells and exits 0.
6. Main session grabs Qt frames headless with `src/experiments/generated/qt_capture_mvp2.argos` (D-022): green trails form (two frames, saved under `results/real/mvp2/`). Fading is shown in M3 (M3 exit 5, M3-06).
7. Main session ran the D-007 tuning rounds into `runs/tuning/`. `tuning_pick.json` exists. pm wrote the freeze D-row.
8. Main session ran the 6 D-010 runs into `runs/judgement/`. `verdict.json` exists. pm wrote the keep-A or switch-B D-row by 2026-11-17.
9. `make_report.py --phase mvp2` writes the stage reports and `results/real/mvp2/index.html`.
- If exit 8 says switch to B: pm rewrites the M3 tasks for B before M3 opens.
- A schema change needed by real code sends that slice back to M1 (DESIGN §5).

### Tactic: copy hw5, then make two stages real (kill: build fails on hw5 tags after 2 fix cycles)

- [x] M2-01 → M2: `src/` skeleton and the controller interface (U4)
  - Static: files of DESIGN §6 `src/` exist. Top `CMakeLists.txt` copies hw5 (C++17, `find_package(ARGoS)`).
  - Static: targets `pheromone_forager` (controller) and `pheromone_loop_functions`. Qt user functions guarded by `ARGOS_QTOPENGL_FOUND`.
  - Static: the controller header declares `SPheromoneReading { here, probe[8] }`, `SDepositRequest { active, amount }`, a food struct as hw5 `SFoodData`, and getters for state and carrying.
  - Static: both `.argos` files set `ticks_per_second` 10, `length` 600, 5 x 5 x 2 m arena, 20 `hb_` robots.
  - Static: `pheromone_headless.template.argos` has no `<visualization>`. `pheromone_qt.argos` has one.
  - Gate: M2 exit 1.
- [x] M2-02 → M2: pure modules `pheromone_grid` and `food_field` (U5, part 1)
  - Static: grid 40 x 40, cell 0.10 m, two layers (true, false). Functions `Evaporate`, `Deposit`, `Probe`.
  - Static: evaporation factor is computed from the half-life parameter (60 s start, D-007). Deposit writes 3 x 3 cells with max-merge.
  - Static: `food_field` draws 3 sources and 2 decoys, then uses the first `n_decoys` (D-009).
  - Static: sources in x 0.5 to 1.7 m, radius 0.25 m. Each decoy at least 1.5 m from every source. Pickup inside a source never empties it.
  - Static: neither module includes a simulator header (grep `argos3/core/simulator` returns nothing in both).
- [x] M2-03 → M2: loop functions, virtual sensor, floor paint, Qt drawing (U5, part 2)
  - Static: `PreStep` evaporates, handles pickup and drop, writes `SPheromoneReading` per robot. Probe ring 8 points, 0.15 m, 45° steps from the heading.
  - Static: `PostStep` applies `SDepositRequest` into the layer of the robot's role (`hb_` true, `dt_` false). No deposit inside the nest.
  - Static: nest test is `x < -1.0` by position (D-008). The ground sensor is not read for nest or pheromone.
  - Static: `GetFloorColor` paints nest grey, sources black, true layer pale green (200, 255, 200), false layer pale red (255, 200, 200). `SetChanged()` every `repaint_every` ticks in Qt only.
  - Static: the `layout` stream uses `CRandom::CreateCategory` seeded with the run seed, passed to `food_field`.
  - Static: `pheromone_qt_user_functions` draws a black cylinder on carrying robots, as hw5 `search_deliver_qt_user_functions.cpp`.
  - Gate: M2 exit 1 and 2 (the `layout` category builds and runs).
- [x] M2-04 → M2: honest controller (U6, DESIGN §3.2 as corrected)
  - Static: states REST, SEARCH, FOLLOW, END_SEARCH, RETURN. LEDs: REST off, SEARCH green, FOLLOW yellow, RETURN blue. END_SEARCH LED: open item below.
  - Static: transitions to RETURN on pickup in SEARCH, FOLLOW or END_SEARCH, or on `t_search` over.
  - Static: valid and invalid peaks both go to END_SEARCH. Only a valid peak may add a suspect (M3). A low-reading peak goes to SEARCH.
  - Static: deposit `A_max · exp(-λ_dep · τ)` while carrying, outside the nest. `λ_dep` start 0.077 (D-007).
  - Static: all Table 2 values are read from `<params>`. One named attribute disables FOLLOW entry (`θ_on` = ∞) for the D-010 arm 2.
  - Static: the controller exposes its state, a peak flag (valid or invalid) and a follow-start flag through getters. It never reads layer split, creator or role of others.
- [x] M2-05 → M2: `RunLogger` and `CHANGELOG.md` (U7)
  - Static: writes `manifest.json`, `ticks.csv`, `robots.csv`, `events.csv` with the exact headers of `schema.py`. `mock` = 0.
  - Static: `ticks.csv` one row per tick with `n_rest` to `n_return` from controller states. `robots.csv` one row per robot per second with `false_share` from ground truth.
  - Static: events `pickup`, `drop`, `follow_start`, `peak` are logged from the controller getters.
  - Static: `wasted_robot_seconds` follows DESIGN §4.1. `metrics` copied from the last tick row. `complete` false if stopped early.
  - Static: `code_version` constant in the loop functions. `CHANGELOG.md` is one table (`rules/measurement.md` §2.2) with a `v1` row.
  - Static: manifest copies `git_commit`, `git_dirty`, `code_sha` and all params from the `.argos` attributes.
  - Gate: M2 exit 3 and 4.
- [x] M2-06 → M2: `tools/make_sweep.py`, single-cell mode (U8)
  - Static: `--cell d,def,seed --root <runs root>` writes one `.argos` into `src/experiments/generated/` from the headless template.
  - Static: sets the run seed, runid, output folder `<root>/<runid>/`, `git_commit`, `git_dirty`, and sha256[:12] of both built libraries.
  - Static: exits nonzero if a built library is missing (no stale hash).
  - Gate: M2 exit 2.
- [x] M2-07 → M2: pheromone tuning scripts (D-007)
  - Static: `prereg/pheromone_tuning.md` restates D-007 in the 4 lines of `rules/measurement.md` §1 (metric, threshold, contrast, failure condition).
  - Static: `tools/make_tuning.py --round k` writes 3 `.argos` files (d = 0, defense off, seeds 101 to 103) into `src/experiments/generated/`. With `--run` it runs them into `runs/tuning/` (D-013).
  - Static: round 1 uses start values. Rounds 2 and 3 refuse more than one change from the previous best, or a value outside the D-007 candidates.
  - Static: `tools/tuning_pick.py` reads saved runs only, prints mean `food_collected` per round, picks by D-007 (tie to the earlier round), writes `tuning_pick.json`.
  - Static: runs go one at a time, one core, `timeout 300` each (`tools/run_argos.py`). Seeds 1 to 10 are refused.
  - Gate: M2 exit 7 (main session runs, D-013).
- [x] M2-08 → M2: keep-A judgement scripts, seeds 104 to 106 (D-010)
  - Static: `prereg/keep_a_judgement.md` restates D-010 in the 4 lines of `rules/measurement.md` §1. It is committed before the runs.
  - Static: `tools/make_judgement.py` writes 6 `.argos` files (arm 1 and arm 2 x seeds 104 to 106) with values from `tuning_pick.json`. With `--run` it runs them into `runs/judgement/`. It exits nonzero if `tuning_pick.json` is missing.
  - Static: `tools/judge_keep_a.py` reads saved runs only. Pass = arm 1 mean ≥ 1.2 x arm 2 mean AND arm 1 > arm 2 on all 3 seeds.
  - Static: `verdict.json` holds per-seed values, both means, pass, the criterion file path and the sha256 of `judge_keep_a.py` (`rules/measurement.md` §4.1).
  - Gate: M2 exit 8 (main session runs, D-013).
- [x] M2-09 → M2: `README.md` how to build and run
  - Static: sections: build (cmake, make), Qt demo run, headless smoke run, tools (`check_runs.py`, `analyze.py`, `make_mock_runs.py`, `make_report.py`), tuning and judgement scripts.
  - Static: every command names its folder and its runs root (Fixed paths table). The arm-2 attribute (M2-04) is named.
- [x] M2-10 → M2: `make_report.py --phase mvp2`
  - Static: reports for build, generate, run, check, analyze, Qt view, tuning, judgement. Each with 8 fields, one figure, one table, from saved outputs.
  - Static: `results/real/mvp2/index.html` links them, `tuning_pick.json` and `verdict.json`.
  - Gate: M2 exit 9.

## M3: MVP3 detractors, defense, sweep (sweep by 2026-11-24, report by 2026-11-28)

### M3 exit (runnable)

1. Main session smoke: one run at d = 2, defense on, seed 1 into `runs/smoke/` passes `check_runs.py`. Its `events.csv` has `decoy_reach` and `suspect_add` rows.
2. Main session ran the D-011 defense tuning into `runs/defense_tuning/` (D-013). `defense_pick.json` exists. pm wrote the freeze D-row before the sweep.
3. Main session ran `tools/make_sweep.py --sweep --run` (D-013). `check_runs.py runs/sweep` exits 0 on 80 complete runs (G1, by 2026-11-24).
4. `analyze.py runs/sweep` writes `results/real/g2_recovered_share.png` with 95 % error bars for d = 1, 2, 4, or the "loss not resolved" line (G2, by 2026-11-28).
5. Main session captures the Qt demo frames headless (D-022) at d = 2, defense off and on. Frames at later times show a painted trail turning pale again (M2 exit 6 fade part, D-022).
6. `make_report.py --phase mvp3` writes the stage reports and `results/index.html`.

### Tactic: attack, then defense, then freeze and sweep (kill: D-010 fails, then pm rewrites M3 for B)

- [x] M3-01 → M3: detractor controller (U9, DESIGN §3.3)
  - Static: states REST, GO_DECOY, wait 2 s, RETURN_LAY. LED red. Never carries food. Same `t_rest`.
  - Static: decoy assigned by the loop functions at `Init` (D-009 counts). Deposits go to the false layer.
  - Static: `decoy_reach` event is logged. Detractors are added to 20 honest robots (D-005).
- [x] M3-02 → M3: defense rule (U10, DESIGN §3.4)
  - Static: rules 1 to 5 run only when the defense param is 1. Only a valid peak with no food adds a suspect.
  - Static: merge within `r_merge`, memory `n_mem`, ignore within `r_suspect`, cone `±α_cone` within `d_cone`.
  - Static: `suspect_add` and `cone_abort` events logged. `suspects_total` filled in `ticks.csv`.
  - Gate: M3 exit 1.
- [x] M3-03 → M3: defense tuning scripts (D-011)
  - Static: `make_tuning.py --defense --round k` writes d = 2, defense on, seeds 101 to 103 into `runs/defense_tuning/`, with values from `tuning_pick.json`.
  - Static: candidate values for `r_suspect`, `α_cone`, `d_cone`, `t_end` are read from `prereg/defense_candidates.json`. The script exits nonzero if that file has no git commit.
  - Static: rounds 2 and 3 refuse more than one change. `tuning_pick.py --defense` picks by mean `F(2, on)`, tie to the earlier round, writes `defense_pick.json`.
  - Gate: M3 exit 2 (main session runs, D-013).
- [x] M3-04 → M3: 80-run sweep script (U11). Gate met on v3: 80 of 80, check 0 failed (`results/real/check_sweep_log.txt`, D-025)
  - Static: `tools/make_sweep.py --sweep` writes one `.argos` file per cell not yet done (d 0, 1, 2, 4 x defense 0, 1 x seeds 1 to 10), each with output folder under `runs/sweep/` (D-013).
  - Static: it exits nonzero unless `tuning_pick.json` and `defense_pick.json` exist. All 80 files carry the same frozen values.
  - Static: `tools/make_sweep.py --sweep --run` runs them one at a time, one core, `timeout 300` each. It skips a cell only if a manifest is complete AND has the same cell, params and code (same `git_commit`, or no `src/` change since it).
  - Static: README gets a sweep section (README §8).
  - Gate: M3 exit 3.
- [x] M3-05 → M3: analysis and figures from real logs (U12, part 1)
  - Static: `analyze.py runs/sweep` writes `results/real/g2_recovered_share.png`, a food bar chart and a wasted robot-seconds bar chart per cell, and `summary.csv`.
  - Static: the report table states the crowding note (R10), the decoy-count note (D-009) and the pairing limit (R11).
  - Static: counts of `suspect_add` and `cone_abort` per cell are tabled.
  - Gate: M3 exit 4.
- [x] M3-06 → M3: demo `.argos` files (U12, part 2). Gate met: frames under `results/real/mvp3/demo/` (d2 def0 and def1)
  - Static: `pheromone_qt_d2_def0.argos` and `pheromone_qt_d2_def1.argos` with the frozen values (`tools/make_demo.py`). README demo section (README §9).
  - Gate: at least two frames of one place, earlier and later, show a trail forming and then fading (D-022). Saved under `results/real/mvp3/`.
  - Gate: M3 exit 5.
- [x] M3-07 → M3: `make_report.py --phase mvp3` and the results page
  - Static: reports for detractor smoke, defense tuning, sweep, check, analyze, demo. Each with 8 fields, one figure, one table.
  - Static: `results/index.html` opens with G1 (logged runs out of 80) and G2 (`R(d)` with intervals), read from `summary.csv`.
  - Static: it links the G2 chart, all stage reports, the demo, and the M1 and M2 pages. `results/README.md` lists every file in `results/`.
  - Gate: M3 exit 6.
- [ ] M3-08 → M3: M3 gate review (reviewer)
  - Gate: reviewer checks M3 exit 1 to 6 against saved files and writes `results/reviews/M3_gate.md` with PASS or ISSUE.
  - Gate: the review re-checks the schema contract after the early M3 start (D-023): `schema.py` and `check_runs.py` match the M1 versions plus logged changes.
  - Gate: the review states whether the M2 ISSUE fixes (D-020 to D-025) close `results/reviews/M2_gate.md` I-1 and I-2.

## M4: defense v2 lockout (by 2026-11-21, D-027 to D-033)

Spec: `decisions/2026-11-11_fable_defense_v2.md` "Defense v2 spec". It does not block M2 or M3 (D-032). Result: FAIL under its prereg (D-033).

### M4 exit (runnable, runner: main session, D-031)

1. Invariance: code v4 with `t_lock` = 0 gives the saved v3 `food_collected` for `d2_def1_s1` and `d0_def0_s1` (`CHANGELOG.md` v4). Met (STATUS 2026-11-11, 8 of 8 cells).
2. `results/real/tuning_v2/pick.json` exists. pm wrote the freeze D-row before confirmation. Met (pick file exists; no separate freeze D-row, D-033 cites it).
3. `check_runs.py` exits 0 on `runs/sweep_v2/` and `runs/sweep_v2_lock0/`, 160 complete runs each. Met (`results/real/check_sweep_v2.txt`, `results/real/check_sweep_v2_lock0.txt`).
4. `results/real/v2/verdict.json` exists, pass or fail, by 2026-11-21. Met: FAIL (D-033).
5. The final report has the defense v2 section (M4-06). Open.

### Tactic: one lockout arm, pre-registered, new seeds (kill: tuning picks `t_lock` 0, then stop without confirmation. Seeds 11-30 are used once. 2 gate cycles, end 2026-11-21)

- [x] M4-01 → M4: code v4 and tools (developer)
  - Static: after `cone_abort`, `TryEnterFollow()` returns false for `t_lock` s, read from `<defense t_lock>`, default 0 (D-028).
  - Static: `CHANGELOG.md` has a v4 row. `code_version` is `v4`. `t_lock` is in manifest params. No new event, no new column (grep `schema.py`: unchanged since v3).
  - Static: the seed range is a CLI option (D-030). The tuning tool refuses seeds 11 to 30 (D-029).
  - Static: `prereg/defense_v2_lockout.md` restates spec items 5 to 12 in the 4 lines of `rules/measurement.md` §1 (metric, threshold, contrast, failure).
  - Static: the run tools write only to the M4 roots of the Fixed paths table (D-030). The tuning and confirmation tools exit nonzero if `prereg/defense_v2_lockout.md` has no git commit. The invariance rerun (M4-03) is exempt.
- [x] M4-02 → M4: defense diagnostics CSV (`tools/defense_diagnostics.py`, `results/real/defense_diagnostics.csv`)
  - Static: a tool reads saved `runs/sweep` logs only and writes `results/real/defense_diagnostics.csv`.
  - Static: one row per d in 1, 2, 4, defense on, mean per run. Columns: abort-to-next-`follow_start` gap, share of gaps ≤ 5 s, false-trail FOLLOW time before and after learning that decoy, `cone_abort` on and off false trail.
  - Static: one extra row: at d = 0, defense on, `suspect_add` per run and the count within 1.0 m of a real source.
  - Static: one row per cell (d in 0, 1, 2, 4 x defense 0, 1): mean seconds per run in each controller state, and false-trail FOLLOW seconds.
  - Static: no number is typed into the tool.
  - Gate: main session runs it once. The CSV exists with the rows above.
- [x] M4-03 → M4: invariance with `t_lock` 0 (STATUS 2026-11-11: 8 of 8 cells equal v3 seed 1)
  - Gate: main session reruns `d2_def1_s1` and `d0_def0_s1` on v4, `t_lock` = 0. `food_collected` equals the saved v3 value in `runs/sweep`. M4 exit 1.
  - A mismatch stops M4-04 and goes to `recover`.
- [x] M4-04 → M4: tuning, seeds 107-116 (`results/real/tuning_v2/pick.json`: `t_lock` 10 s)
  - Gate: `prereg/defense_v2_lockout.md` has a git commit before the first run (D-029).
  - Gate: cells (d = 2, on) and (d = 0, on) x `t_lock` 0, 5, 10, 20 s x seeds 107 to 116 = 80 runs, other values at D-018.
  - Gate: the pick tool reads saved runs only. Metric: seed mean of food(d=2,on) + food(d=0,on). Highest wins. Tie goes to the smaller `t_lock`. It writes `results/real/tuning_v2/pick.json`. M4 exit 2.
  - Pick = 0: stop. No confirmation run (Tactic kill).
- [x] M4-05 → M4: confirmation seeds 11-30 and judge (`results/real/v2/verdict.json`: FAIL, D-033)
  - Gate: 8 cells x seeds 11 to 30 into `runs/sweep_v2/` (picked `t_lock`) and `runs/sweep_v2_lock0/` (`t_lock` = 0). 160 runs each, same v4 code. M4 exit 3.
  - Static: the judge reads saved runs only. Metric: G(2) = F(2,on) − F(2,off), seeds 11-30, paired bootstrap 10,000, 95 % interval.
  - Static: pass = G(2) interval lower bound > 0. Fail = G(2) interval includes 0, or the d=0 cost interval upper bound < 0.
  - Static: attribution (picked `t_lock` vs 0) is reported with its interval. d = 1, 4 are reported only.
  - Static: `verdict.json` holds per-seed values, intervals, pass, the prereg path and the sha256 of the judge script (`rules/measurement.md` §4.1). M4 exit 4.
- [ ] M4-06 → M4: final report section
  - Static: the headline stays v3 (D-026). The section text uses "not met with v3" for the Vision line.
  - Static: the defense v2 section is marked "post-hoc design, confirmed on new seeds". Pass or fail uses the same format.
  - Static: two figures: time per state, and the abort-to-refollow gap, from `defense_diagnostics.csv`.
  - Static: limits table: wrong suspects at d = 0, crowding (R10), decoy count (D-009), pairing limit (R11).
  - Static: every number in the section is read from a saved file (`g2_stats.csv`, `defense_diagnostics.csv`, `results/real/v2/verdict.json`).
  - Static: the section links the root-cause memo `results/real/failure_analysis.md`.
  - Gate: M4 exit 5. M8-02 may carry this section into the final report.
- [ ] M4-07 → M4: M4 gate review (reviewer)
  - Gate: reviewer checks M4 exit 1 to 5 and writes `results/reviews/M4_gate.md` with PASS or ISSUE.

## M5: T-A, defense v5 confirm-twice x lockout (by 2026-11-17, D-039, D-043, → RQ1, G3)

Spec: `decisions/2026-11-11_fable_tracks.md` "M5 = T-A". Runner: main session, local, one core, sequential (D-044).

### M5 exit (runnable)

1. `results/real/v5_killcheck.md` exists and states "go v5" or "switch to A'" by the kill rule (M5-01).
2. Invariance: v5 with k = 1 gives the saved v4 `food_collected` on 2 cells (M5-05).
3. The mechanism-check table for seeds 201 to 210 exists (M5-06). Reported only, no pick.
4. `check_runs.py` exits 0 on the M5 confirm root: 800 complete runs, seeds 221 to 260 (M5-07).
5. `results/real/v5/verdict.json` exists, pass or fail, with prereg path and judge sha256 (M5-08).
6. On fail: a root-cause memo exists (M5-09). The RQ1 row in `RQ.md` cites the verdict.

### Tactic: measure the cause, then one pre-registered 2 x 2 (kill: M5-01 predicts above 7.2 active wrong points per run at d = 0, then switch to A')

- [x] M5-01 → M5 → RQ1: step-0 kill check (data-analyst). Done: go v5, D-046. Output path set by the tool: `results/real/v5_killcheck.md` (M5 exit 1 path), not `v5/step0_kill.md`
  - Static: reads saved defense-off logs, seeds 11 to 30, only. No run.
  - Static: writes per source at d = 0 the same-robot repeat failures. Writes per decoy at d = 2 the time to the second failure.
  - Static: writes the predicted active wrong points per run at d = 0 under k = 2.
  - Static: compares it with 7.2 (half of 14.45, source file "Kill before code"). Above 7.2: "switch to A'" (a pickup within `r_merge` clears a pending point).
  - Static: output `results/real/v5/step0_kill.md`, every number read from a saved file.
- [x] M5-02 → M5: v5 design (system-architect). Done: `DESIGN_M5.md`, D-047
  - Static: a design section names k (fixed 2) and `t_lock` (0 or 10 s), or A' if M5-01 says switch.
  - Static: it states the schema impact. A needed schema change sends the slice back to M1 (DESIGN §5).
  - Static: it names the 5 arms: off, and (k 1 or 2) x (`t_lock` 0 or 10).
- [x] M5-03 → M5: code v5 and tools (developer)
  - Static: `CHANGELOG.md` has a v5 row. `code_version` is `v5`. k is a `<defense>` attribute and is in manifest params.
  - Static: run tools take seed blocks as CLI options. They refuse seeds 1 to 30, 101 to 116, and any block outside 201 to 210 and 221 to 260.
  - Static: run tools exit nonzero if the M5 prereg has no git commit. The invariance rerun (M5-05) is exempt from this check and the seed check.
  - Static: a judge script reads saved runs only and writes `results/real/v5/verdict.json`.
- [x] M5-04 → M5 → RQ1: prereg (developer writes, main session commits)
  - Static: `prereg/defense_v5.md` holds the 4 lines of `rules/measurement.md` §1, copied from the source "M5 = T-A".
  - Static: metric G(2) = F(2, v5) − F(2, off), seeds 221 to 260, paired bootstrap 10,000, 95 %.
  - Static: threshold G(2) lower bound > 0. Failure: G(2) interval includes 0, or the d = 0 cost upper bound < 0.
  - Static: contrast: 2 x 2 plus off, d = 0, 1, 2, 4. Both main effects reported at d = 0 and d = 2.
  - Gate: the git commit of the prereg is older than the first M5 run (M5-06).
- [x] M5-05 → M5: invariance, v5 with k = 1 (main session run). Done: 2 cells in `runs/invariance_v5/` (ignored root), STATUS 2026-11-11
  - Gate: 2 saved v4 cells rerun on v5 with k = 1 give equal `food_collected`. A mismatch stops M5 and goes to `recover`.
- [x] M5-06 → M5: mechanism check, seeds 201 to 210 (main session run, tool reads saved runs). Done: `results/real/v5/mechanism.md`, `mechanism.csv`
  - Gate: cells (d 0, on) and (d 2, on) on v5. A table of `sus_cls_src`, `sus_cls_dec` per run is saved under `results/real/v5/`.
  - Static: the table is reported only. No value is picked from it.
- [x] M5-07 → M5: confirm runs, seeds 221 to 260 (main session run). Done: `results/real/v5/check_confirm.txt` (800 runs, 0 failed)
  - Gate: 5 arms x d 0, 1, 2, 4 x 40 seeds = 800 runs. `check_runs.py` exits 0 on the root. M5 exit 4.
- [x] M5-08 → M5 → RQ1: verdict (main session runs the judge). Done: PASS for k2t10, `results/real/v5/verdict.json`, D-051, D-057
  - Gate: `results/real/v5/verdict.json` holds per-seed values, intervals, both main effects, pass, prereg path, judge sha256 (`rules/measurement.md` §4.1).
  - Gate: pm writes the verdict D-row. Pass or fail closes the task.
- [ ] M5-09 → M5 → RQ1: root cause (data-analyst; required on fail)
  - Static: `tools/failure_analysis.py` (or its extension) runs on the M5 roots. A memo `results/real/v5/root_cause.md` names the cause with saved-file paths.
  - Static: on pass, the memo states "not required" in one line.
  - Open: verdict PASS (D-051). `results/real/v5/root_cause.md` with the one line does not exist yet.
- [ ] M5-10 → M5: M5 gate review (reviewer)
  - Gate: reviewer checks M5 exit 1 to 6 and writes `results/reviews/M5_gate.md`.

## M6: T-B, ID-based adapted arm (by 2026-11-22, D-040, D-045, → RQ2, Vision)

Spec: `decisions/2026-11-11_fable_tracks.md` "M6 = T-B". Name: "adapted arm", never "replication" (D-040). `schema.py` unchanged.

### M6 exit (runnable)

1. The arm check on seeds 301 to 310 is saved: detractors isolated per run at d = 2 (M6-05).
2. `check_runs.py` exits 0 on the M6 confirm root: 640 complete runs, seeds 321 to 360 (M6-06).
3. `results/real/id_arm/verdict.json` exists: "differs" or "not resolved", or "adapted arm did not function" (M6-07).
4. On fail: a root-cause memo exists (M6-08). The RQ2 row in `RQ.md` cites the verdict.
- Kill: no gate-ready code by 2026-11-21. Then T-B becomes a T-E row and future work. pm writes the D-row.

### Tactic: shared trail store, DBSCAN, creator-ID graph (kill: above)

- [x] M6-01 → M6 → RQ2: TAROS defense re-read (researcher). Done: written as `research/taros_defense_spec.md`, not `taros_defense.md`
  - Static: reads the TAROS 2024 defense section only. Writes `research/taros_defense.md`.
  - Static: lists each mechanism step with page numbers: clustering, creator-ID graph, travel-time check, strike count, reintegration.
  - Static: marks each step "kept", "adapted to grid" or "dropped", with one reason.
- [x] M6-02 → M6: ID arm design (system-architect). Done: `DESIGN_M6.md`, D-048, D-049
  - Static: shared trail store in the loop functions. DBSCAN on trail ends, minPts 2, eps frozen before runs (D-045).
  - Static: creator-ID graph, travel-time check, 5 strikes isolate a creator, reintegration on a late pickup.
  - Static: isolation log as a sidecar file per run. `schema.py` unchanged.
- [x] M6-03 → M6: ID arm code (developer). Done: `CHANGELOG.md` v6 row, v6 invariance in `runs/invariance_v6/`
  - Static: `CHANGELOG.md` has a row for the ID arm. The arm is a `<defense>` mode. The sidecar file is written per run.
  - Static: grep `schema.py`: unchanged.
  - Static: run tools accept only seeds 301 to 310 and 321 to 360 for this arm. They exit nonzero if the M6 prereg has no git commit.
- [x] M6-04 → M6 → RQ2: prereg (developer writes, main session commits). Done: written as `prereg/defense_id_arm.md`
  - Static: `prereg/id_arm.md` holds the 4 lines of `rules/measurement.md` §1 from the source "M6 = T-B".
  - Static: it names the best no-ID arm, read from the M5 verdict, before the first M6 run. Metric delta = F(2, ID arm) − F(2, best no-ID arm).
  - Static: threshold: interval excludes 0 = "differs", else "not resolved". No win line.
  - Static: failure: fewer than 1 of 2 detractors isolated by run end in most seeds = "adapted arm did not function".
  - Static: eps value is written in the prereg.
- [x] M6-05 → M6: arm check, seeds 301 to 310 (main session run). Done: `results/real/id_arm/arm_check.csv`
  - Gate: d = 2, ID arm. A table of detractors isolated per run, from the sidecar files, is saved under `results/real/id_arm/`.
- [x] M6-06 → M6: confirm runs, seeds 321 to 360 (main session run). Done: 800 runs, 5 arms with k1t10 added (D-052), `results/real/id_arm/check_*.txt` 0 failed, `isolation.csv`
  - Gate: off, v3, v5, ID arm x d 0, 1, 2, 4 x 40 seeds = 640 runs. `check_runs.py` exits 0. Honest robots isolated per run are tabled.
- [x] M6-07 → M6 → RQ2: verdict (main session runs the judge). Done: "differs", `results/real/id_arm/verdict.json`, D-054
  - Gate: `results/real/id_arm/verdict.json` holds delta per seed, interval, the word ("differs", "not resolved" or "did not function"), prereg path, judge sha256.
  - Gate: pm writes the verdict D-row.
- [ ] M6-08 → M6 → RQ2: root cause (data-analyst; required on fail)
  - Static: `results/real/id_arm/root_cause.md` names the cause with saved-file paths. On pass, one line "not required".
  - Open: verdict "differs" (D-054), not a fail. `results/real/id_arm/root_cause.md` with the one line does not exist yet.
- [ ] M6-09 → M6: M6 gate review (reviewer)
  - Gate: reviewer checks M6 exit 1 to 4 and writes `results/reviews/M6_gate.md`.

## M7: T-D, scalability 20 vs 40 honest (by 2026-11-24, D-042, → RQ3, Mission)

Spec: `decisions/2026-11-11_fable_tracks.md` "M7 = T-D". No new defense code. Frozen values, not re-tuned at 40 (stated limit).

### M7 exit (runnable)

1. `check_runs.py` exits 0 on the M7 root: 360 complete runs, seeds 401 to 430 (M7-02).
2. `results/real/scale/verdict.json` exists, with the congestion check (M7-03).
3. On fail: a root-cause memo exists (M7-04). The RQ3 row in `RQ.md` cites the verdict.
- Kill: M5 or M6 slips past 2026-11-22. Then run v3 and off only. pm writes the D-row.

### Tactic: one density step, same arena (kill: above)

- [x] M7-01 → M7 → RQ3: prereg and the N option (developer; main session commits the prereg). Done: `prereg/scale.md`, best arm k2t10 (D-053)
  - Static: `prereg/scale.md` holds the 4 lines of `rules/measurement.md` §1 from the source "M7 = T-D".
  - Static: metric G/N at 10 % detractors (d = 2 at N = 20, d = 4 at N = 40), seeds 401 to 430. Threshold: the N=40 minus N=20 interval excludes 0.
  - Static: failure: F(0, off) per robot at N = 40 below half of N = 20 = "confounded by congestion". "Best arm" is named from the M5 and M6 verdicts.
  - Static: `make_sweep.py` takes the honest robot count as an option. Controller and defense code unchanged (git diff on `src/controllers/` empty).
- [x] M7-02 → M7: runs, seeds 401 to 430 (main session run). Done: 360 runs, `results/real/scale/check_*.txt` 0 failed
  - Gate: N 20, 40 x d 0, 10 % x off, v3, best arm x 30 seeds = 360 runs. `check_runs.py` exits 0.
- [x] M7-03 → M7 → RQ3: verdict (main session runs the judge). Done: v5 scales worse, v3 not resolved, `results/real/scale/verdict.json`, D-055
  - Gate: `results/real/scale/verdict.json` holds G/N per seed, the difference interval, the congestion check, wrong source suspects per robot, prereg path, judge sha256.
  - Gate: pm writes the verdict D-row.
- [x] M7-04 → M7 → RQ3: root cause (data-analyst; required on fail). Done: private confirmation, `results/real/scale/root_cause.md`, D-056
  - Static: `results/real/scale/root_cause.md` names the cause with saved-file paths. On pass, one line "not required".
- [ ] M7-05 → M7: M7 gate review (reviewer)
  - Gate: reviewer checks M7 exit 1 to 3 and writes `results/reviews/M7_gate.md`.

## M8: T-E table and T-F report (2026-11-24 to 2026-11-28, → Vision, G3)

Spec: `decisions/2026-11-11_fable_tracks.md` "M8 = T-E + T-F". No runs. Headline stays v3 (D-026).

### M8 exit (runnable)

1. The T-E table file exists with 7 rows and 5 columns (M8-01).
2. The final report HTML opens with one comparison chart and has one failure section per failed verdict (M8-02).
3. G3 check: 3 of 3 run tracks (M5, M6, M7) have a committed `verdict.json`, and each fail has a root-cause memo. Met 2026-11-12: 3 of 3 verdict files exist. The one scales-worse (M7) has `results/real/scale/root_cause.md` (D-056).
4. The slides outline exists (M8-03).

### Tactic: one table, one chart, one page

- [x] M8-01 → M8: T-E comparison table (researcher; no runs). Done: written as `research/cost_of_trust.md` Table 1, not `results/real/te_table.md`. 8 rows (adds k1t10)
  - Static: `results/real/te_table.md`. Rows: blockchain, TAROS, ICCCR, cautionary pheromone, v3, v5, ID arm.
  - Static: columns: messages, IDs, shared store, per-robot memory, measured d = 0 cost (ours only, read from verdict files).
  - Static: ICCCR (T-C, D-041) is a row only. Cells without a source say "not reported".
- [~] M8-02 → M8 → Vision: final report HTML (developer for the script, main session runs it). In final edit
  - Static: one comparison chart: no-ID arms beside the ID arm (Vision, D-035). Every number read from saved verdict and stats files.
  - Static: one failure section per failed verdict, linking its root-cause memo. Includes the M4 section (M4-06).
  - Static: future work: dynamic food, a learned suspect test, quarantine regions.
  - Static: uses `skills/html-theme/theme.css`. Rendered once in headless Chrome per `rules/answering.md` §3.
- [x] M8-03 → M8: slides outline (sonnet-writer, from M8-02). Done: `results/slides_outline.md`
  - Static: `results/slides_outline.md`, one line per slide, each slide names its source figure or table.
- [ ] M8-04 → M8: project-end review (reviewer, system-architect, data-analyst)
  - Gate: final verdict and open items list, per `.claude/CLAUDE.md` Workflow step 4 "Project end".
