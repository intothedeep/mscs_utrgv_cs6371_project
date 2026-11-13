"""Write the 3 .argos files of one tuning round, and run them with --run.

Pheromone (D-007):  make_tuning.py --round k [--half-life H] [--lambda-dep L] [--run]
  d = 0, defense off, seeds 101 to 103, into runs/tuning/. Round 1 uses the start values.
Defense (D-011):    make_tuning.py --defense --round k [--r-suspect R] [--alpha-cone A]
                                   [--d-cone D] [--t-end T] [--run]
  d = 2, defense on, seeds 101 to 103, into runs/defense_tuning/, with the frozen pheromone
  values from tuning_pick.json. Candidates come from prereg/defense_candidates.json.
Rounds 2 and 3 change exactly one value from the best earlier round, to a candidate value.
The pre-registration must be committed first. --run runs the 3 files one at a time,
one core, 300 s each (D-013). It stops on a failure.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from make_sweep import build_argos
from run_argos import run_argos_files
from run_results import PROJECT, require_committed
from sweep_params import Override, overrides
from tuning_rounds import (MAX_ROUNDS, PHEROMONE, TUNING_SEEDS, Rule, best_round,
                           load_defense_rule, read_rounds)

PHEROMONE_ROOT = PROJECT / "runs" / "tuning"
DEFENSE_ROOT = PROJECT / "runs" / "defense_tuning"
PHEROMONE_PREREG = PROJECT / "prereg" / "pheromone_tuning.md"
DEFENSE_PREREG = PROJECT / "prereg" / "defense_tuning.md"
PICK = PROJECT / "results" / "real" / "tuning" / "tuning_pick.json"


def choose_config(k: int, rounds: dict[int, dict], rule: Rule,
                  wanted: tuple[float | None, ...]) -> tuple[float, ...]:
    if k < 1 or k > MAX_ROUNDS:
        raise SystemExit(f"stop: the rule allows rounds 1 to {MAX_ROUNDS}")
    if k in rounds:
        raise SystemExit(f"stop: round {k} already has runs")
    if k == 1:
        if any(v is not None for v in wanted):
            raise SystemExit("stop: round 1 uses the start values, give no value")
        return rule.start
    if set(rounds) != set(range(1, k)):
        raise SystemExit(f"stop: rounds 1 to {k - 1} must exist before round {k}")
    best = rounds[best_round(rounds)]["config"]  # also stops on an incomplete round
    cfg = tuple(b if w is None else w for b, w in zip(best, wanted))
    if any(c not in allowed for c, allowed in zip(cfg, rule.candidates)):
        raise SystemExit(f"stop: values must come from {rule.candidates}")
    if sum(c != b for c, b in zip(cfg, best)) != 1:
        raise SystemExit(f"stop: change exactly one value from the best round {best}")
    if cfg in {r["config"] for r in rounds.values()}:
        raise SystemExit(f"stop: setting {cfg} was already tried")
    return cfg


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--round", required=True, type=int, dest="k")
    ap.add_argument("--defense", action="store_true", help="defense tuning (D-011)")
    ap.add_argument("--half-life", type=float)
    ap.add_argument("--lambda-dep", type=float)
    ap.add_argument("--r-suspect", type=float)
    ap.add_argument("--alpha-cone", type=float, help="degrees")
    ap.add_argument("--d-cone", type=float)
    ap.add_argument("--t-end", type=float)
    ap.add_argument("--run", action="store_true", help="also run the 3 files, one at a time")
    args = ap.parse_args(argv)

    if args.defense:
        if any(v is not None for v in (args.half_life, args.lambda_dep)):
            raise SystemExit("stop: the pheromone values are frozen, take them from tuning_pick.json")
        require_committed(DEFENSE_PREREG)
        rule, root, d, defense = load_defense_rule(), DEFENSE_ROOT, 2, 1
        wanted = (args.r_suspect, args.alpha_cone, args.d_cone, args.t_end)
        if not PICK.is_file():
            raise SystemExit(f"stop: {PICK.relative_to(PROJECT)} is missing. Freeze the pheromone first")
        pick = json.loads(PICK.read_text())
        frozen = overrides(half_life_s=float(pick["half_life_s"]), lambda_dep=float(pick["lambda_dep"]))
    else:
        if any(v is not None for v in (args.r_suspect, args.alpha_cone, args.d_cone, args.t_end)):
            raise SystemExit("stop: defense values need --defense")
        require_committed(PHEROMONE_PREREG)
        rule, root, d, defense, frozen = PHEROMONE, PHEROMONE_ROOT, 0, 0, ()
        wanted = (args.half_life, args.lambda_dep)

    cfg = choose_config(args.k, read_rounds(root, rule), rule, wanted)
    set_values: tuple[Override, ...] = frozen + overrides(**dict(zip(rule.names, cfg)))
    files: list[Path] = []
    for seed in TUNING_SEEDS:
        runid, path = build_argos(d, defense, seed, root, set_values, {"round": str(args.k)})
        files.append(path)
        print(f"round {args.k} seed {seed}: {runid}")
    print("setting: " + " ".join(f"{n}={c:g}" for n, c in zip(rule.names, cfg)))
    if args.run:
        run_argos_files(files)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
