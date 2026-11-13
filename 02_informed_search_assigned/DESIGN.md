# Informed search for central-place foraging swarms: Design

- Author: system-architect, 2026-11-12. Status: draft. Fable picks each option and logs it in `DECISIONS.md`.
- Task: `../docs/Autonomous_Mobile_Robot_Programming_Final Project 2.pdf` (cited as [TASK]).
- Code facts: `research/baseline_code_map.md` (cited as `BCM §n`, or file:line with the short names `ctrl.cpp`, `lf.cpp`, `base.cpp`).
- Literature: `research/informed_search_survey.md` (source IDs `S-IS-n`).
- Measured facts: "main session smoke, 2026-11-12" (baseline build in `02_informed_search_assigned/build_baseline/`, one run, seed 1).
- Pattern reused: `../01_pheromone/` tools (schema, mock runs, check, sweep, analyze, report). Its controller is not reused.
- Words used below:
  - "Baseline" = the professor's central-place foraging algorithm (CPFA) code at commit `9480f2e`, unchanged.
  - "Student grid" = the Grid-Based Complete Foraging Algorithm (GCFA) visitation grid [S-IS-2].
  - "Experiment file" = the ARGoS Extensible Markup Language (XML) configuration file of one run.
  - "Map" = the server's visited-location structure (new).
  - "Map target" = a search location the map gives a robot.
  - "Available" = a region not visited within `T_stale` seconds and not reserved (§3.1).

## 0. Mission block

- No `PLAN.md` exists yet for this project.
- `rules/docs.md` §0.1: draft lines go back to the main session, never into a design doc.
- So the mission, vision, constraint, goal and research question drafts are in this unit's hand-back report.
- `product-manager` writes them into `PLAN.md`. This section then quotes that block.
- Goal IDs used below (drafts, until `PLAN.md` holds them):
  - G1: efficiency. The map query cost and memory, measured by a benchmark.
  - G2: evaluation. 300 checked evaluation runs, box plots and an improvement table.
  - G3: verdict. A committed verdict file, plus a root-cause memo per non-improving distribution.
  - Research questions RQ1 to RQ3: score effect, cost scaling, and which part of the method gives the effect.

Table 0. Traceability of the strategy options (§3) to the goals

| Option | G1 (cost) | G2 (300 runs) | G3 (verdict) |
| --- | --- | --- | --- |
| A: fine uniform grid | weak at large arenas (memory grows with area) | yes | yes |
| B: region quadtree (recommended) | yes | yes | yes |
| C: online disk clusters plus yield scoring | yes, but no completeness bound | yes, highest risk | yes |

## 1. Problem and design in one picture

```
Figure 1. Where the method acts in one robot trip

 nest ──(1) DEPARTING──> target ──(2) SEARCHING──> food? ──(3) RETURNING──> nest
  ^                                    |  log visited points                 |
  |                                    |  (robot buffer, max 100)            |
  |                                    v                                     |
  |                        give up ─────────────────────────────────────────>|
  |                                                                          v
  |   (4) at nest: upload buffer ──> [ server map ] <── insert O(depth)       |
  |                                        |                                  |
  |   decision order:  site fidelity? ── pheromone? ── MAP TARGET (new)       |
  |                                        |   nearest available region,      |
  |                                        |   then reserve it                |
  +────────────────────────────────────────+   (baseline: random wall point)  |
```

- Caption: Figure 1 shows one trip and the two new server calls (insert at upload, query at target choice). Why: the baseline sends uninformed robots toward a random wall point, so they re-search the same space.
- Baseline facts that shape the design:
  1. The random location is a wall point, not a uniform point (BCM §1.3, `ctrl.cpp:578-605`).
  2. The random branch runs only when the pheromone list is empty (BCM §1.3, `ctrl.cpp:526-544`, `ctrl.cpp:778`).
  3. An uninformed departing robot switches to search after about 1 to 2 m (BCM §1.4). So a new target alone is never reached.
  4. Every pickup respawns one resource at a uniform point (BCM §4.6). So "visited" decays over time.
  5. Food is sensed only in `SEARCHING`, every 0.5 s, radius 0.13 m (BCM §3.3).
- Smoke numbers (main session smoke, 2026-11-12): 245 collected in 720 s. Wall time 5.67 s per run. Effective nest radius 0.911 m.
- So 24 robots made about 245 deliveries: about 10 trips per robot, about 70 s per trip (inference).

## 2. Fidelity decisions

Each item lists options and one recommendation. Fable picks and logs a D-row.

- Ranking rule: the professor ranks teams by absolute score against the "original CPFA" [TASK p. 3].
- So the primary setting is the plain reading of the shipped code: what other teams most likely run.
- Stricter readings become pre-registered sensitivity sets, run in full. Runs are cheap: about 6 s each.

### F1. Nest radius 0.25 m

The code scales the experiment-file value by `sqrt(log2(10))` = 1.82 (`lf.cpp:104-111`). The same effective radius drives the nest test (`ctrl.cpp:178-181`) and the food exclusion zone (`lf.cpp:546-549`).

Table 1. Nest radius options

| Option | File `NestRadius` | Effective radius | Drop-off accept radius | Draws per drop (inference) | Change to baseline code |
| --- | --- | --- | --- | --- | --- |
| F1-a | 0.25 | 0.456 m (printed by `lf.cpp:112`) | 0.178 m | about 50 | none |
| F1-b | 0.137 | 0.25 m | 0.075 m | about 5,000 | none |
| F1-c | 0.25, scaling removed | 0.25 m | 0.075 m | about 5,000 | patch `lf.cpp:110` in both arms |

- Draws per drop (inference): the drop point is Gaussian with a +0.5 m mean offset per axis (BCM §4.3).
  - F1-a: standard deviation 0.38 m, offset 0.707 m. Accept probability ≈ 0.02. About 50 draws.
  - F1-b: standard deviation 0.21 m, offset 0.707 m. Accept probability ≈ 2e-4. About 5,000 draws.
  - The loop costs processor time only. Simulated time does not change. 245 drops × 5,000 ≈ 1.2 M draws: small.
- **Recommendation: F1-a primary, F1-b as a full sensitivity set.**
  - Why F1-a: it is the knob the course file exposes. It needs no code change. Other teams most likely edit that value.
  - Why F1-b too: it is the literal 0.25 m geometry. It costs 300 more runs (about 30 min).
  - F1-c is dropped: it patches baseline code. F1-b gives the same geometry without a patch.
  - The report prints both the file value and the effective radius for each set.
- Optional owner action: ask the professor which reading he grades. The answer can swap primary and sensitivity before evaluation, never after.

### F2. Resource respawn on pickup

Table 2. Respawn options

| Option | What | Code change | Effect |
| --- | --- | --- | --- |
| F2-a | Keep respawn in both arms | none | 256 items always. Clustered and Powerlaw drift toward Random (BCM §4.6) |
| F2-b | No respawn in both arms | guard `ctrl.cpp:631-639` with a flag | Fixed 256. Closer to the papers' "collect all" setting [S-IS-2] |

- **Recommendation: F2-a.**
- Why: it is the shipped behaviour, and the build cache names the project `random_drop_CPFA` (BCM §4.6). The grader most likely runs it.
- F2-b touches the baseline arm. It is a stretch after G2 only, never a headline number.
- Design consequence: the map stores recency, not a visited bit (§3.1).

### F3. Baseline parameter set per distribution

The repo has one 10 × 10 m set (Random). It was evolved for 5 × 5 m, 64 items, 2 robots (BCM §4.2). The Clustered set comes from a 16 × 16 m, 64-robot file. No Powerlaw set exists [S-IS-11].

Table 3. Parameter set options

| Option | Random | Powerlaw | Clustered | Note |
| --- | --- | --- | --- | --- |
| F3-a | `xml10` set | `xml10` set | `xml10` set | One shipped file. Only `FoodDistribution` changes |
| F3-b | `xml10` set | `xml10` set | 16 × 16 set (`Clustered_CPFA_r64_tag512_16by16.xml:45-52`) | The Clustered set fits another arena and swarm size |
| F3-c | evolved per distribution at Table 1 settings | same | same | Needs a genetic algorithm budget. Not the "original" |

- **Recommendation: F3-a.** The same set in both arms, for every distribution.
- Why: it is the only 10 × 10 m file. Its 24 robots and 256 items match [TASK Table 1]. F3-b mixes in a set tuned for 64 robots.
- F3-b Clustered is an optional sensitivity set (100 runs), only if time remains after G2.
- Edits on top of `xml10` (BCM §4.1): `FoodDistribution` per distribution, `MaxSimTimeInSeconds="720"`, `NestRadius` per F1, `random_seed` per run, `length="0"` as in the smoke run.

### F4. Tuning fairness

Our method adds new parameters (Table 6). The baseline has no such knobs.

| Option | Rule | Fair? |
| --- | --- | --- |
| F4-a | Tune only the new parameters. Freeze all 7 baseline parameters at F3-a in both arms | Yes. The baseline has nothing to tune with these knobs |
| F4-b | Also tune the 7 baseline parameters for our arm | Only with F4-c |
| F4-c | Equal budget: same tuner, same candidate count, same tuning seeds, applied to the baseline's 7 parameters | Required whenever F4-b is used |

- **Recommendation: F4-a.**
- Tuning budget, pre-registered: 3 rounds, 9 candidate settings, 10 tuning seeds, 3 distributions. 270 runs, about 27 min (§6.3).
- One parameter set for all 3 distributions. The metric is the sum of mean collected over the 3 distributions.
- Why one set: the baseline uses one set for all 3 (F3-a). Per-distribution tuning would give our arm knowledge the baseline lacks.
- If F4-b is ever opened, the headline stays "vs the shipped baseline" [TASK: "original CPFA"]. The equal-budget comparison is reported beside it. This is fixed now, before any run.

## 3. The algorithm: options A, B, C

### 3.1 Shared behaviour (all options)

These parts are the same in A, B and C. Only the map structure differs.

1. Record (robot side, `Searching()`):
   - While `SEARCHING`, log `GetPosition()` every `rec_period` seconds, on a half-second tick (`ctrl.cpp:321`).
   - Skip a point in the same minimum cell as the last logged point. This records fewer points [TASK hint 3].
   - Also log the pickup position.
   - Buffer: first-in first-out, capacity 100 [TASK example].
2. Upload (robot side, `Returning()` nest branch, `ctrl.cpp:489-517`):
   - Send the buffer with the upload time, then clear it. Same place the pheromone is pushed (`ctrl.cpp:513`).
3. Store (server side): each minimum cell or leaf keeps two times.
   - `t_last`: last recorded visit. Never visited = −∞.
   - `t_res_until`: end of the current reservation. None = −∞.
   - Availability key: `avail_at = max(t_last + T_stale, t_res_until)`. The region is available when `avail_at ≤ now`.
   - Why a time, not a bit: respawn refills visited space (F2-a).
   - Refill estimate: 245 pickups in 720 s give about 0.34 respawns per second over about 97 m².
   - One 0.3125 m cell (0.098 m²) then refills about once per 2,900 s (inference).
   - So inside 720 s a visited cell rarely refills. `T_stale` = ∞ is the start value. 300 s is a tuning candidate.
   - With `T_stale` = ∞ a visited cell is never available again. A reserved, unvisited cell becomes available after `t_res`.
4. Choose (server side, `Returning()` decision order, `ctrl.cpp:526-544`):
   - Query the nearest available minimum cell from the robot position (rule below).
   - Reserve the minimum cells within `r_res` of the answer: `t_res_until = now + t_res`.
5. Travel (robot side, `Departing()`, `ctrl.cpp:270-292`):
   - A robot with a map target skips the 5 s switch-to-search test. It drives to the target, then starts the uninformed walk.
   - A new flag `isMapTarget` carries this. `isInformed` stays false, so the uninformed walk runs at the target (`ctrl.cpp:362`).
   - Why a new flag: `isInformed` is read in 5 places (`ctrl.cpp:71, 81, 271, 297, 362`) and set in 3 (`ctrl.cpp:530, 535, 542`). Overloading it would also turn on the informed walk.
6. Decision order (parameter `q_map`):
   - `q_map` = 0: the map replaces only the random branch (pheromone list empty).
   - `q_map` > 0: a robot without site fidelity takes the map target with probability `q_map`, before the pheromone branch.
   - Why: the random branch may rarely fire while pheromones are active (BCM §1.3). The headroom gate (§7, M2) measures how often.
   - The `q_map` draw uses its own random category (`CRandom::CreateCategory`, used in `../01_pheromone` real runs).

Query rule, identical for every option (so A and B can be checked against each other):

- Distance of a cell = Euclidean distance from the robot position to the nearest point of the cell box.
- Answer = the available minimum cell with the smallest distance.
- Tie: the lowest row index, then the lowest column index.
- Target point = the centre of that cell.
- Cells inside the nest exclusion disk or outside the forage range (`base.cpp:31-36`) are never answers.
- In a large never-visited region the answer is its cell nearest to the robot: a frontier cell [S-IS-8].
- No available cell: fall back to `SetRandomSearchLocation()`, and log it.

### 3.2 Option A (stable): fine uniform grid with ring search

```
Figure 2. Option A, 10 m arena, cell 0.3125 m

 +--+--+--+--+--+--+   each cell: t_last, t_res_until (2 floats, 8 bytes)
 |  |▓▓|▓▓|  |  |  |   ▓ = not available
 +--+--+--+--+--+--+   query: square rings outward from the robot cell.
 |  |▓▓|R |▓▓|  |  |   Keep the best Euclidean answer. Stop when the
 +--+--+--+--+--+--+   ring's inner distance exceeds the best answer.
```

- Caption: Figure 2 shows the fixed fine grid and the ring query. Why: it is the simplest map that tells visited from unvisited at sensing size.
- Data: `(L / s_min)²` cells, 8 bytes each. 10 m arena: 32 × 32 = 1,024 cells, 8 KB.
- Insert: O(1) (cell index).
- Query: O(r² / s_min²) cells up to the answer distance r. Worst case: all cells.
- Large arena: memory grows with arena area, not with visited area. 80 m: 65,536 cells, 512 KB. 1 km: 10.2 M cells, 82 MB.
- Versus the student grid: cells stay at sensing size, so they do not grow with the arena. Memory does.

### 3.3 Option B (scalable, recommended): region quadtree with availability summaries

```
Figure 3. Option B, region quadtree (10 m root, minimum leaf 0.3125 m, depth 5)

 root 10 m [a_min = -inf]
  ├─ NW 5 m  leaf, never visited            <- one node for 25 m²
  ├─ NE 5 m  [a_min = -inf]
  │    ├─ 2.5 m leaf, never visited
  │    ├─ 2.5 m leaf, fully visited, merged  <- one node again
  │    └─ ... down to 0.3125 m leaves
  ├─ SW 5 m  leaf, never visited
  └─ SE 5 m  [a_min = 412] ...

 node = { first_child: int32, t_last: float, t_res_until: float, a_min: float }  16 bytes
 a_min = smallest avail_at in the subtree
```

- Caption: Figure 3 shows how never-visited and fully visited space stay as large nodes, while the boundary splits to sensing size. Why: cell size follows the robots' paths, which answers the professor's large-arena critique [TASK p. 2].
- Insert(p, t):
  1. Descend from the root to the minimum leaf that holds p.
  2. Split a larger leaf on the way into 4 children. Children copy the parent's two times.
  3. Set the leaf `t_last = max(t_last, t)`.
  4. Walk back up. Recompute `a_min` from the 4 children.
  5. Merge: when 4 sibling leaves are all unavailable for good (`T_stale` = ∞ and visited), replace them by their parent leaf.
  - Cost: O(depth). Depth = ceil(log2(L / s_min)): 5 at 10 m, 8 at 80 m, 12 at 1 km.
  - With finite `T_stale` the merge needs 4 equal-enough times. Rule: merge when the 4 `t_last` differ by < 10 s. The parent keeps the oldest `t_last` (conservative: it becomes available first).
- Reserve(p, r_res, t_until): split down to the minimum leaves inside the disk. Set `t_res_until`. Update `a_min` up each path.
  - Cost: O((r_res / s_min)² · depth). At `r_res` = 1.0 m: about 32 leaves × 5 levels.
- NearestAvailable(origin, now):
  1. Best-first search. Priority = Euclidean distance from origin to the node box.
  2. Skip a node when `a_min > now`: nothing available inside.
  3. A popped available leaf larger than `s_min` yields its minimum cell nearest to the origin. That cell has the same distance as the leaf box.
  4. Keep popping while the next priority equals the best distance. Apply the tie rule (§3.1).
  - Cost: nodes popped = depth plus the nodes nearer than the answer that still hold an available descendant. Logged per query (§5).
  - Worst case: all nodes. The log shows whether it happens.
- Memory: nodes ≤ min(4 · depth · V + 1, 4/3 · total cells), V = boundary leaves (inference).
  - Without the merge, a densely visited tree reaches 4/3 × cells × 16 bytes ≈ 2.7 × A's memory.
  - So without the merge B beats A only below about 37 % of cells touched (8 / (16 · 4/3), inference).
  - With the merge, fully visited quads collapse. Memory then follows the length of the visited boundary.
  - The benchmark measures the crossover (§5.2). G1 states its memory line against it.
- 10 m arena: at most 1,365 nodes, about 22 KB.
- Honest note: at 10 m, A and B give the same answers by construction (same query rule). The benefit is memory and query cost at large arenas (§5).
- Same interface as A. So A is a drop-in fallback with identical behaviour at 10 m.

### 3.4 Option C (cutting-edge): online disk clusters plus yield scoring

```
Figure 4. Option C, leader clustering into disks

   ( ) ( )        a point joins the nearest disk within r_d,
  (   )   R  ( )  else it starts a new disk (centre, count, t_last).
     ( )          Disks hashed in buckets of side 2·r_d.
                  Query: sample K candidates on rings around the robot.
                  The first candidate outside every disk wins.
                  Score = expected yield / travel time.
```

- Caption: Figure 4 shows variable-size disk clusters with a sampled query. Why: it follows the professor's hint 2 (clusters of different sizes).
- Data: one disk per visited patch, in a hash map of buckets. Memory grows with disk count, not arena area.
- Insert: O(1) expected (check 9 buckets).
- Query: O(K · local disks). No completeness: a gap smaller than the sampling step can be missed.
- Yield scoring: weight a candidate by found-food density near it, from pheromone data.
- Spiral search at the target, as in the distributed deterministic spiral algorithm (DDSA) [S-IS-9].
- Close to Adaptive Repulsive Pheromone Clustering (ARPC) [S-IS-4], without its batch clustering step. Adaptive Repulsive Pheromone Clustering lost on Powerlaw [S-IS-4].
- It draws more random numbers. It has no exact twin to check it against.

### 3.5 Comparison and recommendation

Table 4. Options at the professor's example scale (200 robots, 400,000 points, 80 m arena). Values are bounds (inference). The benchmark (§5.2) measures them.

| Item | Flat list (the problem) | Student grid, n = 12 | Student grid at equal resolution, n = 256 | A: fine grid | B: quadtree | C: disks |
| --- | --- | --- | --- | --- | --- | --- |
| Memory | 400,000 points, 4.8 MB | 144 counters | 65,536 counters | 65,536 cells, 512 KB | grows with the visited boundary | grows with disk count |
| Insert per point | O(1) | O(1) | O(1) | O(1) | O(depth) = 8 | O(1) expected |
| Query per return | 400,000 point tests per candidate | 144 blocks of 9 | 65,536 blocks of 9 | O(r² / s²), worst 65,536 | best-first, logged. Worst: all nodes | O(K · local disks) |
| Region side at 80 m | point | 6.7 m | 0.3125 m | 0.3125 m | 0.3125 m to 80 m, adaptive | r_d, adaptive by merging |
| Grows with | points | nothing | arena area | arena area | visited boundary | visited area |
| Complete (finds every available region) | yes | coarse only | yes | yes | yes | no |
| Code risk | none | low | low | low | medium | high |

- Total insert work: 400,000 points × 8 levels = 3.2 M node steps, spread over the run (inference).
- A flat-list server pays 400,000 point tests per return. 200 robots × 20 trips = 4,000 returns. Total: 1.6 × 10⁹ tests (inference).
- The student grid at n = 12 has the cheapest query. Its price is a 6.7 m region, which the professor names as the limit [TASK p. 2].
- **Recommendation: B, with A as the fallback behind the same interface.**
- Why B: it is complete like a fine grid. Its memory and query follow the visited boundary, not arena size or point count. That is the gap the professor names in the student grid.
- Why not C first: no completeness bound, more random draws, and the published variant lost on Powerlaw. Its yield scoring and spiral stay as later tactics (§3.6).

### 3.6 Behaviour tactics on top of the map

Each tactic is one switch. Each enters only through tuning on tuning seeds (§6.3).

| ID | Tactic | Default | Why |
| --- | --- | --- | --- |
| T1 | Map-target travel without the early switch (§3.1 step 5) | on (part of the method) | Without it the target is not reached (BCM §1.4) |
| T2 | `q_map` > 0: map before pheromone for robots without fidelity | 0 | Fires the map when pheromones are active |
| T3 | Reservation radius `r_res` and time `t_res` | 1.0 m, 60 s | Spreads 24 robots. The student grid has no reservation [S-IS-2] |
| T4 | Spiral search at the map target | off | Covers the target region without overlap [S-IS-9] |

- `t_res` start value: a 3 m trip at 0.16 m/s takes about 19 s, plus search time. 60 s covers travel and the first search (inference).

## 4. Integration into the baseline code

### 4.1 Source layout and the switch

```
Figure 5. Code layout, under 02_informed_search_assigned/

 vendor/Collision_Free_CPFA/   git-ignored clone at 9480f2e, never edited
        │ copy once
        v
 src/                           tracked copy. Diff vs 9480f2e kept in patches/ours.diff
   source/CPFA/CPFA_controller.{h,cpp}        hooks (§4.2), guarded by the switch
   source/CPFA/CPFA_loop_functions.{h,cpp}    owns the map, reads settings, logs
   source/InformedSearch/visit_map.{h,cpp}    PURE: no ARGoS include
   source/InformedSearch/bench_visit_map.cpp  stand-alone benchmark (§5.2)
 build_baseline/   vendor build (exists, main session smoke)
 build_ours/       our build
```

- Caption: Figure 5 shows where each part lives. Why: the vendor clone stays the untouched reference for the invariance check.
- Switch: attribute `InformedSearch` on the `<CPFA>` node, read with `GetNodeAttributeOrDefault`, default `0`.
- New parameters are also read with defaults. So one experiment file runs on both the vendor build and ours.
- Switch off must mean:
  1. No extra draw from the `argos` random stream.
  2. No write to any state a controller reads.
  3. The decision order and `SetRandomSearchLocation()` run exactly as in the vendor code.
- Logging (§5.1) writes files only. It never draws random numbers.
- `visit_map` is pure. So the benchmark and the simulation run the same code.

### 4.2 Hook table

| Hook | Where | Switch on | Switch off |
| --- | --- | --- | --- |
| Record | `Searching()`, `ctrl.cpp:321-323` | log a point every `rec_period` | nothing |
| Upload | `Returning()` nest branch, after `ctrl.cpp:516` | `LoopFunctions->map.InsertBatch(buffer, t)`, then clear | nothing |
| Choose | `Returning()`, `ctrl.cpp:526-544` | order per `q_map` (§3.1 step 6). The random branch calls `SetMapTarget()` | vendor order |
| First departure and wall reach | `Departing()`, `ctrl.cpp:290-291` | `SetMapTarget()` instead of `SetRandomSearchLocation()` | vendor |
| Travel | `Departing()`, `ctrl.cpp:270-289` | skip the switch test while `isMapTarget`. At the target: `SEARCHING`, clear the flag | vendor |
| `SetMapTarget()` | new controller method | query and reserve. None found: `SetRandomSearchLocation()` | not called |
| Upkeep | `PreStep()`, `lf.cpp:169-193` | none (times are compared lazily) | nothing |
| Reset | `lf.cpp:137-167`, `ctrl.cpp:112-137` | clear map, buffer, flag | vendor |

### 4.3 Invariance check (switch off equals vendor)

1. Precondition: vendor build, same experiment file, same seed, twice. Collected counts and per-minute rows must be equal. Otherwise determinism fails: stop and write a root-cause memo.
2. Vendor build vs our build with `InformedSearch="0"`: 5 seeds × 3 distributions, F1-a.
3. Pass: collected count and every per-minute count are equal in all 15 pairs.
4. Any mismatch: no evaluation run starts. Root-cause memo first.

- The harness creates `results/` inside each run's working directory. Without it the vendor per-minute file fails silently (BCM §5.1).
- Pairing limit, stated in the report:
  - Layout and robots share the `argos` stream (BCM §5.2).
  - So both arms share the initial layout for a seed. Respawn points diverge once behaviour diverges.
  - `check_runs.py` compares a hash of the initial food list across arms per seed.

## 5. Efficiency evidence

### 5.1 Logged in every real run

`queries.csv`, one row per nest decision:

| Column | Meaning |
| --- | --- |
| `t_s` | simulated time |
| `robot` | robot id |
| `branch` | `fidelity`, `pheromone`, `map`, `fallback_random`, `random` (logged in both arms) |
| `nodes_visited` | nodes popped by the query (operation count, deterministic) |
| `nodes_total`, `leaves_total` | map size at query time |
| `points_inserted_total` | points received so far |
| `query_us` | wall time in microseconds, `std::chrono::steady_clock` |
| `target_x`, `target_y`, `dist_m` | answer and its distance from the robot |
| `reached` | 1 if the robot reached the target, 0 if not, set at trip end |

- Primary cost measure: `nodes_visited` (deterministic). `query_us` is secondary (machine noise).
- In the baseline arm, the cost columns stay empty. The branch rows give the headroom counts.

### 5.2 Micro-benchmark at the professor's scale

`bench_visit_map` links only `visit_map`. No simulator, no model, one core.

- Inputs, two kinds:
  1. Synthetic: 200 robots, correlated random walk traces from a central nest, 100 points per trip, 20 trips = 400,000 points. Generator seed fixed.
  2. Replay: `points.csv` uploads saved from real runs, replayed in time order.
- Arena sides: 10, 20, 40, 80, 160, 320 m. Minimum leaf 0.3125 m.
- Structures, one interface:
  1. Flat list: scan all points per candidate.
  2. Student grid, n = 12: minimum 3 × 3 block (Algorithm 1 of [S-IS-2]).
  3. Student grid at equal resolution: n = L / `s_min`, same block rule.
  4. A: fine grid. 5. B: quadtree, merge on. 6. B without the merge.
- Output columns per structure × arena × input: region side (m), total insert operations, operations per query (median, 95th percentile, maximum), memory bytes, microseconds per query (median), cells touched (%).
- Queries: one per robot return (4,000), from the nest.
- Equivalence check: A and B return the same cell on the same input (§3.1 query rule). Any difference stops B.
- Expected wall time: under 10 s per arena size (inference). The main session runs it with `timeout 300`, one core.
- Output: `results/bench/bench.csv` and `fig_cost_vs_arena.png` (log scale).

G1 lines (draft, pre-registered in `prereg/G1_bench.json` before the first benchmark run):

1. Query: at 80 m (D-012), B median operations per query ≤ 1 % of the flat-list tests (≤ 4,000).
2. Query: at 80 m (D-012), B median operations per query < the equal-resolution student grid.
3. Memory: at the largest arena where cells touched < 37 %, B (merge on) memory < A memory.
- A fail of any line gets a root-cause memo. The line does not move.

## 6. Experiment protocol

### 6.1 Arms and sets

| Set | Arms | Distributions | Seeds | Runs | Purpose |
| --- | --- | --- | --- | --- | --- |
| S0 invariance | vendor, `cpfa` (switch off) | 3 | 3001 to 3005 | 30, plus 2 determinism | §4.3 |
| S1 headroom and noise | `cpfa` | 3 | 1001 to 1030 | 90 | branch shares, travel and search split, baseline noise |
| S2 tuning | `qmap` candidates | 3 | 1001 to 1010 | 270 | §6.3 |
| S3 evaluation, F1-a (primary) | `cpfa`, `qmap` frozen | 3 | 2001 to 2050 | 300 | G2, G3 |
| S4 sensitivity, F1-b | `cpfa`, `qmap` frozen | 3 | 2001 to 2050 | 300 | nest radius reading |
| S5 ablation (RQ3) | `qmap` minus one tactic | 3 | 2001 to 2050 | ≤ 300 | which part gives the effect |

- `cpfa` = our build with the switch off. After S0 passes, it stands for the vendor baseline.
- Seed 0 (clock seed, BCM §5.2) and seed 1 (smoke) are never used.
- Tuning seeds and evaluation seeds never overlap. The same 50 evaluation seeds serve both arms, paired by seed.
- Total runs ≈ 1,300. At about 6 s each: about 2.2 h, one core, sequential (inference from the smoke).

### 6.2 Pre-registration

- File: `prereg/S3_eval.json`, committed before any S3 run. Its hash goes into every S3 manifest.
- Contents:
  1. Primary metric: `collected` at 720 s.
  2. Primary contrast: `qmap` vs `cpfa`, per distribution, paired by seed.
  3. Improvement: `100 · (mean_qmap − mean_cpfa) / mean_cpfa`, a ratio of means.
  4. Decision rule (the only one, `rules/research.md` §7 item 2): 95 % percentile bootstrap interval of the improvement, 10,000 resamples of the seed index, paired. Bootstrap seed fixed.
  5. Verdict per distribution:
     - `improves`: interval lower bound > 0.
     - `worse`: interval upper bound < 0.
     - `not resolved`: otherwise.
  6. Reported beside the verdict, never part of it: Wilcoxon signed-rank (two-sided) p, Holm-adjusted p over the 3 distributions, medians.
  7. Multiplicity: 3 distributions give 3 separate verdicts. The report says so in one line next to the table.
  8. Noise line: from S1, the standard deviation σ of `collected` per distribution.
     - Detectable paired difference at 50 seeds ≈ 2.8 · σ_diff / √50 (80 % power, α = 0.05).
     - σ_diff is unknown before S3. √2 · σ is the conservative stand-in.
     - The report prints this detectable size beside each result.
  9. Frozen parameter values (from §6.3), code commit, library hashes.
- Nothing in this file changes after the first S3 run. A needed change makes a new file and a new run set.
- G3 needs a root-cause memo for each distribution that is `worse` or `not resolved`.

### 6.3 Tuning rule (S2, pre-registered in `prereg/S2_tuning.json`)

Table 6. Method parameters (start value first, all inference)

| Parameter | Start | Tuned candidates | Why |
| --- | --- | --- | --- |
| `s_min` (minimum cell) | 0.3125 m | fixed | about 2 × pickup radius 0.13 m |
| `rec_period` | 2 s | fixed | 0.32 m at full speed, about one cell |
| `T_stale` | ∞ | 300 s | respawn refill estimate (§3.1) |
| `r_res` | 1.0 m | 0.5 m, 2.0 m | spread 24 robots |
| `t_res` | 60 s | 30 s, 120 s | travel plus first search (§3.6) |
| `q_map` | 0 | 0.5, 1.0 | headroom (M2 gate) |
| `spiral` (T4) | off | on | [S-IS-9] |

1. A round holds up to 4 candidates. Each candidate changes one parameter from the current best.
2. Round 1: the start values (1 candidate).
3. Round 2: `q_map` 0.5, `q_map` 1.0, `r_res` 0.5, `r_res` 2.0.
4. Round 3: `t_res` 30, `t_res` 120, `T_stale` 300, `spiral` on.
5. Each candidate: 10 seeds × 3 distributions = 30 runs. Total 9 × 30 = 270 runs.
6. Metric: sum over 3 distributions of mean `collected` on seeds 1001 to 1010. The best of a round becomes the current best only if it beats it. A tie keeps the earlier one.
7. If the M2 headroom gate shows `targets_reached_share` < 50 % in round 1, a 3 m distance cap replaces `spiral` in round 3.
8. Freeze in a D-row before S3. Never re-tune on evaluation seeds.

### 6.4 Run layout

```
02_informed_search_assigned/
  runs/<set>/<runid>/            runid = <YYYYMMDD-HHMMSS>_<arm>_<dist>_s<seed>
    run.argos                    generated experiment file (seed, arm, distribution, stamps)
    results/                     created by the harness, vendor files land here
    stdout.log                   argos3 output
    manifest.json                rules/measurement.md §2.1 fields plus metrics
    forage_per_minute.csv        minute, collected
    queries.csv                  §5.1
    points.csv                   uploads (t_s, robot, x, y), for replay
  mock/runs/<set>/<runid>/       same layout, runid starts MOCK_
```

- Each run has its own working directory. Vendor result files append with no arm label (BCM §5.1). The directory isolates them.
- The harness parses the score line by the pattern `^\s*([0-9.]+), ([0-9.]+), (\d+)\s*$`, not by "last line".
- Library paths in `run.argos` are absolute, to `build_ours/` or `build_baseline/`.
- `manifest.json` adds: `schema_version`, `mock`, `arm`, `distribution`, `seed`, `set`, `git_commit`, `git_dirty`, `lib_sha` (controller, loop functions, 12 hex), `xml_sha`, `prereg_sha`, `nest_radius_xml`, `nest_radius_eff` (parsed from the log), `respawn`, `param_set`, `layout_sha`, `env` (machine, ARGoS 3.0.0-beta59, threads), `wall_s`.

### 6.5 Per-run summary schema (the single contract)

`results/<real|mock>/runs.csv`, one row per run. `schema_version = 1`. Mock and real write exactly these columns.

| Column | Type | Meaning |
| --- | --- | --- |
| `schema_version` | int | 1 |
| `mock` | int | 1 mock, 0 real |
| `run_id` | str | as §6.4 |
| `set` | str | S0 to S5 |
| `arm` | str | `vendor`, `cpfa`, `qmap`, `qmap-<ablation>` |
| `distribution` | str | `random`, `powerlaw`, `clustered` |
| `seed` | int | |
| `collected` | int | score at 720 s |
| `sim_time_s` | float | from the score line |
| `complete` | int | 1 if 720 s was reached and the score line parsed |
| `code_commit` | str | git hash |
| `git_dirty` | int | `src/` only |
| `lib_sha_controller`, `lib_sha_loop` | str | 12 hex |
| `nest_radius_xml`, `nest_radius_eff` | float | F1 |
| `layout_sha` | str | hash of the initial food list |
| `n_departures` | int | nest departures, all branches |
| `share_fidelity`, `share_pheromone`, `share_map`, `share_random` | float | branch shares |
| `travel_s`, `search_s` | float | swarm totals of `travelingTime`, `searchingTime` |
| `n_queries` | int | map queries |
| `points_inserted` | int | |
| `nodes_total_end`, `leaves_total_end` | int | map size at 720 s |
| `ops_per_query_median` | float | `nodes_visited` |
| `ops_per_query_max` | int | `nodes_visited` |
| `us_per_query_median` | float | |
| `targets_reached_share` | float | |
| `wall_s` | float | |

- Columns that do not apply (cost columns in the baseline arm) are empty, not 0.
- `runs.csv` is the source of every number in the report (`rules/answering.md` §3).

### 6.6 Checks (`tools/check_runs.py`)

1. Every run directory has the 6 files. Columns match `tools/schema.py`.
2. `manifest.metrics.collected` equals the parsed score line and the last per-minute row.
3. One root holds only `mock` = 1 or only `mock` = 0. A mix stops the check.
4. Set completeness: each (set, arm, distribution, seed) cell exists once. A missing cell is listed. A duplicate keeps the latest complete run.
5. `layout_sha` is equal across arms for each (distribution, seed) in S3 and S4.
6. All S3 runs share one `prereg_sha`, one `code_commit`, and `git_dirty` = 0.
7. Deliberate breakage at the M1 gate: a renamed column, a changed score and a mixed root each fail the check.

### 6.7 Analysis outputs (`tools/analyze.py`, `tools/report.py`)

| Output | Content |
| --- | --- |
| `fig_boxplot_3dist.png` | 3 distributions on one x axis. Gray box `cpfa`, colored box `qmap`. 50 points each, overlaid. % improvement and interval written above each pair |
| `fig_paired_diff.png` | mean paired difference per distribution, 95 % interval, zero line |
| `improvement.csv` | per distribution: means, medians, % improvement, interval, verdict, Wilcoxon p, Holm p, detectable size |
| `verdict.json` | `rules/measurement.md` §4.1: comparison, pairs, criteria file hash, analysis code hash |
| `fig_cost_vs_arena.png` | from `bench.csv` (§5.2) |
| `fig_branch_shares.png` | departures per branch, both arms (mechanism) |
| `report.html` | one page with `skills/html-theme/theme.css`, linking the stage reports |

- Wilcoxon: `../01_pheromone/pyproject.toml` has numpy and matplotlib only.
  - Picked: numpy only, no SciPy (D-011).
  - Option 2: a numpy Wilcoxon (normal approximation with tie correction), checked against one hand-worked example.
  - Recommendation: option 1 if the owner agrees, else option 2. The verdict does not depend on it (§6.2 item 4).
- Mock outputs carry "MOCK DATA" in every title and `_MOCK` in every file name.

## 7. Minimum viable product (MVP) ladder and milestones

Ladder: `.claude/CLAUDE.md` "System build phasing". Not restated.

```
Figure 6. Milestones (draft dates, presentation window opens 2026-11-30)

 M1 MVP1 shape ──> M2 MVP2 baseline slice ──> M3 map + bench ──> M4 tune + freeze ──> M5 eval + report
 by 11-14          by 11-18                   by 11-21           by 11-23            by 11-27
 mock end-to-end   invariance, headroom,      G1 benchmark,      S2 (270 runs),      S3, S4 (600 runs),
                   S1 noise (90 runs)         qmap smoke runs    prereg commit       verdict, report
```

- Caption: Figure 6 shows the 5 gates in order. Why: no map code enters the simulation before the baseline harness and the headroom numbers exist.

Table 7. Milestones and exit criteria

| M | Phase | End-to-end cycle | Exit criterion (runnable) |
| --- | --- | --- | --- |
| M1 | MVP1 | `make_mock_runs.py` writes S1 and S3 mock (300 S3 runs) → `check_runs.py` → `analyze.py` → box plot, `improvement.csv`, `verdict.json`, `report.html` | 300 mock runs pass. All MOCK outputs exist. The 3 deliberate breakages (§6.6 item 7) fail the check |
| M2 | MVP2 | `src/` copy builds → `make_runs.py` writes S0 and S1 → `run_argos.py` (one core, timeout) → check → analyze on real `cpfa` only | Determinism holds. S0: 15 of 15 pairs equal. S1: 90 runs pass the check unchanged. Headroom stage report: branch shares, travel and search split, σ per distribution. `analyze.py` lists the missing `qmap` arm and does not crash |
| M3 | MVP3 (core) | `visit_map` and hooks → benchmark (§5.2) → one `qmap` smoke run per distribution → check | `bench.csv` and `fig_cost_vs_arena.png` exist. A and B equivalence holds. G1 lines judged. 3 `qmap` smoke runs pass the same check. Switch off still passes S0 on the new build |
| M4 | MVP3 | S2 tuning rounds → freeze D-row → `prereg/S3_eval.json` committed | Tuning table with every round. Frozen values in `DECISIONS.md`. Pre-registration committed before any S3 run |
| M5 | MVP3 | S3, then S4, then S5 if time → check → analyze → report | 300 S3 runs complete (G2). `verdict.json` committed. Root-cause memo per non-improving distribution (G3). S4 reported as sensitivity |

- MVP2 makes 2 tasks real: (1) the baseline run harness on real runs, (2) the invariance check. The `qmap` arm stays mock in MVP2.
- `visit_map` and the benchmark (U8, U9) are pure code with no simulator. They may start during M1 and M2.
- A schema change needed by real code sends that slice back to MVP1: bump `schema_version`, regenerate the mock.

Table 8. Headroom readings, pre-registered now (S1, baseline arm)

| Reading | Meaning | Action |
| --- | --- | --- |
| `share_random` ≥ 20 % of departures | the map replaces a frequent choice | keep the round-2 list (§6.3) |
| `share_random` < 20 % | the map rarely fires with `q_map` = 0 | round 2 stays as listed (it tests `q_map` first). Report the share |
| `search_s / travel_s` ≥ 2 | time goes to searching. Better search places pay | keep T1 |
| `search_s / travel_s` < 1 | time goes to travel. Far targets may cost score | add the 3 m distance cap to round 3 in place of `spiral` |

## 8. Risks and kill conditions

Table 9. Risks

| ID | Risk | Response | Kill or switch condition (written now) |
| --- | --- | --- | --- |
| R1 | Simulation not deterministic for a fixed seed | M2 precondition check | Fails → stop, root-cause memo, no paired design until fixed |
| R2 | Switch off differs from vendor | §4.3 | Any mismatch → no S3 run until fixed |
| R3 | The map branch rarely fires (pheromone list rarely empty) | headroom gate, `q_map` | none |
| R4 | Far map targets lower a fixed-time count | nearest-first answers, `dist_m` logged | `targets_reached_share` < 50 % in round 1 → 3 m distance cap in round 3 |
| R5 | No score gain. 12 min may stay in the early regime where the papers show no gain [S-IS-2, S-IS-4] | outcome does not matter (repo `CLAUDE.md`). G1 stands alone | `not resolved` or `worse` → root-cause memo, never a widened criterion |
| R6 | Quadtree bug | A fallback, same interface | A and B equivalence fails on 2026-11-21 → ship A, D-row |
| R7 | F1-b drop-off loop slows runs | wall time logged | S4 median run > 60 s → S4 reduced to 20 seeds, D-row |
| R8 | Clustered and Powerlaw drift to Random through respawn | stated in the report (F2-a) | none |
| R9 | Pairing is partial (shared random stream) | `layout_sha` check, stated limit | `layout_sha` differs across arms → stop S3, root-cause memo |
| R10 | Deadline: the window opens 2026-11-30 | M5 by 11-27 | M3 not done by 11-22 → S2 skipped, start values frozen, D-row |
| R11 | Vendor appends result files without an arm label | one working directory per run | none |
| R12 | SciPy not approved | numpy Wilcoxon | none |
| R13 | Reservations lock too much space | `t_res` expiry, `fallback_random` share logged | fallback share > 20 % in round 1 → `r_res` 0.5 m forced into round 2 |

## 9. Design units for `product-manager`

Table 10. Units, size, order. pm phases and allocates them

| # | Unit | M | Size (days) | Depends on |
| --- | --- | --- | --- | --- |
| U1 | `pyproject.toml`, `tools/schema.py`, `check_runs.py` (§6.5, §6.6) | M1 | 1 | none |
| U2 | `make_mock_runs.py` (S1, S3 mock, marked MOCK) | M1 | 0.5 | U1 |
| U3 | `analyze.py` (bootstrap verdict, Wilcoxon, Holm) and figures | M1 | 1.5 | U1, U2 |
| U4 | `report.py` HTML page, stage-report links | M1 | 0.5 | U3 |
| U5 | `src/` copy, `patches/ours.diff`, CMake flag, switch plumbing, branch counters, logger | M2 | 1.5 | none |
| U6 | `make_runs.py` and `run_argos.py` (per-run directory with `results/`, absolute library paths, pattern parse, stamps) | M2 | 1 | U1 |
| U7 | Invariance and determinism script (§4.3) | M2 | 0.5 | U5, U6 |
| U8 | `visit_map` pure module: A and B behind one interface, shared query rule | M3 | 2 | none |
| U9 | `bench_visit_map`, synthetic generator, replay | M3 | 1 | U8 |
| U10 | Controller hooks (§4.2), `queries.csv`, `points.csv` | M3 | 1.5 | U5, U8 |
| U11 | Tuning driver and pick script (§6.3) | M4 | 0.5 | U6 |
| U12 | Pre-registration files and their self-check | M4 | 0.5 | U3 |
| U13 | Final figures, report, root-cause memos | M5 | 1.5 | U3, U4, runs |

- Sum: 14 person-days.

## 10. Open items

- Mission block lines: drafts in the hand-back report. pm writes them into `PLAN.md` after Fable logs them.
- Professor questions (optional owner action, before S3 only): which nest radius reading is graded (F1). Which parameter set is "original CPFA" for Powerlaw and Clustered (F3).
- ~~SciPy approval (§6.7).~~ Resolved: numpy only (D-011).
- Whether ARGoS beta59 accepts unknown attributes on the vendor build. The S0 run answers it. If not, the vendor arm uses a copy of the experiment file without our attributes.
- The memory crossover (§3.3) is inference. The benchmark measures it before G1 line 3 is judged.
