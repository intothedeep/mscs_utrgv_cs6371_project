# Pre-registration: ID-based adapted arm (T-B, D-040, D-043, D-045, D-048)

Commit this file before the first check or confirm run (`rules/measurement.md` 1). Do not edit it after.
Fill the three lines below first (the tools stop on a placeholder), then commit.
Spec: `decisions/2026-11-11_fable_tracks.md` "M6 = T-B". Design: `DESIGN_M6.md`. Code version v6. Answers RQ2.
Name: "adapted arm", never "replication" (D-040).

## Frozen values (read by `tools/v6_common.py`)

- Best no-ID arm: k1t10
- Margin: 5.4
- Eps: 0.3

Other frozen values (DESIGN_M6 Table 3): minPts 2, speed 0.10 m/s, late-return radius 0.5 m, peak-match radius 0.5 m, feedback gain 0.5, isolation 120 s, 5 strikes, record expiry 339 s. Never tuned on seeds 301 to 360.

## Confirmation (judges RQ2)

| Line | Value |
| --- | --- |
| Metric | Delta = F(2, id) - F(2, best no-ID arm), seeds 321 to 360. F = `food_collected`. Paired percentile bootstrap on seed, 10,000 resamples, 95 % interval (`tools/g2_stats.py`) |
| Threshold | The interval excludes 0 = "differs". Else "not resolved". No win line |
| Contrast | off, v3, k1t10 (best no-ID arm, D-050, D-052), v5 (the M5 primary arm k2, t10), id x d 0, 1, 2, 4 x 40 seeds = 800 runs, one run root per arm. Also detractors and honest robots isolated per run |
| Failure condition | More than 20 of 40 seeds at d = 2 with no detractor isolated before run end (an `isolate` event in `defense_log.csv`, D-048 D4) = "adapted arm did not function". It wins over the other two words. Then the root-cause memo (M6-08) runs |

## Seeds and runs

| Item | Value |
| --- | --- |
| Smoke | Seed 900, d = 2, one run per arm, `runs/m6_smoke/`. Outside every block, report only (D-048 D6) |
| Arm check | Seeds 301 to 310, (d 2, id) and (d 0, id, report only), `runs/m6_check/id/`. Detractors isolated per run. No pick |
| Confirmation | Seeds 321 to 360, used once, `runs/m6_confirm/{off,v3,v5,id}/` |
| Spent, never reused | 1 to 30, 101 to 116, 201 to 260 |
| Invariance | `runs/invariance_v6/`: off d0 s11, v3 d0 s11, v3 d2 s11 against saved runs, byte equal CSV files (`CHANGELOG.md`) |
| Gate cycles | 2. End date 2026-11-22 |

## Order and kill

- Invariance passes before the first M6 run. A mismatch stops M6 and goes to `recover`.
- This file is committed before the first `runs/m6_check/` run. `tools/confirm_v6.py` refuses otherwise, and when the margin or best arm line is a placeholder.
- Seeds 301 to 360 are used once. A rerun only fills missing runs.
- Kill: no gate-ready code by 2026-11-21. Then T-B becomes a T-E row and future work.

## Tools

- Runs: `tools/confirm_v6.py --stage invariance|smoke|check|confirm --run`. One core, sequential, 300 s per run (D-013, D-031, D-044).
- Arm table: `tools/v6_arm_table.py` writes `results/real/id_arm/arm_check.csv`.
- Judge: `tools/judge_v6.py` writes `results/real/id_arm/verdict.json`, `contrast.csv`, `isolation.csv` with the sha256 of `judge_v6.py`.
- Expected (`DESIGN_M6.md` section 8 R1): at d = 0 the arm may isolate honest robots.
