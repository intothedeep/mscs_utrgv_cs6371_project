"""Read saved real runs: hashes, git checks, and the food of each run (M2 scripts).

Reads manifests only. Every failure is a SystemExit with a message, so the callers
(tuning pick, keep-A judge) stop with a nonzero exit when an expected run is missing
or not complete.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import schema as S

__all__ = ["PROJECT", "sha256_hex", "require_committed", "load_manifests", "run_food",
           "TUNING_PARAMS"]

PROJECT = Path(__file__).resolve().parent.parent
# Tuned .argos values as they appear in manifest params (the controller ones get a prefix).
TUNING_PARAMS = {"half_life_s": "half_life_s",
                 "lambda_dep": "controller_pheromone_lambda_dep"}


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_committed(path: Path) -> None:
    """A pre-registration must be committed and unchanged before any run (rules/measurement.md 1)."""
    rel = str(path.relative_to(PROJECT))
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=PROJECT,
                             capture_output=True, text=True)
    changed = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=PROJECT,
                             capture_output=True, text=True)
    if tracked.returncode != 0 or changed.stdout.strip():
        raise SystemExit(f"stop: {rel} must be committed and unchanged before the runs")


def load_manifests(root: Path) -> list[dict]:
    if not root.is_dir():
        return []
    return [json.loads(p.read_text()) for p in sorted(root.glob(f"*/{S.MANIFEST_FILE}"))]


def run_food(manifest: dict) -> int:
    """food_collected of a complete run. A run that stopped early stops the caller."""
    metrics = manifest[S.K_METRICS]
    if metrics[S.M_COMPLETE] is not True:
        raise SystemExit(f"stop: run {manifest[S.K_RUNID]} is not complete")
    return int(metrics[S.M_FOOD])
