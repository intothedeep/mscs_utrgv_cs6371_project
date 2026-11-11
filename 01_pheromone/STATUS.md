> Completed items live in `_archive/` (cold storage, do not read unless
> investigating history). This doc holds the active + planned log only.

# Status: 01_pheromone

2026-11-10 project: D-001, D-002, D-003, D-004 (DECISIONS.md)
2026-11-10 design: DESIGN.md draft with Q1 to Q7 resolved (DESIGN.md §9)
2026-11-10 decisions: D-005 to D-012 (decisions/2026-11-10_fable_design_picks.md)
2026-11-10 plan: PLAN.md created, M1 to M3, tasks M1-01 to M3-07 open (PLAN.md)
2026-11-11 M1: mock end-to-end ran (80 runs, check 0 failed, G2 chart) (results/mock/mvp1/index.html)
2026-11-11 decisions: D-013 local multi-seed runs, D-014 mock/runs ignored (DECISIONS.md)
2026-11-11 M1: gate issues I-1..I-13 closed, gates re-run PASS (results/reviews/M1_gate.md, results/reviews/M1_evidence/)
2026-11-11 M2: build clean, smoke run logs 4 files, check 0 failed, analyze lists 79 missing (runs/smoke, results/real/check_log.txt)
2026-11-11 M2: tuning 3 rounds x 3 seeds ran, D-016 freezes round 1 (results/real/tuning/tuning_pick.json)
2026-11-11 M2: keep-A judgement PASS, D-017 (results/real/judgement/verdict.json)
2026-11-11 M2: Qt frames captured headless (autoplay + frame_grabbing), MVP2 report 8 of 8 stages ran (results/real/mvp2/index.html)
2026-11-11 M3: build v2 clean, invariance holds (seed 101 food equal to v1), defense tuning 3 rounds, D-018 freeze (results/real/defense_tuning/defense_pick.json)
2026-11-11 M3: sweep stopped at seed 6 (decoy placement), fixed by D-019, sweep rerun (DECISIONS.md)
2026-11-11 decisions: D-020 decoy-to-decoy gap ≥ 1.0 m, pre-fix sweep to runs/x_sweep_pre_d020/, sweep reruns (DECISIONS.md)
2026-11-11 decisions: D-021 valid-peak reference max(here_entry, θ_on) (DECISIONS.md)
2026-11-11 decisions: D-022 M2 exit 6 by headless Qt frames, fade evidence moves to M3 demo (DECISIONS.md, PLAN.md M2 exit 6)
2026-11-11 decisions: D-023 M3 started before M2 gate closed, kept (DECISIONS.md)
2026-11-11 decisions: D-024 robots rest at the nest boundary, kept as a limit (DECISIONS.md)
2026-11-11 M3: v3 chain rerun, D-025. Sweep 80 of 80 runs, check 0 failed (results/real/check_sweep_log.txt, results/real/g2_stats.csv)
2026-11-11 M3: demo capture d2 def0 21 frames, def1 22 frames. Earlier def1 stop at about tick 983 was frame capture only, sim reached tick 6000 ([diag] Destroy line) (results/real/mvp3/demo/)
