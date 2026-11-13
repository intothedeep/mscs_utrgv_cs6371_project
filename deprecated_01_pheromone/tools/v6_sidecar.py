"""Reader of the ID arm sidecar defense_log.csv (DESIGN_M6 section 5, Table 4) and its header check.

  v6_sidecar.py ROOT   check the header of every defense_log.csv under ROOT (run folders). Exit 1 on a bad one.
Used by the arm table and the judge. schema.py and check_runs.py do not know this file.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

__all__ = ["SIDECAR_FILE", "COLUMNS", "read_sidecar", "run_isolation"]

SIDECAR_FILE = "defense_log.csv"
COLUMNS = ("tick", "robot_id", "role", "event", "check_id", "strikes", "isolated", "group_size",
           "trail_creator", "deadline_tick", "group_source", "cells_zeroed", "x", "y")


def read_sidecar(path: Path) -> list[dict[str, str]]:
    """Rows of one sidecar. A missing file or a header that is not Table 4 stops the caller."""
    if not path.is_file():
        raise SystemExit(f"stop: {path} is missing: an id-mode run must write the sidecar")
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise SystemExit(f"stop: {path} header is not the Table 4 columns: {reader.fieldnames}")
        return list(reader)


def run_isolation(rows: list[dict[str, str]]) -> dict[str, float]:
    """Per run: detractors and honest robots isolated at least once (event `isolate`), detractors
    isolated at the last tick (`end_state`), the number of detractors, the first detractor isolation in seconds."""
    iso = {role: {r["robot_id"] for r in rows if r["event"] == "isolate" and r["role"] == role}
           for role in ("detractor", "honest")}
    end = [r for r in rows if r["event"] == "end_state"]
    first = [int(r["tick"]) / 10 for r in rows if r["event"] == "isolate" and r["role"] == "detractor"]
    return {"n_detractors": sum(r["role"] == "detractor" for r in end),
            "det_isolated": len(iso["detractor"]), "honest_isolated": len(iso["honest"]),
            "det_isolated_at_end": sum(r["role"] == "detractor" and r["isolated"] == "1" for r in end),
            "first_det_isolate_s": min(first) if first else float("nan")}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    files = sorted(Path(argv[0]).glob(f"*/{SIDECAR_FILE}"))
    bad = 0
    for f in files:
        try:
            read_sidecar(f)
        except SystemExit as e:
            print(e)
            bad += 1
    print(f"SUMMARY sidecars={len(files)} bad={bad}")
    return 1 if bad or not files else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
