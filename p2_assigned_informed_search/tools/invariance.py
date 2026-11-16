"""Invariance check: switch off equals vendor (M2-06, DESIGN 4.3).

Usage:
  invariance.py --determinism <run_a> <run_b>
  invariance.py <root> --out results/real/S0/invariance.json     (S0v2 uses another --out)
--determinism compares two runs of one cell: collected and every per-minute row.
<root> pairs each vendor run with the cpfa run of the same (distribution, seed) and compares the
same values. The expected pairs come from schema.SET_CELLS for the set in the manifests, so a
missing run is a failure, never a quiet pass. A run marked failed by run_argos.py is a mismatch.
Exit 0 only when every expected pair is equal. A failure names the pair and the first differing
minute. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import run_io
import schema as S

__all__ = ["compare_runs"]

PROJECT = Path(__file__).resolve().parent.parent
MARK_FAILED = "failed"        # run_argos.py writes params.failed for a failed run
VENDOR, CPFA = S.ARMS[0], S.ARMS[1]


# ---- pure ------------------------------------------------------------------------

def first_difference(a: list[int], b: list[int]) -> int | None:
    """1-based minute of the first difference. A length difference counts. None when equal."""
    for i in range(max(len(a), len(b))):
        if i >= len(a) or i >= len(b) or a[i] != b[i]:
            return i + 1
    return None


def compare_runs(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Result of one pair. Each side: {'collected', 'per_minute', 'failed'}."""
    for side, run in (("a", a), ("b", b)):
        if run["failed"]:
            return {"equal": False, "reason": f"run {side} is marked failed: {run['failed']}"}
    if not a["per_minute"] or not b["per_minute"]:
        return {"equal": False, "reason": "a run has no per-minute row"}
    minute = first_difference(a["per_minute"], b["per_minute"])
    if minute is not None:
        return {"equal": False, "first_differing_minute": minute,
                "reason": f"per-minute rows differ at minute {minute}"}
    if a["collected"] != b["collected"]:
        return {"equal": False, "reason": f"collected {a['collected']} != {b['collected']}"}
    return {"equal": True}


def expected_pairs(manifests: list[dict]) -> list[tuple[str, int]]:
    """(distribution, seed) cells the sets in the root must hold, from schema.SET_CELLS."""
    sets = sorted({m[S.K.set] for m in manifests})
    cells: list[tuple[str, int]] = []
    for name in sets:
        if name not in S.SET_CELLS:
            raise ValueError(f"set {name} has no fixed cells in schema.SET_CELLS")
        cells += [(d, s) for d in S.DISTRIBUTIONS for s in S.SET_CELLS[name][1]]
    return cells


# ---- I/O edge --------------------------------------------------------------------

def load_run(run_dir: Path) -> dict[str, Any]:
    manifest = run_io.read_manifest(run_dir)
    _, rows = run_io.read_csv(run_dir / S.FILE_FORAGE)
    return {"folder": run_dir.name, "manifest": manifest,
            "collected": manifest[S.K.metrics][S.MT.collected],
            "per_minute": [int(r[1]) for r in rows],
            "failed": manifest[S.K.params].get(MARK_FAILED)}


def determinism(path_a: Path, path_b: Path) -> int:
    a, b = load_run(path_a), load_run(path_b)
    result = compare_runs(a, b)
    print(f"{'PASS' if result['equal'] else 'FAIL'} determinism {a['folder']} vs {b['folder']}"
          + ("" if result["equal"] else f": {result['reason']}"))
    return 0 if result["equal"] else 1


def pair_root(root: Path, out: Path) -> int:
    runs = [load_run(d) for d in run_io.find_run_dirs(root)]
    if not runs:
        print(f"FAIL root {root} holds no run")
        return 1
    if any(r["manifest"][S.K.mock] for r in runs):
        print("FAIL root holds a mock run. Invariance reads real runs only")
        return 1
    by_cell: dict[tuple[str, str, int], dict[str, Any]] = {}
    for r in runs:
        m = r["manifest"]
        by_cell[(m[S.K.arm], m[S.K.distribution], m[S.K.seed])] = r
    pairs, lines = [], []
    for distribution, seed in expected_pairs([r["manifest"] for r in runs]):
        a, b = by_cell.get((VENDOR, distribution, seed)), by_cell.get((CPFA, distribution, seed))
        name = f"{S.K.distribution}={distribution} {S.K.seed}={seed}"
        if a is None or b is None:
            result = {"equal": False, "reason": f"missing run: {VENDOR} {a is not None}, {CPFA} {b is not None}"}
        else:
            result = compare_runs(a, b)
        pairs.append({S.K.distribution: distribution, S.K.seed: seed,
                      "run_vendor": a and a["folder"], "run_cpfa": b and b["folder"], **result})
        if not result["equal"]:
            lines.append(f"FAIL pair {name}: {result['reason']}")
    n_equal = sum(p["equal"] for p in pairs)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"root": str(root), "pairs_total": len(pairs), "pairs_equal": n_equal,
                               "pairs": pairs}, indent=2) + "\n")
    print("\n".join(lines + [f"{'PASS' if n_equal == len(pairs) else 'FAIL'} "
                             f"{n_equal} of {len(pairs)} pairs equal, written to {out}"]))
    return 0 if n_equal == len(pairs) else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", type=Path)
    ap.add_argument("--determinism", nargs=2, type=Path, metavar=("RUN_A", "RUN_B"))
    ap.add_argument("--out", type=Path, help="invariance.json, required with a root")
    args = ap.parse_args(argv)
    try:
        if args.determinism:
            return determinism(*args.determinism)
        if args.root is None or args.out is None:
            ap.error("give --determinism A B, or a root with --out")
        return pair_root(args.root, args.out)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as err:
        print(f"FAIL {type(err).__name__}: {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
