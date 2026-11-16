# Prof. Qi (Luki) Lu and MARS lab papers for Final Project 2

- Task tag: LP
- Accessed: 2026-11-16
- Purpose: per paper, the method, the stated limits and future work, and improvement ideas for our design (option B quadtree + reservation, D-010).
- Reused research (not redone): `informed_search_survey.md` (S-IS-*), `../../deprecated_01_pheromone/research/lu_lineage.md` (S-LL-*), `../../research/lu_qi.md` (paper list only). Reused IDs are copied into Sources.
- Status: complete, one pass. 22 web search and fetch calls (no budget set, skill default 15), plus page-image reads of three saved PDFs.
- Abbreviations: central-place foraging algorithm (CPFA), Grid-Based Complete Foraging Algorithm (GCFA), Adaptive Repulsive Pheromone Clustering (ARPC), multiple-place foraging algorithm (MPFA), distributed deterministic spiral algorithm (DDSA), Multiple-Distributed Bidirectional Spiral Algorithm (MDBSA), genetic algorithm (GA), NeuroEvolution of Augmenting Topologies (NEAT), multi-actor-attention-critic (MAAC), University of Texas Rio Grande Valley (UTRGV), IEEE International Conference on Robotics and Automation (ICRA), IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), Conference on Robots and Vision (CRV). GPFA is kept as ARPC prints it.

## Summary counts

- Papers kept: 12 (verified 4, partial 8)
- Papers rejected or not read: 6 (selection log)
- Sources: 19 (9 new S-LP, 10 reused S-IS and S-LL)
- Unverified rows: 0. Ideas ranked: 10
- Open questions: 12

## 1. Per-paper tables

- Verification enum: verified (paper pages read), partial (abstract, record, summary or citation only), unverifiable.
- Lever tags: (a) score lever, more resources in 12 min. (b) efficiency lever, server cost. (c) report or novelty lever.
- Every "idea for us" cell is inference unless a source ID is on it.
- Design words: "T1 to T4", `q_map`, `r_res`, `t_res`, `T_stale`, `rec_period` are from `../DESIGN.md` §3.6 and Table 6.
- "Inside design" = a tuning candidate the design already lists. "New D-row" = needs a `DECISIONS.md` row first.

### 1.1 GCFA: A Visitation Grid for Complete Coverage Foraging in Robot Swarms (key: gcfa-visitation-grid)

| Field | Value |
| --- | --- |
| Authors, venue | Gonzalez, Gao, Zhang, Lu (UTRGV). arXiv 2605.21947, 2026-05-21. Comment: 23rd International Conference on Ubiquitous Robots [S-IS-2] |
| Problem | Collecting the last resources is slow. Robots cannot store every visited point. A server that scans all points costs O(mcr) memory, m robots, c returns, r points (PDF p. 3) [S-LP-1] |
| Method | Robot keeps a first-in first-out queue of 20 positions, one every 25 s. Upload on return. Server keeps one counter per cell of an n × n grid, O(n²) memory. A robot in uninformed walk gets the 3 × 3 block with the minimum summed count. It visits a random point in each of the 9 cells, counter-clockwise, with a spiral search in each. Then a correlated random walk until a find or a give-up with probability p (PDF pp. 3 to 4, Algorithm 1) [S-LP-1] |
| CPFA fact stated | The CPFA uninformed robot heads to "a random location close to the boundaries". On the way it has a 76 % chance every 5 s to switch to a correlated random walk (PDF p. 3) [S-LP-1] |
| Test setup | ARGoS. 16 robots. Arena 14 × 14 m (Exp. I, II), 8 to 16 m (Exp. III). Resources 16 to 80. Clustered, Powerlaw, Random. Metric: median time to collect all. Runs: Table I says 30, text says 50 (PDF pp. 4 to 5) [S-LP-1] |
| Key numbers | Random, 48 resources: 33 % less time. Powerlaw: 14 %. Clustered: "no difference" (PDF p. 5). 10 × 10 m, Random, 48: 1541 s vs 2165 s (Table II). Gain grows with arena: 581 s at 8 m to 1267 s at 16 m (Table II). Last 10 %: Random 900.8 vs 1755.2 s, Powerlaw 774.8 vs 1199.2 s, Cluster 680.7 vs 593.5 s, so −14.69 % (Table III, PDF p. 6) [S-LP-1] |
| Stated limits | "CPFA outperformed, or had very similar results to, our GCFA method in clustered environments" (PDF p. 7). Cause: "Cells near resource clusters accumulate high visit counts, reducing their likelihood of being selected" (PDF p. 7). Robots were sent "to empty corners of the arena rather than persisting at known cluster sites" (PDF p. 7). Selection is O(n²): "sorting cells by visit count requires O(n²) time" (PDF p. 7) [S-LP-1] |
| Stated future work | "we will conduct a theoretical analysis of the relationship between the number of cells and the computation cost and investigate strategies to optimize cell selection" (PDF p. 7). Queue size and logging interval: "Optimizing these parameters and finding the right balance for different scenarios is left for future work" (PDF p. 3) [S-LP-1] |
| Ideas for us | 1. Do not let found-food cells look "visited": the cluster failure above (a, new D-row, see §3 idea 1). 2. The §5.2 benchmark answers the cells-vs-cost future work directly (b, c, inside design). 3. Tour a block of cells per trip, as in Algorithm 1 (a, new D-row). 4. Sweep `rec_period` to answer the logging future work (b, c, new D-row). 5. Report time per 10 % milestone beside the 12 min count, as Fig. 8 to 10 do (c, no new runs) |
| Fit to our score (inference) | The gain is measured as time to collect all. The paper says density "≤ 10 %" is where search gets hard (PDF p. 3). With respawn on (D-007) our arena always holds 256 items. So our runs may never reach that regime |
| Verification | verified (PDF pp. 2 to 8 read as page images this pass, pp. 3 to 6 in the survey) |

### 1.2 Grid-based complete resource foraging for robot swarms (key: grid-based-complete-ant-2025)

| Field | Value |
| --- | --- |
| Authors, venue | Gonzalez, Lu. "ANT-2025", as printed in reference [10] of ARPC [S-IS-3] |
| Method | Per ARPC: "relying solely on visitation frequency within a fixed 3×3 grid". ARPC calls it GPFA [S-IS-4] |
| Key numbers | ARPC's GPFA values equal GCFA Table III values. So it is the same method as §1.1 [S-IS-2], [S-IS-4] |
| Stated limits, future work | Not read. Paper not found |
| Ideas for us | Same as §1.1 |
| Verification | partial (citation only). Not found in two queries this pass: "Gonzalez Lu grid-based complete resource foraging robot swarms ANTS 2025" and the exact title in quotes. Both returned only the arXiv GCFA paper, ARPC and mirrors [S-LP-9] |

### 1.3 ARPC: Adaptive Repulsive Pheromone Clustering for Foraging Robot Swarms (key: arpc)

| Field | Value |
| --- | --- |
| Authors, venue | Pena-Caballero, Tarawneh, Lu. arXiv 2608.16822, 2026-08-17. Submitted to DARS (Distributed Autonomous Robotic Systems) [S-IS-4] |
| Problem | Grid counts in a fixed 3 × 3 block are coarse. Robots re-search explored space [S-IS-4] |
| Method | Robot records a "repulsive pheromone" point every ρ = 2 s, at most λ = 50. Upload on return. Nest clusters every 5 s: absorb points into covering clusters, then density-based spatial clustering of applications with noise (DBSCAN), ε = α + offset, α = 0.75 m, minPts = 2, then merge overlapping clusters. Cluster = centre + radius. Target: first of up to 1000 random candidates outside all clusters. Then spiral search, then random search. Site fidelity and pheromone stay, chosen first [S-IS-4] |
| Test setup | ARGoS. 16 robots. 14 × 14 m, 48 resources (Exp. II). 8 to 16 m (Exp. III). 50 runs. Metric: time to collect all and per 10 % milestone [S-IS-4], [S-LP-2] |
| Key numbers | Last 10 %, Random: 703.7 s vs GPFA 900.8 s (+21.89 %). Cluster: 593.8 vs 680.7 s (+12.78 %). Powerlaw: 1021.1 vs 774.8 s (−31.79 %) [S-IS-4] |
| Stated limits | Powerlaw: "Isolated resources near dense clusters can fall inside repulsive zones, lowering their likelihood of collection" (Section 6.2) [S-LP-2]. Unclustered points are skipped "to avoid long computation times" (Section 4.1) [S-LP-2]. No runtime or complexity numbers [S-LP-2] |
| Where the gain appears [CONFLICT] | "For the Clustered and Powerlaw distributions, beginning at the point where 60% of the resources have been collected, the proposed algorithm exhibits a substantial performance advantage". Random: "once 80% of the resources have been collected" (p. 9) [S-LP-2]. Contradicted by the conclusion: "the performance gains are not limited to the endgame phase; ARPC accelerates initial discovery" (p. 12) [S-LP-2]. Both in one source. This is the only lab claim of an early gain, which is our score window |
| Tail fact stated | "CPFA allocates approximately 50% of its total foraging time to collecting the final 12% of the available resources" (p. 9) [S-LP-2] |
| Stated future work | "motivating future extensions toward real-world deployments involving dynamic targets, communication limits, and energy constraints" (p. 12) [S-LP-2] |
| Ideas for us | 1. Same lesson as GCFA from the other side: repelling robots from visited space loses isolated items near clusters. Keep space near pickups available (a, new D-row). 2. ARPC measures no server cost. Our `queries.csv` cost columns and §5.2 benchmark fill that gap (b, c, inside design). 3. "Dynamic targets" is their future work. Ask the professor whether respawn (D-007) counts as dynamic targets, or whether they mean moving targets (c, question only). 4. Rejection sampling of 1000 candidates has no completeness bound. Our nearest-available query does (c, inside design) |
| Verification | verified (survey read PDF pp. 4 to 12. This pass re-read pp. 9 and 12 as page images) |

### 1.4 CPFA: Beyond pheromones (Hecker and Moses 2015) (key: cpfa-beyond-pheromones)

Lu is not an author. This is the baseline of the assignment and of every Lu-lab paper above.

| Field | Value |
| --- | --- |
| Venue | Swarm Intelligence 9:43 to 70, 2015 [S-LL-1] |
| Problem | Robot swarms need error tolerance, flexibility and scalability in one framework [S-LL-1] |
| Method | Central-place foraging algorithm (CPFA) modeled on seed-harvester ants. A genetic algorithm (GA) tunes 7 parameters (memory, communication, movement) [S-LL-1] |
| Test setup | Simulation and up to 6 iAnt robots [S-LL-1]. Arena and counts not read in this pass |
| Key numbers | A strategy evolved for clustered resources doubles efficiency there vs one evolved for random. More pheromone use when resources are clustered. Larger swarms disperse more [S-LL-1] |
| Stated future work | "Future work should test whether and how a GA can adapt the CPFA to more complex environments, additional sources of robot error, and larger physical robot swarms" (p. 67). Also a foundation "for adapting behavioral rules in response to sensed environmental conditions in real time" (p. 67) [S-LL-1] |
| Stated limits | Not read in this pass |
| Ideas for us | 1. Parameters are distribution-specific. The repo ships one 10 × 10 m set (D-008). Our map gain may differ by distribution partly because the shared set fits Random best (c, report caveat, no runs). 2. Real-time rule adaptation: switch the map on only when the pheromone list is empty or the found-food rate drops (a, new D-row) |
| Verification | verified (pp. 1, 2, 23 to 25 read in `lu_lineage.md`). Other cells not read |

### 1.5 MDBSA: Adaptive Multiple Distributed Bidirectional Spiral Path Planning (Lu and Luna, CRV 2023) (key: mdbsa-spiral-2023)

Page convention: PDF p. 1 is a ScholarWorks cover. PDF pp. 2 to 9 are printed pp. 225 to 232. Printed pages are cited.

| Field | Value |
| --- | --- |
| Venue | 2023 20th Conference on Robots and Vision (CRV), pp. 225 to 232, DOI 10.1109/CRV60082.2023.00036 [S-LP-3], [S-LP-4] |
| Problem | The distributed deterministic spiral algorithm (DDSA) does not scale: congestion at the central zone grows with robots, and spiral paths cannot be planned for many robots (p. 225) [S-LP-3] |
| Method | Split the square arena into N_R = 4^k equal square regions. One square spiral per region. The centre assigns a robot to an unassigned region, else to the region with the longest remaining spiral. A second robot walks that spiral from the other end. Robots resume at the last find. Detection radius 0.13 m, spiral gap g = 0.18 m for wheel-encoder noise (pp. 227 to 228). Two versions: delivery to the central server (Centralized) or to regional centres (Distributed, an upper bound) (p. 228) [S-LP-3] |
| Test setup | ARGoS. 8 × 8 m. Clusters of different sizes. 100 runs. Exp. 1: 8 robots, 160 resources, 4/16/64 regions, 12 min. Exp. 2: 8 to 32 robots, 200 resources, 16 regions, 16 min. Exp. 3: 16 robots, 100 to 300 resources, 12 min. Metrics: resources per robot, collision time per robot. Mann-Whitney U test (pp. 229 to 230) [S-LP-3] |
| Key numbers | Exp. 1: Centralized about equal to DDSA at 4 and 16 regions, about 25 % fewer at 64 regions. Distributed about 101 % more than DDSA (p. 229). Exp. 2: Centralized about 44 % fewer than DDSA as robots rise from 14 to 32 (p. 230). Exp. 3: Centralized about 30.4 % fewer than DDSA (p. 231). Centralized has the highest collision time in all three (pp. 229 to 231) [S-LP-3] |
| Stated limits | Centralized loses at 64 regions "because robots are distributed across smaller regions around the center, which leads to more collisions" (p. 231). "delivering to the center is a major issue" (p. 231). Distributed shows rising variance with more resources: "some instability" (p. 231) [S-LP-3] |
| Stated future work | "the simulations were conducted in a controlled environment, which may not reflect the complexity and dynamics of real-world scenarios" (p. 232). Test "with sensor errors or obstacles" (p. 232). "integrates both tasks", foraging and transport, for example "a specialized transportation vehicle" (p. 232) [S-LP-3] |
| Evidence regime | The only Lu-lab paper read with a fixed 12 min count, like our score (Exp. 1 and 3). No CPFA arm. It compares against DDSA only [S-LP-3] |
| Ideas for us | 1. Our arm is the "Centralized" case: one nest, 24 robots. MDBSA shows region assignment with central delivery can lose to plain search through nest collisions. Add collision time per run as a mechanism column (c, new D-row: schema change). 2. Spiral at the map target (T4) with g = 0.18 m as in this paper (a, inside design). 3. Resume-at-last-find already exists in CPFA as site fidelity. Keep the map behind fidelity (`q_map` = 0 start) (a, inside design). 4. The 64-region loss (25 %) is blamed on collisions near the centre (p. 231), not on target size. So it does not argue against small map targets by itself (inference) |
| Verification | verified (all 9 PDF pages read as page images) |

### 1.6 MPFA: multiple-place foraging algorithm (Lu, Moses, Hecker, 2016) (key: mpfa-2016)

| Field | Value |
| --- | --- |
| Venue | arXiv 1612.00480 (comment: Robotics: Science and Systems). Same work as IROS 2016 pp. 3815 to 3821 is inference [S-LL-3], [S-LP-5] |
| Problem | "Individual robots are not effective at exploring large unmapped areas". One central nest raises travel and collisions [S-LP-5] |
| Method | Four nests placed uniformly. A robot returns to the nearest nest. Pheromone waypoints are shared per nest. GA-tuned Poisson rates for site fidelity and pheromone (Sec. III, IV) [S-LP-5] |
| Test setup | ARGoS, 15 × 15 m, partially clustered targets. Up to 1024 targets, 32 robots in the adaptation test. 100 replicates. Metrics: foraging rate, collision, travel and search time [S-LP-5] |
| Key numbers | Foraging rate up to 66 % higher (64 robots). Search time up to 34 % lower (4 robots) (Sec. VI) [S-LP-5]. Not read in place |
| Stated limits | "there are tradeoffs among communication (and therefore search time) and travel time and congestion" (Sec. VII) [S-LP-5] |
| Stated future work | Consider "the cost of deploying multiply nests" and evolve the number of nests per distribution (Sec. VII) [S-LP-5] |
| Ideas for us | The assignment fixes one nest, so extra nests are out of scope. Borrow only the metric split: travel, search and collision time per robot. Our schema already has `travel_s` and `search_s` (c, inside design) |
| Verification | partial (fetch summary of the arXiv HTML. Numbers not read in place) |

### 1.7 Other PhD-line papers (abstract or record only)

| Key | Paper | What is known | Stated limits or future work | Ideas for us | Source | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| dynamic-depots-2018 | Lu, Hecker, Moses. Multiple-place swarm foraging with dynamic depots. Autonomous Robots 42(4) 909 to 926 | Depots move to the centroid of recent finds. Beats static MPFA and the CPFA. Larger gain in 50 × 50 m | Not read. Springer login wall this pass too | Moving depots are out of scope (one fixed nest). Its idea "go where recent finds are" maps to yield weighting of map targets (option C tactic) (a, new D-row) | [S-LL-4] | partial |
| transport-network-2020 | Lu, Fricke, Tsuno, Moses. A Bio-Inspired Transportation Network for Scalable Swarm Foraging. ICRA 2020 pp. 6120 to 6126 | Mobile depots feed a branching network. Scale-invariant foraging up to thousands of robots in ARGoS | Not read | Out of scope (changes the delivery task) | [S-LL-7] | partial |
| phd-thesis-2019 | Lu. An Efficient Multiple-Place Foraging Algorithm for Scalable Robot Swarms. University of New Mexico, 2019 | Goal: per-robot foraging rate that stays constant as swarm and arena grow. MPFA beats the CPFA in ARGoS | "Full implementation of the MPFA in an outdoor environment is the next step" (abstract, relayed by a fetch summary) | Report framing: our server cost vs arena size is the same "scale" question for search memory (c) | [S-LL-5], [S-LP-7] | partial (full-text PDF returned HTTP 403) |
| cpfa-vs-ddsa-icra-2019 | Lu, Griego, Fricke, Moses. Comparing Physical and Simulated Performance of a Deterministic and a Bio-inspired Stochastic Foraging Strategy for Robot Swarms. ICRA 2019 pp. 9285 to 9291 | DDSA wins in simulation. Outdoors the CPFA is as good or better | Authors say algorithms should be compared in the real world (abstract) | Spiral gains in ARGoS may not survive noise. Report T4 as a simulation-only result (c) | [S-LL-6] | partial (abstract only. No open full text found) |
| exploiting-clusters-iros-2015 | Hecker, Carmichael, Moses. Exploiting clusters for complete resource collection in biologically-inspired robot swarms. IROS 2015 pp. 434 to 440 (Moses lab. Lu not an author) | Per GCFA: "The time to collect the first 88% of the resources is approximately half of the time to collect the last 12%" (GCFA PDF p. 2) | Not read | Supports the regime point: the map pays in the sparse tail, which respawn removes (c) | [S-LP-1] | partial (cited claim only) |
| swarm-foraging-review-2020 | Lu, Fricke, Ericksen, et al. Swarm Foraging Review: Closing the Gap Between Proof and Practice. Current Robotics Reports 1:215 to 225, 2020 | Contrasts bio-inspired and theory-driven foraging (listing) | Not read | Related-work citation for the report (c) | [S-LP-8] | partial (listing only) |

## 2. Future-work themes across papers

```
Figure 1. Where each paper's gain appears (time to collect all) vs our score window

 collected %   0 ........ 60 ........ 80 ........ 100
 GCFA                                 [gain: last 20 %]        S-LP-1
 ARPC                       [gain from 60 % or 80 %]           S-LP-2 p. 9
 ARPC   [conclusion: "not limited to the endgame"] [CONFLICT]  S-LP-2 p. 12
 MDBSA        [12 min count: Centralized <= DDSA]              S-LP-3
 ours         [12 min, 256 items always present (respawn)]     D-007
```

- Caption: Figure 1 places each paper's measured gain on the collection axis. Why: the map methods pay in the sparse tail, and our score window may not contain one (inference).

Table 1. Themes

| # | Theme | Papers that state it | What it means for us (inference) |
| --- | --- | --- | --- |
| T-A | Visited-space memory pushes robots away from clusters | GCFA limits (PDF p. 7) [S-LP-1]. ARPC Powerlaw limit (Sec. 6.2) [S-LP-2] | Two lab methods lose on a clustered layout for the same reason. Our §3.1 logs a point every `rec_period` while searching, so cells around a find become visited anyway. GCFA kept site fidelity and pheromone (PDF p. 3) and still lost the last 10 % on Clustered. So "keep fidelity and pheromone" alone (survey §5, C1) may not prevent it |
| T-B | Server cost is claimed, not measured | GCFA: future work on cells vs computation cost (PDF p. 7) [S-LP-1]. ARPC: no runtime numbers [S-LP-2] | Our §5.2 benchmark and `queries.csv` are the open slot. This is the strongest report lever |
| T-C | Recording rate and memory size are untuned | GCFA: "left for future work" (PDF p. 3) [S-LP-1]. ARPC fixes ρ = 2 s, λ = 50 [S-IS-4] | A `rec_period` sweep answers it with cost and score side by side |
| T-D | Central delivery and congestion limit swarms | MDBSA (p. 231) [S-LP-3]. MPFA trade-off (Sec. VII) [S-LP-5]. Thesis goal [S-LL-5] | With one nest and 24 robots, nest collisions may cap any search gain |
| T-E | Simulation only, real-world noise next | MDBSA (p. 232) [S-LP-3]. ICRA 2019 [S-LL-6]. CPFA (p. 67) [S-LL-1]. ARPC "dynamic targets, communication limits, and energy constraints" [S-LP-2] | State as a limit. Our respawn is already a dynamic-target setting |
| T-F | Gain grows with arena size | GCFA Table II (581 s to 1267 s) [S-LP-1]. ARPC slope 404 s vs 519 s per +2 m side [S-IS-4] | At 10 × 10 m the score gain may be small. An arena-size sensitivity set would show the trend |

## 3. Improvement ideas ranked (top 10)

- Rank = expected score effect first, then report value. All effects are inference. No source measures our setting.
- Cost uses DESIGN §6.3: one S2 candidate = 10 seeds × 3 distributions = 30 runs, about 3 min at about 6 s per run (inference from the smoke).
- Design fit: "inside design" = already a tuning candidate. "New D-row" = needs a `DECISIONS.md` row before S2 pre-registration.

Table 2. Ranked ideas

| Rank | Idea | Lever | Expected effect (inference) | Cost to try | Design fit | Source |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Keep space near a find available: minimum cells within r of a pickup get a short `T_stale` (or are never marked), whatever points the robot logged there | (a) | Avoids the cluster failure of GCFA and ARPC. Should matter most on Clustered and Powerlaw. Dropping only the pickup point would do little, because `rec_period` points already cover the area | 1 candidate, 30 runs | New D-row: changes §3.1 steps 1 and 3 | [S-LP-1], [S-LP-2] |
| 2 | Spiral search at the map target (T4). Sourced gap g = 0.18 m (MDBSA p. 228). 2 × 0.13 m is our inference | (a) | Covers the target without overlap. GCFA and ARPC both spiral at the target | 1 candidate, 30 runs | Inside design (T4, round 3) | [S-LP-1], [S-IS-4], [S-LP-3] |
| 3 | `q_map` > 0 so the map fires while pheromones are active | (a) | More departures use the map. Risk: fewer pheromone trips on Clustered | 2 candidates, 60 runs | Inside design (round 2) | [S-LP-1] (map used only in uninformed walk) |
| 4 | Target a block of 2 × 2 or 3 × 3 minimum leaves per trip, visited in a fixed order, as in GCFA Algorithm 1 | (a) | Longer useful search per trip, fewer empty returns. Caution: MDBSA lost 25 % at 64 regions, but it blames collisions near the centre (p. 231), not target size | 1 to 2 candidates, 30 to 60 runs | New D-row (new tactic) | [S-LP-1], [S-LP-3] |
| 5 | Report the §5.2 benchmark as the answer to GCFA's stated future work (cells vs computation cost) | (b), (c) | No score effect. Fills a gap both lab papers leave open | 0 simulation runs. Benchmark only | Inside design (G1) | [S-LP-1], [S-LP-2] |
| 6 | Sweep `rec_period` (2, 8, 25 s), report points uploaded and score together | (b), (c) | Fewer points lower server cost. Score may drop slowly. Answers GCFA's "left for future work" | 2 candidates, 60 runs | New D-row (`rec_period` is fixed in Table 6) | [S-LP-1] |
| 7 | Add collision time per run as a mechanism column. The vendor already writes `collisions_in_seconds` in its `iAntTagData.txt` file (`research/baseline_code_map.md` line 360) | (c) | Explains a null result if nest congestion caps the gain, as MDBSA found for central delivery | Parsing only, 0 new runs | New D-row (adds a `runs.csv` column, so back to MVP1 for that column) | [S-LP-3] |
| 8 | Plot time to each 10 % milestone and the per-minute curve beside the 12 min count | (c) | Makes our figures comparable to GCFA Fig. 8 to 10 and ARPC Fig. 4 | 0 runs (`forage_per_minute.csv` exists) | Inside design | [S-LP-1], [S-IS-4] |
| 9 | Arena-size sensitivity set (for example 14 × 14 and 16 × 16 m, same density) | (c) | Both lab papers show a larger gain in larger arenas. Tests whether ours grows too | 2 arms × 3 distributions × 2 sizes × 10 seeds = 120 runs | New D-row (new set) | [S-LP-1], [S-IS-4] |
| 10 | No-respawn sensitivity set (F2-b) to reach the sparse tail where the papers gain | (c) | Shows whether a null 12 min result comes from respawn. Never a headline number | 300 runs for 50 seeds | New D-row. Conflicts with D-007 for the headline. DESIGN §2 F2 already lists it as a stretch | [S-LP-1] ("≤ 10 %" regime), exploiting-clusters claim |

Not ranked (conflicts with frozen decisions):

- Re-tune give-up or site-fidelity rates for map-target robots: touches the 7 CPFA parameters (D-009). Allowed only with an equal budget for the baseline.
- Extra nests or moving depots (MPFA line): the assignment names one collection zone of radius 0.25 m [S-IS-1]. So one nest is inference from the task text.

## Selection log

| Entity | Decision | Rule |
| --- | --- | --- |
| gcfa-visitation-grid | kept, verified | in scope item 1. PDF pp. 2 to 8 read |
| grid-based-complete-ant-2025 | kept, partial | in scope item 1. Citation only. Not found again |
| arpc | kept, verified | in scope item 2. Survey page images. Future-work line summary only |
| cpfa-beyond-pheromones | kept, verified | in scope item 3. Reused from `lu_lineage.md` |
| mpfa-2016 | kept, partial | in scope item 4. Fetch summary of arXiv HTML |
| dynamic-depots-2018, transport-network-2020, phd-thesis-2019 | kept, partial | in scope item 4. Full texts blocked (login, HTTP 403) |
| mdbsa-spiral-2023 | kept, verified | in scope item 5. All pages read |
| cpfa-vs-ddsa-icra-2019 | kept, partial | in scope item 5. Abstract only |
| exploiting-clusters-iros-2015 | kept, partial | Moses lab, cited by GCFA for the tail claim. Lu not an author |
| swarm-foraging-review-2020 | kept, partial | Lu first author. Listing only |
| Collision_Free_CPFA paper | not found | one web search returned nothing. The lab research page lists no coverage or search project [S-LP-6]. The vendor clone has no `.md` file citing a paper (grep for "paper", "doi", "arxiv") |
| Robot chains, ICRA 2021 and 2022 | rejected | delivery-network topic, not search. Covered in `lu_lineage.md` L6, L7 |
| Misleading pheromone papers (ICCCR 2024, UR 2024, TAROS 2024, "TAROS2025" label) | rejected | security topic, not search. Covered in `lu_lineage.md` U1 to U3 |
| LLM-Foraging, arXiv 2605.01461 | rejected | Gazebo, decentralized language-model agents. No server map |
| NEAT foraging 2025, MAAC reinforcement learning 2021 | rejected | learned controllers, not search memory. Listing only |
| Aggarwal et al. "Ignorance is not bliss", IROS 2019 | not read | Moses lab analysis of central-place foraging, seen only as MDBSA ref [26]. Lu not an author |

## open_questions:

- GCFA run count: 30 in Table I, 50 in the text (PDF pp. 4 to 5). Which is right?
- GCFA grid size n is never given as a number. A fair "vs student grid" benchmark needs it. Ask the professor or the author.
- grid-based-complete-ant-2025: full text not found. Is "ANT-2025" a venue we can look up, or the paper the professor shared?
- ARPC [CONFLICT] within one source: the conclusion (p. 12) claims early gains. The p. 9 text puts the gain after 60 % or 80 %. Re-checked on page images this pass. Fig. 4 significance marks would decide it for our window.
- ARPC τ is 1 % of arena area in Sec. 4.1 and 0.5 % in the experiments. τ also names the spiral radius.
- Does the professor count respawn (D-007) as the "dynamic targets" of ARPC's future work, or do they mean moving targets?
- Dynamic depots 2018, DOI 10.1007/s10514-017-9693-2: Springer login. Reading it would give its stated limits.
- PhD thesis 2019: PDF returned HTTP 403. Its conclusion chapter would give Lu's own future-work list. Access needed (main session, `check/access-needed.md`).
- ICRA 2019, DOI 10.1109/ICRA.2019.8794240: no open full text. It holds the only CPFA vs spiral comparison on Lu's side.
- Collision_Free_CPFA: is there a paper behind the repo? Ask the professor which paper describes the baseline changes.
- Does a 12 min run with respawn ever reach a sparse tail? Answer from S1 per-minute curves (main session run, not this agent).
- Does nest congestion limit our arm? Needs a collision-time column (idea 7) and a D-row.

## Sources

Reused rows, copied so every ID resolves here:

[S-IS-1] Final Project 2: Informed Search for Foraging Robot Swarms | local: `submodule_project/docs/Autonomous_Mobile_Robot_Programming_Final Project 2.pdf` | published: course handout, undated | accessed: 2026-11-12 | type: official | note: all 3 pages read in the survey
[S-IS-2] A Visitation Grid for Complete Coverage Foraging in Robot Swarms | https://arxiv.org/abs/2605.21947 | published: 2026-05-21, arXiv v1 | accessed: 2026-11-12 | type: paper | note: PDF pages 3 to 6 read as page images in the survey
[S-IS-3] Grid-based complete resource foraging for robot swarms | no URL found | published: "ANT-2025" as printed in reference [10] of S-IS-4 | accessed: 2026-11-12 | type: paper | note: citation entry only
[S-IS-4] Adaptive Repulsive Pheromone Clustering for Foraging Robot Swarms | https://arxiv.org/abs/2608.16822 | published: 2026-08-17, arXiv v1 | accessed: 2026-11-12 | type: paper | note: PDF pages 4 to 12 read as page images in the survey
[S-LL-1] Beyond pheromones: evolving error-tolerant, flexible, and scalable ant-inspired robot swarms | https://cs.unm.edu/~joel/cs351/paper/BeyondPheromones.pdf | published: 2015-02-15, Swarm Intelligence 9:43 to 70 | accessed: 2026-11-11 | type: paper | note: pages 1, 2, 23 to 25 read as page images in lu_lineage.md
[S-LL-3] A Scalable and Adaptable Multiple-Place Foraging Algorithm for Ant-Inspired Robot Swarms | https://arxiv.org/abs/1612.00480 | published: 2016-12-01 | accessed: 2026-11-11 | type: paper | note: abstract page via fetch summary
[S-LL-4] Multiple-place swarm foraging with dynamic depots | https://link.springer.com/article/10.1007/s10514-017-9693-2 | published: 2018, Autonomous Robots 42(4) | accessed: 2026-11-11 | type: paper | note: search snippet only. PDF redirected to a login again on 2026-11-16
[S-LL-5] An Efficient Multiple-Place Foraging Algorithm for Scalable Robot Swarms | https://digitalrepository.unm.edu/cs_etds/100 | published: 2019-07-15 | accessed: 2026-11-16 | type: official | note: repository record page via fetch summary. PhD dissertation
[S-LL-6] Comparing Physical and Simulated Performance of a Deterministic and a Bio-inspired Stochastic Foraging Strategy for Robot Swarms | https://api.openalex.org/works/doi:10.1109/ICRA.2019.8794240 | published: 2019-05, ICRA 2019 pp. 9285 to 9291 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex abstract
[S-LL-7] A Bio-Inspired Transportation Network for Scalable Swarm Foraging | https://api.openalex.org/works/doi:10.1109/ICRA40945.2020.9196762 | published: 2020-05, ICRA 2020 pp. 6120 to 6126 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex abstract

New sources:

[S-LP-1] A Visitation Grid for Complete Coverage Foraging in Robot Swarms | https://arxiv.org/pdf/2605.21947 | published: 2026-05-21, arXiv v1 | accessed: 2026-11-16 | type: paper | note: PDF pages 2 to 8 read as page images. Section text also via a fetch summary of https://arxiv.org/html/2605.21947
[S-LP-2] Adaptive Repulsive Pheromone Clustering for Foraging Robot Swarms | https://arxiv.org/pdf/2608.16822 | published: 2026-08-17, arXiv v1 | accessed: 2026-11-16 | type: paper | note: PDF pages 9 and 12 read as page images. Section 4.1 and 6.2 lines via a fetch summary of https://arxiv.org/html/2608.16822
[S-LP-3] Adaptive Multiple Distributed Bidirectional Spiral Path Planning for Foraging Robot Swarms | https://par.nsf.gov/servlets/purl/10591790 | published: 2023, CRV 2023 pp. 225 to 232 | accessed: 2026-11-16 | type: paper | note: ScholarWorks accepted manuscript, all 9 PDF pages read as page images
[S-LP-4] Adaptive Multiple Distributed Bidirectional Spiral Path Planning for Foraging Robot Swarms: NSF PAR record | https://par.nsf.gov/biblio/10591790 | published: 2023-06-01 | accessed: 2026-11-16 | type: official | note: record page via fetch summary. DOI and pages
[S-LP-5] A Scalable and Adaptable Multiple-Place Foraging Algorithm for Ant-Inspired Robot Swarms | https://arxiv.org/html/1612.00480v1 | published: 2016-12-01 | accessed: 2026-11-16 | type: paper | note: fetch summary of the HTML full text
[S-LP-6] Qi Lu: Research | https://sites.google.com/view/qilu/research | published: undated | accessed: 2026-11-16 | type: official | note: fetch summary. No coverage or informed-search project listed
[S-LP-7] An Efficient Multiple-Place Foraging Algorithm for Scalable Robot Swarms: full text | https://digitalrepository.unm.edu/cgi/viewcontent.cgi?article=1100&context=cs_etds | published: 2019 | accessed: 2026-11-16 | type: paper | note: HTTP 403, not read
[S-LP-8] Swarm Foraging Review: Closing the Gap Between Proof and Practice | https://aminer.org/pub/621943ab5aee126c0fda5a1c/swarm-foraging-review-closing-the-gap-between-proof-and-practice | published: 2020, Current Robotics Reports 1:215 to 225, DOI 10.1007/s43154-020-00018-1 | accessed: 2026-11-16 | type: aggregator | note: search snippet of the listing only
[S-LP-9] Web search "Gonzalez Lu grid-based complete resource foraging robot swarms ANTS 2025" | https://arxiv.org/abs/2605.21947 | published: live index | accessed: 2026-11-16 | type: aggregator | note: only the arXiv GCFA paper and its mirrors returned
