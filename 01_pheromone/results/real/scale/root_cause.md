# Root cause: why defense v5 scales worse from 20 to 40 honest robots (M7-04)

Status: 2026-11-11. Method and verdict rules written before `root_cause.csv` existed. Every [TBD] cell names its key in `results/real/scale/root_cause.csv` as `scope / arm / n / d / metric`.
Script: `tools/m7_root_cause.py` (saved runs only, run by the main session).

- Disclosure: some numbers were already seen when the rules were written.
  - Rule (b): the N = 20 k2t10 gains at d = 2 and d = 4 in `results/real/v5/g2_stats.csv`.
  - Rule (c): the `verdict.json` wrong source suspects per robot and the d = 0 cost per robot.
- So rules (b) and (c) are not blind. Rules (a), (d), (e) and (f) are.

## 1. Conclusion

**[TBD after the run.]** One line: the root cause, then the mechanism in three short lines.

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
- Pairing check: the layout of seed s must be the same at N = 20 and N = 40. Key `check / / / / layout_differs_n20_n40` = [TBD] (must be 0).

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
| G/N, v5, deviation from `verdict.json` | `check / v5 / / d10 / G_pr_max_abs_dev_vs_verdict` | [TBD] |
| G/N, v3, deviation from `verdict.json` | `check / v3 / / d10 / G_pr_max_abs_dev_vs_verdict` | [TBD] |
| Runs with an inexact replay (v3, v5) | `run / * / * / * / replay_ok` = 0 count | [TBD] |
| Aborts with no active point, per robot (v3, v5) | `cell / * / * / * / abort_none_pr` | [TBD] |
| Layout pairs that differ between N 20 and N 40 | `check / / / / layout_differs_n20_n40` | [TBD] |

### 5.2 (d) Loss per robot and recovered share

Table 1. Off arm loss and recovered share (`scope split`, n `40-20`, d `d10`)

| Item | N 20 | N 40 | N 40 − N 20 [95 %] |
| --- | --- | --- | --- |
| L/N, off (`L_pr`) | [TBD] | [TBD] | [TBD] |
| R, v5 (`R_n20`, `R_n40`, `R_diff`) | [TBD] | [TBD] | [TBD] |
| R, v3 (`R_n20`, `R_n40`, `R_diff`) | [TBD] | [TBD] | [TBD] |
| v5 drop from L (`drop_from_L`) [95 %] | | | [TBD] |
| v5 drop from R (`drop_from_R`) [95 %] | | | [TBD] |

Verdict (d): [TBD]

### 5.3 (a) Confirmation per decoy, v5 and v3, d10

Table 2. Per decoy, per honest robot (`scope cell`, `contrast`)

| Metric | v5 N 20 | v5 N 40 | v5 Δ [95 %] | v3 N 20 | v3 N 40 | v3 Δ [95 %] |
| --- | --- | --- | --- | --- | --- | --- |
| Exposure: decoy peaks per robot per decoy, off (`pk_dec_prd`) | [TBD] | [TBD] | [TBD] | | | |
| Exposure, same arm (`pk_dec_prd`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| Robots with ≥ 1 decoy failure (`fail1_share`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| Robots with ≥ 2 decoy failures (`fail2_share`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| Robots with a decoy point active (`act_share`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| Protected robot-time share (`cover_time`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| First activation per decoy, s, censored 600 (`t_first_act_s`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| False FOLLOW s per robot, arm − off (`delta d_ffollow_pr`, negative = saved) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| Pickups gained per robot, arm − off (`delta d_pickup_pr`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

| Item | Key | N 20 | N 40 | Δ [95 %] |
| --- | --- | --- | --- | --- |
| v5 `act_share` / v3 `act_share` | `dd / v5/v3 / 40-20 / d10 / act_share_v5_over_v3_*` | [TBD] | [TBD] | [TBD] |

Verdict (a): [TBD]

Verdict (f), added: [TBD] (rows `d_ffollow_pr` and `d_pickup_pr` above)

### 5.4 (b) Attack per decoy

Table 3. Trail refresh and the fixed-N check

| Metric | Key | N 20 | N 40 | Δ [95 %] |
| --- | --- | --- | --- | --- |
| Detractor decoy_reach per decoy, off | `cell / off / * / d10 / det_reach_pd` | [TBD] | [TBD] | [TBD] |
| False pheromone per decoy, off | `cell / off / * / d10 / pher_false_pd` | [TBD] | [TBD] | [TBD] |
| False FOLLOW s per robot, off | `cell / off / * / d10 / ffollow_pr` | [TBD] | [TBD] | [TBD] |

| Fixed N 20, k2t10, seeds 221-260 | Key | d 2 (1 per decoy) | d 4 (2 per decoy) | m7 N 40, d 4 (2 per decoy), unpaired |
| --- | --- | --- | --- | --- |
| G/N [95 %] | `check / v5_N20_seeds221-260 / 20 / d2, d4 / G_pr` | [TBD] | [TBD] | [TBD] |
| L/N [95 %] | `check / v5_N20_seeds221-260 / 20 / d2, d4 / L_pr` | [TBD] | [TBD] | [TBD] |
| R [95 %] | `check / v5_N20_seeds221-260 / 20 / d2, d4 / R_share` | [TBD] | [TBD] | [TBD] |

Verdict (b): [TBD]

### 5.5 (c) Crowding and wrong source suspects

Table 4. Per honest robot. Crowding rows are d0 only (the script reads crowding at d0)

| Metric | Level | v5 N 20 | v5 N 40 | v5 Δ [95 %] | v3 Δ [95 %] |
| --- | --- | --- | --- | --- | --- |
| Source peaks with no pickup, share, off (`src_fail_share`) | d0 | [TBD] | [TBD] | [TBD] | |
| Robots near a failed source peak, off (`crowd_src_fail`) | d0 | [TBD] | [TBD] | [TBD] | |
| Robots near a successful source peak, off (`crowd_src_ok`) | d0 | [TBD] | [TBD] | [TBD] | |
| Wrong source failures stored (`sus_src_pr`) | d0 | [TBD] | [TBD] | [TBD] | [TBD] |
| Wrong source points activated (`act_src_pr`) | d0 | [TBD] | [TBD] | [TBD] | [TBD] |
| Aborts by an active source point (`abort_src_pr`) | d0 | [TBD] | [TBD] | [TBD] | [TBD] |
| d = 0 cost per robot (`delta d_food`) | d0 | [TBD] | [TBD] | [TBD] | [TBD] |
| Wrong source points activated (`act_src_pr`) | d10 | [TBD] | [TBD] | [TBD] | [TBD] |
| Aborts by an active source point (`abort_src_pr`) | d10 | [TBD] | [TBD] | [TBD] | [TBD] |

Verdict (c): [TBD]

### 5.6 (e) Lockout side effects

Table 5. v5, per honest robot

| Metric | d0 N 20 | d0 N 40 | d0 Δ | d10 N 20 | d10 N 40 | d10 Δ |
| --- | --- | --- | --- | --- | --- | --- |
| Aborts on a true trail (`abort_true_pr`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| Lockout s after a true-trail abort, upper bound (`lock_true_s_pr`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| Abort to next pickup, s (`abort_to_pickup_s`) | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

| Item | Key | Value [95 %] |
| --- | --- | --- |
| v5 drop minus v3 drop | `dd / v5-v3 / 40-20 / d10 / G_pr_drop` | [TBD] |

Verdict (e): [TBD]

## 6. Root cause

Table 6. Candidate summary

| Candidate | Measurement | Number | File | Verdict |
| --- | --- | --- | --- | --- |
| (a) slower or rarer confirmation per decoy | `cover_time`, `act_share`, `d_ffollow_pr` | [TBD] | `results/real/scale/root_cause.csv` | [TBD] |
| (b) attack per decoy doubles | `det_reach_pd`, fixed-N G/N | [TBD] | `root_cause.csv`, `results/real/v5/g2_stats.csv` | [TBD] |
| (c) crowding, wrong source suspects | `act_src_pr`, d0 `d_food` | [TBD] | `root_cause.csv`, `verdict.json` | [TBD] |
| (d) loss per robot changes | `L_pr`, `R_share`, drop split | [TBD] | `root_cause.csv` | [TBD] |
| (e) lockout side effects | `lock_true_s_pr`, dd | [TBD] | `root_cause.csv` | [TBD] |
| (f) added: saved time does not become food | `d_ffollow_pr`, `d_pickup_pr` | [TBD] | `root_cause.csv` | [TBD] |

### 6.1 The mechanism

[TBD after the run. Numbered chain, one measured number per step.]

## 7. What a v6 no-ID design would need

Options only. The mechanism choice belongs to `system-architect`. The pick is the owner's.

[TBD: requirements follow the supported candidate. Draft frame below, to be cut to what the numbers support.]

| Option | What it changes | Answers | Trade-off |
| --- | --- | --- | --- |
| A. Shared confirmation through local stigmergy | A robot that fails at a point leaves a short-lived local mark (or lowers the trail there). A second failure by ANY robot confirms | (a): confirmations per decoy grow with N instead of shrinking | Detractors can lay or erase marks too. A crowded true source gets two failures from two robots faster, so (c) may return |
| B. Lower k with density | k = 1 when many robots are near, k = 2 otherwise | (a), if the density cue is local | Brings back the d = 0 cost of v3 (`failure_analysis.md` §1) where crowding is high |
| C. Time-based confirm | Count failures by one robot over a longer window, or keep pending points longer | (a), partly | Confirmation still per robot. Slower at N 40 if visits per robot fall |
| D. No change | Accept the per-robot gain at N 40 | none | RQ3 stays "no" for v5 |

- Theory link (inference, not measured at N = 40): the M6 ID arm (D-054) wins by pooling evidence across robots in a shared store. Option A pools evidence through the environment instead of IDs. The ID arm was not run at N = 40 (D-053), so its scaling is unknown.

## 8. Limits

- (a) and (b) are confounded inside `m7_scale`. The fixed-N check uses other seeds (221-260) and N 20 only.
- No k1t10 or k2t0 arm at N = 40. The lockout share of the drop is bounded by proxies and the dd contrast, not isolated.
- `lock_true_s_pr` is an upper bound: it assumes every true-trail abort costs the full t_lock.
- `robots.csv` has one row per second. false_share and crowding at an event use the row of that second.
- The stored point and the abort trigger are rebuilt from events. Heading is not used.
- Crowding is an association (`failure_analysis.md` §8).
