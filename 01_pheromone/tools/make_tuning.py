"""Write the 3 .argos files of one pheromone tuning round (D-007), and run them with --run.

Usage: make_tuning.py --round k [--half-life H] [--lambda-dep L] [--run]
Runs: d = 0, defense off, seeds 101 to 103, into runs/tuning/. Round 1 uses the start values.
Rounds 2 and 3 change exactly one value from the best earlier round, both from the D-007
candidates. The pre-registration prereg/pheromone_tuning.md must be committed first.
--run runs the 3 files one at a time, one core, 300 s each (D-013). It stops on a failure.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from make_sweep import Override, build_argos
from run_argos import run_argos_files
from run_results import PROJECT, require_committed
from tuning_rounds import (HALF_LIVES, LAMBDAS, MAX_ROUNDS, START, TUNING_SEEDS, Config,
                           best_round, read_rounds)

TUNING_ROOT = PROJECT / "runs" / "tuning"
PREREG = PROJECT / "prereg" / "pheromone_tuning.md"
CONTROLLER_PH = "controllers/pheromone_forager_controller/params/pheromone"


def choose_config(k: int, rounds: dict[int, dict], half_life: float | None,
                  lambda_dep: float | None) -> Config:
    if k < 1 or k > MAX_ROUNDS:
        raise SystemExit(f"stop: D-007 allows rounds 1 to {MAX_ROUNDS}")
    if k in rounds:
        raise SystemExit(f"stop: round {k} already has runs under runs/tuning/")
    if k == 1:
        if half_life is not None or lambda_dep is not None:
            raise SystemExit("stop: round 1 uses the start values, give no value")
        return START
    if set(rounds) != set(range(1, k)):
        raise SystemExit(f"stop: rounds 1 to {k - 1} must exist before round {k}")
    best = rounds[best_round(rounds)]["config"]  # also stops on an incomplete round
    cfg = (best[0] if half_life is None else half_life, best[1] if lambda_dep is None else lambda_dep)
    if cfg[0] not in HALF_LIVES or cfg[1] not in LAMBDAS:
        raise SystemExit(f"stop: values must come from half-life {HALF_LIVES} and lambda_dep {LAMBDAS}")
    if (cfg[0] != best[0]) + (cfg[1] != best[1]) != 1:
        raise SystemExit(f"stop: change exactly one value from the best round {best}")
    if cfg in {r["config"] for r in rounds.values()}:
        raise SystemExit(f"stop: setting {cfg} was already tried")
    return cfg


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--round", required=True, type=int, dest="k")
    ap.add_argument("--half-life", type=float)
    ap.add_argument("--lambda-dep", type=float)
    ap.add_argument("--run", action="store_true", help="also run the 3 files, one at a time")
    args = ap.parse_args(argv)
    require_committed(PREREG)
    cfg = choose_config(args.k, read_rounds(TUNING_ROOT), args.half_life, args.lambda_dep)
    overrides: tuple[Override, ...] = (("loop_functions/pheromone", "half_life_s", f"{cfg[0]:g}"),
                                       (CONTROLLER_PH, "lambda_dep", f"{cfg[1]:g}"))
    files: list[Path] = []
    for seed in TUNING_SEEDS:
        runid, path = build_argos(0, 0, seed, TUNING_ROOT, overrides, {"round": str(args.k)})
        files.append(path)
        print(f"round {args.k} seed {seed}: {runid}")
    print(f"setting: half_life_s={cfg[0]:g} lambda_dep={cfg[1]:g}")
    if args.run:
        run_argos_files(files)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
