"""Write (and with --run, run) the defense v5 runs. One core, sequential, 300 s per run (D-013, D-031, D-044).

  --stage invariance  v5 code with confirm_k 1, t_lock 0 on 2 saved v4 cells (DESIGN_M5 section 2),
                      into runs/invariance_v5/. Then compares food, events rows and params.
                      Exempt from the prereg commit check and the seed guard (TASKS M5-03).
  --stage check       mechanism check: arms k2t10 and k1t10, cells (d 0, on) and (d 2, on),
                      seeds 201-210, into runs/v5_check/ (40 runs).
  --stage confirm     5 arms x d 0, 1, 2, 4 x seeds 221-260 into runs/v5_confirm/ (800 runs).
                      off and k2t10 first, then the other 3 arms.
check and confirm refuse unless prereg/defense_v5.md is committed and unchanged, and refuse seeds
outside their block (D-043). A rerun only fills missing runs (resume, sweep_plan.is_done).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import schema as S
from run_results import PROJECT, load_manifests, require_committed
from sweep_params import manifest_key, parse_seeds
from sweep_plan import Job, frozen_values, plan_runs
from v5_common import (ARMS, CHECK_ROOT, CHECK_SEEDS, CONFIRM_ROOT, CONFIRM_SEEDS, DS, INVARIANCE_ROOT,
                       OFF, PREREG, PRIMARY, SAVED_V4_ROOT, arm_values, require_seeds)

INVARIANCE_CELLS = {(0, 1, 11): "20261111-115700_d0_def1_s11",   # (d, defense, seed) -> saved v4 runid
                    (2, 1, 11): "20261111-115700_d2_def1_s11"}
CHECK_ARMS = (PRIMARY, "k1t10")
CHECK_CELLS = ((0, 1), (2, 1))                                    # (d, defense)
CONFIRM_FIRST = (OFF, PRIMARY)                                    # judged pair first: early wall-time estimate


def make_jobs(arms: tuple[str, ...], cells: tuple[tuple[int, int], ...] | None,
              seeds: tuple[int, ...]) -> list[Job]:
    """Seed-major. cells None = every d at the arm's own defense value."""
    frozen = frozen_values()
    jobs: list[Job] = []
    for seed in seeds:
        for arm in arms:
            defense = ARMS[arm][0]
            arm_cells = cells if cells is not None else tuple((d, defense) for d in DS)
            jobs += [((d, f, seed), {**frozen, **arm_values(arm)}) for d, f in arm_cells if f == defense]
    return jobs


def compare_invariance() -> int:
    """Rerun against saved v4: equal food, equal events.csv rows, equal params except confirm_k."""
    done = {(m[S.K_PARAMS][S.P_NDET], m[S.K_PARAMS][S.P_DEFENSE], m[S.K_PARAMS][S.P_SEED]): m
            for m in load_manifests(INVARIANCE_ROOT)}
    bad = 0
    for cell, saved_id in INVARIANCE_CELLS.items():
        new = done.get(cell)
        if new is None:
            print(f"{cell}: no complete v5 run yet, comparison skipped")
            bad += 1
            continue
        old_dir, new_dir = SAVED_V4_ROOT / saved_id, INVARIANCE_ROOT / new[S.K_RUNID]
        old = json.loads((old_dir / S.MANIFEST_FILE).read_text())
        rows = [sum(1 for _ in (d / S.EVENTS_FILE).open()) - 1 for d in (old_dir, new_dir)]
        params = {k: v for k, v in new[S.K_PARAMS].items() if k != manifest_key("confirm_k")}
        checks = {"food": old[S.K_METRICS][S.M_FOOD] == new[S.K_METRICS][S.M_FOOD],
                  "events_rows": rows[0] == rows[1],
                  "params_except_confirm_k": params == old[S.K_PARAMS],
                  "confirm_k_is_1": new[S.K_PARAMS].get(manifest_key("confirm_k")) == "1",
                  "code_version_v5": new["code_version"] == "v5"}
        print(f"{cell} food v4={old[S.K_METRICS][S.M_FOOD]} v5={new[S.K_METRICS][S.M_FOOD]} "
              f"events {rows[0]}/{rows[1]}: " + ", ".join(f"{k}={'ok' if v else 'FAIL'}" for k, v in checks.items()))
        bad += not all(checks.values())
    print("INVARIANCE " + ("PASS" if bad == 0 else "FAIL: stop M5 and go to recover (TASKS M5-05)"))
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", required=True, choices=("invariance", "check", "confirm"))
    ap.add_argument("--run", action="store_true", help="also run the new files, one at a time")
    ap.add_argument("--seeds", type=parse_seeds, metavar="a-b", help="a part of the stage block, to resume")
    args = ap.parse_args(argv)
    if args.stage == "invariance":
        jobs = make_jobs(("k1t0",), tuple(c[:2] for c in INVARIANCE_CELLS), (11,))
        plan_runs(INVARIANCE_ROOT, jobs, args.run)
        return compare_invariance()
    block, root = (CHECK_SEEDS, CHECK_ROOT) if args.stage == "check" else (CONFIRM_SEEDS, CONFIRM_ROOT)
    seeds = args.seeds or block
    require_committed(PREREG)
    require_seeds(seeds, block)
    if args.stage == "check":
        jobs = make_jobs(CHECK_ARMS, CHECK_CELLS, seeds)
    else:
        rest = tuple(a for a in ARMS if a not in CONFIRM_FIRST)
        jobs = make_jobs(CONFIRM_FIRST, None, seeds) + make_jobs(rest, None, seeds)
    print(f"== {args.stage}: {len(jobs)} jobs into {root.relative_to(PROJECT)}")
    return plan_runs(root, jobs, args.run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
