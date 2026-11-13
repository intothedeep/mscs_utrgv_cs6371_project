"""The D-007 and D-011 tuning rules as code: start values, candidates, and the round table.

Rounds are read from manifests under a tuning runs root (params `round` plus the tuned values).
Nothing else holds round state. A config is a tuple of floats, in the order of its key names.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import schema as S
from run_results import PROJECT, load_manifests, require_committed, run_food
from sweep_params import manifest_key

__all__ = ["PHEROMONE", "DEFENSE", "TUNING_SEEDS", "MAX_ROUNDS", "Rule", "read_rounds",
           "best_round", "load_defense_rule"]

TUNING_SEEDS = (101, 102, 103)  # never the sweep seeds 1 to 10
MAX_ROUNDS = 3


class Rule:
    """Names of the tuned values, their start values and the allowed candidates."""

    def __init__(self, names: tuple[str, ...], start: tuple[float, ...],
                 candidates: tuple[tuple[float, ...], ...]) -> None:
        self.names, self.start, self.candidates = names, start, candidates
        self.keys = tuple(manifest_key(n) for n in names)


# D-007: half-life 30, 60, 120 s and lambda_dep 0.05, 0.077, 0.115. Round 1 is the start values.
PHEROMONE = Rule(("half_life_s", "lambda_dep"), (60.0, 0.077), ((30.0, 60.0, 120.0), (0.05, 0.077, 0.115)))
DEFENSE_CANDIDATES = PROJECT / "prereg" / "defense_candidates.json"
DEFENSE_NAMES = ("r_suspect", "alpha_cone_deg", "d_cone", "t_end")


def load_defense_rule() -> Rule:
    """D-011 values come from prereg/defense_candidates.json, which must be committed first."""
    require_committed(DEFENSE_CANDIDATES)
    spec = json.loads(DEFENSE_CANDIDATES.read_text())
    return Rule(DEFENSE_NAMES, tuple(float(spec[n]["start"]) for n in DEFENSE_NAMES),
                tuple((float(spec[n]["start"]), *map(float, spec[n]["alternates"])) for n in DEFENSE_NAMES))


def read_rounds(root: Path, rule: Rule) -> dict[int, dict]:
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
        configs = {tuple(float(r[S.K_PARAMS][key]) for key in rule.keys) for r in runs}
        if len(configs) != 1:
            raise SystemExit(f"stop: round {k} mixes settings")
        foods = {int(r[S.K_PARAMS][S.P_SEED]): run_food(r) for r in runs}
        seeds_ok = set(foods) == set(TUNING_SEEDS) and len(runs) == len(TUNING_SEEDS)
        rounds[k] = {"config": configs.pop(), "foods": foods,
                     "runids": sorted(r[S.K_RUNID] for r in runs),
                     "mean_food": sum(foods.values()) / len(foods) if seeds_ok else None}
    return rounds


def best_round(rounds: dict[int, dict]) -> int:
    """Highest mean food. A tie goes to the earlier round (D-007, D-011)."""
    best = None
    for k, r in sorted(rounds.items()):
        if r["mean_food"] is not None and (best is None or r["mean_food"] > rounds[best]["mean_food"]):
            best = k
    if best is None:
        raise SystemExit("stop: no tuning round has all seeds 101 to 103 complete")
    return best
