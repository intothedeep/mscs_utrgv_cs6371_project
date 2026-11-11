"""Arm check table of the ID arm (DESIGN_M6 section 5, D-048 D3): detractors isolated per run, from the sidecars.

  v6_arm_table.py [ROOT] [--out FILE]
ROOT is a runs root of id-mode runs (default runs/m6_check/id). Writes one row per run: d, seed, detractors,
detractors isolated (event `isolate`), detractors isolated at the last tick, honest robots isolated,
first detractor isolation in seconds. Report only, no pick. Reads manifests and defense_log.csv only.
A root under mock/ writes to mock/arm_check_mock.csv and never to results/real/ (MOCK data stays isolated).
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import schema as S
from run_results import PROJECT, load_manifests
from v6_common import CHECK_ROOT, RESULTS, arm_root
from v6_sidecar import SIDECAR_FILE, read_sidecar, run_isolation

__all__ = ["arm_rows"]

COLUMNS = ("d", "seed", "n_detractors", "det_isolated", "det_isolated_at_end", "honest_isolated", "first_det_isolate_s")


def arm_rows(root: Path) -> list[dict]:
    rows = []
    for m in load_manifests(root):
        p = m[S.K_PARAMS]
        side = root / m[S.K_RUNID] / SIDECAR_FILE
        if m[S.K_MOCK] is True and not side.is_file():
            continue  # MOCK runs without a sidecar (defense off) are skipped; a real id run must have one
        iso = run_isolation(read_sidecar(side))
        rows.append({"d": int(p[S.P_NDET]), "seed": int(p[S.P_SEED]), **{k: iso[k] for k in COLUMNS[2:]}})
    return sorted(rows, key=lambda r: (r["d"], r["seed"]))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", type=Path, nargs="?", default=arm_root(CHECK_ROOT, "id"))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    is_mock = "mock" in args.root.resolve().relative_to(PROJECT).parts
    out = args.out or (PROJECT / "mock" / "arm_check_mock.csv" if is_mock else RESULTS / "arm_check.csv")
    if is_mock and "mock" not in out.resolve().relative_to(PROJECT).parts:
        raise SystemExit("stop: MOCK data is written under mock/ only")
    rows = arm_rows(args.root)
    if not rows:
        raise SystemExit(f"stop: no complete run under {args.root}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for d in sorted({r["d"] for r in rows}):
        sel = [r for r in rows if r["d"] == d]
        n_fn = sum(r["det_isolated"] == 0 for r in sel)
        print(f"d={d}: {len(sel)} runs, runs with 0 detractors isolated {n_fn}, "
              f"mean detractors isolated {sum(r['det_isolated'] for r in sel) / len(sel):.2f}, "
              f"mean honest isolated {sum(r['honest_isolated'] for r in sel) / len(sel):.2f}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
