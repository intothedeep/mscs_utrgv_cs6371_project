# Informed search for central-place foraging algorithm (CPFA) swarms: survey

- Task tag: IS
- Accessed: 2026-11-12
- Purpose: methods to store robots' visited locations so the central server finds unvisited regions fast. Final Project 2.
- Task file: `../docs/Autonomous_Mobile_Robot_Programming_Final Project 2.pdf` (read in full).
- Reused research: `01_pheromone/research/lu_lineage.md` (S-LL-*), `research/lu_qi.md` (S-LQ-*). Reused IDs are copied into Sources.
- Status: complete, one pass. About 24 web search and fetch calls (no budget set. Skill default is 15), plus local PDF and XML reads.
- Abbreviations: central-place foraging algorithm (CPFA), distributed deterministic spiral algorithm (DDSA), density-based spatial clustering of applications with noise (DBSCAN), Adaptive Repulsive Pheromone Clustering (ARPC), Grid-Based Complete Foraging Algorithm (GCFA, as expanded in G1), genetic algorithm (GA). GPFA is kept as printed in G3.

## Summary counts

- Rows kept: 31 (paper rows 3, structure rows 10, behaviour rows 7, fairness facts 8, candidates 3)
- Rows rejected: 3 (selection log)
- Sources: 13 (11 new S-IS, 2 reused S-LL)
- Unverified: 3 rows (D7, D9, D10)

## 0. Task facts (from the assignment PDF)

Source: assignment PDF [S-IS-1], read in full (3 pages).

| Fact | Value |
| --- | --- |
| Cost example | 200 robots, 100 remembered points each, 20 trips: 400,000 points to scan per robot return |
| Professor's hint 1 | The MS student's grid: cells get large when the arena is large |
| Professor's hint 2 | Cluster the points, clusters of different sizes |
| Professor's hint 3 | Record fewer points, still tell visited from unvisited |
| Ultimate goal | Implement the organizing algorithm. "You can also think about other methods to improve the search strategy" |
| Score setting | 10 × 10 m arena, collection zone radius 0.25 m, 256 resources, 24 robots, 12 min |
| Distributions | Random, Powerlaw, Clustered. 50 runs each |
| Comparison | Box plots vs the original CPFA. Percentage improvement in collected resources. Teams ranked by score |
| Baseline code | `MARSLab-UTRGV/Collision_Free_CPFA` (pinned in `02_informed_search/README.md`) |

```
robot returns ──> server ──> pick unvisited region ──> robot searches there
                    │
   scan cost:  list of points  O(N), N up to 400,000   (the problem)
               grid counts     O(cells)                (MS student, fixed n × n)
               clusters        O(clusters)             (ARPC, variable size)
```

## 1. The MS student's grid paper (question 1)

**Found: one method, two write-ups, by Arturo Gonzalez and Qi Lu (UTRGV).**

- G1 (arXiv 2026) is the full text we read. G2 (cited as "ANT-2025") is only a reference entry. We did not find G2 online.
- G1 and G2 are the same method. Evidence: G3 Table 2 "GPFA" values (394.0, 680.7, 313.7, 774.8, 298.6, 900.8) equal G1 Table III "GCFA" values. G3 Fig. 3 legend prints "GCFA", its text says "GPFA" [S-IS-2], [S-IS-4].
- G3 (ARPC) is a third MARS lab paper. It already does the professor's hint 2 (variable-size clusters).
- Method names GCFA, GPFA and ARPC are kept as printed. G1 expands GCFA as "Grid-Based Complete Foraging Algorithm". GPFA is not expanded in what we read. ARPC = Adaptive Repulsive Pheromone Clustering.

| # | Paper | Venue | Method | Numbers | Source | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| G1 | Gonzalez, Gao, Zhang, Lu. A Visitation Grid for Complete Coverage Foraging in Robot Swarms (method: GCFA) | arXiv 2605.21947, 2026-05-21. Comment: "The 23rd International Conference on Ubiquitous Robots" | Arena split into an n × n grid "based on the size of the arena and the memory capacity of the server". Server keeps only a counter per cell, O(n²) memory. Robot keeps a first-in first-out queue of 20 positions, logged every 25 s, uploaded on return. When the robot was in uninformed walk, the server picks the 3 × 3 block with the minimum summed count (Algorithm 1, line 15: deterministic minimum). Robot visits a random point in each of the 9 cells, counter-clockwise, spiral search in each. Then correlated random walk until find, or give up with probability p. Site fidelity and pheromone stay as in the CPFA | ARGoS, 16 robots, 14 × 14 m (arena test 8 to 16 m), 16 to 80 resources. Metric: time to collect all. Random, 48 resources: about 33 % less time. Powerlaw: about 14 % less. Clustered: "no difference". 10 × 10 m, Random, 48 resources: 1541 s vs CPFA 2165 s (Table II). Last 10 %, Random: 900.8 s vs 1755.2 s (Table III). Last 10 %, Cluster: 680.7 s vs 593.5 s (worse). Fig. 8 (Random): bars for 10 % to 70 % look about equal for both (read by eye) | [S-IS-2] | verified (pages 3 to 6 read as page images). n not given as a number. Fig. 3a shows a 12 × 12 m arena with about 12 × 12 cells (read by eye). Runs: Table I says 30, text says 50 |
| G2 | Gonzalez, Lu. Grid-based complete resource foraging for robot swarms (called GPFA by G3) | "ANT-2025", as printed in reference [10] of G3 | G3: "relying solely on visitation frequency within a fixed 3×3 grid" | G3: GPFA had "49% and 35% improvements over CPFA" in the last two 10 % intervals | [S-IS-3] | partial (citation only. Paper not found) |
| G3 | Pena-Caballero, Tarawneh, Lu. Adaptive Repulsive Pheromone Clustering for Foraging Robot Swarms (ARPC) | arXiv 2608.16822, 2026-08-17. Comment: submitted to the 18th International Symposium on Distributed Autonomous Robotic Systems (DARS) | Robot records a "repulsive pheromone" point every ρ = 2 s, at most λ = 50, oldest overwritten. Upload on return. Nest every 5 s: (1) absorb new points into clusters whose radius covers them, (2) density-based spatial clustering of applications with noise (DBSCAN) on the rest, ε = α + offset, α = 0.75 m, minPts = 2, (3) merge overlapping clusters if an area test holds (Eq. 1, τ). Cluster = center + radius. Target: "up to 1000 random candidate locations", first one outside all clusters. Then spiral search, then random search. Site fidelity and pheromone kept, chosen first by Poisson probabilities | ARGoS, 16 robots, 14 × 14 m, 50 runs. Better than CPFA and GPFA in "8 out of 15" Experiment I settings. Last 10 %, Random: 703.7 s vs GPFA 900.8 s (+21.89 %). Cluster: 593.8 vs 680.7 s (+12.78 %). Powerlaw: 1021.1 vs 774.8 s (−31.79 %). Text, p. 9: Clustered and Powerlaw advantage starts "at the point where 60%" is collected. Random: "once 80%". Powerlaw: "marked decline occurs early (10%40% completion)", isolated resources fall "inside repulsive zones". Conclusion, p. 12: "the performance gains are not limited to the endgame", ARPC "accelerates initial discovery". Fig. 4 shows significance marks at early milestones, mainly Clustered (read by eye). Abstract: about 10 % early, up to 60 % late. Arena slope: 404 s vs 519 s per +2 m side (p. 12). Fig. 2: a 10 × 10 m run, clusters cover most of the arena by 10 min (read by eye) | [S-IS-4] | verified (pages 4 to 12 read as page images). Server cost not measured. τ is 1 % of arena area on p. 6, 0.5 % on p. 8. Early-gain claims conflict between p. 9 and p. 12 |

Read for our score (inference):

- Both papers measure **time to collect all** of 16 to 80 resources. Our score is **count collected in 12 min** of 256.
- GCFA gains appear late (last 20 %). Its early milestones look equal to the CPFA (Fig. 8, by eye).
- ARPC is mixed early: its conclusion claims faster "initial discovery" and the abstract about 10 % early. Its own p. 9 text puts the advantage after 60 % or 80 %, and Powerlaw drops early (10 to 40 %).
- Our setting is denser: 24 robots, 10 × 10 m, 256 resources. A 12 min run may stay in the early regime. There, only ARPC claims a gain, and it can lose on Powerlaw.
- Each lab method loses on one distribution: the grid on Clustered, ARPC on the Powerlaw endgame.
- G1 reports 1541 s to collect 48 resources at 10 × 10 m with 16 robots [S-IS-2]. That is longer than our 720 s, for far fewer resources.
- Search terms used: "CPFA informed search grid unvisited foraging robot swarm", "Qi Lu UTRGV foraging swarm unvisited regions grid 2025", "Grid-based complete resource foraging robot swarms ANTS 2025", OpenAlex "foraging robot swarm unvisited". No search used "ANT-2025" as printed.

## 2. Data structures for visited and unvisited space (question 2)

Symbols: N = recorded points, C = cells, leaves or clusters, K = random candidates tried.

- Cost cells marked "inference" are our reading of the structure. No source states them for this task.
- "Expected effect on score" is inference in every row. No source reports a 12 min count at 24 robots, 10 × 10 m, 256 resources.

| # | Method | Memory | Insert cost | "Find unvisited region" cost | Large-arena behaviour | Expected effect on score (inference) | Source | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | Flat list of all visited points (the problem) | O(N), N up to 400,000 in the example | O(1) append | Scan all N points per candidate | N grows with robots × trips | Baseline. Slow server, no score gain by itself | [S-IS-1] | verified |
| D2 | Uniform grid with visit counts (GCFA) | O(n²) counters | O(1) per point (cell index) | Scan for the minimum 3 × 3 block sum: O(n²) (inference) | Fixed n: cells get large in big arenas, per the professor | Gains only after about 80 % collected in their tests. Loses on Clustered | [S-IS-1], [S-IS-2] | verified |
| D3 | Occupancy bitmap: 1 visited bit per cell, cell about one sensing footprint | O(cells) bits | O(1) | Breadth-first search outward from the nest or robot to the first 0 bit: O(cells) worst (inference) | Memory grows with arena area at a fixed cell size (inference) | Fine enough to tell visited from unvisited in 10 × 10 m (inference) | Occupancy grids as the base map for frontiers: [S-IS-8] | partial (the structure is ours. Source is a snippet only) |
| D4 | Region quadtree of visits (visited flag or count per leaf) | O(leaves). Uniform regions stay one large leaf | O(depth) descent, split a leaf on demand (inference) | Best-first descent to the nearest low-count leaf. About O(depth) only if each node stores a subtree summary (minimum count or "has unvisited"). Without it, a scan of all leaves (inference) | Cell size adapts. Large empty or fully visited areas stay one node. Depth grows with log₂(arena side / smallest cell), so slowly with the arena (inference) | Same targets as a fine grid in 10 × 10 m. Answers the professor's large-arena critique (inference) | Region quadtree: "four equal quadrants", splits "as long as there is interesting data", height depends on the data: [S-IS-5] | partial (encyclopedia page. Costs are inference) |
| D5 | k-d tree over visited points | O(N) | O(log n) average, O(n) worst | Nearest visited point: O(log n) average, O(n) worst. Test a candidate as "unvisited" if that distance > r (inference) | Fine for any arena. N still grows unless points are thinned | Fast test for random candidates. Does not reduce N (inference) | Complexity table: [S-IS-6] | partial (encyclopedia page) |
| D6 | Batch density clustering (DBSCAN) into disks (ARPC) | O(C) disks + recent unclustered points | DBSCAN: average O(n log n) with an R*-tree index, one O(log n) region query per point | Up to K = 1000 random candidates, each tested against all C disks: O(K · C) (inference from the method) | Variable-size disks. Arena slope 404 s vs 519 s per +2 m side, vs the grid | Endgame gains on Random and Clustered. Powerlaw endgame worse than the grid | DBSCAN cost: [S-IS-7]. ARPC: [S-IS-4] | verified (DBSCAN p. 229 read as page image. ARPC pages read) |
| D7 | Online leader (sequential) clustering: a point joins the nearest disk within radius r, else starts a new disk | O(C) | O(C), or O(1) with a grid hash of disk centers (inference) | Same candidate test as D6 (inference) | Disk count follows the visited area, not the arena (inference) | Like ARPC without the 5 s batch DBSCAN (inference) | [UNVERIFIED] no source read in this pass | unverifiable |
| D8 | Frontier-based exploration: go to the boundary between explored and unexplored cells | Occupancy grid (D3) | O(1) per cell update | Nearest frontier: search over the grid (inference) | Single-robot origin. Many robots may pick the same frontier without reservation (inference) | Shorter trips if the nearest frontier replaces the CPFA's "random location close to the boundaries" (inference) | Yamauchi 1997, CIRA, pp. 146 to 151: [S-IS-8] | partial (search snippet only) |
| D9 | Voronoi split of unvisited space among robots | O(robots) sites | Rebuild per return (inference) | Each robot owns its cell's unvisited area (inference) | Scales with robots, not arena (inference) | Cuts overlap between robots (inference) | [UNVERIFIED] no source read | unverifiable |
| D10 | Geohash (interleaved-bit cell key) | Same as D2 or D4 | O(1) key | Prefix of the key = a coarser cell, like a quadtree level (inference) | Same as D4 (inference) | Implementation detail of D4, not a separate method (inference) | [UNVERIFIED] no source read | unverifiable |

## 3. Search behaviour improvements (question 3)

No source reports collected count in 12 min at 24 robots, 10 × 10 m, 256 resources. The effect column is inference.

| # | Behaviour | What the source says | Expected effect in a 12 min, 10 × 10 m run (inference) | Source | Verification |
| --- | --- | --- | --- | --- | --- |
| B1 | Spiral search at the target (DDSA-style) | Distributed deterministic spiral algorithm (DDSA) extends a single-searcher spiral to swarms. DDSA beats the CPFA in simulation. Outdoors the CPFA is as good or better. G1 and G3 both spiral at the chosen target | Positive. Spiral covers a target region without overlap. Simulation favors it | [S-IS-9], [S-LL-6], [S-IS-2], [S-IS-4] | partial (DDSA: listing and snippet only) |
| B2 | Repulsion from visited areas | ARPC: robots avoid clustered "repulsive pheromone" areas in informed search. Can push isolated resources into repulsive zones (Powerlaw) | Positive on Random and Clustered endgame. Risk on Powerlaw | [S-IS-4] | verified |
| B3 | Frontier or nearest-unvisited assignment | Go to the boundary of the explored area | Positive if it replaces the CPFA's random target "close to the boundaries" with a nearer unvisited one: shorter trips | [S-IS-8], CPFA target rule in [S-IS-2] | partial |
| B4 | Lévy walk | A collective Lévy walk with a potential field from local communication. A variant adapts the Lévy exponent to local target density, "useful when targets are distributed in patches". No numbers on the page read | Unclear. Long Lévy steps meet walls in a 10 × 10 m arena. Needs robot-to-robot communication the CPFA does not use | [S-IS-10] | partial (proceedings page, no numbers) |
| B5 | Informed random walk with less overlap | CPFA informed search decays to uninformed (parameter `RateOfInformedSearchDecay`). The CPFA uses a correlated random walk | Small. Overlap is the problem the server map already targets | [S-LL-1], [S-IS-11] | partial |
| B6 | Give-up and site-fidelity tuning (genetic algorithm, GA) | A GA tunes 7 CPFA parameters. A strategy evolved for clustered resources doubles efficiency there vs one evolved for random | Likely the largest lever in a dense 12 min run, where pheromone and site fidelity dominate | [S-LL-1] | verified (in lu_lineage) |
| B7 | Target reservation | Not in G1 or G3. G1 picks the deterministic minimum block, so robots returning close in time may get the same block | Positive with 24 robots: spreads targets | Algorithm 1 in [S-IS-2] | inference |

## 4. Fair comparison with the original CPFA (question 4)

| Fact | Value | Source |
| --- | --- | --- |
| CPFA parameters are evolved per resource distribution | GA-evolved sets differ by distribution | [S-LL-1] |
| Baseline repo, Random set | `RateOfSiteFidelity` 14.1514, `ProbabilityOfReturningToNest` 0.01476 (`Random_CPFA_r24_tag256_10by10.xml`) | [S-IS-11] |
| Baseline repo, Clustered set | `RateOfSiteFidelity` 1.3763, `ProbabilityOfReturningToNest` 0.01894 (`Clustered_CPFA_r64_tag512_16by16.xml`) | [S-IS-11] |
| 10 × 10 m files in the repo | Only `Random_CPFA_r24_tag256_10by10.xml`: 256 resources, 4 robot groups of `quantity="6"` | [S-IS-11] |
| Nest radius in that file | `NestRadius="0.5"`. The assignment says 0.25 m | [S-IS-11], [S-IS-1] |
| Time limit in that file | `MaxSimTimeInSeconds="1800"`. The assignment needs 12 min | [S-IS-11], [S-IS-1] |
| Powerlaw file | None found by name. `FoodDistribution="1"` or `"2"` appears only in the Clustered file and two `*Example.xml~` files | [S-IS-11] |
| Do G1 and G3 state their CPFA parameters? | No | [S-IS-2], [S-IS-4] |

Fair-comparison rules we propose (inference):

1. Same CPFA parameter set in both arms, per distribution.
   - Blocker: the repo has no Powerlaw set. Its Clustered set comes from a 16 × 16 m, 64-robot, 512-resource file.
   - Ask the professor which set defines "original CPFA" for each distribution at 10 × 10 m. Until then, use one set for both arms and say which.
2. Same seeds, same 720 s limit, same 50 runs, same arena and resource files.
3. Change only the uninformed-search target (and its spiral). Leave site fidelity and pheromone untouched in the main arm.
4. If we re-tune parameters for our method, also re-tune the CPFA with the same budget. Report both. Otherwise the gain mixes tuning with the method.
5. Report the percentage gain in collected resources per distribution, with the median and a 95 % interval.

## 5. Candidate designs for us

Ranked on two axes: fit to task 1 (the professor asked for variable-size regions or fewer points) and expected score effect. All rankings are inference.

```
returning robot ──> [site fidelity / pheromone?] ──yes──> CPFA as is
                              │ no
                              v
                     server map (C1 quadtree | C2 disks)
                              │ nearest unvisited, not reserved
                              v
                     travel ──> spiral search ──> correlated random walk
```

| Rank | Design | Why | Risk |
| --- | --- | --- | --- |
| 1 | C1: region quadtree visit map + nearest-unvisited target + reservation + spiral | Directly answers "cells get large in big arenas": cells split only where robots went. Memory O(leaves), query about O(depth). Nearest target shortens trips, which a 12 min count rewards. Reservation spreads 24 robots. Keeps CPFA site fidelity and pheromone, so Clustered should not lose like GCFA | Gain may be small if the run never reaches the endgame. Quadtree code is new |
| 2 | C2: online leader clustering into disks (ARPC without batch DBSCAN) + nearest uncovered candidate | Fewer recorded points: one disk per visited patch. O(C) or O(1) insert. Simpler than ARPC's four stages. Close to the professor's hint 2 | ARPC already published it. ARPC is the only lab method claiming early gains, but it drops on Powerlaw early (10 to 40 %) and in the endgame. Disk overlap test cost grows with C |
| 3 | C3: behaviour layer on top of C1: tuned give-up probability and nearest-first targets, fair re-tune of both arms | Parameters likely dominate a dense 12 min run [S-LL-1] | Not a server structure. Fairness needs the same tuning budget for the CPFA |

## Selection log

| Entity | Decision | Rule |
| --- | --- | --- |
| G1 Visitation Grid (arXiv 2605.21947) | kept | the MS student's grid method. Pages 3 to 6 read |
| G2 Grid-based complete resource foraging (ANT-2025) | kept as partial | same method as G1. Citation only |
| G3 ARPC (arXiv 2608.16822) | kept | MARS lab, variable-size clusters. Pages 4 to 12 read |
| Quadtree, k-d tree pages | kept as partial | encyclopedia pages. Used for structure and complexity only |
| DBSCAN, KDD-96 | kept | first-party paper, p. 229 read |
| Yamauchi 1997 frontier exploration | kept as partial | snippet only. PDF redirected, not followed (budget) |
| DDSA, Fricke et al. IROS 2016 | kept as partial | listing only. core.ac.uk PDF returned HTTP 403 |
| Nauta et al. ECAI 2020 Lévy walk | kept as partial | proceedings page, no numbers |
| López-Incera 2020, Katada 2022 and 2023 Lévy studies | rejected | search snippet only. Not fetched (budget) |
| Hecker, Carmichael, Moses "exploiting clusters" IROS 2015 | rejected | search did not find it. Named only in a search summary |
| Leader clustering, Voronoi, geohash sources | not found | not searched (budget). Rows marked [UNVERIFIED] |
| OpenAlex "foraging robot swarm unvisited" | rejected | 5 visible results, none from UTRGV or Qi Lu |

## open_questions:

- G2: full text not found. Search with "ANT-2025" as printed, or ask the professor for the shared PDF. Is it the paper he shared?
- Grid shape: G3 says "a fixed 3×3 grid". G1 says an n × n grid with a 3 × 3 block. Numeric n not given. This decides what "better than the grid" means.
- G1: run count is 30 in Table I and 50 in the text.
- G1: abstract says "probabilistically", Algorithm 1 takes the minimum.
- G3: τ is 1 % of arena area on p. 6 and 0.5 % on p. 8.
- G3 [CONFLICT] within one source: conclusion (p. 12) and abstract claim early gains. Results text (p. 9) puts the advantage after 60 % or 80 %, and Powerlaw declines early.
- Which CPFA parameter set is "original CPFA" for Powerlaw and Clustered at 10 × 10 m? Repo has no Powerlaw set. Ask the professor.
- Nest radius: repo file 0.5 m vs assignment 0.25 m.
- G3: server computation time not measured. No paper measures the server cost the professor asks about.
- No source reports a fixed-time count at our setting. Every "expected effect on score" cell is inference.
- Whether a 12 min run at 24 robots and 256 resources reaches the 60 % to 80 % point where the lab methods start to gain. Needs a baseline run (main session, owner's order).
- Powerlaw experiment file for 10 × 10 m not found in the baseline repo.
- D7, D9, D10: no source read. [UNVERIFIED].
- DDSA (Fricke et al. 2016) full text: HTTP 403 at core.ac.uk. Access needed (main session, `check/access-needed.md`).
- Yamauchi 1997 full text not read.

## Sources

Reused rows, copied so every ID resolves here:

[S-LL-1] Beyond pheromones: evolving error-tolerant, flexible, and scalable ant-inspired robot swarms | https://cs.unm.edu/~joel/cs351/paper/BeyondPheromones.pdf | published: 2015-02-15, Swarm Intelligence 9:43 to 70 | accessed: 2026-11-11 | type: paper | note: pages 1, 2, 23 to 25 read as page images in lu_lineage.md
[S-LL-6] Comparing Physical and Simulated Performance of a Deterministic and a Bio-inspired Stochastic Foraging Strategy for Robot Swarms | https://api.openalex.org/works/doi:10.1109/ICRA.2019.8794240 | published: 2019-05, ICRA 2019 pp. 9285 to 9291 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex abstract, via lu_lineage.md

New sources:

[S-IS-1] Final Project 2: Informed Search for Foraging Robot Swarms | local: `submodule_project/docs/Autonomous_Mobile_Robot_Programming_Final Project 2.pdf` | published: course handout, undated | accessed: 2026-11-12 | type: official | note: all 3 pages read
[S-IS-2] A Visitation Grid for Complete Coverage Foraging in Robot Swarms | https://arxiv.org/abs/2605.21947 | published: 2026-05-21, arXiv v1 | accessed: 2026-11-12 | type: paper | note: HTML via fetch summary, then PDF pages 3 to 6 read as page images
[S-IS-3] Grid-based complete resource foraging for robot swarms | no URL found | published: "ANT-2025" as printed in reference [10] of S-IS-4 | accessed: 2026-11-12 | type: paper | note: citation entry only
[S-IS-4] Adaptive Repulsive Pheromone Clustering for Foraging Robot Swarms | https://arxiv.org/abs/2608.16822 | published: 2026-08-17, arXiv v1 | accessed: 2026-11-12 | type: paper | note: HTML via fetch summary, then PDF pages 4 to 12 read as page images
[S-IS-5] Quadtree | https://en.wikipedia.org/wiki/Quadtree | published: live page | accessed: 2026-11-12 | type: aggregator | note: fetch summary
[S-IS-6] k-d tree | https://en.wikipedia.org/wiki/K-d_tree | published: live page | accessed: 2026-11-12 | type: aggregator | note: fetch summary
[S-IS-7] A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise | https://cdn.aaai.org/KDD/1996/KDD96-037.pdf | published: 1996, KDD-96 | accessed: 2026-11-12 | type: paper | note: pages 229 and 230 read as page images
[S-IS-8] A Frontier-Based Approach for Autonomous Exploration | https://dblp.dagstuhl.de/rec/conf/cira/Yamauchi97.html | published: 1997, CIRA pp. 146 to 151 | accessed: 2026-11-12 | type: aggregator | note: search snippet only
[S-IS-9] A distributed deterministic spiral search algorithm for swarms | https://researchr.org/publication/FrickeHGTM16 | published: 2016, IROS 2016 pp. 4430 to 4436, DOI 10.1109/IROS.2016.7759652 | accessed: 2026-11-12 | type: aggregator | note: search snippet of the listing only
[S-IS-10] Enhanced Foraging in Robot Swarms Using Collective Lévy Walks | https://ebooks.iospress.nl/pdf/doi/10.3233/FAIA200090 | published: 2020, ECAI 2020, FAIA 325 pp. 171 to 178 | accessed: 2026-11-12 | type: paper | note: fetch summary of the page, no numbers
[S-IS-11] Collision_Free_CPFA experiment files | local: `02_informed_search/vendor/Collision_Free_CPFA/experiments/` at commit `9480f2e3` | published: 2026-05-01 commit | accessed: 2026-11-12 | type: official | note: XML attributes read with grep
