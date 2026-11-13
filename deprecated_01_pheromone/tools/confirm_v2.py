"""Write (and with --run, run) the v2 confirmation: 8 cells x seeds 11-30 = 160 runs per root.

runs/sweep_v2/        picked t_lock (from results/real/tuning_v2/pick.json)
runs/sweep_v2_lock0/  t_lock 0, the same v4 code, for the attribution contrast
Kill rule (spec 12): a pick of 0 stops here, before any file is written. Seeds 11-30 are used once:
a rerun only fills missing cells, it never repeats a complete one.
One core, sequential, 300 s per run (D-013, D-031).
"""
from __future__ import annotations

import argparse
import sys

from run_results import require_committed
from sweep_plan import run_sweep
from v2_common import CONFIRM_ROOT, CONFIRM_SEEDS, CONTROL_ROOT, PREREG, load_pick


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", action="store_true", help="also run the new files, one at a time")
    ap.add_argument("--arm", choices=("picked", "lock0"), help="only one root. Default: both")
    args = ap.parse_args(argv)
    require_committed(PREREG)
    picked = load_pick()
    if picked == 0:
        raise SystemExit("stop: tuning picked t_lock 0. Kill rule (spec 12): no confirmation. "
                         "Report v2 as null at tuning")
    # Picked arm first: a stopped session then holds the arm that decides G(2).
    for arm, root, t_lock in (("picked", CONFIRM_ROOT, picked), ("lock0", CONTROL_ROOT, 0)):
        if args.arm in (None, arm):
            print(f"== {arm}: t_lock={t_lock} into {root}")
            run_sweep(args.run, root, CONFIRM_SEEDS, t_lock)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
