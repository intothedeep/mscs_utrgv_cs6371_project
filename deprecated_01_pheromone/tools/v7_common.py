"""Shared constants and readers of M7, scalability 20 vs 40 honest (D-042, D-043, prereg/scale.md).

One place for the arms, N, seed blocks, roots and the planner, so the run tool and the judge cannot
disagree. No new defense code: the arms are the v6 arms off, v3 and v5 (= the M5 primary arm k2t10).
Reads manifests only.
"""
from __future__ import annotations

import re
from pathlib import Path

import schema as S
from make_sweep import build_argos, git_stamp
from run_argos import run_argos_files
from run_results import PROJECT, load_manifests, require_committed
from sweep_params import overrides
from sweep_plan import frozen_values, move_incomplete_runs
from v6_common import ARMS, is_done, read_arm_runs

__all__ = ["ARM_ORDER", "BEST_ARM", "NS", "D10", "SMOKE_SEEDS", "CONFIRM_SEEDS", "PREREG", "RUNS", "SMOKE_BASE",
           "CONFIRM_BASE", "RESULTS", "VERDICT", "cells", "cell_root", "require_prereg", "plan_runs_v7",
           "read_scale_runs"]

ARM_ORDER = ("off", "v3", "v5")        # keys of v6_common.ARMS. v5 = k2, t_lock 10 = M5 primary arm (k2t10)
BEST_ARM = "v5"                        # named by rule before any M7 run (prereg/scale.md), not after M6
NS = (20, 40)                          # honest robots
D10 = {20: 2, 40: 4}                   # 10 % detractors at each N
SMOKE_SEEDS = (900,)                   # a throwaway block outside D-043 (same as D-048 D6)
CONFIRM_SEEDS = tuple(range(401, 431))  # D-043, used once
RUNS = PROJECT / "runs"
SMOKE_BASE, CONFIRM_BASE = RUNS / "m7_smoke", RUNS / "m7_scale"
PREREG = PROJECT / "prereg" / "scale.md"
RESULTS = PROJECT / "results" / "real" / "scale"
VERDICT = RESULTS / "verdict.json"


def cells(n: int) -> tuple[int, ...]:
    """Detractor counts of the confirm stage at N honest robots: d = 0 and 10 %."""
    return (0, D10[n])


def cell_root(base: Path, arm: str, n: int) -> Path:
    """One run root per arm and N. check_runs.py reads every folder of a root as a run."""
    return base / f"{arm}_n{n}"


def require_prereg() -> None:
    """The confirm stage and the judge: prereg committed and unchanged, best arm equal to BEST_ARM."""
    require_committed(PREREG)
    found = re.search(r"^- Best arm: (\S+)", PREREG.read_text(), re.M)
    if found is None or found.group(1) != BEST_ARM:
        raise SystemExit(f"stop: {PREREG.name} must hold the line '- Best arm: {BEST_ARM}'")


def plan_runs_v7(root: Path, jobs: list[tuple[tuple[int, int, int], str]], n: int, run: bool) -> int:
    """Write a .argos file for each (cell, arm) job with no complete run in root. Run them if asked.

    Own planner: v6_common.plan_runs_v6 passes no honest count. The skip rule is v6_common.is_done,
    after a filter on n_honest.
    """
    move_incomplete_runs(root)
    commit, _ = git_stamp()
    done = [m for m in load_manifests(root) if str(m[S.K_PARAMS].get("n_honest")) == str(n)]
    frozen = frozen_values()
    files: list[Path] = []
    for cell, arm in jobs:
        if is_done(done, cell, arm, 0.0, commit):  # margin is used by the id arm only
            continue
        a = ARMS[arm]
        values: dict[str, float | str] = {**frozen, "confirm_k": a.k, "t_lock": float(a.t_lock)}
        runid, path = build_argos(*cell, root, overrides(**values), {"defense_mode": a.mode}, n_honest=n)
        files.append(path)
        print(f"{arm} n={n} d={cell[0]} defense={cell[1]} seed={cell[2]}: {runid}")
    print(f"{len(jobs) - len(files)} of {len(jobs)} jobs already complete, {len(files)} to run")
    if run:
        run_argos_files(files)
    return 0


def read_scale_runs(root: Path, arm: str, n: int) -> dict[tuple[int, int], tuple[int, Path]]:
    """(d, seed) -> (food, run folder) of one root. Stops on a wrong N, mode, value, code or a repeat."""
    for m in load_manifests(root):
        if str(m[S.K_PARAMS].get("n_honest")) != str(n):
            raise SystemExit(f"stop: run {m[S.K_RUNID]} under {root.name} has n_honest "
                             f"{m[S.K_PARAMS].get('n_honest')}, expected {n}")
    return read_arm_runs(root, arm, 0.0)
