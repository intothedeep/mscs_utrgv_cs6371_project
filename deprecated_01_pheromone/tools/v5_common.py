"""Shared constants and readers of defense v5 (D-039, D-043, D-047, prereg/defense_v5.md).

One place for the arms, seed blocks, roots and the manifest reader, so the run tool, the
mechanism tool and the judge cannot disagree. Reads manifests only.
"""
from __future__ import annotations

from pathlib import Path

import schema as S
from run_results import PROJECT, load_manifests, run_food
from sweep_params import manifest_key

__all__ = ["ARMS", "OFF", "PRIMARY", "CHECK_SEEDS", "CONFIRM_SEEDS", "DS", "INVARIANCE_ROOT",
           "CHECK_ROOT", "CONFIRM_ROOT", "SAVED_V4_ROOT", "PREREG", "RESULTS", "VERDICT",
           "arm_values", "require_seeds", "read_food", "arm_food"]

Arm = tuple[int, int, int]                       # (defense, confirm_k, t_lock seconds)
OFF = "off"
PRIMARY = "k2t10"                                # named before any run (DESIGN_M5 section 4)
ARMS: dict[str, Arm] = {OFF: (0, 1, 0),          # k and t_lock are inert when the defense is off
                        "k1t0": (1, 1, 0), "k1t10": (1, 1, 10),
                        "k2t0": (1, 2, 0), "k2t10": (1, 2, 10)}
CHECK_SEEDS = tuple(range(201, 211))             # D-043, mechanism check
CONFIRM_SEEDS = tuple(range(221, 261))           # D-043, used once
DS = S.DETRACTOR_COUNTS
INVARIANCE_ROOT = PROJECT / "runs" / "invariance_v5"
CHECK_ROOT = PROJECT / "runs" / "v5_check"
CONFIRM_ROOT = PROJECT / "runs" / "v5_confirm"
SAVED_V4_ROOT = PROJECT / "runs" / "sweep_v2_lock0"
PREREG = PROJECT / "prereg" / "defense_v5.md"
RESULTS = PROJECT / "results" / "real" / "v5"
VERDICT = RESULTS / "verdict.json"

Key = tuple[int, int, int, int, int]             # (confirm_k, t_lock, d, defense, seed)


def arm_values(arm: str) -> dict[str, float]:
    """The .argos values an arm sets, on top of the frozen ones (sweep_params short names)."""
    _defense, k, t_lock = ARMS[arm]
    return {"confirm_k": k, "t_lock": float(t_lock)}


def require_seeds(seeds: tuple[int, ...], block: tuple[int, ...]) -> None:
    """Stop on any seed outside the allowed block. Spent seeds (1-30, 101-116) are never in a block."""
    bad = sorted(set(seeds) - set(block))
    if bad:
        raise SystemExit(f"stop: seeds {bad[:5]} are outside the allowed block "
                         f"{block[0]}-{block[-1]} (D-043: spent or reserved)")


def read_food(root: Path) -> dict[Key, tuple[int, str]]:
    """(confirm_k, t_lock, d, defense, seed) -> (food_collected, runid) for every run under root.

    A run without confirm_k or t_lock (a v3 or v4 run), an incomplete run or a repeated key stops
    the caller: a silent mix of versions or a double run would change the verdict.
    """
    out: dict[Key, tuple[int, str]] = {}
    for m in load_manifests(root):
        p = m[S.K_PARAMS]
        try:
            k = int(float(p[manifest_key("confirm_k")]))
            t_lock = int(float(p[manifest_key("t_lock")]))
        except KeyError:
            raise SystemExit(f"stop: run {m[S.K_RUNID]} has no confirm_k or t_lock: it is not a v5 run")
        key = (k, t_lock, int(p[S.P_NDET]), int(p[S.P_DEFENSE]), int(p[S.P_SEED]))
        if key in out:
            raise SystemExit(f"stop: {key} appears twice under {root.name}: {out[key][1]} and {m[S.K_RUNID]}")
        out[key] = (run_food(m), m[S.K_RUNID])
    return out


def arm_food(raw: dict[Key, tuple[int, str]], arm: str, seeds: tuple[int, ...]
             ) -> dict[tuple[int, int], dict[int, float]]:
    """(d, defense) -> {seed: food} of one arm. Stops unless the arm has every d and seed."""
    defense, k, t_lock = ARMS[arm]
    food: dict[tuple[int, int], dict[int, float]] = {}
    for d in DS:
        try:
            food[(d, defense)] = {s: float(raw[(k, t_lock, d, defense, s)][0]) for s in seeds}
        except KeyError as e:
            raise SystemExit(f"stop: arm {arm} is missing run {e.args[0]}")
    return food
