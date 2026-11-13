# Project-end review: numbers, tables and analysis method (M8-04)

- Reviewer role: data-analyst. Read only. No run, no new computation from raw data.
- Read: `results/report.html`, `results/slides_outline.md`, `results/real/final/arm_contrasts.csv`, `fig_cost_vs_gain.png`, `tools/g2_stats.py`, `tools/final_tables.py`, `tools/final_figs.py`, the verdict files of v2, v5, id_arm, scale and judgement, `prereg/defense_v2_lockout.md`, `defense_v5.md`, `defense_id_arm.md`, `scale.md`, `results/real/failure_analysis.md` (parts), `results/real/scale/root_cause.md` (parts), `scale/contrast.csv`, `research/cost_of_trust.md`, `DECISIONS.md` D-026 to D-057.
- Not read: `prereg/keep_a_judgement.md`, `defense_tuning.md`, `pheromone_tuning.md`, `x_v2_judgement/verdict.json` (tuning and a soft-deleted copy, no report claim rests on them).
- Arithmetic marked "approx." is a normal approximation: standard error (SE) = interval width / 3.92. It must not enter the report. An exact answer needs per-seed data and a run.

## Conclusion

**The method is sound. The report numbers checked match their files. Ten findings (section 2) flag claims stronger than their intervals. The report never separates the judged contrast from reported-only ones. The v3 no-attack cost differs across seed blocks beyond noise (approx.), driven by the defense-off baseline.**

| Severity | Count | Items |
| --- | --- | --- |
| High | 2 | N1, N2 |
| Medium | 9 | N3 to N8, N11, N14, N15 |
| Low | 4 | N9, N10, N12, N13 |

- Numbers checked, all match: report Tables 2, 3, 5, 6, 7, 8, 9, 10, 12, 13, 16, Figure 3 text, Result panel.
- Not checked: Table 4 (`v5/mechanism.md` not read), Table 1 and 11 design cells.

## 1. Analysis method (question 1)

- Pairing holds: one index draw serves the base, off and on cells (`tools/g2_stats.py:50`).
- R(d) is a ratio of means with a loss guard (`g2_stats.py:58-68`, guard at `:61`). Correct.
- Two-part pass rules (gain AND no resolved cost) need no multiplicity correction for the pass itself.
- **N1 (High). Judged and reported-only contrasts are not kept apart.** Each prereg names one judged metric: G(2) of k2t10 (`prereg/defense_v5.md:12`), Δ(2) id minus k1t10 (`prereg/defense_id_arm.md:20`), D per arm (`prereg/scale.md:17`).
  - The report shows about 60 unadjusted 95 % intervals. Only `class="flag"` rows mark a primary arm (`report.html:199, 238, 274`).
  - Table 7 flags the id row, but the judged Δ(2) is not in Table 7 (`report.html:232-239`).
  - Method says "one statistic for every verdict" and is silent on multiplicity (`report.html:425`). About 3 of 60 can exclude 0 by chance.
  - Fix: a "Role" column (judged, pre-registered reported-only, exploratory) in Tables 3, 5, 6, 7, 9, 10, 12, 16.
  - Fix: one Method line: "Non-judged intervals are unadjusted and descriptive."
- **N10 (Low). Percentile intervals run narrow at small n** (`g2_stats.py:41-43`). Against a t interval: about 18 % narrower at n = 10, 9 % at n = 20, 4 % at n = 40 (approx.). Re-widened, no verdict flips. M6 v3 G(2) lower bound 0.125 goes to about 0.04. M6 v5 G(0) upper bound 0.025 goes to about 0.08.
  - Fix: state the limit once in Method. A bias-corrected (BCa) check needs a run.

## 2. Claims stronger than the intervals (question 2)

- **N2 (High). "Removes the no-attack cost" reads "not resolved" as "zero".** The rule only asks that the cost interval is not entirely below 0 (`prereg/defense_v5.md:15`). It sets no equivalence margin.
  - Where: `report.html:31, 214`, `slides_outline.md:9, 44`, `DECISIONS.md:60` (D-051), `:66` (D-057 "k2 removes cost").
  - Support exists: E_k(0) = 3.0625 [1.5375, 4.625] is a resolved reduction (`v5/verdict.json:73-77`). Three blocks give near-zero v5 costs: 0.125 [−0.975, 1.15] (221-260), −1.025 [−2.175, 0.025] (321-360), 79.5 − 79.07 = +0.43 (401-430, `scale/contrast.csv:2, 10`, no interval saved).
  - Fix at `:31`: "no resolved cost. The interval bounds it to at most 0.975 items per run." Fix at `:214`: "lowers the cost by 3.06 [1.54, 4.63]".
- **N3 (Medium). The RQ1 headline uses a contrast that is neither judged nor in any file read with an interval.** "Cuts the gain from 5.05 (k1t10) to 2.75" (`report.html:31`) is k2t10 minus k1t10.
  - Fix: cite E_k(2) = −2.7875 [−4.475, −1.1625], marked reported-only. Or compute the pair with `paired_diff_interval` (needs a run).
- **N4 (Medium). "Halves the gain"** (`report.html:215`, `DECISIONS.md:60`). 2.79 / 4.81 = 58 %. The interval allows about 24 % to 93 % (approx.). Fix: "lowers the gain by 2.79 [1.16, 4.48]".
- **N5 (Medium). "The only arm with no d = 0 cost" is false.** M5 k2t0 G(0) is −0.25 [−1.2, 0.65] (`arm_contrasts.csv:22`).
  - Where: `prereg/scale.md:11`, `DECISIONS.md:61` (D-052), `:62` (D-053). Not in the report (grep).
  - Fix: a correction D-row only. The preregs stay frozen. The M7 arm pick stays valid: the rule came before data.
- **N6 (Medium). "The lockout breaks this loop"** (`report.html:339`, `failure_analysis.md:105`). Only d = 4 is resolved: +3.25 [0.9, 5.55]. d = 2: +1.7 [−1.0, 4.45]. E_t includes 0 at d = 0 and 2 (D-057). It is the clause D-057 struck, on another block.
  - Fix: "at d = 4 the lockout added 3.25 [0.9, 5.55]. Elsewhere not resolved."
- **N7 (Medium). "v5 scales worse" reads as "worse than v3".** D is within-arm (`prereg/scale.md:17-18`). v5 drop minus v3 drop is −0.100 [−0.230, 0.032] (`root_cause.md:279`).
  - Where: `report.html:33, 47, 264`, `slides_outline.md:9, 58`.
  - Also flat at `report.html:289`: "The cause is private confirmation" (mechanism level only) and "Congestion does not explain it" (the 0.5 rule did not fire, yet off food per robot fell 39 %).
  - Fix: "v5 per-robot gain falls (resolved). Not shown worse than v3." Write "the congestion rule did not fire".
- **N8 (Medium). Pooled −4.73 [−6.70, −2.80] over seeds 1-30** (`report.html:125`, `failure_analysis.md:12, 120`). It is (10 · −1.9 + 20 · −6.15) / 30: two blocks, two code versions, pooled after both were seen. N11 shows the blocks may differ.
  - Fix: show the blocks separately. Label any pooled value post hoc.
- **N9 (Low). Rank or "resolved" words with no judged contrast behind them.**
  - `report.html:242` Figure 5: "id sits above every no-identifier arm at 1, 2 and 4". Only d = 2 against k1t10 is tested. Figure 5 uses per-arm intervals (`final_figs.py:27-31, 46`).
  - `report.html:125`: M6 v3 gain "resolved", 2.025 [0.125, 3.975]. Reported-only arm, lower bound 0.125.
  - `report.html:220`, D-052: k1t10 46.1 against k1t0 45.6 is a rule pick, not a resolved difference.
  - `report.html:258`, `slides_outline.md:55`, `cost_of_trust.md:80`: "lowest" or "cheapest" v5 cost has no paired interval.
  - Fix: write "point estimate", "reported-only" or "by rule".
- **N12 (Low). Figure 7 caption cites an interval found in no file read** (`report.html:286`). `fig_scale` computes it at draw time (`final_figs.py:116`). `scale/contrast.csv` holds means only.
  - Fix: save the per-N intervals to a CSV, then cite it.
- **N14 (Medium). Table 16 drops the root-cause memo's disclosure.** Verdict rules (b) and (c) were written after the numbers were seen (`root_cause.md:7, 206, 230`). `report.html:360-369` states the verdicts with no such note.
  - Fix: add "rules (b), (c) written post hoc" under Table 16.

## 3. Seed-block variance of the v3 no-attack cost (question 3)

Table A. d = 0, v3 rule (k = 1, no lockout). Source: `arm_contrasts.csv` rows 2, 10, 14, 30, `scale/contrast.csv` rows 2, 6.

| Seeds | n | Code | F(0, off) | F(0, on) | G(0) [95 %] | SE approx. |
| --- | --- | --- | --- | --- | --- | --- |
| 1-10 | 10 | v3 | 75.8 | 73.9 | −1.9 [−5.0, 1.5] | 1.66 |
| 11-30 | 20 | v4, t_lock 0 | 81.35 | 75.2 | −6.15 [−8.25, −4.05] | 1.07 |
| 221-260 | 40 | v5, k1t0 | 77.55 | 74.85 | −2.7 [−4.5, −0.85] | 0.93 |
| 321-360 | 40 | v6 | 81.4 | 75.15 | −6.25 [−8.1, −4.374] | 0.95 |
| 401-430 (N = 20) | 30 | v6 | 79.07 | 74.57 | −4.5 (no interval saved) | |

- Every pair of intervals overlaps. 221-260 overlaps 11-30 by 0.45 and 321-360 by 0.126.
- Overlap is a weak test. Blocks are independent, so z = difference / √(SE₁² + SE₂²) (approx.):
  - 221-260 against 321-360: 3.55 / 1.33 = 2.67. Against 11-30: 3.45 / 1.42 = 2.43.
- Cochran Q over the 4 interval rows: about 11.9 on 3 degrees of freedom, p about 0.008. With the N10 widening: about 10.2, p about 0.017.
- **N11 (Medium). Not consistent with sampling noise alone (approx., post hoc, p about 0.01 to 0.02).** Two groups appear: about −2 (1-10, 221-260) and about −6.2 (11-30, 321-360).
- F(0, on) is flat: 73.9 to 75.2 in all 5 blocks. F(0, off) moves: 75.8 to 81.4. The cost spread is the baseline spread.
- k1t10 shows the same: F(0, on) 74.65, 74.0, 75.175 (rows 6, 18, 34). v5 tracks its baseline instead: 77.675, 80.375, 79.5.
- Confound: block equals code version. Invariance covers 1 to 3 cells on seed 1 or 11 (`report.html:428`).
- Inference: k = 1 rules may cap no-attack food near 75, so their cost grows with block productivity. A per-seed correlation is biased: cost contains F(off).
- Needs a run: a script-backed cross-block test, and the per-block SD of F(0, off).
- Fix: Table A in Limitations, with "approx." numbers replaced by script output. `cost_of_trust.md:154` lists 3 blocks and omits 321-360.

## 4. Mixed-block displays (question 4)

- **N15 (Medium). Figure 4 mixes M5 and M6** (`report.html:208-210`, `final_figs.py:58-78`). Markers and the line under the caption label the blocks. Defects:
  - One rule, two names and colors: k2t10 grey (M5) and v5 green (M6), k1t0 grey and v3 blue. `COLORS` lacks k1t0, k2t0, k2t10 (`final_figs.py:22`).
  - The legend explains markers only, not colors (`final_figs.py:76-77`, `rules/figures.md` §2).
  - No "compare within one block" warning. `report.html:258` invites the cross reading.
  - "No arm gets both" (`report.html:209`): k2t10 has G(0) about 0 and G(2) > 0, the M5 PASS (`:31`). It means "zero cost and the top gain".
  - Fix: one name and color per rule. Color legend. Add "compare within one marker shape". Reword "both".
- **Table 16 row (b)** (`report.html:364`) sets seeds 221-260 numbers (0.138, 0.250) beside the M7 block. No seed label. "It rises" rests on overlapping intervals with no paired difference (`root_cause.md:197`).
  - Fix: add "seeds 221 to 260" and "not a paired contrast".
- **`cost_of_trust.md:94-101`** (Figure 1 panel A) puts 3 blocks on one axis. Seeds sit on 1 of 6 rows, the rest at line 133. The v3 rule sits at −1.9, −2.7 and −6.15. That block spread is about as large as the arm spread.
  - Fix: seeds on every row, or one block per panel.
- Table 12 (`report.html:305-318`) mixes 4 blocks but says "Never subtract across blocks". Labeled. It lacks F(off) (section 3).

## 5. Missing summary table (question 5)

- **N13 (Low). The report has no single verdict table.** Verdicts sit in 4 step boxes and the Result panel. Recommended, after the Result panel, one row per track:

| Track | Research question | Prereg | Judged contrast | Seeds, n | Value [95 %] | Pass line | Verdict | D-row |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G2 v3 | not checked | not checked | R(2) | 1-10, 10 | `real/g2_stats.csv` | not checked | null | D-026 |
| v2 lockout | not checked | `defense_v2_lockout.md` | G(2), G(0) | 11-30, 20 | `v2/verdict.json` | G(2) lower > 0, cost not resolved | fail | D-033 |
| M5 v5 | RQ1 | `defense_v5.md` | G(2), G(0) of k2t10 | 221-260, 40 | `v5/verdict.json` | same | pass | D-051, D-057 |
| M6 id | RQ2 | `defense_id_arm.md` | Δ(2) id minus k1t10 | 321-360, 40 | `id_arm/verdict.json` | excludes 0 | differs | D-054 |
| M7 scale | RQ3 | `scale.md` | D per arm | 401-430, 30 | `scale/verdict.json` | excludes 0 | v3 not resolved, v5 worse | D-055 |

- Fill the value cells by script from the verdict files (`rules/answering.md` §3). Anything outside this table is secondary (fixes N1).
- Also add F(0, off) and F(0, on) columns to Table 12.

## 6. Fix list, in order

1. Verdict table and Role column (N13, N1).
2. Reword report, slides and memo: N2, N3, N4, N6, N7, N9, N14.
3. One correction D-row: D-051 "removes", "halves". D-052, D-053, D-057 "no cost" and "removes" (N2, N4, N5). Preregs stay frozen.
4. Figure 4 and the mixed-block labels (N15).
5. Split the pooled −4.73 (N8). Table A in Limitations (N11).
6. Needs a run (owner's call): cross-block test and F(0, off) SD (N11), k2t10 minus k1t10 at d = 2 (N3), id minus v5 at d = 1, 4 (N9), per-N intervals (N12).
