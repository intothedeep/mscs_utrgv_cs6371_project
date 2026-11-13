"""MOCK generator (U2): 90 S1 and 300 S3 fake runs that satisfy the run schema.

Every value here is invented. Nothing is simulated. The runs exist to prove the flow
(check, collect, analyze, report) before any real pipeline exists (MVP1).
Safety: writes only to mock/runs/. Any other --out exits before writing.
Determinism: all random streams derive from GEN_SEED, so two calls give identical files.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

import schema as S

OUT_ROOT = Path(__file__).resolve().parent.parent / S.KIND_MOCK / "runs"
GEN_SEED = 20261112
STAMP = "20261112-000000"   # fixed, so runids repeat between generator calls
N_ROBOTS = 24
ARENA_HALF_M = 5.0
SEED_SD, NOISE_SD = 12.0, 6.0   # shared seed effect, then per-arm noise (invented)
# Invented mean of `collected` per distribution: (cpfa, qmap). One up, one flat, one down,
# so all 3 verdict words can appear. These are not predictions.
MOCK_MEAN = {"random": (240.0, 258.0), "powerlaw": (300.0, 300.0), "clustered": (360.0, 338.0)}
# Invented branch mix of departures per arm.
BRANCH_P = {
    "cpfa": {"fidelity": 0.35, "pheromone": 0.35, "random": 0.30},
    "qmap": {"fidelity": 0.25, "pheromone": 0.25, "map": 0.35, "fallback_random": 0.05,
             "random": 0.10},
}
MOCK_SETS = ("S1", "S3")        # cells come from schema.SET_CELLS
PREREG_SETS = ("S3",)


# ---- pure builders ---------------------------------------------------------------

def build_queries(arm: str, n_dep: int, rng: np.random.Generator) -> list[list]:
    """One row per departure. Cost columns are filled only on rows that asked the map."""
    p = BRANCH_P[arm]
    branches = rng.choice(list(p), size=n_dep, p=list(p.values()))
    times = np.sort(rng.uniform(0, S.SIM_SECONDS, n_dep)).round(2)
    rows, n_points = [], 0
    for i, (t, branch) in enumerate(zip(times, branches)):
        n_points += int(rng.integers(0, 4))
        base = [float(t), f"R{int(rng.integers(0, N_ROBOTS))}", str(branch)]
        if branch in S.QUERY_ANSWER_BRANCHES:
            leaves = 1 + i // 4
            cost = [int(rng.integers(10, 80)), 2 * leaves + 1, leaves, n_points,
                    round(float(rng.uniform(1, 30)), 1),
                    *np.round(rng.uniform(-ARENA_HALF_M, ARENA_HALF_M, 2), 2).tolist(),
                    round(float(rng.uniform(0.5, 8)), 2), int(rng.random() < 0.8)]
        else:
            cost = [""] * (len(S.QUERIES_COLUMNS) - len(base))
        rows.append(base + cost)
    return rows


def build_points(n_rows: int, rng: np.random.Generator) -> list[list]:
    t = np.sort(rng.uniform(0, S.SIM_SECONDS, n_rows)).round(2)
    xy = rng.uniform(-ARENA_HALF_M, ARENA_HALF_M, (n_rows, 2)).round(2)
    return [[float(a), f"R{int(rng.integers(0, N_ROBOTS))}", float(x), float(y)]
            for a, (x, y) in zip(t, xy)]


def layout_sha(distribution: str, seed: int) -> str:
    """Same for both arms of a (distribution, seed). Starts MOCK so it cannot pass for a hash."""
    digest = hashlib.sha256(f"{GEN_SEED}/{distribution}/{seed}".encode()).hexdigest()
    return S.MOCK_MARK + digest[:12 - len(S.MOCK_MARK)]


def build_run(set_name: str, arm: str, distribution: str, seed: int) -> dict:
    dist_i = S.DISTRIBUTIONS.index(distribution)
    arm_mean = MOCK_MEAN[distribution][S.ARMS.index(arm) - 1]   # cpfa -> 0, qmap -> 1
    seed_effect = np.random.default_rng([GEN_SEED, seed, dist_i, 99]).normal(0, SEED_SD)
    rng = np.random.default_rng([GEN_SEED, seed, dist_i, S.ARMS.index(arm)])
    collected = max(0, round(arm_mean + seed_effect + rng.normal(0, NOISE_SD)))
    per_minute = np.cumsum(rng.multinomial(collected, np.full(12, 1 / 12))).tolist()
    n_dep = 2 * collected + int(rng.integers(0, 100))
    queries = build_queries(arm, n_dep, rng)
    runid = f"{S.MOCK_PREFIX}{STAMP}_{arm}_{distribution}_s{seed}"
    manifest = {
        S.K.schema_version: S.SCHEMA_VERSION, S.K.mock: 1, S.K.set: set_name, S.K.arm: arm,
        S.K.distribution: distribution, S.K.seed: seed,
        S.K.git_commit: S.MOCK_MARK, S.K.git_dirty: 0,
        S.K.lib_sha: {S.L.controller: S.MOCK_MARK, S.L.loop: S.MOCK_MARK},
        S.K.xml_sha: S.MOCK_MARK, S.K.prereg_sha: S.MOCK_MARK if set_name in PREREG_SETS else None,
        S.K.nest_radius_xml: 0.25, S.K.nest_radius_eff: 0.456, S.K.respawn: 1,
        S.K.param_set: "xml10", S.K.layout_sha: layout_sha(distribution, seed),
        S.K.wall_s: round(float(rng.normal(6, 1)), 2),
        S.K.code_version: S.MOCK_MARK, S.K.code_sha: S.MOCK_MARK,
        S.K.params: {S.PA.random_seed: seed, S.PA.max_sim_time_s: S.SIM_SECONDS,
                     S.PA.food_distribution: S.DISTRIBUTION_CODES[distribution],
                     "mock_generator_seed": GEN_SEED},
        S.K.env: {S.E.machine: S.MOCK_MARK, S.E.argos: S.MOCK_MARK, S.E.threads: 0},
        S.K.metrics: {
            S.MT.collected: collected, S.MT.sim_time_s: float(S.SIM_SECONDS), S.MT.complete: 1,
            S.MT.n_departures: n_dep,
            S.MT.travel_s: round(float(rng.normal(4300, 150)), 1),
            S.MT.search_s: round(float(rng.normal(8600, 300)), 1)},
    }
    return {
        "runid": runid, "manifest": manifest,
        S.FILE_ARGOS: "MOCK stub: not an ARGoS experiment file. No simulator ran.\n",
        S.FILE_STDOUT: (f"MOCK stub stdout. No simulator ran.\n"
                        f"{collected:.6f}, {S.SIM_SECONDS:.6f}, {seed}\n"),
        S.FILE_FORAGE: [[m + 1, v] for m, v in enumerate(per_minute)],
        S.FILE_QUERIES: queries,
        # cpfa has no map, so it uploads nothing (D-015). Only qmap writes points.
        S.FILE_POINTS: build_points(min(n_dep, 150), rng) if arm == "qmap" else [],
    }


# ---- I/O edge --------------------------------------------------------------------

def write_csv(path: Path, header: tuple[str, ...], rows: list[list]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def write_run(root: Path, set_name: str, run: dict) -> None:
    folder = root / set_name / run["runid"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / S.FILE_ARGOS).write_text(run[S.FILE_ARGOS])
    (folder / S.FILE_STDOUT).write_text(run[S.FILE_STDOUT])
    (folder / S.FILE_MANIFEST).write_text(json.dumps(run["manifest"], indent=2) + "\n")
    write_csv(folder / S.FILE_FORAGE, S.FORAGE_COLUMNS, run[S.FILE_FORAGE])
    write_csv(folder / S.FILE_QUERIES, S.QUERIES_COLUMNS, run[S.FILE_QUERIES])
    write_csv(folder / S.FILE_POINTS, S.POINTS_COLUMNS, run[S.FILE_POINTS])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT_ROOT,
                    help="must be mock/runs (anything else is refused)")
    args = ap.parse_args(argv)
    if args.out.resolve() != OUT_ROOT.resolve():
        print(f"refused: --out must be {OUT_ROOT}, got {args.out.resolve()}")
        return 1
    n = 0
    for set_name in MOCK_SETS:
        arms, seeds = S.SET_CELLS[set_name]
        for arm in arms:
            for distribution in S.DISTRIBUTIONS:
                for seed in seeds:
                    write_run(OUT_ROOT, set_name, build_run(set_name, arm, distribution, seed))
                    n += 1
    print(f"wrote {n} MOCK runs to {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
