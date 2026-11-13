# M5 design: defense v5, confirm-twice x lockout (T-A)

Status: 2026-11-11, system-architect, task M5-02. Spec: `decisions/2026-11-11_fable_tracks.md` "M5 = T-A" (D-039, D-043).
Kill check passed: build option A, not A' (D-046, `results/real/v5_killcheck.csv`).

## 0. Mission block (quoted from `PLAN.md`, lines for M5 only)

- Mission: Keep pheromone foraging swarms trustworthy against false trails as they scale, change and learn. (Fable, owner-delegated, 2026-11-11, D-034)
- Vision: A chart sets our no-ID defense beside Prof. Lu's ID-based defense, each failure explained. (Fable, owner-delegated, 2026-11-11, D-035)
- Constraints: no local training. The main session builds and runs every run locally, one core, sequential (D-002, D-013, D-031, D-044). Agents never build, run or commit.
- G3: By 2026-11-28, 3 of 3 run tracks (T-A, T-B, T-D) have a committed `verdict.json`, plus a root-cause memo for each fail. (Fable, owner-delegated, 2026-11-11, D-036)
- Goals (question-type): [RQ.md](./RQ.md): 3 open (D-037)
- S2 → G3, RQ1 to RQ3: run tracks in order, step 0, T-A, T-B, T-D, then T-E and T-F. Each track pre-registered on its own fresh seed block (Fable, owner-delegated, 2026-11-11, D-038, D-043). Listed alternatives: T-B first, T-D first. T-C not run (D-041).
- M5 → S2 → RQ1: T-A, defense v5 confirm-twice x lockout, by 2026-11-17. Exit: `results/real/v5/verdict.json` on seeds 221 to 260, pass or fail, plus a root-cause memo on fail (TASKS.md "M5 exit"). cycle 0/2; recovery 0/2

RQ1: does a second independent failure before marking remove the d = 0 cost and keep G(2) above 0?

## 1. The v5 rule

```
 valid peak, 15 s END_SEARCH, no food
        |  AddSuspect(peak)  (unchanged from v4)
        v
 first stored point within r_merge 0.3 m? --yes--> centroid update, Count + 1
        | no
        v
 append {peak, Count 1}; size > n_mem 16 --> erase index 0 (oldest inserted)

 Count <  confirm_k : PENDING  (held, no mask, no cone)
 Count >= confirm_k : ACTIVE   (mask r_suspect 0.4 m, cone 10 deg x 1.0 m)
```

1. `AddSuspect` is not changed. Every failure calls it, as in v4.
2. A new point is stored with `Count` 1 in the same 16-slot vector. It is pending while `Count < confirm_k`.
3. Merge: the new failure goes into the first stored point, in vector order, within `r_merge` of that point's current centroid. Pending and active points are both candidates.
4. The merge sets the centroid to the count-weighted mean and adds 1 to `Count`. The point becomes active in the same call when `Count` reaches `confirm_k`. The mask applies from the next `MaskSuspects()` call.
5. Ageing: no timer. A pending point never expires by time.
6. Eviction: one first-in-first-out queue for pending and active points. Order is insertion order. A merge does not refresh a point's place. Size above 16 erases index 0, pending or active.
7. Only `MaskSuspects()` and `IsConeHit()` change. Both skip a point with `Count < confirm_k`. `TryEnterFollow()` uses `IsConeHit()`, so it skips pending points too.
8. "Same robot": memory is private (DESIGN §3.4). Two failures by different robots never merge.

Why no ageing for pending points: the kill check replays exactly this queue (`tools/v5_killcheck.py` `replay`, first match in insertion order). Any other eviction breaks the model behind D-046.
Why eviction is rare: at d = 2 the kill check counts the pending points held at run end (`pending_end`, scope `cell`, `off_lock0`, `valid/A`). That count is per run, summed over 20 robots. Per robot it is far below 16.

### 1.1 Parameters and naming

| Item | Value |
| --- | --- |
| XML | `<defense ... confirm_k="1\|2" t_lock="0\|10">` |
| `confirm_k` | optional, default 1, integer ≥ 1. A missing attribute loads as 1, so v4 files still load |
| k = 1 | v4 behavior: every point is active at `Count` 1 |
| Manifest key | `controller_defense_confirm_k` (written by `run_info_reader.cpp`, like `t_lock`) |
| `code_version` | `v5` |
| M6 coordination | M6 (`DESIGN_M6.md`) owns `defense_mode`. v5 needs only that `confirm_k` is read whenever the defense is on |
| Note for the main session | Both tracks edit `pheromone_forager_params.cpp`, `.h`, `sweep_params.py` and the template. The merge order is the main session's call |

### 1.2 Schema impact: none

- No new event, column or manifest key in `schema.py`. `defense` stays 0/1 (D-030).
- `suspect_add` still fires on every `AddSuspect` call. It now means "a failure was recorded", pending or active. Without it no replay can rebuild merges.
- `ticks.csv` `suspects_total` still counts held points, pending included (`GetSuspectCount()` unchanged).

## 2. Invariance: k = 1, `t_lock` 0 equals v4

| Saved v4 cell (`runs/sweep_v2_lock0/`) | Why this cell |
| --- | --- |
| `20261111-115700_d0_def1_s11` | defense on at d = 0: masks and cones on real sources |
| `20261111-115700_d2_def1_s11` | defense on at d = 2: decoy points and merges |

- Rerun both on v5 code with `confirm_k` 1, `t_lock` 0 and the frozen values (`sweep_plan.frozen_values()`), into `runs/invariance_v5/`.
- Do not use `make_sweep.py --cell` alone. The template holds `alpha_cone_deg` 15, the frozen value is 10.
- Gate: `food_collected` equals the saved manifest value for both cells. The check also asserts equal `events.csv` row counts and equal params except `confirm_k`.
- Tool: `tools/confirm_v5.py --stage invariance` runs both cells and prints the comparison (task 8).
- A mismatch stops M5 and goes to `recover` (TASKS M5-05).

## 3. Mechanism check, seeds 201-210 (reported, no pick)

- Arms: (k2, t10) and its twin (k1, t10). Cells (d 0, on) and (d 2, on). 2 x 2 x 10 = 40 runs, root `runs/v5_check/`.
- Why a twin: the legacy and the activation counts have different definitions. Only a same-seed k = 1 twin gives a fair comparison. Why t10: it is the primary arm (§4).

Definitions, per run, from `manifest.json` and `events.csv` (honest robots, file order):

| Metric | Exact definition |
| --- | --- |
| stored point | for a `suspect_add` of robot r: (x, y) of r's last `peak` row before it |
| class(p) | landmarks = `layout.sources` and `layout.decoys[:n_decoys_used]`. Nearest landmark within 1.00 m. Source if source distance ≤ decoy distance. Else decoy. None within 1.00 m: other |
| `sus_cls_src`, `sus_cls_dec` | count of `suspect_add` rows whose stored point is class source / decoy. Same as `tools/failure_analysis.py` `run_metrics`. Under v5 it counts failures, merges included |
| `act_cls_src`, `act_cls_dec` | replay each robot's stored points with the §1 queue. Count the calls where `Count` reaches `confirm_k` (k = 1: every append). Class of the centroid after that call |
| replay check | replayed held points, summed over robots, equal `ticks.csv` `suspects_total` at every tick. A mismatch marks the run "replay inexact" |

- The replay check catches a wrong merge-or-append decision only. A match does not prove the activation counts.

- Mechanism reading: `act_cls_src` at d = 0 and `act_cls_dec` at d = 2, k2 against k1, same seeds.
- Never compare `act_*` with the legacy 14.45 or 38.9 (`failure_analysis.md` Table 3). Those are `sus_cls_*`.
- Do not reuse `failure_analysis.py` `abort_triggers` as the replay. It merges into the nearest point, the controller into the first.
- Also reported: `n_cone_abort`, `food`. Output: `results/real/v5/mechanism.csv` and `mechanism.md`. No value is picked.

## 4. Confirm design, seeds 221-260

| Arm | `defense` | `confirm_k` | `t_lock` | Role |
| --- | --- | --- | --- | --- |
| off | 0 | 1 (inert) | 0 (inert) | baseline for G and the d = 0 cost |
| k1t0 | 1 | 1 | 0 | v4 = v3 behavior |
| k1t10 | 1 | 1 | 10 | v2 lockout |
| k2t0 | 1 | 2 | 0 | confirm only |
| **k2t10** | 1 | 2 | 10 | **primary arm, judged** |

- 5 arms x d 0, 1, 2, 4 x 40 seeds = 800 runs. One root: `runs/v5_confirm/`.
- `is_done()` compares `confirm_k` and `t_lock`, so 4 on-arms share one root safely.
- Order: off and k2t10 first, all seeds (320 runs). Then the other 3 arms (480 runs). The judge still needs all 800. The order only gives an early wall-time estimate and the judged pair first.
- Inert values on off runs make the key (k, t, d, def, seed) unique.

Why k2t10 is primary, named before any run:
- RQ1 asks for k = 2 with the decoy side kept. k = 2 delays decoy learning (§7).
- The lockout is the only resolved decoy-side gain: +3.25 food at d = 4 (`failure_analysis.md` §4.2).
- Its d = 0 share was not resolved: -0.55 [-3.45, 2.30]. So t10 does not carry the d = 0 cost.
- 10 s is the v2 tuning pick (5, 10, 20 s tried on seeds 107-116). It is the only nonzero value confirmed on 20 seeds (D-033). No new tuning.

## 5. Prereg text (`prereg/defense_v5.md`, → RQ1)

| Line | Value |
| --- | --- |
| Metric | G(2) = F(2, k2t10) − F(2, off), seeds 221-260. Paired percentile bootstrap on seed, 10,000 resamples, 95 % (`tools/g2_stats.py`) |
| Threshold | lower bound of the G(2) interval > 0 |
| Contrast | main: k2t10 against off at d = 0, 1, 2, 4. 2 x 2 main effects at d = 0 and d = 2 (below). G of the other 3 arms: reported only |
| Failure | the G(2) interval includes 0, or the upper bound of the d = 0 cost F(0, k2t10) − F(0, off) is below 0. Then v5 is reported as null and M5-09 runs |

Main effects, per seed s at d (F = `food_collected`, on arms):

```
E_k(d, s) = ½ [F(k2t0) − F(k1t0)] + ½ [F(k2t10) − F(k1t10)]
E_t(d, s) = ½ [F(k1t10) − F(k1t0)] + ½ [F(k2t10) − F(k2t0)]
I(d, s)   = [F(k2t10) − F(k1t10)] − [F(k2t0) − F(k1t0)]     (reported)
```

- Each: mean over 40 seeds, same bootstrap. `paired_diff_interval(a, b)` with a = ½(k2t0 + k2t10), b = ½(k1t0 + k1t10) gives E_k.
- No pass or fail on the main effects. Seeds 221-260 are used once. A rerun only fills missing cells.
- Invariance (§2) passes before the first M5 run. The prereg commit is older than the first `runs/v5_check/` run.
- Mechanism check: seeds 201-210, arms k2t10 and k1t10, cells (0, on) and (2, on). Reported only, no pick.
- Roots: `runs/invariance_v5/`, `runs/v5_check/`, `runs/v5_confirm/`. Tools: `confirm_v5.py`, `v5_mechanism.py`, `judge_v5.py`.

## 6. Developer tasks

| # | Files | Change |
| --- | --- | --- |
| 1 | `src/controllers/pheromone_forager/pheromone_forager.h` | `SParams::ConfirmK` (UInt32). Private `bool IsActive(const SSuspect &) const` |
| 2 | `.../pheromone_forager_params.cpp` | `GetNodeAttributeOrDefault(tDef, "confirm_k", ...)`, default 1. Stop on a value below 1 |
| 3 | `.../pheromone_forager_defense.cpp` | `MaskSuspects()`, `IsConeHit()` skip pending points. `AddSuspect` untouched |
| 4 | `src/loop_functions/pheromone_loop_functions/pheromone_loop_functions_log.cpp` | `CODE_VERSION = "v5"` |
| 5 | `src/experiments/pheromone_headless.template.argos` | `confirm_k="1"` beside `t_lock="0"` |
| 6 | `tools/sweep_params.py` | `PARAM_SITES["confirm_k"]` under `{_CTRL}/defense` |
| 7 | `tools/v5_common.py` (new) | arms, `CHECK_SEEDS` 201-210, `CONFIRM_SEEDS` 221-260, roots, `PREREG`, `VERDICT`. `read_food()` keyed (k, t_lock, d, def, seed). Seed guard: refuse 1-30, 101-116 and any seed outside 201-210, 221-260. Imports `run_food`, `load_manifests` like `v2_common.py` |
| 8 | `tools/confirm_v5.py` (new) | `--stage check\|confirm\|invariance`, `--run`. Builds jobs with `frozen_values()` plus k and t, calls `plan_runs()`. `require_committed(PREREG)` and the seed guard, except `invariance` |
| 9 | `tools/v5_mechanism.py` (new) | §3 metrics. Imports `classify` from `tools/v5_killcheck.py`. Own `replay_k(points, k, r_merge, n_mem)`: the same loop as `v5_killcheck.replay`, but k is a parameter. It records the activation tick and centroid at any k, and each point's insert and evict tick for the held-count series. `v5_killcheck.py` stays unchanged (D-046 evidence) |
| 10 | `tools/judge_v5.py` (new) | §5. Pass logic copied from `judge_v2.py`. Adds per-seed values, E_k, E_t, I at d 0 and 2, prereg path, own sha256. Writes `g2_stats.csv` (all 4 on-arms against off, via `g2_rows`) and `verdict.json`. Refuses unless all 800 runs exist |
| 11 | `CHANGELOG.md` | v5 row with the invariance evidence |
| 12 | `prereg/defense_v5.md` | §5 text, written by developer, committed by the main session |

- `v2_common.py` and `judge_v2.py` stay unchanged. The M4 verdict holds their sha256.
- Outputs: `results/real/v5/mechanism.csv`, `mechanism.md`, `g2_stats.csv`, `verdict.json`.

## 7. Expected result

| Number (saved) | Source | Reading |
| --- | --- | --- |
| predicted active source points at d = 0, k = 2 | D-046, `v5_killcheck.csv` `act_src` | far below the 7.2 line |
| source points at d = 0, k = 1 replay | same file, `pts_src` | the k = 1 reference, same definition |
| decoy points active at d = 2 | same file, `act_dec` against `pts_dec` | about half reach k = 2 without masks |

- d = 0 cost shrinks. Its interval may include 0.
- G(2) may drop: each robot needs two visits per decoy. Decoy points need `dec_robots_ge2` of `dec_robots_ge1` robots.
- A split result is likely: cost fixed, G(2) interval includes 0. That is a fail, and M5-09 explains it.
- E_k at d = 0 is expected positive. E_t at d = 2 may not resolve (v2 attribution included 0).

## 8. Risks

| Risk | Effect | Response |
| --- | --- | --- |
| Run time: worst 800 x 300 s ≈ 67 h before 2026-11-17 | M5 slips, M7 kill fires | off and k2t10 first. Report wall time after seed 221 |
| CSV rounding near `r_merge` | replay misses a merge | replay check against `suspects_total`. Mark inexact runs |
| Kill check ran on off logs | masks change later returns. `act_src` may overcount | the mechanism check measures it on v5 |
| Pending points never expire | a stale pending point merges a late failure | rare at these counts. M5-09 can test it |
| Shared files with M6 | merge conflict, wrong `code_version` | merge order: main session's call (§1.1) |
| `confirm_k` not in manifest | judge cannot key arms | `read_food()` stops on a missing key |
