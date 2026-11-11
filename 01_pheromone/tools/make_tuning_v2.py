"""Write the 80 .argos files of the defense v2 tuning (spec item 5), and run them with --run.

t_lock 0, 5, 10, 20 s x cells (d = 2, on) and (d = 0, on) x seeds 107 to 116, into runs/tuning_v2/.
The frozen pheromone and defense values come from the two pick files, as in the sweep.
The pre-registration (prereg/defense_v2_lockout.md) must be committed first.
--run runs the new files one at a time, one core, 300 s each (D-013, D-031). Resumes a stopped run.
"""
from __future__ import annotations

import argparse
import sys

from run_results import require_committed
from sweep_plan import Job, frozen_values, plan_runs
from v2_common import PREREG, T_LOCKS, TUNE_CELLS, TUNE_ROOT, TUNE_SEEDS


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", action="store_true", help="also run the new files, one at a time")
    args = ap.parse_args(argv)
    require_committed(PREREG)
    frozen = frozen_values()
    # Seed-major: a stopped tuning leaves whole seeds, so every t_lock has the same seeds.
    jobs: list[Job] = [((d, defense, seed), {**frozen, "t_lock": float(t_lock)})
                       for seed in TUNE_SEEDS for t_lock in T_LOCKS for d, defense in TUNE_CELLS]
    return plan_runs(TUNE_ROOT, jobs, args.run)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
