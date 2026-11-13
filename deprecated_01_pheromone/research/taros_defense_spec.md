# TAROS 2024 defense spec for M6 (T-B, adapted arm)

- Purpose: give the architect the exact Luna and Lu defense, so T-B can adapt it to our grid (D-040).
- Main source: Luna and Lu, TAROS 2024, printed pp. 307 to 317, read in full as page images [S-TB-1].
- Page numbers below are the printed page numbers (LNAI 15052). Pages 318 to 319 (references) were not opened in this pass.
- The paper has no algorithm box and no pseudocode. Section 1 is assembled from prose on pp. 309 to 311.
- Tag key: `stated p. N` = printed on that page. `NOT STATED` = the paper is silent. `inference` = our reading.
- Source tag: `TB` (track T-B). [S-TB-1] is the same document as [S-PH-1] in `pheromone_research.md`.
- Summary counts: sources 6. Papers read in full 1 of 3. Unverifiable parameter rows 3. Open questions 10.

## 0. What could not be read

| Paper | Status | Open copy found | Why not read |
| --- | --- | --- | --- |
| TAROS 2024 | read in full, pp. 307 to 317 | NSF PAR PDF [S-TB-1] | none |
| UR 2024, DOI 10.1109/UR61395.2024.10597515 | NOT READ. Abstract only, as a fetch-tool paraphrase | UTRGV ScholarWorks PDF: https://scholarworks.utrgv.edu/cgi/viewcontent.cgi?article=1165&context=cs_fac (landing page cs_fac/166) [S-TB-5] | PDF returned HTTP 403 to the fetch tool. Semantic Scholar and OpenAlex mark it closed [S-TB-2], [S-TB-4] |
| ICCCR 2024, DOI 10.1109/ICCCR61138.2024.10585509 | NOT READ. Abstract only, as a fetch-tool paraphrase | UTRGV ScholarWorks PDF: https://scholarworks.utrgv.edu/cgi/viewcontent.cgi?article=1174&context=cs_fac (landing page cs_fac/175) [S-TB-6] | PDF returned HTTP 403 to the fetch tool. Semantic Scholar and OpenAlex mark it closed [S-TB-3], [S-TB-4] |

- New finding: both earlier papers have a PDF on UTRGV ScholarWorks. Earlier research files said "abstract only".
- The owner can open both links in a browser. A bot check blocks only the fetch tool (inference from the 403).
- ResearchGate and author pages: not tried. ScholarWorks is the author-institution repository.
- What reading UR would decide: UR's abstract describes the same defense (DBSCAN, cluster grouping, adaptive timing) [S-TB-2]. It may fill the NOT STATED gaps in Section 1 (inference).
- What reading ICCCR would decide: the quarantine radius and the merge distance for a possible T-E row (inference).

## 1. Defense pseudocode

### 1.1 Base foraging loop (CPF), what a robot records

| Step | Content | Tag | Source |
| --- | --- | --- | --- |
| States | Departing, Searching, Surveying, Returning | stated p. 309 | [S-TB-1] |
| Surveying | Count k resources within r_search | stated p. 309 | [S-TB-1] |
| Lay decision | On return, lay a new pheromone waypoint if Pois(c, λ_lp) > U(0,1). Pois(k, λ) = e^(−λ) · Σ_{i=0}^{k} λ^i / i! | stated p. 309, Eq. 1 | [S-TB-1] |
| Lay-rate sign | Smaller λ values mean more frequent trail laying | stated p. 313 | [S-TB-1] |
| Waypoint strength | Starts at 1. Decays w = e^(−t · λ_pd). Removed below threshold γ | stated p. 309 | [S-TB-1] |
| Waypoint fields | Spatial coordinates (p. 310). Creator ID (p. 310). Estimated travel time (p. 310). A creation time is implied by the decay (inference) | partial | [S-TB-1] |
| Where waypoints live, how shared | NOT STATED. The defense needs every trail with its creator ID in one place. This implies a central or nest-side store (inference) | NOT STATED | [S-TB-1] |

### 1.2 Attack model

| Step | Content | Tag | Source |
| --- | --- | --- | --- |
| Detractor | Mimics a benign forager. Reports coordinates near a capture site instead of a real resource | stated p. 309 | [S-TB-1] |
| Effect | Followers reach the capture site and are removed from foraging | stated p. 309 | [S-TB-1] |
| Capture site radius | r_cs = r_center / 2 | stated p. 312, Table 1 | [S-TB-1] |
| Number and place of capture sites | NOT STATED. Fig. 1 shows several red discs near the arena edge | partial (figure only) | [S-TB-1] |
| Detractor lay rate | λ_dt, separate from forager rate λ_fg | stated p. 312 | [S-TB-1] |

### 1.3 Defense pseudocode

```
# DATA (per waypoint)
waypoint = { xy, creator_id, est_travel_time, strength }      # p. 310, p. 309
# per robot
strikes[robot_id] = 0                                          # counter scope: per robot, p. 311 wording
isolated[robot_id] = False

# STEP A. DBSCAN on trail points                               # p. 310
points  = xy of all current pheromone waypoints
labels  = DBSCAN(points, eps = r_search, minPts = 2)           # p. 310, Table 1 p. 312
# when DBSCAN re-runs: NOT STATED
# noise points (label -1): NOT STATED
# do decayed or removed waypoints leave the input: NOT STATED (inference: yes, they no longer exist)

# STEP B. Cluster grouping by creator ID                       # p. 310, Fig. 2 p. 311
G = graph(nodes = clusters)
for each pair of clusters (Ci, Cj):
    if creators(Ci) ∩ creators(Cj) is not empty:
        add edge (Ci, Cj)
groups = connected_components(G)
# "robots associated with a group" = all creator IDs in its clusters (inference from p. 311)

# STEP C. Travel-time check                                    # p. 310 to 311
when robot f starts following waypoint w:
    start_time = now
    deadline = w.est_travel_time
    # est_travel_time = f(distance to destination, average speed). Formula and speed value: NOT STATED
    # "destination" = waypoint location or round trip to nest: NOT STATED

# STEP D. Strike rule                                          # p. 311
if f has not returned by deadline:
    for r in robots_associated_with(group_of(w)):
        strikes[r] += 1
    # "significant margin" (p. 311) and "significant deviations" (p. 310): no value given
    # how a strike is timed if f returns later (one strike or none): NOT STATED

# STEP E. Isolation                                            # p. 311
if strikes[r] >= 5:                                            # "five strikes (determined empirically)"
    isolated[r] = True                                         # "temporary isolation from the swarm"
    # duration of isolation: NOT STATED
    # what happens to r's waypoints: NOT STATED
    # who executes it: NOT STATED. Fig. 1 parks "Isolated Detractors" at the arena edge (p. 310)

# STEP F. Late return: feedback and reintegration               # p. 311
if f returns on w AFTER w.est_travel_time:
    w.est_travel_time = update(est, measured)                  # "simple feedback loop", formula NOT STATED
    for r in robots_associated_with(group_of(w)):
        if isolated[r]: isolated[r] = False                    # reintegrated
        else:           strikes[r] -= 1                        # "have a 'strike' removed"
# the estimate is updated ONLY on a return after the current estimate (p. 311)
# a return before the estimate: no change stated
```

### 1.4 Step table with tags

| # | Step | What the paper says | Tag | Source |
| --- | --- | --- | --- | --- |
| A1 | DBSCAN input | "spatial coordinates given by the pheromone trail waypoints" | stated p. 310 | [S-TB-1] |
| A2 | eps | "search radius ε equal to the robots' search radius" | stated p. 310. Table 1 ε = r_search (p. 312) | [S-TB-1] |
| A3 | eps as a number | r_search = 4 · r_resource, r_resource = 0.05. So ε = 0.2 (our arithmetic). Units not printed, meters assumed | inference | [S-TB-1] |
| A4 | minPts | 2, "due to the expected data sparsity in small-scale swarm scenarios" | stated p. 310 | [S-TB-1] |
| A5 | DBSCAN schedule, noise handling | Not described | NOT STATED | [S-TB-1] |
| B1 | Graph | Nodes = clusters. Edge if two clusters' trails "share at least one common creator ID" | stated p. 310 | [S-TB-1] |
| B2 | Purpose | Larger groupings to identify robots "exhibiting similar trail laying behavior" | stated p. 310 | [S-TB-1] |
| B3 | Fig. 2 example | Honest clusters C2, C3, C4 look linked through R2 and R4. Detractor clusters C1 and C5 link through R10 and R20. Labels are small | partial (figure read) | [S-TB-1] |
| B4 | Consequence of B3 | One missed return in an honest group strikes every honest creator in that group. This may drive false positives at d = 0 | inference | [S-TB-1] |
| C1 | Estimate | Each trail "includes an estimated travel time calculated based on the distance to the destination and the robot's average speed" | stated p. 310 | [S-TB-1] |
| C2 | Measure | "When a robot follows a trail, the actual time taken to travel is recorded and compared against the estimated time" | stated p. 310 | [S-TB-1] |
| C3 | Update | "simple feedback loop" using measured time "when a robot returns". "only updated when a robot returns after the current estimated travel time" | stated p. 311 | [S-TB-1] |
| C4 | Why update | "obstacles and collisions can affect travel time and must be taken into account" | stated p. 311 | [S-TB-1] |
| C5 | Margin, speed, update formula | No values | NOT STATED | [S-TB-1] |
| D1 | Strike | "given to all robots associated with a cluster group when a robot does not return within the estimated travel time of one of the trails within the group" | stated p. 311 | [S-TB-1] |
| D2 | p. 310 vs p. 311 wording | p. 310: deviations trigger "an isolation event for the trail creator and other robot's associated with the flagged trail's cluster group". p. 311: a strike, isolation at five. Read p. 310 as the summary of p. 311 (inference) | partial | [S-TB-1] |
| E1 | Threshold | "predefined threshold of five strikes (determined empirically)" | stated p. 311 | [S-TB-1] |
| E2 | Isolation | "the robot's temporary isolation from the swarm to prevent further disruption" | stated p. 311 | [S-TB-1] |
| E3 | Isolated robot's trails | Not described | NOT STATED | [S-TB-1] |
| F1 | Reintegration | "if a forager returns on a trail within a flagged cluster group after its estimated travel time, the trail creator and other robots associated with the trail's cluster group are reintegrated (if isolated) or have a 'strike' removed" | stated p. 311 | [S-TB-1] |
| F2 | Implied | Reintegration needs a robot to keep following trails of a flagged group. So those trails stay followable after isolation | inference | [S-TB-1] |
| F3 | Same event, two roles | A late return both updates the estimate and removes a strike. A missed return gives a strike | stated p. 311 (both clauses) | [S-TB-1] |
| G1 | Who runs the defense | Not described. Central process or each robot | NOT STATED | [S-TB-1] |

## 2. Parameters

All from Table 1 unless noted. Table 1 is on p. 312 [S-TB-1].

| Parameter | Value | Page | Verification | Source |
| --- | --- | --- | --- | --- |
| D_arena | (10, 10, 1), foraging area (x, y, z) | p. 312 | verified | [S-TB-1] |
| D_cluster | (6, 6), resource cluster size (l, w) | p. 312 | verified | [S-TB-1] |
| n_fg | 24 foragers | p. 312 | verified | [S-TB-1] |
| n_dt | Exp 1: 25 %. Exp 2: 10, 20, 30, 40, 50 %. Exp 3: 25 %. "# of detractors based on n_fg" | p. 312 | verified | [S-TB-1] |
| n_dt as a count | 25 % of 24 = 6 (our arithmetic). Extra robots or part of the 24: NOT STATED | p. 312 | inference | [S-TB-1] |
| n_cl | 8 resource clusters | p. 312 | verified | [S-TB-1] |
| n_obs | Exp 1, 2: N/A. Exp 3: 0, 4, 8, 12, 16 | p. 312 | verified | [S-TB-1] |
| r_center | 0.25 | p. 312 | verified | [S-TB-1] |
| r_resource | 0.05 | p. 312 | verified | [S-TB-1] |
| r_search | 4 · r_resource, "Foot-bot search radius" | p. 312 | verified | [S-TB-1] |
| r_cs | r_center / 2, capture site radius | p. 312 | verified | [S-TB-1] |
| λ_fg | Exp 1: 1, 4, 8, 12. Exp 2: 4. Exp 3 cell blank in the table | p. 312 | partial (Exp 3 unclear) | [S-TB-1] |
| λ_dt | Exp 1: 1, 4, 8, 12. Exp 2: 1 (Table 1) [CONFLICT] with "a rate of 4 selected for further testing in Experiment 2" (p. 313). Exp 3 cell blank | p. 312, p. 313 | partial | [S-TB-1] |
| d_obs | Exp 3: Random, Annular | p. 312 | verified | [S-TB-1] |
| ε (DBSCAN) | r_search | p. 310, p. 312 | verified | [S-TB-1] |
| minPts | 2 | p. 310, p. 312 | verified | [S-TB-1] |
| Strike threshold | 5 | p. 311 | verified | [S-TB-1] |
| λ_sf, λ_lp, p_r, λ_pd, γ | Named on p. 309. No values printed | p. 309 | unverifiable [UNVERIFIED] | [S-TB-1] |
| Travel-time margin, average speed, feedback gain | Not printed | p. 310 to 311 | unverifiable [UNVERIFIED] | [S-TB-1] |
| Isolation duration | Not printed ("temporary") | p. 311 | unverifiable [UNVERIFIED] | [S-TB-1] |
| Robot | Foot-bot in ARGoS | p. 311, p. 312 | verified | [S-TB-1] |

## 3. Experimental setup and results

- There is no results table. All numbers below are from the text on pp. 313 to 316.
- Values are not read off box plots.

| Item | Value | Page | Verification | Source |
| --- | --- | --- | --- | --- |
| Simulator | ARGoS | p. 311 | verified | [S-TB-1] |
| Exp 1 | Vary λ_fg and λ_dt, attack only | p. 312 | verified | [S-TB-1] |
| Exp 2 | Vary n_dt 10 to 50 %, with and without defense | p. 312, p. 313 | verified | [S-TB-1] |
| Exp 3 | Obstacles, density 0 to 16, random or annular, attack plus defense | p. 312, p. 316 Fig. 5 | verified | [S-TB-1] |
| Runs | "over 50 runs" stated for Exp 1 only. Exp 2 and Exp 3 run counts NOT STATED | p. 313 | partial | [S-TB-1] |
| Run length | NOT STATED. Fig. 4 time axis ends at 16 minutes | p. 314 | partial | [S-TB-1] |
| Seeds | NOT STATED | none | unverifiable | [S-TB-1] |
| Metrics | Total Resources Collected (%). Total Foragers Captured (%). Exp 3 adds False Positives Detected and Final Univelocity. Units of false positives and the meaning of Univelocity are not defined | p. 313, p. 315, p. 316 | partial | [S-TB-1] |
| Exp 1, λ = 1 | Resources 61.61 %. Captured 88.75 % | p. 313 | verified | [S-TB-1] |
| Exp 1, λ = 4 | Resources 61.82 %. Captured 92.50 % (highest) | p. 313 | verified | [S-TB-1] |
| Exp 1, λ = 8 | Resources 54.71 %. Captured 72.92 % | p. 313 | verified | [S-TB-1] |
| Exp 1, λ = 12 | Resources 73.19 %. Captured 14.31 % | p. 313 | verified | [S-TB-1] |
| Exp 2, no detractors | Baseline efficiency "approximately 85%" | p. 313 | verified | [S-TB-1] |
| Exp 2, attack only | 57.92 % at 10 % detractors. 43.66 % at 50 % | p. 314 | verified | [S-TB-1] |
| Exp 2, defense gain | +16.06 % at 10 %. +12.33 % at 50 % (p. 314). Conclusion: "up to 16.07%" (p. 316) [CONFLICT] (rounding, inference) | p. 314, p. 316 | partial | [S-TB-1] |
| Exp 2, capture reduction | "reduced forager capture rates by up to 65.69%" | p. 316 | verified | [S-TB-1] |
| Exp 2, capture rate per minute | 10 %: peak 0.866 by minute 4, 0.033 by minute 15. 50 %: peak 2.6 by minute 4, near 0.0 by minute 16 | p. 314 | verified | [S-TB-1] |
| Exp 2, isolation rate per minute | 10 %: peak 0.066 at minute 11. 20 %: 0.133 by minute 7. 30 %: 0.5 by minute 5. Virtually none after minute 16 | p. 314 to 315 | verified | [S-TB-1] |
| Exp 3 | Resources peak 66.26 % (SD 7.78) with sixteen obstacles. Captures, false positives and Univelocity "stable" or "minor variations" | p. 315 | verified | [S-TB-1] |
| Exp 3 conclusion | "obstacles affected foraging efficiency, they did not compromise the defense's effectiveness" | p. 316 | verified | [S-TB-1] |
| False positives at d = 0 | NOT REPORTED. Fig. 3b plots 0 % on the x axis. Fig. 5 shows nonzero false positives under attack | p. 313, p. 316 | partial | [S-TB-1] |

## 4. Grid adaptation assumptions

- "Paper does" cells are from [S-TB-1]. "Our grid" cells come from the dispatch, D-040 and fable_tracks M6. The testbed code was not read.

| # | Paper does | Our grid must change | Verification | Source |
| --- | --- | --- | --- | --- |
| 1 | Trails are discrete waypoints with xy and creator ID (p. 310) | Trails are floor-grid cells. No ID unless the loop functions record the depositor per cell. Need a per-cell depositor record, or a separate "trail end" record per deposit run | partial (paper side verified, grid side from dispatch) | [S-TB-1], dispatch |
| 2 | One DBSCAN point per waypoint (p. 310) | Pick one point per trail. fable_tracks M6 says "trail ends". Clustering every deposited cell would make dense clusters out of one trail | inference | [S-TB-1], fable_tracks M6 |
| 3 | ε = r_search = 0.2 in a 10 x 10 arena (p. 312) | Our arena is 5 x 5 m (fable_tracks M7). ε must be chosen for our cell size and search radius and frozen before runs (fable_tracks M6) | inference | [S-TB-1], fable_tracks M6, M7 |
| 4 | A robot "follows a trail" to one waypoint (p. 309) | A gradient follower has no single trail. Need a rule for which trail end a follower is assigned to (for example the end it reaches or the cluster it enters) | inference | [S-TB-1] |
| 5 | Each trail carries est_travel_time from distance and average speed (p. 310) | Compute from nest-to-trail-end distance and a measured honest speed. Margin and feedback gain are not in the paper and must be pre-registered | inference | [S-TB-1] |
| 6 | "Return" ends a check. A capture means no return (p. 309, p. 311) | Define "return" as reaching the nest. Define what our capture site does to a robot. If our robots are not removed, a captured robot may return late and erase strikes (F1) | inference | [S-TB-1] |
| 7 | Strikes go to all creators in a connected group (p. 311) | Keep the group strike. Log honest robots struck per run, since B4 predicts d = 0 false positives | inference | [S-TB-1] |
| 8 | 5 strikes isolate (p. 311) | Keep 5 as the paper value. It was tuned for 24 robots and λ = 4 | verified (value) | [S-TB-1] |
| 9 | Isolated robots park at the arena edge (Fig. 1, p. 310). Their trails: NOT STATED | Must pick: isolated robots stop depositing, and their cells are masked or left to decay. Log it as an adaptation choice | inference | [S-TB-1] |
| 10 | Who runs DBSCAN and strikes: NOT STATED | Run it in the loop functions as a shared trail store, per fable_tracks M6. This is a global-knowledge arm | partial (design from fable_tracks) | fable_tracks M6 |
| 11 | Re-run schedule: NOT STATED | Pick a fixed period, or run on each new trail end. Pre-register it | inference | [S-TB-1] |
| 12 | Reintegration on a late return (p. 311) | Keep it. Needs isolated robots' trails to stay followable (F2). Conflicts with masking in row 9. Choose one | inference | [S-TB-1] |
| 13 | Lay rate is Poisson on resource density (p. 309) | Our deposit rule differs. Not part of the defense. Keep our deposit rule | inference | [S-TB-1] |

## 5. Stated future work

| Quote | Page | Verification | Source |
| --- | --- | --- | --- |
| "Future work will focus on enhancing the scalability and efficiency of our defense mechanisms" | p. 317 | verified | [S-TB-1] |
| "exploring applications in more dynamic environments" | p. 317 | verified | [S-TB-1] |
| "possibly integrating advanced machine learning techniques to further refine adaptability and threat detection capabilities" | p. 317 | verified | [S-TB-1] |

## 6. Earlier papers (UR 2024, ICCCR 2024)

| Paper | Claim | Verification | Source |
| --- | --- | --- | --- |
| UR 2024 | Abstract: DBSCAN clustering, cluster grouping and an adaptive timing mechanism isolate detractors early. Same three parts as TAROS | partial (abstract paraphrase only) | [S-TB-2], [S-TB-5] |
| ICCCR 2024 | Abstract: fake-resource attack. Circular quarantine regions keep robots away. A distance-based merging algorithm limits storage. ARGoS | partial (abstract paraphrase only) | [S-TB-3], [S-TB-6] |
| Both | Full text exists on UTRGV ScholarWorks. Not read (HTTP 403 to the fetch tool) | verified (existence of landing page) | [S-TB-4], [S-TB-5], [S-TB-6] |

## Selection log

| Item | Decision | Rule |
| --- | --- | --- |
| Luna and Lu, TAROS 2024 | kept, read in full | named in dispatch, first-party |
| Luna and Lu, UR 2024 | kept, abstract only | named in dispatch. Full text blocked (403) |
| Luna and Lu, ICCCR 2024 | kept, abstract only | named in dispatch. Full text blocked (403) |
| "Adaptive Repulsive Pheromone Clustering for Foraging Robot Swarms", arXiv 2608.16822 | not used | appeared in one search. Authors and relevance not checked. Out of dispatch scope |

## open_questions

- UR and ICCCR full text: owner can download from the two ScholarWorks links in Section 0.
- λ_dt in Exp 2: 1 (Table 1, p. 312) vs 4 (p. 313) [CONFLICT].
- Defense gain: 16.06 % (p. 314) vs 16.07 % (p. 316) [CONFLICT].
- λ_sf, λ_lp, p_r, λ_pd, γ values [UNVERIFIED].
- Travel-time margin, average speed, feedback formula [UNVERIFIED].
- Isolation duration and the fate of isolated robots' trails [UNVERIFIED].
- DBSCAN re-run schedule and noise handling. Who runs the defense.
- Runs, seeds and length for Exp 2 and Exp 3.
- Are detractors part of the 24 foragers?
- Fig. 2 group links (B3) read from small labels.

## Sources

[S-TB-1] Robust Mitigation Strategy for Misleading Pheromone Trails in Foraging Robot Swarms | https://par.nsf.gov/servlets/purl/10593555 | published: 2025, TAROS 2024 LNAI 15052 pp. 307 to 319, DOI 10.1007/978-3-031-72062-8_27 | accessed: 2026-11-11 | type: paper | note: pp. 307 to 317 read as page images from the NSF PAR PDF. Same document as S-PH-1
[S-TB-2] Semantic Scholar record: Detection and Mitigation of Misleading Pheromone Trails in Foraging Robot Swarms | https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/UR61395.2024.10597515 | published: UR 2024 | accessed: 2026-11-11 | type: aggregator | note: openAccessPdf status CLOSED. Abstract read as a fetch-tool paraphrase
[S-TB-3] Semantic Scholar record: Controlling Adversarial Pheromone-Based Infections via Quarantine Strategies in Foraging Robot Swarms | https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/ICCCR61138.2024.10585509 | published: ICCCR 2024 | accessed: 2026-11-11 | type: aggregator | note: openAccessPdf status CLOSED. Abstract read as a fetch-tool paraphrase
[S-TB-4] OpenAlex records for both DOIs | https://api.openalex.org/works?filter=doi:10.1109/UR61395.2024.10597515|10.1109/ICCCR61138.2024.10585509 | published: live index | accessed: 2026-11-11 | type: aggregator | note: oa_status closed. Lists scholarworks.utrgv.edu cs_fac/166 and cs_fac/175 as locations
[S-TB-5] UTRGV ScholarWorks: Detection and Mitigation of Misleading Pheromone Trails in Foraging Robot Swarms | https://scholarworks.utrgv.edu/cs_fac/166 | published: UR 2024 | accessed: 2026-11-11 | type: official | note: landing page read. PDF viewcontent.cgi?article=1165 returned HTTP 403
[S-TB-6] UTRGV ScholarWorks: Controlling Adversarial Pheromone-Based Infections via Quarantine Strategies in Foraging Robot Swarms | https://scholarworks.utrgv.edu/cs_fac/175 | published: ICCCR 2024 | accessed: 2026-11-11 | type: official | note: landing page read. PDF viewcontent.cgi?article=1174 returned HTTP 403
