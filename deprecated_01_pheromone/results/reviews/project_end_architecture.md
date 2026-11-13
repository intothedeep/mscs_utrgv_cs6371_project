# Project-end review, architecture remit (M8-04)

- Author: system-architect, 2026-11-12. Run with reviewer and data-analyst. Recommend only.
- Gating note: PLAN.md says M8-04 waits for the M3 to M7 gates. Only `M1_gate.md` and `M2_gate.md` exist.
- No git or shell here. History rests on files and DECISIONS.md. Reviewer confirms with `git log -- tools/schema.py tools/check_runs.py`.

## 0. Mission lines served (quoted from `PLAN.md`)

> - Mission: Keep pheromone foraging swarms trustworthy against false trails as they scale, change and learn. (D-034)
> - Vision: A chart sets our no-ID defense beside Prof. Lu's ID-based defense, each failure explained. (D-035)
> - G3: By 2026-11-28, 3 of 3 run tracks (T-A, T-B, T-D) have a committed `verdict.json`, plus a root-cause memo for each fail. (D-036)

## 1. Verdict

| Question | Answer | Severity |
| --- | --- | --- |
| Q1 design and schema | Four schema files hold. Two drifts outside `schema.py`, one reading note | medium |
| Q2 invariance records | v2, v5, v6 recorded. v4 has no CHANGELOG result. All evidence in ignored roots | medium |
| Q3 code health | No file over 400. Three tools over 300. Two dead `[diag]` sites. Copied planners | low |
| Q4 back to MVP1 | Nothing must go back. Three items fold in at the next schema touch | low |
| Q5 stigmergy step | New pure mark module, controller, glue, sidecar. About 5 to 6 person-days | owner decision first |

## 2. Q1: design and schema contract

What holds:

- `schema.py` is `SCHEMA_VERSION = 1`. Its one recorded change is `WAIT_DECOY` in the M1 fix (`M2_gate.md` I-10).
- v2 to v6 add no column, event name or top-level manifest key (CHANGELOG rows, file content).
- New knobs enter the open `params` set. `run_info_reader.cpp:41-53` copies every `.argos` attribute.
- `check_runs.py:87` allows extra params. `check_runs.py:224` checks only `S.FILES`, so the sidecar is ignored.
- `defense` stays 0/1. `RUNID_RE` is unchanged (D-030, DESIGN_M6 Table 5). The v6 controller is unchanged.
- The sidecar has the same 14 columns in DESIGN_M6 Table 4, `defense_log.cpp` and `v6_sidecar.py`.

Drift 1. `check_runs.py` changed in M7 with no D-row:

- `honest_count()` (`check_runs.py:27-29`) reads `params.n_honest`, else `S.N_HONEST`.
- TASKS.md:60 and :183 expect `check_runs.py` unchanged since M1, or changed only with a log entry.
- The literal `n_honest` sits in 4 tools. M1-02 wanted contract names only in `schema.py`.
- No mock run has 40 honest robots. Real runs exercised that validator path first.

Reading note (not a contract break):

- The counting code for `suspect_add` and `suspects_total` is unchanged (DESIGN_M5 §1.2). DESIGN §4 still holds.
- At k = 2 a held point can be pending. Do not read `suspects_total` as active points in v5 runs.

Drift 2. Load-bearing keys outside `schema.py`:

- Arm identity lives in params (`defense_mode`, `controller_defense_confirm_k`, `controller_defense_t_lock`), not in the runid.
- So each arm needs its own root (DESIGN_M6 §6). Readers stop on repeats. `analyze.py` keeps the latest and lists the rest (`analyze.py:65-72`).
- The sidecar header exists twice (`defense_log.cpp:12-13`, `v6_sidecar.py:15-16`). Types and event names are unchecked.
- `final_tables.py:29-30` re-declares the M6 root, seeds and arms instead of importing `v6_common.py`.
- DESIGN.md §0 still quotes the D-004 mission and vision. The architect owes this edit (out of scope here).
- DESIGN_M6 §6 lists 4 arm roots. The code has 5 with `k1t10` (D-052). The doc is not updated.

## 3. Q2: invariance claims against records

| Code | Claim | Record | Gap |
| --- | --- | --- | --- |
| v2 | d 0 off equals v1 food | CHANGELOG PASS, `runs/x_v2_invariance/` | `x_` root. Historical only, v3 superseded v2 (D-025) |
| v3 | none expected | D-025 reran the chain | none |
| v4 | `t_lock` 0 equals v3 food | `STATUS.md:33` only. Re-checked here, 8 of 8 food equal `runs/sweep/*_s1` | No CHANGELOG result. CHANGELOG names 2 cells, 8 ran. No committed compare output |
| v5 | k 1 equals v4 | CHANGELOG PASS (food, event rows), `runs/invariance_v5/` | Not byte-level |
| v6 | off, v3 byte-equal | CHANGELOG PASS "3 of 3", `runs/invariance_v6/`, session log | Off cell compared with saved v4 bytes. Defense-on cells compared with v5 reruns, so v4 to v6 on that path is food and event rows only |
| v6 `v5` mode | none stated | none | No check against v5-code k2t10. Matters once: `root_cause.md` §5.4 (b) reads M5 numbers for M7 |

- Every gap is a record gap. Food checked here (v4 8 of 8, v5 and v6 defense-on) agrees. Bytes not re-checked. Only v5 puts its numbers in CHANGELOG (`rules/measurement.md` §2.2).
- All roots are git-ignored. A clean clone cannot re-check any claim.
- Recommend: commit one compare file per version (runid pairs, food, CSV sha256). Add the v4 result line.

## 4. Q3: code health

| File | Lines | Reading |
| --- | --- | --- |
| `tools/m7_root_cause.py` | 390 | below 400. Do not grow it (Q5) |
| `tools/failure_analysis.py` | 352 | one analysis. Justify or split at next touch |
| `tools/v5_killcheck.py` | 324 | frozen D-046 evidence. Do not touch |
| `pheromone_forager.cpp` (largest C++) | 272 | fine |

Dead code. Bounded pass over `[diag]`, TODO and "not verified" greps, plus files read.

- `pheromone_forager.cpp:86-97` wraps `ControlStep` in a `[diag]` catch and rethrow. `pheromone_loop_functions.cpp:95` logs `[diag] Destroy`. STATUS.md:25 closed that cause, so both are dead.
- Stale comment at `pheromone_loop_functions.cpp:61`. The M2 layout check verified the `layout` stream. `:174` stays, it explains the PreStep order.
- Removal changes both library hashes. Bundle it with the next `code_version` and its invariance check.

Duplication:

- `v2_common.read_food` and `v5_common.read_food` are one loop with different keys.
- Three planners do one job: `sweep_plan.plan_runs`, `plan_runs_v6`, `plan_runs_v7`.
- Also copied: `require_prereg` (2 forms), `compare_invariance` (`confirm_v5.py`, `confirm_v6.py`), `row_dict` (`judge_v2.py`, `judge_v5.py`).
- The bootstrap core (`g2_stats.paired_diff_interval`) is shared. Do not refactor the copies. Committed verdicts hold their sha256 (`rules/measurement.md` §4.1).
- New code: one planner with tags and optional `n_honest`, and one keyed manifest reader.
- Naming: `v2_` is defense v2 on code v4, `v5_`, `v6_` are code versions, `v7_` is M7 on code v6. Name new tools by milestone (`m9_`).

## 5. Q4: what goes back to MVP1

- Must go back now: nothing. No built slice needed a column, event or state change.

Fold in at the next schema touch, each with a D-row first. No run becomes invalid. `schema_version` stays 1.

1. `P_NHONEST` as an optional param key in `schema.py`. Tools import it. One mock run at 40 honest robots.
2. An arm-key tuple in `schema.py`. `analyze.py` stops on a repeated arm key.
3. Sidecar columns as an optional block in `schema.py`. `check_runs.py` checks a sidecar when present.

## 6. Q5: shared no-ID confirmation through local stigmergy

Source: `results/real/scale/root_cause.md` §7.2 option A. RQ.md lists it under Proposed.

Owner decisions first (strategy line):

- D-028 rejected a "cautionary pheromone layer". Option A is that layer in a new role. Owner question: do shared marks break no-communication?
- S2 lists no such track. It needs an accepted RQ and a strategy line. The prereg must fix the attack model: do detractors lay or clear marks?

Step 0 (MVP1 of this capability, no run):

- Replay pooled confirmation from saved `runs/m7_scale/` events (root_cause.md §7.2). New tool, not `m7_root_cause.py`. Stop before code if pooled wrong source activations at d 0 exceed the v5 level.

```
 controller --(mark request on a failed valid peak)--> loop functions
      ^                                                     |
      |  SPheromoneReading + mark_here, mark_probe[8]       v
      +---------------------------------------------- MarkGrid (new, pure)
                                                       deposit, evaporate, clear near pickup
```

| Component | Change | Why |
| --- | --- | --- |
| `mark_grid.{h,cpp}` (new, pure) | one layer, own decay, clear in a radius | `CPheromoneGrid` holds trail layers and `Probe` sums them. A separate module leaves the grid code and its bytes untouched |
| controller defense | activation reads the local mark, not the private `Count` | the root cause is private confirmation |
| controller structs | `SPheromoneReading` gains mark fields. `SDepositRequest` gains a mark flag | marks are sensed like pheromone (DESIGN §2.1) |
| loop functions glue | new `defense_mode` value, mark deposits, pickup clears | ID arm pattern |
| logger | `mark_log.csv` sidecar | keeps `schema_version` 1 |

Schema impact:

- Sidecar route: no schema change, but Drift 2 deepens. Do §5 item 3 first. Recommended.
- Event route (`mark_add`, `mark_clear` in `events.csv`): `EVENT_NAMES` changes. That slice goes back to MVP1 (`schema_version` 2).
- Invariance: the controller changes this time. Modes off, v3, v5 must be byte-equal to saved v6 runs, one at 40 honest robots.

Size estimate (inference, scaled from DESIGN_M6 Table 7):

| Unit | Person-days |
| --- | --- |
| Pooled replay tool (step 0) | 0.5 |
| `mark_grid` module | 0.5 |
| Controller sensing and activation rule | 1.5 |
| Glue, mode, sidecar writer and its mock, code version, CHANGELOG | 1.5 |
| Run tool and judge, 20 and 40 honest robots | 1.25 |
| Sum (tuning of mark decay and clear radius not included) | 5.25 |

- MVP2 of this capability: the real mark layer at d 2, 20 honest robots, smoke seed 900. The rest stays on the replay.
