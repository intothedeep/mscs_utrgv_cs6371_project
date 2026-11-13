"""The 80-run sweep (U11, M3-04): frozen values, resume check, sequential run.

Cells: d in 0, 1, 2, 4 x defense 0, 1 x seeds 1 to 10, into runs/sweep/ (G1).
Defense v2 reuses plan_runs() with other seeds, roots and a t_lock value.
All 80 files carry the same frozen values (tuning_pick.json and defense_pick.json).
A cell that already has a complete run with the same setting is skipped, so a stopped
sweep resumes. Runs go one at a time, one core, 300 s each (D-013).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import schema as S
from make_sweep import build_argos, git_stamp
from run_argos import run_argos_files
from run_results import PROJECT, load_manifests
from sweep_params import manifest_key, overrides

__all__ = ["run_sweep", "plan_runs", "frozen_values", "Job"]

ROOT = PROJECT / "runs" / "sweep"
INCOMPLETE = PROJECT / "runs" / "x_sweep_incomplete"  # soft delete: moved out, never removed
PICKS = {"tuning": PROJECT / "results" / "real" / "tuning" / "tuning_pick.json",
         "defense": PROJECT / "results" / "real" / "defense_tuning" / "defense_pick.json"}
FROZEN = {"tuning": ("half_life_s", "lambda_dep"),
          "defense": ("r_suspect", "alpha_cone_deg", "d_cone", "t_end")}


def frozen_values() -> dict[str, float]:
    values: dict[str, float] = {}
    for kind, path in PICKS.items():
        if not path.is_file():
            raise SystemExit(f"stop: {path.relative_to(PROJECT)} is missing. Freeze it first")
        pick = json.loads(path.read_text())
        values.update({name: float(pick[name]) for name in FROZEN[kind]})
    return values


def same_code(old_commit: str, new_commit: str) -> bool:
    """Same commit, or no change under src/ between them (a docs commit must not redo the sweep)."""
    if old_commit == new_commit:
        return True
    return subprocess.run(["git", "diff", "--quiet", old_commit, new_commit, "--", "src"],
                          cwd=PROJECT, capture_output=True).returncode == 0


def is_done(manifests: list[dict], cell: tuple[int, int, int], values: dict[str, float], commit: str) -> bool:
    """A complete run with the same cell, the same code and the same params (D-016, D-011 values)."""
    for m in manifests:
        p = m[S.K_PARAMS]
        if ((p[S.P_NDET], p[S.P_DEFENSE], p[S.P_SEED]) == cell
                and m[S.K_METRICS][S.M_COMPLETE] is True
                and same_code(m["git_commit"], commit)
                and all(float(p[manifest_key(n)]) == v for n, v in values.items())):
            return True
    return False


def move_incomplete_runs(root: Path = ROOT) -> None:
    """A stopped run leaves a folder with no complete manifest. check_runs.py reads every folder
    of a root as a run, so move such a folder out before the next run."""
    for folder in sorted(p for p in root.iterdir() if p.is_dir()) if root.is_dir() else []:
        manifest = folder / S.MANIFEST_FILE
        complete = False
        if manifest.is_file():
            try:
                complete = json.loads(manifest.read_text())[S.K_METRICS][S.M_COMPLETE] is True
            except (json.JSONDecodeError, KeyError):
                complete = False
        if not complete:
            INCOMPLETE.mkdir(parents=True, exist_ok=True)
            shutil.move(str(folder), str(INCOMPLETE / folder.name))
            print(f"moved incomplete run {folder.name} to {INCOMPLETE.relative_to(PROJECT)}/")


Job = tuple[tuple[int, int, int], dict[str, float]]  # ((d, defense, seed), values to set)


def plan_runs(root: Path, jobs: list[Job], run: bool) -> int:
    """Write a .argos file for each job that has no complete run in root, and run them if asked.

    Shared by the v3 sweep, the v2 tuning and the v2 confirmation, so the skip and resume
    rules are the same for all three. Each job carries its own values (frozen ones, t_lock).
    """
    move_incomplete_runs(root)
    commit, _ = git_stamp()
    done = load_manifests(root)
    files: list[Path] = []
    for cell, values in jobs:
        if is_done(done, cell, values, commit):
            continue
        runid, path = build_argos(*cell, root, overrides(**values))
        files.append(path)
        print(f"d={cell[0]} defense={cell[1]} seed={cell[2]}: {runid}")
    print(f"{len(jobs) - len(files)} of {len(jobs)} cells already complete, {len(files)} to run")
    if run:
        run_argos_files(files)
    return 0


def run_sweep(run: bool, root: Path = ROOT, seeds: tuple[int, ...] = S.SEEDS,
              t_lock: float | None = None) -> int:
    """8 cells x seeds with the frozen values. t_lock None leaves the template value (v3 sweep)."""
    values = frozen_values()
    if t_lock is not None:
        values["t_lock"] = float(t_lock)
    # Seed-major order: a stopped sweep leaves whole seeds (all 8 cells) rather than whole cells.
    jobs: list[Job] = [((d, defense, seed), values) for seed in seeds
                       for d in S.DETRACTOR_COUNTS for defense in S.DEFENSES]
    return plan_runs(root, jobs, run)
