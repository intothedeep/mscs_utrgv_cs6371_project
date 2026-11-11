"""The D-007 tuning rule as code: start values, candidates, and the round table (M2-07).

Rounds are read from manifests under runs/tuning/ (params `round`, `half_life_s`,
`controller_pheromone_lambda_dep`). Nothing else holds round state.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import schema as S
from run_results import TUNING_PARAMS, load_manifests, run_food

__all__ = ["START", "HALF_LIVES", "LAMBDAS", "TUNING_SEEDS", "MAX_ROUNDS", "Config",
           "read_rounds", "best_round"]

Config = tuple[float, float]          # (half_life_s, lambda_dep)
START: Config = (60.0, 0.077)         # D-007 round 1
HALF_LIVES = (30.0, 60.0, 120.0)      # D-007 candidates
LAMBDAS = (0.05, 0.077, 0.115)
TUNING_SEEDS = (101, 102, 103)        # never the sweep seeds 1 to 10
MAX_ROUNDS = 3


def read_rounds(root: Path) -> dict[int, dict]:
    """round -> {config, foods {seed: food}, runids, mean_food or None when seeds are missing}.

    A started run that is not complete stops the caller (run_food).
    """
    by_round: dict[int, list[dict]] = defaultdict(list)
    for m in load_manifests(root):
        params = m[S.K_PARAMS]
        if "round" in params:
            by_round[int(params["round"])].append(m)
    rounds = {}
    for k, runs in sorted(by_round.items()):
        cfg = {float(r[S.K_PARAMS][TUNING_PARAMS["half_life_s"]]) for r in runs}, \
              {float(r[S.K_PARAMS][TUNING_PARAMS["lambda_dep"]]) for r in runs}
        if len(cfg[0]) != 1 or len(cfg[1]) != 1:
            raise SystemExit(f"stop: round {k} mixes settings")
        foods = {int(r[S.K_PARAMS][S.P_SEED]): run_food(r) for r in runs}
        seeds_ok = set(foods) == set(TUNING_SEEDS) and len(runs) == len(TUNING_SEEDS)
        rounds[k] = {"config": (cfg[0].pop(), cfg[1].pop()), "foods": foods,
                     "runids": sorted(r[S.K_RUNID] for r in runs),
                     "mean_food": sum(foods.values()) / len(foods) if seeds_ok else None}
    return rounds


def best_round(rounds: dict[int, dict]) -> int:
    """Highest mean food. A tie goes to the earlier round (D-007)."""
    best = None
    for k, r in sorted(rounds.items()):
        if r["mean_food"] is not None and (best is None or r["mean_food"] > rounds[best]["mean_food"]):
            best = k
    if best is None:
        raise SystemExit("stop: no tuning round has all seeds 101 to 103 complete")
    return best
