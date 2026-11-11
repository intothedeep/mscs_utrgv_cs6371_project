"""The 80-run sweep (U11, M3-04): frozen values, resume check, sequential run.

Cells: d in 0, 1, 2, 4 x defense 0, 1 x seeds 1 to 10, into runs/sweep/ (G1).
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
from sweep_params import Override, manifest_key, overrides

__all__ = ["run_sweep"]

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


def move_incomplete_runs() -> None:
    """A stopped run leaves a folder with no complete manifest. check_runs.py reads every folder
    of a root as a run, so move such a folder out before the next run."""
    for folder in sorted(p for p in ROOT.iterdir() if p.is_dir()) if ROOT.is_dir() else []:
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


def run_sweep(run: bool) -> int:
    values = frozen_values()
    set_values: tuple[Override, ...] = overrides(**values)
    move_incomplete_runs()
    commit, _ = git_stamp()
    done = load_manifests(ROOT)
    files: list[Path] = []
    # Seed-major order: a stopped sweep leaves whole seeds (all 8 cells) rather than whole cells.
    for seed in S.SEEDS:
        for d in S.DETRACTOR_COUNTS:
            for defense in S.DEFENSES:
                if is_done(done, (d, defense, seed), values, commit):
                    continue
                runid, path = build_argos(d, defense, seed, ROOT, set_values)
                files.append(path)
                print(f"d={d} defense={defense} seed={seed}: {runid}")
    total = len(S.DETRACTOR_COUNTS) * len(S.DEFENSES) * len(S.SEEDS)
    print(f"{total - len(files)} of {total} cells already complete, {len(files)} to run")
    if run:
        run_argos_files(files)
    return 0
