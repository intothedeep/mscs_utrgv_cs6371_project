"""Write and run the 6 keep-A judgement runs (D-010, M2). Judged once: no retry.

Usage: make_judgement.py [--run]
Arm 1: pheromone on. Arm 2: follow_enabled="false" (theta_on infinite). Seeds 104 to 106,
d = 0, defense off, values from results/real/tuning/tuning_pick.json.
Stops when the pick is missing, the pre-registration is not committed, or judgement
runs already exist (D-010 allows one judgement).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from make_sweep import build_argos
from sweep_params import Override
from run_argos import run_argos_files
from run_results import PROJECT, load_manifests, require_committed

ROOT = PROJECT / "runs" / "judgement"
PICK = PROJECT / "results" / "real" / "tuning" / "tuning_pick.json"
PREREG = PROJECT / "prereg" / "keep_a_judgement.md"
JUDGEMENT_SEEDS = (104, 105, 106)
ARMS = {"1": "true", "2": "false"}  # arm -> follow_enabled
CONTROLLER_PH = "controllers/pheromone_forager_controller/params/pheromone"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", action="store_true", help="also run the 6 files, one at a time")
    args = ap.parse_args(argv)
    if not PICK.is_file():
        raise SystemExit(f"stop: {PICK.relative_to(PROJECT)} is missing. Freeze the tuning first")
    require_committed(PREREG)
    if load_manifests(ROOT):
        raise SystemExit("stop: judgement runs already exist. D-010 allows no retry")
    pick = json.loads(PICK.read_text())
    files: list[Path] = []
    for arm, follow in ARMS.items():
        overrides: tuple[Override, ...] = (
            ("loop_functions/pheromone", "half_life_s", f"{pick['half_life_s']:g}"),
            (CONTROLLER_PH, "lambda_dep", f"{pick['lambda_dep']:g}"),
            (CONTROLLER_PH, "follow_enabled", follow))
        for seed in JUDGEMENT_SEEDS:
            runid, path = build_argos(0, 0, seed, ROOT, overrides, {"arm": arm})
            files.append(path)
            print(f"arm {arm} seed {seed}: {runid}")
    if args.run:
        run_argos_files(files)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
