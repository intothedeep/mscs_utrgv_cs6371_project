"""Write (and with --run, run) the M6 ID arm runs. One core, sequential, 300 s per run (D-013, D-031, D-044).

  --stage invariance  off and v3 code paths against saved runs (DESIGN_M6 section 7): off d0 s11, v3 d0 s11, v3 d2 s11,
                      into runs/invariance_v6/. The 3 CSV files must be byte equal and metrics equal.
                      Exempt from the prereg commit check and the seed guard.
  --stage smoke       1 run per arm (off, v3, v5, id) at d = 2, seed 900, into runs/m6_smoke/<arm>/ (D-048 D6).
                      Report only. Needs no prereg. Uses the margin of results/real/m6_margin.csv, else 1.5.
  --stage check       arm check: arm id, cells (d 2, id) and (d 0, id, report only), seeds 301-310,
                      into runs/m6_check/id/ (20 runs). Then run tools/v6_arm_table.py.
  --stage confirm     arms off, v3, v5, id x d 0, 1, 2, 4 x seeds 321-360, one root per arm under runs/m6_confirm/ (640 runs).
check and confirm refuse unless prereg/defense_id_arm.md is committed and unchanged, names the best no-ID arm
and holds the margin of m6_margin.csv, and refuse seeds outside their block (D-043). A rerun only fills missing runs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import schema as S
from run_results import load_manifests
from sweep_params import parse_seeds
from v5_common import SAVED_V4_ROOT, INVARIANCE_ROOT as V5_INVARIANCE_ROOT, require_seeds
from v6_common import (ARM_ORDER, ARMS, CHECK_ROOT, CHECK_SEEDS, CONFIRM_ROOT, CONFIRM_SEEDS, DS, INVARIANCE_ROOT,
                       SMOKE_ROOT, SMOKE_SEEDS, arm_root, plan_runs_v6, read_margin, require_prereg)

# (arm, (d, defense, seed)) -> the saved run it must reproduce byte for byte. off has no v5-code run: the v4 sweep is the reference.
INVARIANCE_CELLS = {("off", (0, 0, 11)): SAVED_V4_ROOT, ("v3", (0, 1, 11)): V5_INVARIANCE_ROOT,
                    ("v3", (2, 1, 11)): V5_INVARIANCE_ROOT}
BYTE_FILES = (S.TICKS_FILE, S.ROBOTS_FILE, S.EVENTS_FILE)
IGNORED_PARAMS = ("defense_mode", "controller_defense_confirm_k")  # new in v6, new in v5 (absent in v4 manifests)


def saved_folder(root: Path, cell: tuple[int, int, int]) -> Path:
    found = sorted(root.glob(f"*_d{cell[0]}_def{cell[1]}_s{cell[2]}"))
    if len(found) != 1:
        raise SystemExit(f"stop: {len(found)} saved runs for {cell} under {root.name}. Name one by hand")
    return found[0]


def compare_invariance() -> int:
    done = {(m[S.K_PARAMS].get("defense_mode"), m[S.K_PARAMS][S.P_NDET], m[S.K_PARAMS][S.P_DEFENSE],
             m[S.K_PARAMS][S.P_SEED]): m for m in load_manifests(INVARIANCE_ROOT)}
    bad = 0
    for (arm, cell), ref_root in INVARIANCE_CELLS.items():
        new = done.get((arm, *cell))
        if new is None:
            print(f"{arm} {cell}: no complete v6 run yet, comparison skipped")
            bad += 1
            continue
        old_dir, new_dir = saved_folder(ref_root, cell), INVARIANCE_ROOT / new[S.K_RUNID]
        old = json.loads((old_dir / S.MANIFEST_FILE).read_text())
        ignored = lambda p: {k: v for k, v in p.items() if k not in IGNORED_PARAMS}  # noqa: E731
        checks = {f: (old_dir / f).read_bytes() == (new_dir / f).read_bytes() for f in BYTE_FILES}
        checks["metrics"] = old[S.K_METRICS] == new[S.K_METRICS]
        checks["params"] = ignored(old[S.K_PARAMS]) == ignored(new[S.K_PARAMS])
        checks["code_version_v6"] = new["code_version"] == "v6"
        print(f"{arm} {cell} vs {ref_root.name}/{old_dir.name}: " +
              ", ".join(f"{k}={'ok' if v else 'FAIL'}" for k, v in checks.items()))
        bad += not all(checks.values())
    print("INVARIANCE " + ("PASS" if bad == 0 else "FAIL: stop M6 and go to recover (DESIGN_M6 section 7: re-run the cell on the v5 build to attribute)"))
    return 1 if bad else 0


def plan_arms(base: Path, arms: tuple[str, ...], cells: dict[str, tuple[int, ...]], seeds: tuple[int, ...],
              margin: float, run: bool) -> int:
    """Seed-major over arms: a stopped stage leaves whole seeds. cells: arm -> detractor counts."""
    for seed in seeds:
        for arm in arms:
            jobs = [((d, ARMS[arm].defense, seed), arm) for d in cells[arm]]
            plan_runs_v6(arm_root(base, arm), jobs, margin, run)
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", required=True, choices=("invariance", "smoke", "check", "confirm"))
    ap.add_argument("--run", action="store_true", help="also run the new files, one at a time")
    ap.add_argument("--seeds", type=parse_seeds, metavar="a-b", help="a part of the stage block, to resume")
    args = ap.parse_args(argv)
    if args.stage == "invariance":
        jobs = [((d, de, s), arm) for (arm, (d, de, s)) in INVARIANCE_CELLS]
        plan_runs_v6(INVARIANCE_ROOT, jobs, read_margin(), args.run)
        return compare_invariance()
    if args.stage == "smoke":
        require_seeds(args.seeds or SMOKE_SEEDS, SMOKE_SEEDS)
        return plan_arms(SMOKE_ROOT, ARM_ORDER, {a: (2,) for a in ARM_ORDER}, args.seeds or SMOKE_SEEDS,
                         read_margin(), args.run)
    _best, margin = require_prereg()
    block = CHECK_SEEDS if args.stage == "check" else CONFIRM_SEEDS
    seeds = args.seeds or block
    require_seeds(seeds, block)
    if args.stage == "check":
        # (0, id) is report only (D-048 D3): same seeds, no pick.
        return plan_arms(CHECK_ROOT, ("id",), {"id": (2, 0)}, seeds, margin, args.run)
    return plan_arms(CONFIRM_ROOT, ARM_ORDER, {a: DS for a in ARM_ORDER}, seeds, margin, args.run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
