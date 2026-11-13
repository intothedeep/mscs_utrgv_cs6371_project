# Pre-registration: scalability 20 vs 40 honest robots (T-D, D-042, D-043)

Commit this file before the first confirm run (`rules/measurement.md` 1). Do not edit it after.
Spec: `decisions/2026-11-11_fable_tracks.md` "M7 = T-D". Code version v6, no new defense code. Answers RQ3.
Frozen values stay at the D-018 and D-033 freeze (`sweep_plan.frozen_values()`). They are not re-tuned at N = 40. This is a stated limit.

## Frozen values (read by `tools/v7_common.py`)

- Best arm: v5

The best arm is named here by rule, before M6 reports: the M5 primary arm k2t10 (code name `v5`: confirm_k 2, t_lock 10 s, D-051). Why: it is the only arm with no d = 0 cost (D-051). Nobody picks it after seeing M6. The M6 arm k1t10 (D-052) and the ID arm are not run at N = 40.

## Confirmation (judges RQ3)

| Line | Value |
| --- | --- |
| Metric | Per arm in v3, v5 and seed s: g_N(s) = (F(d10, arm, s) - F(d10, off, s)) / N. d10 = 2 at N = 20 and 4 at N = 40 (10 % detractors). F = `food_collected`. The metric is D = mean of g_40(s) - g_20(s) over seeds 401 to 430. Seed s at N = 20 is paired with seed s at N = 40. Paired percentile bootstrap on seed, 10,000 resamples, 95 % interval (`tools/g2_stats.py`) |
| Threshold | The D interval excludes 0: "scales better" (above 0) or "scales worse" (below 0). Else "not resolved". One word per arm. No win line |
| Contrast | N 20, 40 x d 0 and d10 x off, v3, v5 x 30 seeds = 360 runs, one run root per arm and N. Also reported, no pass or fail: the d = 0 cost per robot (F(0, arm) - F(0, off)) / N with the same N = 40 minus N = 20 interval, and wrong source suspects per robot (`suspect_add` near a source, `failure_analysis.run_metrics` key `sus_cls_src`, divided by N) |
| Failure condition | Mean F(0, off) / N at N = 40 below half of mean F(0, off) / N at N = 20 = "confounded by congestion". It wins over the arm words. Then the root-cause memo (M7-04) runs |

## Arms and N (3 arms x 2 N x 2 d-levels x 30 seeds = 360 runs)

| Arm | defense | confirm_k | t_lock (s) | Role |
| --- | --- | --- | --- | --- |
| off | 0 | 1 (inert) | 0 (inert) | baseline for G and the d = 0 cost |
| v3 | 1 | 1 | 0 | headline arm (D-026) |
| v5 | 1 | 2 | 10 | best arm by rule (above) |

| N honest | d = 0 | d10 | Robots at d10 |
| --- | --- | --- | --- |
| 20 | 0 | 2 | 22 |
| 40 | 0 | 4 | 44 |

Same 5 x 5 m arena, same nest start area (x -2 to -1 m, y -2 to 2 m). The honest block of the template is changed by `make_sweep.py --honest` and nothing else (`src/` is unchanged). The start density doubles with N, which is the test. `n_honest` is recorded in each manifest.

## Seeds and runs

| Item | Value |
| --- | --- |
| Smoke | Seed 900, arms x N x d10, `runs/m7_smoke/<arm>_n<N>/` (6 runs). Outside every block, report only. Shows that 44 robots start in the nest area |
| Confirmation | Seeds 401 to 430, used once, `runs/m7_scale/<arm>_n<N>/` |
| Spent, never reused | 1 to 30, 101 to 116, 201 to 260, 301 to 360 |
| Gate cycles | 2. End date 2026-11-24 |

## Order and kill

- This file is committed before the first confirm run. `tools/confirm_v7.py` refuses otherwise, and when the best arm line is not `v5`.
- Seeds 401 to 430 are used once. A rerun only fills missing runs.
- Judge: `tools/judge_v7.py` writes `results/real/scale/verdict.json` (with the sha256 of `judge_v7.py`) and `contrast.csv`.
- Kill: M5 or M6 slips past 2026-11-22. Then run v3 and off only. The pm writes the D-row first.
- Expected: per-robot gain may shrink at N = 40 (crowding at the sources). A split result is possible.
