"""Write (and with --run, run) the M7 scalability runs. One core, sequential, 300 s per run (D-013, D-031, D-044).

  --stage smoke    arms off, v3, v5 x N 20, 40 x d = 10 % of N (2, 4), seed 900, into runs/m7_smoke/<arm>_n<N>/ (6 runs).
                   Report only. Needs no prereg. Run it first: it shows that 44 robots start in the nest area.
  --stage confirm  arms off, v3, v5 x N 20, 40 x d = 0 and 10 % of N x seeds 401-430, one root per arm and N under
                   runs/m7_scale/<arm>_n<N>/ (360 runs).
confirm refuses unless prereg/scale.md is committed and unchanged and names the best arm, and refuses seeds
outside 401-430 (D-043). A rerun only fills missing runs. Seed-major, so a stopped stage leaves whole seeds.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sweep_params import parse_seeds
from v5_common import require_seeds
from v6_common import ARMS
from v7_common import (ARM_ORDER, CONFIRM_BASE, CONFIRM_SEEDS, D10, NS, SMOKE_BASE, SMOKE_SEEDS, cell_root, cells,
                       plan_runs_v7, require_prereg)


def plan_stage(base: Path, seeds: tuple[int, ...], smoke: bool, run: bool) -> int:
    for seed in seeds:
        for n in NS:
            for arm in ARM_ORDER:
                ds = (D10[n],) if smoke else cells(n)
                jobs = [((d, ARMS[arm].defense, seed), arm) for d in ds]
                plan_runs_v7(cell_root(base, arm, n), jobs, n, run)
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", required=True, choices=("smoke", "confirm"))
    ap.add_argument("--run", action="store_true", help="also run the new files, one at a time")
    ap.add_argument("--seeds", type=parse_seeds, metavar="a-b", help="a part of the stage block, to resume")
    args = ap.parse_args(argv)
    if args.stage == "smoke":
        seeds = args.seeds or SMOKE_SEEDS
        require_seeds(seeds, SMOKE_SEEDS)
        return plan_stage(SMOKE_BASE, seeds, True, args.run)
    require_prereg()
    seeds = args.seeds or CONFIRM_SEEDS
    require_seeds(seeds, CONFIRM_SEEDS)
    return plan_stage(CONFIRM_BASE, seeds, False, args.run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
