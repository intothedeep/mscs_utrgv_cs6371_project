# Prof. Qi Lu research lineage: milestone papers

- Task tag: LL
- Accessed: 2026-11-11
- Purpose: milestone papers behind the 01_pheromone project. For each: problem, method, why, result, open problems, student opportunity.
- Inputs: `research/lu_qi.md` (S-LQ-*), `01_pheromone/research/pheromone_research.md` (S-PH-*).
- Earlier IDs are reused by name: [S-LQ-n] and [S-PH-n] rows are copied into this file's Sources. New sources get [S-LL-n].
- Status: complete, one pass. About 31 search and fetch calls (no budget set. Skill default is 15).
- Abbreviations: central-place foraging algorithm (CPFA), multiple-place foraging algorithm (MPFA), distributed deterministic spiral algorithm (DDSA), genetic algorithm (GA), density-based spatial clustering of applications with noise (DBSCAN).

## Summary counts

- Milestone rows: 18 (outside 5, PhD and chains 7, UTRGV 6). Verified 5, partial 13
- Sources: 14 new (S-LL), 6 reused (S-LQ, S-PH)
- Unverified: 0 rows. Unreadable full texts: 7 (listed in §2)
- Open questions: 13

## 1. Milestone table

Verification enum: verified (paper or first-party page read), partial (abstract, record page or secondary), inference (author judgment).

### 1.1 Outside milestones the line builds on

| # | Year | Paper | Venue | Problem | Method | Why this way | Result | Open problems | Student opportunity | Source | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| O1 | 1996 | Dorigo, Maniezzo, Colorni. The Ant System: Optimization by a colony of cooperating agents | IEEE Transactions on Systems, Man, and Cybernetics, Part B, 26(1) | Hard combinatorial problems (traveling salesman problem, TSP) need good solutions fast | Ant System (AS): artificial ants build tours. Shared pheromone gives "positive feedback". A greedy heuristic guides early steps | Ant colonies find short paths with no central control | AS solves TSP instances and applies to asymmetric TSP, quadratic assignment and job-shop scheduling. Compared with tabu search and simulated annealing | Pheromone here is a trusted shared memory inside one program. No agent can lie (inference) | Origin of evaporation and reinforcement. Our grid decay is the same idea moved onto a floor (inference) | [S-LL-12] | partial (page 1 and abstract read. Update rule not read) |
| O2 | 2001 | Payton, Daily, Estowski, Howard, Lee. Pheromone Robotics | Autonomous Robots 11(3) 319 to 324 | Coordinate very large numbers of small robots. Unique IDs, point-to-point routing and central state "can be overwhelmed" at that scale | "Virtual pheromone": symbolic messages over simple transceivers on each robot. Messages are tied to robots, not places. Robots relay a discovery and remember its direction | No chemicals. The robot mesh becomes a distributed compute grid and a display of the gradient | Robots form "a distributed array of guideposts" to a resource (scenario, pages 1 and 2) | Every relaying robot is trusted. Any one can inject a false gradient (inference) | Shows that virtual pheromone can live in robots or in the floor. Our testbed stores it in the floor (inference) | [S-LL-13] | partial (pages 1 and 2 read) |
| O3 | 2015 | Hecker, Moses. Beyond pheromones: evolving error-tolerant, flexible, and scalable ant-inspired robot swarms | Swarm Intelligence 9:43 to 70 | Robot swarms must work outside the lab. They need error tolerance, flexibility and scalability. No system had all three in one framework | Central-place foraging algorithm (CPFA) modeled on seed-harvester ants. A genetic algorithm (GA) tunes 7 parameters (memory, communication, movement). Tested in simulation and on up to 6 iAnt robots | Tune a fixed set of ant behaviors, not low-level controllers. "We make no attempt to evolve low-level controllers" | Evolved strategy doubles efficiency on clustered resources vs a strategy evolved for random resources. More pheromone use when resources are clustered and sensing is reliable. Larger swarms disperse more | Paper names: more complex environments, more robot error sources, larger physical swarms, real-time rule adaptation. No adversary is modeled (inference) | Use the CPFA as the honest baseline. Ask how evolved pheromone parameters behave when some robots lie (inference) | [S-LL-1] | verified (pages 1, 2, 23 to 25 read) |
| O5 | 2018 | Strobel, Castelló Ferrer, Dorigo. Managing Byzantine Robots via Blockchain Technology in a Swarm Robotics Collective Decision Making Scenario | AAMAS 2018, starts p. 541, 9 pages (end page 549 computed) | Swarms are "claimed to be highly fault-tolerant". One or a few Byzantine (faulty or malicious) robots can still break coordination | Ethereum smart contracts on top of a best-of-2 collective decision task (Valentini et al.). A robot whose opinion mismatches the contract record is blacklisted. ARGoS, N = 20 robots, k = 0 to 9 Byzantine | A tamper-proof shared ledger lets mutually distrusting robots agree without a central authority | With Byzantine robots the classical approach "always converges to the wrong color if the simulation is not stopped when sub-swarm consensus is reached". Blockchain variants keep high exit probability. Cost: about 160 bytes per transaction vs 2 to 4 bytes. Ledger about 4 to 10 MB per 15 min run | Paper names: more Byzantine failure types, other swarm tasks, scale down computation and memory, port to real e-pucks. Sparse connectivity not studied | Contrast case for our no-communication defense. Their defense needs messages and a ledger. Ours needs none (inference) | [S-LL-2] | verified (pages 1, 2, 7, 8 read) |
| O4 | 2022 | Aswale, López, Ammartayakun, Pinciroli. Hacking the Colony: On the Disruptive Effect of Misleading Pheromone and How to Defend Against It | AAMAS 2022, pp. 27 to 34 | Stigmergy has no built-in trust. A few detractors can secrete misleading food pheromone | Grid pheromone, 1024 ants, custom AntSimulator (not ARGoS). Detractors form a blockade near the nest. Defense: "cautionary pheromone" laid by searching ants as patience runs out | Needs no IDs and no messages. It uses the same medium as the attack | 3 % detractors cut food collection 150 fold. Defense restores over 8 food bits per ant. It fails at 50 % detractors with non-evaporating pheromone | Defense fails at high detractor share. Only one attack shape (nest blockade) | Closest match to our floor-grid testbed. Reimplement cautionary pheromone in ARGoS as a baseline against our v3 (inference) | [S-PH-6] | verified (read in full in the earlier pass) |

### 1.2 Prof. Lu PhD line (UNM, Moses lab) and robot chains

| # | Year | Paper | Venue | Problem | Method | Why this way | Result | Open problems | Student opportunity | Source | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | 2016 | Lu, Hecker, Moses. The MPFA: a multiple-place foraging algorithm for biologically-inspired robot swarms (arXiv title: A Scalable and Adaptable Multiple-Place Foraging Algorithm for Ant-Inspired Robot Swarms) | IROS 2016, pp. 3815 to 3821 | In the CPFA every robot returns to one central nest. Travel time and collisions grow with swarm and arena size | Multiple-place foraging algorithm (MPFA): several nests spread over the arena. A robot returns a target to the nearest nest. GA tunes parameters. ARGoS | Shorter trips and spread-out traffic, like ant colonies with several nests (inference for the ant analogy) | Higher foraging rate, fewer collisions, lower travel and search time than the CPFA on partially clustered targets | Less communication among robots (fewer shared pheromone waypoints per nest). The GA only partly offsets it | Fewer pheromone readers per nest also means fewer victims per false trail (inference). Not tested anywhere we found | [S-LL-3], venue from [S-PH-1] ref 23 | partial (arXiv abstract page and a reference entry). That the arXiv preprint (other title, author order Lu, Moses, Hecker, comment "Robotics: Science and Systems") is the IROS 2016 paper is inference |
| L2 | 2018 | Lu, Hecker, Moses. Multiple-place swarm foraging with dynamic depots | Autonomous Robots 42(4) 909 to 926 | Static nests must be placed in advance. Good placement needs global information | Depots are robots. They move to the centroid of recently found local targets (MPFA dynamic). ARGoS, GA tuning | Depots follow the food, so trips stay short without a prior map (inference) | Beats the static MPFA, even with optimally placed static depots, and beats the CPFA. Gain is larger in 50 × 50 m arenas. Still ahead with sensing error | Depots must still travel far to the center in large arenas (stated by the 2021 chain paper) | Moving collection points make "suspect trail end" logic harder. A trail end may be stale, not false (inference) | [S-LL-4], [S-LL-8]. Volume and pages from [S-PH-1] ref 25 | partial (search snippet of the paper text, then confirmed by the 2021 abstract) |
| L3 | 2019 | Lu, Griego, Fricke, Moses. Comparing Physical and Simulated Performance of a Deterministic and a Bio-inspired Stochastic Foraging Strategy for Robot Swarms | ICRA 2019, pp. 9285 to 9291 | Do simulation rankings of foraging algorithms hold on real robots | Compare the CPFA with the distributed deterministic spiral algorithm (DDSA) in Gazebo and in a large outdoor arena | Real noise (collisions, obstacles, errors) is what swarms face outside the lab | DDSA wins in simulation. Outdoors the CPFA is as good or better. The authors say algorithms should be compared in the real world | Sim-to-real gap for pheromone attacks is not studied (inference) | Report our ARGoS results as simulation only. Add a noise test (position noise on trail laying) as a cheap robustness check (inference) | [S-LL-6] | partial (OpenAlex abstract) |
| L4 | 2019 | Lu. An Efficient Multiple-Place Foraging Algorithm for Scalable Robot Swarms (PhD dissertation, chair Moses, committee incl. Pinciroli) | University of New Mexico | Collect resources from large unmapped areas at a rate that does not drop with scale | MPFA, dynamic depots, a branching transport network, physical CPFA vs DDSA tests | Aim: scale-invariant per-robot foraging rate | MPFA beats the CPFA on rate, collisions, travel and search time in ARGoS | Stated: "Full implementation of the MPFA in an outdoor environment is the next step" | Pinciroli (Hacking the Colony author) sat on this committee. The security line links back to the PhD line through him (inference about influence) | [S-LL-5] | verified (repository record page) |
| L5 | 2020 | Lu, Fricke, Tsuno, Moses. A Bio-Inspired Transportation Network for Scalable Swarm Foraging | ICRA 2020, pp. 6120 to 6126 (extended abstract at MRS 2019) | Larger swarms collide more. Larger arenas raise travel cost | Mobile depots feed a hierarchical branching network, modeled on fractal biological networks. Scaling laws predict the rate | Biology already solved scale-invariant delivery with branching networks (abstract names fractal biological networks as the model) | Scale-invariant foraging in ARGoS with up to thousands of robots. A simple depot built in hardware | Assumes all robots cooperate (inference) | A branching network has choke points. One bad depot could divert a whole branch (inference) | [S-LL-7] | partial (OpenAlex abstract) |
| L6 | 2021 | Lee, Lu, Au. Multiple-Place Swarm Foraging with Dynamic Robot Chains | ICRA 2021, pp. 11337 to 11342 | Dynamic depots travel far in big arenas. More robots means more congestion | Robot chains link a location to the center. Resources pass along the chain | Passing items cuts the distance any one robot drives (inference) | Beats the dynamic-depot MPFA with less congestion, in ARGoS | A chain reaches one location at a time. Congestion at its end (stated by the 2022 paper) | Chains are relay paths, like pheromone trails made of robots. A lying chain member is an open attack (inference) | [S-LL-8] | partial (OpenAlex abstract) |
| L7 | 2022 | Lee, Lu, Au. Dynamic Robot Chain Networks for Swarm Foraging | ICRA 2022, pp. 4965 to 4971 | One chain serves one cluster and jams at its end | Branching chain networks. Smallest network posed as a Euclidean Steiner tree problem. ARGoS | Branches split traffic across clusters (abstract) | Avoids obstacles and collects more than the single chain | Not found in abstract. Robustness to robot failure not reported (inference) | Out of 2-week scope | [S-LL-9] | partial (OpenAlex abstract) |

- Affiliation note: OpenAlex prints "University of Texas at San Antonio" for Qi Lu on L6 and L7 [S-LL-8], [S-LL-9]. His UTRGV research page lists both papers [S-LQ-2]. So the UTSA "Qi Lu" in `research/lu_qi.md` open_questions is likely the same person before UTRGV (inference).

### 1.3 Prof. Lu UTRGV line (MARS lab)

| # | Year | Paper | Venue | Problem | Method | Why this way | Result | Open problems | Student opportunity | Source | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U0 | 2023 | Lu, Luna. Adaptive Multiple Distributed Bidirectional Spiral Path Planning for Foraging Robot Swarms | CRV 2023 per Scholar | Deterministic spiral search (DDSA, see L3) scales poorly | Multi-region bidirectional spirals in ARGoS | Keep the near-first strength of spirals, add parallel regions | Not read beyond the record | Not read | Search-pattern project, not the pheromone line | [S-LQ-5] | partial (record and abstract only) |
| U1 | 2024 (Apr) | Luna, Lu. Controlling Adversarial Pheromone-Based Infections via Quarantine Strategies in Foraging Robot Swarms | ICCCR 2024 (4th International Conference on Computer, Control and Robotics), pp. 251 to 256 | Virtual pheromone is open to attack through the stigmergy it relies on | Fake resource attack in ARGoS, varying number of fakes and time. Defense: circular quarantine regions around fakes. Distance-based merging of regions saves storage | Block the bait, not the robots (inference) | Per a paraphrase of the abstract: the attack cuts foraging significantly. Quarantine reduces collection of fake resources | Per the paraphrase: the authors call the algorithms fragile under such attacks. Who places quarantines is not in the abstract | Quarantine is close to our "suspect end" mark. Cite it as prior art for v3 (inference) | [S-LL-10] | partial (OpenAlex abstract) |
| U2 | 2024 (Jun) | Luna, Lu. Detection and Mitigation of Misleading Pheromone Trails in Foraging Robot Swarms | UR 2024 (21st International Conference on Ubiquitous Robots), pp. 350 to 357 | Detractor robots lay misleading trails and cut collection | DBSCAN on trails, grouping by cluster, adaptive timing from trail travel time | Isolate detractors early, not just their bait (inference) | Detractors isolated, capture rate down, foraging kept (abstract) | Not read. Overlap with U3 not checked | Read the full text before claiming novelty over it | [S-LL-11] | partial (OpenAlex abstract) |
| U3 | 2024 (pub. 2025) | Luna, Lu. Robust Mitigation Strategy for Misleading Pheromone Trails in Foraging Robot Swarms | TAROS 2024, LNAI 15052, pp. 307 to 319 | Same attack, now with lay-rate, detractor-share and obstacle tests | CPF with pheromone waypoints. Detractors report coordinates near capture sites. DBSCAN (ε = r_search, minPts = 2), creator-ID graph, travel-time check, 5 strikes to isolate. 24 foragers, ARGoS | Behavior-level evidence (late returns) needs no ground truth about who lies (inference) | Defense raised foraging "by up to 16.07%" and cut capture "by up to 65.69%". Obstacles "did not compromise" the defense | False positives stay nonzero in the obstacle test. Fig. 5 box plots span about 5 to 20 on the y axis (read by eye from the plot, no table). Needs creator IDs and a shared trail store (inference). Stated future work in §2 | Test a defense that needs no IDs (our v3). Report false positives like Fig. 5 does | [S-PH-1] | verified (read in full) |
| U4 | 2025 | Evolving Adaptive Foraging Robot Swarms with NEAT in Environments with Obstacles | 8th International Conference on Intelligent Robotics and Control | Hand rules break with obstacles | NeuroEvolution of Augmenting Topologies (NEAT) | Not read | Not read | Not read | Out of 2-week scope | [S-LQ-3] | partial (Scholar listing only) |
| U5 | 2026 | Li, Gutierrez, Hernandez, Lu, Zhou. LLM-Foraging: Large Language Models for Decentralized Swarm Robot Foraging | arXiv 2605.01461 | Not read beyond abstract page | Large language model (LLM) agents, Gazebo | Not read | Not read | An LLM forager could be a new detractor or a new defender (inference) | Out of 2-week scope | [S-LQ-6] | partial (affiliation of "Qi Lu" not shown) |

- Citation note: the TAROS reference list (pages 11 to 13) does not cite U1 or U2. It cites Lu's MPFA papers (refs 23, 25) and Hecker and Moses (refs 14, 15) [S-PH-1].
- No 2025 or 2026 pheromone-security paper by Lu or Luna was found in an OpenAlex search [S-LL-14]. "Not found" is not "does not exist".

## 2. Stated future work (quotes)

Only lines read on a page image are quoted. Fetch summaries are labeled.

| Paper | Quote (short) | Page | How read | Source |
| --- | --- | --- | --- | --- |
| Luna and Lu, TAROS 2024 (U3) | "Future work will focus on enhancing the scalability and efficiency of our defense mechanisms" | p. 317 | page image | [S-PH-1] |
| Luna and Lu, TAROS 2024 (U3) | "exploring applications in more dynamic environments" | p. 317 | page image | [S-PH-1] |
| Luna and Lu, TAROS 2024 (U3) | "possibly integrating advanced machine learning techniques to further refine adaptability and threat detection capabilities" | p. 317 | page image | [S-PH-1] |
| Luna and Lu, TAROS 2024 (U3), conclusion | "obstacles affected foraging efficiency, they did not compromise the defense's effectiveness" | p. 316 | page image | [S-PH-1] |
| Hecker and Moses 2015 (O3) | "Future work should test whether and how a GA can adapt the CPFA to more complex environments, additional sources of robot error, and larger physical robot swarms" | p. 67 | page image | [S-LL-1] |
| Hecker and Moses 2015 (O3) | foundation "for adapting behavioral rules in response to sensed environmental conditions in real time" | p. 67 | page image | [S-LL-1] |
| Strobel et al. 2018 (O5) | "In future work, we will expand the range of possible Byzantine failures" | p. 548 | page image | [S-LL-2] |
| Strobel et al. 2018 (O5) | "We have not investigated how sparse connectivity affects the blockchain approach" | p. 548 | page image | [S-LL-2] |
| Lu dissertation 2019 (L4) | "Full implementation of the MPFA in an outdoor environment is the next step" | abstract | relayed by a fetch summary, not seen on a page image | [S-LL-5] |

Unreadable in this pass (no future-work quote possible):

- UR 2024 (U2), DOI 10.1109/UR61395.2024.10597515. Abstract only via OpenAlex [S-LL-11].
- ICCCR 2024 (U1), DOI 10.1109/ICCCR61138.2024.10585509. Abstract only via OpenAlex [S-LL-10].
- Autonomous Robots 2018 (L2), DOI 10.1007/s10514-017-9693-2. Springer redirected to a login [S-LL-4].
- ICRA 2021 (L6), DOI 10.1109/ICRA48506.2021.9561124, and ICRA 2022 (L7), DOI 10.1109/ICRA46639.2022.9811625. Author copies refused connection. OpenAlex says not open access [S-LL-8], [S-LL-9].
- ICRA 2019 (L3) and ICRA 2020 (L5): abstracts only [S-LL-6], [S-LL-7].

## 3. Timeline: problem, solution, next problem

Arrows marked `cites` come from reference lists read in this pass. Other arrows are inference.

```
1996  Ant System (O1)                 problem: hard search, no central control
        |  pheromone = trusted shared memory, evaporation + reinforcement
        v
2001  Pheromone Robotics (O2)         solution: virtual pheromone on real robots
        |  every relaying robot is trusted (inference)
        v
2015  CPFA, Hecker and Moses (O3)     solution: GA-tuned pheromone waypoints,
        |                             site fidelity, error tolerance
        |  next problem: one central nest does not scale
        v
2016  MPFA (L1)  ==> 2018 dynamic depots (L2)  ==> 2020 branching network (L5)
        |  next problem: depots travel far, congestion at the center
        v
2021  robot chains (L6)  ==> 2022 chain networks (L7)
        :
        :  all of the above assume honest robots (inference)
        :
2009  Higgins et al. security survey  <== cites ==  Strobel 2018 [14], TAROS 2024 ref 16
        |
        +==> 2018 Byzantine robots + blockchain (O5)
        |       defense needs messages and a ledger
        |
        +==> 2022 Hacking the Colony (O4)  <== cites ==  TAROS 2024 ref 5
                attack: misleading pheromone. defense: cautionary pheromone, no IDs
                next problem: fails at 50 % detractors
        v
2024  ICCCR (U1)  fake resources  -> quarantine regions
2024  UR (U2)     detractors      -> DBSCAN + travel-time check
2024  TAROS (U3)  + obstacles, lay rates, 10 to 50 % detractors
        |  TAROS cites MPFA refs 23, 25 and CPFA refs 14, 15
        |  next problem (stated): scalability, efficiency, dynamic environments
        |  next problem (read): defense needs creator IDs, false positives stay
        v
2026  our testbed: floor-grid pheromone, no-communication defense (v3), lockout (v2)
```

## 4. Open problems we can attack in 2 weeks with our ARGoS testbed

Testbed numbers below come from two saved files.

- `01_pheromone/results/real/g2_stats.csv`: 10 seeds per detractor count. The dispatch prompt says this is defense v3 (inference from the prompt).
- `01_pheromone/results/real/v2/verdict.json`: lockout v2, 20 seeds, verdict `fail`, "report v2 as null".
- The 28 to 30 % cut in wasted time is stated in the dispatch prompt. It is not in either file.

| Detractors d | Food, defense off | Food, defense on | Gain (interval) | Source |
| --- | --- | --- | --- | --- |
| 0 | 75.8 | 73.9 | −1.9 (−5.0 to 1.5) | g2_stats.csv, interval level not stated in the file |
| 1 | 57.4 | 56.5 | −0.9 (−4.7 to 2.5) | g2_stats.csv |
| 2 | 42.1 | 44.4 | +2.3 (−0.7 to 5.2) | g2_stats.csv |
| 4 | 38.3 | 39.2 | +0.9 (−3.2 to 5.5) | g2_stats.csv |
| v2 (picked `t_lock` 10) at d = 2 | 42.45 | 46.5 | +4.05 (0.85 to 7.25), 95 % | verdict.json `item_8_metric_G2` |
| v2 at d = 0, failure test | not in file | not in file | −6.7 (−9.7 to −3.85), 95 % | verdict.json `item_11_failure.d0_cost` |
| `t_lock` 0 (v3 behavior on v4 code) at d = 0 | 81.35 | 75.2 | −6.15 (−8.25 to −4.05), 95 % | verdict.json `lock0_control_G.d0` |
| Picked vs `t_lock` 0, at d = 2, defense on | 44.8 (lock 0) | 46.5 (picked) | +1.7 (−1.0 to 4.45), 95 % | verdict.json `attribution_picked_vs_lock0_at_d2_on` |

- `t_lock` 0 means v3 behavior on the v4 code (`prereg/defense_v2_lockout.md`).
- Read: every v3 gain interval in g2_stats.csv includes 0.
- Read: v2 gains at d = 2, but the d = 0 cost triggered the pre-registered failure. v2 is a null result (`"verdict": "fail"`).
- Read: the `t_lock` 0 control also loses about 6 food at d = 0 on seeds 11 to 30. So the d = 0 cost is not shown to come from the lockout. It may come from the v3 base rule (inference).
- The v3 d = 0 cost differs between g2_stats.csv (−1.9, 10 seeds) and the `t_lock` 0 control (−6.15, 20 other seeds). Seed sets differ. Not resolved here.

Gaps below mean "not found in this survey". They are not proof that nobody did it.

| # | Open problem | Tied to | Our 2-week test (inference) | Type |
| --- | --- | --- | --- | --- |
| 1 | Defense cost when there is no attack (false positives). Source of our d = 0 cost is not established | TAROS Fig. 5 shows nonzero false positives [S-PH-1]. Our `t_lock` 0 control loses 6.15 food at d = 0 (verdict.json) | First count how often honest trail ends get marked suspect at d = 0. Then arm marking only after k independent suspect marks on one region. Pre-register k. Target: d = 0 cost interval includes 0 | measurement + application |
| 2 | Saturating damage curve | Aswale: 3 % detractors cut food 150 fold [S-PH-6]. Our loss: 18.4 at d = 1, 33.7 at d = 2, 37.5 at d = 4 (g2_stats.csv) | Add d = 8 and fit the dose-response shape. Ask why d = 4 adds little over d = 2 | theory + measurement |
| 3 | No-ID defense against a misleading-trail attack | TAROS defense needs creator IDs and a trail graph [S-PH-1]. Aswale's defense needs none [S-PH-6] | Reimplement cautionary pheromone on our grid as a third arm next to v3 | application |
| 4 | Less waste but no more food | v3 cut waste 28 to 30 % (dispatch prompt) but no gain interval excludes 0 (g2_stats.csv). Hecker and Moses: pheromone value depends on resource distribution [S-LL-1] | Log time per state (search, follow, return). Rerun v3 with clustered food, where pheromone matters most per [S-LL-1] | measurement |
| 5 | Scalability of the defense | TAROS stated future work: "scalability and efficiency" [S-PH-1] | Same detractor fraction at 20 and 40 honest robots. Report food per robot | application |
| 6 | Dynamic environments: stale trail vs false trail | TAROS stated future work: "more dynamic environments" [S-PH-1]. Depots move in L2 [S-LL-4] | Deplete or move food patches. Count honest trails wrongly marked suspect | application |
| 7 | Region quarantine vs end marking | ICCCR quarantine regions with distance-based merging [S-LL-10] | Turn suspect ends into circular no-follow regions on the grid. Compare with v3 point marks | application |
| 8 | Cost of trust: bits per defense | Blockchain needs about 160 bytes per transaction vs 2 to 4 bytes [S-LL-2]. Aswale and our v3 need 0 messages [S-PH-6] | A short table: messages, IDs and memory each defense needs. No runs needed | theory |

## Selection log

| Entity | Decision | Rule |
| --- | --- | --- |
| Dorigo, Maniezzo, Colorni 1996 (O1) | kept | outside milestone named in the dispatch. Page 1 read |
| Payton et al. 2001 (O2) | kept | virtual pheromone on robots. Pages 1 and 2 read. Cited by Hecker and Moses |
| Hecker and Moses 2015 (O3) | kept | CPFA, named in the dispatch. Pages 1, 2, 23 to 25 read |
| Aswale et al. 2022 (O4) | kept | named in the dispatch. Read in full earlier [S-PH-6] |
| Strobel et al. 2018 (O5) | kept | swarm security and Byzantine robots, named in the dispatch. Pages 1, 2, 7, 8 read |
| Lu PhD and chain papers (L1 to L7) | kept | named in the dispatch |
| Luna and Lu ICCCR, UR, TAROS (U1 to U3) | kept | named in the dispatch |
| Spiral 2023, NEAT 2025, LLM-Foraging 2026 (U0, U4, U5) | kept as partial | Lu papers 2023 to 2026. Not read past listing or abstract |
| Strobel et al., Frontiers in Robotics and AI 2020 | not rowed | search snippet only. Not fetched (budget) |
| Higgins et al. 2009 security survey | not rowed | cited by O5 and U3. Not fetched (budget). Used only as a cited bridge in §3 |
| Swarm Foraging Review 2020 (Lu, P4 in lu_qi.md) | not rowed | Scholar listing only. Not fetched (budget) |
| Multi-actor-attention-critic RL 2021 (P5) | not rowed | Scholar listing only. Off the pheromone and security line |
| PID tuning with particle swarm optimization 2024 (P9) | not rowed | off topic (quadrotor control) |
| Lu Swarmathon or iAnt hardware papers | not searched | out of budget |
| OpenAlex author-ID lookup | failed lookup | the guessed author ID returned a different person. Discarded, not cited |

## open_questions:

- L1: is arXiv 1612.00480 the same work as the IROS 2016 MPFA paper? Title, author order and comment differ.
- L2: 2018 dynamic-depot numbers come from a search snippet. Springer full text not read.
- U1, U2: full texts not read. How U2 differs from U3 is unknown.
- U3: TAROS does not cite U1 or U2. Reason unknown.
- U3: false positives read by eye from Fig. 5. No table value.
- U4: NEAT 2025 authors and venue details not read.
- U5: affiliation of "Qi Lu" on LLM-Foraging not shown.
- Qi Lu at UTSA (L6, L7) vs UTRGV: likely the same person (inference). Not confirmed by a first-party page.
- No Lu or Luna pheromone-security paper from 2025 or 2026 found. One OpenAlex query only [S-LL-14].
- O1: the Ant System update and evaporation rule not read (page 1 only).
- g2_stats.csv: the label "v3" comes from the dispatch prompt, not from the file.
- The 28 to 30 % waste cut is not in either saved file.
- v3 d = 0 cost: −1.9 in g2_stats.csv vs −6.15 in the `t_lock` 0 control. Different seed sets. Cause not checked.

## Sources

Reused rows from `research/lu_qi.md` and `01_pheromone/research/pheromone_research.md`, copied so every ID resolves here:

[S-LQ-2] Qi Lu: Research | https://sites.google.com/view/qilu/research | published: undated | accessed: 2026-11-10 | type: official
[S-LQ-3] Qi Lu: Google Scholar profile | https://scholar.google.com/citations?user=5471pIYAAAAJ&hl=en | published: live profile | accessed: 2026-11-10 | type: aggregator | note: first 20 articles only
[S-LQ-5] Adaptive Multiple Distributed Bidirectional Spiral Path Planning for Foraging Robot Swarms | https://par.nsf.gov/biblio/10591790 | published: 2023 | accessed: 2026-11-10 | type: paper | note: NSF PAR record and abstract only
[S-LQ-6] LLM-Foraging: Large Language Models for Decentralized Swarm Robot Foraging | https://arxiv.org/abs/2605.01461 | published: 2026-05-02 | accessed: 2026-11-10 | type: paper | note: abstract page only
[S-PH-1] Robust Mitigation Strategy for Misleading Pheromone Trails in Foraging Robot Swarms | https://par.nsf.gov/servlets/purl/10593555 | published: 2025, TAROS 2024 LNAI 15052 pp. 307 to 319, DOI 10.1007/978-3-031-72062-8_27 | accessed: 2026-11-11 | type: paper | note: read in full 2026-11-10. Pages 10 to 13 re-read as page images 2026-11-11 for the quotes
[S-PH-6] Hacking the Colony: On the Disruptive Effect of Misleading Pheromone and How to Defend Against It | https://arxiv.org/abs/2202.01808 | published: AAMAS 2022 pp. 27 to 34 | accessed: 2026-11-10 | type: paper | note: all 8 pages read in the earlier pass

New sources:

[S-LL-1] Beyond pheromones: evolving error-tolerant, flexible, and scalable ant-inspired robot swarms | https://cs.unm.edu/~joel/cs351/paper/BeyondPheromones.pdf | published: 2015-02-15, Swarm Intelligence 9:43 to 70, DOI 10.1007/s11721-015-0104-z | accessed: 2026-11-11 | type: paper | note: pages 1, 2, 23 to 25 read as page images
[S-LL-2] Managing Byzantine Robots via Blockchain Technology in a Swarm Robotics Collective Decision Making Scenario | https://ifaamas.csc.liv.ac.uk/Proceedings/aamas2018/pdfs/p541.pdf | published: 2018-07, AAMAS 2018 | accessed: 2026-11-11 | type: paper | note: pages 1, 2, 7, 8 read as page images
[S-LL-3] A Scalable and Adaptable Multiple-Place Foraging Algorithm for Ant-Inspired Robot Swarms | https://arxiv.org/abs/1612.00480 | published: 2016-12-01 | accessed: 2026-11-11 | type: paper | note: arXiv abstract page via fetch summary
[S-LL-4] Multiple-place swarm foraging with dynamic depots | https://link.springer.com/article/10.1007/s10514-017-9693-2 | published: 2018, Autonomous Robots 42(4) | accessed: 2026-11-11 | type: paper | note: search snippet of the paper text only. PDF redirected to a login
[S-LL-5] An Efficient Multiple-Place Foraging Algorithm for Scalable Robot Swarms | https://digitalrepository.unm.edu/cs_etds/100 | published: 2019-07-15 | accessed: 2026-11-11 | type: official | note: UNM repository record page via fetch summary. PhD dissertation
[S-LL-6] Comparing Physical and Simulated Performance of a Deterministic and a Bio-inspired Stochastic Foraging Strategy for Robot Swarms | https://api.openalex.org/works/doi:10.1109/ICRA.2019.8794240 | published: 2019-05, ICRA 2019 pp. 9285 to 9291 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex record, abstract paraphrased from the inverted index
[S-LL-7] A Bio-Inspired Transportation Network for Scalable Swarm Foraging | https://api.openalex.org/works/doi:10.1109/ICRA40945.2020.9196762 | published: 2020-05, ICRA 2020 pp. 6120 to 6126 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex record, abstract paraphrased
[S-LL-8] Multiple-Place Swarm Foraging with Dynamic Robot Chains | https://api.openalex.org/works/doi:10.1109/ICRA48506.2021.9561124 | published: 2021-05-30, ICRA 2021 pp. 11337 to 11342 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex record, abstract paraphrased, index has gaps
[S-LL-9] Dynamic Robot Chain Networks for Swarm Foraging | https://api.openalex.org/works/doi:10.1109/ICRA46639.2022.9811625 | published: 2022-05-23, ICRA 2022 pp. 4965 to 4971 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex record, abstract paraphrased
[S-LL-10] Controlling Adversarial Pheromone-Based Infections via Quarantine Strategies in Foraging Robot Swarms | https://api.openalex.org/works/doi:10.1109/ICCCR61138.2024.10585509 | published: 2024-04-19, ICCCR 2024 pp. 251 to 256 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex record, abstract paraphrased
[S-LL-11] Detection and Mitigation of Misleading Pheromone Trails in Foraging Robot Swarms | https://api.openalex.org/works/doi:10.1109/UR61395.2024.10597515 | published: 2024-06-24, UR 2024 pp. 350 to 357 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex record, abstract paraphrased
[S-LL-12] The Ant System: Optimization by a colony of cooperating agents | https://faculty.washington.edu/paymana/swarm/dorigo96-itsmc.pdf | published: 1996, IEEE Transactions on Systems, Man, and Cybernetics, Part B, 26(1) | accessed: 2026-11-11 | type: paper | note: page 1 read as a page image. Preprint pagination pp. 1 to 13
[S-LL-13] Pheromone Robotics | https://www2.cs.sfu.ca/~vaughan/teaching/415/papers/Payton%202001a.pdf | published: 2001, Autonomous Robots 11(3) 319 to 324 per search snippet | accessed: 2026-11-11 | type: paper | note: pages 1 and 2 of an HRL preprint read as page images. Venue from search snippet
[S-LL-14] OpenAlex works search "pheromone foraging robot swarms detractor" | https://api.openalex.org/works?search=pheromone%20foraging%20robot%20swarms%20detractor&sort=publication_date:desc&per-page=15 | published: live index | accessed: 2026-11-11 | type: aggregator | note: 4 results. Newest Lu and Luna item is TAROS, 2024-12-29
