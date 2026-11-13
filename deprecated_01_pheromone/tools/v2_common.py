"""Shared constants and readers of defense v2 (D-028 to D-032, prereg/defense_v2_lockout.md).

One place for the t_lock candidates, seed sets, roots and the manifest reader, so the tuning,
pick, confirm and judge scripts cannot disagree. Reads manifests only.
"""
from __future__ import annotations

import json
from pathlib import Path

import schema as S
from run_results import PROJECT, load_manifests, run_food
from sweep_params import manifest_key

__all__ = ["T_LOCKS", "TUNE_SEEDS", "CONFIRM_SEEDS", "TUNE_CELLS", "CONFIRM_CELLS", "TUNE_ROOT",
           "CONFIRM_ROOT", "CONTROL_ROOT", "PREREG", "PICK", "VERDICT", "read_food", "load_pick"]

T_LOCKS = (0, 5, 10, 20)                        # spec item 2, seconds
TUNE_SEEDS = tuple(range(107, 117))             # spec item 5, never 1-10 or 11-30
CONFIRM_SEEDS = tuple(range(11, 31))            # spec item 7, used once
TUNE_CELLS = ((2, 1), (0, 1))                   # (d, defense)
CONFIRM_CELLS = tuple((d, f) for d in S.DETRACTOR_COUNTS for f in S.DEFENSES)
TUNE_ROOT = PROJECT / "runs" / "tuning_v2"
CONFIRM_ROOT = PROJECT / "runs" / "sweep_v2"
CONTROL_ROOT = PROJECT / "runs" / "sweep_v2_lock0"
PREREG = PROJECT / "prereg" / "defense_v2_lockout.md"
RESULTS = PROJECT / "results" / "real"
PICK = RESULTS / "tuning_v2" / "pick.json"
VERDICT = RESULTS / "v2" / "verdict.json"

Key = tuple[int, int, int, int]  # (t_lock, d, defense, seed)


def read_food(root: Path) -> dict[Key, tuple[int, str]]:
    """(t_lock, d, defense, seed) -> (food_collected, runid) for every run under root.

    An incomplete run, a run without t_lock (a v3 run) or a repeated key stops the caller:
    a silent mix of versions or a double run would change the verdict.
    """
    out: dict[Key, tuple[int, str]] = {}
    for m in load_manifests(root):
        p = m[S.K_PARAMS]
        try:
            t_lock = int(float(p[manifest_key("t_lock")]))
        except KeyError:
            raise SystemExit(f"stop: run {m[S.K_RUNID]} has no t_lock: it is not a v4 run")
        key = (t_lock, int(p[S.P_NDET]), int(p[S.P_DEFENSE]), int(p[S.P_SEED]))
        if key in out:
            raise SystemExit(f"stop: {key} appears twice under {root.name}: {out[key][1]} and {m[S.K_RUNID]}")
        out[key] = (run_food(m), m[S.K_RUNID])
    return out


def load_pick() -> int:
    """The picked t_lock from the tuning pick file. Stops when the pick is missing."""
    if not PICK.is_file():
        raise SystemExit(f"stop: {PICK.relative_to(PROJECT)} is missing. Run tuning_v2_pick.py first")
    return int(json.loads(PICK.read_text())["picked_t_lock"])
