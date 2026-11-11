# Root cause: why defense v5 scales worse from 20 to 40 honest robots (M7-04)

Status: 2026-11-11. Method and verdict rules written before `root_cause.csv` existed. Numbers filled from `results/real/scale/root_cause.csv` (7,646 rows). Each cell names its key as `scope / arm / n / d / metric`.
Script: `tools/m7_root_cause.py` (saved runs only, run by the main session, 14 s).
Numbers marked "computed" are products or ratios of two cell means from that CSV.

- Disclosure: some numbers were already seen when the rules were written.
  - Rule (b): the N = 20 k2t10 gains at d = 2 and d = 4 in `results/real/v5/g2_stats.csv`.
  - Rule (c): the `verdict.json` wrong source suspects per robot and the d = 0 cost per robot.
- So rules (b) and (c) are not blind. Rules (a), (d), (e) and (f) are.

## 1. Conclusion

**v5 needs the SAME robot to fail twice at a decoy. At N = 40 each robot meets each decoy about half as often, so fewer robots ever confirm it.**

- Total visits per decoy stay about the same (computed 71 at N 20, 79 at N 40). They are spread over twice as many robots.
- Protected robot-time per decoy halves: 0.244 to 0.126 (`cover_time`). False FOLLOW time saved per robot falls from 32.3 s to 20.1 s. v3 (k = 1) saves the same time at both N.
- This fall of the recovered share carries −0.139 of the −0.246 drop (`drop_from_R`).
- A second part is shared with v3: the loss per robot itself shrinks (1.95 to 1.19 food), so there is less to recover. It carries −0.107 (`drop_from_L`).
- Not causes: attack per decoy (b), wrong source suspects (c), lockout side effects (e).

```
 N 20 -> 40, 2 decoys, fixed arena
        |
 decoy visits per decoy ~ constant (71 -> 79, computed)
        |  spread over 2x robots
        v
 decoy peaks per robot per decoy, off: 3.55 -> 1.98
        |  private memory: k = 2 needs 2 failures by ONE robot
        v
 robots with a decoy point active: 0.52 -> 0.31     (v3, k = 1: 0.70 -> 0.59)
 protected robot-time share:       0.24 -> 0.13
        v
 false FOLLOW s saved per robot:   32.3 -> 20.1     (v3: 21.3 -> 23.3, same)
 pickups gained per robot:         0.25 -> 0.01
        v
 recovered share R: 0.140 -> 0.023  -> drop_from_R  -0.139
 plus loss per robot L/N: 1.95 -> 1.19 -> drop_from_L -0.107   (shared with v3)
                                         G/N drop    -0.246
```

Caption: Figure 2 shows the measured chain from N to the gain. Why: it locates where the v5 gain is lost.

## 2. Why this analysis

- Owner rule: "if we fail we need to find why we have failed."
- M7 verdict (D-055, `results/real/scale/verdict.json`): v5 scales worse.
  - Gain per honest robot G/N: 0.273 at N = 20 (d = 2), 0.028 at N = 40 (d = 4).
  - Difference −0.246 [−0.411, −0.085].
- v3 also drops (0.208 to 0.062), but its interval includes 0.
- The next design (v6, no ID) needs the cause, not another parameter guess.

## 3. Data used

| Root | Arm | confirm_k | t_lock (s) | N honest | d levels | Seeds | Runs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `runs/m7_scale/off_n20/`, `off_n40/` | off | inert | inert | 20, 40 | 0, 10 % | 401-430 | 120 |
| `runs/m7_scale/v3_n20/`, `v3_n40/` | v3 | 1 | 0 | 20, 40 | 0, 10 % | 401-430 | 120 |
| `runs/m7_scale/v5_n20/`, `v5_n40/` | v5 | 2 | 10 | 20, 40 | 0, 10 % | 401-430 | 120 |
| `results/real/v5/g2_stats.csv` | k2t10 (= v5) | 2 | 10 | 20 | 2, 4 | 221-260 | saved summary |

- All runs are real simulation logs, 600 s, same 5 × 5 m arena, same nest area.
- 10 % detractors: d = 2 at N = 20, d = 4 at N = 40. Both use 2 active decoys (D-009 cap).
- Detractor j lures to decoy j mod 2 (`pheromone_loop_functions.cpp` `AssignDecoys`). So each decoy has 1 detractor at N = 20 and 2 at N = 40.
- Pairing check: the layout of seed s must be the same at N = 20 and N = 40. Key `check / / / / layout_differs_n20_n40` = 0 of 60 pairs.

## 4. Method

### 4.1 What is confounded, and what is not

```
 N 20 -> N 40 in m7_scale changes two things at once:
   honest robots   20 -> 40   (more robots per source, per decoy)   -> candidates a, c, d, e
   detractors/decoy 1 -> 2    (each false trail refreshed 2x)        -> candidate b
 Only one saved cell varies b alone: N 20, k2t10, d 2 vs d 4 (seeds 221-260)
```

Caption: Figure 1 shows what the N change moves. Why: a and b cannot be split inside `m7_scale` alone.

- Inside `m7_scale`, (a) and (b) move together. The N = 20 cell of `results/real/v5/g2_stats.csv` varies detractors per decoy at a fixed N. It uses other seeds. That is a limit.
- Second view of the same file: N = 20 with d = 4 against `m7_scale` N = 40 with d = 4. Both have 2 detractors per decoy. Only the honest count differs. This comparison is unpaired and uses other seeds, so it is a reading, not a verdict.
- No k1t10 or k2t0 arm exists at N = 40. So the lockout and k = 2 cannot be isolated by a contrast. (e) uses direct proxies and the v5-minus-v3 drop. The missing arms are named, not collected.

### 4.2 Measurements

1. Per run, honest robots only, read `events.csv`, `robots.csv`, `ticks.csv`, `manifest.json`.
2. Stored point of a failure = the robot's last peak (as `failure_analysis.py`, `v5_mechanism.py`).
3. Rebuild each robot's private memory with the v5 queue: first match within r_merge 0.3 m, a Count per point, 16 slots, first-in-first-out (FIFO) eviction. A point is active when Count ≥ confirm_k.
4. Three replay checks per run.
   - Held points equal `ticks.csv` `suspects_total` at every row. Key `replay_ok`.
   - The activations equal `v5_mechanism.replay_k`. Key `replay_ok`.
   - Every cone_abort finds an active point within d_cone. Key `abort_none_pr`, near 0 expected.
5. A cone_abort is assigned to the nearest ACTIVE point within d_cone. `failure_analysis.abort_triggers` uses every stored point. It is not used here.
6. Per seed, paired N 40 minus N 20, 95 % percentile bootstrap, 10,000 resamples (`g2_stats.paired_diff_interval`).
7. Defense effect per robot = (arm − off) on the same seed, divided by N for food (scope `delta`).
   - Sign: a negative `d_ffollow_pr` means the defense cut false FOLLOW time. "Saved" = −`d_ffollow_pr`.
8. (d) split: G/N = R × L/N.
   - L/N = (F(0, off) − F(d10, off)) / N.
   - R = mean G / mean L (ratio of means, not per-seed ratios: per-seed L can be near 0).
   - The drop splits exactly: drop = R20 × ΔL + ΔR × L40.
   - All split terms share one seed bootstrap index, so each term gets an interval.
   - The ratio v5 `act_share` / v3 `act_share` uses the same bootstrap (scope `dd`, arm `v5/v3`).
9. Censoring: time to first confirmation is censored at 600 s. The memo reports the confirmed share and the time-averaged protected share (`cover_time`), not a mean over confirmed pairs.

### 4.3 Candidates, predictions and verdict rules (written before the numbers)

A per-robot difference between N alone is not "supported". It also needs a link to food or to false-trail time.

| Candidate | Prediction if it is the cause | Supported if | Not supported if |
| --- | --- | --- | --- |
| (a) Fewer repeat visits per robot per decoy, so k = 2 confirms later or less | v5 d10: `fail2_share`, `act_share`, `cover_time` lower at N 40. `t_first_act_s` later. Less false FOLLOW time saved (`d_ffollow_pr` contrast above 0) | `cover_time` contrast below 0, AND `d_ffollow_pr` contrast above 0, AND the `act_share_v5_over_v3_diff` interval below 0 (the k = 2 part) | `cover_time` contrast includes 0 or is above 0 |
| (b) Attack per decoy doubles (2 detractors per decoy) | `det_reach_pd`, `pher_false_pd` up. Higher L/N. At fixed N 20, G/N falls from d 2 to d 4 | trail refresh up, AND at fixed N 20 G/N at d 4 below d 2 | at fixed N 20, G/N at d 4 is not below d 2 |
| (c) Crowding raises wrong source suspects even with k = 2 | v5: `act_src_pr`, `abort_src_pr` up at N 40, at d0 and at d10 (where G is measured). d = 0 cost per robot worse | both contrasts above 0 at d10, AND the d0 `d_food` contrast below 0 | `act_src_pr` contrast includes 0 or is below 0 at both levels |
| (d) The loss per robot changes, so there is less to recover | L/N lower at N 40 with R unchanged | L/N contrast below 0, AND `drop_from_L` interval below 0, AND `R_diff` interval includes 0 | L/N contrast includes 0 |
| (e) Lockout side effects grow with density | v5 `abort_true_pr`, `lock_true_s_pr` up at N 40. v5 drops more than v3 | `lock_true_s_pr` contrast above 0, AND the `G_pr_drop` (v5-v3) interval below 0 | `G_pr_drop` interval includes 0 and `lock_true_s_pr` does not rise |
| (f) added: saved time does not become food in a crowded arena | v5 d10: same false FOLLOW time saved per robot at both N, but fewer pickups gained (`d_pickup_pr` contrast below 0) | `d_ffollow_pr` contrast includes 0, AND `d_pickup_pr` contrast below 0 | `d_pickup_pr` contrast includes 0, or less time is saved (then (a) or (b) applies) |

- Anything between the two columns is "unclear".
- If several are supported, the root cause is the one that carries the most of the drop (`drop_from_L` against `drop_from_R`, and the `d_ffollow_pr` link).

## 5. Results

### 5.1 The verdict numbers, reproduced

| Item | Key | Value |
| --- | --- | --- |
| G/N, v5, deviation from `verdict.json` | `check / v5 / / d10 / G_pr_max_abs_dev_vs_verdict` | 0.0000 |
| G/N, v3, deviation from `verdict.json` | `check / v3 / / d10 / G_pr_max_abs_dev_vs_verdict` | 0.0000 |
| Runs with an inexact replay (v3, v5) | `cell / * / * / * / replay_ok` | 0 (mean 1.0000 in all 8 cells) |
| Aborts with no active point, per robot (v3, v5) | `cell / * / * / * / abort_none_pr` | 0.0000 in all 8 cells |
| Layout pairs that differ between N 20 and N 40 | `check / / / / layout_differs_n20_n40` | 0 of 60 |

- The script reproduces the verdict. The memory replay is exact. Every abort finds its active trigger point.

### 5.2 (d) Loss per robot and recovered share

Table 1. Off arm loss and recovered share (`scope split`, n `40-20`, d `d10`)

| Item | N 20 | N 40 | N 40 − N 20 [95 %] |
| --- | --- | --- | --- |
| L/N, off (`L_pr`) | 1.952 | 1.186 | −0.766 [−0.948, −0.580] |
| R, v5 (`R_n20`, `R_n40`, `R_diff`) | 0.140 [0.064, 0.212] | 0.023 [−0.029, 0.075] | −0.117 [−0.207, −0.028] |
| R, v3 (`R_n20`, `R_n40`, `R_diff`) | 0.107 [0.030, 0.179] | 0.053 [−0.021, 0.120] | −0.054 [−0.157, 0.046] |
| v5 drop from L (`drop_from_L`) [95 %] | | | −0.107 [−0.182, −0.043] |
| v5 drop from R (`drop_from_R`) [95 %] | | | −0.139 [−0.243, −0.032] |
| v3 drop from L (`drop_from_L`) [95 %] | | | −0.082 [−0.149, −0.021] |
| v3 drop from R (`drop_from_R`) [95 %] | | | −0.064 [−0.182, 0.056] |

- Each honest robot loses less food to the detractors at N 40. The arena saturates: food per robot at d = 0 falls from 3.95 to 2.42 (`verdict.json` congestion).
- v5 also recovers a smaller share of that loss (R_diff interval below 0). v3 does not resolve a change in R.
- The L part carries computed 44 % of the v5 drop (0.107 of 0.246). The R part carries 56 %.

Verdict (d): **unclear by the rule, real as a part.** L/N falls and `drop_from_L` is below 0. But the rule also needs `R_diff` to include 0, and for v5 it does not. The loss shrink explains part of the v5 drop and most of the v3 drop. It does not explain why v5 drops more.

### 5.3 (a) Confirmation per decoy, v5 and v3, d10

Table 2. Per decoy, per honest robot (`scope cell`, `contrast`)

| Metric | v5 N 20 | v5 N 40 | v5 Δ [95 %] | v3 N 20 | v3 N 40 | v3 Δ [95 %] |
| --- | --- | --- | --- | --- | --- | --- |
| Exposure: decoy peaks per robot per decoy, off (`pk_dec_prd`) | 3.553 | 1.980 | −1.572 [−1.734, −1.408] | | | |
| Exposure, same arm (`pk_dec_prd`) | 2.577 | 1.802 | −0.775 [−0.887, −0.663] | 2.118 | 1.650 | −0.467 [−0.560, −0.373] |
| Robots with ≥ 1 decoy failure (`fail1_share`) | 0.708 | 0.573 | −0.135 [−0.165, −0.103] | 0.703 | 0.588 | −0.115 [−0.143, −0.086] |
| Robots with ≥ 2 decoy failures (`fail2_share`) | 0.567 | 0.391 | −0.176 [−0.205, −0.148] | 0.273 | 0.226 | −0.047 [−0.073, −0.021] |
| Robots with a decoy point active (`act_share`) | 0.523 | 0.313 | −0.209 [−0.239, −0.180] | 0.703 | 0.588 | −0.115 [−0.143, −0.086] |
| Protected robot-time share (`cover_time`) | 0.244 | 0.126 | −0.118 [−0.134, −0.102] | 0.424 | 0.341 | −0.083 [−0.101, −0.066] |
| First activation per decoy, s, censored 600 (`t_first_act_s`) | 120.3 | 133.0 | +12.7 [−0.9, 25.4] | 64.9 | 60.5 | −4.4 [−9.4, 0.4] |
| False FOLLOW s per robot, arm − off (`delta d_ffollow_pr`, negative = saved) | −32.35 | −20.06 | +12.29 [6.76, 17.82] | −21.33 | −23.33 | −2.00 [−9.66, 6.06] |
| Pickups gained per robot, arm − off (`delta d_pickup_pr`) | 0.247 | 0.011 | −0.236 [−0.393, −0.085] | 0.175 | 0.043 | −0.132 [−0.301, 0.037] |

| Item | Key | N 20 | N 40 | Δ [95 %] |
| --- | --- | --- | --- | --- |
| v5 `act_share` / v3 `act_share` | `dd / v5/v3 / 40-20 / d10 / act_share_v5_over_v3_*` | 0.744 [0.705, 0.785] | 0.533 [0.502, 0.562] | −0.210 [−0.260, −0.163] |

- Exposure halves. Off arm: 3.55 to 1.98 decoy peaks per robot per decoy.
- Total decoy peaks per decoy stay about the same: computed 3.553 × 20 = 71 at N 20, 1.980 × 40 = 79 at N 40. A decoy serves a near-fixed flow of visits. More robots share it.
- k = 2 needs two failures by one robot. So the v5 confirmed share falls more than the v3 share (ratio 0.74 to 0.53).
- v5 saves 12.3 s less false FOLLOW time per robot at N 40. v3 saves the same time at both N.
- First activation is not resolved (interval includes 0). The per-robot count falls, not the first time.

Verdict (a): **supported.** All three parts of the rule hold. `cover_time` −0.118 [−0.134, −0.102] is below 0. `d_ffollow_pr` +12.29 [6.76, 17.82] is above 0 (less saved). `act_share_v5_over_v3_diff` −0.210 [−0.260, −0.163] is below 0. The link to food: pickups gained per robot fall by 0.236 [0.085, 0.393].

Verdict (f), added: **not supported for v5.** v5 saves less time at N 40 (`d_ffollow_pr` above 0), so (a) applies, as the rule says. Reading for v3 only: the same time is saved, and pickups gained fall by 0.132, but the interval [−0.301, 0.037] includes 0. That fits (d), less food per saved second in a saturated arena.

### 5.4 (b) Attack per decoy

Table 3. Trail refresh and the fixed-N check

| Metric | Key | N 20 | N 40 | Δ [95 %] |
| --- | --- | --- | --- | --- |
| Detractor decoy_reach per decoy, off | `cell / off / * / d10 / det_reach_pd` | 10.68 | 12.93 | +2.25 [1.63, 2.83] |
| False pheromone per decoy, off | `cell / off / * / d10 / pher_false_pd` | 25,931 | 27,528 | +1,597 [700, 2,473] |
| False FOLLOW s per robot, off | `cell / off / * / d10 / ffollow_pr` | 102.24 | 100.18 | −2.06 [−6.98, 2.69] |

| Fixed N 20, k2t10, seeds 221-260 | Key | d 2 (1 per decoy) | d 4 (2 per decoy) | m7 N 40, d 4 (2 per decoy), unpaired |
| --- | --- | --- | --- | --- |
| G/N [95 %] | `check / v5_N20_seeds221-260 / 20 / d2, d4 / G_pr`. m7: `delta / v5 / 40 / d10 / d_food` | 0.138 [0.020, 0.249] | 0.250 [0.139, 0.350] | 0.028 |
| L/N [95 %] | `check / v5_N20_seeds221-260 / 20 / d2, d4 / L_pr`. m7: `split / off / 40 / d10 / L_pr` | 1.825 [1.623, 2.029] | 2.250 [2.044, 2.451] | 1.186 |
| R [95 %] | `check / v5_N20_seeds221-260 / 20 / d2, d4 / R_share`. m7: `split / v5 / 40-20 / d10 / R_n40` | 0.075 [0.011, 0.130] | 0.111 [0.065, 0.151] | 0.023 [−0.029, 0.075] |

- Two detractors per decoy refresh the trail more, but not twice as much: decoy_reach +21 % (computed 12.93 / 10.68), false pheromone +6 % (computed).
- False FOLLOW time per honest robot does not change (interval includes 0). Each robot meets the same attack.
- At fixed N 20, doubling detractors per decoy RAISES G/N (0.138 to 0.250) and R (0.075 to 0.111).
- Same attack per decoy, N 20 against N 40 (unpaired, other seeds): R 0.111 against 0.023. The honest count, not the attack, goes with the fall.

Verdict (b): **not supported.** Trail refresh rises. But at fixed N 20, G/N at d 4 is not below d 2. It is higher. (Rule written with these numbers seen, see the disclosure.)

### 5.5 (c) Crowding and wrong source suspects

Table 4. Per honest robot. Crowding rows are d0 only (the script reads crowding at d0)

Rows marked "off" show the off arm in the N 20, N 40 and Δ columns. Other rows show v5.

| Metric | Level | N 20 | N 40 | Δ [95 %] | v3 Δ [95 %] |
| --- | --- | --- | --- | --- | --- |
| Source peaks with no pickup, share, off (`src_fail_share`) | d0 | 0.313 | 0.331 | +0.018 [−0.018, 0.052] | |
| Robots near a failed source peak, off (`crowd_src_fail`) | d0 | 2.18 | 2.67 | +0.49 [0.28, 0.69] | |
| Robots near a successful source peak, off (`crowd_src_ok`) | d0 | 1.60 | 1.95 | +0.34 [0.11, 0.54] | |
| Wrong source failures stored (`sus_src_pr`) | d0 | 0.767 | 0.484 | −0.283 [−0.349, −0.218] | −0.196 [−0.264, −0.130] |
| Wrong source points activated (`act_src_pr`) | d0 | 0.068 | 0.033 | −0.036 [−0.061, −0.013] | −0.196 [−0.264, −0.130] |
| Aborts by an active source point (`abort_src_pr`) | d0 | 0.085 | 0.054 | −0.031 [−0.076, 0.013] | −2.634 [−3.431, −1.863] |
| d = 0 cost per robot (`delta d_food`) | d0 | 0.022 | 0.012 | −0.010 [−0.056, 0.036] | +0.178 [0.066, 0.295] |
| Wrong source points activated (`act_src_pr`) | d10 | 0.025 | 0.006 | −0.019 [−0.038, −0.003] | −0.081 [−0.125, −0.038] |
| Aborts by an active source point (`abort_src_pr`) | d10 | 0.035 | 0.004 | −0.031 [−0.064, −0.007] | −0.593 [−1.021, −0.195] |

- Crowding at sources rises at N 40 (+0.49 robots near a failed peak). The share of failed source peaks does not change.
- Per robot, wrong source points FALL at N 40, at both levels. Each robot reaches a source less often (`pk_src_pr`, off d0, −1.20 [−1.34, −1.06]).
- k = 2 keeps wrong activations near 0 at both N. The v5 d = 0 cost stays near 0.

Verdict (c): **not supported.** `act_src_pr` contrast is below 0 at d0 and d10. (Rule written with the `verdict.json` suspect numbers seen, see the disclosure.)

### 5.6 (e) Lockout side effects

Table 5. v5, per honest robot

| Metric | d0 N 20 | d0 N 40 | d0 Δ | d10 N 20 | d10 N 40 | d10 Δ |
| --- | --- | --- | --- | --- | --- | --- |
| Aborts on a true trail (`abort_true_pr`) | 0.085 | 0.054 | −0.031 [−0.076, 0.013] | 1.267 | 0.548 | −0.718 [−0.903, −0.544] |
| Lockout s after a true-trail abort, upper bound (`lock_true_s_pr`) | 0.85 | 0.54 | −0.31 [−0.76, 0.13] | 12.67 | 5.48 | −7.18 [−9.03, −5.44] |
| Abort to next pickup, s (`abort_to_pickup_s`) | 40.4 (14 runs) | 75.9 (12 runs) | +43.4 [3.2, 91.6] (6 paired seeds) | 96.8 | 93.7 | −3.1 [−15.9, 10.5] |

| Item | Key | Value [95 %] |
| --- | --- | --- |
| v5 drop minus v3 drop | `dd / v5-v3 / 40-20 / d10 / G_pr_drop` | −0.100 [−0.230, 0.032] |

- Lockout time after true-trail aborts FALLS at N 40 (12.7 s to 5.5 s per robot at d10). Fewer points are active, so fewer aborts happen.
- The d0 abort-to-pickup row rests on 6 paired seeds with a rare event (0.05 aborts per robot). It carries no food effect: the d = 0 cost is flat.
- The v5 drop is not resolved as larger than the v3 drop in food. So the k = 2 plus lockout part is not shown at the food level by this contrast. It is shown at the mechanism level by (a).

Verdict (e): **not supported.** The `G_pr_drop` interval includes 0, and `lock_true_s_pr` does not rise. It falls.

## 6. Root cause

Table 6. Candidate summary

| Candidate | Measurement | Number | File | Verdict |
| --- | --- | --- | --- | --- |
| (a) slower or rarer confirmation per decoy | `cover_time`, `act_share`, `d_ffollow_pr` | `cover_time` −0.118 [−0.134, −0.102]. `d_ffollow_pr` +12.29 [6.76, 17.82]. v5/v3 `act_share` ratio −0.210 [−0.260, −0.163] | `results/real/scale/root_cause.csv` | **supported** |
| (b) attack per decoy doubles | `det_reach_pd`, fixed-N G/N | refresh +2.25 [1.63, 2.83]. N 20: G/N 0.138 at d 2, 0.250 at d 4 | `root_cause.csv`, `results/real/v5/g2_stats.csv` | **not supported** |
| (c) crowding, wrong source suspects | `act_src_pr`, d0 `d_food` | d0 −0.036 [−0.061, −0.013]. d10 −0.019 [−0.038, −0.003]. Cost −0.010 [−0.056, 0.036] | `root_cause.csv`, `verdict.json` | **not supported** |
| (d) loss per robot changes | `L_pr`, `R_n*`, drop split | L/N −0.766 [−0.948, −0.580]. `drop_from_L` −0.107 [−0.182, −0.043]. `R_diff` −0.117 [−0.207, −0.028] | `root_cause.csv` | **unclear** by the rule. A real part (44 %, computed), shared with v3 |
| (e) lockout side effects | `lock_true_s_pr`, dd | `lock_true_s_pr` −7.18 [−9.03, −5.44]. `G_pr_drop` −0.100 [−0.230, 0.032] | `root_cause.csv` | **not supported** |
| (f) added: saved time does not become food | `d_ffollow_pr`, `d_pickup_pr` | v5 saves less time (+12.29). v3: same time, pickups −0.132 [−0.301, 0.037] | `root_cause.csv` | **not supported** for v5 |

### 6.1 The mechanism

1. The arena, the 3 sources and the 2 decoys stay fixed. N doubles.
2. A decoy takes a near-fixed flow of honest visits: computed 71 peaks per decoy at N 20, 79 at N 40 (off arm).
3. So each robot meets each decoy about half as often: 3.55 to 1.98 decoy peaks per robot per decoy (off).
4. v5 memory is private, and a point needs 2 failures by the SAME robot (DESIGN_M5 §1 rule 8).
5. Robots with 2 or more failures at a decoy fall from 0.567 to 0.391. Robots with an active decoy point fall from 0.523 to 0.313.
6. The protected robot-time share halves: 0.244 to 0.126. v3, with k = 1, falls less: 0.424 to 0.341.
7. False FOLLOW time saved per robot falls from 32.3 s to 20.1 s. v3 saves 21.3 s and 23.3 s, the same.
8. Pickups gained per robot fall from 0.247 to 0.011. The recovered share R falls from 0.140 to 0.023.
9. Separately, the loss per robot shrinks from 1.95 to 1.19 food (arena saturation). This hits v3 and v5 alike.
10. Sum for v5: −0.139 from R plus −0.107 from L = −0.246 per robot.

- Root cause: **private, same-robot confirmation does not scale with robot density.** The evidence a decoy offers is a fixed flow of failures. k = 2 per robot needs that flow per robot, and per robot it halves.
- Limit of this claim: the food-level contrast v5 drop minus v3 drop is −0.100 [−0.230, 0.032]. It is not resolved. The k = 2 cause is resolved at the mechanism level (`act_share` ratio, `d_ffollow_pr`), not as a separate food number.

## 7. What a v6 no-ID design would need

Options only. The mechanism choice belongs to `system-architect`. The pick is the owner's.

### 7.1 Requirements from the root cause

1. Confirmation must count failures over ALL robots at a place, not per robot. Per robot, decoy visits halve with N (3.55 to 1.98). Per decoy, they stay or grow (71 to 79, computed).
2. It must keep the v5 d = 0 safety. Wrong source activations are near 0 now (0.068 and 0.033 per robot at d0).
3. Pooled failures at true sources grow with N. Computed from `sus_src_pr` at d0: 15.3 per run at N 20, 19.4 at N 40. A pooled count needs a check that a decoy never passes.
4. The separating fact (computed, off d0): about 86 pickups per run at N 20 from 3 sources. A decoy gives 0 pickups. Pooled failures with no nearby pickup separate the two. This is inference. It is not measured as a rule.

### 7.2 Options

| Option | What it changes | Answers | Trade-off |
| --- | --- | --- | --- |
| A. Shared confirmation through local stigmergy | A failure leaves a short-lived local mark. A pickup clears the mark nearby. A point confirms when marks from ANY robots reach k | (a): confirmation follows total visits per decoy, which do not fall with N | Needs a new environment channel. Detractors may lay or clear marks. Pooled source failures (19.4 per run at N 40) need the pickup clear to stay safe |
| B. Lower k with density | k = 1 when many robots are near, k = 2 otherwise | (a), in part. v3 (k = 1) keeps its confirmed share better (0.70 to 0.59) | Brings back the d = 0 cost of v3 where crowding is high: −0.225 per robot at N 20 (`delta / v3 / 20 / d0 / d_food`) |
| C. Longer per-robot memory window | Keep pending points longer, or count over a longer time | (a), weakly. First activation is not the bottleneck (`t_first_act_s` Δ includes 0) | Confirmation stays per robot. Per-robot visits still halve |
| D. No change | Accept the per-robot gain at N 40 | none | RQ3 stays "no" for v5 |

- **The evidence favours option A.** The root cause is that evidence is split across robots. Only A pools it without IDs. B trades back the d = 0 cost. C does not touch the per-robot count.
- Next check before any design, from saved files: replay the `m7_scale` events with a pooled count (any robot, same r_merge, k = 2, pickup clears). Report pooled `act_share` and wrong source activations at both N. This needs one added function in `tools/m7_root_cause.py`, no run.
- Theory link (inference, not measured at N = 40): the M6 ID arm (D-054) wins by pooling evidence across robots in a shared store. Option A pools evidence through the environment instead of IDs. The ID arm was not run at N = 40 (D-053), so its scaling is unknown.

## 8. Limits

- (a) and (b) are confounded inside `m7_scale`. The fixed-N check uses other seeds (221-260) and N 20 only.
- No k1t10 or k2t0 arm at N = 40. The lockout share of the drop is bounded by proxies and the dd contrast, not isolated.
- `lock_true_s_pr` is an upper bound: it assumes every true-trail abort costs the full t_lock.
- `robots.csv` has one row per second. false_share and crowding at an event use the row of that second.
- The stored point and the abort trigger are rebuilt from events. Heading is not used.
- Crowding is an association (`failure_analysis.md` §8).
- The v5 drop minus the v3 drop is not resolved in food (−0.100 [−0.230, 0.032]). The k = 2 cause rests on mechanism measures.
- "Visits per decoy stay about the same" is a product of two cell means (computed), with no interval.
- The pooled-confirmation benefit of option A is inference. No replay or run has tested it.
