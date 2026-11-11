# Pheromone foraging under misleading trails: Design

- Author: system-architect, 2026-11-10. Status: strategy A picked (Fable, owner-delegated, D-006). Picks: `decisions/2026-11-10_fable_design_picks.md`.
- Sources: `research/pheromone_research.md` (S-PH-n IDs), `../site/en/projects/pheromone-misleading-trails.html`, `../DESIGN.md` §2 (floor painting, cited not restated).
- Build pattern: `hw5_ARGoS_02/src/` (CMake, controller, loop functions, `.argos`). ARGoS 3.0.0-beta59, C++17.

## 0. Mission block (quoted from `PLAN.md`)

> - Mission: Keep swarm foraging trustworthy when some robots lay false pheromone trails.
> - Vision: One chart and one demo show the defense winning back lost food.
> - G1: By 2026-11-24, log 80 runs with food collected and wasted robot-seconds (4 detractor counts 0/1/2/4 x 2 defense states x 10 seeds).
> - G2: By 2026-11-28, report recovered loss share for detractor counts 1, 2, 4 with 10-seed error bars.

- Source: the mission block of `PLAN.md` (D-004). `product-manager` writes `PLAN.md`. If the two differ, `PLAN.md` wins.
- S1 → G1, G2: strategy A (D-006). Listed alternative: B only. C is a post-G2 stretch.
- Constraints: no local training. The owner runs builds and simulations by hand (repo-root `CLAUDE.md` Execution).
- Exception (D-002): the main session builds and runs one 1-seed smoke run per gate, on the owner's order.

## 1. Strategy options (S1 → G1, G2)

Table 1. Pheromone substrate and defense options

| | A: floor grid, virtual sensor (picked, D-006) | B: waypoint pheromone (Luna and Lu style) | C: hybrid, grid plus waypoint defense |
| --- | --- | --- | --- |
| Substrate | 2-layer grid (true, false) in loop functions. Exponential evaporation | List of waypoints (x, y, strength, creator id). `w = e^(-t·λ_pd)` [S-PH-1] | Grid of A for following. Each deposit also tags a creator id |
| Sensing | Loop functions write 8 probe values per robot into a controller struct | Robot in the nest receives the strongest waypoint, then drives to it by position | As A |
| Attack | Detractor lays the same deposit profile from a decoy point to the nest | Detractor reports a waypoint near a decoy | As A |
| Defense | Private suspect-end list, no communication (page Step 5, Aswale-style [S-PH-6]) | Travel-time check plus strikes per creator [S-PH-1] | A's rule plus density-based spatial clustering of applications with noise (DBSCAN) on suspect ends, creator graph |
| Cost, all units incl. tools (person-days, inference) | 14.5 (Table 7 sum) | 14 | 21 to 24 |
| Main risk | Gradient following on a grid is untested in our sources [S-PH-1 Q3 row "no source"] | A central waypoint store is not stigmergy. Departs from the page and the demo | Does not fit 2 weeks with 4 people |
| Fit to G1 | Good. Headless runs are cheap (repaint only in Qt, `../DESIGN.md` §2.1) | Good | At risk by 2026-11-24 |
| Fit to G2 | Good. Loss and recovery are measured on ground-truth layers | Good, but the result restates Prof. Lu's paper | Best evidence, latest date |
| Fit to Vision (demo) | Best. True and false trails are painted in two tints | Weak. Waypoints are invisible without extra Qt drawing | As A |

- Picked: **A** (D-006). It matches the page and the Vision demo. Its defense is the novelty angle in the research file (Implications 9).
- Budget: 4 people × 10 working days = 40 person-days. A and B fit. C fits only with no slack.
- Fallback: B, only if the Q7 judgement in §5 fails (risk R1, D-010).
- C is a stretch goal after G2 only. It adds no G1 or G2 measure.

## 2. Components and data flow (option A)

```
Figure 1. Components and one simulation tick

 .argos file (params, seed, git_commit, code_sha)  <- tools/make_sweep.py, one per run
        |
        v
 +----------------------- loop functions (owns ALL world state) ------------------+
 | PheromoneGrid (pure core)    FoodField (pure)      RunLogger                   |
 |  true[1600], false[1600]     sources, decoys       ticks.csv events.csv        |
 |  Evaporate() Deposit()       Pickup() Drop()       robots.csv manifest.json    |
 |  Probe(x,y)                                                                    |
 +--------------|--------------------------------------------^--------------------+
                | (1) PreStep: evaporate, food pickup/drop,   | (3) PostStep: apply
                |     write SPheromoneReading per robot       |     SDepositRequest,
                v                                             |     ground truth, log
 +------------------------------ controller (per robot) -----+--------------------+
 | (2) ControlStep: reads SPheromoneReading, SFoodData, positioning,              |
 |     proximity. Sets wheels, LEDs, SDepositRequest. Keeps private suspect list   |
 +---------------------------------------------------------------------------------+
        |
        v
 runs/<runid>/  ->  tools/check_runs.py  ->  tools/analyze.py  ->  results/ (G2 chart)
```

- Caption: Figure 1 shows who owns each piece of state and the order inside one tick. Why: the controller sees only what a real robot could sense.
- Tick order is from the header: `PreStep` runs before sensors update. `PostStep` runs after the control step (`loop_functions.h:114-127`).
- So a reading written in `PreStep` reaches `ControlStep` in the same tick. A deposit lands one tick later. Both are fine.

### 2.1 Virtual pheromone sensor

- Real robots cannot read loop-function memory. In sim, the loop functions play the sensor hardware.
- The pattern is the course's own: hw5 loop functions write the controller's `SFoodData` (`search_deliver.h:43`, `.cpp:144-185`).
- `SPheromoneReading { Real here; Real probe[8]; }`: sum of both layers at the robot centre and at 8 probe points.
- Probe ring: 8 points at 0.15 m, every 45°, starting at the heading (inference).
- Why a full ring: a robot that crosses a trail or faces the nest still sees the uphill side.
- Real-robot analogue: a ring of 8 local sensors, as the Kilobot antenna sectors [S-PH-7].
- The controller never receives the layer split, a deposit's creator, or any robot's role.
- `SDepositRequest { bool active; Real amount; }`: the controller asks. The loop functions write it into the layer that matches the robot's role.
- Role comes from the entity id prefix: `hb_` honest, `dt_` detractor (same pattern as `../DESIGN.md` §2.3).

### 2.2 Floor paint and the nest test

- The ground sensor gives one grey value (`../DESIGN.md` §2.2). Grey 0.25 to 0.75 means "in nest" in hw5 (`search_deliver.cpp:229-232`).
- Decision (D-008): the nest test uses the **positioning sensor** (`x < -1.0`). The ground sensor is not used for nest or pheromone.
- Floor paint is display only: nest grey, food sources black, true pheromone green tint, false red tint.
- Tints keep grey value above 0.80 at full strength. Pale green (200, 255, 200) gives 0.91. Pale red (255, 200, 200) gives 0.85 (`ToGrayScale` weights, `../DESIGN.md` §2.2).
- So a stale ground-sensor nest test would still not fire on pheromone.
- `GetFloorColor` is an O(1) cell lookup. `SetChanged()` runs every 10 ticks in Qt runs only (`repaint_every`).

## 3. Behavior

### 3.1 Food model

- Food comes from persistent sources, not single items. Why: a trail to a single item is stale once the item is taken.
- `n_sources` disc sources, radius 0.25 m. A pickup inside a source never empties it (Font Llenas sources [S-PH-7]).
- Decoys: empty discs, same radius as sources.
- Decoys sit in the same distance band from the nest as sources.
- Each decoy is at least 1.5 m from every source.
- Layout stream: a dedicated random category `layout`, seeded with the run seed.
- It always draws 3 sources and 2 decoys, then uses the first `n_decoys`. So all 8 cells of a seed share sources and decoy spots.
- Decoys per detractor count (D-009): d = 1, 2, 4 use 1, 2, 2 decoys.
- So d = 2 to 4 raises the trail refresh rate, not the decoy count. The report states this.
- Robot start poses use the `argos` stream through `<distribute>`. They differ across cells because the robot count differs.
- So the bootstrap pairs cells on layout, not on robot starts.
- `CRandom::CreateCategory` for the `layout` stream is not verified on beta59. MVP2 checks it.

### 3.2 Honest controller

```
Figure 2. Honest forager states

 REST --t>=t_rest--> SEARCH <----------trail lost (low)---------- FOLLOW
   ^                  | ^  |                                      ^  |  |
   |                  | |  +--probe>θ_on, uphill, not suppressed--+  |  | peak
   |     pickup or    | |                                            |  | (valid or
   |     t_search     | +--t_end over, no food----------+            |  |  invalid)
   |                  v    (suspect only if valid peak   |            |  v
   +------drop------ RETURN    and defense on)           +------- END_SEARCH
                    (deposit  ^  ^                                    |
                    if carry) |  +-------------pickup-----------------+
                              +----------------pickup in FOLLOW------+
```

- Caption: Figure 2 shows the honest state machine. Why: END_SEARCH is the only place a false trail can be detected.
- Transitions to RETURN: pickup in SEARCH, pickup in FOLLOW, pickup in END_SEARCH, or `t_search` over.
- REST: in nest, at least `t_rest`. LED off.
- SEARCH: correlated random walk with obstacle avoidance (hw5 `DiffusionVector`). LED green.
- FOLLOW entry: the largest probe > `θ_on` and > `here` + `δ_up`. A flat ridge does not start a follow.
- FOLLOW: steer to the largest probe. LED yellow. Record `here_entry` and the entry time. Pickup leads to RETURN.
- Peak test: all 8 probes ≤ `here` for `t_peak`, or all probes < `θ_off` for `t_peak`.
- Peak by a low reading ("trail lost") goes to SEARCH, not END_SEARCH.
- END_SEARCH: random walk inside 0.3 m of the peak for `t_end`. Pickup leads to RETURN.
- A peak is "valid" only after `t_follow_min` in FOLLOW and `here` ≥ 2 × `here_entry`.
- An invalid peak also goes to END_SEARCH, but it never adds a suspect.
- Why END_SEARCH: a robot that joins near a true trail end must still search for the source.
- Why no suspect: it stops suspects on honest trails after a short or flat follow.
- With `λ_dep` 0.077, the 2 × rise needs about 9 s (0.9 m) of follow. A shorter follow is invalid but still searches.
- RETURN: drive to nest centre by position. LED blue.
- Deposit: while carrying, outside the nest, `amount = A_max · exp(-λ_dep · τ)`. τ = seconds since pickup.
- Why decay with τ: the trail is strongest at the food. Uphill means toward the food [S-PH-6].
- Grid merge: a cell takes the max of its value and the deposit [S-PH-6]. Why: it stops build-up near the nest.
- Footprint: a deposit writes the 3 × 3 cells (0.30 m) under the robot. Why: a robot that swerves around a returner stays on the trail.

### 3.3 Detractor controller

- REST, then GO_DECOY: drive to its assigned decoy by position. LED red (page Table 1).
- At the decoy: wait 2 s (mimics a pickup), set τ = 0.
- RETURN_LAY: drive to nest. Deposit the honest profile into the false layer.
- Repeat. Same `t_rest` as honest. Detractors never carry food.
- Decoy assignment: loop functions write it at `Init` (the attacker knows its lure point).

### 3.4 Defense rule (no communication)

1. A robot leaves END_SEARCH from a valid peak with no food. It records the peak as a suspect point.
2. Merge: a new point within `r_merge` of a stored one updates that point's centroid and count.
3. Memory holds at most `n_mem` points, oldest dropped.
4. Ignore: probe values at points within `r_suspect` of a suspect point read as 0.
5. Cone: in FOLLOW, abort to SEARCH if a suspect point lies within `±α_cone` of the heading and within `d_cone`.
6. Rule 5 exists because a false trail still attracts far from its end. Rule 4 alone wastes most of the trip again.

Cone geometry check (start values `α_cone` = 15°, `d_cone` = 1.0 m):

- Worst case: the suspect is 1.0 m ahead and a real source is 1.5 m to the side of it.
- Bearing gap seen from the robot: atan(1.5 / 1.0) = 56°. That is far outside 15°.
- From 2.5 m away the gap is atan(1.5 / 2.5) = 31°. But 2.5 m is beyond `d_cone`, so the cone is off there.
- Cost: a fooled robot still walks the first part of a false trail. `wasted_robot_seconds` shows that cost.

- Defense off: steps 1 to 5 do not run. Everything else is identical.
- DBSCAN on suspect ends is optional (option C). Not in G2.

### 3.5 Parameters (starting values)

Table 2. Starting parameters. "inference" = no direct source

| Name | Value | Source |
| --- | --- | --- |
| `ticks_per_second` | 10 | [S-PH-4], hw5 |
| `length` | 600 s | page "food per 10 minutes". hw5 uses 0, which never ends headless |
| Arena, walls | 5 × 5 × 2 m, inner faces ±2 m | [S-PH-4], hw5 |
| Nest | x < -1.0 m | [S-PH-2], hw5 |
| Honest robots `n_honest` | 20 | [S-PH-4] |
| Detractors `n_det` | 0, 1, 2, 4, added to the 20 (totals 20, 21, 22, 24) | page. Added: D-005 |
| `max_speed` | 10 cm/s | hw5 |
| Grid cell | 0.10 m, 40 × 40 = 1600 cells, 5 px per cell at 50 px/m | inference. Whole pixels per cell (`../DESIGN.md` §2.1) |
| `n_sources`, `n_decoys` | 3, 1 per detractor, max 2 (d = 1, 2, 4 → 1, 2, 2) | inference. D-009 |
| Source and decoy radius | 0.25 m | inference |
| Decoy to source gap | ≥ 1.5 m | inference, from the cone check in §3.4 |
| Source band | x in [0.5, 1.7] m | inference, inside [S-PH-2] range |
| Probe ring | 8 points, 0.15 m, every 45° | inference |
| Deposit footprint | 3 × 3 cells | inference |
| `δ_up` | 5 | inference |
| `t_peak`, `t_follow_min` | 1 s, 5 s | inference |
| `n_mem` | 16 | inference |
| `α_cone` | 15° | inference |
| Wasted-time decoy radius | 0.5 m | inference (decoy radius + 0.25 m) |
| `repaint_every` | 10 ticks, Qt runs only | inference |
| `A_max` | 1000 | [S-PH-6] |
| `λ_dep` | 0.077 per s | inference: end-to-start ratio 0.1 over a 30 s trip, ln(10)/30. The source band reaches 2.7 m from the nest. D-007 |
| Evaporation | half-life 60 s, factor 0.5^(1/600) = 0.99885 per tick | inference: one-way trip 2 m / 0.10 m/s = 20 s. A trail must last about 3 trips. D-007 |
| `θ_on`, `θ_off` | 20, 5 | inference |
| `t_rest`, `t_search`, `t_end` | 5 s, 120 s, 15 s | inference. hw5 min rest is 50 ticks |
| `r_merge`, `r_suspect`, `d_cone` | 0.3 m, 0.4 m, 1.0 m | inference |
| Sweep seeds | 1 to 10, same in all 8 cells | page (10 seeds). Values: inference |
| Tuning seeds | 101 to 103, never used in the sweep | inference. Why: tuning on sweep seeds would fit the result |
| Judgement seeds (Q7) | 104 to 106, used once | D-010 |

Pheromone tuning rule (D-007, fixed before running):

1. Runs: d = 0, defense off, seeds 101 to 103.
2. Round 1 uses the start values.
3. Rounds 2 and 3 change one value only.
4. Candidates: half-life 30, 60 or 120 s. `λ_dep` 0.05, 0.077 or 0.115.
5. Metric: mean `food_collected` with pheromone on. A tie goes to the earlier round.
6. At most 3 rounds. The picked values freeze in a D-row before defense tuning.
7. They are never re-tuned with detractor runs.

Defense tuning rule (D-011, fixed before running, start of MVP3):

1. Runs: d = 2, defense on, seeds 101 to 103.
2. Round 1 uses the start values. Rounds 2 and 3 change one value only.
3. Values in scope: `r_suspect`, `α_cone`, `d_cone`, `t_end`.
4. Metric: mean `F(2, on)`. A tie goes to the earlier round.
5. At most 3 rounds. The picked values freeze in a D-row before the 80-run sweep (`rules/measurement.md` §1).

## 4. Log schema (the single contract)

`schema_version = 1`. Mock and real write exactly these files and columns.

```
runs/<runid>/                      mock/runs/<runid>/   (same layout)
  manifest.json   1 per run        runid = <YYYYMMDD-HHMMSS>_d<k>_def<0|1>_s<seed>
  ticks.csv       1 row per tick (6000 rows)           mock runid starts MOCK_
  robots.csv      1 row per robot per second
  events.csv      1 row per event
```

Table 3. `ticks.csv`, one row per tick. Why: G1 counts per-tick time, and 6000 rows are small

| Column | Type | Meaning |
| --- | --- | --- |
| `tick` | int | Simulation clock |
| `food_collected` | int | Cumulative deliveries to the nest |
| `wasted_robot_seconds` | float | Cumulative, definition below |
| `n_rest`, `n_search`, `n_follow`, `n_end`, `n_return` | int | Honest robots per state |
| `pher_true_sum`, `pher_false_sum` | float | Grid sums per layer |
| `suspects_total` | int | Suspect points held, all robots |
| `mock` | int | 1 mock, 0 real. Constant per run |

Table 4. Other files

| File | Columns |
| --- | --- |
| `robots.csv` | `tick, robot_id, role, x, y, yaw_deg, state, carrying, here, false_share` |
| `events.csv` | `tick, robot_id, event, x, y` with event in `pickup, drop, follow_start, peak, suspect_add, cone_abort, decoy_reach` |

`manifest.json` fields (`rules/measurement.md` §2.1, extended):

```json
{
  "schema_version": 1, "mock": false,
  "runid": "20261120-101500_d2_def1_s3",
  "code_version": "v1",
  "code_sha": {"loop_functions": "<sha256[:12]>", "controller": "<sha256[:12]>"},
  "git_commit": "<sha>", "git_dirty": false,
  "params": {"n_det": 2, "defense": 1, "seed": 3, "length_s": 600, "...": "every .argos value"},
  "env": {"machine": "...", "argos": "3.0.0-beta59", "threads": 0},
  "metrics": {"food_collected": 0, "wasted_robot_seconds": 0.0, "ticks": 6000, "complete": true}
}
```

- `code_version`: a constant in the loop functions, bumped by hand with a `CHANGELOG.md` line.
- `make_sweep.py` hashes both built libraries and reads `git rev-parse HEAD` and `git status`.
- It writes `git_commit`, `git_dirty` and both hashes as attributes in the generated `.argos` file.
- The loop functions copy them into `manifest.json`. Why: C++ has no built-in hash or git access.
- `metrics` must equal the last `ticks.csv` row. `check_runs.py` enforces it.
- `complete` is false if the run stopped before `length`.

### 4.1 Metric definitions

- `food_collected`: items delivered to the nest by honest robots in 600 s.
- `false_share` of a cell: false / (true + false). It is 0 when both are 0.
- `wasted_robot_seconds`: sum over honest robots of ticks / 10, where either holds:
  1. state is FOLLOW and `false_share` under the robot ≥ 0.5,
  2. state is END_SEARCH within 0.5 m of a decoy centre.
- It uses loop-function ground truth only. So it is defined the same with defense on and off.
- At 0 detractors the false layer is empty, so the value is 0 by definition.

### 4.2 G2 computation (`tools/analyze.py`)

- `F(d, def)` = mean over the 10 seeds of `food_collected`.
- Loss: `L(d) = F(0, off) - F(d, off)`.
- Gain: `G(d) = F(d, on) - F(d, off)`.
- Recovered loss share: `R(d) = G(d) / L(d)`, for d in 1, 2, 4.
- Ratio of means, not mean of per-seed ratios. Why: a small per-seed loss explodes the ratio.
- Error bars: 95 % percentile bootstrap, 10,000 resamples of the seed index, paired across cells.
- If the 95 % interval of `L(d)` contains 0, the report writes "loss not resolved at d". `R(d)` is not plotted.
- Defense cost: `F(0, on) - F(0, off)` is also reported.
- Cell check: exactly 8 cells × seeds 1 to 10. A missing cell is listed. A duplicate keeps the latest complete run and lists the rest.
- Mixing guard: all manifests under one root must share `mock`. Otherwise the script stops.
- A mock chart carries a "MOCK DATA" stamp in the title and the file name `*_MOCK.png`.

## 5. MVP ladder (`.claude/CLAUDE.md` "System build phasing")

Table 5. Phases, end-to-end cycle and exit

| Phase | End-to-end cycle | Exit criterion (runnable) | Who runs |
| --- | --- | --- | --- |
| MVP1 shape (by 2026-11-13) | `make_mock_runs.py` writes 80 runs to `mock/runs/` → `check_runs.py` passes → `analyze.py` draws the G2 chart and the summary table | 80 mock runs pass the check. Chart `results/mock/g2_recovered_share_MOCK.png` exists. Deliberate breakage: a renamed column in one run fails the check. A mixed root stops `analyze.py` | Main session (D-012) |
| MVP2 real slice (by 2026-11-18) | Build `src/` → `make_sweep.py` writes one `.argos` (d = 0, defense off, seed 1) → 1 headless run → `check_runs.py` → `analyze.py` on that root | Real run passes the same check unchanged. `food_collected` > 0. `analyze.py` lists 79 missing cells and does not crash. Qt run shows green trails forming and fading | Main session 1-seed smoke (D-002) |
| MVP3 core (sweep by 2026-11-24, report by 2026-11-28) | Detractors + defense → defense tuning runs → freeze → `make_sweep.py` writes 80 `.argos` files and `run_sweep.sh` → owner runs → check → G2 chart from real logs | 80 complete real runs pass the check (G1). Real G2 chart with error bars (G2). Qt demo at d = 2, defense off vs on | Owner runs tuning and sweep. Main session 1-seed smoke first |

Q7 judgement: keep A or switch to B (D-010, written before the runs):

- When: once, after the pheromone tuning freeze (D-007). Deadline 2026-11-17.
- Runs: d = 0, defense off, held-out seeds 104 to 106. Arm 1 pheromone on. Arm 2 `θ_on` = ∞ (no following). 6 runs.
- Runner: the owner, or the main session on the owner's order.
- Pass: arm 1 mean `food_collected` ≥ 1.2 × arm 2 mean, AND arm 1 > arm 2 on all 3 seeds.
- Pass keeps A. Fail switches to B with a D-row. No retry.
- Why held-out seeds: best of 3 rounds on the tuning seeds is optimistic.
- Why the deadline: after it, 5 workdays (20 person-days) remain. B needs about 8.
- 1.2 is a planning threshold, not derived from noise.

- MVP2 makes real two tasks: (1) the pheromone grid with evaporation and deposits, (2) the honest forager writing the real schema.
- Everything else stays mock in MVP2. The mock stays as the schema's reference after MVP3.
- A schema change needed by real code sends that slice back to MVP1 (bump `schema_version`, regenerate mock).
- Each stage writes the short stage report the ladder names. One summary page links them.

## 6. Directory layout

```
01_pheromone/
  DESIGN.md  PLAN.md (pm)  STATUS.md  DECISIONS.md  CHANGELOG.md  research/
  src/
    CMakeLists.txt                      copy of hw5 top level (C++17, find_package(ARGoS))
    controllers/
      CMakeLists.txt
      pheromone_forager/                honest + detractor (role from <params>), shared motion code
    loop_functions/
      CMakeLists.txt
      pheromone_loop_functions/
        pheromone_grid.{h,cpp}          pure: index, evaporate, deposit, probe. No simulator calls
        food_field.{h,cpp}              pure: sources, decoys, pickup test
        pheromone_loop_functions.{h,cpp}
        pheromone_qt_user_functions.{h,cpp}   guarded by ARGOS_QTOPENGL_FOUND as hw5
    experiments/
      pheromone_qt.argos                demo, with <visualization>
      pheromone_headless.template.argos sweep template, no <visualization>
      generated/                        gitignored, written by make_sweep.py
  tools/
    schema.py          columns, types, validator (single Python copy of §4)
    make_mock_runs.py  MOCK generator, writes only to mock/runs/
    check_runs.py      validates a runs root against schema.py
    make_sweep.py      writes 80 .argos files + run_sweep.sh, stamps git_commit
    analyze.py         §4.2, writes results/<real|mock>/
  mock/runs/           committed, small, every runid starts MOCK_
  runs/                gitignored (80 runs, about 50 to 100 MB, inference)
  results/             committed: summary.csv (one row per run), figures, README
```

- Why `pheromone_grid` is pure: it is easy to check by deliberate breakage. Tests are suspended (`rules/core.md`).
- No `*.test.*` files. `check_runs.py` is a validator, not a test runner.

## 7. Risks

Table 6. Risks and responses

| ID | Risk | Response |
| --- | --- | --- |
| R1 | Grid gradient following does not lead robots to food. No source tested it on foot-bots | Q7 judgement in §5 (D-010). Switch to B if it fails |
| R2 | Loss at d = 1 is inside seed noise | §4.2 writes "loss not resolved". Do not widen criteria after the result |
| R3 | Defense never pays off. A false trail is re-laid faster than robots learn | Cone rule 5. Log `cone_abort` events to see it |
| R4 | Max-merge near the nest mixes layers, so `false_share` is ambiguous there | Deposits stop inside the nest. Metric counts FOLLOW only, outside the nest |
| R5 | Honest trails flagged as suspect (false positive) | Valid-peak rule (§3.2). `analyze.py` counts every `suspect_add` farther than 0.5 m from a decoy as a false positive |
| R11 | Robot starts differ across cells, so pairing is partial | Layout stream is shared (§3.1). Report the pairing limit |
| R6 | Repaint slows Qt runs | Repaint every 10 ticks. Headless sweep has no repaint |
| R7 | XML tag spellings and class names unverified (research open questions) | Copy hw5 `.argos` tags. MVP2 build catches the rest |
| R8 | No seed flag on the command line (`../DESIGN.md` §3.4, not verified) | One generated `.argos` per run |
| R9 | 4 people edit the same loop functions | Pure modules split by file. One owner per file (§8) |
| R10 | Added detractors (D-005) add slight crowding, so loss is not purely deception | The report notes the crowding effect |

## 8. Design units for `product-manager`

Table 7. Units, size and order. pm phases and allocates them

| # | Unit | Phase | Size (days) | Depends on |
| --- | --- | --- | --- | --- |
| U1 | `tools/schema.py` + `check_runs.py` from §4 | MVP1 | 1 | none |
| U2 | `make_mock_runs.py` (80 MOCK runs) | MVP1 | 1 | U1 |
| U3 | `analyze.py` (§4.2) + mock chart | MVP1 | 1.5 | U1, U2 |
| U4 | `src/` skeleton: CMake, empty controller and loop functions, `.argos` files | MVP2 | 1 | none |
| U5 | `pheromone_grid` + `food_field` + floor paint | MVP2 | 2 | U4 |
| U6 | Honest controller (§3.2), virtual sensor structs | MVP2 | 2 | U4 |
| U7 | `RunLogger` writing §4 | MVP2 | 1 | U1, U5 |
| U8 | `make_sweep.py`: one `.argos` per run, hashes, git stamp | MVP2 | 0.5 | U4 |
| U9 | Detractor controller (§3.3) | MVP3 | 1 | U6 |
| U10 | Defense rule (§3.4) | MVP3 | 1.5 | U6 |
| U11 | `run_sweep.sh` for 80 runs + tuning run list | MVP3 | 0.5 | U8 |
| U12 | Real G2 chart, demo video, stage reports | MVP3 | 1.5 | U3, sweep |

- Sum: 14.5 person-days. Table 1 uses this sum for A.

## 9. Resolved decisions (Fable, owner-delegated, 2026-11-10)

Detail: `decisions/2026-11-10_fable_design_picks.md`. Rows: `DECISIONS.md`.

Table 8. Picks

| Q | Pick | D-row | Section |
| --- | --- | --- | --- |
| Q1 | Detractors added to the 20 honest robots | D-005 | §3.5 |
| Q2 | Strategy A. B is the only fallback. C is a post-G2 stretch | D-006 | §1 |
| Q3 | Half-life 60 s. `λ_dep` start 0.077 per s. Pheromone tuning rule | D-007 | §3.5 |
| Q4 | Main session runs `make_mock_runs.py` | D-012 | §5 |
| Q5 | Nest test by positioning sensor. Floor color is display only | D-008 | §2.2 |
| Q6 | 1 decoy per detractor, max 2. `n_sources` = 3 | D-009 | §3.1 |
| Q7 | One judgement on seeds 104 to 106, 1.2 × and all 3 seeds, by 2026-11-17 | D-010 | §5 |
| (new) | Defense tuning rule, d = 2, seeds 101 to 103 | D-011 | §3.5 |
