# Prof. Lu's papers vs our Final Project 2 design: applied, not applied, next work

- Author: system-architect, 2026-11-16. Status: proposal. Fable picks and logs D-rows. Nothing here changes `DESIGN.md` or a living doc yet.
- Inputs: `lu_papers_p2.md` (paper facts, page cites), `informed_search_survey.md`, `baseline_code_map.md` (BCM), `../DESIGN.md`, `../PLAN.md`, `../DECISIONS.md` D-001 to D-021, `../TASKS.md`.
- Code facts read this pass: `vendor/Collision_Free_CPFA/source/Base/BaseController.cpp:300-362` (collision counter, see §5).
- Every paper fact cites the page printed in `lu_papers_p2.md`. Every other number is marked inference, or is a run for the main session (§7).
- Abbreviations: central-place foraging algorithm (CPFA), Grid-Based Complete Foraging Algorithm (GCFA), Adaptive Repulsive Pheromone Clustering (ARPC), Multiple-Distributed Bidirectional Spiral Algorithm (MDBSA), multiple-place foraging algorithm (MPFA), correlated random walk (CRW), density-based spatial clustering of applications with noise (DBSCAN), genetic algorithm (GA). Paper short names are the keys of `lu_papers_p2.md`.

## 0. Mission block (quoted from `../PLAN.md`)

> - Mission: Find ground no robot has searched, so the swarm collects more in 12 minutes. Keep server cost small as swarms and arenas grow. (Fable, owner-delegated, 2026-11-12, D-003)
> - Vision: One page shows 3-distribution box plots with % improvement over original CPFA and its interval. A query-cost vs arena-size chart sits beside the student grid. Each failure has a cause. (Fable, owner-delegated, 2026-11-12, D-004)
> - Constraints: local runs one core, sequential, main session only (D-002). Vendor never edited (D-001). Switch off equals vendor (DESIGN §4.3). Criteria pre-registered, never changed after a run.
> - G1 (benchmark, 2026-11-21), G2 (300 runs, 2026-11-27), G3 (verdict and memos, 2026-11-27). S1: option B quadtree with reservation (D-010).
> - M1 to M5 as in `../PLAN.md`. Kill R10: M3 not done by 2026-11-22 → S2 skipped.

Mission clauses used below: **M-score** = "collects more in 12 minutes". **M-cost** = "keep server cost small". **V-cause** = "each failure has a cause".

## 1. Result in one picture

```
Figure 1. Paper findings (left) mapped to our design parts (right)

 GCFA visit grid + upload at nest ─────────────> §3.1 steps 2-3 map + upload   APPLIED
 GCFA FIFO queue 20 pts / 25 s ────────────────> §3.1 step 1, cap 100, 2 s     PARTLY
 GCFA 3x3 min-count block, 9-cell tour ────────> §3.1 nearest available cell   NOT (by design)
 GCFA/ARPC spiral at target ───────────────────> §3.6 T4 (off) + D-018 hybrid  PARTLY
 GCFA map only in uninformed walk ─────────────> §3.1 step 6, q_map = 0        APPLIED
 GCFA/ARPC LOSS ON CLUSTERS (visited ≈ food) ──> no part yet  ◄── RISK  (P1, P2)
 GCFA/ARPC gain only in sparse tail ───────────> D-007 respawn: tail may not   RISK R5 (P5)
                                                 exist in 12 min
 GCFA future work: cells vs compute cost ──────> §5.2 benchmark, G1            APPLIED (answer)
 GCFA future work: logging interval ───────────> Table 6 rec_period fixed      NOT (P6)
 ARPC: no runtime numbers ─────────────────────> §5.1 queries.csv cost cols    APPLIED (new)
 ARPC DBSCAN + 1000 random candidates ─────────> option C, rejected D-010      NOT (by design)
 MDBSA central delivery → nest collisions ─────> no collision column           NOT (P4)
 MDBSA region assignment ──────────────────────> §3.6 T3 reservation           PARTLY
 MPFA multiple nests, dynamic depots ──────────> one nest (assignment)         NOT APPLICABLE
```

- Caption: Figure 1 maps each paper finding to the part of our design that takes it, or to the gap. Why: the two marked risks (clusters, sparse tail) come from the papers' own stated limits, and our design has no part for them yet.

Status counts (Table A, 33 rows): applied 5, partly 10, not applied 12, not applicable 6.

## 2. Table A: paper ideas and findings vs our design

Status words:

| Status | Meaning |
| --- | --- |
| applied | in the design, on by default in the `qmap` arm |
| partly | in the design in a changed form, or only as an off-by-default tuning candidate |
| not applied | could apply to our task, but the design has no part for it |
| not applicable | the assignment or a frozen decision rules it out |

Table A. One row per idea or finding

| # | Idea or finding | Source (paper, page) | Status | Where in our design | Why, or why not | Risk to our score |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Server keeps a visit structure. Robots upload logged positions at the nest | GCFA PDF pp. 3 to 4 | applied | §3.1 steps 2 and 3, D-010 | Core of the task. We store recency times, not counts, because respawn refills space (D-007) | low |
| A2 | Robot first-in first-out queue: 20 positions, one per 25 s | GCFA PDF p. 3 | partly | §3.1 step 1, Table 6 | Cap 100 and `rec_period` 2 s, from the task example. Same-cell points are skipped | low |
| A3 | Pick the 3 × 3 block with the minimum summed count | GCFA PDF pp. 3 to 4, Algorithm 1 | not applied | §3.1 query rule | We answer the nearest available minimum cell. Why: the professor names coarse cells as the limit. Nearest-first shortens trips in a fixed-time count | low |
| A4 | Visit a point in each of the 9 cells per trip, counter-clockwise | GCFA PDF pp. 3 to 4, Algorithm 1 | not applied | none | One target per trip. A block tour is a new tactic (P7) | medium (possible lost gain) |
| A5 | Spiral search at the chosen target | GCFA PDF pp. 3 to 4. ARPC [S-IS-4] | partly | §3.6 T4 (off), D-018 | Tuning candidate only. Exact form drafted in §5 | low |
| A6 | After the target, correlated random walk until a find or give-up | GCFA PDF pp. 3 to 4 | applied | §3.1 step 5 | Vendor uninformed walk runs at the target | low |
| A7 | Map used only in uninformed walk. Site fidelity and pheromone kept first | GCFA PDF p. 3. ARPC [S-IS-4] | applied | §3.1 step 6, `q_map` = 0. T2 departs from it | Keeps CPFA strengths. T2 (`q_map` > 0) is an S2 candidate only | medium if T2 wins (A9) |
| A8 | Clustered layout: cells near clusters get high counts. Robots are sent to empty corners | GCFA PDF p. 7 | not applied | none. §3.1 step 1 logs every `rec_period` and the pickup point | No mitigation in the design. GCFA kept fidelity and pheromone and still lost on Clustered (PDF p. 7). So `q_map` = 0 is not a proven guard | **high** on Clustered (P1, P2) |
| A9 | Clustered last 10 %: GCFA 680.7 s vs CPFA 593.5 s | GCFA Table III, PDF p. 6 | not applied | none | Same cause as A8 | high on Clustered |
| A10 | Cell selection costs O(n²). Future work: cells vs computation cost | GCFA PDF p. 7 | applied | §5.2 benchmark, G1 | Our benchmark measures it at 10 to 320 m. This answers their future work (Table B, B2) | none |
| A11 | Future work: queue size and logging interval | GCFA PDF p. 3 | not applied | Table 6, `rec_period` fixed at 2 s | S2 budget is full. A cost-only sweep fits the benchmark (P6) | none |
| A12 | Metric: time to collect all, time per 10 % | GCFA PDF pp. 4 to 6 | not applicable | §6.2: `collected` at 720 s | The assignment ranks by the 12 min count. With respawn, "all" never happens | none |
| A13 | Gain grows with arena: 581 s at 8 m to 1267 s at 16 m | GCFA Table II | not applied | score at 10 m only. Cost at 10 to 320 m | Assignment fixes 10 m. A score set at 14 m is a stretch (P8) | medium (gain may be small at 10 m) |
| A14 | Repulsive points: ρ = 2 s, at most λ = 50 | ARPC [S-IS-4] | partly | Table 6 `rec_period` 2 s, cap 100 | Same period. Larger cap from the task example | low |
| A15 | Nest clusters points every 5 s by DBSCAN | ARPC [S-IS-4] | not applied | option C, rejected (D-010) | No completeness bound. Batch cost not measured by ARPC | none |
| A16 | Target = first of 1000 random candidates outside all clusters | ARPC [S-IS-4] | not applied | §3.1 query rule | Our query is deterministic and complete | none |
| A17 | Powerlaw: isolated items near dense clusters fall in repulsive zones | ARPC Sec. 6.2 | not applied | none | Same cause as A8, other side | **high** on Powerlaw |
| A18 | Gain appears after 60 % (Clustered, Powerlaw) or 80 % (Random) collected. [CONFLICT]: p. 12 claims early gains | ARPC p. 9, p. 12 | not applicable | D-007 respawn | Our arena never empties. Only the p. 12 claim supports a gain in our window | high (R5: no score gain) |
| A19 | CPFA spends about 50 % of time on the last 12 % | ARPC p. 9 | not applicable | D-007 | No last 12 % with respawn | high (R5) |
| A20 | Future work: dynamic targets, communication limits, energy | ARPC p. 12 | partly | D-007, §3.1 step 3 (`T_stale`) | Respawn is a dynamic-target setting. Recency handles it. Whether they mean moving targets is a question (§6) | low |
| A21 | GA parameters fit one distribution. Clustered-evolved set doubles efficiency there | CPFA [S-LL-1] | partly | F3-a, D-008 | One shipped set in both arms. Report caveat: the set fits Random best (inference) | medium (map gain may differ by distribution for this reason) |
| A22 | Future work: adapt rules to sensed conditions in real time | CPFA p. 67 | not applied | none | The D-018 hybrid is a small case of it (§5) | low |
| A23 | Spiral gap g = 0.18 m, detection radius 0.13 m | MDBSA pp. 227 to 228 | partly | §3.6 T4, gap not set | §5 fixes g = 0.18 m | low |
| A24 | Server assigns robots to regions. A second robot walks the same spiral from the other end | MDBSA pp. 227 to 228 | partly | §3.6 T3 reservation | Reservation is assignment without fixed regions. No bidirectional pairing | low |
| A25 | Robots resume at the last find | MDBSA pp. 227 to 228 | applied | CPFA site fidelity, unchanged | Vendor behaviour kept | none |
| A26 | Central delivery raises nest collisions and can cap the gain | MDBSA p. 231 | not applied | no collision column in §6.5 | A null result could hide this cause (P4) | medium (V-cause) |
| A27 | Fixed 12 min count, Mann-Whitney U test | MDBSA pp. 229 to 230 | partly | §6.2 | Same metric. We pair by seed and decide by bootstrap interval | none |
| A28 | Several nests, return to the nearest | MPFA Sec. III, IV | not applicable | assignment: one collection zone | Out of task scope | none |
| A29 | Split time into travel, search, collision per robot | MPFA Sec. VI | partly | §6.5 `travel_s`, `search_s` | Collision missing (P4) | none |
| A30 | Depots move to the centroid of recent finds | dynamic-depots-2018 (abstract) | not applied | option C yield scoring, rejected | The P2 food halo is a small form of "go where finds are" | low |
| A31 | Transport network of mobile depots | transport-network-2020 (abstract) | not applicable | one nest | Changes the delivery task | none |
| A32 | Spiral wins in simulation. Outdoors CPFA is as good or better | cpfa-vs-ddsa-icra-2019 (abstract) | not applicable | simulation only | Report any T4 or hybrid gain as simulation-only | none |
| A33 | Per-robot rate should stay constant as swarm and arena grow | phd-thesis-2019 (abstract) | partly | G1 cost scaling only | Score at one arena size. Cost scaling is measured | none |

Count check: applied A1, A6, A7, A10, A25 (5). Partly A2, A5, A14, A20, A21, A23, A24, A27, A29, A33 (10). Not applied A3, A4, A8, A9, A11, A13, A15, A16, A17, A22, A26, A30 (12). Not applicable A12, A18, A19, A28, A31, A32 (6). Total 33.

## 3. Table B: where we do better than the papers, and the evidence still needed

Table B. Improvements over the papers' own work

| # | What we do better or newly | Paper gap it answers | Evidence still needed (path when it exists) | Honest limit |
| --- | --- | --- | --- | --- |
| B1 | Complete query at sensing-size cells, with cells that grow only where robots went (quadtree) | GCFA coarse 3 × 3 block (PDF pp. 3 to 4). ARPC sampling has no completeness bound | A and B equivalence on every query (M3 exit 3). `results/real/bench/bench.csv` | At 10 m, A and B give the same answers by construction (DESIGN §3.3). The gain is cost only, not score |
| B2 | Measured server cost: operations per query, memory, microseconds, vs arena size | GCFA future work (PDF p. 7). ARPC prints no runtime | `bench.csv`, `fig_cost_vs_arena.png`, `G1_verdict.json` (M3) | The student grid `n = 12` is our assumption. GCFA prints no number for n (open question). Ask the professor (§6) |
| B3 | Reservation spreads 24 robots across targets | Neither GCFA nor ARPC has one | S5 ablation arm without T3, `results/real/S5/` | S5 runs only if time remains (TASKS M5-05). Without S5, B3 is a design claim, not a result |
| B4 | Recency (`t_last`, `T_stale`), not visit counts, so respawned space can come back | ARPC future work "dynamic targets" (p. 12) | S2 candidate `T_stale` 300 (`tuning_table.csv`) | DESIGN §3.1 estimates a cell refills about once per 2,900 s (inference). So the effect inside 720 s may be nil |
| B5 | Nearest-first targets fit a fixed-time count | Papers optimise time to collect all | `dist_m`, `targets_reached_share`, `travel_s` in S3 | Nearest-first may sweep outward and lengthen trips over time (R4) |
| B6 | Travel fix T1: a map target is actually reached (no 5 s switch) | GCFA notes the CPFA 76 % switch chance (PDF p. 3) but reports no reach rate | `targets_reached_share` (SMK, S2 round 1) | None measured yet |
| B7 | Pre-registered, seed-paired design with an invariance check (switch off = vendor) | Papers report medians over 30 to 100 runs, no pairing | `results/real/S0/invariance.json`, `prereg/S3_eval.json`, `verdict.json` | Pairing is partial: respawn points diverge (R9) |
| B8 | Evaluation in the dense, respawning 12 min regime the papers never tested | GCFA and ARPC test "collect all" with no respawn | S3 verdict per distribution, plus the P5 per-minute reading | A null verdict is the likely outcome (R5). It is still a result with a cause |
| B9 | Proposed: food halo against the cluster failure (P2) | GCFA PDF p. 7, ARPC Sec. 6.2 | S2 round 4 on Clustered and Powerlaw, plus the P4 diagnostic | Not in the design yet. Needs a D-row |
| B10 | Proposed: hybrid spiral with a local crowd switch (P3, §5) | MDBSA congestion (p. 231). CPFA real-time adaptation (p. 67) | S2 round 4, `n_crowd_switch` if P4 lands | One candidate only (D-018). Novelty claim needs a gap check (`rules/research.md` §10) |

## 4. Next-work proposals, ranked

Ranking rule: `rules/core.md` Decision hierarchy. Eliminate any proposal that harms a mission-block line. Rank the rest by the line served, M-score first, then V-cause, then M-cost.

```
Figure 2. Where each proposal enters the milestone path

 M1 gate (open) ── M2 S1 headroom ── M3 bench + SMK ── M4 S2 tuning ── M5 eval
   │                 │                 │                 │              │
   P4 schema v2      P5 late-phase     P4 diagnostic     P1 guard       P8 stretch
   (MVP1 return)     reading           (near-food        P2 halo        sets
                     (S1 prereg)       share), P6 bench  P3 hybrid
                                       rec_period axis   (round 4)
```

- Caption: Figure 2 places each proposal on the milestone it fits. Why: P1 to P5 must be written before the pre-registration of the set they touch, or they cannot enter without tuning after seeing results.

### 4.1 Summary table

| Rank | Proposal | Lever | Mission line | DESIGN section changed | Schema change | Cost in 6 s runs (inference) | Milestone | Kill condition (written now) | Into S2 plan before pre-registration |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | Per-distribution no-harm guard in the S2 pick rule | (a) | M-score, V-cause | §6.3 rule 6 | no | 0 runs | M4 (in `prereg/S2_tuning.json`, M4-01) | `S1/headroom.json` has no σ per distribution by 2026-11-18 → guard dropped, D-row | **yes** |
| P2 | Food halo: drop buffered points within `r_halo` = 0.6 m of this trip's pickup (new tactic T5) | (a) | M-score (see mission note) | §3.1 step 1, §3.6 (T5), Table 6 | no | 30 runs, about 3 min | M4, S2 round 4 | not the round-4 pick on the pre-registered metric and guard → off. M3 not done by 2026-11-22 (R10) → dropped with S2 | **yes** |
| P3 | Hybrid search mode (D-018): parameter `search_mode` ∈ {`walk`, `spiral`, `hybrid`} (§5) | (a), (c) | M-score, V-cause | §3.6 (T4 becomes `search_mode`), Table 6, §6.3 rules 4 and 7 | no (yes only for the optional `n_crowd_switch` in P4) | 30 runs for `spiral` (already budgeted), 30 more for `hybrid` | M4, S2 rounds 3 and 4 | §6.3 rule 7 or Table 8 (`search_s / travel_s` < 1) fires → both spiral modes skipped, recorded. Not the pick → off | **yes** (D-018 says so) |
| P4 | Schema v2 (one bump). `points.csv` gets `kind` (`visit`, `pickup`). `runs.csv` gets `collision_s`, `collected_4min`, `collected_8min`, `near_pickup_target_share`, `n_crowd_switch` | (c) | V-cause | §5.1, §6.4, §6.5 | **yes**: back to MVP1, bump `schema_version` to 2 | 0 sim runs. Edits to done tasks M1-02, M1-04, M1-05, then mock regen and the M1 gate | M1 return, before M1-09, M2-03, M2-05, M2-09 | not decided by 2026-11-17 → keep v1, P5 and the P4 diagnostic are dropped and listed as gaps in the root-cause memos | no (but before M2-03) |
| P5 | Late-phase reading from S1, using the P4 columns | (c) | V-cause, informs R5 | §7 Table 8 (one reading) | needs P4 | 0 runs (S1 already planned) | M2, `prereg/S1_headroom.json` (M2-07) | P4 not taken → dropped. Else report-only | no (S1 pre-registration, before S1 runs) |
| P6 | Answer GCFA future work: present §5.2 as the cells-vs-cost answer, and add a `rec_period` axis (2, 8, 25 s) to the benchmark replay | (b), (c) | M-cost, Vision (cost chart) | §5.2 (inputs list) | no | 0 sim runs. Benchmark under `timeout 300` | M3 (M3-03, M3-04) | benchmark wall time > 300 s with the axis → axis dropped, D-row | no (G1 pre-registration instead) |
| P7 | Block tour: 2 × 2 minimum cells per trip, fixed order | (a) | M-score | §3.1 query rule, §3.6, `visit_map` interface (block query) | no | 30 to 60 runs | future work, after M5 | not proposed for this project. Reason: S2 is full, and it changes the done `visit_map` interface (M3-01, M3-02) | no |
| P8 | Stretch sets: F2-b no respawn, and a 14 m arena at the same density | (c) | V-cause (explains R5) | §6.1 (new sets) | no | 300 and 120 runs, about 30 and 12 min | M5, after S4 | S4 not done by 2026-11-26 → skipped, recorded | no (own pre-registration) |

Mission check: no proposal changes a mission, vision, goal, constraint or strategy line. P8 touches D-007 only for a sensitivity set, never the headline (DESIGN F2 already lists it).

### 4.2 Details

**P1. No-harm guard (clustered-layout risk, part 1).**
- Problem: §6.3 rule 6 picks by the sum over 3 distributions. A candidate can win on Random and lose on Clustered, and still pass. That is exactly the GCFA pattern (A8, A9).
- `q_map` = 0 is not a proven guard. GCFA kept fidelity and pheromone and still lost on Clustered (PDF p. 7).
- Rule (draft), two conditions for a new current best:
  1. It beats the current best on the sum (rule 6, unchanged).
  2. No distribution mean drops by more than δ_d.
- δ_d = 2 · σ_d · √(2/10).
- σ_d = S1 standard deviation of `collected` for distribution d.
- √(2/10) is the standard error factor for a difference of two 10-seed means (inference).
- δ_d comes from noise, as `rules/measurement.md` §1 asks. It is fixed before round 1.

**P2. Food halo (clustered-layout risk, part 2).**
- Robot-side rule: at a pickup, remove from the buffer every point within `r_halo` of the pickup position. Do not log the pickup point.
- Why robot-side: `visit_map` (M3-01, M3-02 done) needs no new operation. A server-side "unvisit" would change the interface.
- Value: `r_halo` = 0.6 m, one candidate. Read statically this pass:
  - Clustered: 4 clusters of 8 × 8 items (`xml10:44-47`, `ClusterWidthX`, `ClusterWidthY`, `NumberOfClusters`).
  - Item spacing = 3 · `FoodRadius` = 3 · 0.05 = 0.15 m (`lf.cpp:370`, `xml10:46`).
  - Cluster side ≈ 8 · 0.15 = 1.2 m. Half-side = 0.6 m.
  - Powerlaw groups have sides of powers of 2 at the same spacing (`lf.cpp:415`, `lf.cpp:438-445`). The largest is likely 8 items wide, so 0.6 m fits the largest group (inference, not traced to the end).
- Limit 1: points that other robots log near the cluster stay. Those robots likely find food there too, so they filter too (inference).
- Limit 2: nearest-first plus halo cells may pull map targets onto the nearest halo. That duplicates the pheromone branch.
- Limit 3, self-correcting: a robot that searches a depleted halo finds nothing. It logs visits with no pickup, so the cells close (inference).
- **Mission note:** the halo keeps searched ground near food "available". It serves M-score, not the literal "ground no robot has searched". Reading: ground with food is not searched out. Fable logs this reading in the D-row.

**P3. Hybrid (D-018).** Exact form in §5. S2 slot: §4.3.

**P4. Schema v2 (MDBSA congestion, and the M2 diagnostic).**
- The requested M2 diagnostic "share of map targets near food" does not fit M2:
  1. S1 runs the `cpfa` arm. It has no map targets.
  2. `points.csv` is header-only in `cpfa` (D-015).
  3. No file marks a pickup position. `points.csv` has `t_s, robot, x, y` only.
- So the diagnostic first exists in SMK (M3 exit 5, 3 runs) and S2 round 1 (30 runs). It needs `kind` in `points.csv`.
- Diagnostic (report-only, pre-registered in `S2_tuning.json`): `near_pickup_target_share` = share of map targets within 0.6 m of any earlier pickup.
- Every report number comes from `runs.csv` (DESIGN §6.5). D-013 rejected tools that read run folders. So each new reading needs a `runs.csv` column:

| Column | Source file | Filled by | Serves |
| --- | --- | --- | --- |
| `kind` (in `points.csv`) | controller upload | M2-03 logger, M3-06 | the near-pickup share |
| `collision_s` | vendor `iAntTagData.txt` `collisions_in_seconds` (`lf.cpp:286-295`) | M2-05 harness, both arms | MDBSA congestion (A26) |
| `collected_4min`, `collected_8min` | `forage_per_minute.csv` | M1-04 `collect_runs.py` | P5 |
| `near_pickup_target_share` | `points.csv` `kind`, `queries.csv` targets | M1-04 `collect_runs.py` | P2 cause |
| `n_crowd_switch` | `queries.csv` or the metrics line | M3-05 | P3 cause |

- Rejected alternative: a D-013 exception that lets `analyze.py --headroom` read `forage_per_minute.csv` directly. It splits the single contract.
- Cost: edits to done tasks M1-02 (`schema.py`), M1-04 (`collect_runs.py`), M1-05 (`make_mock_runs.py`). Then mock regen and the M1 gate (M1-09).
- Open tasks that must carry the columns: M2-03, M2-05, M2-09, M3-05, M3-06.
- Doing it now is cheapest. After M2-03 is coded, it also costs code rework.

**P5. Late-phase reading (respawn and late-phase point).**
- The papers gain late: GCFA in the last 20 % (Table III), ARPC after 60 % or 80 % (p. 9, [CONFLICT] with p. 12).
- Respawn keeps 256 items in the arena (D-007). So the global sparse tail never comes.
- But a local tail may come. The smoke collected 245 in 720 s with 256 items placed (DESIGN §1). So most initial items may turn over in 12 min (inference, one seed, Random).
- On Clustered, the clusters may deplete and the respawned items are uniform (BCM §4.6). Late minutes then look like Random at the same density (R8, inference).
- Confounds: minute 1 is a ramp-up from the nest. Pheromone use builds over time. Both change the rate on every distribution.
- So the reading skips minutes 0 to 4 and contrasts Clustered with Random.
- Reading (draft for `prereg/S1_headroom.json`, needs P4 columns):
  1. Per seed: late = `collected` − `collected_8min`. Mid = `collected_8min` − `collected_4min`.
  2. Per distribution: drop = mean(mid − late).
  3. Contrast: drop(Clustered) − drop(Random), 95 % bootstrap interval over the 30 seeds.
  - Interval above 0: Clustered slows late more than Random. A depletion phase exists inside 12 min. The map has a window there.
  - Interval covers 0: no Clustered-specific late phase. The root-cause memo cites this reading for R5.
- No tuning action is attached. So it cannot become tuning after seeing results.

**P6. GCFA future-work answer.** Report §5.2 as the measured answer to "cells vs computation cost" (GCFA PDF p. 7). Add a `rec_period` axis to the replay input. It answers "logging interval" (GCFA PDF p. 3) on the cost side, with no new simulation run. The score side of `rec_period` stays future work.

**P7, P8.** Listed so the report can name them as future work with a reason. Neither enters S2 or S3.
- P7 is deferred, not killed. S2 is full, and a block query changes the done `visit_map` interface.

### 4.3 S2 budget: what changes if P1 to P3 are taken

S2 has no free slot. Round 3 holds 4 candidates (§6.3 rule 4).

| Round | Candidates now | Candidates proposed |
| --- | --- | --- |
| 1 | start values | same |
| 2 | `q_map` 0.5, `q_map` 1.0, `r_res` 0.5, `r_res` 2.0 | same |
| 3 | `t_res` 30, `t_res` 120, `T_stale` 300, `spiral` on | `t_res` 30, `t_res` 120, `T_stale` 300, `search_mode` = `spiral` |
| 4 | none | `search_mode` = `hybrid`, `r_halo` on |

- Budget: 9 → 11 candidates. 270 → 330 runs. About 27 → 33 min (inference from the smoke wall time).
- Each round-4 candidate changes one parameter from the current best. `tune.py` accepts it (TASKS M4-02).
  - If round 3 picked `spiral`, `hybrid` adds only the crowd switch.
  - If round 3 kept `walk`, `hybrid` is still one parameter value.
- Round 4 adopts one winner at most, like every round. Halo and hybrid cannot both enter.
- Two rules can remove `spiral` from round 3 and put the 3 m cap there:
  1. §6.3 rule 7: `targets_reached_share` < 50 % in round 1.
  2. Table 8: `search_s / travel_s` < 1 in S1.
- If either fires, `hybrid` is skipped in round 4 and recorded. Round 4 then holds `r_halo` only.
- Lines that change together (one D-row, before M4-01):
  1. DESIGN §2 F4-a "3 rounds, 9 candidate settings ... 270 runs".
  2. DESIGN §6.1 S2 row "270" and the total "≈ 1,300" (becomes ≈ 1,360).
  3. DESIGN §6.3 Table 6 (`spiral` row → `search_mode`, new `r_halo` row), rules 2 to 7.
  4. DESIGN §7 Table 7 and Figure 6 "S2 (270 runs)".
  5. PLAN M4 line "S2 tuning (270 runs)".
  6. TASKS M4 exit 1 "270 runs" and M4-03 "rounds 1 to 3".
- R10 is unchanged: if M3 is not done by 2026-11-22, all of S2 is skipped.

## 5. Draft: exact form of the D-018 hybrid rule (for DESIGN §3.6)

```
Figure 3. One map-target trip under search_mode = hybrid

 nest ──T1 travel──> map target ──> square spiral, outward, gap g ──> spiral end ──> vendor walk
                                       │          │                                   (CRW)
                                       │          └─ 2nd collision event ──> vendor walk
                                       ├─ food found ──> vendor RETURNING (spiral cleared)
                                       └─ vendor give-up test (unchanged) ──> RETURNING
```

- Caption: Figure 3 shows when a hybrid robot leaves the spiral. Why: a collision pushes the robot off the spiral path, so the spiral's no-overlap property is already lost.

| Item | Rule | Why |
| --- | --- | --- |
| Parameter | `search_mode` ∈ {`walk` (start), `spiral`, `hybrid`}. Replaces the T4 `spiral` switch | One parameter, so one S2 candidate per value |
| Scope | Only trips with `isMapTarget` at arrival. Fidelity, pheromone and random trips run the vendor walk | Keeps the CPFA strengths (A7) |
| Spiral shape | Square spiral, outward from the target point. Leg lengths g, g, 2g, 2g, 3g, ... | MDBSA square spiral (pp. 227 to 228) |
| Gap | g = 0.18 m, fixed | MDBSA value (p. 228). Detection radius 0.13 m (BCM §3.3) gives a 0.26 m strip, so 0.18 m overlaps safely |
| Extent | Stop when the half-side reaches `r_res` | Stays inside the reserved disk in space. Not in time: a full spiral takes about 139 s, `t_res` is 60 s (limit below) |
| Step targets | Each step target lies `SearchStepSize` (0.08 m) further along the spiral path. It replaces the CRW step at `ctrl.cpp:358-388`. A step outside the forage range or inside the nest exclusion disk jumps to the next leg | Same step length as the vendor walk, so the give-up cadence stays the same (next row) |
| Give-up | Vendor test unchanged (`ctrl.cpp:332-334`) | The test runs only when the robot is within the target tolerance (0.224 m, BCM §1.5) on a 5 s tick. With 0.08 m steps the robot is within it on every tick, as in the walk (inference). Corner waypoints 2 m apart would cut the test rate and change the give-up rate (D-009) |
| On pickup | Vendor `RETURNING`. Spiral state cleared. No resume | Site fidelity already resumes at the find (A25) |
| Spiral end | Vendor uninformed walk for the rest of the trip | GCFA order: spiral, then walk (PDF pp. 3 to 4) |
| Crowd signal (`hybrid` only) | Count collision events since the spiral began. Event = a control step where `collisionFlag` is true and no event was counted in the previous 1.0 s | Read-only, local, no new sensor, no random draw |
| Event window | 1.0 s = the longest vendor `collisionDelay` (0.5 to 1.0 s, `BaseController.cpp:328-329`) | Line 310 retests every tick. One encounter can set the flag on several ticks while the robot turns. The window merges them into one event |
| Switch | At the 2nd event (`c_crowd` = 2, fixed, not tuned) → leave the spiral, vendor walk | One event can be a single robot passing. Fixed before any run (inference) |
| Determinism | No new random draw. Nothing runs when the switch is off | DESIGN §4.1 |
| Log | `n_crowd_switch` per run, only if P4 lands. Else none | Avoids a schema change for one candidate |

Code facts behind the crowd signal (read this pass):
- `collision_counter++` runs on every control step with a detection (`BaseController.cpp:304-315`, called from `Move()` at line 362).
- So the counter counts ticks, not contacts. The vendor file prints it divided by `2 · ticks_per_second` (`lf.cpp:294`).
- A threshold on the counter would mix contact count and contact length. So the rule counts windowed events of `collisionFlag` instead.
- `Move()` returns early while `Wait()` is true (line 360). `collisionFlag` then keeps its last value. The 1.0 s window stops a long wait from counting twice (inference, developer checks at M3).
- Each detection draws `RNG->Uniform` (line 328). That is vendor behaviour in both arms. The hybrid adds no draw.

Limits of this form:
- After `t_res` (60 s) the reserved cells free up. Another robot may then get a target inside a running spiral. The crowd switch is the answer to that case.
- The window value 1.0 s and `c_crowd` = 2 are fixed by reasoning, not measured. S2 tests one setting only (D-018).

Expected size (inference, for the run list):
- A full spiral to half-side 1.0 m is about (2.0 m)² / 0.18 m ≈ 22 m of path, about 139 s at 0.16 m/s.
- On Random, 256 items over about 97 m² give about 0.69 items per metre of fresh 0.26 m strip.
- So a spiral robot on Random likely finds food within about 1.5 m. Spiral and hybrid effects may show only between clusters.

## 6. Questions for the professor

1. Is the graded run respawn on, as shipped (D-007)? Does ARPC's "dynamic targets" (p. 12) mean respawn, or moving targets?
2. Which grid size n did the GCFA student grid use? Our benchmark assumes n = 12.
3. Is "ANT-2025" (cited in ARPC) the same method as the arXiv GCFA paper? Can we get the text?
4. Which nest radius do you grade: file value 0.25, or effective 0.25 m (F1)?
5. Which CPFA parameter set is "original" for Clustered and Powerlaw (F3)?
6. Is there a paper behind the `Collision_Free_CPFA` changes?

## 7. Runs for the main session (no run by this agent)

Each claim below needs a measured number. None is run here.

| Claim (inference now) | Run or read that answers it | Set | Pre-registered in |
| --- | --- | --- | --- |
| A late depletion phase exists inside 12 min on Clustered | P5 reading on `collected_4min`, `collected_8min` (P4) | S1 (90 runs, planned) | `prereg/S1_headroom.json` (M2-07) |
| With 0.08 m spiral steps the give-up test rate equals the walk's | give-ups per search minute, `spiral` vs `walk` (needs a count in the metrics line) | S2 rounds 1 and 3 | report-only |
| σ per distribution for the P1 guard | `analyze.py --headroom` | S1 | same |
| Map targets land near earlier pickups on Clustered | P4 diagnostic | SMK, S2 round 1 | `prereg/S2_tuning.json` (M4-01) |
| Halo and hybrid change the score | S2 round 4 | S2 (60 runs added) | same |
| Spiral finds food within about 1.5 m on Random | `search_s / n_departures` per arm | S2 rounds 1 and 3 | report-only |
| `rec_period` changes server cost | benchmark replay axis | M3 bench | `prereg/G1_bench.json` (report-only rows) |

## 8. Decisions this file asks Fable to log

1. P1 guard rule and its δ_d formula (before M4-01).
2. P2 halo as T5, with the mission reading in §4.2 (before M4-01).
3. P3 form in §5, `search_mode` replacing `spiral`, round 4 (before M4-01. D-018 requires it before S2 pre-registration).
4. P4 schema v2, MVP1 return (by 2026-11-17, before M1-09, M2-03, M2-05, M2-09).
5. P5 reading added to `S1_headroom.json` (before the S1 run, only with P4).
6. S2 budget 270 → 330 runs, 3 → 4 rounds, and the six lines in §4.3 (one D-row).
