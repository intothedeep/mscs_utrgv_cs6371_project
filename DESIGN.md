# Territory Capture Game in ARGoS 3: Design

- Course: CSCI 6371 Robotics Programming, UTRGV, Fall 2026.
- Instructor: Prof. Qi (Luki) Lu, printed as "Lu Qi" in the task (`research/lu_qi.md` §1.1).
- Team: 4 members.
- Presentation window: 2026-11-30 to 2026-12-11.
- Build scope: 2 weeks, from 2026-11-10.
- ARGoS: 3.0.0-beta59, prefix `/usr/local`, double precision.
- Author role: system-architect. Status: draft for the owner's pick (2026-11-10).

## 0. Mission block (pending `PLAN.md`)

- No `PLAN.md` exists yet (`rules/docs.md` §0.1).
- `product-manager` creates `PLAN.md` with the mission block after the owner approves.
- This document will then quote that block here.
- Draft lines for the owner are in §0.1. They are not approved.

### 0.1 Draft lines (architect draft, owner decides)

| Level | Draft line |
| --- | --- |
| Mission | Owner sets (owner-only line, `rules/core.md` Decision hierarchy) |
| Vision | Owner sets (owner-only line) |
| G1 (numeric) | By 2026-11-24, one strategy beats random walk on final territory share |
| G1 measure | Paired over at least 20 seeds, 95% bootstrap interval of the share difference above 0 |
| G2 (numeric) | By 2026-11-28, one Qt demo video and one results figure from saved logs exist |
| RQ1 (question) | Does a learned tabular policy beat the best hand-written swarm rule here? |

- Options A, B and C in §5 each trace to these lines (Table 7).
- RQ1 applies only if the owner picks B or C.

## 1. System at a glance

```
Figure 1. Components and data flow (one simulation step)

  .argos file (params, seed, teams)
        |
        v
+----------------- ARGoS core (one process) -----------------+
|                                                             |
|  foot-bot "t0_*" x N   foot-bot "t1_*" x N                  |
|   controller (team 0)   controller (team 1)                 |
|     | reads: motor-ground (4 grey values)                   |
|     |        positioning (x, y, yaw)                        |
|     |        proximity (8+ rays), range-and-bearing packets |
|     | writes: wheel speeds, LEDs, range-and-bearing packet  |
|                                                             |
|  loop functions (territory)                                 |
|     PostStep: robot centre -> cell -> capture rule          |
|               -> counts -> ticks.csv (+ robots.csv)         |
|               -> floor SetChanged() only if a cell changed  |
|     GetFloorColor(x, y): O(1) lookup in the ownership grid  |
|     PostExperiment: cells_final.csv, manifest.json          |
|                                                             |
|  Qt user functions (visual build only): team marker, score |
+-------------------------------------------------------------+
        |
        v
  runs/<runid>_<tag>/ : ticks.csv, cells_final.csv, robots.csv, manifest.json
        |
        v
  analysis script (saved outputs only) -> figures, summary page
```

- Caption: Figure 1 shows who reads and writes the ownership grid. Why: the grid is the one shared state.
- The loop functions own the grid. Controllers never read it directly (§2.4).

## 2. Confirmed mechanisms (from source)

### 2.1 How this course's code paints the floor

Read with the Read tool: `hw5_ARGoS_02/src/loop_functions/search_deliver_loop_functions/*`, `hw5_ARGoS_02/src/experiments/search_deliver1.argos`.

Table 1. Floor painting in hw5

| Piece | Where (hw5) | What it does |
| --- | --- | --- |
| `<floor id="floor" source="loop_functions" pixels_per_meter="50"/>` | `search_deliver1.argos` line 80 | Floor color comes from the loop functions |
| `CColor GetFloorColor(const CVector2&)` | `search_deliver_loop_functions.cpp` line 95 | Returns a color per floor point |
| `m_pcFloor = &GetSpace().GetFloorEntity()` | same file, line 30 | Gets the floor entity pointer |
| `m_pcFloor->SetChanged()` | same file, lines 162, 183 | Marks the floor dirty after a state change |
| `RegisterUserFunction<..., CFootBotEntity>(&...::Draw)` | `search_deliver_qt_user_functions.cpp` line 12 | Draws extra shapes per foot-bot in Qt |
| `if(ARGOS_QTOPENGL_FOUND)` guard | `loop_functions/.../CMakeLists.txt` lines 4, 21 | Builds the Qt file only when Qt exists |

Table 2. API confirmed on the installed headers (beta59)

| API | Header | Evidence |
| --- | --- | --- |
| `virtual CColor GetFloorColor(const CVector2&)` | `core/simulator/loop_functions.h:169` | Declared, overridable |
| `PreStep`, `PostStep`, `IsExperimentFinished`, `PostExperiment`, `Reset`, `Destroy` | `core/simulator/loop_functions.h:103-155` | All virtual |
| `PostStep` timing | same, line 123 | "after a control step ... before the actuators are updated" |
| `CFloorEntity::SetChanged()`, `HasChanged()`, `ClearChanged()` | `core/simulator/entity/floor_entity.h:113-131` | Comment: "mainly used by the OpenGL visualization to ... create a new texture" |
| `EColorSource { UNSET, FROM_IMAGE, FROM_LOOP_FUNCTIONS }` | `floor_entity.h:46` | Loop-function source exists |
| `CSimulator::GetRandomSeed()` | `core/simulator/simulator.h:191` | Loop functions can log the seed |
| `CQTOpenGLUserFunctions::DrawInWorld`, `DrawOverlay(QPainter&)`, `DrawText` | `qtopengl_user_functions.h:225, 234, 373` | Score text overlay is possible |

Design consequences:

- `SetChanged()` only triggers a texture rebuild for Qt. Call it only in a step where a cell changed owner.
- The texture rebuild calls `GetFloorColor` once per pixel. At 50 px/m on 5 m × 5 m that is 62,500 calls.
- So `GetFloorColor` must be an O(1) grid lookup. hw5 loops over all food items per call.
- Cell size must be a whole number of pixels. 0.20 m × 50 px/m = 10 px per cell.
- Points outside the grid return the "outside" color (Table 3). No index is computed for them.

### 2.2 How a robot senses floor color

- Sensor: `footbot_motor_ground`, implementation `rot_z_only` (hw5 `.argos` line 36).
- Interface: `CCI_FootBotMotorGroundSensor::SReading { Real Value; CVector2 Offset; }` (`ci_footbot_motor_ground_sensor.h:50-52`).
- There are 4 readings. 0 and 1 are front, 2 and 3 are back (header comment, lines 16-25).
- Each reading is ONE grey value. Hue is lost. Teams must differ by luminance, not hue.
- The sim sensor holds a floor-entity pointer and an optional noise range (`footbot_motor_ground_rotzonly_sensor.h:50-62`).
- The color-to-value code is in a `.cpp` that is not installed. So the mapping below is **inferred**.
- Inference: value = `CColor::ToGrayScale()` / 255. `ToGrayScale` = 0.299 R + 0.587 G + 0.114 B (`color.h:68-72`).
- Support: hw5's comment says white reads 1, black 0, grey about 0.5 (`search_deliver.cpp:217-227`).
- MVP1 check M1-C1 (§6) logs one reading per color to confirm it.

Table 3. Floor colors and controller thresholds (inferred values)

| Cell state | RGB | Grey value (inferred) | Controller band |
| --- | --- | --- | --- |
| Free | 255, 255, 255 | 1.00 | above 0.85 |
| Team 0 (blue) | 0, 0, 200 | 0.09 | below 0.35 |
| Team 1 (orange) | 255, 140, 0 | 0.62 | 0.35 to 0.85 |
| Outside grid | 128, 128, 128 | 0.50 | not reachable (walls) |

- Gaps between bands are at least 0.26. Sensor noise stays off by default.
- More than 3 teams would crowd the grey scale. See open question Q5.

Footprint and timing:

- Foot-bot body diameter is about 0.17 m. A cell is 0.20 m.
- The 4 sensors sit near the wheels, a few cm from the centre. Exact offsets are in `SReading::Offset` at run time.
- Capture uses the robot centre (loop functions). Sensing uses 4 offset points (controller).

```
Figure 2. One robot crossing a cell border (driving right)

   cell k (own)        | cell k+1 (enemy)
                       |
      back  centre  front
       2,3 ---o---- 0,1|          front pair reads k+1: ENEMY
                       |
       2,3 -------o--- | 0,1      centre enters k+1 -> capture
                       |          now all 4 readings: OWN
```

- Caption: Figure 2 shows when each sensor pair sees the next cell. Why: capture repaints a cell before the back pair reaches it.
- The back pair almost always reads "own". It reaches a cell only after the centre captured it.
- So the front pair (0, 1) is the only pair that sees a cell's color before capture.
- Rule: the controller watches the front pair. When the front class changes, that is the class of the cell ahead.
- The controller stores that class with the next cell id (from the positioning sensor) in its private map.
- hw5 uses the back pair to ask "fully inside the nest" (`search_deliver.cpp:229-232`). That is a different question.
- The window is short: about 6 cm of travel, about 0.6 s at 10 cm/s. Readings at 10 ticks/s catch it.

Self-computed capture signal (used by A2 and as the B and C reward):

1. The positioning sensor gives the current cell id each tick.
2. When the cell id changes, the last front-pair class before the change is the cell's old owner.
3. Old owner free means "capture". Old owner enemy means "steal". Old owner own means "wasted move".
4. No loop-function data is used. So training and play see the same inputs (§2.4).

### 2.3 Team identity, position, and communication

| Need | Mechanism | Evidence |
| --- | --- | --- |
| Team identity | Each team has its own `<controller>` config with `<team id="0"/>` in `<params>` | hw5 shows the `<params>` pattern (`search_deliver1.argos:39-58`) |
| Identity fallback and cross-check | Robot id prefix `t0_` / `t1_`, set in `<foot-bot id="t0_">` of each `<distribute>` | hw5 uses `id="fb"` the same way (line 126) |
| Loop functions find a robot's team | Parse the entity id prefix | No link to the controller library needed |
| Own position | `positioning` sensor, `implementation="default"`. `SReading { CVector3 Position; CQuaternion Orientation; }` | `ci_positioning_sensor.h:23-25`. hw5's `.argos` does NOT have it. Our `.argos` adds it |
| Talk to neighbours | range-and-bearing sensor and actuator. `SPacket { Real Range; CRadians HorizontalBearing; CByteArray Data; }` | `ci_range_and_bearing_sensor.h:28-39`, hw5 lines 134-135 |
| Packet size and range | Foot-bot constructor defaults: range 3.0 m, data 10 bytes | `footbot_entity.h:46-47`. The XML attribute names are NOT verified |
| Show team | LEDs actuator (team color) and a Qt marker | hw5 uses `leds` (line 30) and `DrawCylinder` |

- The controller checks in `Init` that `<team id>` matches the id prefix. A mismatch throws.
- Range-and-bearing has no team channel. Every robot in range hears every packet.

### 2.4 What a controller may know (fairness contract)

| Allowed | Not allowed |
| --- | --- |
| Own 4 ground readings | Reading the loop functions' grid |
| Own pose from the positioning sensor | Other robots' poses except via range-and-bearing |
| Own private map of cells it has seen | Global score during the match |
| Teammates' range-and-bearing packets | Acting on enemy packet contents (see Q3) |

- Why: the game should test local sensing and swarm rules, not a global planner.
- Q-learning in §5 uses the same inputs. A global "oracle" input is open question Q4.

## 3. Schema (the contract)

This section is the single contract for MVP1 to MVP3 (`.claude/CLAUDE.md` "System build phasing").

### 3.1 Arena and grid

Table 4. Arena and grid values

| Item | Value | Note |
| --- | --- | --- |
| Arena size | 5, 5, 2 m | Same as hw5 |
| Walls | inner faces at x, y = ±2.00 m | Wall centres at ±2.05, size 4.2 × 0.1 × 0.5 |
| Grid area | x, y in [-2.0, 2.0) | Cells fully inside the walls |
| Cell size | 0.20 m | `cell_size` param |
| Grid | 20 × 20 = 400 cells | Derived |
| Pixels per cell | 10 | `pixels_per_meter="50"` |
| Cell index | `ix = floor((x + 2.0) / 0.2)`, `iy = floor((y + 2.0) / 0.2)`, `id = iy * 20 + ix` | Out of range: no cell |
| Ticks per second | 10 | As hw5 |
| Match length | 300 s = 3000 ticks | `length` in `<experiment>` |
| Team size | 5 per team | `quantity` in each `<distribute>` |
| Spawn | team 0 at x in [-1.9, -1.4], team 1 at x in [1.4, 1.9] | Mirrored strips |
| Robot top speed | 10 cm/s | hw5 `max_speed="10"` |

- Rough scale check: one robot covers at most 30 m = 150 cells per match. 10 robots can cover the 400 cells. So contest happens.

### 3.2 Ownership state (loop functions)

```
struct Cell {
  int8_t  owner;          // -1 free, 0..T-1 team
  uint32_t last_change;   // tick of last owner change
  uint16_t flips;         // owner changes (free->team counts)
};
std::vector<Cell> grid;   // size 400, index = id
std::array<uint32_t, T> owned;   // cells per team, kept in sync
```

- Invariant: `free + sum(owned) == 400` every tick. MVP1 check M1-C2.
- Pure logic lives in `territory_grid.{h,cpp}`: index, capture, counts. It has no simulator calls.
- Why: a functional core is easy to read and to check by deliberate breakage.

### 3.3 Capture rule

Default rule R0 "last visit":

1. In `PostStep`, map each robot centre to a cell.
2. If robots of only one team are in that cell this tick, the cell takes that team.
3. If two teams are in the same cell this tick, the cell does not change.
4. Count a change as "capture" (from free) or "steal" (from the enemy).
5. If any cell changed, call `SetChanged()` once.

Alternatives (owner pick, Q1):

| Rule | Change | Effect |
| --- | --- | --- |
| R1 dwell | A cell flips after `dwell_ticks` in a row (e.g. 10 = 1 s) | Fewer drive-by steals, slower game |
| R2 lock | A cell is locked for `lock_ticks` after a flip | Rewards defending |
| R3 free only | Only free cells can be taken | Pure exploration race, no conflict |

### 3.4 Experiment parameters in the `.argos` file

```xml
<framework>
  <system threads="0" />
  <experiment length="300" ticks_per_second="10" random_seed="123" />
</framework>

<loop_functions library="build/loop_functions/territory_loop_functions/libterritory_loop_functions"
                label="territory_loop_functions">
  <territory cell_size="0.2" grid_min="-2,-2" grid_max="2,2"
             num_teams="2" capture_rule="last_visit" dwell_ticks="1"
             runs_root="../runs" tag="rw_vs_rw" log_robots_every="10" />
</loop_functions>
```

- Working directory: the owner runs `argos3 -c experiments/<file>.argos` from `project_final/src`. The `build/...` library paths need it.
- So `runs_root="../runs"` resolves to `project_final/runs/`.
- In `Init`, the loop functions build the run folder name and create it with `std::filesystem::create_directories`.
- Why: `std::ofstream` does not create folders. A missing folder fails without an error.
- If the folder cannot be created, `Init` throws.

- `threads="0"` keeps one thread. Why: a team Q-table (option B, C) is shared in one process.
- Two controller configs, one per team: `t0_ctrl` and `t1_ctrl`, each with `<team id="k"/>`.
- Sensors in both configs: `footbot_proximity`, `footbot_motor_ground` (`rot_z_only`), `positioning`, `range_and_bearing`.
- Actuators: `differential_steering`, `leds`, `range_and_bearing`.
- Two files share all values except `<visualization>`: `territory_qt.argos` (has it), `territory_headless.argos` (no block).
- ARGoS has no seed flag on the command line (not verified). A script writes one `.argos` per seed from the headless file. The owner runs it.

### 3.5 Log files (one run = one folder, `rules/measurement.md` §2)

Folder: `runs/<YYYYMMDD-HHMMSS>_<tag>_s<seed>/`, e.g. `runs/20261118-142301_rw_vs_rw_s123/`.

- The time stamp makes the run id never reused. A rerun gets a new folder.
- `<tag>` names the matchup. Cradle runs use `<JOB>_<RUN>` instead (skill §6).

Table 5. `ticks.csv`, one row per tick

| Column | Type | Meaning |
| --- | --- | --- |
| `tick` | int | Simulation clock |
| `free` | int | Free cells |
| `owned_t0`, `owned_t1` | int | Cells owned per team |
| `share_t0`, `share_t1` | float | owned / 400 |
| `captures_t0`, `captures_t1` | int | Cumulative free-to-team flips |
| `steals_t0`, `steals_t1` | int | Cumulative enemy-to-team flips |
| `contested` | int | Cells with both teams this tick |

Table 6. Other files

| File | Rows | Columns |
| --- | --- | --- |
| `cells_final.csv` | 400, at `PostExperiment` | `cell_id, ix, iy, owner, last_change, flips` |
| `robots.csv` | every `log_robots_every` ticks, per robot | `tick, robot_id, team, x, y, yaw_deg, cell_id, ground_mean` |
| `manifest.json` | 1 | `code_version`, `code_sha`, `params` (all `.argos` values, seed), `env` (machine, ARGoS version), `metrics` (final share per team, winner) |

- Per-tick CSV keeps scores only. Cell-level and robot-level outputs are separate (`rules/measurement.md` §3).
- `Reset()` clears the grid, zeroes counters, and reopens all files (hw5 does the same, lines 65-81).
- `manifest.json` follows `rules/measurement.md` §2.1.
- `ground_mean` needs the controller value. The loop functions read it through a small getter, or the column stays empty in MVP1 (Q6).
- Each controller can also write its own `ground_<robot_id>.csv` (`tick, r0, r1, r2, r3, front_class, cell_id`). MVP1 check M1-C1 uses this file.

### 3.6 Controller-facing contract

- Range-and-bearing packet, 10 bytes:

| Byte | Content |
| --- | --- |
| 0 | team id |
| 1 | message type (0 none, 1 "my target cell", 2 "cell seen") |
| 2-3 | cell id, uint16 |
| 4 | cell owner as seen (-1, 0, 1 stored as 255, 0, 1) |
| 5-9 | reserved, 0 |

- Ground classification: Table 3 bands, one function `ClassifyGround(Real) -> {FREE, TEAM0, TEAM1}`.
- Motion: copy hw5's `SetWheelSpeedsFromVector` and `DiffusionVector` (`search_deliver.h:262-268`).

## 4. Directory layout

```
project_final/
├── DESIGN.md
├── research/lu_qi.md                  (researcher's note)
├── src/                               (mirrors hw5_ARGoS_02/src)
│   ├── CMakeLists.txt                 copy of hw5, project name changed
│   ├── controllers/
│   │   ├── CMakeLists.txt
│   │   ├── territory_common/          team id, ground bands, packet codec, motion (copied hw5 helpers)
│   │   ├── territory_random_walk/     MVP1 baseline A0
│   │   ├── territory_swarm/           A1-A3, one controller, behavior by param (after pick)
│   │   └── territory_qlearn/          B or C (after pick)
│   ├── loop_functions/
│   │   ├── CMakeLists.txt
│   │   └── territory_loop_functions/
│   │       ├── territory_grid.{h,cpp}            pure grid logic
│   │       ├── territory_loop_functions.{h,cpp}  ARGoS hooks, logging
│   │       └── territory_qt_user_functions.{h,cpp}  behind ARGOS_QTOPENGL_FOUND
│   └── experiments/
│       ├── territory_qt.argos
│       ├── territory_headless.argos
│       └── make_seeds.sh              writes one .argos per seed
├── analysis/                          plots from saved CSV only
├── cluster/                           B or C only: Cradle build and job scripts
└── runs/                              outputs, one folder per run
```

- Reused hw5 code is COPIED here. Files under `hw*/` are never edited (`.claude/rules/homework.md`).
- Copied items: the top `CMakeLists.txt`, the loop-functions skeleton, the Qt registration, the controller motion helpers and their XML params.
- The loop functions do not link the controller library. hw5 does (`CMakeLists.txt` line 13), because it casts to the controller.
- If `ground_mean` needs the controller (Q6), only the Qt and logging file link it.

## 5. Strategy options (owner picks)

All options share MVP1 (§6). They differ after it.

- Effort is in person-days. One person-day is about 4 focused hours. All are estimates, not measurements.
- Capacity estimate: 4 people × 10 working days ≈ 40 person-days. Usable for code: about 24 person-days.
- The rest goes to course load, slides, the video and rehearsal.
- MVP1 estimate: about 6 person-days (grid and loop functions 3, `.argos` and Qt 1.5, A0 and checks 1.5).
- So about 18 person-days remain after MVP1.

### 5.1 Option A: rule-based swarm teams (stable)

| Variant | Rule |
| --- | --- |
| A0 random walk | Straight, random turn on a timer or obstacle (MVP1 baseline) |
| A1 dispersion | Steer away from teammates heard on range-and-bearing |
| A2 color stigmergy | Keep straight while the front pair sees non-own cells ahead. Turn when it sees own color ahead (§2.2) |
| A3 frontier | Private map plus teammates' "cell seen" packets. Head to the nearest non-own cell not claimed by a teammate |

- Measured comparison: round-robin of A0 to A3. Final share, 20 seeds × 2 sides per pair.
- Cost (person-days): A1 2, A2 1, A3 4, runs and analysis 3. Total about 10 after MVP1.
- Risk: low. All runs are local sims by the owner. No learning.
- Weakness: no learning story, if the course expects one.

### 5.2 Option B: tabular Q-learning self-play (scalable)

- No deep learning. One Q-table per team, shared by its robots.
- State (about 120): last front-pair class ahead (3) × nearest-teammate sector (4 + none) × obstacle ahead (2) × private-map direction to most non-own cells (4).
- Actions (4): forward, turn left 45°, turn right 45°, turn back. One decision every 1 s.
- Reward: +1 capture, +2 steal, -0.05 per wasted move. Source: the self-computed capture signal (§2.2), not the loop functions.
- Episode mechanics: one `argos3` process per episode. `Init` loads the table. `Destroy` saves it. Seed = base seed + episode number.
- Why one process per episode: an in-process reset from inside loop functions is not a documented path.
- Measured comparison: learning curve (share per episode), then frozen policy vs A0 over 20 seeds × 2 sides.
- Cost (person-days): state and reward 3, table I/O and episode loop 3, Cradle build 2-4, job scripts 1, tuning 3, evaluation 3. Total about 15-17 after MVP1.
- Risk: high. It may not beat A0 in 2 weeks. The Cradle build may fail (§5.4).

### 5.3 Option C: hybrid, learned behavior selector (cutting-edge)

- The learner picks one of A0, A1, A2 as a macro-action every 2 s. It does not steer wheels.
- State (about 24): last front-pair class ahead (3) × teammates near (2) × share of wasted moves over the last 10 s (4).
- Reward: the same self-computed capture signal as B (§2.2).
- Matchups: learned team vs best fixed swarm team. This is "swarm vs RL".
- Measured comparison: learned selector vs each fixed A variant, 20 seeds × 2 sides. Answers RQ1 directly.
- Cost (person-days): A1 and A2 first 3, selector and table I/O 5, Cradle build 2-4, jobs 1, evaluation 3. Total about 14-16 after MVP1.
- Risk: medium-high. Smaller table learns faster than B. It still needs the Cradle build.

### 5.4 Training path for B and C (Cradle, owner decision 2026-11-10)

```
Figure 3. Training path

 Mac (owner)                           Cradle (main session submits)
 territory_headless.argos  --rsync-->  code/ + jobs/train.slurm
 project_final/cluster/*.sh            build ARGoS beta59 in $HOME (once)
                                       episodes 1..E, one argos3 per episode
                                       runs/<JOB>_<RUN>/qtable_t0.csv
                                                         episodes.csv
 runs/<JOB>_<RUN>/  <--fetch_runs.sh-- (tar over ssh, skill §10)
 copy qtable into experiments/qtables/
 owner runs frozen-policy matches in Qt and headless
```

- Caption: Figure 3 shows where each step runs. Why: agents write scripts, only the main session submits and fetches.
- Skill: `.claude/skills/cradle-cluster/SKILL.md` §5-§11.
- ARGoS on Cradle: source build of tag 3.0.0-beta59 into `$HOME/argos3`. No `sudo`, `dnf` or `apt` (skill §2).
- Build flags: simulator only, Qt off. Our CMake keeps the `ARGOS_QTOPENGL_FOUND` guard, so it builds without Qt.
- OS: Rocky Linux 8.6, glibc 2.28 (skill §3). A `module` system exists. Its cmake and gcc versions are not known.
- Dependencies to check: cmake, a C++17 compiler, Lua (ARGoS may require it), FreeImage (optional). Not verified.
- Q-table file: `qtable_t<k>.csv`, columns `state_id, action_id, q, visits`. Written at every episode end.
- Checkpoint: the table file is the checkpoint. A killed job resumes from it. `kimq` limit is 12 h.
- `episodes.csv`: `episode, seed, epsilon, share_t0, share_t1, reward_t0, reward_t1`.
- Seeds in a batch: one seed per array task (skill §9). Parallel self-play needs a merge rule (Q7).
- Fetch-back: skill §10 `fetch_runs.sh` into `project_final/runs/<JOB>_<RUN>/`. Then one ledger line.
- Training speed (episodes per hour) is not known. It must come from a cluster run, not a local one.

Table 7. Options side by side

| | A swarm rules | B tabular Q self-play | C learned selector |
| --- | --- | --- | --- |
| Effort after MVP1 (person-days, estimate) | about 10 | about 15-17 | about 14-16 |
| Against about 18 person-days left | 8 spare | 1-3 spare | 2-4 spare |
| Main risk | Weak "learning" story | May not learn in time. Cradle build | Cradle build |
| Training | None | Cradle | Cradle |
| Presentation result | Strategy ranking, share vs time | Learning curve, learned vs A0 | Swarm vs learned share |
| Serves | G1, G2 | G1, G2, RQ1 | G1, G2, RQ1 |
| Fit with the instructor's interests (`research/lu_qi.md` §1.2) | Strong: swarm robotics and stigmergy in ARGoS are his stated core. A spiral-sweep variant could cite his 2023 spiral search | Medium: his reinforcement learning paper (2021) is listed on Scholar only, and it is deep multi-agent learning, not tabular | Medium-strong: swarm rules stay central, learning is a small add-on |

### 5.5 Measurement plan (all options)

- Primary metric: final share of the tested team (owned cells / 400).
- Pairing: same seed, then sides swapped. Why: spawn side may bias the result.
- Noise first: A0 vs A0 over 20 seeds × 2 sides. Its spread sets the decision line (`rules/measurement.md` §1).
- Criteria are written before the runs. Win = 95% bootstrap interval of the paired difference above 0.
- Secondary columns, table only: time to 50% coverage, steals per minute.

## 6. MVP ladder (`.claude/CLAUDE.md` "System build phasing")

| Phase | What is real | What is mock |
| --- | --- | --- |
| MVP1 | Arena, grid, capture rule R0, scores, 3 log files, Qt and headless `.argos` | Strategy: A0 random walk stands in for every team strategy |
| MVP2 | 1-2 strategy tasks after the pick (below) | Other strategies stay A0 |
| MVP3 | The picked strategy's full matchup set | A0 stays as the baseline |

- No backend is needed. So the loop functions are real from MVP1. Only the strategy is a stand-in.

MVP1 end-to-end cycle:

1. Owner builds `project_final/src` with cmake.
2. Owner runs `territory_qt.argos`. Two colors spread on the floor.
3. Owner runs `territory_headless.argos`, one seed. Three CSV files and `manifest.json` appear.
4. Analysis script draws share vs time from `ticks.csv`.
5. One summary page links each stage report.

MVP1 exit checks (pm turns these into AC):

| ID | Check |
| --- | --- |
| M1-C1 | `ground_<robot_id>.csv` holds readings on each color. Each lies within ±0.05 of Table 3 |
| M1-C2 | `free + owned_t0 + owned_t1 == 400` on every row of `ticks.csv` |
| M1-C3 | Same seed twice, headless: identical `ticks.csv` |
| M1-C4 | Qt and headless, same seed: identical `ticks.csv` |
| M1-C5 | Reset from the Qt window clears floor and counters |
| M1-C6 | Noise run done: A0 vs A0, 20 seeds × 2 sides. Spread of `share_t0` recorded in the ledger |
| M1-C7 | Over one Qt run, the front-pair class at a border matches the cell's owner in `robots.csv` |

MVP2, first real slice per option:

| Option | MVP2 tasks |
| --- | --- |
| A | A2 color stigmergy, then A1 dispersion |
| B | Q-table load and save, plus one short Cradle job whose table plays in Qt |
| C | Selector with a hand-set table, plus one short Cradle job |

## 7. Work split (4 members, module owners)

| Slot | Owns | MVP1 deliverable | After the pick |
| --- | --- | --- | --- |
| Member 1 | `territory_grid`, `territory_loop_functions` (schema owner) | Grid, capture, logs | Capture rule variants, tournament script |
| Member 2 | `experiments/*.argos`, `make_seeds.sh`, Qt user functions, `analysis/` | Two `.argos` files, share plot | Results figures, demo video |
| Member 3 | `territory_common`, `territory_random_walk` | A0, M1-C1 check | A or C swarm variants |
| Member 4 | `territory_qlearn` or `territory_swarm`, `cluster/` | Packet codec, ground bands | B/C learner and Cradle scripts, or A3 |

- The owner assigns names to slots. Phasing and dates belong to `product-manager`.
- Member 1 changes the schema only through this document. Why: the schema is the one contract.

## 8. Open questions for the owner

| # | Question | Default if no answer |
| --- | --- | --- |
| Q1 | Capture rule: R0 last visit, R1 dwell, R2 lock, or R3 free only? | R0 |
| Q2 | Grid 20 × 20 at 0.20 m, 5 robots per team, 300 s: acceptable? | Yes |
| Q3 | May a team use enemy range-and-bearing packets? | No |
| Q4 | May a learner (B or C) read the global grid as input? | No (§2.4) |
| Q5 | More than 2 teams? The grey scale fits about 3 | 2 teams |
| Q6 | May loop functions link the controller library for `ground_mean`? | Column empty in MVP1 |
| Q7 | B/C parallel seeds: merge Q-tables, or one sequential chain per job? | One chain per job |
| Q8 | Cradle: is a CPU-only job allowed? The skill's template asks for a GPU, and ARGoS needs none | Ask before the first job |
| Q9 | Cradle: do `module` cmake, gcc and Lua cover an ARGoS beta59 build in `$HOME`? | Main session checks with read-only `module avail` |
| Q10 | Where do the multi-seed evaluation matches run: owner's Mac by hand, or Cradle? | Owner's Mac by hand (root `CLAUDE.md` "Execution") |
| Q11 | Must the Cradle build match beta59 exactly? A different build makes the stack differ (`rules/measurement.md` §2.4) | Yes, same tag |
| Q12 | Does the course require a learning component? This decides A vs B/C | Unknown |
| Q13 | `research/lu_qi.md` §3.0 ranks this game 5th of 8 ideas (score 12). It ranks pheromone foraging under misleading trails 1st (score 27). Keep the territory game? | Keep it, as the owner asked |

## 9. Design units for `product-manager`

Sizes are estimates in person-days. Order is the dependency order.

| Unit | Depends on | Size | Phase |
| --- | --- | --- | --- |
| U1 `territory_grid` pure logic (index, capture R0, counts) | none | 1 | MVP1 |
| U2 loop functions: hooks, `GetFloorColor`, run folder, 3 CSV files, `manifest.json`, `Reset` | U1 | 2 | MVP1 |
| U3 `territory_common`: team id check, ground bands, front-pair tracker, packet codec, copied motion helpers | none | 1 | MVP1 |
| U4 A0 random-walk controller plus `ground_<robot_id>.csv` | U3 | 0.5 | MVP1 |
| U5 `territory_qt.argos`, `territory_headless.argos`, `make_seeds.sh`, Qt user functions | U2, U4 | 1.5 | MVP1 |
| U6 analysis script and summary page from saved CSV | U2 | 1 | MVP1 |
| U7 strategy slice 1-2 per Table in §6 "MVP2" | owner pick, MVP1 exit | 2-5 | MVP2 |
| U8 Cradle build and job scripts (B or C only) | owner pick | 3-5 | MVP2 |
| U9 tournament runs and result figures | U7 | 3 | MVP3 |

- U1 and U3 can start in parallel. U5 closes MVP1.
