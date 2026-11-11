"""Run generated .argos files one at a time (D-013): one core, a timeout per run."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

__all__ = ["SRC", "TIMEOUT_S", "run_argos_files"]

SRC = Path(__file__).resolve().parent.parent / "src"  # library paths in .argos are relative to src/
TIMEOUT_S = 300


def run_argos_files(files: list[Path]) -> None:
    """Sequential on purpose: D-013 allows one core. Stops at the first failed run."""
    env = {**os.environ, "OMP_NUM_THREADS": "1"}
    for path in files:
        log = path.with_suffix(".log")
        print(f"run {path.name} (timeout {TIMEOUT_S} s)", flush=True)
        try:
            done = subprocess.run(["argos3", "-c", str(path.relative_to(SRC))], cwd=SRC, env=env,
                                  capture_output=True, text=True, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            raise SystemExit(f"stop: {path.name} passed {TIMEOUT_S} s and was killed")
        log.write_text(done.stdout + done.stderr)
        if done.returncode != 0:
            raise SystemExit(f"stop: argos3 exited {done.returncode} on {path.name}, see {log}")
