# Baseline code map: Collision_Free_CPFA (pinned commit 9480f2e)

- Scope: the professor's Central-Place Foraging Algorithm (CPFA) code for Final Project 2.
- Simulator: Autonomous Robots Go Swarming (ARGoS) 3.0.0-beta59, installed under `/usr/local`.
- Method: code reading only. Nothing was built or run.
- Root of every relative path below: `02_informed_search/vendor/Collision_Free_CPFA/`.
- Short forms used in citations:
  - `ctrl.cpp` = `source/CPFA/CPFA_controller.cpp`
  - `ctrl.h` = `source/CPFA/CPFA_controller.h`
  - `lf.cpp` = `source/CPFA/CPFA_loop_functions.cpp`
  - `lf.h` = `source/CPFA/CPFA_loop_functions.h`
  - `base.cpp` = `source/Base/BaseController.cpp`
  - `xml10` = `experiments/Random_CPFA_r24_tag256_10by10.xml`
- Source-ID tag: `BCM`. Code facts cite file:line. Web facts cite `[S-BCM-n]`.
- `inference` marks a value I derived from the code, not one the code prints.

## Key findings (read first)

1. No Extensible Markup Language (XML) file matches Table 1. The closest file is `xml10`. It needs 3 edits (section 4).
2. The "random location" is a point on one of the 4 walls, not a uniform point (`ctrl.cpp:578-605`).
3. A robot uses that point only when it has no site fidelity and the pheromone list is empty (`ctrl.cpp:526-544`, `ctrl.cpp:778`).
4. Each collected resource respawns at a uniform random point (`ctrl.cpp:631-639`). The arena always holds 256 resources.
5. The XML nest radius is scaled by `sqrt(log2(arena width))` (`lf.cpp:104-111`). XML `0.5` gives about `0.911 m` (inference).
6. Local CMake is 4.4. The vendor `cmake_minimum_required(VERSION 2.8.12)` is a configure error on CMake 4.x `[S-BCM-3]`.
7. No grid, occupancy or visited-location code exists (grep `grid|occup|visited` in `source/Base`, `source/CPFA`).

## 1. State machine

### 1.1 Diagram

```
                 Init: SetTarget(own position)  ctrl.cpp:50
                                |
                                v
        +--------------------- DEPARTING  ctrl.cpp:255-316 -----------------+
        | uninformed: every 5 s, p = ProbabilityOfSwitchingToSearching       |
        |   -> SEARCHING (ctrl.cpp:272-289)                                  |
        | uninformed and target reached -> new wall point (ctrl.cpp:290-291) |
        | informed and target reached -> SEARCHING (ctrl.cpp:297-313)        |
        +----------------------------------+---------------------------------+
                                           v
        +--------------------- SEARCHING  ctrl.cpp:318-444 -----------------+
        | food within 0.13 m -> SURVEYING (ctrl.cpp:623-626)                 |
        | at target, every 5 s, p = ProbabilityOfReturningToNest             |
        |   -> give up -> RETURNING (ctrl.cpp:334-356)                       |
        +--------------+-----------------------------------+-----------------+
                       v                                   |
        SURVEYING  ctrl.cpp:448-476                        |
        (4 quarter turns, then RETURNING ctrl.cpp:467-475) |
                       |                                   |
                       v                                   v
        +--------------------- RETURNING  ctrl.cpp:484-576 -----------------+
        | in nest: drop food, maybe lay pheromone, choose next target:       |
        |   1 site fidelity   (ctrl.cpp:526-531)                             |
        |   2 pheromone       (ctrl.cpp:533-537)                             |
        |   3 wall point      (ctrl.cpp:539-544)                             |
        |   -> DEPARTING (ctrl.cpp:547)                                      |
        +--------------------------------------------------------------------+
```

### 1.2 States and transitions

| State | Code | Transition | Where |
| --- | --- | --- | --- |
| `DEPARTING` (0) | `ctrl.h:74-79`, `ctrl.cpp:255-316` | Uninformed robot switches to `SEARCHING` | `ctrl.cpp:270-289` |
| `DEPARTING` | same | Uninformed robot reaches its wall point, picks a new one | `ctrl.cpp:290-291` |
| `DEPARTING` | same | Informed robot reaches its target, starts `SEARCHING` | `ctrl.cpp:297-313` |
| `SEARCHING` (1) | `ctrl.cpp:318-444` | Robot finds food, goes to `SURVEYING` | `ctrl.cpp:622-641` |
| `SEARCHING` | same | Robot gives up, goes to `RETURNING` | `ctrl.cpp:334-356` |
| `SURVEYING` (3) | `ctrl.cpp:448-476` | After 5 headings (`survey_count` 0 to 4), goes to `RETURNING` | `ctrl.cpp:450-475` |
| `RETURNING` (2) | `ctrl.cpp:484-576` | Robot enters nest, goes to `DEPARTING` | `ctrl.cpp:489-551` |

- The dispatcher `CPFA()` calls each state function (`ctrl.cpp:147-176`).
- `Searching()` runs only on half-second ticks (`ctrl.cpp:160`).
- `ControlStep()` runs every tick (`ctrl.cpp:57-110`). It calls `CPFA()` then `Move()` (`ctrl.cpp:108-109`).

### 1.3 Where the "random location" target is picked

`SetRandomSearchLocation()` (`ctrl.cpp:578-605`):

- It picks one of 4 walls with probability 0.25 each (`ctrl.cpp:579-601`).
- It picks a uniform coordinate along that wall (`ctrl.cpp:584`, `589`, `595`, `600`).
- Wall edges are `ForageRangeX`, `ForageRangeY` = half arena minus 0.085 m (`base.cpp:31-36`, `lf.cpp:96-100`).
- It sets `SetIsHeadingToNest(true)`, so no destination noise applies (`ctrl.cpp:603`, `base.cpp:98-110`).

Three call paths reach it:

| Path | Where | When |
| --- | --- | --- |
| First departure | `ctrl.cpp:50` sets target = own position, then `ctrl.cpp:290-291` | Simulation start |
| After a nest visit | `ctrl.cpp:539-544` | No site fidelity chosen, and `SetTargetPheromone()` returned false |
| Wall point reached while still departing | `ctrl.cpp:290-291` | Uninformed robot did not switch to search yet |

When `SetTargetPheromone()` returns false (`ctrl.cpp:774-817`):

- It returns false at once when `PheromoneList` is empty (`ctrl.cpp:778`).
- With a non-empty list it walks all entries until `randomWeight < weight` (`ctrl.cpp:795-808`).
- `randomWeight` is drawn in `[0, sum of active weights)` (`ctrl.cpp:785-792`).
- So with any active pheromone it almost always returns true (inference).
- Result: the wall-point branch runs only when the pheromone list is empty (inference).

### 1.4 The wall point is a direction, not a destination

- An uninformed departing robot tests a switch every 5 s (`ctrl.cpp:270-272`).
- Switch probability = `ProbabilityOfSwitchingToSearching` = `0.723128706375` in `xml10` (`xml10:42`).
- Chance of still departing after k tests = `0.277^k` (inference).
- Speed = 16 cm/s (`xml10:32`, `base.cpp:206`). One 5 s period = 0.8 m at most (inference).
- The first test comes 0 to 5 s after departure (inference).
- Expected tests until a switch = 1 / 0.723 = 1.38 (inference).
- So most uninformed robots switch within about 1 to 2 m of the start point (inference).
- The wall is about 4.9 m from the nest (`base.cpp:33-36`). Few robots reach it (inference).
- Impact for our method: a new target alone will not be reached. We also need to change `ctrl.cpp:270-292` (see section 8).

### 1.5 Uninformed walk and give-up

Uninformed walk (`ctrl.cpp:358-388`):

- Turn angle = `Gaussian(UninformedSearchVariation)` added to current heading (`ctrl.cpp:358-367`).
- Step length = `SearchStepSize` = 0.08 m (`xml10:32`, `ctrl.cpp:367`).
- `UninformedSearchVariation` is read in degrees and stored in radians (`lf.cpp:54`, `lf.cpp:61`).

Informed walk (`ctrl.cpp:390-429`):

- Turn spread decays with search time: `w + (2π − w) · exp(−λ · t)` (`ctrl.cpp:822-832`).
- `λ` = `RateOfInformedSearchDecay` (`ctrl.cpp:398`).

Give-up (`ctrl.cpp:332-356`):

- Test runs when the robot is at its step target and the tick is a 5 s multiple (`ctrl.cpp:332-334`).
- Probability = `ProbabilityOfReturningToNest` = `0.0147598869881` in `xml10` (`xml10:42`).
- The robot clears its fidelity and heads to the nest (`ctrl.cpp:336-344`).
- `SetFidelityList()` sets the site to (10000, 10000) (`ctrl.cpp:765`). It cannot become a target:
  - Give-up sets `updateFidelity = false` right after (`ctrl.cpp:343`).
  - Pickup overwrites the site with the robot position (`ctrl.cpp:713`).
  - Only `updateFidelity == true` reaches the fidelity target (`ctrl.cpp:526-529`).
- The "at target" test compares a squared distance to an unsquared tolerance (`ctrl.cpp:332`). The real radius is `sqrt(0.05)` = 0.224 m (inference). This looks like an upstream quirk. Do not fix it in the baseline arm.

### 1.6 Nest decision (Poisson rule)

At the nest (`ctrl.cpp:489-551`):

1. Compute `poissonCDF_pLayRate` and `poissonCDF_sFollowRate` from `ResourceDensity` (`ctrl.cpp:492-493`, `ctrl.cpp:877-887`).
2. If holding food: drop it and count it (`ctrl.cpp:496-508`).
3. Lay a pheromone if `pLayRate > r1` and `updateFidelity` (`ctrl.cpp:509-515`).
4. Go back to the fidelity site if `updateFidelity` and `sFollowRate > r2` (`ctrl.cpp:526-531`).
5. Else follow a pheromone if one exists (`ctrl.cpp:533-537`).
6. Else pick a wall point (`ctrl.cpp:539-544`).

## 2. Central server (pheromone list)

The loop functions object is the central server. Controllers hold a pointer to it.

| Item | Type and container | Owner | Where |
| --- | --- | --- | --- |
| Pheromone waypoint list | `std::vector<Pheromone> PheromoneList` | `CPFA_loop_functions` | `lf.h:120` |
| Site fidelity map (drawing only) | `map<string, CVector2> FidelityList` | `CPFA_loop_functions` | `lf.h:119` |
| Resource list | `std::vector<CVector2> FoodList` | `CPFA_loop_functions` | `lf.h:116` |
| Controller access | `friend class CPFA_controller` | `CPFA_loop_functions` | `lf.h:18` |
| Pointer hand-off | `SetLoopFunctions(this)` per foot-bot | `CPFA_loop_functions::Init` | `lf.cpp:114-124` |

`Pheromone` class (`source/Base/Pheromone.h:10-39`, `source/Base/Pheromone.cpp`):

- Fields: `location`, `trail`, `lastUpdated`, `decayRate`, `weight`, `threshold`, `ResourceDensity`.
- New pheromone: `weight` = 1.0, `threshold` = 0.001 (`Pheromone.cpp:26-27`).
- Decay: `weight *= exp(−decayRate · (t − lastUpdated))` (`Pheromone.cpp:34-38`).
- Active when `weight > threshold` (`Pheromone.cpp:80-82`).

Lifecycle:

| Step | Who | Where |
| --- | --- | --- |
| Create | Controller at the nest, after a food drop | `ctrl.cpp:509-515` |
| Location stored | `SiteFidelityPosition` = robot position at pickup | `ctrl.cpp:713` |
| Decay and remove inactive | `UpdatePheromoneList()` every 0.5 s | `lf.cpp:312-333`, called from `lf.cpp:180` |
| Choose | `SetTargetPheromone()`, weighted random by `weight` | `ctrl.cpp:774-817` |
| Clear | When `FoodList` is empty, and on `Reset()` | `lf.cpp:188-192`, `lf.cpp:151` |

- Selection is a linear scan over the whole list (`ctrl.cpp:785-808`). There is no spatial index.
- `Nest` class (`source/Base/Nest.h`) holds its own `PheromoneList`. CPFA code never uses it (grep `Nest` in `source/CPFA`). It is a leftover from the Multiple-Place Foraging Algorithm (MPFA).

## 3. Robot position access and sensing range

### 3.1 Own position

- Sensor: `CCI_PositioningSensor` named `"positioning"` (`ctrl.cpp:27`, `xml10:25`).
- `GetPosition()` returns the sensor x, y (`base.cpp:55-77`).
- Position noise code is commented out (`base.cpp:65-74`). `PositionNoiseStdev` = 0 (`xml10:32`).
- Heading comes from the same sensor's quaternion (`base.cpp:41-53`).

### 3.2 How often a robot could log a point

- `ControlStep()` runs every tick. `ticks_per_second` = 32 (`xml10:8`).
- `ControlStep()` already logs a ray per tick into `LoopFunctions->TargetRayList` (`ctrl.cpp:98-105`). This is the only existing position log. It grows without bound and is cleared only on reset or empty food list (`lf.cpp:153`, `lf.cpp:191`).
- `myTrail` per robot also grows every tick (`ctrl.cpp:101`). It is never read.
- Distance per half second = 16 cm/s · 0.5 s = 0.08 m (inference).

### 3.3 Sensing range for resources

- Resource check runs only in `SEARCHING`, every 0.5 s (`ctrl.cpp:321-323`).
- No sensor is used. The robot scans the global `FoodList` by distance (`ctrl.cpp:622-623`).
- Pickup radius = `FoodDistanceTolerance` = 0.13 m (`xml10:32`). `Init` squares it (`ctrl.cpp:47`).
- Density count radius: squared distance `< SearchRadiusSquared · 2` (`ctrl.cpp:705`).
- `SearchRadiusSquared` = `(4 · 0.05)^2` = 0.04 (`lf.cpp:41`). Radius = `sqrt(0.08)` = 0.283 m (inference).
- Impact: points logged in `DEPARTING` or `RETURNING` were travelled but not sensed (inference).

## 4. Experiment config (Table 1)

### 4.1 Closest file and the gap

No file matches Table 1. Closest: `xml10` (24 robots, 256 resources, 10 m by 10 m).

| Table 1 item | Table 1 | `xml10` value | Where | Edit needed |
| --- | --- | --- | --- | --- |
| Arena | 10 m · 10 m | `size="10.0, 10.0, 1"` | `xml10:55` | none |
| Nest radius | 0.25 m | `NestRadius="0.5"`, scaled at run time | `xml10:47`, `lf.cpp:104-111` | yes, see 4.3 |
| Resources | 256 | `FoodItemCount="256"` | `xml10:45` | none |
| Distribution | Random, Powerlaw, Clustered | `FoodDistribution="0"` (Random) | `xml10:45` | 1 file per distribution |
| Robots | 24 | 4 groups · `quantity="6"` | `xml10:84,94,104,114` | none |
| Foraging time | 12 min = 720 s | `MaxSimTimeInSeconds="1800"` | `xml10:46` | yes, set `720` |
| Runs | 50 | `MaxSimCounter="1"`, `random_seed="0"` | `xml10:46`, `xml10:8` | set 50 explicit seeds |

- `experiments/parameters_10by10_setting.txt:1-10` names a 16-robot file and the same 1800 s, 0.5 radius.
- `ga.py:680-683` defaults to 24 robots, 256 tags and `length = 720`. This suggests the course setup came from the Genetic Algorithm (GA) script (inference).

### 4.2 Every parameter in `xml10`

Framework (`xml10:6-9`):

| Parameter | Value |
| --- | --- |
| `threads` | 0 |
| `length` (s) | 6000 |
| `random_seed` | 0 |
| `ticks_per_second` | 32 |

Controller settings (`xml10:32`):

| Parameter | Value |
| --- | --- |
| `DestinationNoiseStdev` | 0.0 |
| `FoodDistanceTolerance` (m) | 0.13 |
| `NestAngleTolerance` | 0.1 |
| `NestDistanceTolerance` (m) | 0.05 |
| `PositionNoiseStdev` | 0.00 |
| `ResultsDirectoryPath` | `results/` (read, unused: `ctrl.cpp:40`, `ctrl.cpp:200-212`) |
| `RobotForwardSpeed` (cm/s) | 16.0 |
| `RobotRotationSpeed` | 8.0 |
| `SearchStepSize` (m) | 0.08 |
| `TargetAngleTolerance` | 0.1 |
| `TargetDistanceTolerance` (m) | 0.05 |

Sensors and actuators (`xml10:17-28`): `differential_steering`, `leds`, `footbot_proximity`, `positioning`, `footbot_motor_ground` (`rot_z_only`, unused by code).

CPFA evolved parameters (`xml10:42`):

| Parameter | Value |
| --- | --- |
| `PrintFinalScore` | 1 |
| `ProbabilityOfReturningToNest` | 0.0147598869881 |
| `ProbabilityOfSwitchingToSearching` | 0.723128706375 |
| `RateOfInformedSearchDecay` | 0.205799848158 |
| `RateOfLayingPheromone` | 14.7027566005 |
| `RateOfPheromoneDecay` | 0.0245057227138 |
| `RateOfSiteFidelity` | 14.1514206414 |
| `UninformedSearchVariation` (degrees) | 2.81939731297 |

- These 7 values equal `evolved_parameters.txt:3-4` exactly.
- That file says they were evolved for a 5 m by 5 m arena, 64 random cubes, 2 robots (`evolved_parameters.txt:1-2`).
- So they were not evolved for Table 1.

Loop function settings (`xml10:44-48`):

| Parameter | Value |
| --- | --- |
| `ClusterWidthX`, `ClusterWidthY` | 8, 8 |
| `DrawDensityRate`, `DrawIDs` | 4, 1 |
| `DrawTargetRays`, `DrawTrails` | 0, 0 |
| `FoodDistribution` | 0 |
| `FoodItemCount` | 256 |
| `FoodRadius` (m) | 0.05 |
| `MaxSimCounter` | 1 |
| `MaxSimTimeInSeconds` | 1800 |
| `NestElevation` | 0.001 |
| `NestPosition` | 0,0 |
| `NestRadius` (m, before scaling) | 0.5 |
| `NumberOfClusters` | 4 |
| `OutputData` | 0 |
| `PowerlawFoodUnitCount` | 256 (read, unused by the generators) |
| `VariableFoodPlacement` | 0 |

Arena (`xml10:55-121`): 4 walls at ±5 m. Robots start in 4 grids of 2 by 3 at (±1, ±1) (`xml10:82`, `92`, `102`, `112`). Physics: `dynamics2d` id `dyn2d` (`xml10:127`). Visualization is commented out (`xml10:139-148`).

### 4.3 Nest radius scaling

- Code: `NestRadius *= sqrt(log(ArenaWidth)/log(2))` (`lf.cpp:110`).
- The quad-arena branch `abs(x) < -1` is never true (`lf.cpp:104`).
- `ArenaWidth` is a `size_t` (`lf.h:93`), so 10 m gives 10.
- Factor = `sqrt(log2(10))` = `sqrt(3.3219)` = 1.8226 (inference).

| XML `NestRadius` | Effective radius (inference) | Drop-off accept radius `r/2 − 0.05` (inference) |
| --- | --- | --- |
| 0.5 (current) | 0.911 m | 0.406 m |
| 0.25 | 0.456 m | 0.178 m |
| 0.137 | 0.25 m | 0.075 m |

- The run prints the effective value: `argos::LOG<<"NestRadius="` (`lf.cpp:112`).
- Drop-off loop: `placementPosition = nest + Gaussian(NestRadius/1.2, 0.5)` per axis (`ctrl.cpp:499-502`).
- ARGoS `Gaussian(f_std_dev, f_mean)` takes std dev first (`/usr/local/include/argos3/core/utility/math/rng.h:192`).
- So the mean offset is +0.5 m per axis, and the loop repeats until the point is inside `r/2 − 0.05` (inference).
- With a 0.25 m effective radius the accept area is small. The loop may spin many times per drop (inference).
- `ctrl.cpp:501` squares `r/2 − 0.05`. Only an effective radius of exactly 0.1 m never ends (inference).

### 4.4 Distribution switch

- `FoodDistribution`: 0 = Random, 1 = Clustered, 2 = Powerlaw (`lf.cpp:334-348`).
- The constructor default is 2 (`lf.cpp:21`). The XML value overrides it (`lf.cpp:74`).
- Output labels use the same mapping (`lf.cpp:234-236`).

### 4.5 Layout generators

Random (`lf.cpp:350-365`):

- 256 uniform points in the forage range. Rejects points near other food or the nest (`lf.cpp:358`, `lf.cpp:509-561`).

Clustered (`lf.cpp:368-409`):

- `NumberOfClusters` blocks of `ClusterWidthX · ClusterWidthY` items. Default 4 · 8 · 8 = 256.
- Item spacing = `3 · FoodRadius` = 0.15 m (`lf.cpp:370`).
- Each cluster corner is uniform and rejected if it overlaps (`lf.cpp:378-382`).
- It overwrites `FoodItemCount` (`lf.cpp:375`).
- It does not clear `FoodColoringList` (`lf.cpp:369`). Upstream quirk, harmless in headless runs (inference).

Powerlaw (`lf.cpp:412-507`), traced for 256 items (inference):

1. The loop finds `priorPowerRank` = 3, since `4^3 + 3 · 4^3` = 256 (`lf.cpp:438-442`).
2. `PowerRank` = 4 (`lf.cpp:445`).
3. 256 mod 4 = 0, so 64 items per rank (`lf.cpp:452-454`).
4. Cluster counts per rank: 1, 4, 16, 64 (`lf.cpp:462-465`).
5. Cluster sides per rank: 8, 4, 2, 1 (`lf.cpp:467-470`).
6. Result: 1 cluster of 64, 4 of 16, 16 of 4, 64 singles = 256.
- Placement stops after 200 failed tries with a log error, and places anyway (`lf.cpp:479-487`).

### 4.6 Resource respawn

- On every pickup, a new resource appears at a uniform random point (`ctrl.cpp:631-639`).
- `NumDistributedFood` grows by 1 each time (`ctrl.cpp:639`, `lf.cpp:617-619`).
- So the arena always holds 256 items. Clustered and Powerlaw layouts drift toward Random over a run (inference).
- The stop rule `score >= NumDistributedFood` can never fire (`lf.cpp:206-208`, inference).
- The run ends only at `MaxSimTime` (`lf.cpp:202`).
- `MaxSimTime` = seconds · 32 ticks (`lf.cpp:64-66`). For 720 s that is 23,040 ticks (inference).
- The vendored build cache names the project `random_drop_CPFA` (`build/CMakeCache.txt:506`). That fits this respawn behaviour.

## 5. Outputs and batch runs

### 5.1 What a run writes

| Output | Content | Where |
| --- | --- | --- |
| stdout line | `score, sim time (s), RandomSeed` | `lf.cpp:229` |
| `./results/<type>_CPFA_r24_tag256_10by10_quard_arena_0_iAntTagData.txt` | header, then `tags_collected, collisions_in_seconds, time_in_minutes, random_seed` | `lf.cpp:255`, `lf.cpp:286-295` |
| `./results/<same prefix>ForageData.txt` | collected per minute | `lf.cpp:297-301`, per-minute counter `lf.cpp:172-177` |
| Log | `NestRadius=`, `Number of robots=` | `lf.cpp:112`, `lf.cpp:118` |

- Files are written only when `PrintFinalScore == 1` (`lf.cpp:232`). `xml10` sets 1 (`xml10:42`).
- `score` = swarm total. `num_targets_collected` is one `static` counter shared by all controllers (`ctrl.h:13`, `ctrl.cpp:506-508`).
- `RandomSeed` is read in the constructor (`lf.cpp:12`).

Traps:

- The file name has no algorithm label (`lf.cpp:255`). Baseline and our method would append to one file.
- Files open in append mode (`lf.cpp:286`, `lf.cpp:297`).
- `./results/` is relative to the working directory. The full file listing of the clone shows no path under `results/`. A missing folder makes the `ofstream` fail silently (inference).
- The XML library paths are also relative: `build/source/CPFA/libCPFA_controller` (`xml10:16`, `xml10:39`). Run `argos3` from the vendor root.

### 5.2 Seeds

- `random_seed="0"` (`xml10:8`).
- ARGoS master reads seed 0 as "take it from the clock" `[S-BCM-4]`. It uses the microsecond field only.
- That source is master, not beta59 `[UNVERIFIED]`.
- Food layout uses the `"argos"` generator (`lf.cpp:4`). Robots use the same category (`ctrl.cpp:5`, `base.cpp:29`).
- So one seed fixes layout and behaviour together (inference).

### 5.3 Batch drivers

`experiments.py`:

- Python 2 syntax (`print file`, `experiments.py:20`, `25`). It fails under Python 3.
- It sets no seed. It calls `argos3 -n -c <xml>` 20 times (`experiments.py:18`, `28`).
- Its file list points to `03_10_19_constant_speed/`, which is not in `experiments/` (inference from the file listing).

`argos_util.py`:

- `set_seed(xml, seed)` writes `framework/experiment/@random_seed` (`argos_util.py:93-95`).
- `set_parameters` writes the CPFA attributes (`argos_util.py:83-91`).
- The macOS library names are stale `iAnt` paths (`argos_util.py:9-12`). They apply only with `system="darwin"`.

`ga.py` (Python 3):

- `run_argos_simulation` sets the seed, writes a temp XML in `experiments/`, runs `argos3 -n -c` (`ga.py:92-111`).
- It parses the last stdout line as `fitness, time, seed` (`ga.py:123-132`).
- Evaluation mode draws `num_trials` random seeds (`ga.py:592-616`). It runs the CSV parameters with `--eval-csv`, `--trials` (`ga.py:619-648`, `ga.py:671-674`).
- It returns only the mean. It does not save per-run values (`ga.py:613-616`).
- It runs in parallel with `os.cpu_count()` workers by default (`ga.py:668-669`). That breaks the one-core rule for local runs.

### 5.4 What to add for a per-run Comma-Separated Values (CSV) file

Pick one. Both keep the baseline code unchanged.

- With `MaxSimCounter="1"` the code never calls `PostExperiment()` itself (`lf.cpp:212-222`).
- The stdout line therefore depends on ARGoS calling `PostExperiment()` at run end (inference).
- `ga.py:123-132` parses that last line, which supports this (inference).

1. Wrapper script (no C++ change). For each arm, distribution and seed, set seed and `MaxSimTimeInSeconds`. Run `argos3 -n -c`. Parse the `lf.cpp:229` stdout line. Write `arm, distribution, seed, collected, sim_time_s`.
2. C++ change in `PostExperiment()` (`lf.cpp:227-305`). Add a CSV path setting and an `Algorithm` label to the file name. This touches the baseline arm, so the wrapper is safer (inference).

- Use a fixed seed list shared by both arms. Then each seed gives a paired comparison (inference).

## 6. Build risks on ARGoS 3.0.0-beta59, macOS

Do not run these. Evidence is static only.

| Risk | Evidence | Likely edit |
| --- | --- | --- |
| 1 CMake 4.x rejects `VERSION 2.8.12` | `CMakeLists.txt:1`. Local CMake is 4.4 at `/opt/homebrew/bin/cmake` (`01_pheromone/src/build/CMakeCache.txt:456-464`). CMake 4.0 removed compatibility below 3.5 `[S-BCM-3]` | Raise to `3.8` like `01_pheromone/src/CMakeLists.txt:1`, or pass `-DCMAKE_POLICY_VERSION_MINIMUM=3.5` |
| 2 Qt user functions always compile (low risk) | `source/CPFA/CMakeLists.txt:6-9` always adds `CPFA_qt_user_functions.cpp`. `include(ARGoSCheckQTOpenGL)` is commented out (`CMakeLists.txt:38`). But the Linux build got Qt 6 include paths from the ARGoS config anyway (`build/source/CPFA/CMakeFiles/CPFA_loop_functions.dir/flags.make:5-7`). Local ARGoS has Qt-OpenGL (`01_pheromone/src/build/CMakeCache.txt:42`). Same result on macOS `[UNVERIFIED]` | Only if compile fails: copy the `01_pheromone` guard `if(ARGOS_QTOPENGL_FOUND)` with `include_directories(${ARGOS_QTOPENGL_INCLUDE_DIRS})` (`01_pheromone/src/loop_functions/pheromone_loop_functions/CMakeLists.txt:19-25`, `37-39`) |
| 3 Stale Linux build caches in the clone | `build/CMakeCache.txt:427-437` (`/home/qlu/...`, CMake 3.22, `/usr/bin/cmake`). Also `source/CPFA/build/` and `source/ga-mpi/CMakeCache.txt` (CMake 2.8.12.2) | Build in a new folder. Do not reuse `build/` |
| 4 `build.sh` deletes `build/` | `build.sh:4` runs `rm -rf build` | Soft-delete rule: rename to `x_build` by hand, or use a new folder name |
| 5 `CPFA_loop_functions.cpp` is in two libraries | `source/CPFA/CMakeLists.txt:6-14` | `REGISTER_LOOP_FUNCTIONS` (`lf.cpp:633`) then runs in both libraries. Effect on macOS `[UNVERIFIED]`. Remove it from the controller library if loading fails |
| 6 Missing explicit plugin links | `source/CPFA/CMakeLists.txt:25-32` lacks `dynamics2d` and `media`. `01_pheromone` links them (`.../pheromone_loop_functions/CMakeLists.txt:28-35`) | Add them if the macOS linker reports undefined symbols |
| 7 `footbot_motor_ground` `rot_z_only` | `xml10:27`. Not found in installed foot-bot headers (grep). Registration lives in the plugin binary | `[UNVERIFIED]`. If ARGoS rejects it, delete the line. The code never reads it |
| 8 `ARGOS_QTOPENGL_LIBRARIES` may be empty | `source/CPFA/CMakeLists.txt:32` relies on a variable set only by the commented include | Covered by edit 2 |

- No Lua or GNU Scientific Library (GSL) is needed. Both `find_package` calls are commented out (`CMakeLists.txt:46`, `CMakeLists.txt:49`).
- `BUILD_EVOLVER=NO` skips Message Passing Interface (MPI) and Boost (`build.sh:11`, `CMakeLists.txt:60-79`).
- `CMAKE_MACOSX_RPATH 0` is the same as `01_pheromone` (`CMakeLists.txt:16-18`).
- `unistd.h` and `gethostname` are Portable Operating System Interface (POSIX). They work on macOS (`ctrl.cpp:2`, `ctrl.cpp:198`).
- C++17 is set in both projects (`CMakeLists.txt:25`, `01_pheromone/src/CMakeLists.txt:17`).

## 7. What "collision free" adds

- Collision handling lives in `BaseController`.
- I compared only that one file with upstream, through a fetch summary `[S-BCM-2]`.
- Other files were not compared. Respawn and nest scaling may also be fork changes. Unknown.
- No nest queue or nest traffic rule exists. Grep `Collision|collision` in `source/CPFA` finds only the time counter.

| Item | This fork | Upstream BCLab CPFA-ARGoS `[S-BCM-2]` |
| --- | --- | --- |
| Avoidance trigger cone | ±80 degrees (`base.cpp:38`) | ±37.5 degrees |
| Turn on contact | by the collision angle (`base.cpp:321-327`) | about 37.5 degrees, adjusted by the angle |
| `collisionDelay` | random 0.5 to 1.0 s (`base.cpp:328-329`) | absent |
| During the delay | turn states drive forward instead of turning (`base.cpp:384-388`, `400-404`) | absent |
| Collision counter | `collision_counter++` (`base.cpp:315`), summed at run end (`lf.cpp:272`) | present |

- Sensor: the summed `footbot_proximity` vector (`base.cpp:335-349`).
- Effect on our comparison: both arms share `BaseController`. Keep it unchanged, and the effect cancels (inference).
- Our method may send more robots to far, empty regions. Fewer robots near the nest may mean fewer collisions there (inference).

## 8. Hook points

| Goal | Function | Where | Why here |
| --- | --- | --- | --- |
| (a) Record visited positions per robot | `CPFA_controller::Searching()` | `ctrl.cpp:318-323` | Food is sensed only here, every 0.5 s. Log `GetPosition()` on the same tick |
| (a) alt. | `CPFA_controller::ControlStep()` | `ctrl.cpp:98-105` | Runs every tick. Already logs rays. Add a state check and a period |
| (b) Upload to the server at the nest | `CPFA_controller::Returning()`, `IsInTheNest()` branch | `ctrl.cpp:489-517` | Same place the pheromone is pushed (`ctrl.cpp:513`). Push the buffer into a new loop functions structure, then clear it |
| (c) Replace the random target | `CPFA_controller::SetRandomSearchLocation()` | `ctrl.cpp:578-605` | Single function for all 3 call paths (section 1.3) |
| (c) also | `CPFA_controller::Departing()` uninformed branch | `ctrl.cpp:270-292` | Without a change, the robot switches to search after a few seconds (section 1.4) |
| (c) also | `Returning()` decision order | `ctrl.cpp:526-544` | The random branch runs only with an empty pheromone list (section 1.3) |
| Server structure | `CPFA_loop_functions` members | `lf.h:115-123` | Add the visited structure next to `PheromoneList` |
| Server upkeep | `CPFA_loop_functions::PreStep()` | `lf.cpp:169-193` | Per-tick upkeep, like `UpdatePheromoneList()` |
| Server reset | `CPFA_loop_functions::Reset()` | `lf.cpp:137-167` | Clear the structure like `PheromoneList.clear()` |
| Per-robot reset | `CPFA_controller::Reset()` | `ctrl.cpp:112-137` | Clear the robot buffer |

- `CPFA_controller` is a `friend` of `CPFA_loop_functions` (`lf.h:18`). The controller can call new protected members directly.
- Existing grid or occupancy code: none (grep `grid|occup|visited`). `Nest.h:27` has an unused `visited_time_point_in_minute` counter only.
- `01_pheromone` has `pheromone_grid.cpp`, `owner_grid.cpp`, `trail_clusters.cpp` (`01_pheromone/src/loop_functions/pheromone_loop_functions/CMakeLists.txt:5-9`). They may be reusable. Not read for this map.

## 9. Open questions

open_questions:

1. Nest radius 0.25 m: XML value 0.25 (effective 0.456 m), or effective 0.25 m (XML 0.137)? See 4.3. The professor must say. Do not pick.
2. With effective 0.25 m, does the drop-off loop (`ctrl.cpp:499-502`) slow runs badly? Needs a timed run. Not run.
3. Respawn (`ctrl.cpp:631-639`) keeps 256 items. Does Table 1 expect respawn, or a fixed 256? The professor must say.
4. The evolved parameters fit 5 m, 64 cubes, 2 robots. Should the baseline use them, or GA-evolved values for Table 1? Does each distribution need its own values?
5. Does ARGoS beta59 also read `random_seed="0"` as a clock seed? Checked on master only `[S-BCM-4]`. `[UNVERIFIED]`
6. Does macOS loading fail on the double `REGISTER_LOOP_FUNCTIONS` (build risk 5)? Needs a build. Not run. `[UNVERIFIED]`
7. Does beta59 accept `footbot_motor_ground` `rot_z_only` (build risk 7)? `[UNVERIFIED]`
8. Collision-free comparison came through a fetched summary, not a full read `[S-BCM-2]`. `verification: partial`.
9. Per-run wall time for 720 s, 24 robots, headless. Needed to size 300 runs (3 distributions · 50 · 2 arms). Needs a run.

## Sources

[S-BCM-1] Final Project 2: Informed Search for Foraging Robot Swarms | `submodule_project/docs/Autonomous_Mobile_Robot_Programming_Final Project 2.pdf` | published: course handout, undated | accessed: 2026-11-12 | type: official | note: full text, 3 pages
[S-BCM-2] BCLab-UNM CPFA-ARGoS: source/Base/BaseController.cpp | https://raw.githubusercontent.com/BCLab-UNM/CPFA-ARGoS/master/source/Base/BaseController.cpp | published: master branch | accessed: 2026-11-12 | type: official | note: read through a fetch summary, verification partial
[S-BCM-3] CMake 4.0 Release Notes | https://cmake.org/cmake/help/v4.0/release/4.0.html | published: CMake 4.0 | accessed: 2026-11-12 | type: official | note: removal of compatibility below 3.5, CMAKE_POLICY_VERSION_MINIMUM, quoted in place
[S-BCM-4] ARGoS 3: src/core/simulator/simulator.cpp | https://raw.githubusercontent.com/ilpincy/argos3/master/src/core/simulator/simulator.cpp | published: master branch | accessed: 2026-11-12 | type: official | note: InitFramework seed logic, master not beta59
[S-BCM-5] Collision_Free_CPFA vendored clone, commit 9480f2e | `02_informed_search/vendor/Collision_Free_CPFA/` | published: commit 9480f2e | accessed: 2026-11-12 | type: official | note: code read in place, file:line cited per claim
