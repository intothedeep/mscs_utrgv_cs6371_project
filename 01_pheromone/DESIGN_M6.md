# M6 (T-B): ID-based adapted arm of the Luna and Lu defense: Design

- Author: system-architect, 2026-11-11. Status: draft for M6-02. Open decisions: §10.
- Source paper: Luna and Lu, Towards Autonomous Robotic Systems conference 2024 (TAROS 2024), pp. 307 to 317. Read via `research/taros_defense_spec.md` (rows A1 to G1, assumptions 1 to 13).
- Spec: `decisions/2026-11-11_fable_tracks.md` "M6 = T-B", D-040, D-043, D-045.
- Base design: `DESIGN.md`. Its §4 schema stays the single contract. This file adds no column to it.
- Name: "adapted arm". This is not a replication (D-040).

## 0. Mission block (quoted from `PLAN.md`)

> - Mission: Keep pheromone foraging swarms trustworthy against false trails as they scale, change and learn. (Fable, owner-delegated, 2026-11-11, D-034)
> - Vision: A chart sets our no-ID defense beside Prof. Lu's ID-based defense, each failure explained. (Fable, owner-delegated, 2026-11-11, D-035)
> - Constraints: no local training. The main session builds and runs every run locally, one core, sequential (D-002, D-013, D-031, D-044). Agents never build, run or commit.
> - G3: By 2026-11-28, 3 of 3 run tracks (T-A, T-B, T-D) have a committed `verdict.json`, plus a root-cause memo for each fail. (Fable, owner-delegated, 2026-11-11, D-036)
> - S2 → G3, RQ1 to RQ3: run tracks in order, step 0, T-A, T-B, T-D, then T-E and T-F. Each track pre-registered on its own fresh seed block (Fable, owner-delegated, 2026-11-11, D-038, D-043). Listed alternatives: T-B first, T-D first. T-C not run (D-041).
> - M6 → S2 → RQ2: T-B, ID-based adapted arm, by 2026-11-22. Exit: `results/real/id_arm/verdict.json` on seeds 321 to 360, plus a root-cause memo on fail. Kill: no gate-ready code by 2026-11-21. cycle 0/2; recovery 0/2

- G1, G2 and M1 to M5, M7, M8 lines: see `PLAN.md`. `PLAN.md` wins if the two differ.
- RQ2: "On one grid, one attack and one seed block, how do the no-ID defense and the ID-based defense differ in food and false positives?"
- Every choice below serves M6 → RQ2 → Vision. No line here changes the mission block.

## 1. Adapted, not replicated

Table 1. TAROS 2024 element, our grid version, and why. Tag: verified = printed in the paper. Inference = our reading or our choice

| # | TAROS 2024 element | Our grid version | Why | Tag |
| --- | --- | --- | --- | --- |
| 1 | Waypoints with xy and creator ID (p. 310) | Per-cell owner ID beside each grid layer, plus one trail record per deposit run | Our trails are grid cells. A cell has no ID unless we store one | paper: verified. Grid: inference |
| 2 | One clustering point per waypoint (p. 310) | One point per trail: its end, the first deposit of a run | One trail fills about 20 cells. Clustering every cell would make one trail a cluster by itself | inference |
| 3 | Density clustering, eps = robot search radius, minPts 2 (p. 310, p. 312) | Same algorithm, minPts 2. eps = 0.3 m, our END_SEARCH radius (§4) | Our robot's search radius is the END_SEARCH radius `end_radius` | minPts: verified. eps value: inference |
| 4 | Graph of clusters, edge on a shared creator ID (p. 310) | Same | No change needed | verified |
| 5 | Robot follows one waypoint | A gradient follower gets a trail at `follow_start`, confirmed at its next peak (§3.2) | A grid follower has no single trail | inference |
| 6 | Estimated travel time from distance and average speed (p. 310) | Distance to the assigned trail end / 0.10 m/s, plus `t_end` 15 s, times margin 1.5 (§4) | `t_end` is our END_SEARCH time. Without it every follow is late | formula form: verified. Values: inference |
| 7 | "Return" ends a check. A captured robot never returns (p. 309) | Any pickup before the deadline closes the check with no strike. A late pickup counts only near the assigned cluster | Our decoys do not capture. A fooled robot can find food later by chance | inference |
| 8 | Strike to every creator in the group on a missed return (p. 311) | Same | Faithful. It drives the d = 0 risk (§8 R1) | verified |
| 9 | 5 strikes isolate (p. 311) | 5 | Paper value, tuned for 24 robots and λ = 4. Kept, not re-tuned | verified |
| 10 | Late return updates the estimate and removes a strike or reintegrates (p. 311) | Same. Estimate update gain 0.5 (§4) | Gain not printed | rule: verified. Gain: inference |
| 11 | Isolated robots park at the arena edge (Fig. 1) | The robot keeps moving. The store zeroes its owned cells and drops its future deposits | A parked state needs a new `state` name in `robots.csv`. That is a schema change, which sends the slice back to MVP1 (`DESIGN.md` §5) | inference |
| 12 | Isolation is "temporary", length not printed | Ends on a late return (paper) or after 120 s (ours) | Without a timer, a fully isolated group can never come back (§8 R1) | inference |
| 13 | Who runs the defense: not printed | The loop functions, as a central trail store | The defense needs every trail and its creator in one place | inference (assumption) |
| 14 | Poisson lay decision (p. 309) | Our deposit rule stays (`DESIGN.md` §3.2) | Not part of the defense | inference |

- Assumption, stated once: the loop functions act as a central trail store. A real swarm would need a nest server or broadcast. The T-E table (M8) lists this cost.
- The controller stays unchanged. It never sees an ID, a strike or an isolation flag (`DESIGN.md` §2.1).

## 2. Components and data flow

```
Figure 1. ID arm inside one tick (new parts marked *)

 PreStep (unchanged)                       pickups of this tick ----------------+
   evaporate, pickup/drop, write readings                                       |
        |                                                                       |
 ControlStep (controller unchanged): sets follow_start, peak, deposit request   |
        |                                                                       |
 PostStep                                                                       v
   (1) deposits ----> PheromoneGrid ------> *OwnerGrid  owner[2][1600] = robot index
        |  * dropped if the depositor           (who set each cell's current value)
        |    is isolated
        +--------------> *TrailStore: new trail record when a robot's deposit run starts
        |                  {creator, end_xy, start_tick, est_extra_s}, expires at 339 s
        v
   (2) *IdDefense (pure)
        a. open checks:   follow_start -> provisional trail (owner of strongest probe cell)
        b. confirm:       peak -> cluster of the nearest trail end within 0.5 m
        c. resolve:       pickup before deadline -> closed, no strike
                          deadline passed -> strike every creator in the group
                          late pickup within 0.5 m of the cluster -> reintegrate / -1 strike
        d. on demand:     cluster trail ends (eps 0.3 m, minPts 2) -> creator graph -> groups
        e. isolate at 5:  zero owned cells, drop future deposits, start 120 s timer
        |
   (3) LogStep (unchanged schema files)  +  *defense_log.csv (sidecar, id mode only)
```

- Caption: Figure 1 shows where the new state lives and when it runs. Why: every new part sits after the deposits and before logging, so the controller path is untouched.
- Owner of all new state: the loop functions (assumption, Table 1 row 13).
- `OwnerGrid` and `TrailStore` and `IdDefense` are pure modules, like `pheromone_grid` (`DESIGN.md` §6). No simulator header.

Table 2. New modules

| Module | Holds | Reads | Writes |
| --- | --- | --- | --- |
| `owner_grid.{h,cpp}` | `owner[layer][cell]`, an integer robot index, -1 = none | deposit cells that won the max-merge | owner per cell. `ZeroOwned(r)` returns the cells to zero |
| `trail_store.{h,cpp}` | trail records, expiry | deposit-run starts, tick | active trail ends with creator |
| `id_defense.{h,cpp}` | checks, strikes, isolation timers, clustering | trail ends, follow starts, peaks, pickups | strike, isolate and release events |
| glue in `pheromone_loop_functions*.cpp` | `defense_mode`, robot index map | controller flags, positions | grid filter, zeroing, sidecar rows |

Opaque IDs (hard rule):

- The store maps each entity id string to an integer index at first sight. It never parses the `hb_` or `dt_` prefix.
- `IdDefense` never reads the layer index or a role. It sees (index, position, value) only.
- The dominant owner of a cell is the owner of the larger layer value there. The value is physical, the layer label is storage.
- The sidecar writes the role as ground truth for analysis. Only the logger reads the prefix, as `LogStep` does today.

## 3. Behavior

### 3.1 Trail records

1. A deposit run starts on the rising edge of the controller's deposit request, outside the nest. That is the pickup tick (honest) or the first `RETURN_LAY` tick (detractor), where τ = 0.
2. The start position is the trail end. Honest: at the pickup point. Detractor: at the decoy after the 2 s wait.
3. Record: `{creator, end_xy, start_tick, est_extra_s = 0}`.
4. A run that starts while its creator is isolated gets no record, even if the creator is released before the run ends. Why: its first landed cell would sit mid-trail, not at the food or decoy.
5. A record expires when its own end deposit (1000) would decay below `θ_on` (20).
6. Expiry age = 60 s × log2(1000 / 20) = 60 × 5.64 = 339 s.
7. A record is removed early when its creator is isolated (its cells are zeroed, §3.4).
8. An isolated robot's deposits do not land.

### 3.2 Assigning an honest follower to a trail (TAROS assumption 4)

```
Figure 2. One check, from follow_start to its end

 follow_start (t0, p0)
   provisional trail = latest record of the dominant owner of the strongest of the 9 probe cells
   deadline = t0 + 1.5 x (|p0 - end| / 0.10 m/s + 15 s + est_extra_s)
        |
        v
 first peak (valid or invalid) at p1
   confirm: cluster C = cluster of the trail end nearest p1, if within 0.5 m
   no such end -> keep the provisional trail's cluster
        |
        +-- any pickup before deadline ---------------> closed, no strike
        +-- deadline passes, no pickup ---------------> strike group(C), store the struck set S
                 |                                       on the check, keep "awaiting"
                 +-- next pickup within 0.5 m of an end in C -> late return:
                 |      isolated members of S released, others in S -1 strike,
                 |      est_extra_s += 0.5 x (measured - estimate) on the provisional record
                 +-- next pickup elsewhere -> awaiting dropped
```

- Caption: Figure 2 shows the life of one travel-time check. Why: the peak tells which trail end the follower actually reached, and ownership near the nest flips often.
- Why confirm at the peak: max-merge and the 3 × 3 footprint make many robots own cells near the nest. The follow_start owner is a weak guess there.
- Why store S: an isolated robot's records are removed (§3.1), so it is no longer in any group. The stored set still names it, so a late return can release it (TAROS row F1).
- C is kept as its list of trail ends at the miss. A late return matches against that list, not against a later clustering.
- Why the deadline uses the provisional trail: the follower needs a deadline before it knows where it ends.
- One open check per (follower, provisional trail). A re-follow of the same trail opens no new check.
- A new check after a strike is allowed. A victim that loops on a false trail strikes its group once per deadline.
- Only honest robots open checks. Detractors never follow.
- Why any pickup closes in time: TAROS counts a return, not where the food was. A decoy victim rarely reaches food in time (decoys are ≥ 1.5 m from sources).
- Why a late return needs the cluster: a decoy victim may find a real source later by chance. That must not erase detractor strikes.
- 0.5 m late-return radius: a source disc is 0.5 m wide. A decoy end is ≥ 1.0 m from any source edge, so no pickup can match a decoy cluster.

### 3.3 Clustering and groups

1. Input: every active trail end (not expired, not removed).
2. Density-based spatial clustering of applications with noise (DBSCAN), eps 0.3 m, minPts 2.
3. A noise end becomes a cluster of one. It links to other clusters through its creator like any cluster. Why: a single detractor trail must still be strikeable, and a lone honest end should not form an unlinked group.
4. Graph: clusters are nodes. An edge joins two clusters that share a creator. Groups = connected components (union-find).
5. When: on demand, at most once per tick, only on a tick where a check confirms or resolves. Result cached for that tick.
6. Deterministic: no random draw, ends sorted by (start_tick, creator) before clustering.

Expected shape on our layout (inference, from `DESIGN.md` §3.1):

- Honest ends lie on the 3 source discs. Detractor ends lie on the decoy discs.
- Honest robots visit several sources, so the 3 source clusters likely link into one honest group.
- d = 1 and d = 2: each decoy has one detractor. Each detractor is its own group.
- d = 4: two detractors share each decoy, so groups of 2.
- No honest end lies at a decoy, so honest and detractor groups stay apart.

### 3.4 Strikes, isolation, release

Table 2a. Events and their effect

| Event | Effect |
| --- | --- |
| Missed deadline | +1 strike to every non-isolated creator in group(C). This set S is stored on the check |
| Late return | Isolated members of S released. Others in S -1 strike, floor 0 |
| Strikes reach 5 | Isolate: zero the robot's owned cells in both layers, remove its trail records, drop its future deposits, start the 120 s timer |
| Timer ends | Release, strikes reset to 0 |
| Release (either way) | Deposits land again. Old cells stay zero |

- An isolated robot gets no more strikes. It keeps moving and picking up food, as its controller does not know.
- Zeroing touches only cells the robot still owns. Cells another robot overwrote stay.
- Why zero, not only drop future deposits: a false trail end stays above `θ_on` for 339 s after the last deposit (§3.1). The run is 600 s. Dropping alone leaves the trail followable longer than the 120 s isolation.
- Conflict with TAROS reintegration (row F2 in the spec): a zeroed trail cannot be followed.
- A late return still releases a robot when a follower missed on its trail before the isolation (stored S, §3.2).
- After the zeroing, a single-detractor group gets no new followers. So in practice the timer releases it.
- Honest groups keep other members' trails, so late returns can still release honest robots. Alternative in §10 D2.

## 4. Values the paper does not state

All are pre-registered before runs. They go into `prereg/id_arm.md` (M6-04) and are never tuned on seeds 301 to 360.

Table 3. NOT STATED values, our number and reason

| Value | Number | Reason |
| --- | --- | --- |
| eps | 0.3 m | TAROS: eps = robots' search radius. Ours: END_SEARCH radius 0.3 m. Same-source ends lie within a 0.5 m disc and chain. Decoy-to-decoy edge gap ≥ 0.5 m and source-to-decoy edge gap ≥ 1.0 m exceed eps, so no false chain. Scaling TAROS 0.2 m by resource size would give 1.0 m and merge decoys |
| minPts | 2 | Paper value (verified). D-045 |
| Reference speed | 0.10 m/s | `max_speed` (`DESIGN.md` Table 2) |
| Travel-time margin | ×1.5 on (distance / speed + `t_end` + extra) | Trail paths bend and robots swerve. 1.5 allows 50 % detour. Example: end 1.5 m away gives 1.5 × (15 + 15) = 45 s. §10 D1 offers a measured replacement |
| Late-return radius | 0.5 m | Source disc diameter (§3.2) |
| Peak-match radius | 0.5 m, nearest end | Peaks lie 0.32 to 0.41 m from source centres on average (`results/real/failure_analysis.md` Table 5). eps 0.3 m would miss many. 0.5 m stays below the 1.0 m source-to-decoy edge gap |
| Estimate feedback gain | 0.5 | Half-step toward the measured time. Paper: "simple feedback loop" |
| Re-cluster period | On demand, at most once per tick (0.1 s) | Groups are needed only when a check confirms or resolves. Cost bound §8 R2 |
| Isolation length | 120 s, or earlier by a late return | 2 evaporation half-lives. Bounds a full honest-group isolation to a fifth of the run |
| Strikes after release | 0 | Paper silent. A fresh start avoids instant re-isolation |
| Trail record expiry | 339 s | Own end deposit falls below `θ_on` (§3.1) |
| Strike threshold | 5 | Paper value (verified) |

## 5. Logging

- `tools/schema.py` stays unchanged. `schema_version` stays 1. Same precedent as D-030.
- `check_runs.py` needs no change. It requires the 4 `S.FILES` (line 218) and lists only folders as runs (line 245). An extra file in a run folder is ignored.
- Developer acceptance criterion (AC) proves it by deliberate breakage: a run folder with `defense_log.csv` still exits 0.
- The sidecar `defense_log.csv` is written in id mode only. Other modes write no extra file (§7).
- Header row always present, so a run with no event still has the file.

Table 4. `defense_log.csv`, one row per event per affected robot

| Column | Type | Meaning |
| --- | --- | --- |
| `tick` | int | Simulation clock |
| `robot_id` | str | Affected robot. For check rows: the follower |
| `role` | str | `honest` or `detractor`. Ground truth from the id prefix, logged only |
| `event` | str | `check_open`, `check_confirm`, `check_ontime`, `check_miss`, `strike`, `late_return`, `strike_removed`, `isolate`, `release_late`, `release_timer`, `deposit_dropped`, `end_state` |
| `check_id` | int | Links a strike to its check. -1 for `end_state` and `deposit_dropped` |
| `strikes` | int | Strikes of `robot_id` after the event |
| `isolated` | int | 1 if `robot_id` is isolated after the event |
| `group_size` | int | Creators in the struck or released group. 0 if none |
| `trail_creator` | str | Creator of the provisional trail of the check. Empty if none |
| `deadline_tick` | int | Deadline of the check. -1 if none |
| `group_source` | str | `peak` (confirmed at the peak), `fallback` (provisional trail) or empty |
| `cells_zeroed` | int | Cells zeroed at `isolate`. 0 otherwise |
| `x`, `y` | float | Position of `robot_id` |

- `deposit_dropped`: one row per isolated robot per second at most, so the file stays small.
- `end_state`: one row per robot at the last tick. It gives the state at run end.
- Readers: detractors ever isolated per run (`isolate`, role detractor), honest robots isolated per run (`isolate`, role honest), state at run end (`end_state`).
- Mock first (`.claude/CLAUDE.md` minimum viable product (MVP) ladder): a MOCK sidecar for a few id-mode mock runs under `mock/` drives the arm-check table and the judge before real code exists.

## 6. Arm selection

- New attribute `<pheromone defense_mode="off|v3|v5|id">` in the loop functions node.
- `run_info_reader.cpp` already copies every extra `<pheromone>` attribute into manifest params. So `params.defense_mode` appears with no code change there.
- Absent attribute: the mode is `legacy`. The run behaves as v4. Saved `.argos` files still load.

Table 5. Mode mapping. `pheromone.defense` keeps its 0/1 meaning for `analyze.py` and the runid

| `defense_mode` | `pheromone.defense` | controller `<defense enabled>` | k | `t_lock` | Trail store |
| --- | --- | --- | --- | --- | --- |
| `off` | 0 | false | not used | not used | off |
| `v3` | 1 | true | 1 | 0 | off |
| `v5` | 1 | true | M5 freeze | M5 freeze | off |
| `id` | 1 | false | not used | not used | on |

- `defense` = 0 means "no defense of any kind". `defense` = 1 means "some defense on". So `analyze.py` and `RUNID_RE` (`def[01]`) need no change.
- The id arm turns the controller suspect rule off. Otherwise the arm mixes two defenses.
- Init guard: the loop functions read the controller `<defense enabled>` and throw if a row of Table 5 is broken. The run tool checks k and `t_lock`.
- v5 means whatever M5 freezes (k = 2 and its `t_lock`, or A' if M5-01 switches). So M6-03 depends on M5-03.
- One run root per arm, because v3, v5 and id share one runid key and `analyze.py` keeps only the latest duplicate:
  - `runs/m6_confirm/off/`, `.../v3/`, `.../v5/`, `.../id/`, each 160 runs. `check_runs.py` runs once per root.
  - The judge pairs seeds across roots and stops if a manifest's `defense_mode` differs from its root name.
  - product-manager rewords M6 exit 2 to "exits 0 on each of the 4 M6 confirm roots".
  - product-manager rewords M6-03 "The arm is a `<defense>` mode" to "the arm is `<pheromone defense_mode="id">`".

## 7. Invariance

- Claim: with `defense_mode` = `off` and `v3`, code v6 gives byte-equal `ticks.csv`, `robots.csv` and `events.csv` to the saved v4 runs with `t_lock` 0.
- `manifest.json` cannot be byte-equal (code version, hashes, runid, the new param). Its `metrics` block must be equal.
- Check cells: `d0_def0_s11` and `d2_def1_s11` of `runs/sweep_v2_lock0/`, re-run with the same values.
- Why it holds:
  1. The trail store, owner grid and ID defense run only when the mode is `id`.
  2. They draw no random number in any mode.
  3. The deposit filter is open in `off` and `v3`. Grid values follow the same max-merge.
  4. M6 changes no controller file.
  5. No sidecar is written outside `id`.
- A mismatch stops M6 and goes to `recover`.
- M5's own k = 1 check compares `food_collected` only. So it does not prove byte equality of the controller.
- Attribution on a mismatch: re-run the same cell on the v5 build. If v5 bytes equal v4, M6 caused it. Else M5 did.

## 8. Risks

Table 6. Risks and responses

| ID | Risk | Response |
| --- | --- | --- |
| R1 | Honest mass isolation at d = 0. Fig. 2 of the paper shows linked honest clusters (spec B3, B4). Our 3 source clusters likely form one honest group. Defense off, d = 0: 19.0 of 63.4 near-source peaks per run end without food (`results/real/failure_analysis.md` §6.1). That is an upper bound on misses. 5 misses isolate all 20 honest robots and zero every true trail for 120 s | Not tuned away. It is the expected finding (spec "may isolate honest robots at d = 0"). Log honest isolated per run. The 120 s timer bounds each episode. §10 D3 adds a report-only d = 0 cell to the arm check |
| R2 | Clustering cost per step | Bound: honest trails about 81 per 600 s (F(0, off), `results/real/v2/g2_stats.csv`), so about 46 in a 339 s window. Detractors: one trail per about 57 s each, 24 at d = 4 (inference: 2 × 2.5 m at 0.10 m/s, plus 2 s wait and 5 s rest). Under 150 ends. Pairwise check 150² = 22,500 distances per call, at most 6000 calls per run. Small next to physics. Wall time not measured |
| R3 | Misassignment near the nest | Confirm at the peak (§3.2). Log `check_confirm` with the group size |
| R4 | D-033 shape: the verdict line fires on something other than the new mechanism | Δ uses the best no-ID arm, chosen from the M5 verdict before any M6 run. The contrast table shows every arm at every d. The arm check shows the mechanism first |
| R5 | Arm does not function: detractors never reach 5 strikes | Arm check on 301 to 310 shows it first. A code defect goes to `recover`. No value changes after the prereg commit. No retry on 301 to 310 or 321 to 360 (D-043, each block used once). A smoke run outside all blocks comes first (§10 D6) |
| R6 | Isolated detractor released by its timer re-lays the false trail | Expected. Report time isolated per detractor |
| R7 | M5 slips, so no frozen v5 | Best no-ID arm falls back to v3 (D-026). The v5 root is dropped with a product-manager D-row. 480 runs |
| R8 | Owner-grid change alters float results in off or v3 | §7 byte check |

## 9. Design units, prereg sketch, kill

Table 7. Units for product-manager (size in person-days)

| # | Unit | Size | Depends on |
| --- | --- | --- | --- |
| U1 | `owner_grid` + grid hook: `Deposit` reports won cells, `ZeroOwned` | 0.5 | none |
| U2 | `trail_store`: records, run-start detection input, expiry | 0.5 | U1 |
| U3 | `id_defense`: clustering, groups, checks, strikes, isolation, release | 2 | U2 |
| U4 | Glue: `defense_mode`, Init guard, deposit filter, flags feed, sidecar writer, `code_version` v6, `CHANGELOG.md` row | 1 | U3, M5-03 |
| U5 | MOCK sidecar + arm-check table tool + sidecar header check (mock first) | 0.5 | none |
| U6 | Run tool: 4 roots, seeds 301 to 310 and 321 to 360 only, refuses without a committed prereg | 0.5 | U4 |
| U7 | Judge `judge_id_arm.py`: Δ, paired bootstrap, the word, prereg path, judge sha256 | 0.75 | U5 |

- Sum 5.75 person-days. Order: U5 and U1 now, U4 after M5-03.
- Minimum viable product (MVP) ladder: U5 runs end to end on mock first. Then the real id arm replaces the mock sidecar under the same columns.

Table 8. Pre-registration sketch (`prereg/id_arm.md`, `rules/measurement.md` §1, from the Fable spec)

| Line | Content |
| --- | --- |
| Primary metric | Δ = F(2, id) − F(2, best no-ID). Best no-ID named from the M5 verdict before the first M6 run |
| Threshold | Paired bootstrap, 10,000 resamples, 95 %, seeds 321 to 360. Interval excludes 0 = "differs". Else "not resolved". No win line |
| Contrast | off, v3, v5, id × d 0, 1, 2, 4 × 40 seeds = 640 runs. Also honest robots isolated per run |
| Failure | "fewer than 1 of 2 detractors isolated by run end in most seeds" = "adapted arm did not function". Reading: §10 D4 |
| Arm check | Seeds 301 to 310, (d 2, id). Detractors isolated per run. Report only, no pick |
| Frozen values | Table 3, written in the prereg |

- Kill: no gate-ready code by 2026-11-21. Then T-B becomes a T-E row and future work. product-manager writes the D-row.

## 10. Open decisions

Table 9. Open decisions, each with a recommendation

| ID | Question | Options | Recommendation |
| --- | --- | --- | --- |
| D1 | Travel-time margin | (a) 1.5 fixed. (b) 95th percentile of honest follow-to-pickup time over the estimate, from saved v4 `lock0` d = 0 off logs, seeds 11 to 30 | (b), if data-analyst can do it from saved files before the prereg commit. Else (a) |
| D2 | Isolation effect on old trails | (a) zero owned cells + drop new. (b) drop new only | (a). With (b) a false trail outlives the 120 s isolation (§3.4) |
| D3 | Arm check cells | (a) (2, id) only, as the spec. (b) add (0, id), report only | (b). It shows R1 before 640 runs. Same seeds, no pick |
| D4 | Failure line reading | "isolated by run end" = (a) at least one `isolate` event before 600 s. (b) isolated at the last tick. "Most seeds" = more than 20 of 40 | (a) and more than 20 of 40 with zero detractors isolated. The timer makes (b) depend on timing |
| D5 | Late pickup scope | (a) gated by the cluster (§3.2). (b) any pickup, as the paper's "return" | (a). (b) lets a decoy victim's chance find erase detractor strikes |
| D6 | Smoke run before the arm check | (a) none. (b) 1 run per mode at d = 2 on seed 900, outside every block, report only | (b). A defect then costs no spent seed. Seed 900 needs a product-manager D-row (D-043 lists the blocks) |
