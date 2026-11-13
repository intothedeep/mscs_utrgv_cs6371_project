> Split from `PLAN.md` (rules/docs.md §1). The PLAN.md stub is the truth if
> the two disagree; update both in the same edit.

# Tasks: p2_assigned_informed_search

Mission block, task format, run forms and fixed paths: [PLAN.md](./PLAN.md).
Roles: developer (code, static AC only), data-analyst (pre-registrations, memos), sonnet-writer (prose), product-manager (D-rows, living docs), main session (every build and run, D-002).

## M1: MVP1 shape (mock end-to-end, by 2026-11-14)

### M1 exit (runnable, runner: main session)

1. `tools/make_mock_runs.py` writes 90 S1 runs and 300 S3 runs under `mock/runs/`. Every runid starts `MOCK_`.
2. `tools/check_runs.py mock/runs` exits 0 on all 390 runs.
3. `tools/collect_runs.py mock/runs --out results/mock/runs.csv` writes 390 rows with the DESIGN §6.5 header.
4. `tools/analyze.py --set S3 --criteria prereg/S3_eval_MOCK.json results/mock/runs.csv` writes `fig_boxplot_3dist_MOCK.png`, `fig_paired_diff_MOCK.png`, `fig_branch_shares_MOCK.png`, `improvement_MOCK.csv`, `verdict_MOCK.json` under `results/mock/S3/`.
5. `tools/analyze.py --selfcheck` exits 0 (hand-worked Wilcoxon and bootstrap examples).
6. Breakage (DESIGN §6.6 item 7), each on a scratchpad copy, each makes `check_runs.py` exit nonzero and name the cause:
   - a renamed `forage_per_minute.csv` column,
   - a manifest `collected` that differs from the score line,
   - one root holding a `mock` = 1 and a `mock` = 0 run.
7. `tools/report.py --phase mvp1` writes one stage report per stage and `results/mock/mvp1/index.html`. The cost chart stage is listed as "skipped, not built yet".
8. Gate review: reviewer, `cycle 1/2; recovery 0/2`.

### Tactic: schema first, mock fills it (kill: a column the mock cannot fill without changing DESIGN §6.5)

- [x] M1-01 → M1: Python project files and `.gitignore` (developer, U1 part)
  - Static: `p2_assigned_informed_search/pyproject.toml` per `rules/development/python.md`: `[tool.uv] python-downloads = "never"`. Dependencies numpy and matplotlib only (D-011).
  - Static: `submodule_project/.gitignore` adds `p2_assigned_informed_search/mock/runs/` and `p2_assigned_informed_search/build_ours/`. Existing lines for `vendor/`, `build_baseline/`, `runs/` stay. `prereg/`, `results/`, `src/` are not ignored.
  - Gate: main session runs `uv sync` once before M1 exit 1.
  - Depends on: none.
- [x] M1-02 → M1: `tools/schema.py` (developer, U1)
  - Static: `SCHEMA_VERSION = 1`. `RUNS_COLUMNS` lists the DESIGN §6.5 columns in table order.
  - Static: `QUERIES_COLUMNS` lists DESIGN §5.1 columns. `FORAGE_COLUMNS = ["minute", "collected"]`. `POINTS_COLUMNS = ["t_s", "robot", "x", "y"]`.
  - Static: `RUN_FILES` lists the 6 files of DESIGN §6.4 (`run.argos`, `stdout.log`, `manifest.json`, `forage_per_minute.csv`, `queries.csv`, `points.csv`).
  - Static: `MANIFEST_KEYS` holds the DESIGN §6.4 keys plus `code_version`, `code_sha`, `params`, `env`, `metrics` (`rules/measurement.md` §2.1).
  - Static: `ARMS`, `DISTRIBUTIONS` (`random`, `powerlaw`, `clustered`), `SCORE_PATTERN` = the DESIGN §6.4 regex, `RUNID_PATTERN`.
  - Static: `SETS` = `S0` to `S5` plus `S0det` (determinism pair), `S0v2` (S0 re-run on the M3 build), `SMK` (M3 `qmap` smoke). Each set has its own run root (PLAN fixed paths).
  - Static: `METRICS_TAG` = the prefix of the one `stdout.log` line our build prints with run totals. `SCORE_PATTERN` cannot match it.
  - Static: no other file in `tools/` holds a column literal (grep each name of `RUNS_COLUMNS` in `tools/*.py`, only `schema.py` matches).
  - Depends on: M1-01.
- [x] M1-03 → M1: `tools/check_runs.py` (developer, U1, DESIGN §6.6)
  - Static: `check_runs.py <root>` checks items 1 to 6 of DESIGN §6.6. Item 5 and 6 run only for S3 and S4 runs.
  - Static: header-only `queries.csv` and `points.csv` pass only when manifest `arm` = `vendor` (PLAN open item).
  - Static: runid prefix `MOCK_` exactly when `mock` = 1. Runid matches `schema.RUNID_PATTERN`.
  - Static: exits nonzero on any failure and prints run, file and column or key. Prints the missing-cell list for item 4.
  - Gate: M1 exit 2 and 6.
  - Depends on: M1-02.
- [x] M1-04 → M1: `tools/collect_runs.py` (developer, pm proposal, PLAN open item)
  - Static: `collect_runs.py <root> --out <csv>` reads each run folder and writes one row per run with exactly `schema.RUNS_COLUMNS`.
  - Static: non-applying columns are empty, not 0 (DESIGN §6.5). `share_*` come from `queries.csv` `branch` rows. `ops_per_query_*` come from `nodes_visited`.
  - Static: refuses an `--out` path outside `results/mock/` for mock roots and outside `results/real/` for real roots.
  - Static: the same code path serves mock and real (no `if mock` branch for column values).
  - Gate: M1 exit 3.
  - Depends on: M1-02.
- [x] M1-05 → M1: `tools/make_mock_runs.py` (developer, U2)
  - Static: writes only under `mock/runs/`. A different root makes it exit nonzero before writing.
  - Static: S1 = arm `cpfa` × 3 distributions × seeds 1001 to 1030. S3 = arms `cpfa`, `qmap` × 3 distributions × seeds 2001 to 2050.
  - Static: each run folder holds the 6 `schema.RUN_FILES`. `run.argos` and `stdout.log` are stub text that starts `MOCK`. `mock` = 1 in the manifest.
  - Static: the score line in `stdout.log` matches `schema.SCORE_PATTERN` and equals manifest `collected` and the last per-minute row.
  - Static: `layout_sha` is equal across arms for each (distribution, seed). Fixed generator seed, so two calls give identical files.
  - Static: mock `qmap` means differ by distribution (one up, one flat, one down), so all 3 verdict words can appear.
  - Gate: M1 exit 1 and 2.
  - Depends on: M1-02.
- [x] M1-06 → M1: `tools/analyze.py` statistics (developer, U3, DESIGN §6.2 items 3 to 8)
  - Static: improvement = `100 · (mean_qmap − mean_cpfa) / mean_cpfa`. 95 % percentile bootstrap, 10,000 resamples of the seed index, paired, fixed bootstrap seed.
  - Static: verdict per distribution: `improves`, `worse`, `not resolved` by the interval rule only.
  - Static: Wilcoxon signed-rank in numpy (normal approximation, tie correction), Holm over 3 distributions, medians, detectable size from S1 σ. These go to `improvement.csv` only, never into the verdict (D-011).
  - Static: `verdict.json` holds per comparison: arms, pairs, paired differences, statistics, verdict, criteria file path and sha, `analyze.py` sha (`rules/measurement.md` §4.1).
  - Static: `--selfcheck` runs one hand-worked Wilcoxon example (expected values written in the source comment) and one bootstrap case with a known sign. Exits nonzero on mismatch.
  - Static: stops on a mixed `mock` column. Mock output names end `_MOCK`. Missing cells are listed and the script continues.
  - Static: resample count, bootstrap seed, interval level and verdict rule are read from the criteria file passed by `--criteria`. None is typed in the script.
  - Gate: M1 exit 4 and 5.
  - Depends on: M1-04, M1-10.
- [x] M1-07 → M1: `tools/analyze.py` figures and `tools/plot_style.py` (developer, U3, DESIGN §6.7)
  - Static: `plot_style.py` holds the arm → color map (`cpfa` gray) and the font list of `rules/figures.md` §5. Every figure imports it.
  - Static: `fig_boxplot_3dist`: 3 distributions on one x axis, `cpfa` gray and `qmap` colored, 50 points overlaid. % improvement and interval above each pair.
  - Static: `fig_paired_diff`: mean paired difference per distribution, 95 % interval, zero line. `fig_branch_shares`: departures per branch, both arms.
  - Static: legend outside, above the axes (`fig.legend(loc="outside upper center")`, `layout="constrained"`). Mock titles contain "MOCK DATA".
  - Gate: M1 exit 4. Main session opens each PNG and checks no overlap.
  - Depends on: M1-06.
- [x] M1-08 → M1: `tools/report.py` (developer, U4)
  - Static: `--phase <name>` reads saved outputs only (manifests, `runs.csv`, check and analyze logs, figures). No number is typed into the script.
  - Static: one report per stage with the fields of `.claude/CLAUDE.md` "System build phasing", one figure and one table.
  - Static: a stage with no saved output is reported as skipped with the reason. The script continues.
  - Static: `index.html` links every stage report and uses `skills/html-theme/theme.css`.
  - Gate: M1 exit 7. Main session renders `index.html` with the `rules/answering.md` §3 Chrome command.
  - Depends on: M1-07.
- [ ] M1-09 → M1: M1 gate run (main session)
  - Gate: M1 exit 1 to 7 run in order. Command lines and exit codes go into `results/mock/mvp1/gate_log.txt`.
  - Depends on: M1-01 to M1-08, M1-10.
- [x] M1-10 → M1: mock criteria file `prereg/S3_eval_MOCK.json` (data-analyst)
  - Static: same keys as DESIGN §6.2 items 1 to 8, values from DESIGN §6.2. Top-level `"mock": true` and "MOCK" in its title field.
  - Static: M4-05 later writes the real `prereg/S3_eval.json` with the same keys. The mock file is never cited by a real verdict.
  - Depends on: none.

## M2: MVP2 baseline slice (by 2026-11-18)

### M2 exit (runnable, runner: main session)

0. Precondition: `prereg/S0_invariance.json` and `prereg/S1_headroom.json` are committed and their D-row exists (M2-08).
1. `build_ours/` builds from `src/` with the same configure command used for `build_baseline/`, with no error.
2. Determinism: `make_runs.py --set S0det --arm vendor --dist random --seeds 3001 --repeat 2`, then `run_argos.py runs/S0det`. Then `invariance.py --determinism` on the 2 runs exits 0.
3. S0: `make_runs.py --set S0 --arm vendor,cpfa --seeds 3001-3005`, then `run_argos.py runs/S0`. `invariance.py runs/S0 --out results/real/S0/invariance.json` reports 15 of 15 pairs equal.
4. S1: `make_runs.py --set S1 --arm cpfa --seeds 1001-1030`, then `run_argos.py runs/S1` (90 runs). `check_runs.py runs/S1` exits 0 with `check_runs.py` and `schema.py` unchanged since M1.
5. `collect_runs.py runs --out results/real/runs.csv` writes one row per run under `runs/` (S0det 2, S0 30, S1 90).
6. `analyze.py --headroom results/real/runs.csv` writes `results/real/S1/headroom.json` (Table 8 readings, σ per distribution).
7. `analyze.py --set S3 results/real/runs.csv` (no `--criteria`) lists the missing S3 cells and exits 0 before any verdict.
8. `report.py --phase mvp2` writes the stage reports and `results/real/mvp2/index.html`.
9. Gate review: reviewer, `cycle 1/2; recovery 0/2`.
- Kill R1: exit 2 fails → stop, root-cause memo, no paired design until fixed.
- Kill R2: exit 3 has any mismatch → no S3 run until fixed.
- A schema change needed by real code sends that slice back to M1 (bump `schema_version`, regenerate the mock).

### Tactic: copy the vendor once, add a switch that does nothing when off (kill: build fails after 2 fix cycles on the BCM §6 risks)

- [ ] M2-01 → M2: `src/` copy, CMake fixes, `patches/ours.diff`, `CHANGELOG.md` (developer, U5 part 1)
  - Static: `src/` is a copy of `vendor/Collision_Free_CPFA/` `source/`, `CMakeLists.txt` and `experiments/Random_CPFA_r24_tag256_10by10.xml`. No vendor file is edited.
  - Static: no build edit up front. The vendor tree already built in `build_baseline/`. Build edits from BCM §6 are made only after M2 exit 1 fails, each with a WHY comment.
  - Static: the main session passes the `build_baseline/` configure command in the dispatch. The task writes it into `src/BUILD.md` for `build_ours/`.
  - Static: `patches/ours.diff` = `diff -ru` of vendor vs `src/`. It is empty at this point, except new files.
  - Static: `CHANGELOG.md` is one table (`rules/measurement.md` §2.2) with a `v1` row. `CODE_VERSION` constant in `CPFA_loop_functions.cpp`.
  - Gate: M2 exit 1.
  - Depends on: none.
- [ ] M2-02 → M2: switch plumbing and new parameters (developer, U5 part 2, DESIGN §4.1)
  - Static: `<CPFA>` attribute `InformedSearch` read with `GetNodeAttributeOrDefault`, default `0`. Every DESIGN Table 6 parameter is read the same way with its start value.
  - Static: with the switch off, no new code draws random numbers. Grep `RNG->` and `CreateCategory` in the added lines of `patches/ours.diff`: every match sits inside an `if (InformedSearch)` block. The vendor draws are `RNG->Uniform` and `RNG->Gaussian` (`ctrl.cpp:259` to `792`, `lf.cpp:356` to `481`).
  - Static: with the switch off, `Returning()` decision order and `SetRandomSearchLocation()` match the vendor lines (`ctrl.cpp:526-544`, `ctrl.cpp:578-605`) byte for byte in the diff.
  - Gate: M2 exit 3.
  - Depends on: M2-01.
- [ ] M2-03 → M2: run logger (developer, U5 part 3, DESIGN §5.1)
  - Static: the loop functions write `queries.csv` with `schema` columns in both switch states. In `cpfa`, one row per nest decision with `branch` set, cost columns empty.
  - Static: `branch` values `fidelity`, `pheromone`, `random` come from the existing `Returning()` branches (`ctrl.cpp:530`, `535`, `542`). Logging reads state only.
  - Static: `points.csv` is written header-only when the switch is off.
  - Static: at run end, the loop functions print one `stdout.log` line that starts with `schema.METRICS_TAG`. It holds swarm totals of `travelingTime` and `searchingTime` (`ctrl.h:69-70`, in ticks), the departure count and `layout_sha`.
  - Static: `layout_sha` = sha256[:12] of the initial `FoodList` (`lf.h:116`) after layout, read only, in both switch states.
  - Static: the C++ code never writes `manifest.json`. `run_argos.py` (M2-05) is the one writer.
  - Static: logging never draws random numbers and never writes state a controller reads (DESIGN §4.1).
  - Gate: M2 exit 3 and 4.
  - Depends on: M2-02.
- [ ] M2-04 → M2: `tools/make_runs.py` (developer, U6 part 1)
  - Static: flags `--set`, `--arm` (comma list), `--dist` (default all 3), `--seeds` (list or range), `--repeat` (S0det only). Any set outside `schema.SETS` is refused.
  - Static: `--set <set> --arm <arm>` writes `runs/<set>/<runid>/run.argos` from `xml10` with: `FoodDistribution` 0, 1, 2 per distribution, `MaxSimTimeInSeconds="720"`, `NestRadius` per D-006, `random_seed` per run, `length="0"`.
  - Static: library paths are absolute, to `build_ours/` or `build_baseline/`.
  - Static: seeds 0 and 1 are refused. Tuning and evaluation seed blocks never overlap (DESIGN §6.1).
  - Static: the `vendor` arm file carries no attribute our build adds (DESIGN §10 open item), unless M2-10 shows beta59 accepts them.
  - Depends on: M1-02, M2-01.
- [ ] M2-05 → M2: `tools/run_argos.py` (developer, U6 part 2)
  - Static: runs one folder at a time: creates `results/`, calls `timeout 120 argos3 -n -c run.argos` with the run folder as working directory, saves `stdout.log`.
  - Static: parses the score by `schema.SCORE_PATTERN`, not "last line". Converts the vendor `ForageData.txt` to `forage_per_minute.csv`.
  - Static: the only writer of `manifest.json`, with all `schema.MANIFEST_KEYS`. `nest_radius_eff` parsed from the `NestRadius=` log line (`lf.cpp:112`). `lib_sha` = sha256[:12] of both libraries.
  - Static: parses the `schema.METRICS_TAG` line. `travel_s`, `search_s` = ticks / `ticks_per_second` read from `run.argos` (32 in `xml10`).
  - Static: for `arm = vendor`, writes header-only `queries.csv` and `points.csv`. `layout_sha` and the time totals stay empty (the vendor prints no tag line).
  - Static: exempt from the 300 s Python cap. Form: `OMP_NUM_THREADS=1 uv run python tools/run_argos.py <root>`. Each `argos3` call has its own `timeout 120`.
  - Static: exits nonzero if a library is missing. Runs are sequential, no worker pool.
  - Gate: M2 exit 2 to 4.
  - Depends on: M2-04.
- [ ] M2-06 → M2: `tools/invariance.py` (developer, U7, DESIGN §4.3)
  - Static: `--determinism <run_a> <run_b>` compares collected and every per-minute row.
  - Static: `<root>` pairs vendor and `cpfa` runs by (distribution, seed) and writes `results/real/S0/invariance.json` with each pair and a pass count.
  - Static: exits nonzero on any mismatch and names the pair and the first differing minute.
  - Gate: M2 exit 2 and 3. Breakage: a scratchpad copy with one edited per-minute row fails.
  - Depends on: M2-05.
- [ ] M2-07 → M2: pre-registrations `prereg/S0_invariance.json`, `prereg/S1_headroom.json` (data-analyst)
  - Static: each file has the 4 lines of `rules/measurement.md` §1 (metric, threshold, contrast, failure condition) and names its goal or RQ.
  - Static: `S1_headroom.json` copies DESIGN Table 8 readings and actions, plus the R4 and R13 round-1 rules, word for word.
  - Depends on: none.
- [ ] M2-08 → M2: D-row for the S0 and S1 pre-registrations (product-manager)
  - Static: one `DECISIONS.md` row cites both file paths before any S0 or S1 run.
  - Depends on: M2-07.
- [ ] M2-09 → M2: `analyze.py --headroom` (developer)
  - Static: reads `runs.csv` S1 rows only. Writes `results/real/S1/headroom.json`: `share_random` per distribution, `search_s / travel_s`, σ of `collected`, and the Table 8 action that fires.
  - Static: thresholds are read from `prereg/S1_headroom.json`, never typed in the script.
  - Gate: M2 exit 6.
  - Depends on: M1-06, M2-07.
- [ ] M2-10 → M2: M2 gate run (main session)
  - Gate: M2 exit 0 to 8 in order. S0 is 30 runs. S0det is 2 runs. S1 is 90 runs. Log to `results/real/mvp2/gate_log.txt`.
  - Gate: records whether the vendor build accepts our attributes (DESIGN §10).
  - Depends on: M2-01 to M2-09, M1 gate PASS.
- [ ] M2-11 → M2 → RQ1: headroom memo (data-analyst)
  - Static: `results/real/S1/headroom_memo.md` names the Table 8 action that fired, with paths to `headroom.json`. No retyped number.
  - Depends on: M2-10.

## M3: MVP3 map and benchmark (by 2026-11-21)

### M3 exit (runnable, runner: main session)

0. Precondition: `prereg/G1_bench.json` is committed and its D-row exists (M3-10).
1. `build_ours/` builds `visit_map`, `bench_visit_map` and the hooked controller with no error.
2. `OMP_NUM_THREADS=1 timeout 300 build_ours/.../bench_visit_map --out results/real/bench/bench.csv` writes rows for arenas 10 to 320 m.
3. A and B equivalence holds on every query (benchmark exit 0).
4. `analyze.py --bench --criteria prereg/G1_bench.json` writes `fig_cost_vs_arena.png` and `G1_verdict.json` under `results/real/bench/`.
5. `make_runs.py --set SMK --arm qmap --seeds 1001`, then `run_argos.py runs/SMK`: 3 runs, one per distribution, start values. `check_runs.py runs/SMK` exits 0.
6. `make_runs.py --set S0v2 --arm vendor,cpfa --seeds 3001-3005` on the new build, then `run_argos.py runs/S0v2`. `invariance.py runs/S0v2 --out results/real/S0v2/invariance.json` reports 15 of 15.
7. `report.py --phase mvp3` writes `results/real/mvp3/index.html`.
8. Gate review: reviewer, `cycle 1/2; recovery 0/2`.
- Kill R6: exit 3 fails on 2026-11-21 → ship A behind the same interface, D-row.

### Tactic: one pure map module, two structures, one query rule (kill: R6 above)

- [x] M3-01 → M3: `visit_map` interface and option A (developer, U8 part 1)
  - Static: `src/source/InformedSearch/visit_map.{h,cpp}` include no ARGoS header (grep `argos3` returns nothing).
  - Static: one interface: `InsertBatch`, `Reserve`, `NearestAvailable`, `Clear`, size getters, an operation counter.
  - Static: A = fine uniform grid, ring search. Query rule of DESIGN §3.1 (box distance, row then column tie, cell centre, nest disk and forage range excluded).
  - Depends on: none (may start during M1).
- [x] M3-02 → M3: option B region quadtree (developer, U8 part 2, DESIGN §3.3)
  - Static: node = 16 bytes (`first_child`, `t_last`, `t_res_until`, `a_min`). Insert splits, sets `t_last`, recomputes `a_min`, merges per §3.3.
  - Static: `NearestAvailable` is best-first by box distance, skips `a_min > now`, applies the same tie rule as A.
  - Static: merge can be switched off (benchmark structure 6).
  - Depends on: M3-01.
- [ ] M3-03 → M3: `bench_visit_map` (developer, U9, DESIGN §5.2)
  - Static: links only `visit_map`. Structures 1 to 6 of DESIGN §5.2 behind one interface.
  - Static: synthetic generator (200 robots, 20 trips, 100 points per trip, fixed seed) and `points.csv` replay.
  - Static: writes the §5.2 output columns. Exits nonzero if A and B return a different cell for any query.
  - Static: CMake target in `src/`, built into `build_ours/`.
  - Depends on: M3-02.
- [ ] M3-04 → M3 → G1, RQ2: `prereg/G1_bench.json` (data-analyst)
  - Static: G1 lines 1 to 3 of DESIGN §5.2. Which arenas decide G1 ("80 m" or "80 m and larger") follows the D-row of the main session pick (PLAN open item).
  - Static: the 4 lines of `rules/measurement.md` §1. A fail gets a root-cause memo, the line does not move.
  - Depends on: the G1-reading D-row.
- [ ] M3-05 → M3: controller hooks (developer, U10, DESIGN §4.2)
  - Static: every hook row of DESIGN §4.2 exists, each inside `if (InformedSearch)`. New flag `isMapTarget`. `isInformed` is not assigned in new code.
  - Static: `SetMapTarget()` queries and reserves. No answer → `SetRandomSearchLocation()` and a `fallback_random` row.
  - Static: the `q_map` draw uses its own `CRandom::CreateCategory` stream.
  - Static: `patches/ours.diff` regenerated. `CHANGELOG.md` gets a `v2` row.
  - Depends on: M2-03, M3-02.
- [ ] M3-06 → M3: cost logging and the `qmap` arm in the harness (developer)
  - Static: `queries.csv` fills `nodes_visited`, `nodes_total`, `leaves_total`, `points_inserted_total`, `query_us`, target and `reached` in `qmap` runs. `points.csv` gets every upload.
  - Static: `make_runs.py` accepts `--arm qmap` with a parameter file. `collect_runs.py` fills the cost columns.
  - Depends on: M3-05, M2-05.
- [ ] M3-07 → M3: `analyze.py --bench` (developer)
  - Static: reads `bench.csv` only. Writes `fig_cost_vs_arena.png` (log scale) and `G1_verdict.json` with criteria path and sha.
  - Static: thresholds are read from `prereg/G1_bench.json`.
  - Depends on: M3-03, M3-04.
- [ ] M3-08 → M3: M3 gate run (main session)
  - Gate: M3 exit 0 to 7 in order. Log to `results/real/mvp3/gate_log.txt`.
  - Depends on: M3-01 to M3-07, M3-10, M2 gate PASS.
- [ ] M3-09 → M3 → G1: G1 root-cause memo, only if a G1 line fails (data-analyst)
  - Static: `results/real/bench/root_cause.md` names the failed line, the cause and the evidence paths.
  - Depends on: M3-08.
- [ ] M3-10 → M3: D-row for `prereg/G1_bench.json` (product-manager)
  - Static: one `DECISIONS.md` row cites the file path and sha before the first benchmark run.
  - Depends on: M3-04.

## M4: tuning, freeze, pre-registration (by 2026-11-23)

### M4 exit (runnable, runner: main session)

1. `results/real/S2/tuning_table.csv` holds every round and candidate (270 runs, or the R10 path).
2. Frozen values are in a `DECISIONS.md` row.
3. `prereg/S3_eval.json`, `S4_sens.json`, `S5_ablation.json` are committed, and their self-check passed, before any S3 run.
4. Gate review: reviewer, `cycle 1/2; recovery 0/2`.
- Kill R10: M3 not done by 2026-11-22 → S2 skipped, start values frozen, D-row.
- These rows are re-cut after the M2 headroom memo (M2-11).

### Tactic: tune only the new parameters on tuning seeds (D-009)

- [ ] M4-01 → M4: `prereg/S2_tuning.json` (data-analyst)
  - Static: DESIGN §6.3 rounds, candidates, metric and tie rule, with the Table 8, R4 and R13 actions fired by `headroom.json`.
  - Depends on: M2-11.
- [ ] M4-08 → M4: D-row for `prereg/S2_tuning.json` (product-manager)
  - Static: one `DECISIONS.md` row cites the file path before round 1.
  - Depends on: M4-01.
- [ ] M4-02 → M4: `tools/tune.py` and `tools/pick.py` (developer, U11)
  - Static: `tune.py --round k` writes the round's candidates as runs on seeds 1001 to 1010. It refuses a candidate that changes more than one parameter from the current best.
  - Static: `pick.py` reads saved runs only and writes `tuning_table.csv` and `pick.json` by the pre-registered rule.
  - Depends on: M3-06, M4-01.
- [ ] M4-03 → M4: S2 rounds 1 to 3 (main session)
  - Gate: each round runs, then `pick.py`. M4 exit 1. `tune.py` uses the `run_argos.py` form (no 300 s cap, `timeout 120` per run).
  - Depends on: M4-02, M4-08, M3 gate PASS.
- [ ] M4-04 → M4: freeze D-row (product-manager)
  - Static: one row with the frozen values and the `pick.json` path. M4 exit 2.
  - Depends on: M4-03.
- [ ] M4-05 → M4 → RQ1, RQ3: `prereg/S3_eval.json`, `S4_sens.json`, `S5_ablation.json` (data-analyst, U12)
  - Static: S3 holds DESIGN §6.2 items 1 to 9. S4 differs only in nest radius (D-006). S5 lists one ablation arm per tactic.
  - Depends on: M4-04.
- [ ] M4-06 → M4: pre-registration stamp and self-check (developer, U12)
  - Static: `make_runs.py` writes `prereg_sha` into every S3, S4, S5 manifest. `analyze.py` refuses a set whose runs carry another sha.
  - Static: `analyze.py --prereg-selfcheck <file>` scores control inputs (`rules/research.md` §7 item 3): a clear gain passes, identical arms do not pass, a clear loss reads `worse`.
  - Depends on: M4-05.
- [ ] M4-07 → M4: self-check run and commit (main session)
  - Gate: `--prereg-selfcheck` exits 0 for each file. Its output is committed with the files. M4 exit 3.
  - Depends on: M4-06.
- [ ] M4-09 → M4: D-row for `prereg/S3_eval.json`, `S4_sens.json`, `S5_ablation.json` (product-manager)
  - Static: one `DECISIONS.md` row cites the 3 paths and shas before any S3 run.
  - Depends on: M4-07.

## M5: evaluation, verdict, report (by 2026-11-27)

### M5 exit (runnable, runner: main session)

1. 300 S3 runs pass `check_runs.py` (G2).
2. `results/real/S3/verdict.json` and `improvement.csv` are committed (G3).
3. A root-cause memo exists for each distribution that is `worse` or `not resolved` (G3).
4. S4 is reported as sensitivity. S5 is reported if run.
5. `report.py --phase final` writes `results/real/final/index.html` with the Vision page items.
6. Project-end review: reviewer, system-architect, data-analyst.
- Kill R7: S4 median run > 60 s → S4 reduced to 20 seeds, D-row.
- Kill R9: `layout_sha` differs across arms → stop S3, root-cause memo.

### Tactic: paired evaluation on fresh seeds, one decision rule (DESIGN §6.2)

- [ ] M5-01 → M5 → G2: S3 runs (main session)
  - Gate: 300 runs, check, then `collect_runs.py runs --out results/real/runs.csv` (all sets in one file). M5 exit 1.
  - Depends on: M4-09.
- [ ] M5-02 → M5 → G3, RQ1: S3 analysis and verdict commit (main session)
  - Gate: `analyze.py --set S3` writes `verdict.json`, `improvement.csv`, figures. M5 exit 2.
  - Depends on: M5-01.
- [ ] M5-03 → M5 → G3: root-cause memos (data-analyst)
  - Static: one `root_cause_<distribution>.md` per non-improving distribution, citing `queries.csv` branch and `reached` evidence by path. M5 exit 3.
  - Depends on: M5-02.
- [ ] M5-04 → M5: S4 runs and analysis (main session)
  - Gate: 300 runs, or 120 under R7. Check, collect, analyze. M5 exit 4.
  - Depends on: M5-02.
- [ ] M5-05 → M5 → RQ3: S5 ablation, only if time remains (main session)
  - Gate: runs per `S5_ablation.json`, then analyze. Skipped → recorded with the reason.
  - Depends on: M5-04.
- [ ] M5-06 → M5: method section prose (sonnet-writer)
  - Static: `results/real/final/method.md` from DESIGN §1, §3.3, §4. No number that is not read from a saved output path.
  - Depends on: M3 gate PASS.
- [ ] M5-07 → M5: `report.py --phase final` (developer, U13)
  - Static: one page with the box plot, paired difference, cost-vs-arena chart, branch shares, `method.md`, memo links and the S4 table.
  - Depends on: M5-03, M5-06.
- [ ] M5-08 → M5: final report build and render check (main session)
  - Gate: M5 exit 5. Chrome render per `rules/answering.md` §3: no horizontal scroll, no overlap.
  - Depends on: M5-07.
- [ ] M5-09 → M5 → G1, G2, G3: goal check and RQ evidence (product-manager)
  - Static: mission block goal lines marked met or not, with paths. `RQ.md` rows get evidence paths.
  - Depends on: M5-08.
