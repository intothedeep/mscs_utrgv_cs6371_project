# Slide outline: pheromone foraging under misleading trails (10-minute talk, 12 slides)

- Source for every number: `results/report.html` (copied from saved verdict files).
- Figure paths are relative to `results/`.
- Terms: confirm count k, lockout time t_lock in seconds. Arm k2t10 = k 2, lockout 10 s (also called v5). Arm k1t0 = v3.

## 1. Question and answer at a glance
- Mission: keep pheromone foraging swarms trustworthy against false trails as they scale, change and learn.
- Three questions, three answers: confirm-twice removes the no-attack cost (yes), the identifier arm differs (yes), v5 scales worse (yes).
- Figure: `real/final/fig_cost_vs_gain.png`

## 2. Why: Prof. Lu's line and future work
- Foraging line assumes honest robots. Luna and Lu 2024 attack with misleading trails.
- Their future work, page 317: scalability, dynamic environments, machine learning.
- Figure: none (text slide). Optional: lineage strip from `research/lu_lineage.md` §3.

## 3. Setup: arena, robots, attack
- 5 x 5 m grid floor, 20 honest robots, 0 to 4 detractors, 600 s runs.
- Detractors drive to a decoy and lay a false trail. Green tint = true pheromone, red tint = false.
- Figure: `real/mvp3/demo/d2_def0_10.png` and `real/mvp3/demo/d2_def0_19.png`

## 4. The five defenses and the information each needs
- k1t0 (v3), k1t10 (v2), k2t0, k2t10 (v5): no messages, no identifiers, no shared store.
- id arm: identifiers, a shared trail store, a central store.
- Figure: report Table 1 (information table).

## 5. v3 baseline: null
- 80 runs, seeds 1 to 10. Recovered loss share R(2) = 0.07 [−0.02, 0.15].
- Every interval includes 0. Headline stays v3 (D-026).
- Figure: `real/g2_recovered_share.png`

## 6. v2 lockout: FAIL
- Gain at 2 detractors passes: 4.05 [0.85, 7.25].
- No-attack cost −6.7 [−9.7, −3.85] fires the failure rule. The t_lock 0 control costs −6.15 [−8.25, −4.05].
- Figure: report Figure 3 (causal chain, inline SVG).

## 7. Root cause: wrong suspects at crowded real sources
- 14.45 of 14.6 wrong suspects per run sit nearest a real source. 102.55 cone aborts per run.
- Pickups −7.2 per run [−9.35, −5.2]. The base defense causes the cost, not the lockout.
- Figure: report Figure 3 (same chain) or a table of candidate causes (report Table 13).

## 8. M5: confirm-twice (PASS)
- k2t10: no-attack cost 0.125 [−0.975, 1.15], gain at 2 detractors 2.75 [0.40, 4.975].
- Trade-off: k = 2 lowers the gain from 5.05 (k1t10) to 2.75. Lockout effect is not resolved at d = 0 and d = 2.
- Figure: `real/final/fig_cost_vs_gain.png`

## 9. M6: the identifier arm differs
- id beats the best no-identifier arm k1t10 at 2 detractors: 4.375 [2.25, 6.45].
- The arm worked: 0 of 40 seeds with no detractor isolated.
- Figure: `real/final/fig_m6_food.png`

## 10. M6 price: honest isolation
- id isolates 9.05 honest robots per run at no attack and 15.925 at 2 detractors, out of 20.
- v5 keeps the lowest no-attack cost.
- Figure: `real/final/fig_honest_isolation.png`

## 11. M7: v5 scales worse
- Gain per robot falls from 0.273 to 0.0275. Difference −0.246 [−0.411, −0.085]. v3 not resolved.
- Not congestion: food ratio 0.6117, above the 0.5 line. Root cause: pending (`real/scale/root_cause.md`).
- Figure: `real/final/fig_scale.png`

## 12. Limits, future work, takeaways
- Limits: crowding (R10), decoy cap (D-009), adapted not replicated, quarantine paper and detection paper unread.
- Future work: dynamic food, a learned suspect test, quarantine regions, shared confirmation without identifiers (proposal).
- Take-away: more information buys more food and costs more trust.
- Figure: none (text slide).
