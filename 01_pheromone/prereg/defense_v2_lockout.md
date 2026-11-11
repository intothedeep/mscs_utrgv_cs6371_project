# Pre-registration: defense v2, FOLLOW lockout (D-027 to D-032)

Commit this file before the first v2 tuning run (`rules/measurement.md` 1). Do not edit it after.
Spec: `decisions/2026-11-11_fable_defense_v2.md`. Code version v4. Other defense values stay at D-018.
This is a post-hoc design (it follows the null v3 result, D-026), so it is confirmed on new seeds.

## Tuning (picks `t_lock`)

| Line | Value |
| --- | --- |
| Metric | Seed mean of `food_collected(d=2, defense on)` + `food_collected(d=0, defense on)`, seeds 107 to 116. One metric only. |
| Threshold | The highest mean wins. No margin. A tie goes to the smaller `t_lock`. |
| Contrast | `t_lock` 0 (v3 behavior), 5, 10, 20 s. 4 values x 2 cells x 10 seeds = 80 runs in `runs/tuning_v2/`. |
| Failure condition | Tuning picks `t_lock` 0. Then stop, run no confirmation, and report v2 as null. |

## Confirmation (judges v2)

| Line | Value |
| --- | --- |
| Metric | `G(2) = F(2, on) - F(2, off)` at the picked `t_lock`, seeds 11 to 30. Paired percentile bootstrap, 10,000 resamples, 95 % interval (`tools/g2_stats.py`). |
| Threshold | The lower bound of the `G(2)` interval is above 0. |
| Contrast | Main: v2 on against v2 off. Attribution: picked `t_lock` against `t_lock` 0 at (d=2, on), with its interval. d = 1 and d = 4 are reported only. |
| Failure condition | The `G(2)` interval includes 0, or the upper bound of the d = 0 cost interval `F(0, on) - F(0, off)` is below 0. Then v2 is reported as null. |

## Seeds and runs

| Item | Value |
| --- | --- |
| Tuning seeds | 107 to 116, never used for confirmation |
| Confirmation seeds | 11 to 30, used once |
| Confirmation roots | `runs/sweep_v2/` (picked `t_lock`, 160 runs), `runs/sweep_v2_lock0/` (`t_lock` 0, 160 runs). Same v4 code, 8 cells x 20 seeds each |
| Gate cycles | 2. End date 2026-11-21 |

## Kill rule

- Tuning picks 0: stop without confirmation (`tools/confirm_v2.py` refuses to run).
- Seeds 11 to 30 are used once. A rerun only fills missing cells.
- The invariance check passes first: v4 with `t_lock` 0 equals the saved v3 `food_collected` of `d2_def1_s1` and `d0_def0_s1` (`CHANGELOG.md`). If it fails, stop and report.

## Tools

- Tuning: `tools/make_tuning_v2.py --run`, then `tools/tuning_v2_pick.py` writes `results/real/tuning_v2/pick.json`.
- Confirmation: `tools/confirm_v2.py --run`, then `tools/judge_v2.py` writes `results/real/v2/verdict.json` with the sha256 of `judge_v2.py`.
- One core, sequential, 300 s per run (D-013, D-031).
- The expected ceiling is about 5 food, `R(2)` about 0.15 (estimate, spec item 13). The pass probability is not high.
