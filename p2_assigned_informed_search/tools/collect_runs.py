"""Build runs.csv from run folders (DESIGN 6.5, D-013).

Usage: collect_runs.py <root> --out <csv>
One row per run, exactly schema.RUNS_COLUMNS. A column with no data in the run is empty.
The same code path serves mock and real roots. Only the --out guard looks at the root kind.
Run check_runs.py first: this tool trusts the files it reads.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path
from typing import Any

import run_io
import schema as S

__all__ = ["build_row"]

PROJECT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT / "results"


def _cell(value: str, typ: type) -> Any:
    return None if value == "" else typ(value)


def read_queries(path: Path) -> list[dict[str, Any]]:
    header, rows = run_io.read_csv(path)
    return [{c: _cell(v, S.QUERIES_TYPES[c]) for c, v in zip(header, row)} for row in rows]


def column(rows: list[dict[str, Any]], name: str) -> list[Any]:
    """Non-empty values of one queries column."""
    return [r[name] for r in rows if r[name] is not None]


def last(rows: list[dict[str, Any]], name: str) -> Any:
    """Last non-empty value of one queries column, or None."""
    return (column(rows, name) or [None])[-1]


def build_row(m: dict, run_id: str, queries: list[dict[str, Any]]) -> dict[str, Any]:
    """One runs.csv row. Manifest gives the identity and totals, queries.csv gives the rest."""
    met = m[S.K.metrics]
    shares = {c: None for c in set(S.SHARE_COLUMN_OF_BRANCH.values())}
    if queries:
        shares = {c: 0.0 for c in shares}
        for r in queries:
            shares[S.SHARE_COLUMN_OF_BRANCH[r[S.Q.branch]]] += 1 / len(queries)
    ops, us = column(queries, S.Q.nodes_visited), column(queries, S.Q.query_us)
    reached = column(queries, S.Q.reached)
    row = {
        S.C.schema_version: m[S.K.schema_version], S.C.mock: m[S.K.mock], S.C.run_id: run_id,
        S.C.set: m[S.K.set], S.C.arm: m[S.K.arm], S.C.distribution: m[S.K.distribution],
        S.C.seed: m[S.K.seed], S.C.collected: met[S.MT.collected],
        S.C.sim_time_s: met[S.MT.sim_time_s], S.C.complete: met[S.MT.complete],
        S.C.code_commit: m[S.K.git_commit], S.C.git_dirty: m[S.K.git_dirty],
        S.C.lib_sha_controller: m[S.K.lib_sha][S.L.controller],
        S.C.lib_sha_loop: m[S.K.lib_sha][S.L.loop],
        S.C.nest_radius_xml: m[S.K.nest_radius_xml], S.C.nest_radius_eff: m[S.K.nest_radius_eff],
        S.C.layout_sha: m[S.K.layout_sha], S.C.n_departures: met[S.MT.n_departures],
        **shares,
        S.C.travel_s: met[S.MT.travel_s], S.C.search_s: met[S.MT.search_s],
        S.C.n_queries: len(ops) or None, S.C.points_inserted: last(queries, S.Q.points_inserted_total),
        S.C.nodes_total_end: last(queries, S.Q.nodes_total), S.C.leaves_total_end: last(queries, S.Q.leaves_total),
        S.C.ops_per_query_median: statistics.median(ops) if ops else None,
        S.C.ops_per_query_max: max(ops) if ops else None,
        S.C.us_per_query_median: statistics.median(us) if us else None,
        S.C.targets_reached_share: sum(reached) / len(reached) if reached else None,
        S.C.wall_s: m[S.K.wall_s],
    }
    if row.keys() != set(S.RUNS_COLUMNS):  # a column added to schema.py must be filled here
        raise ValueError(f"row columns differ from schema: {row.keys() ^ set(S.RUNS_COLUMNS)}")
    return row


def out_guard(manifests: list[dict], out: Path) -> str | None:
    """None when --out sits in results/mock for a mock root or results/real for a real root."""
    kinds = {m[S.K.mock] for m in manifests}
    if len(kinds) != 1:
        return f"root holds {len(kinds)} kinds of run (mock and real mixed, or no run)"
    kind = S.KIND_MOCK if kinds == {1} else S.KIND_REAL
    allowed = (RESULTS / kind).resolve()
    if not out.resolve().is_relative_to(allowed):
        return f"--out must be inside {allowed} for a {kind} root, got {out.resolve()}"
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if not args.root.is_dir():
        print(f"refused: root {args.root} is not a folder")
        return 1
    run_dirs = run_io.find_run_dirs(args.root)
    manifests = [run_io.read_manifest(d) for d in run_dirs]
    refusal = out_guard(manifests, args.out)
    if refusal:
        print(f"refused: {refusal}")
        return 1
    rows = [build_row(m, d.name, read_queries(d / S.FILE_QUERIES))
            for d, m in zip(run_dirs, manifests)]
    rows.sort(key=lambda r: (r[S.C.set], r[S.C.run_id]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=S.RUNS_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
