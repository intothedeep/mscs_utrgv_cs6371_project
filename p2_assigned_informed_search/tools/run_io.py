"""Read side of a runs root, shared by check_runs.py and collect_runs.py."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import schema as S

__all__ = ["find_run_dirs", "read_csv", "read_manifest"]


def _is_visible_file(p: Path) -> bool:
    return p.is_file() and not p.name.startswith(".")


def find_run_dirs(root: Path) -> list[Path]:
    """Run folders under a root. The root is `runs`, `mock/runs`, or one set folder (`runs/S1`).

    A child folder holding a file is a run. A child holding only folders is a set folder.
    """
    runs: list[Path] = []
    for child in sorted(p for p in root.iterdir() if p.is_dir()):
        subdirs = [p for p in child.iterdir() if p.is_dir()]
        is_set_folder = subdirs and not any(_is_visible_file(p) for p in child.iterdir())
        runs.extend(sorted(subdirs) if is_set_folder else [child])
    return runs


def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open(newline="") as fh:
        reader = csv.reader(fh)
        return next(reader, []), list(reader)


def read_manifest(run_dir: Path) -> Any:
    """Parsed manifest. Raises OSError or json.JSONDecodeError; the caller names the run."""
    return json.loads((run_dir / S.FILE_MANIFEST).read_text())
