# Pheromone foraging under misleading trails: sourced research

- Task tag: PH
- Accessed: 2026-11-10
- Project: CSCI 6371 final project, UTRGV, Prof. Qi Lu. Build window 2 weeks from 2026-11-10. 4 people.
- Inputs: `research/lu_qi.md` (S-LQ-21, S-LQ-9), `site/en/projects/pheromone-misleading-trails.html`.
- Note: the dispatch path `en/projects/...` does not exist. The page lives under `site/en/projects/`.
- Status: complete, one pass. 17 search and fetch calls, 2 over the 15-call default budget.
- Abbreviations: central-place foraging (CPF), cumulative distribution function (CDF), central-place foraging algorithm (CPFA), density-based spatial clustering of applications with noise (DBSCAN), Augmented Reality for Kilobots (ARK), light-emitting diode (LED).

## Summary counts

- Rows kept: 96 (Q1 31, Q2 9, Q3 13, Q4 25, Q5 18)
- Sources: 10
- Unverified: 3 (COSΦ, Kilogrid, ground-sensor gradient following)
- Open questions: 16

## Q1. Detractor (attacker) model

| Claim | Value | Verification | Source |
| --- | --- | --- | --- |
| Foraging model | Central-place foraging (CPF). Four states: Departing, Searching, Surveying, Returning. Built on Hecker and Moses (ref 14 in the paper) | verified | [S-PH-1] |
| Pheromone form | Pheromone waypoints (coordinates), not a floor grid. Laying is a Poisson CDF decision on local resource count k | verified | [S-PH-1] |
| Pheromone decay | Waypoint strength starts at 1 and decays as w = e^(-t · λ_pd). Waypoints below threshold γ are removed. Values of λ_pd and γ are not printed | verified (form). Values: not stated | [S-PH-1] |
| Detractor behavior | Detractors mimic benign foragers. They report coordinates near capture sites instead of real resource locations | verified | [S-PH-1] |
| Where false trails lead | Capture sites. A forager that reaches one is captured and removed from foraging. Capture-site radius r_cs = r_center / 2 | verified | [S-PH-1] |
| Arena | D_arena = (10, 10, 1). Units not printed. ARGoS uses meters (inference) | verified (value) | [S-PH-1] |
| Robots | n_fg = 24 foragers (foot-bots per "Foot-bot search radius") | verified | [S-PH-1] |
| Detractor counts | Exp 1 and Exp 3: 25% of n_fg. Exp 2: 10%, 20%, 30%, 40%, 50% of n_fg | verified | [S-PH-1] |
| Resources | n_cl = 8 resource clusters, cluster size (6, 6). r_resource = 0.05. r_center = 0.25. r_search = 4 · r_resource | verified | [S-PH-1] |
| Lay rates | λ_fg and λ_dt in {1, 4, 8, 12} (Exp 1). The paper says smaller values mean more frequent laying | verified | [S-PH-1] |
| Lay rates, Exp 2 | Table 1 prints λ_fg = 4 and λ_dt = 1 for Exp 2. Section 6.1 says "a rate of 4 selected for further testing in Experiment 2". The two do not clearly agree for λ_dt [CONFLICT] (inside one paper) | partial | [S-PH-1] |
| Obstacles (Exp 3) | n_obs in {0, 4, 8, 12, 16} cylinders, random or annular layout | verified | [S-PH-1] |
| Run count, length | Exp 1: 50 runs. Time axes in Fig. 4 run to 16 minutes. Total simulated length per run not printed | partial | [S-PH-1] |
| Metrics | Total resources collected (%), total foragers captured (%), detractors isolated per minute, false positives detected, final "univelocity" | verified | [S-PH-1] |
| Effect, Exp 1 (attack only, 25% detractors) | Lay rate 1: 61.61% collected, 88.75% captured. Rate 4: 61.82%, 92.50%. Rate 8: 54.71%, 72.92%. Rate 12: 73.19%, 14.31% | verified | [S-PH-1] |
| Effect, Exp 2 | No detractors: about 85% collected. Attack only: 57.92% at 10%, 43.66% at 50%. Defense gain: +16.06% at 10%, +12.33% at 50%. Conclusion states up to 16.07% and capture cut up to 65.69% | verified. Note 16.06 vs 16.07 differ inside the paper | [S-PH-1] |
| Capture dynamics with defense | Capture rate peaks at 0.866 per minute (10%) and 2.6 per minute (50%) near minute 4. Falls near 0 by minute 15 to 16 | verified | [S-PH-1] |
| Earlier attack paper | Aswale, López, Ammartayakun, Pinciroli, "Hacking the colony", AAMAS 2022, pp. 27 to 34. Cited as ref 5 | verified (read in full, rows below) | [S-PH-1], [S-PH-6] |

### Q1 continued: Aswale et al. 2022 (grid pheromone, WPI)

| Claim | Value | Verification | Source |
| --- | --- | --- | --- |
| Simulator | Custom simulator, github.com/NESTLab/AntSimulator. Not ARGoS | verified | [S-PH-6] |
| Scale | n = 1024 ants, N = 50,000 steps, Δt = 0.016 s per step. World 1920 × 1080 units | verified | [S-PH-6] |
| Pheromone grid | Cell size c = 4 units. Each cell holds food pheromone and home pheromone, each in [0, 1000]. Nest and food cells are marked | verified | [S-PH-6] |
| Deposit | Intensity = 1000 · exp(−λτ), λ = 0.01, τ = steps since leaving nest (home) or since last food (food). Deposit takes the max of cell and ant intensity | verified | [S-PH-6] |
| Evaporation | Linear. Intensity' = Intensity − k · Δt, k = 1 unit per second | verified | [S-PH-6] |
| Gradient following | Every τ_turn = 7 steps, the ant draws χ = 32 random probe vectors (length up to 40, angle within ±0.8π). It heads to the probed cell with the highest intensity. Noise η = 0.1π. No pheromone: straight | verified | [S-PH-6] |
| Detractor placement | Detractors start at the nest center, facing the food. Dormant until τ_attack = 100 steps. Then secrete food pheromone constantly. "Refill" resets τ_d at the nest. Result: a blockade of misleading pheromone around the nest | verified | [S-PH-6] |
| Variables | Detractor share 0.10% to 50% (log steps). Misleading evaporation multiplier 0 to 1000 × normal. 20 runs per cell | verified | [S-PH-6] |
| Metrics | Food bits collected and delivered per cooperator. Fraction of cooperators that delivered food | verified | [S-PH-6] |
| Effect sizes | Never-evaporating misleading pheromone: 0.39% detractors disrupt the colony (5% of normal food). 3.13% detractors at normal rate: 0.14 food bits per ant vs 21.74 with none. Conclusion: 3% detractors cut food collection 150 fold | verified | [S-PH-6] |
| Defense | "Cautionary pheromone". Searching cooperators secrete it with intensity 1000 · exp(−λρ). Patience ρ falls while searching and refills to ρ_max on food. A cell is ignored when cautionary > food pheromone | verified | [S-PH-6] |
| Defense result | Best at ρ_max = 250, t_p in 2 to 10. Over 8 food bits per ant and over 96% collecting (vs 0.14 without defense). Fails at 50% detractors with non-evaporating pheromone (0.35 bits per ant) | verified | [S-PH-6] |
| Communication | None beyond the pheromone grid. No IDs, no messages | verified | [S-PH-6] |

## Q2. DBSCAN-based defense

| Claim | Value | Verification | Source |
| --- | --- | --- | --- |
| Points clustered | Spatial coordinates of pheromone trail waypoints | verified | [S-PH-1] |
| eps | ε = r_search (robot search radius). Table 1 prints r_search = 4 · r_resource and r_resource = 0.05 | verified. Any single number for ε is inference | [S-PH-1] |
| minPts | 2, "due to the expected data sparsity in small-scale swarm scenarios" | verified | [S-PH-1] |
| Cluster grouping | Graph: node = DBSCAN cluster. Edge when two clusters share at least one trail creator ID. Connected groups = robots with similar trail-laying behavior | verified | [S-PH-1] |
| Travel-time check | Each trail carries an estimated travel time from distance and average speed. A follower's actual time is compared with it. The estimate is updated by feedback only when a robot returns after the current estimate | verified | [S-PH-1] |
| Strike rule | A robot that does not return within the estimated time gives a strike to all robots in that cluster group. 5 strikes (empirical) = temporary isolation | verified | [S-PH-1] |
| Reintegration | A forager that returns on a flagged trail after the estimate reintegrates the creator and group members, or removes a strike | verified | [S-PH-1] |
| Communication needs | Not stated as a protocol. The defense needs creator IDs on every trail, shared trail lists, and a swarm-wide strike count. This implies a central or shared trail store (inference). CPF waypoints are typically shared at the nest (inference) | inference | [S-PH-1] |
| Who isolates | Not stated who executes isolation. Fig. 1 shows "Isolated Detractors" parked at the arena edge | partial | [S-PH-1] |

## Q3. Virtual pheromone implementations

| System | Mechanism | Parameters | Verification | Source |
| --- | --- | --- | --- | --- |
| Luna and Lu (ARGoS) | Pheromone waypoints, exponential decay w = e^(−t · λ_pd), removed below γ. Robots go to a waypoint, not up a gradient | λ_pd, γ not printed | verified | [S-PH-1] |
| Aswale et al. AntSimulator | Two-layer grid (food, home). Linear evaporation. Max-merge deposit. Probe-vector gradient choice | c = 4 units in a 1920 × 1080 world. k = 1 unit per s. Max 1000 | verified | [S-PH-6] |
| Font Llenas et al. 2018, Kilobots in ARGoS + ARK | Matrix of cells updated each step: c(i,j) = c(i,j)[1 − (ε + 4γ)dt] + γ[c(i, j±1) + c(i±1, j)]dt, c ≥ 0. Evaporation plus 4-neighbor diffusion | Cell 6.7 mm (150 cells per m). dt = 0.5 s. ε = 0.08 (evaporation). γ = 0.01 (diffusion). Drop φ = 100 | verified | [S-PH-7] |
| Font Llenas et al. 2018, sensing | Binary "antennae": 4 sectors of 45° in front, up to about 3.5 cm. Follow the triggered sector. Several triggered: pick the one most opposite the depot direction | Not a gradient. Presence or absence only | verified | [S-PH-7] |
| Font Llenas et al. 2018, deposit rule | On the way to the depot, drop with probability P = v / v_max every about 2 s | Quality v in [0, 10] | verified | [S-PH-7] |
| Font Llenas et al. 2018, setup | ARGoS with the Kilobot plugin and Augmented Reality for Kilobots (ARK). Code: github.com/DiODeProject/PheromoneKilobot | 2.5 × 2.5 m arena, central depot. 1, 2 or 4 sources, radius 10 cm, at 0.5 to 1.5 m. S in {50, 100, 200}. 20 simulated minutes. 100 runs per point | verified | [S-PH-7] |
| Font Llenas et al. 2018, scale effect | Absolute throughput rises with swarm size. Per-robot efficiency falls from crowding | S from 10 to 250 | verified | [S-PH-7] |
| Phormica (Salman et al. 2020), physical | e-puck projects ultraviolet (UV) light from 9 rear LEDs onto a photochromic floor. An omnidirectional camera detects magenta. No ARGoS | Fade to white in about 50 s. Trail width 30 to 75 mm. Control cycle 100 ms. 5 robots. Foraging runs 180 s, 20 runs per condition | verified | [S-PH-8] |
| Phormica foraging result | Phormica-Foraging retrieved "significantly more items" than Basic-Foraging (Wilcoxon signed-rank test, 95%) | Numbers only in a box plot, not read | partial | [S-PH-8] |
| Gradient following on a ground sensor | No source found in this pass. Font Llenas uses binary sectors. Aswale uses probe vectors over the grid. Luna and Lu use waypoints | none | unverifiable [UNVERIFIED] | none |
| COSΦ (Arvin, Krajník, Turgut, Yue), IROS 2015, pp. 407 to 412 | Artificial pheromone system for swarm research. Mechanism and parameters not read | not read | unverifiable [UNVERIFIED] | [S-PH-9] |
| iAnt-ARGoS (CPFA in ARGoS) | Repo with `source/`, `experiments/iAnt_linux.argos`, `iAnt_mac.argos`. Implements the CPFA. Pheromone classes and decay values not read | not read | partial | [S-PH-10] |
| Kilogrid | Named in [S-PH-7] as another augmented-reality pheromone platform for Kilobots. Not read | not read | unverifiable [UNVERIFIED] | [S-PH-7] |

## Q4. argos3-examples foraging demo

Files (repo `ilpincy/argos3-examples`, master branch):

- `experiments/foraging.argos` [S-PH-4]
- `loop_functions/foraging_loop_functions/foraging_loop_functions.cpp` [S-PH-2]. The matching `.h` was not fetched.
- A Qt user-functions class labelled `foraging_qt_user_functions` in the `.argos` file [S-PH-4]. Its file path was not checked (partial).
- `controllers/footbot_foraging/footbot_foraging.h` and `.cpp` [S-PH-3], [S-PH-5]
- Note: the fetch tool returned paraphrased summaries, not raw source. Method names below were reported by name. XML tag spellings were not shown verbatim.

| Item | Value | Verification | Source |
| --- | --- | --- | --- |
| Loop functions XML params | `items`, `radius`, `output`, `energy_per_item`, `energy_per_walking_robot` (node `foraging`) | verified | [S-PH-2] |
| Food placement | Uniform random, x in [-0.9, 1.7], y in [-1.7, 1.7]. Same in `Init()` and `Reset()`. RNG category "argos" | verified | [S-PH-2] |
| Nest area | x < -1.0. No nest entity. The nest is a floor region | verified | [S-PH-2] |
| `GetFloorColor(const CVector2&)` | Nest: `CColor::GRAY50`. Within food radius of an item: `CColor::BLACK`. Else `CColor::WHITE` | verified | [S-PH-2] |
| `PreStep()` drop | Carrying and x < -1.0: respawn item at a new random spot, clear carry flag, count +1, energy + `energy_per_item`, `m_pcFloor->SetChanged()` | verified | [S-PH-2] |
| `PreStep()` pickup | Not carrying and x > -1.0: first item within radius moves to (100, 100). Robot carries that index. `SetChanged()` | verified | [S-PH-2] |
| How a robot "has food" | The loop function writes the controller's `SFoodData` (`HasFoodItem`, `FoodItemIdx`). The controller never senses food itself | verified | [S-PH-2], [S-PH-5] |
| Output file | Truncated on open. Header `# clock walking resting collected_food energy` (tab separated). One row per step | verified | [S-PH-2] |
| Energy | Starts at 0. + `energy_per_item` per drop. − walking robots × `energy_per_walking_robot` per step | verified | [S-PH-2] |
| Sensors | Foot-bot proximity (default), foot-bot light (rot_z_only), foot-bot motor ground (rot_z_only), range-and-bearing (medium "rab"). Likely XML tags `footbot_proximity`, `footbot_light`, `footbot_motor_ground`, `range_and_bearing` (not shown verbatim) | verified (sensor set). Tag spellings partial | [S-PH-3], [S-PH-4] |
| Actuators | Differential steering, LEDs (medium "leds"), range-and-bearing. `CCI_...` class names not shown verbatim | verified (set). Class names partial | [S-PH-3], [S-PH-4] |
| State machine | `SStateData::EState`: `STATE_RESTING`, `STATE_EXPLORING`, `STATE_RETURN_TO_NEST` | verified | [S-PH-3] |
| Nest detection | Motor ground sensors 2 and 3 (back) both read in [0.25, 0.75] = gray = in nest. White ≈ 1, black ≈ 0 | verified | [S-PH-5] |
| Return to nest | Light vector from `CalculateVectorToLight()` plus proximity diffusion vector. In the nest while exploring: diffusion − 0.25 × light vector | verified | [S-PH-5] |
| Obstacle avoidance | `DiffusionVector()`: sum of proximity readings. If angle in go-straight range and length < `Delta`, go straight. Else steer opposite | verified | [S-PH-5] |
| Range-and-bearing message | 1 byte, `Data[0]` = last exploration result (none, successful, unsuccessful). Neighbors in Rest adjust probabilities (social rule) | verified | [S-PH-5] |
| LED colors | Red = resting. Green = exploring. Blue = returning | verified | [S-PH-5] |
| Transitions | Rest → Explore after `MinimumRestingTime` and a random draw. Explore → Return on food, or after `MinimumUnsuccessfulExploreTime` with probability. Return → Rest after `MinimumSearchForPlaceInNestTime` in nest | verified | [S-PH-5] |
| Framework | `ticks_per_second` = 10, `length` = 0 (unlimited), `random_seed` = 123 | verified | [S-PH-4] |
| Arena | 5 × 5 × 2 m, walls at x, y = ±2 (4 × 4 m inside). Floor `pixels_per_meter` = 50, source "loop_functions" | verified | [S-PH-4] |
| Lights | 4 yellow lights at x = -2, y in {-1.5, -0.5, 0.5, 1.5}, z = 1.0, intensity 3.0 | verified | [S-PH-4] |
| Robots | 20 foot-bots, uniform in x [-2, -1], y [-2, 2] (in the nest) | verified | [S-PH-4] |
| Food params | `items` = 15, `radius` = 0.1, `energy_per_item` = 1000, `energy_per_walking_robot` = 1, `output` = foraging.txt | verified | [S-PH-4] |
| Controller params | Max speed 10. Initial rest↔explore probs 0.1. Rule deltas 0.01. Min resting 50, min unsuccessful explore 600, min nest search 50 (ticks) | verified | [S-PH-4] |
| Physics | `dynamics2d` | verified | [S-PH-4] |

## Q5. Recommended starting parameters

Column "Design": W = waypoint replication of Luna and Lu. G = floor-grid pheromone (the project page design). Both = either.

| Parameter | Value | Design | Basis | Verification |
| --- | --- | --- | --- | --- |
| Ticks per second | 10 | Both | argos3-examples foraging [S-PH-4] | verified (source value) |
| Arena (W) | (10, 10, 1), as in Luna and Lu | W | [S-PH-1] | verified (source value) |
| Arena (G, start) | 5 × 5 m with walls at ±2 m, as in the example. Scale up only if time allows | G | [S-PH-4]. Choice is inference | inference |
| Foragers (W) | 24 | W | [S-PH-1] | verified (source value) |
| Foragers (G, start) | 20, as in the example | G | [S-PH-4] | verified (source value). Reuse is inference |
| Detractor counts 0, 1, 2, 4 | Keep the project page plan. Whether detractors are added to or taken from the forager count is not printed in [S-PH-1]. Decide and log it | Both | Project page. Mapping to percent not given | inference |
| Detractor shares (W) | 10%, 20%, 30%, 40%, 50% of n_fg (Exp 2). 25% for the other experiments | W | [S-PH-1] | verified (source value) |
| Food (W) | 8 resource clusters, size (6, 6), r_resource = 0.05 | W | [S-PH-1] | verified (source value) |
| Food (G, start) | 15 items, radius 0.1, respawn on delivery | G | [S-PH-4], [S-PH-2] | verified (source value) |
| Floor resolution | Example floor uses `pixels_per_meter` = 50 for the floor texture. Pheromone cell size is a separate choice. A coarse cell (several cm) keeps `SetChanged()` repaints cheap | G | [S-PH-4]. Cell size is inference | inference |
| Evaporation (G) | No ARGoS foot-bot value found. Anchors with different units: ε = 0.08, multiplied by dt = 0.5 s each step, on 6.7 mm Kilobot-scale cells [S-PH-7]. Linear k = 1 unit per s on a 0 to 1000 scale [S-PH-6]. Physical fade about 50 s [S-PH-8]. Do not copy one value across without rescaling | G | [S-PH-6], [S-PH-7], [S-PH-8] | inference (no direct source) |
| Diffusion (G) | γ = 0.01 with the same dt and cell caveat. Optional for week 1 | G | [S-PH-7] | verified (source value). Reuse is inference |
| Deposit (G) | φ = 100 per drop [S-PH-7], or 1000 · exp(−λτ) with λ = 0.01 [S-PH-6] | G | [S-PH-6], [S-PH-7] | verified (source values). Choice is inference |
| Pheromone decay (W) | w = e^(−t · λ_pd), removed below γ. λ_pd and γ not printed. Pick and log values | W | [S-PH-1] | partial |
| Lay rates (W) | λ ∈ {1, 4, 8, 12}. See the Exp 2 conflict in Q1 | W | [S-PH-1] | partial |
| DBSCAN (W) | ε = r_search, minPts = 2. 5 strikes to isolate | W | [S-PH-1] | verified (source value) |
| Simulation length | 20 simulated minutes [S-PH-7]. Luna and Lu plots run to 16 minutes [S-PH-1]. The project page plans food per 10 minutes | Both | [S-PH-1], [S-PH-7] | partial |
| Runs per point | 50 (Luna and Lu Exp 1), 20 (Aswale), 100 (Font Llenas). Project page plans 10 seeds | Both | [S-PH-1], [S-PH-6], [S-PH-7] | verified (source values). Choice is inference |

## Implications for design

All items are inference from the cited rows.

1. Finding: the project page and Luna and Lu differ in design. This is a finding, not a decision.

   | Aspect | Project page | Luna and Lu [S-PH-1] |
   | --- | --- | --- |
   | Pheromone | Floor grid, gradient following | Waypoints with exponential decay |
   | False trail target | An empty area | Capture sites that remove foragers |
   | Defense | Suspect trail ends clustered by distance | DBSCAN on waypoints, creator-ID graph, travel-time check, 5 strikes |
   | Metric | Food per 10 minutes | % resources collected, % foragers captured |

2. The floor-grid design is closer to Aswale et al. [S-PH-6] than to Luna and Lu. Aswale's attack is a pheromone blockade near the nest, and its defense needs no IDs or messages.
3. A faithful Luna and Lu replication needs creator IDs on trails and a shared trail store. That implies nest-side or range-and-bearing sharing [S-PH-1].
4. Reuse the example skeleton: `GetFloorColor`, `PreStep` pickup and drop, `SetChanged()`, and the per-step output file [S-PH-2].
5. Floor-color collision: the example nest test reads gray (0.25 to 0.75) on back ground sensors 2 and 3. Food is black [S-PH-5]. A gray pheromone shade would trigger the nest test. Keep pheromone off the ground-sensor channel, or redesign the nest test.
6. For sensing, a loop-function lookup of the cell values near the robot is simpler than the ground sensor. That matches Font Llenas, where ARK supplies a virtual sensor [S-PH-7].
7. No foot-bot evaporation value exists in the sources. Pick one, write it before the runs, and log it (`rules/measurement.md` §1).
8. Report both metrics: resources collected and foragers captured or time wasted. Both prior papers report two metrics [S-PH-1], [S-PH-6].
9. Novelty angle: a no-communication defense (Aswale-style) against the Luna and Lu capture-site attack. No source in this pass tests that pair. This is "not found", not "nobody did it".

## Selection log

| Entity | Decision | Rule |
| --- | --- | --- |
| Luna and Lu, TAROS 2024 | kept, read in full | core paper, first-party |
| Aswale et al., AAMAS 2022 | kept, read in full | direct prior attack and defense, first-party |
| argos3-examples foraging (loop functions, controller, `.argos`) | kept | first-party code, asked in Q4 |
| Font Llenas et al., ANTS 2018 | kept, pages 3 to 9 read | ARGoS grid pheromone with numbers |
| Phormica, Frontiers 2020 | kept | physical pheromone with a decay time |
| COSΦ, IROS 2015 | kept as citation only | asked in Q3. Not read |
| iAnt-ARGoS (CPFA) | kept as partial | ARGoS code lead for waypoint pheromone. Source not read |
| Kilogrid | kept as citation only | named in [S-PH-7]. Not read |
| GenGrid (arXiv 2504.20071) | rejected | physical light grid, no ARGoS. Snippet only, out of budget |
| Talamali et al. 2019, Swarm Intelligence | rejected | follow-up of [S-PH-7]. Snippet only, out of budget |
| Generic grid-evaporation papers (arXiv 2408.10278, cs/0512002, cs/0512003) | rejected | not swarm robotics in ARGoS. Snippet only |
| Qi Lu pheromone papers, UR 2024 and ICCCR 2024 | not fetched | IEEE blocked in the earlier pass (`research/lu_qi.md`). Out of budget |

## open_questions:

- Luna and Lu: λ_pd and γ values are not printed. Total simulated length per run is not printed.
- Luna and Lu: λ_dt in Exp 2 [CONFLICT] between Table 1 (1) and Section 6.1 text (4).
- Luna and Lu: defense gain 16.06% (Results) vs 16.07% (Conclusion) inside the paper.
- Luna and Lu: who executes isolation, and how trail lists and strikes are shared. Not described.
- Luna and Lu: are detractors part of the 24 foragers or extra? How a percent maps to whole robots is not printed.
- Arena units in Luna and Lu (assumed meters, inference).
- argos3-examples: `foraging_loop_functions.h` not fetched. XML tag spellings and `CCI_...` class names were summarized, not shown verbatim. Re-read the raw files to confirm exact API names.
- argos3-examples: path of the Qt user-functions files not checked.
- No source found for pheromone gradient following on a foot-bot ground sensor in ARGoS.
- No ARGoS foot-bot evaporation rate found.
- COSΦ mechanism and parameters not read [UNVERIFIED].
- Kilogrid not read [UNVERIFIED].
- iAnt-ARGoS pheromone class and decay values not read.
- Phormica foraging numbers exist only in a box plot.
- Font Llenas: pages 1, 2 and 10 onward not read.
- Qi Lu UR 2024 and ICCCR 2024 pheromone paper titles still unread.

## Sources

[S-PH-1] Robust Mitigation Strategy for Misleading Pheromone Trails in Foraging Robot Swarms | https://par.nsf.gov/servlets/purl/10593555 | published: 2025, TAROS 2024 LNAI 15052 pp. 307 to 319, DOI 10.1007/978-3-031-72062-8_27 | accessed: 2026-11-10 | type: paper | note: all 13 pages read from the NSF PAR PDF. Same document as S-LQ-21
[S-PH-2] argos3-examples: foraging_loop_functions.cpp | https://raw.githubusercontent.com/ilpincy/argos3-examples/master/loop_functions/foraging_loop_functions/foraging_loop_functions.cpp | published: master branch | accessed: 2026-11-10 | type: official | note: read through a fetch summary, not verbatim. Same file as S-LQ-9
[S-PH-3] argos3-examples: footbot_foraging.h | https://raw.githubusercontent.com/ilpincy/argos3-examples/master/controllers/footbot_foraging/footbot_foraging.h | published: master branch | accessed: 2026-11-10 | type: official | note: fetch summary with identifiers, not verbatim
[S-PH-4] argos3-examples: foraging.argos | https://raw.githubusercontent.com/ilpincy/argos3-examples/master/experiments/foraging.argos | published: master branch | accessed: 2026-11-10 | type: official | note: fetch summary of the XML, values reported, tags not verbatim
[S-PH-5] argos3-examples: footbot_foraging.cpp | https://raw.githubusercontent.com/ilpincy/argos3-examples/master/controllers/footbot_foraging/footbot_foraging.cpp | published: master branch | accessed: 2026-11-10 | type: official | note: fetch summary with identifiers, not verbatim
[S-PH-6] Hacking the Colony: On the Disruptive Effect of Misleading Pheromone and How to Defend Against It | https://arxiv.org/abs/2202.01808 | published: AAMAS 2022 pp. 27 to 34, arXiv v2 2022-03-28 | accessed: 2026-11-10 | type: paper | note: all 8 pages of the arXiv PDF read
[S-PH-7] Quality-Sensitive Foraging by a Robot Swarm through Virtual Pheromone Trails | https://mstalamali.github.io/pdf/fontllenas-ANTS2018.pdf | published: ANTS 2018, LNCS 11172 pp. 135 to 149 | accessed: 2026-11-10 | type: paper | note: pages 3 to 9 of the author-hosted PDF read
[S-PH-8] Phormica: Photochromic Pheromone Release and Detection System for Stigmergic Coordination in Robot Swarms | https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.591402/full | published: 2020-12, Frontiers in Robotics and AI 7 | accessed: 2026-11-10 | type: paper | note: full text read through a fetch summary. PMC mirror blocked by a browser check
[S-PH-9] COSΦ: Artificial Pheromone System for Robotic Swarms Research | https://doi.org/10.1109/IROS.2015.7353405 | published: IROS 2015 pp. 407 to 412 | accessed: 2026-11-10 | type: paper | note: citation only, from a search snippet and the reference list of S-PH-6. Not read
[S-PH-10] iAnt-ARGoS | https://github.com/johncarl81/iAnt-ARGoS | published: repository, undated | accessed: 2026-11-10 | type: official | note: top-level README and folder list only. Source code not read
