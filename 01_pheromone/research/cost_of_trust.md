# Cost of trust: what each defense needs, and what ours cost (T-E, M8-01)

- Task tag: CT
- Accessed: 2026-11-11
- Purpose: one table that sets each defense's information need beside its measured cost. Spec: `decisions/2026-11-11_fable_tracks.md` "M8 = T-E" [S-CT-9].
- No runs. Every measured number is copied from a saved file named in the cell. No number is computed here.
- Inputs: `research/lu_lineage.md` (S-LL), `research/taros_defense_spec.md` (S-TB), `research/pheromone_research.md` (S-PH), `DESIGN.md` §2.1 and §3.4, `DESIGN_M5.md`, `DESIGN_M6.md`.
- Earlier IDs are reused by name. Their rows are copied into this file's Sources. New sources get [S-CT-n].
- Status: complete, one pass. 1 fetch call (Strobel et al. 2018 PDF, pages 543 to 545 and 547 to 548 read as page images).
- Abbreviations: density-based spatial clustering of applications with noise (DBSCAN), identifier (ID), Towards Autonomous Robotic Systems 2024 (TAROS 2024), International Conference on Computer, Control and Robotics 2024 (ICCCR 2024), confirm count k (`confirm_k`), lockout seconds t (`t_lock`), DMVD (voter model strategy, Strobel p. 544), DMMD (majority voting strategy, p. 544), DC (direct comparison, p. 544). The paper prints no longer form of DMVD or DMMD on pp. 542 to 548.

## Summary counts

- Table 1 rows: 8 (literature 4, ours 4). Rows verified 4, partial 3, inference 1 (ID arm design cells. Its measured cells are verified)
- Table 2 rows: 5 (M6 block, seeds 321 to 360), all verified. G cells "not in file"
- Sources: 15 new (S-CT), 7 reused (S-LL, S-PH, S-TB)
- Unverified cells: 0. Cells "not stated" by the source: 9 (TAROS 4, ICCCR 5)
- Open questions: 7

## 1. Terms

- Decision: one choice a robot makes about trust.
  - In Strobel: one opinion update.
  - In the pheromone papers: one trail-follow choice.
  - In ours: one follow, mask or abort choice on a suspect point.
- Messages per decision: robot-to-robot or robot-to-store messages the defense needs per decision. Reading the pheromone medium is not a message.
- Shared store: a data store beyond the pheromone medium that several robots read or write. The floor grid itself does not count.
- Per-robot memory: defense state each robot holds.
- Central component: a process that sees all robots' data during the run.
- Measured d = 0 cost: G(0) = F(0, defense) − F(0, off), food per run. Negative means food lost with no attacker.
- Measured d = 2 gain: G(2) = F(2, defense) − F(2, off), food per run, 2 detractors.
- Intervals: 95 % paired percentile bootstrap, 10,000 resamples, paired on seed (`tools/g2_stats.py` line 91 [S-CT-5], `results/real/v5/verdict.json` "bootstrap" [S-CT-3]).
- Float noise is trimmed only (example: 0.3999999999999986 is written 0.40). Signs are kept as in the files.
- Seed blocks and off baselines differ between files. So rows from different files are never subtracted here.
- Cell tags: (verified) = read in the paper or our own saved file. (partial) = abstract, secondary file, or label from a dispatch. (inference) = our reading.

## 2. Cost-of-trust table

Table 1. Information each defense needs, and the measured food cost on our testbed (ours only)

| Defense | Messages per decision | Robot IDs needed | Shared store needed | Per-robot memory | Central component | Measured d = 0 cost [95 % interval] | Measured d = 2 gain [95 % interval] | Sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Blockchain swarm (Strobel et al. 2018) | DMVD and DMMD: one vote transaction every 5 ticks of dissemination. DC: one vote per dissemination state. Plus one `applyStrategy` transaction per opinion update, p. 545 (verified). About 160 bytes per transaction vs 2 or 4 bytes in the classical approach, p. 547 (verified) | Yes. Each robot registers its public key (`registerRobot`). Byzantine robots are blacklisted by public key, pp. 544 to 545 (verified) | Yes. A blockchain with a smart contract. "Each robot keeps a separate copy", p. 544 (verified) | Full chain copy. About 10 MB (DMVD, DMMD) or 4 MB (DC) per 15 min run. Grows linearly with time and robots, p. 548 (verified) | Setup only. An auxiliary node publishes the contract, then stops mining after registration, pp. 544 to 545 (verified). During the run, consensus is "fully decentralized", p. 547 (verified) | not measured on our testbed | not measured on our testbed | [S-LL-2] |
| TAROS 2024 DBSCAN + creator-ID graph (Luna, Lu) | Not stated. Every trail with its creator ID must reach one place (inference) | Yes. Each waypoint carries a creator ID, p. 310 (verified) | Yes. Not stated in the paper. DBSCAN and the creator graph need all trails in one place (inference) | Not stated. Defense state: strikes per robot, travel-time estimate per trail, pp. 310 to 311 (verified). Who holds it: not stated | Not stated who runs the defense. A central or nest-side store is implied (inference) | not measured on our testbed | not measured on our testbed | [S-TB-1], [S-PH-1] |
| ICCCR 2024 quarantine (Luna, Lu) | Not stated in abstract (partial) | Not stated in abstract (partial) | Not stated in abstract. Per the abstract paraphrase, regions are merged by distance to save storage (partial) | Circular quarantine regions around fake resources, merged by distance (partial). Whether per robot: not stated in abstract | Not stated in abstract (partial) | not measured on our testbed | not measured on our testbed | [S-LL-10], [S-TB-3], [S-TB-6] |
| Cautionary pheromone (Aswale et al. 2022) | 0. No communication beyond the pheromone grid, per `pheromone_research.md` Q1 (verified) | No (verified) | No. A cautionary layer in the same grid medium (verified) | Patience ρ per ant, falls while searching, refills on food (verified) | None in the defense (inference from no IDs and no messages) | not measured on our testbed | not measured on our testbed | [S-PH-6] |
| Our v3 (suspect mark, mask and cone, k = 1, t = 0) | 0. The controller reads the pheromone sensor only, `DESIGN.md` §2.1, §3.4 (verified) | No. The controller never receives a deposit's creator, `DESIGN.md` §2.1 (verified) | No. Private suspect list, `DESIGN.md` Fig. 1 (verified) | Up to `n_mem` 16 suspect points (centroid, count), oldest dropped, `DESIGN.md` §3.4, Table 2 (verified) | None for the defense. Loop functions only play the floor sensor, `DESIGN.md` §2.1 (verified) | −1.9 [−5.0, 1.5], seeds 1 to 10, `results/real/g2_stats.csv` row d = 0 (partial: "v3" label from the dispatch, level from [S-CT-5]). Same rule, other blocks: k1t0 −2.7 [−4.5, −0.85], seeds 221 to 260, `results/real/v5/g2_stats.csv` (verified). `t_lock` 0 control −6.15 [−8.25, −4.05], seeds 11 to 30, `results/real/v2/verdict.json` `lock0_control_G.d0` (verified) | 2.3 [−0.7, 5.2], `results/real/g2_stats.csv` row d = 2 (partial). k1t0 4.575 [2.325, 6.825], `results/real/v5/g2_stats.csv` (verified). `t_lock` 0 control 2.35 [−1.9, 6.35], `results/real/v2/verdict.json` `lock0_control_G.d2` (verified) | [S-CT-1], [S-CT-2], [S-CT-4], [S-CT-5], [S-CT-6] |
| Our v5 primary arm k2t10 (confirm twice, 10 s lockout) | 0. Same controller path as v3, `DESIGN_M5.md` §1 (verified) | No (verified, `DESIGN_M5.md` §1 rule 8: memory is private) | No (verified) | Same 16-slot queue. Each point adds a `Count`. Pending below k = 2, `DESIGN_M5.md` §1 (verified). Plus a FOLLOW-entry lockout of 10 s after a cone abort, `CHANGELOG.md` v4 (verified) | None (verified) | 0.125 [−0.975, 1.15], seeds 221 to 260, `results/real/v5/g2_stats.csv` row k2t10 d = 0, same in `results/real/v5/verdict.json` `failure.d0_cost` (verified) | 2.75 [0.40, 4.975], `results/real/v5/g2_stats.csv` row k2t10 d = 2, same in `results/real/v5/verdict.json` `metric_G2` (verified) | [S-CT-2], [S-CT-3], [S-CT-7] |
| Our k1t10 (v2 lockout, k = 1, 10 s) | 0 (verified, `DESIGN_M5.md` §4 "v2 lockout") | No (verified) | No (verified) | 16-slot queue, every point active at count 1, plus 10 s lockout, `DESIGN_M5.md` §1.1 (verified) | None (verified) | −3.55 [−5.4, −1.725], seeds 221 to 260, `results/real/v5/g2_stats.csv` row k1t10 d = 0 (verified). Same rule, seeds 11 to 30: −6.7 [−9.7, −3.85], `results/real/v2/verdict.json` `item_11_failure.d0_cost` (verified) | 5.05 [2.025, 7.975], `results/real/v5/g2_stats.csv` row k1t10 d = 2 (verified). Seeds 11 to 30: 4.05 [0.85, 7.25], `results/real/v2/verdict.json` `item_8_metric_G2` (verified) | [S-CT-2], [S-CT-4], [S-CT-7] |
| Our ID adapted arm (M6, draft design) | In sim 0. A real swarm "would need a nest server or broadcast", `DESIGN_M6.md` §1 (inference). Store inputs per check: deposit-run start, follow start, peak, pickup, `DESIGN_M6.md` §2 (inference) | Yes. Per-cell owner ID `owner[2][1600]`, `DESIGN_M6.md` §2 (inference, draft) | Yes. Trail store and owner grid in the loop functions, `DESIGN_M6.md` §1 row 13 (inference, draft) | None. The controller is unchanged and its suspect rule is off, `DESIGN_M6.md` §1, §6 (inference, draft) | Yes. The loop functions as a central trail store, `DESIGN_M6.md` §1 row 13 (inference, draft) | id vs off G(0) and its interval: not in file (`results/real/id_arm/verdict.json`, `contrast.csv`). Means only, seeds 321 to 360: F(0, id) 77.775, F(0, off) 81.4, `results/real/id_arm/contrast.csv` (verified). Honest robots isolated per run at d = 0: 9.05, `results/real/id_arm/verdict.json` `isolation_mean_per_run.d0.honest_isolated` (verified) | id vs off G(2) and its interval: not in file. Means only: F(2, id) 52.7, F(2, off) 43.85, `results/real/id_arm/contrast.csv` (verified). Judged Δ = F(2, id) − F(2, k1t10): 4.375 [2.25, 6.45], verdict "differs", `results/real/id_arm/verdict.json` `metric_delta2` (verified). Honest isolated per run at d = 2: 15.925, `isolation_mean_per_run.d2.honest_isolated` (verified) | [S-CT-8], [S-CT-9], [S-CT-13], [S-CT-14], [S-CT-15] |

Table 2. Second measured block: M6 arms on one shared seed block, seeds 321 to 360 (40 seeds)

- All values copied from `results/real/id_arm/contrast.csv` and `results/real/id_arm/verdict.json` [S-CT-13], [S-CT-14].
- These files hold mean food F per arm, not G against off. So G and its interval are "not in file".
- Do not compare Table 2 rows with Table 1 rows. Seed blocks and off baselines differ.

| Arm (M6 name) | F(0) mean | F(2) mean | d = 0 cost G(0) [95 % interval] | d = 2 gain G(2) [95 % interval] | Honest isolated per run, d = 0 / d = 2 | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| off | 81.4 | 43.85 | reference | reference | not in file (no ID defense) | verified |
| v3 | 75.15 | 45.875 | not in file | not in file | not in file (no ID defense) | verified |
| k1t10 (best no-ID arm, `best_no_id_arm`) | 75.175 | 48.325 | not in file | not in file | not in file (no ID defense) | verified |
| v5 (k2, t10) | 80.375 | 46.575 | not in file | not in file | not in file (no ID defense) | verified |
| id (adapted arm) | 77.775 | 52.7 | not in file | not in file. Δ vs k1t10 at d = 2: 4.375 [2.25, 6.45], "differs" | 9.05 / 15.925 | verified |

- Detractors isolated per run (id): 0.0 at d = 0, 2.0 at d = 2. Seeds with no detractor isolated at d = 2: 0. Failure not triggered (`verdict.json` `failure`).
- Frozen values judged: margin 5.4, eps 0.3 m, minPts 2 (`verdict.json` `frozen`, `prereg/defense_id_arm.md`) [S-CT-15].

What Tables 1 and 2 show (the information-vs-cost trade-off):

1. More information buys detection. Strobel needs keys and a ledger. TAROS needs creator IDs and one trail store.
2. Low information was not free on our testbed. The v3 rule lost food at d = 0 on 20 and 40 seeds.
3. Confirm-twice removed that cost: k2t10 d = 0 is 0.125 [−0.975, 1.15]. Its d = 2 gain stayed above 0.
4. On seeds 321 to 360 the ID arm beat k1t10 at d = 2: Δ 4.375 [2.25, 6.45].
5. Its price is trust in honest robots. It isolated 9.05 per run at d = 0 and 15.925 at d = 2.

```
Figure 1, panel A. Information needed (x) against measured d = 0 cost (y), ours only

 y = G(0), food per run (negative = food lost, rounded to the nearest row)
 x = information needed, ordinal (inference): LOW < MID < HIGH

        | LOW                     | MID                     | HIGH
        | own memory + medium     | IDs + shared store      | keys + ledger copy
        | 0 messages              | central store           | signed transactions
 -------+-------------------------+-------------------------+--------------------
    0 --| k2t10 +0.125 -----------|-------------------------|-------------- 0 line
   -1   |                         |                         |
   -2   | v3 -1.9 (s 1-10)        |                         |
   -3   | k1t0 -2.7 (v3 rule)     |                         |
   -4   | k1t10 -3.55             |                         |
   -5   |                         |                         |
   -6   | lock0 -6.15 (v3 rule)   |                         |
   -7   | v2 -6.7 (k1t10 rule)    |                         |
 -------+-------------------------+-------------------------+--------------------
 G(0)   |                         | ID arm: not in file     |
 n/a    |                         | (see panel B)           |
 -------+-------------------------+-------------------------+--------------------
 not on | cautionary pheromone    | TAROS 2024              | blockchain 2018
 our    | (Aswale 2022)           | ICCCR 2024 (x unclear,  | (Strobel)
 testbed|                         |  abstract only)         |
```

```
Figure 1, panel B. M6 block, seeds 321 to 360: mean food at d = 0 (y) by information needed (x)

 y = F(0) mean, food per run, rounded to the nearest row. Off reference = 81.4
 x = information needed, ordinal (inference)

        | LOW                     | MID                     |
        | 0 messages, no IDs      | IDs + central store     |
 -------+-------------------------+-------------------------+
   81 --|-------------------------|-------------------------|-- off 81.4 reference
   80   | v5 80.375               |                         |
   79   |                         |                         |
   78   |                         | id 77.775               |
   77   |                         | (honest isolated 9.05)  |
   76   |                         |                         |
   75   | v3 75.15, k1t10 75.175  |                         |
 -------+-------------------------+-------------------------+
 d = 2  | v3 45.875, v5 46.575,   | id 52.7, honest         |  off 43.85
 F mean | k1t10 48.325            | isolated 15.925         |
```

- Caption: Figure 1 places each defense by information needed and by its measured d = 0 cost (panel A) or mean d = 0 food on one shared seed block (panel B). Why: it asks whether more information removes the no-attack cost, and panel B shows the ID arm pays in honest isolations instead.
- Intervals for panel A points: Table 1. Seeds: v3 1 to 10, k1t0 k1t10 k2t10 221 to 260, lock0 and v2 11 to 30. Panel B: Table 2, means only, no intervals in file.
- Source folder: `results/real/` (`g2_stats.csv`, `v5/g2_stats.csv`, `v5/verdict.json`, `v2/verdict.json`, `id_arm/contrast.csv`, `id_arm/verdict.json`).

## Selection log

| Entity | Decision | Rule |
| --- | --- | --- |
| Strobel et al. 2018 blockchain | kept | named in dispatch. Pages 543 to 545, 547 to 548 read as page images |
| Luna, Lu TAROS 2024 | kept | named in dispatch. Read in full in `taros_defense_spec.md` |
| Luna, Lu ICCCR 2024 | kept, partial | named in dispatch. Abstract only. Full text returned HTTP 403 earlier, not retried |
| Aswale et al. 2022 cautionary pheromone | kept | named in dispatch. Read in full in `pheromone_research.md` |
| Our v3 | kept | named in dispatch. Three saved measurements of the same rule, all listed |
| Our v5 k2t10 | kept | named in dispatch. Primary M5 arm (D-051) |
| Our k1t10 | kept | named in dispatch. Same rule as v2, both measurements listed |
| Our ID adapted arm | kept, measured | named in dispatch. M6 verdict "differs" read 2026-11-11 |
| M6 no-ID arms v3, k1t10, v5 (seeds 321 to 360) | kept, Table 2 | coordinator message: same seeds as the ID arm |
| Our k2t0 | not rowed | not in the dispatch row list. Values stay in `results/real/v5/g2_stats.csv` |
| Luna, Lu UR 2024 | not rowed | not in the dispatch row list. Abstract only |

## open_questions:

- v3 d = 0 cost differs by seed block: −1.9 [−5.0, 1.5] (seeds 1 to 10) vs −2.7 [−4.5, −0.85] (221 to 260) vs −6.15 [−8.25, −4.05] (11 to 30). Cause not checked here.
- `results/real/g2_stats.csv` does not state its interval level or its defense version. The 95 % level and the "v3" label are taken from `tools/g2_stats.py` and the dispatch.
- ICCCR 2024 full text unread. IDs, messages and the central component of quarantine are unknown.
- TAROS 2024 does not say who runs the defense or how trails are shared.
- ID arm design cells (messages, IDs, store, memory, central) come from `DESIGN_M6.md`, status draft. Not checked against the v6 code.
- M6 files hold no G against off and no interval for any arm except Δ(2) vs k1t10. G(0) and G(2) for the M6 block are "not in file". A judge run that writes them would fill Table 2.
- Strobel per-decision transaction count depends on dissemination time. No single number per decision is printed.

## Sources

Reused rows, copied so every ID resolves here:

[S-LL-2] Managing Byzantine Robots via Blockchain Technology in a Swarm Robotics Collective Decision Making Scenario | https://ifaamas.csc.liv.ac.uk/Proceedings/aamas2018/pdfs/p541.pdf | published: 2018-07, AAMAS 2018 | accessed: 2026-11-11 | type: paper | note: pages 543 to 545 and 547 to 548 read as page images in this pass
[S-LL-10] Controlling Adversarial Pheromone-Based Infections via Quarantine Strategies in Foraging Robot Swarms | https://api.openalex.org/works/doi:10.1109/ICCCR61138.2024.10585509 | published: 2024-04-19, ICCCR 2024 pp. 251 to 256 | accessed: 2026-11-11 | type: aggregator | note: OpenAlex record, abstract paraphrased
[S-PH-1] Robust Mitigation Strategy for Misleading Pheromone Trails in Foraging Robot Swarms | https://par.nsf.gov/servlets/purl/10593555 | published: 2025, TAROS 2024 LNAI 15052 pp. 307 to 319, DOI 10.1007/978-3-031-72062-8_27 | accessed: 2026-11-11 | type: paper | note: read in full 2026-11-10
[S-PH-6] Hacking the Colony: On the Disruptive Effect of Misleading Pheromone and How to Defend Against It | https://arxiv.org/abs/2202.01808 | published: AAMAS 2022 pp. 27 to 34 | accessed: 2026-11-10 | type: paper | note: all 8 pages read in the earlier pass
[S-TB-1] Robust Mitigation Strategy for Misleading Pheromone Trails in Foraging Robot Swarms | https://par.nsf.gov/servlets/purl/10593555 | published: 2025, TAROS 2024 LNAI 15052 pp. 307 to 319 | accessed: 2026-11-11 | type: paper | note: pp. 307 to 317 read as page images. Same document as S-PH-1
[S-TB-3] Semantic Scholar record: Controlling Adversarial Pheromone-Based Infections via Quarantine Strategies in Foraging Robot Swarms | https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/ICCCR61138.2024.10585509 | published: ICCCR 2024 | accessed: 2026-11-11 | type: aggregator | note: abstract read as a fetch-tool paraphrase
[S-TB-6] UTRGV ScholarWorks: Controlling Adversarial Pheromone-Based Infections via Quarantine Strategies in Foraging Robot Swarms | https://scholarworks.utrgv.edu/cs_fac/175 | published: ICCCR 2024 | accessed: 2026-11-11 | type: official | note: landing page read. PDF returned HTTP 403

New sources (local saved files and designs):

[S-CT-1] v3 G2 statistics, seeds 1 to 10 | results/real/g2_stats.csv | published: saved run output | accessed: 2026-11-11 | type: dataset | note: rows d = 0 and d = 2 read
[S-CT-2] v5 G2 statistics, 4 on-arms, seeds 221 to 260 | results/real/v5/g2_stats.csv | published: saved run output | accessed: 2026-11-11 | type: dataset | note: rows k1t0, k1t10, k2t10 at d = 0 and d = 2 read
[S-CT-3] M5 verdict, defense v5 | results/real/v5/verdict.json | published: saved run output | accessed: 2026-11-11 | type: dataset | note: lines 1 to 105 read (verdict, bootstrap, metric_G2, d0_cost, main_effects)
[S-CT-4] M4 verdict, defense v2 lockout | results/real/v2/verdict.json | published: saved run output | accessed: 2026-11-11 | type: dataset | note: read in full
[S-CT-5] G2 statistics code | tools/g2_stats.py | published: repo code | accessed: 2026-11-11 | type: code | note: line 91 docstring states the 95 % paired percentile bootstrap
[S-CT-6] Pheromone foraging design | DESIGN.md | published: repo design | accessed: 2026-11-11 | type: design | note: §2, §2.1, §3.4, Table 2 read
[S-CT-7] M5 design, defense v5 | DESIGN_M5.md | published: 2026-11-11 | accessed: 2026-11-11 | type: design | note: read in full
[S-CT-8] M6 design, ID adapted arm | DESIGN_M6.md | published: 2026-11-11, draft | accessed: 2026-11-11 | type: design | note: read in full
[S-CT-9] Fable decision: tracks M5 to M8 | decisions/2026-11-11_fable_tracks.md | published: 2026-11-11 | accessed: 2026-11-11 | type: design | note: read in full
[S-CT-10] Code change log | CHANGELOG.md | published: repo log | accessed: 2026-11-11 | type: design | note: v4 row (FOLLOW-entry lockout `t_lock`) and v5 row read via search
[S-CT-11] Pre-registration: defense v2 lockout | prereg/defense_v2_lockout.md | published: repo prereg | accessed: 2026-11-11 | type: design | note: seeds 11 to 30, 95 % bootstrap line read via search
[S-CT-12] Decision log | DECISIONS.md | published: repo log | accessed: 2026-11-11 | type: design | note: D-028 and D-051 rows read via search
[S-CT-13] M6 verdict, ID adapted arm | results/real/id_arm/verdict.json | published: saved run output | accessed: 2026-11-11 | type: dataset | note: read in full
[S-CT-14] M6 contrast, mean food per arm and d | results/real/id_arm/contrast.csv | published: saved run output | accessed: 2026-11-11 | type: dataset | note: read in full
[S-CT-15] Pre-registration: ID adapted arm | prereg/defense_id_arm.md | published: repo prereg | accessed: 2026-11-11 | type: design | note: read in full
