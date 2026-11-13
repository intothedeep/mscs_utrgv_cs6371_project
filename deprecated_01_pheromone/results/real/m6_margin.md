# M6 travel-time margin from saved logs (D-048 D1)

**Result: margin = 5.4 (p95 of actual over expected travel time, n = 2762 episodes). Fallback 1.5 if not frozen before the M6 prereg.**

- Status: method fixed before the run. Numbers come from `results/real/m6_margin.csv` only (`rules/answering.md` §3).
- Code: `tools/m6_margin.py`. Run: `OMP_NUM_THREADS=1 timeout 300 uv run python tools/m6_margin.py`.

## 1. Why

- The M6 ID-defense arm strikes a trail's group when a follower misses its deadline (`DESIGN_M6.md` §3.2).
- The deadline is t0 + margin × expected time. The margin sets how many honest follows strike honest robots (`DESIGN_M6.md` §8 R1).
- D-048 D1 picks a measured margin over the guessed 1.5, if it is frozen before the prereg commit.

## 2. Data

| Item | Value |
| --- | --- |
| Root | `runs/sweep_v2_lock0/` |
| Cells | d = 0, defense off (`d0_def0_*`), seeds 11 to 30, 20 runs |
| Code | v4, real runs (`mock: false`) |
| Files read | `manifest.json`, `events.csv` (honest rows). `robots.csv` is not needed |
| Kind | Saved simulation outputs, no new run |

## 3. Method (fixed before the run)

```
follow_start (t0, p0) ──► [peak, END_SEARCH allowed] ──► next pickup by the same robot (t1)
expected = |p0 - end| / 0.10 m/s + 15 s + 0
actual   = (t1 - t0) / 10 ticks per s
ratio    = actual / expected
margin   = ceil(10 × p95(ratio)) / 10
```

1. Constants come from `DESIGN_M6.md` Table 3. The script stops if a manifest disagrees (speed 0.10 m/s, `t_end` 15 s).
2. `est_extra_s` = 0. The off logs have no estimate feedback.
3. Percentiles: numpy default (linear interpolation).
4. One episode = one opened check that ends in a pickup.

### 3.1 Proxy for the trail end (not in the logs)

- The design takes `end` from the owner grid. The v4 logs have no owner grid. So `end` is a proxy.

| Proxy | `end` | Role |
| --- | --- | --- |
| `pick` | the follower's own pickup position | primary |
| `near` | the live honest trail end nearest p0. Live = an honest pickup, age 339 s or less at t0 | bound: tightest deadline (conservative) |
| `far` | the live honest trail end farthest from p0 | bound: loosest deadline |

- `pick` uses hindsight. The real deadline uses the provisional trail, which may sit at another source.
- The provisional end is one of the live ends. So `near` and `far` bracket the true expected time.
- `near` and `far` fall back to `pick` when no end is live.

### 3.2 Episode variants

- The logs cannot tell a re-follow of the same trail (no new check) from a new trail (a new check).

| Variant | Opens a check at | Role |
| --- | --- | --- |
| `each` | every `follow_start` | primary |
| `first` | the first `follow_start` since the robot's last drop | bound: every re-follow is the same trail |

### 3.3 Miss shares

| Share | Denominator |
| --- | --- |
| `miss_ep` | pickup-ending episodes |
| `miss_all` | all opened checks with a known outcome inside the run |

- A check with no later pickup uses the farthest source centre for `end`. So its deadline is the longest. Its miss count is a lower bound.
- A check whose deadline passes the last tick with no pickup is censored and counted apart.

## 4. Result

Table 1. Ratio distribution per variant and proxy. Source: `results/real/m6_margin.csv`, scope summary

| Variant | Proxy | n | p50 | p90 | p95 | p99 | Margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| each | pick (primary) | 2762 | 1.3229 | 3.3576 | 5.3048 | 7.8184 | 5.4 |
| each | near | 2762 | 1.4047 | 3.6558 | 5.7865 | 8.7226 | 5.8 |
| each | far | 2762 | 1.1016 | 2.8161 | 4.3281 | 6.5531 | 4.4 |
| first | pick | 1713 | 1.4941 | 3.3004 | 5.4509 | 7.7490 | 5.5 |
| first | near | 1713 | 1.5917 | 3.5914 | 5.8337 | 8.4722 | 5.9 |
| first | far | 1713 | 1.2831 | 2.7868 | 4.6804 | 6.5662 | 4.7 |

Table 2. Honest miss share at margin 1.5 and at the p95 margin

| Variant | Proxy | `miss_ep` 1.5 | `miss_ep` p95 | `miss_all` 1.5 | `miss_all` p95 | Censored (1.5 / p95) |
| --- | --- | --- | --- | --- | --- | --- |
| each | pick (primary) | 0.4178 | 0.0471 | 0.4426 | 0.0498 | 225 / 340 |
| each | near | 0.4518 | 0.0496 | 0.4752 | 0.0517 | 225 / 342 |
| each | far | 0.3316 | 0.0492 | 0.3601 | 0.0568 | 225 / 326 |
| first | pick | 0.4974 | 0.0479 | 0.5203 | 0.0501 | 157 / 235 |
| first | near | 0.5336 | 0.0479 | 0.5549 | 0.0495 | 157 / 236 |
| first | far | 0.3987 | 0.0502 | 0.4262 | 0.0574 | 157 / 226 |

- `miss_ep` at the p95 margin is about 5 % by construction.
- `miss_all` is the share that drives honest strikes (R1).

## 5. Reading

- All six margins equal: freeze that value. Primary = `each` / `pick`.
- Margins differ: 4.4 to 5.9 over the six variants (Table 1). Frozen: primary `each` / `pick` = 5.4 (D-049). The other 5 are report-only. The main session takes the options to the owner. No pick after the numbers.
- `near` gives the tightest deadline, so its margin is the conservative one for honest robots.
- The printed `MARGIN p95=` value is the rounded margin, not the raw p95. The CSV holds the raw p95.
- Margin much above 1.5: the deadline gets loose. Decoy victims may then pick up food in time by chance (`DESIGN_M6.md` §3.2).

## 6. Limits

- The trail end is a proxy (§3.1).
- Long episodes that start late have no pickup before tick 6000. They drop out of the ratio set. So the upper percentiles are biased low.
- `est_extra_s` stays 0. The id arm adds feedback, so real deadlines drift.
- Defense off, d = 0 only. Follow times may differ with decoys present.
