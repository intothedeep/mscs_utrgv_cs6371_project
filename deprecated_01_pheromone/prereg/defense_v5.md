# Pre-registration: defense v5, confirm-twice x lockout (D-039, D-043, D-046, D-047)

Commit this file before the first v5 run, except the invariance rerun (`rules/measurement.md` 1). Do not edit it after.
Spec: `decisions/2026-11-11_fable_tracks.md` "M5 = T-A". Design: `DESIGN_M5.md`. Code version v5. Answers RQ1.
Other defense values stay at the D-018 freeze (`sweep_plan.frozen_values()`).
Kill check passed: build option A (k = 2), not A' (D-046).

## Confirmation (judges v5, answers RQ1)

| Line | Value |
| --- | --- |
| Metric | G(2) = F(2, k2t10) - F(2, off), seeds 221 to 260. F = `food_collected`. Paired percentile bootstrap on seed, 10,000 resamples, 95 % interval (`tools/g2_stats.py`) |
| Threshold | The lower bound of the G(2) interval is above 0 |
| Contrast | Main: k2t10 against off at d = 0, 1, 2, 4. The 2 x 2 main effects below at d = 0 and d = 2. G of the other 3 arms is reported only |
| Failure condition | The G(2) interval includes 0, or the upper bound of the d = 0 cost F(0, k2t10) - F(0, off) is below 0. Then v5 is reported as null and the root-cause memo (M5-09) runs |

## Arms (5 arms x d 0, 1, 2, 4 x 40 seeds = 800 runs)

| Arm | defense | confirm_k | t_lock (s) | Role |
| --- | --- | --- | --- | --- |
| off | 0 | 1 (inert) | 0 (inert) | baseline for G and the d = 0 cost |
| k1t0 | 1 | 1 | 0 | v4 = v3 behavior |
| k1t10 | 1 | 1 | 10 | v2 lockout |
| k2t0 | 1 | 2 | 0 | confirm only |
| k2t10 | 1 | 2 | 10 | primary arm, judged |

Why k2t10 is primary: RQ1 asks for k = 2 with the decoy side kept. The lockout is the only resolved decoy-side gain (+3.25 food at d = 4). 10 s is the v2 tuning pick, the only nonzero value confirmed on 20 seeds (D-033). No new tuning.

## Main effects (reported, no pass or fail)

Per seed s and d in 0, 2, with F on the on-arms:

```
E_k(d, s) = 1/2 [F(k2t0) - F(k1t0)] + 1/2 [F(k2t10) - F(k1t10)]
E_t(d, s) = 1/2 [F(k1t10) - F(k1t0)] + 1/2 [F(k2t10) - F(k2t0)]
I(d, s)   = [F(k2t10) - F(k1t10)] - [F(k2t0) - F(k1t0)]
```

Each is the mean over 40 seeds with the same paired bootstrap (`paired_diff_interval`).

## Seeds and runs

| Item | Value |
| --- | --- |
| Mechanism check seeds | 201 to 210. Arms k2t10 and its twin k1t10, cells (d 0, on) and (d 2, on), 40 runs in `runs/v5_check/`. Reported only, no pick |
| Confirmation seeds | 221 to 260, used once, 800 runs in `runs/v5_confirm/` |
| Spent, never reused | 1 to 30, 101 to 116 |
| Invariance | `runs/invariance_v5/`, saved v4 cells `20261111-115700_d0_def1_s11` and `20261111-115700_d2_def1_s11` rerun on v5 with confirm_k 1, t_lock 0 |
| Gate cycles | 2. End date 2026-11-17 |

## Kill rule and order

- Invariance passes before the first M5 run: `food_collected` equal, `events.csv` row counts equal, params equal except `confirm_k`. A mismatch stops M5 and goes to `recover`.
- This file is committed before the first `runs/v5_check/` run. `tools/confirm_v5.py` refuses otherwise.
- Seeds 221 to 260 are used once. A rerun only fills missing cells.
- Confirm order: off and k2t10 first, then the other 3 arms. The judge needs all 800 runs.

## Tools

- Runs: `tools/confirm_v5.py --stage invariance|check|confirm --run`. One core, sequential, 300 s per run (D-013, D-031, D-044).
- Mechanism: `tools/v5_mechanism.py` writes `results/real/v5/mechanism.csv` and `mechanism.md`.
- Judge: `tools/judge_v5.py` writes `results/real/v5/g2_stats.csv` and `verdict.json` with the sha256 of `judge_v5.py`.
- Expected (D-046 and DESIGN_M5 section 7): the d = 0 cost shrinks. G(2) may drop, since each robot needs two visits per decoy. A split result is likely and counts as a fail.
