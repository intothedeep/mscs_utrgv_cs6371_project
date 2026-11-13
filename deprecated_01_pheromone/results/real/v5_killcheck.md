# M5 step 0: kill check for defense v5 (confirm-twice)

Status: 2026-11-11. Method and threshold written before the run. Numbers filled from `results/real/v5_killcheck.csv` after the run (project-end review P-2).
Numbers come from `results/real/v5_killcheck.csv` (`tools/v5_killcheck.py`, run by the main session).

## 1. Conclusion

**Verdict: proceed with A, k = 2 (D-046).** Primary `valid/A` confirmed at sources 1.70 [1.20, 2.20] per run. Upper `all/A` 2.50 [1.95, 3.00].

## 2. Why

- M5 spec (`decisions/2026-11-11_fable_tracks.md`): check the kill rule before any v5 code.
- Option A (`failure_analysis.md` §7.1): a point marks only after a second failure.
- It helps only if one robot rarely fails twice at the same real source.
- Kill rule (Fable, pre-registered): confirmed wrong points at d = 0 above 7.2 per run.
- 7.2 is half of 14.45, the wrong suspects per d = 0 run with v3 behavior (`failure_analysis.md` Table 3).
- Above 7.2: switch to A' ("a pickup within r_merge clears a pending point").

## 3. Data

| Root | Code | Defense | Seeds | d | Role |
| --- | --- | --- | --- | --- | --- |
| `runs/sweep_v2_lock0/` | v4 | off | 11-30 | 0, 2 | primary (kill rule) |
| `runs/sweep/` | v3 | off | 1-10 | 0, 2 | supplementary, outside the rule |
| `runs/sweep_v2_lock0/` | v4 | on, `t_lock` 0 | 11-30 | 0 | calibration of the validity rebuild |

- `runs/sweep_v2/` def 0 holds the same off runs. It is not pooled. The script checks food per (d, seed): scope `check`.
- Why off runs: under k = 2 a pending point does not mask. Until activation, robots behave as with the defense off.

## 4. Method

```
 off log: peak (t, x, y) -- no pickup by t + t_end --> failure
      |  validity rebuilt (off logs have no flag)
      v
 private memory replay, per robot (copy of AddSuspect)
      |  merge: first point within r_merge 0.3 m, count-weighted centroid
      |  n_mem 16, oldest dropped
      v
 point reaches count 2 --> "confirmed" (active under k = 2)
      |  class at activation: nearest landmark within 1.0 m
      v
 act_src per run (d = 0)  --> compare with 7.2
```

1. Failure: a peak with no pickup by the same robot within `t_end` 15 s. Windows past the run end are dropped.
   - The timeout fires at exactly +150 ticks (sample: `hb_3`, peak 3567, `follow_start` 3718).
   - The 2-tick slack applies only to matching `suspect_add` in the calibration.
2. Stored point: the peak position, as in `failure_analysis.md` §3.
3. Validity, because only a valid peak calls `AddSuspect`:
   - `dur`: peak tick minus the last `follow_start` tick ≥ `t_follow_min` × 10. Exact.
   - `valid`: `dur`, and `here` at the peak ≥ 2 × max(`here` at follow start, `theta_on`). Uses 1 s rows.
   - `all`: every failed peak. Upper bound.
4. Memory replay: every kept failure enters memory, not only those near sources.
5. Policy A: a point is active at count 2. Policy A' also clears a pending point on a pickup within `r_merge`. A' is context only.
6. Calibration: on defense-on d = 0 runs, the observed `suspect_add` is ground truth. Script reports tp, fp, fn, tn per variant.
   - The controller tests the masked reading. `robots.csv` logs the raw one.
   - So subset `no_mask` (peaks before the robot's first `suspect_add`) is the clean test. `all_peaks` is shown too.
7. The verdict fails closed: fewer than 20 primary runs or a non-finite mean prints `NO VERDICT`.

## 5. Pre-registered reading

| Item | Value |
| --- | --- |
| Primary metric | `act_src`, variant `valid/A`, root `off_lock0`, d = 0, mean over 20 runs |
| Upper bound | `act_src`, variant `all/A`, same cell |
| Kill line | mean > 7.2 |
| Both above 7.2 | switch to A' |
| Both at or below 7.2 | proceed with A (k = 2) |
| Opposite sides | straddle: report both, Fable decides |
| Interval | 95 % bootstrap over seeds, context only. The rule uses the mean |

## 6. Results

Table 1. d = 0, `off_lock0`, per run (scope `cell`)

| Variant / policy | Failures at sources (`fail_src_k1`) | Robot points at sources (`pts_src`) | Confirmed at sources (`act_src`) | 95 % interval | 3rd+ failures (`fail3plus_src`) | Active seconds (`act_src_s`) |
| --- | --- | --- | --- | --- | --- | --- |
| valid / A | 16.95 | 15.00 | 1.70 | [1.20, 2.20] | 0.25 | 286.86 |
| dur / A | 17.15 | 15.10 | 1.80 | [1.30, 2.30] | 0.25 | 339.32 |
| all / A | 18.70 | 15.70 | 2.50 | [1.95, 3.00] | 0.50 | 502.41 |
| valid / A' | 16.95 | 15.70 | 1.05 | [0.65, 1.45] | 0.20 | 193.50 |

- `fail_src_k1` is not expected to match 14.45. Off runs have no masks, so repeat failures inflate it. Table 2 is the check.
- Share confirmed (computed): `act_src` / `pts_src` = 1.70 / 15.00 = 0.11 (`valid/A`).

Table 2. Calibration, `on_lock0` d = 0, summed over runs (scope `calib_sum`)

| Variant, subset | tp | fp | fn | tn |
| --- | --- | --- | --- | --- |
| all, no_mask | 212 | 31 | 0 | 0 |
| dur, no_mask | 212 | 22 | 0 | 9 |
| valid, no_mask | 212 | 21 | 0 | 10 |
| valid, all_peaks | 275 | 25 | 17 | 157 |

Table 3. d = 2, `off_lock0`, per decoy (scopes `cell` and `cell_decoy`, variant `valid/A`)

| Measure | Value |
| --- | --- |
| Robots with ≥ 1 failure (`dec_robots_ge1`) | 12.80 |
| Robots that confirm (`dec_robots_ge2`) | 8.85 |
| First failure, any robot (`first_fail_s`) | 64.56 s |
| First confirmation, any robot (`first_confirm_s`) | 127.23 s |
| Gap, first to second failure (`gap_mean_s`) | 107.87 s |
| Decoys with a confirmation (n of `cell_decoy`) | 40 / 40 |

- Delay of decoy learning under k = 2: `first_confirm_s` minus `first_fail_s`.

## 7. Limits

- v5 pending points are assumed to merge like the current `AddSuspect`.
- The `valid` test uses `here` at 1 s resolution. Table 2 measures its error.
- Off runs ignore masking after activation. A robot's first activation is unaffected.
- Its later points may be: once a point is active, that robot returns to the source less. So `act_src` may overcount.
- A confirmed point may later be evicted. `act_src` counts it once. `act_src_s` gives its active time.
- The d = 2 numbers predict decoy learning without masks. With masks, robots may return less.
