> Completed items live in `_archive/` (cold storage, do not read unless
> investigating history). Split detail, if any, is linked from stubs below;
> a stub's state is the truth if it and the detail disagree.

# Plan: 01_pheromone (pheromone foraging under misleading trails)

## Mission block

- Mission: Keep pheromone foraging swarms trustworthy against false trails as they scale, change and learn. (Fable, owner-delegated, 2026-11-11, D-034)
- Vision: A chart sets our no-ID defense beside Prof. Lu's ID-based defense, each failure explained. (Fable, owner-delegated, 2026-11-11, D-035)
- Constraints: no local training. The main session builds and runs every run locally, one core, sequential (D-002, D-013, D-031, D-044). Agents never build, run or commit.
- G1: By 2026-11-24, log 80 runs with food collected and wasted robot-seconds (measure: logged runs out of 80 = 4 detractor counts x 2 defense states x 10 seeds). (Fable, owner-delegated, 2026-11-10, D-004)
- G2: By 2026-11-28, report recovered loss share for 3 of 3 nonzero detractor counts (1, 2, 4) with 10-seed error bars. (Fable, owner-delegated, 2026-11-10, D-004)
- G3: By 2026-11-28, 3 of 3 run tracks (T-A, T-B, T-D) have a committed `verdict.json`, plus a root-cause memo for each fail. (Fable, owner-delegated, 2026-11-11, D-036). Met 2026-11-12: 3 of 3 run tracks have a `verdict.json`. Every fail or scales-worse has a root-cause memo (D-055, D-056)
- Goals (question-type): [RQ.md](./RQ.md): 0 open, 3 answered (2026-11-12), 1 proposed (D-037)
- S1 → G1, G2: A, floor grid with a virtual sensor (picked: A of A/B/C, Fable owner-delegated 2026-11-10, D-006). Listed alternatives: B (fallback, only if the D-010 judgement fails), C (stretch after G2 only).
- S2 → G3, RQ1 to RQ3: run tracks in order, step 0, T-A, T-B, T-D, then T-E and T-F. Each track pre-registered on its own fresh seed block (Fable, owner-delegated, 2026-11-11, D-038, D-043). Listed alternatives: T-B first, T-D first. T-C not run (D-041).
- M1 → S1: MVP1 shape, mock end-to-end, by 2026-11-13. Exit: TASKS.md "M1 exit". cycle 1/2; recovery 0/2. Review 1 ISSUE, fixes closed, gates re-run PASS (`results/reviews/M1_gate.md` Resolution). Closed
- M2 → S1: MVP2 real slice, 0 detractors, plus the D-010 keep-A judgement, by 2026-11-17. Exit: TASKS.md "M2 exit". cycle 1/2; recovery 0/2. Review 1 ISSUE (`results/reviews/M2_gate.md`). Fixes applied (D-020 to D-025). No re-review yet; M3-08 checks I-1 and I-2
- M3 → S1: MVP3 detractors, defense, 80-run sweep, figures from real logs. Sweep by 2026-11-24, report by 2026-11-28. Exit: TASKS.md "M3 exit". cycle 1/2; recovery 0/2. Sweep done on v3 (D-025). G1 met (80 of 80 runs). G2 measured (D-026). Gate closed by the project-end review (D-061)
- M4 → S1 → Vision: defense v2 lockout, one added arm (D-027, D-032), by 2026-11-21. Exit: `results/real/v2/verdict.json` exists, pass or fail (TASKS.md "M4 exit"). cycle 1/2; recovery 0/2. Verdict FAIL (D-033). Report section done. Gate closed by D-061. Closed
- M5 → S2 → RQ1: T-A, defense v5 confirm-twice x lockout, by 2026-11-17. Exit: `results/real/v5/verdict.json` on seeds 221 to 260, pass or fail, plus a root-cause memo on fail (TASKS.md "M5 exit"). cycle 1/2; recovery 0/2. Verdict PASS for k2t10 (D-051, D-057). 10 of 10 done. Gate closed by D-061. Closed. M5 to M8 opened while the M3 and M4 gates were open. D-061 covers the order (P-7)
- M6 → S2 → RQ2: T-B, ID-based adapted arm, by 2026-11-22. Exit: `results/real/id_arm/verdict.json` on seeds 321 to 360, plus a root-cause memo on fail (TASKS.md "M6 exit"). Kill: no gate-ready code by 2026-11-21. cycle 1/2; recovery 0/2. Verdict "differs" (D-054). 9 of 9 done. Gate closed by D-061. Closed
- M7 → S2 → RQ3: T-D, 20 vs 40 honest robots, by 2026-11-24. Exit: `results/real/scale/verdict.json` on seeds 401 to 430, plus a root-cause memo on fail (TASKS.md "M7 exit"). Kill: M5 or M6 past 2026-11-22, then v3 and off only. cycle 1/2; recovery 0/2. Verdict: v5 scales worse (D-055), root-cause memo done (D-056). 5 of 5 done. Gate closed by D-061. Closed
- M8 → S2 → Vision, G3: T-E table and T-F final report, 2026-11-24 to 2026-11-28. Exit: T-E table, report with one comparison chart and one failure section per failed verdict, G3 check (TASKS.md "M8 exit"). cycle 1/2; recovery 0/2. M8-01 and M8-03 done, G3 check met. Project-end review cycle 1 written (`results/reviews/project_end_review.md`). M8-02 and M8-04 in progress

Design: [DESIGN.md](./DESIGN.md). Decisions: [DECISIONS.md](./DECISIONS.md). Questions: [RQ.md](./RQ.md). Progress: [STATUS.md](./STATUS.md). Track spec: `decisions/2026-11-11_fable_tracks.md`.

## How tasks close

- Format: `[ ]` TODO, `[~]` IN PROGRESS, `[x]` DONE.
- One task = one dispatch. Gate review only, at each milestone exit (no per-task review).
- "Static AC": the developer checks it (file exists, grep, read). Developers never build or run.
- "Gate AC": checked at the gate run. The runner is the main session: 1-seed smoke (D-002, D-012), multi-seed (D-013, D-031, D-044), headless Qt frames (D-022).
- No `*.test.*` files. Behavior is checked by deliberate breakage at the gate. Breakage copies go to the session scratchpad, never into the repo.
- Every gate run writes its stage reports (fields: `.claude/CLAUDE.md` "System build phasing").
- Every run track ends with a committed `verdict.json`. A fail adds a root-cause memo (G3, D-036).

## Fixed paths (all tasks use these)

| What | Path | Git |
| --- | --- | --- |
| Mock runs | `mock/runs/` | ignored (D-014, regenerated by `make_mock_runs.py`) |
| Smoke runs (1 seed) | `runs/smoke/` | ignored |
| Pheromone tuning runs | `runs/tuning/` | ignored |
| Keep-A judgement runs | `runs/judgement/` | ignored |
| Defense tuning runs | `runs/defense_tuning/` | ignored |
| 80-run sweep | `runs/sweep/` | ignored |
| Defense v2 tuning runs (M4-04) | `runs/tuning_v2/` | ignored |
| Defense v2 confirmation, picked `t_lock` | `runs/sweep_v2/` | ignored |
| Defense v2 confirmation control, `t_lock` 0 | `runs/sweep_v2_lock0/` | ignored |
| Defense diagnostics (M4-02) | `results/real/defense_diagnostics.csv` | committed |
| Defense v2 pick | `results/real/tuning_v2/pick.json` | committed |
| Defense v2 verdict | `results/real/v2/verdict.json` (control: `results/real/v2_lock0/`) | committed |
| v2 and v3 root-cause memo | `results/real/failure_analysis.md` | committed |
| Defense v5 outputs (M5) | `results/real/v5/` (`step0_kill.md`, `verdict.json`, `root_cause.md`) | committed |
| ID arm outputs (M6) | `results/real/id_arm/` | committed |
| Scalability outputs (M7) | `results/real/scale/` | committed |
| T-E comparison table (M8-01) | `research/cost_of_trust.md` Table 1 | committed |
| Pre-registrations | `prereg/` (M4: `defense_v2_lockout.md`; M5 to M7: `defense_v5.md`, `id_arm.md`, `scale.md`) | committed |
| Pheromone pick (D-007) | `results/real/tuning/tuning_pick.json` | committed |
| Keep-A verdict (D-010) | `results/real/judgement/verdict.json` | committed |
| Defense candidates (D-011) | `prereg/defense_candidates.json` | committed |
| Defense pick (D-011) | `results/real/defense_tuning/defense_pick.json` | committed |
| Stage reports and pages | `results/<mock\|real>/<phase>/` | committed |

- M5 to M7 run roots are set by the code task of each track (M5-03, M6-03, M7-01). This table then follows the code.

### Task list: split out (2026-11-11)

> Current state (2026-11-12): M1 to M7 tasks done. Gates M3 to M7 closed by the project-end review (D-061). Total 0 open, 0 in progress. Project closed 2026-11-12. <!-- see TASKS.md -->
> Gating fact: the main session closes M8-02 and M8-04 after the report fix and the render check. M8-04 ran before M8-02 closed. D-061 covers the order (P-7).
> Detail: [TASKS.md](./TASKS.md)

## Open items for the architect

- ~~Source and decoy centres have no field in DESIGN §4.~~ Resolved: DESIGN §4 `layout` (2026-11-10).
- ~~M4 kill path: if tuning picks `t_lock` 0, no confirmation runs.~~ Moot: tuning picked 10 s, verdict exists (D-033).
- ~~M4 names not in the spec are pm proposals.~~ Resolved: the code set them (`tools/v2_common.py`), this plan follows.
- DESIGN Table 5 says MVP2 by 2026-11-18. This plan uses 2026-11-17 (D-010 deadline).
- ~~DESIGN Table 5 gives the MVP2 Qt run to the main session. The owner runs the Qt demo (it needs a display).~~ Resolved: the main session grabs MVP2 Qt frames headless (D-022). Headless runs are the main session's (D-013).
- ~~DESIGN §3.2 gives no LED color for END_SEARCH.~~ Resolved: DESIGN Table 2a, magenta (2026-11-10).
- M5 to M7 output folder names (`results/real/v5/`, `id_arm/`, `scale/`) and prereg names are pm proposals. The code tasks may set others.
- DESIGN.md mission block still quotes the D-004 Mission and Vision. The architect updates it from this block (D-034, D-035).
