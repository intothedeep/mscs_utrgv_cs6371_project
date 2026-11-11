# Slide outline: pheromone foraging under misleading trails (10-minute talk, 12 slides)

- Source for every number: `results/report.html` (copied from saved verdict files).
- Figure paths are relative to `results/`.
- Terms: confirm count k, lockout time t_lock in seconds. Arm k2t10 = k 2, lockout 10 s (also called v5). Arm k1t0 = v3.
- Wording standard (D-059): an interval that includes 0 is "not resolved". Each track has one judged contrast. Every other interval is "reported, not judged".

## 1. Question and answer at a glance
- Mission: keep pheromone foraging swarms trustworthy against false trails as they scale, change and learn.
- Three questions, three answers: question 1 yes (no resolved no-attack cost, 0.125 [−0.975, 1.15], gain above 0), question 2 differs (4.375 [2.25, 6.45]), question 3 no (v5 gain per robot falls, worse than itself at N = 20, not shown worse than v3).
- Figure: `real/final/fig_cost_vs_gain.png` (colour = rule, shape = seed block), plus the verdict table (report Table 1).

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
- Figure: report Table 2 (information table).

## 5. v3 baseline: null
- 80 runs, seeds 1 to 10. Recovered loss share R(2) = 0.07 [−0.02, 0.15].
- Every interval includes 0. Headline stays v3 (D-026).
- Figure: `real/g2_recovered_share.png`

## 6. v2 lockout: FAIL (post-hoc design, confirmed on new seeds)
- Gain at 2 detractors passes: 4.05 [0.85, 7.25]. No-attack cost −6.7 [−9.7, −3.85] fires the failure rule.
- The t_lock 0 control costs −6.15 [−8.25, −4.05]. Pairing limit (risk R11): robot starts differ across cells.
- Figure: report Table 5 (v3 diagnostics: gap from cone abort to the next follow 0.582 s over 4057 aborts) and Figure 4 (causal chain, inline SVG).

## 7. Root cause: wrong suspects at crowded real sources
- 14.45 of 14.6 wrong suspects per run sit nearest a real source. 102.55 cone aborts per run.
- Pickups −7.2 per run [−9.35, −5.2]. The base defense causes the cost. The lockout alone is not resolved at d = 0, −0.55 [−3.45, 2.30].
- Figure: report Figure 4 (same chain) or report Table 15 (candidate causes).

## 8. M5: confirm-twice (PASS)
- k2t10: no-attack cost not resolved, 0.125 [−0.975, 1.15], at most 0.975 food lost. Gain at 2 detractors 2.75 [0.40, 4.975].
- Confirm-count effect is resolved both ways (reported, not judged): +3.0625 [1.5375, 4.625] at d = 0, −2.7875 [−4.475, −1.1625] at d = 2.
- Lockout effect includes 0 at d = 0 and d = 2. D-057 corrects D-051. D-058 corrects D-052 and D-053 (k2t0 also has an interval that includes 0).
- Figure: `real/final/fig_cost_vs_gain.png` (circles = this block)

## 9. M6: the identifier arm differs
- id beats the best no-identifier arm k1t10 at 2 detractors: 4.375 [2.25, 6.45]. This is the judged contrast.
- The arm worked: 0 of 40 seeds with no detractor isolated. Arm check: at d = 2, 9 of 10 seeds isolated 16 to 19 honest robots.
- Figure: `real/final/fig_m6_food.png`

## 10. M6 price: honest isolation
- id isolates 9.05 honest robots per run at no attack and 15.925 at 2 detractors, out of 20.
- v5 has the smallest no-attack cost point estimate, −1.025 [−2.175, 0.025], with no paired interval against the other arms.
- Figure: `real/final/fig_honest_isolation.png`

## 11. M7: v5 gain per robot falls with density
- Gain per robot falls from 0.273 to 0.0275. Difference −0.246 [−0.411, −0.085]. That is worse than v5 at N = 20. v3 not resolved.
- Not shown worse than v3: v5 drop minus v3 drop −0.100 [−0.230, 0.032]. The congestion rule did not fire (ratio 0.6117, above 0.5).
- Root cause (D-056, mechanism level): private confirmation does not scale with density. cover_time 0.244 to 0.126, decoy peaks per robot per decoy 3.55 to 1.98.
- Figure: `real/final/fig_scale.png`

## 12. Limits, future work, takeaways
- Limits: crowding (R10), decoy cap (D-009), adapted not replicated, quarantine paper and detection paper unread. F(0, off) spans 75.8 to 81.4 across seed blocks. Every verdict is within one block and paired (D-061).
- Future work: dynamic food, a learned suspect test, quarantine regions, shared confirmation through local stigmergy (`root_cause.md` §7 option A, untested).
- Take-away: more information buys more food and costs more trust.
- Figure: none (text slide).
