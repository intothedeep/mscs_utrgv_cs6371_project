# M1 gate review: MVP1 mock end-to-end

- Reviewer: `reviewer` agent, 2026-11-11. Gate review 1 for M1 (PLAN line shows `cycle 0/2; recovery 0/2`).
- Target: `01_pheromone/` at submodule commit `9c96d69`.
- Verdict: **ISSUE**. 4 blocking issues (I-1 to I-4), 9 minor.
- The flow itself works: 80 mock runs pass the check, and the analysis reproduces the saved numbers.

## What was run in this review

| Command (form: `OMP_NUM_THREADS=1 timeout 300 uv run python ...`) | Result |
| --- | --- |
| `tools/check_runs.py mock/runs` | exit 0, `SUMMARY runs=80 failed=0 problems=0` |
| `tools/analyze.py mock/runs` | exit 0. `g2_stats.csv` and `summary.csv` are byte-equal to the saved copies |

- Not run here (outside the allowed runs): the generator, both breakages, `make_report.py`, a browser render of the pages.
- Environment check: `.python-version` 3.12.12, `.venv` python3.12, `requires-python >=3.12`. They agree.

## M1 exit criteria

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| 1 | 80 run folders under `mock/runs/`, every runid starts `MOCK_` | met | `ls mock/runs`: 80 folders, 0 without the prefix |
| 2 | `check_runs.py mock/runs` exits 0 | met | re-run in this review, `results/mock/check_log.txt` |
| 3 | `analyze.py mock/runs` writes the chart and `summary.csv` | met, with I-3 | re-run in this review, `results/mock/g2_recovered_share_MOCK.png`, `results/mock/summary.csv` (80 rows) |
| 4 | Breakage 1: renamed `ticks.csv` column, exit nonzero, column named | met by report only | main-session report. Code: `tools/check_runs.py:29-34`, `:265`, `:275`. No saved output (I-5) |
| 5 | Breakage 2: mixed `mock` root makes `analyze.py` exit nonzero | **not met** | no run reported or saved. Code path exists: `tools/analyze.py:38-42`, `:175` (I-1) |
| 6 | `make_report.py --phase mvp1` writes 3 stage reports and `index.html` | met | `results/mock/mvp1/{generate,check,analyze,index}.html` |

## Static acceptance criteria

| Task | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| M1-01 | `pyproject.toml`: `python-downloads = "never"`, numpy and matplotlib only | met | `pyproject.toml:6-12` |
| M1-01 | `.gitignore` ignores `runs/` and `src/experiments/generated/` | met | `../.gitignore:2-3`, `git check-ignore` |
| M1-01 | `mock/runs/`, `prereg/`, `results/` are not ignored | **not met** for `mock/runs/` | `../.gitignore:8` ignores it (D-014). The AC text is stale (I-2) |
| M1-02 | `SCHEMA_VERSION = 1`, Table 3 and Table 4 columns in order | met | `tools/schema.py:24`, `:40-58` against `DESIGN.md:262-277` |
| M1-02 | 7 event names, manifest keys of DESIGN §4 | met | `tools/schema.py:59-60`, `:67-79` against `DESIGN.md:282-293` |
| M1-02 | Per run: 4 files, exact headers, 6000 rows when complete, `mock` constant and equal to manifest | met | `tools/check_runs.py:218-220`, `:29-34`, `:126`, `:138` |
| M1-02 | `metrics` equals last tick row. Runid pattern. `MOCK_` exactly when mock | met | `tools/check_runs.py:141-145`, `:90-95`, `tools/schema.py:87-89` |
| M1-02 | Exit nonzero on failure, prints run, file, column. No column literal in `check_runs.py` | met | `tools/check_runs.py:265`, `:275`. Grep for the 22 column names: no hit |
| M1-03 | Writes only under `mock/runs/`. Other path exits nonzero before writing | met | `tools/make_mock_runs.py:193-195`. Main-session report: `--out runs/x` exit 1 |
| M1-03 | 80 runs, prefix `MOCK_`, `mock` = 1, `"mock": true` | met | `tools/make_mock_runs.py:198-201`, `:79`, `:155`. Sample manifest and tick row read |
| M1-03 | Imports columns from `schema.py`. Fixed generator seed | met by code read | `tools/make_mock_runs.py:18`, `:21-22`, `:35`, `:56`, `:150`. Two-run equality was not demonstrated (I-10) |
| M1-03 | `robots.csv`: one row per robot per second, 20 + d robots | met | d = 0: 12,000 rows. d = 4: 14,400 rows. `tools/make_mock_runs.py:83-106` |
| M1-03 | `wasted_robot_seconds` 0 at d = 0. Loss at d > 0, partial gain with defense | met | `results/mock/summary.csv` (0 nonzero d = 0 rows), `results/mock/g2_stats.csv` |
| M1-04 | `F`, `L`, `G`, `R` as ratio of means. 10,000 paired resamples, 95 % percentile | met | `tools/g2_stats.py:14`, `:41-43`, `:50-51`, `:68` |
| M1-04 | "loss not resolved at d" and no `R(d)` when the `L(d)` interval contains 0. Defense cost reported | met by code read | `tools/g2_stats.py:61-63`, `:55-57`, `tools/analyze.py:146-148`. The unresolved branch never ran on this mock |
| M1-04 | Cell check lists missing and duplicates, keeps the latest complete run, does not stop | met by code read | `tools/analyze.py:45-65`, `:84-87`. Never ran with a missing cell (M2 exit 5 will) |
| M1-04 | Mixing guard stops. Mock to `results/mock/`, real to `results/real/` | met by code read, not demonstrated | `tools/analyze.py:38-42`, `:176` (I-1) |
| M1-04 | Mock chart has "MOCK DATA" in the title and `_MOCK.png`. `summary.csv` one row per run | **partly met** | The title string is set (`tools/analyze.py:159`). The legend covers it in the saved PNG (I-3) |
| M1-05 | Reads saved outputs only. No number typed into the script | met, one low note | `tools/make_report.py:118`, `:157`, `:193-195`. `:113` types "80" into the What text (I-9) |
| M1-05 | One report per stage, 8 fields, one figure, one table | met | `tools/report_html.py:64-76`, the three stage pages |
| M1-05 | `index.html` links every report and uses the theme | met | 3 stage links. `results/assets/theme.css` is byte-equal to `.claude/skills/html-theme/theme.css` |
| M1-05 | A stage with no saved output is reported as skipped, script continues | met by code read | `tools/make_report.py:103-105`, `:122-123`, `:154-156`, `:188-192` |

## MVP ladder checks

| Check | Status | Evidence |
| --- | --- | --- |
| L1 schema is the single contract | PASS, one note | `schema.py` equals DESIGN §4 (columns, order, events, manifest keys, layout check). No real writer exists yet (M2-05 open), so there is no real shape to diff. Note I-8 |
| L2 no pipeline before the flow ran on mocks | ISSUE (timing) | M2-01 to M2-04 were built and smoke-run on 2026-11-10 (`c666a9d`). The mock flow first ran on 2026-11-11 (`9c96d69`). The paths that exist in `src/` now have a mock demonstration. No `RunLogger` or `make_sweep.py` exists yet |
| L3 mock is unmistakable and isolated | ISSUE | Isolated: own folder, `MOCK_` prefix, `mock` flag, `"MOCK"` manifest values, no `mock` reference in `src/`. Not unmistakable: the chart stamp is covered (I-3) |
| L4 a phase opens only when the previous exit is closed | ISSUE | Four M2 tasks are `[x]` before this gate (`PLAN.md:111-132`). Exit 5 has no demonstration (I-1, I-4) |

## Hierarchy checks

| Check | Status | Evidence |
| --- | --- | --- |
| H1 trace | PASS, two stale lines | Mission block in `PLAN.md:7-17` and `DESIGN.md:7-17`. Every task tags `→ M<n>`. Milestones trace to S1, G1, G2. Counters within bounds. Stale lines: I-2, I-6 |
| H2 decisions logged | PASS, minor | D-013 and D-014 exist with a Why line. Evidence cells are not paths (I-7). The early M2 start has no D-row (I-4) |

## Issues

| ID | Severity | Class and route | Where | What | Fix suggestion |
| --- | --- | --- | --- | --- | --- |
| I-1 | blocking | ladder (L4), main session runs it | M1 exit 5, `tools/analyze.py:38-42` | Breakage 2 was never run | Build a scratchpad root with one `"mock": true` and one `"mock": false` manifest. Run `analyze.py` on it. Save the output and exit code under `results/mock/` |
| I-2 | blocking | hierarchy, `product-manager`. DESIGN line to `system-architect` | `PLAN.md:34`, `PLAN.md:63`, `DESIGN.md:389` | Three lines say `mock/runs/` is committed. D-014 ignores it. The M1-01 AC is false as written | Rewrite the two PLAN lines and the DESIGN line to match D-014. State that `make_mock_runs.py` recreates the folder |
| I-3 | blocking | implementation, `developer` | `tools/analyze.py:159-160`, `tools/make_report.py:94-96` | The figure legend sits on the suptitle. "MOCK DATA" is unreadable in `g2_recovered_share_MOCK.png` and `mvp1/generate_fig.png`. Also breaks `rules/figures.md` (no overlap) | Put the title on the axes (`ax.set_title`) and the legend below the plot (`loc="outside lower center"`), or the reverse. Re-run `analyze.py` and `make_report.py`, then view both PNGs |
| I-4 | blocking | ladder (L2, L4), `system-architect` | `PLAN.md:111-132`, commit `c666a9d` | M2 opened before M1 exit closed. Four M2 tasks are done and smoke-run | Architect confirms no M2-01 to M2-04 code depends on a path the mock flow did not cover. pm logs a D-row for the early start. Hold M2-05 onward until M1 closes |
| I-5 | low | hierarchy (evidence), main session | M1 exit 4, M1-03 refusal | Breakage 1 and the `--out` refusal have no saved output. Only the dispatch states them | Save both command outputs with exit codes next to `check_log.txt` (for example `results/mock/breakage_log.txt`) |
| I-6 | low | hierarchy, `product-manager` | `PLAN.md:11`, `PLAN.md:222` | Constraints still says the owner runs multi-seed sweeps (D-013 changed it). The open item on source and decoy centres is closed by DESIGN §4 `layout` | Update both lines surgically |
| I-7 | low | hierarchy, `product-manager` | `DECISIONS.md:22-23` | D-013 and D-014 Evidence cells hold retyped numbers, not paths (`rules/docs.md` §8) | D-014 can cite `results/mock/mvp1/generate.html` (it reports the folder size) |
| I-8 | low | ladder note (L1), `system-architect` | `tools/schema.py:64`, `DESIGN.md:161` | `STATES_DETRACTOR` has no name for the "wait 2 s" step. A new state name in M3 would fail `check_runs.py` and send the slice back to M1 | Decide now: the wait is part of `GO_DECOY`, or add a named state to DESIGN §4 and `schema.py` |
| I-9 | low | implementation, `developer` | `tools/make_report.py:113` | The What text types "80" | Drop the number or build it from `schema.py` counts |
| I-10 | low | implementation note | `tools/make_mock_runs.py:21-22` | Determinism is by code read only. D-014 depends on it | At the next generator run, hash `mock/runs/` before and after and save the two hashes |
| I-11 | low | implementation, `developer` | `tools/analyze.py:168`, `:176` | `--out` lets mock output go to `results/real/` | Refuse an `--out` under `results/real/` when `mock` is true |
| I-12 | low | reasoning note, `system-architect` | `tools/g2_stats.py:61` | A loss interval fully below 0 counts as resolved, and `R(d)` is reported with a negative loss | Decide whether "resolved" needs `L(d)` lower bound > 0 (DESIGN §4.2) |
| I-13 | low | not checked | `results/mock/mvp1/*.html` | No browser render in this review (outside the allowed runs) | Main session renders `index.html` once per `rules/answering.md` §3 |

## To close the gate

1. Fix I-3, then re-run `analyze.py` and `make_report.py`.
2. Run and save breakage 2 (I-1). Save breakage 1 and the refusal output with it (I-5).
3. pm and architect align the three "committed" lines with D-014 (I-2).
4. Architect answers I-4. pm logs the D-row.
5. Second gate review (cycle 2 of 2) reads the new PNGs and the saved breakage logs.
