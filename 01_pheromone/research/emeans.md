# E-means clustering: what it is, and does it fit the pheromone defense?

- Question (owner, 2026-11-11): "yesterday we do have e-means clustering came out? can we use this to this project also?"
- Scope: identify "e-means clustering". Then check its fit against the Luna and Lu defense [S-PH-1] and our suspect-end defense (`../DESIGN.md` §3.4).
- Method: read, grep, and web only. No runs. Source IDs use tag EM.
- Summary counts: kept 2, rejected 3, sources 9, unverified 1.

## 1. Local search

- Command: case-insensitive grep for `e-means|emeans|e_means` over `/Users/tio/Documents/mscs_utrgv`.
- Result: no mention found.
- The two hits are false positives (`tab:a2-future-means` in a deep-learning teaching assistant book chapter).

## 2. Findings table

| Candidate | What it is | Date | Verification | Source |
| --- | --- | --- | --- | --- |
| e-means (2026), the likely match | Mini-batch k-means with exponential moving average (EMA) centroid updates. Paper title: "e-means: outperforming k-means (in one-tenth the epochs)" | arXiv v1 submitted 2026-11-06 | verified | [S-EM-1] |
| e-means authors and lab | Bessa, Mazaré, Szilvasy, Touvron, Picard, Douze, Jégou. "Developed at Meta FAIR" (Meta Fundamental AI Research) | 2026 | verified | [S-EM-1], [S-EM-3], [S-EM-4] |
| e-means claim | Reaches a lower loss than Lloyd k-means at 25 epochs within 1.4 to 2.6 epochs. 10 to 45 times graphics processing unit (GPU) wall-clock speedup | 2026-11-06 | verified (self-reported by authors) | [S-EM-1] |
| e-means code | Python, in the Faiss repository under `contrib/e_means`. `Emeans(d, k, nepochs=5, ...)`. `d` and `k` are required | on Faiss main. No tagged Faiss release seen | verified | [S-EM-4] |
| e-means code dates | Commits on `contrib/e_means`: earliest seen 2026-11-04 ("Separate Emeans implementations"). Others on 11-07, 11-09, and 11-11 | 2026-11-04 to 2026-11-11 | partial (commit list page cut off, older commits may exist) | [S-EM-5] |
| e-means low-dimension commit | Commit title (2026-11-09): "E-means: quality batch at d <= 16 and no revival at d <= 2 by default" | 2026-11-09 | verified (title only, diff not read) | [S-EM-5] |
| 2026-11-10 announcement | A post on X attributed to "AGTP" says Meta FAIR released e-means "today". The post date could not be read (HTTP 402) | [UNVERIFIED] | unverifiable | [S-EM-6] |
| E-Means (2008), older and unrelated | Evolutionary extension of k-means (Lu, Tong, Traore). Estimates the cluster count with an entropy-based fitness and genetic operators | 2008 [STALE] | partial (search snippet only, Springer page not read) | [S-EM-7] |

## 3. Fit analysis

What the defense needs from a clusterer: group suspect points with an unknown group count, and leave lone points alone.

```
suspect points (2-D, few)
        |
        +--> DBSCAN (Luna and Lu): eps = r_search, minPts = 2 --> clusters + noise --> creator-ID graph --> strikes
        |
        +--> our §3.4 rule 2: merge within r_merge = 0.3 m, keep <= 16 points --> no k, online
        |
        +--> e-means: needs k, d, n >> k, epochs over shuffled batches --> every point gets a centroid
```

Figure 1. Three ways to group suspect points. Why: the clusterer must work without a known group count.
Abbreviations: density-based spatial clustering of applications with noise (DBSCAN), exponential moving average (EMA).

Table 1. Fit of e-means against the defense needs

| Need | Density-based spatial clustering of applications with noise (DBSCAN) in Luna and Lu | Our §3.4 merge rule | e-means | Source |
| --- | --- | --- | --- | --- |
| Inputs | 2-D waypoint coordinates. eps = robot search radius. minPts = 2 | Suspect peak positions. `r_merge` = 0.3 m. `n_mem` = 16 | Points of dimension `d`, and `k`. Batch size and step come from scaling laws on (k, n, epochs) | [S-PH-1], `../DESIGN.md` §3.4 and §3.5, [S-EM-2] |
| Needs k? | No | No | Yes. `k` is a required argument | [S-PH-1], [S-EM-4] |
| Noise and outliers | Points that fail minPts stay unclustered (the "with noise" part, inference from the method's definition) | A lone point is kept as its own suspect | Not addressed in the paper. Every point goes to its nearest centroid. Dead-cluster revival only refills empty clusters | [S-EM-2], inference |
| Online or streaming | Luna and Lu do not describe an incremental version (from Q2 of `pheromone_research.md`) | Yes. One point at a time, at END_SEARCH exit | No. Mini-batch over repeated shuffled epochs. The paper describes no true streaming mode | [S-PH-1], [S-EM-2] |
| Data scale it was built for | Small swarm, sparse points ("expected data sparsity") | At most 16 points per robot, 2-D | Scaling laws fitted for n from 1e5 to 1e8, k from 256 to 65,536, n/k of at least 8. Tested at d from 96 to 1024 | [S-PH-1], [S-EM-2] |
| Low dimension, tiny data | Built for it | Built for it | Paper: laws "are not optimal on very low-dimensional and tiny datasets". Code has a special default at d <= 2 (commit title) | [S-EM-2], [S-EM-5] |
| Compute | Not stated in Luna and Lu | One distance check per stored point (inference) | Paper: floating-point operations per epoch "comparable to Lloyd". No formal bound given | [S-EM-2], inference |
| Fit to our controller | Not built (option C, outside goal G2) | Built into the C++17 ARGoS controller design | Python code in Faiss contrib, with NumPy or PyTorch. A C++ port would be needed (inference) | `../DESIGN.md` line 5, [S-EM-4], inference |

Reading Table 1:

- e-means solves a different problem. It speeds up k-means on very large embedding sets.
- The defense needs an unknown cluster count and noise points. e-means gives neither.
- Its speed gain matters at 1e5 points and more. We hold at most 16 points per robot.
- With 16 points, any clusterer runs in negligible time (inference). Speed is not our bottleneck.

What it would change in our testbed:

- Goal G2: nothing. §3.4 uses no clusterer. Rule 2 already merges online with no k.
- Option C (DBSCAN on suspect ends): e-means cannot drop in. It would need a fixed k and a noise rule we would have to invent.
- A fixed k would force lone suspect points into a cluster. That could merge an honest-trail suspect with a decoy cluster (inference).

## 4. Recommendation

**Do not use e-means for the pheromone defense.** (inference, from Table 1)

- Reason 1: it needs k. The number of decoy clusters is what the defense must find.
- Reason 2: it has no noise label. DBSCAN's minPts = 2 rule is what keeps lone points out.
- Reason 3: it targets 1e5 to 1e10 points in high dimension. Our case is 2-D and at most 16 points.
- Reason 4: it is multi-epoch mini-batch, not a one-point-at-a-time update on a robot.
- Keep DBSCAN as option C, as `../DESIGN.md` §3.4 already says.
- Possible variant, not e-means: rule 2 could update a merged centroid with an EMA instead of a plain mean. Older evidence would then fade. This borrows only the EMA idea. It is untested (inference).
- Where e-means could fit: a project that clusters many high-dimensional embeddings. Not this one (inference).

## 5. Selection log

| Candidate | Status | Reason |
| --- | --- | --- |
| e-means (2026, Meta FAIR, arXiv 2611.09501) | kept, the match | Name matches. Paper and code dated 2026-11-04 to 2026-11-11, around the owner's "yesterday" |
| E-Means (2008, Lu, Tong, Traore) | kept as background, partial, [STALE] | Same name, unrelated method. Springer page not read |
| Equilibrium K-Means (EKMeans, `sklekmeans`) | rejected | Name mismatch. Seen as a search snippet only [S-EM-8] |
| "Modified global E-means" (MGK'M) | rejected | Search snippet only, no source page read. Low confidence |
| ε-means, elastic, entropy, energy-based k-means | rejected | No search result used that name for a 2026 release |

## open_questions

- [UNVERIFIED] Was e-means announced on 2026-11-10? The X post [S-EM-6] returned HTTP 402. arXiv v1 is dated 2026-11-06.
- First commit date of `contrib/e_means`: the commit list was cut off. 2026-11-04 is the earliest seen.
- Is e-means in a tagged Faiss release, or on main only? Not checked.
- The paper was read through a summarizer, first 100,000 of about 167,000 characters. Later appendices were not read.
- E-Means 2008 [S-EM-7]: abstract seen as a snippet only. Springer redirected to a login.
- What the 2026-11-09 commit does at d <= 2: title read, diff not read.

## Sources

[S-EM-1] e-means: outperforming k-means (in one-tenth the epochs) | https://arxiv.org/abs/2611.09501 | published: 2026-11-06 (v1) | accessed: 2026-11-11 | type: paper | note: abstract page read
[S-EM-2] e-means: outperforming k-means (in one-tenth the epochs) | https://arxiv.org/html/2611.09501v1 | published: 2026-11-06 (v1) | accessed: 2026-11-11 | type: paper | note: HTML full text read through a summarizer, first 100,000 of about 167,000 characters
[S-EM-3] e-means project page | https://e-means.github.io | published: 2026 (no date on page) | accessed: 2026-11-11 | type: official
[S-EM-4] Faiss contrib e_means README | https://github.com/facebookresearch/faiss/tree/main/contrib/e_means | published: main branch snapshot | accessed: 2026-11-11 | type: official | note: tree page and README read
[S-EM-5] Faiss commits on contrib/e_means | https://api.github.com/repos/facebookresearch/faiss/commits?path=contrib/e_means&per_page=100 | published: 2026-11-04 to 2026-11-11 | accessed: 2026-11-11 | type: official | note: first 100,000 characters read, about 11 commits visible
[S-EM-6] AGTP post on X about e-means | https://x.com/AGTPinsights/status/2120273239012237559 | published: unknown | accessed: 2026-11-11 | type: anecdotal | note: fetch returned HTTP 402, text seen only as a search snippet
[S-EM-7] E-Means: An Evolutionary Clustering Algorithm | https://link.springer.com/chapter/10.1007/978-3-540-92137-0_59 | published: 2008 | accessed: 2026-11-11 | type: paper | note: search snippet only, page redirected to login
[S-EM-8] sklekmeans: Equilibrium K-Means clustering algorithms compatible with scikit-learn | https://pypi.org/project/sklekmeans/ | published: unknown | accessed: 2026-11-11 | type: official | note: search snippet only
[S-PH-1] Robust Mitigation Strategy for Misleading Pheromone Trails in Foraging Robot Swarms | https://par.nsf.gov/servlets/purl/10593555 | published: 2025, TAROS 2024 LNAI 15052 pp. 307 to 319 | accessed: 2026-11-10 | type: paper | note: claims taken from `pheromone_research.md` Q2, not re-read here
