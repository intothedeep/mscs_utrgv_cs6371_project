> Completed items live in `_archive/` (cold storage, do not read unless
> investigating history). Split detail, if any, is linked from stubs below;
> a stub's state is the truth if it and the detail disagree.

# Plan: 02_informed_search_assigned (informed search for CPFA swarms)

## Mission block

- Mission: Find ground no robot has searched, so the swarm collects more in 12 minutes. Keep server cost small as swarms and arenas grow. (Fable, owner-delegated, 2026-11-12, D-003)
- Vision: One page shows 3-distribution box plots with % improvement over original CPFA and its interval. A query-cost vs arena-size chart sits beside the student grid. Each failure has a cause. (Fable, owner-delegated, 2026-11-12, D-004)
- Constraints:
  - Local runs: one core, `timeout`, sequential, main session only (D-002). Agents never build, run or commit.
  - Vendor code `vendor/Collision_Free_CPFA/` at `9480f2e` is never edited (D-001).
  - Switch off (`InformedSearch="0"`) gives runs identical to the vendor build (DESIGN §4.3).
  - Criteria are pre-registered before the run. They never change after a run (`rules/measurement.md` §1).
- G1: By 2026-11-21, benchmark verdict. Measure: at 80 m and 400,000 points, option B median operations per query ≤ 1 % of a flat-list scan, and below the student grid at the same resolution. Memory line per DESIGN §5.2. (Fable, owner-delegated, 2026-11-12, D-005)
- G2: By 2026-11-27, 300 evaluation runs done. Measure: runs passing checks out of 300, plus a per-distribution improvement table. (Fable, owner-delegated, 2026-11-12, D-005)
- G3: By 2026-11-27, a committed `verdict.json`, plus a root-cause memo for each distribution with no confirmed improvement. (Fable, owner-delegated, 2026-11-12, D-005)
- Goals (question-type): [RQ.md](./RQ.md): 3 open (D-005)
- S1 → G1, G2, G3: option B, region quadtree with availability summaries and reservation. Option A (fine grid) stays as fallback behind the same interface (picked: B of A/B/C, Fable owner-delegated 2026-11-12, D-010). Listed alternatives: A, C.
- M1 → S1: MVP1 shape, mock end-to-end, by 2026-11-14. Exit: TASKS.md "M1 exit". cycle 1/2; recovery 0/2
- M2 → S1 → RQ1: MVP2 baseline slice (invariance, headroom, S1 noise, 90 runs), by 2026-11-18. Exit: TASKS.md "M2 exit". cycle 1/2; recovery 0/2
- M3 → S1 → G1, RQ2: MVP3 map and benchmark, `qmap` smoke runs, by 2026-11-21. Exit: TASKS.md "M3 exit". cycle 1/2; recovery 0/2
  - Kill R6: A and B equivalence fails on 2026-11-21 → ship A, D-row.
- M4 → S1 → G2: S2 tuning (270 runs), freeze, S3 pre-registration committed, by 2026-11-23. Exit: TASKS.md "M4 exit". cycle 1/2; recovery 0/2
  - Kill R10: M3 not done by 2026-11-22 → S2 skipped, start values frozen, D-row.
- M5 → S1 → G2, G3, RQ1, RQ3: S3 (300), S4 (300), S5 if time, verdict, report, by 2026-11-27. Exit: TASKS.md "M5 exit". cycle 1/2; recovery 0/2
  - Kill R7: S4 median run > 60 s → S4 reduced to 20 seeds, D-row.

Design: [DESIGN.md](./DESIGN.md). Decisions: [DECISIONS.md](./DECISIONS.md). Questions: [RQ.md](./RQ.md). Progress: [STATUS.md](./STATUS.md). Code facts: `research/baseline_code_map.md`.

## How tasks close

- Format: `[ ]` TODO, `[~]` IN PROGRESS, `[x]` DONE.
- One task = one dispatch. Gate review only, at each milestone exit (no per-task review).
- "Static AC": the developer checks it (file exists, grep, read). Developers never build or run.
- "Gate AC": checked at the gate run. The runner is the main session (D-002).
- Python tool form: `OMP_NUM_THREADS=1 timeout 300 uv run python tools/<script> ...`.
- Run drivers `run_argos.py` and `tune.py` are exempt from the 300 s cap (S1 alone takes about 540 s). Form: `OMP_NUM_THREADS=1 uv run python tools/run_argos.py <root>`. Each `argos3 -n -c run.argos` call has its own `timeout 120`, one run at a time.
- No `*.test.*` files. Behavior is checked by self-check modes and deliberate breakage at the gate. Breakage copies go to the session scratchpad, never into the repo.
- Every measured set has its pre-registration file committed and a D-row written before its first run.
- Every gate run writes its stage reports (fields: `.claude/CLAUDE.md` "System build phasing").

## Fixed paths (all tasks use these)

| What | Path | Git |
| --- | --- | --- |
| Vendor clone, `9480f2e` | `vendor/Collision_Free_CPFA/` | ignored (D-001) |
| Vendor build | `build_baseline/` | ignored |
| Our tracked source copy | `src/` | committed |
| Our diff vs vendor | `patches/ours.diff` | committed |
| Our build | `build_ours/` | ignored (M1-01 adds it) |
| Base experiment file | `vendor/Collision_Free_CPFA/experiments/Random_CPFA_r24_tag256_10by10.xml` (`xml10`) | ignored, read only |
| Python tools | `tools/` | committed |
| Mock runs | `mock/runs/<set>/<runid>/`, runid starts `MOCK_` | ignored (M1-01 adds it) |
| Real runs | `runs/<set>/<runid>/`, sets `S0det`, `S0`, `S1`, `SMK`, `S0v2`, `S2` to `S5` | ignored |
| Mock criteria file (M1 only) | `prereg/S3_eval_MOCK.json` | committed |
| Per-run summary (single contract) | `results/<mock\|real>/runs.csv` | committed |
| Stage reports and pages | `results/<mock\|real>/<phase>/` | committed |
| Benchmark outputs | `results/real/bench/` (`bench.csv`, `fig_cost_vs_arena.png`, `G1_verdict.json`) | committed |
| Headroom readings (S1) | `results/real/S1/headroom.json` | committed |
| Invariance verdict (S0, M3 re-run S0v2) | `results/real/S0/invariance.json`, `results/real/S0v2/invariance.json` | committed |
| Tuning table and pick (S2) | `results/real/S2/tuning_table.csv`, `pick.json` | committed |
| Evaluation outputs (S3, S4, S5) | `results/real/<set>/` (`improvement.csv`, `verdict.json`, figures) | committed |
| Root-cause memos | `results/real/<set>/root_cause_<distribution>.md` | committed |
| Pre-registrations | `prereg/` (`S0_invariance.json`, `S1_headroom.json`, `G1_bench.json`, `S2_tuning.json`, `S3_eval.json`, `S4_sens.json`, `S5_ablation.json`) | committed |
| Code version ledger | `CHANGELOG.md` | committed |

- Distribution codes in `xml10` `FoodDistribution`: 0 random, 1 clustered, 2 powerlaw (`lf.cpp:234-236`, `lf.cpp:336-342`).
- Run id: `<YYYYMMDD-HHMMSS>_<arm>_<dist>_s<seed>` (DESIGN §6.4).

### Task list: split out (2026-11-12)

> Current state (2026-11-12): 0 of 5 milestones closed. 49 open (M1 10, M2 11, M3 10, M4 9, M5 9), 0 in progress. <!-- see TASKS.md -->
> Gating fact: M1 opens first. M3-01 to M3-03 (pure code) may start during M1 and M2 (DESIGN §7).
> Detail: [TASKS.md](./TASKS.md)

## Open items for the architect

- DESIGN §6.7 still recommends SciPy (option 1). D-011 picked numpy only. The architect updates §6.7.
- DESIGN §0 holds draft goal IDs. It should now quote this mission block.
- G1 wording: this block says "at 80 m". DESIGN §5.2 lines 1 and 2 say "80 m and larger". The main session picks the reading and logs a D-row before M3-04.
- The `build_baseline/` configure command is not written down. The main session passes it to M2-01.
- No design unit builds `runs.csv` from run folders. pm proposal: `tools/collect_runs.py`, used for mock and real (M1-04).
- The vendor build writes no `queries.csv` or `points.csv`. pm proposal: the harness writes them header-only for `arm = vendor`, and `check_runs.py` accepts header-only only for that arm (M1-03, M2-05).
- DESIGN Table 7 says "300 mock runs pass". The M1 mock writes S1 (90) and S3 (300), so the M1 exit counts 390.
- The M1 cycle has no mock benchmark stage. The M1 report lists the cost chart as "skipped, not built yet". A mock `bench.csv` can be added if the architect wants the chart shape proved in MVP1.
- Table 8 headroom readings and Table 9 kill conditions have no D-row yet. M2-07 pre-registers Table 8. pm writes the D-row before the S1 run.
