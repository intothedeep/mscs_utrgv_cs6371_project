# Fable decision: revised mission, vision, tracks M5 to M8 (2026-11-11, owner-delegated)

Inputs: research/lu_lineage.md, research/emeans.md, results/real/failure_analysis.md, PLAN.md, DECISIONS.md D-001..D-033.

## Decisions
| ID | Decision | Why | Rejected |
| --- | --- | --- | --- |
| D-034 | Mission: "Keep pheromone foraging swarms trustworthy against false trails as they scale, change and learn." Supersedes the D-004 Mission | Adds Prof. Lu's 3 future-work words (TAROS p. 317): scalability, dynamic environments, machine learning | Keep the old line (no tie to the Lu line), name a method in it (it would finish) |
| D-035 | Vision: "A chart sets our no-ID defense beside Prof. Lu's ID-based defense, each failure explained." Supersedes the D-004 Vision | The old line needs a win. Owner: success or fail does not matter | Keep "winning back lost food" (not met with v3 or v2) |
| D-036 | G1, G2, D-026 stay. Add G3: by 2026-11-28, 3 of 3 run tracks have a committed verdict.json, plus a root-cause memo for each fail | Vision, owner rule "if we fail we need to find why" | Effect-size goal (rejected in D-004) |
| D-037 | RQ1 to RQ3 (below). A negative answer closes each | Mission, G3 | Numeric win thresholds for the comparison |
| D-038 | Order: step 0 housekeeping, M5 = T-A, M6 = T-B, M7 = T-D, M8 = T-E + T-F. Each cycle 0/2, recovery 0/2 | G3. Fix the measured root cause first, then compare against the best no-ID arm | T-B first, T-D first |
| D-039 | T-A = defense v5: confirm-twice (k = 2, fixed) x lockout (t_lock 0 or 10 s), a 2 x 2 on one seed block | RQ1. Only a 2 x 2 shows the lockout share | v5 as one arm, tune k, options B and D |
| D-040 | T-B = an ID-based arm adapted from TAROS 2024 to the grid. Called "adapted arm", never "replication". Supersedes the D-004 DBSCAN rejection, now as RQ2 | RQ2, Vision | Faithful waypoint replication (8 person-days), skip |
| D-041 | T-C (ICCCR quarantine) is not run. It becomes a T-E row and future work | G3 date. Masks already cover the source centre in 66 % of wrong suspects. ICCCR full text unread | Run as a third arm |
| D-042 | T-D = scalability only: 20 vs 40 honest, same 5 x 5 m arena, 10 % detractors. Dynamic food is future work | RQ3, Mission "scale". Doubled density tests the crowding root cause | Dynamic food (needs a new food model), scaled arena (new tuning) |
| D-043 | Seed blocks, each used once: T-A check 201-210, T-A confirm 221-260, T-B check 301-310, T-B confirm 321-360, T-D 401-430. Spent: 1-30, 101-116 | G3, measurement rule | Reuse 11-30, 10 or 20 seeds (10 seeds hid a -4.73 cost) |
| D-044 | Main session runs all M5 to M7 runs locally, one core, sequential | Constraints | Cluster |
| D-045 | e-means is not used. DBSCAN (eps, minPts = 2) stays for T-B | RQ2. e-means needs k and has no noise label | e-means |

## RQs (Fable, owner-delegated)
- RQ1: Does a second independent failure before marking remove the d = 0 cost and keep G(2) above 0?
- RQ2: On one grid, one attack and one seed block, how do the no-ID defense and the ID-based defense differ in food and false positives?
- RQ3: Do per-robot gain and d = 0 cost hold from 20 to 40 honest robots at 10 % detractors?

## Timeline
step 0 (11-12) -> M5 T-A (11-13..17) -> M6 T-B (11-14..22) -> M7 T-D (11-23..24) -> M8 T-E table, T-F report (11-24..28)
Every run track: research -> design -> plan -> code -> prereg commit -> run -> verdict.json -> failure_analysis.py -> root-cause memo if fail.

## M5 = T-A, defense v5 (RQ1, G3), ends 2026-11-17
- Step 0 (saved files only): from defense-off logs (seeds 11-30), same-robot repeat failures per source at d = 0, and time to the second failure per decoy at d = 2.
- Kill before code: predicted active wrong points at d = 0 above 7.2 per run (half of 14.45). Then switch to A' = "a pickup within r_merge clears a pending point".
- Invariance: v5 with k = 1 equals v4 food on 2 saved cells.
- Mechanism check, seeds 201-210, (0,on) and (2,on): sus_cls_src, sus_cls_dec, reported, no pick.
- Metric: G(2) = F(2, v5) - F(2, off), seeds 221-260, paired bootstrap 10,000, 95 %.
- Threshold: G(2) lower bound > 0.
- Contrast: 2 x 2 (k 1 or 2, t_lock 0 or 10) plus off, d = 0,1,2,4. 800 runs. Report both main effects at d = 0 and d = 2.
- Failure: G(2) interval includes 0, or the d = 0 cost upper bound < 0.
- Expected: d = 0 cost shrinks. G(2) may drop (two visits per decoy). A split result is likely.

## M6 = T-B, ID-based adapted arm (RQ2, Vision), ends 2026-11-22
- Research: re-read the TAROS defense section only.
- Design: shared trail store in the loop functions. DBSCAN on trail ends (minPts 2, eps frozen before runs). Creator-ID graph. Travel-time check. 5 strikes isolate a creator. Reintegration on a late pickup. Isolation log as a sidecar file, schema.py unchanged.
- Arm check, seeds 301-310: does the arm isolate detractors at d = 2?
- Metric: delta = F(2, ID arm) - F(2, best no-ID arm), seeds 321-360, same bootstrap.
- Threshold: interval excludes 0 = "differs", else "not resolved". No win line.
- Contrast: off, v3, v5, ID arm x d = 0,1,2,4. 640 runs. Also honest robots isolated per run.
- Failure: fewer than 1 of 2 detractors isolated by run end in most seeds -> "adapted arm did not function".
- Kill: no gate-ready code by 2026-11-21 -> T-B becomes a T-E row and future work.
- Expected: ID arm gains more at d >= 1. It may isolate honest robots at d = 0.

## M7 = T-D, scalability (RQ3, Mission), ends 2026-11-24
- No new defense code. Frozen values, not re-tuned at 40 (stated limit).
- Metric: per-robot gain G/N at 10 % detractors (d = 2 at N = 20, d = 4 at N = 40), seeds 401-430.
- Threshold: interval of the N=40 minus N=20 difference excludes 0 = "scales worse or better".
- Contrast: N 20/40 x d 0/10 % x off, v3, best arm. 360 runs. Also wrong source suspects per robot.
- Failure: F(0, off) per robot at N = 40 below half of N = 20 -> "confounded by congestion".
- Kill: M5 or M6 slips past 2026-11-22 -> run v3 and off only.

## M8 = T-E + T-F (Vision), 2026-11-24 to 11-28
- T-E: one table, no runs. Rows: blockchain, TAROS, ICCCR, cautionary pheromone, v3, v5, ID arm. Columns: messages, IDs, shared store, per-robot memory, measured d = 0 cost (ours only).
- T-F: headline stays v3 (D-026). One comparison chart. One failure section per failed verdict. Future work: dynamic food, a learned suspect test, quarantine regions.

## Reading guide (in order)
1. Hecker, Moses 2015, "Beyond pheromones" (Swarm Intelligence): the CPFA honest baseline of the line.
2. Lu, Hecker, Moses 2016, MPFA (IROS): Prof. Lu's first step, why one nest does not scale.
3. Aswale et al. 2022, "Hacking the Colony" (AAMAS): the attack we copy, and a defense with no IDs.
4. Luna, Lu 2024, quarantine (ICCCR): his first defense, block the bait not the robot. Full text needed.
5. Luna, Lu 2024, detection and mitigation (UR): DBSCAN on trails first appears. Full text needed.
6. Luna, Lu 2024, robust mitigation (TAROS): the method T-B adapts, and future work on p. 317.
7. Strobel et al. 2018, Byzantine robots + blockchain (AAMAS): the high-cost end of the T-E table.
