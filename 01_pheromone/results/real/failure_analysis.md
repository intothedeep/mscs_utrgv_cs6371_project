# Failure analysis: why the defense did not win back food (F1 v3, F2 v2 lockout)

Status: 2026-11-11. Numbers come from saved files named in each row.
New numbers come from `results/real/failure_analysis.csv` (`tools/failure_analysis.py`, run by the main session, 400 runs).
Ratios marked "computed" are divisions of two cell means from that CSV.

## 1. Conclusion

**The d = 0 cost comes from the base defense, not the lockout. Wrong suspects at crowded real sources cause it.**

- With `t_lock` 0 the d = 0 cost is -6.15 food [-8.25, -4.05] (seeds 11-30).
- On 30 seeds of v3-equal code it is -4.73 [-6.70, -2.80]. v3 had this cost all along. Its 10 seeds did not resolve it.
- The lockout alone adds -0.55 [-3.45, 2.30] at d = 0. The interval includes 0.
- Chain at d = 0, all measured:
  - 14.45 of 14.6 wrong suspects per run sit nearest a real source. 9.7 lie within 0.40 m of its centre, so the mask covers the food.
  - 102.55 of 102.6 cone aborts are triggered by those points.
  - Pickups fall by 7.2 per run [-9.35, -5.2].
- About one in four peaks at a real source ends with no food in 15 s (computed 25 to 27 %). The test turns each such peak into a suspect.
- Those failed peaks have more robots around the source (2.14 against 1.48). The peak position barely differs (0.41 m against 0.32 m).
- F1 shares this cost only in part. At d = 2 the wrong suspects drop to 5.4 per run. F1 also has a second cause: the 0.6 s re-follow loop at decoys.

```
 peak at a REAL source, crowd 2.1 robots (vs 1.5 when food is found)
        |  about 1 in 4 such peaks: no pickup in t_end 15 s
        v
 suspect stored at the source       d = 0: 14.45 per run, 9.7 within 0.40 m of the centre
        |
        +--> mask r_suspect 0.4 m covers the source centre
        +--> cone 10 deg, 1.0 m: 102.55 aborts per run, all at sources
                     |
                     v
        pickups -7.2 per run, carrying time -248 s        -> d = 0 cost -6.15 (F2)
        at d = 2: 5.4 such suspects, 24.7 such aborts     -> part of F1
        at d > 0: re-follow in 0.6 s after a decoy abort  -> other part of F1
```

Caption: Figure 1 shows the measured causal chain. Why: it locates where food is lost.

## 2. Why this analysis

- Owner rule: "if we fail we need to find why we have failed."
- Defense v2 failed its pre-registration (D-033, `results/real/v2/verdict.json`).
- The next design needs the cause, not another parameter guess.

## 3. Data used

| Root | Code | `t_lock` | Seeds | Runs | Summary files |
| --- | --- | --- | --- | --- | --- |
| `runs/sweep/` | v3 | absent (0) | 1-10 | 80 | `results/real/g2_stats.csv`, `defense_diagnostics.csv`, `events_by_cell.csv`, `summary.csv` |
| `runs/sweep_v2/` | v4 | 10 s | 11-30 | 160 | `results/real/v2/g2_stats.csv`, `results/real/v2/verdict.json` |
| `runs/sweep_v2_lock0/` | v4 | 0 | 11-30 | 160 | `results/real/v2_lock0/g2_stats.csv` |

- All runs are real simulation logs, 600 s, 20 honest robots plus d detractors.
- v4 with `t_lock` 0 equals v3 (invariance check, `CHANGELOG.md` v4 row). So `lock0` is v3 on new seeds.
- All mechanism numbers in §5 and §6 use `lock0`, seeds 11-30, unless a row names another root.
- Logging detail (controller source): a `suspect_add` row logs the robot's position at the end of END_SEARCH. The stored point is the robot's earlier peak position (`pheromone_forager_states.cpp` `EndSearch()`). The script uses the last `peak` row of that robot.

## 4. F1: v3 cut false-trail time but recovered no food

### 4.1 What the saved files show

Table 1. v3, seeds 1-10, defense on minus off, honest robot-seconds per run (`failure_analysis.csv`, scope `contrast`, root `v3:on-off`)

| Measure | d = 0 | d = 1 | d = 2 | d = 4 |
| --- | --- | --- | --- | --- |
| SEARCH | +84.6 | +570.2 | +789.6 | +902.5 |
| END_SEARCH | +19.6 | -312.2 | -552.0 | -423.0 |
| FOLLOW (all trails) | +20.6 | -192.5 | -179.4 | -412.5 |
| carrying | -212.0 [-352.5, -71.9] | +128.1 [-45.3, 279.9] | +126.5 [31.3, 231.5] | +17.0 [-168.4, 209.2] |
| pickups per run | -3.1 [-6.4, 0.5] | -1.0 [-5.1, 3.2] | +2.2 [-0.9, 5.0] | +0.6 [-4.5, 6.0] |

- Saved time moves into SEARCH. Pickups do not rise clearly at any d.
- Most of the saving is END_SEARCH at decoys, not false FOLLOW.

Table 2. v3 false-trail FOLLOW seconds per run (`results/real/defense_diagnostics.csv`)

| d | Off | On, before learning that decoy | On, after learning | On total | Change |
| --- | --- | --- | --- | --- | --- |
| 1 | 1219.1 | 342.5 | 682.5 | 1025.0 | -16 % |
| 2 | 1875.3 | 494.4 | 1118.9 | 1613.3 | -14 % |
| 4 | 2217.8 | 550.6 | 1264.7 | 1815.3 | -18 % |

- Robots keep following a false trail after they learned its decoy.
- Reason: after an abort the robot re-enters FOLLOW in 0.59 to 0.71 s (`abort_to_follow_s_mean`, v3).
- `TryEnterFollow()` tests the cone with the current yaw only. `Follow()` turns 90 degrees after an abort, so the cone is empty at once.

Table 3. Where suspects and aborts land, defense on, per run (`failure_analysis.csv`, scope `cell`)

| Root, d | Suspects at sources (`sus_cls_src`) | at decoys (`sus_cls_dec`) | elsewhere (`sus_other`) | Aborts by a source point (`abort_trig_src`) | by a decoy point (`abort_trig_dec`) |
| --- | --- | --- | --- | --- | --- |
| v3, 0 | 13.4 | 0 | 0.3 | 97.3 | 0 |
| lock0, 0 | 14.45 | 0 | 0.15 | 102.55 | 0 |
| lock0, 1 | 8.55 | 22.55 | 6.4 | 53.2 | 219.2 |
| lock0, 2 | 5.4 | 38.9 | 8.95 | 24.7 | 344.25 |
| lock0, 4 | 4.8 | 41.3 | 7.75 | 23.95 | 386.85 |

- At d = 0, every suspect and every abort is wrong.
- At d > 0 wrong source suspects fall to a third (5.4 of 14.45 at d = 2). Fewer robots reach true sources.
- Suspect precision at d = 2 (computed): 38.9 / (38.9 + 5.4) = 88 % against sources, 73 % against all suspects.

### 4.2 Reading

- F1 has two parts.
- Part 1, decoy side: the saved time does not become pickups. Robots re-follow learned false trails in 0.6 s (Table 2).
  - Evidence: the lockout breaks this loop. Lockout alone at d = 4: +3.25 food [0.9, 5.55]. At d = 2: +1.7 [-1.0, 4.45].
- Part 2, source side: the d = 0 cost of wrong suspects is still paid at d > 0, but smaller.
  - Inference (linear scaling, not measured): 5.4 / 14.45 of the d = 0 cost is about 2.3 food at d = 2. The v3 gain at d = 2 was +2.3 [-0.8, 5.1].
- Verdict for F1: part 1 **supported** (resolved at d = 4 by the lockout contrast). Part 2 **plausible, size not measured** at d > 0.

## 5. F2: lockout 10 s cost 6.7 food at d = 0

### 5.1 The premise does not hold

Table 4. d = 0 food (`results/real/v2/g2_stats.csv`, `results/real/v2_lock0/g2_stats.csv`, `failure_analysis.csv` scope `contrast`)

| Arm | Seeds | F(0, off) | F(0, on) | Cost on minus off | 95 % interval |
| --- | --- | --- | --- | --- | --- |
| `t_lock` 10 | 11-30 | 81.35 | 74.65 | -6.70 | [-9.70, -3.85] |
| `t_lock` 0 (v3 behavior) | 11-30 | 81.35 | 75.20 | -6.15 | [-8.25, -4.05] |
| v3-equal code (v3 + lock0) | 1-30 | | | -4.73 | [-6.70, -2.80] |
| Lockout alone (10 minus 0, defense on) | 11-30 | | | -0.55 | [-3.45, 2.30] |

- The cost is there without the lockout. The lockout's own share is not resolved.
- The failure condition fired on the base defense, not on the new mechanism.
- With `t_lock` 0: G(2) = +2.35 [-1.9, 6.35], G(4) = +3.95 [0.15, 7.55] (`results/real/v2_lock0/g2_stats.csv`).

### 5.2 Candidate causes

Table 5. Candidates for the d = 0 cost. `lock0`, (d = 0), seeds 11-30, per run, unless named

| Candidate | Measurement (`failure_analysis.csv`) | Number | Verdict |
| --- | --- | --- | --- |
| (a) `cone_abort` on true trails | `n_cone_abort`, `abort_true_trail`, `abort_trig_src`, `abort_pos_src_le150` | 102.6 aborts, 102.6 on true trails, 102.55 by a source point, 102.0 within 1.5 m of a source | **supported** |
| (b) lockout blocks re-entry to the true trail | `contrast` `lock10-lock0:on`, d 0: `food`, `n_pickup`, `n_cone_abort`, `abort_to_pickup_s_mean` | food -0.55 [-3.45, 2.30]. Pickups -1.0 [-3.85, 1.70]. Aborts -72.4 [-89.15, -55.5]. Abort-to-pickup +16.9 s [1.85, 32.03] | **not supported** as the cause. Each abort delays food 17 s longer, but aborts fall by 72. Net effect not resolved |
| (c) suspect masks cover real sources | `sus_src_le040`, `_le055`, `_le065`, `_le100` against `n_suspect_add` | 9.7 (66 %) within 0.40 m: mask covers the centre. 12.8 (89 %) within 0.65 m: mask touches the disc. 14.45 within 1.0 m | **supported** |
| (d) fewer pickups | `contrast` `lock0:on-off`, d 0: `n_pickup`, `carry_s`. `fs_to_pickup` on against off | pickups -7.2 [-9.35, -5.2]. Carrying -247.8 s [-307.3, -191.8]. Follows ending in a pickup 37.15 against 41.55 | **supported**. Most of the food loss is lost pickups |
| (e) crowding at real sources | `pkcrowd_suspect` against `pkcrowd_pickup` (other robots within 0.5 m during END_SEARCH) | 2.14 against 1.48. v3: 2.11 against 1.29. lock10: 1.99 against 1.31. Defense off, failed peaks: 2.20 against 1.58 | **supported as an association**. Same sign in all roots and with the defense off. Not shown causal |
| Peak offset (added) | `pkdist_suspect` against `pkdist_pickup`, `sus_src_le055` | 0.41 m against 0.32 m. 12.6 of 14.45 (87 %) within reach (0.55 m) | **not supported** as the main cause |
| Dose (exploratory) | `dose` slope and r, cost against `sus_src_le100` | lock10 -1.38 (r -0.67). lock0 -0.60 (r -0.41). v3 +0.10 (r 0.11). 30 seeds -0.23 (r -0.19) | **unclear**. Sign and size differ by seed set |

## 6. Root cause

### 6.1 The mechanism

1. The suspect test is "valid peak, then 15 s END_SEARCH with no pickup" (DESIGN §3.4 rule 1).
2. A real source cannot be depleted (DESIGN §3.1). Yet near-source peaks fail often.
   - Defense off, d = 0: 19.0 of 63.4 near-source peaks end without food (computed 30 %, `pk_src_neither`, `pk_src_pickup`).
   - Defense on: of 53.95 near-source peaks that end in a pickup or a suspect, 14.45 become suspects (computed 27 %, end-test false-positive rate).
3. Failed peaks have more robots near the source (Table 5, e). The peak is within reach of the disc in 87 % of them.
4. The stored point lies within 0.40 m of the source centre in 66 % of cases. The mask then hides the source itself.
5. True trails converge on the source. The cone fires on them: 102.55 aborts per run.
6. Memory has no expiry below 16 points. A wrong point stays for the rest of the run.
7. Result: 7.2 fewer pickups and 6.15 less food per run.

- Root-cause hypothesis "low suspect precision because the end test cannot tell a crowded true source from a decoy": **supported at d = 0**.
- Depletion: ruled out by design. Peak offset: **not supported**. Crowding: **supported as an association**.
- As the common cause of F1 and F2: **partly supported**. It explains F2. It explains only part of F1 (§4.2).

### 6.2 What a fix must achieve

- The dose slope does not resolve (Table 5). So this memo gives no precision number from it.
- Use direct gates, written before the next run:
  - The d = 0 cost interval includes 0.
  - Decoy suspects at d = 2 (`sus_cls_dec`, 38.9 per run now) stay above a share written before the run.
- Context, inference only: the mean ratio is 6.15 / 14.45 = 0.43 food per wrong suspect. This assumes a linear cost through 0, which the dose rows do not confirm.
- Current precision against sources: 0 % at d = 0, 88 % at d = 2 (computed, Table 3). The fix must raise both.

## 7. Implications for the next track

### 7.1 Options (the mechanism choice belongs to `system-architect`, the pick to the owner)

Table 6. Options that attack suspect precision

| Option | What it changes | Expected effect | Trade-off |
| --- | --- | --- | --- |
| A. Two failures before a point is active | A point needs merge count ≥ 2 (counts already exist) | One crowded failure no longer marks a source | Decoys are learned later. Less time saved at d > 0 |
| B. Suspect expiry | A point is dropped after T s | A wrong suspect costs for T s, not the run | Decoys are relearned. Repeated waste at decoys |
| C. Pickup clears a point | A pickup within r of a stored point deletes it | Wrong suspects at real sources self-correct | The mask covers the centre in 66 % of cases, so the robot rarely finds the trail back |
| D. Longer or wider END_SEARCH | Larger `t_end` or end radius | A crowd has time to clear | More time per decoy visit |
| E. Keep the lockout (re-follow fix) | `t_lock` > 0 | Helps the decoy side (+3.25 food at d = 4) | Does not touch the d = 0 cost |

- **Evidence favours A, combined with E.** Failures at real sources are crowd-linked and so likely transient. A decoy fails every visit. A second, independent failure separates the two. E keeps the resolved decoy-side gain.
- Check before design, from saved files: the share of wrong source points that a robot would hit twice (merge count ≥ 2). This needs one added metric in `failure_analysis.py`.

### 7.2 How the next design can be tested

1. Fresh seeds only. Seeds 11-30 are spent (prereg kill rule). New tuning seeds and new confirmation seeds.
2. Mechanism check first, cheap: (d = 0, on) and (d = 2, on), 10 tuning seeds.
   - Primary metric: wrong suspects per run at d = 0 (`sus_cls_src`, 14.45 now).
   - Second line: decoy suspects at d = 2 (`sus_cls_dec`) above a share of 38.9, written before the run.
3. Pre-register both lines before the full sweep: G(2) lower bound > 0, and the d = 0 cost interval includes 0.
4. Report the attribution contrast (new mechanism against v3 behavior) at d = 0 and d = 2, on the same seeds.
5. Run `failure_analysis.py` on every new arm as its mechanism report.

## 8. Limits

- The trigger point of a `cone_abort` is not logged. `abort_trig_*` rebuilds each robot's memory from its own events. It ignores heading.
- A `peak` row does not say valid or invalid. A near-source peak with neither pickup nor suspect is treated as invalid.
- `robots.csv` has one row per second. Crowding and false_share at an event use the row of that second.
- Crowding is an association. Crowded sources may also be the busiest sources, so the link may be indirect.
- The d > 0 size of the source-side cost (§4.2) is a linear-scaling inference, not a measurement.
