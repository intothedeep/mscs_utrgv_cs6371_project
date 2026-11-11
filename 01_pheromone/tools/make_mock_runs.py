"""MOCK generator (U2): 80 fake runs that satisfy the log schema.

Every value here is invented. Nothing is simulated. The runs exist to prove the
flow (check, analyze, report) before any real pipeline exists (MVP1).
Safety: writes only to mock/runs/. Any other --out exits before writing.
Determinism: all random streams derive from GEN_SEED, so two runs give identical files.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

import schema as S

OUT_ROOT = Path(__file__).resolve().parent.parent / "mock" / "runs"
GEN_SEED = 20261110
STAMP = "20261110-000000"  # fixed, so runids repeat between generator runs
ROBOT_SECONDS = S.TICKS_PER_RUN // S.TICKS_PER_SECOND
STATE_P = (0.10, 0.40, 0.15, 0.10, 0.25)  # fake share of honest robots per state
# Fake cell means (off, on). Loss grows with d, defense wins back about half of it,
# and d = 0 has a small defense cost. Values are not predictions.
MOCK_FOOD = {0: (60.0, 58.0), 1: (52.0, 56.0), 2: (40.0, 49.0), 4: (30.0, 42.0)}
MOCK_WASTED = {0: (0.0, 0.0), 1: (80.0, 40.0), 2: (160.0, 80.0), 4: (280.0, 150.0)}  # d = 0 stays 0


# ---- pure builders ---------------------------------------------------------------

def build_layout(seed: int, d: int) -> dict:
    """Sources and decoys depend on the seed only, so all 8 cells of a seed share them."""
    rng = np.random.default_rng([GEN_SEED, seed, 0])
    sources = np.column_stack([rng.uniform(0.5, 1.7, 3), rng.uniform(-0.6, 0.6, 3)])
    decoys: list[np.ndarray] = []
    for _ in range(10_000):  # rejection sampling: decoy >= 1.5 m from every source
        c = np.array([rng.uniform(-1.0, 1.7), rng.uniform(-1.75, 1.75)])
        if np.all(np.linalg.norm(sources - c, axis=1) >= 1.5):
            decoys.append(c)
        if len(decoys) == 2:
            break
    if len(decoys) < 2:
        raise RuntimeError(f"no decoy spot found for layout seed {seed}")
    return {S.L_SEED: seed, S.L_SOURCES: np.round(sources, 3).tolist(),
            S.L_DECOYS: np.round(np.array(decoys), 3).tolist(),
            S.L_NUSED: S.DECOYS_USED[d], "radius_m": 0.25}


def build_ticks(d: int, defense: int, seed: int, rng: np.random.Generator
                ) -> tuple[dict[str, list], np.ndarray]:
    n = S.TICKS_PER_RUN
    t = np.arange(1, n + 1)
    # The seed effect is shared by all cells of a seed, as paired seeds would be.
    effect = np.random.default_rng([GEN_SEED, seed, 99]).normal(0, 3.0)
    food_final = max(0, int(round(MOCK_FOOD[d][defense] + effect + rng.normal(0, 2.5))))
    food_ticks = np.sort(rng.integers(1, n + 1, size=food_final))
    food = np.searchsorted(food_ticks, t, side="right")  # cumulative deliveries
    target = MOCK_WASTED[d][defense]
    if target > 0:
        inc = rng.random(n) + 0.05
        wasted = np.round(np.cumsum(inc) / inc.sum() * target * (1 + rng.normal(0, 0.1)), 1)
    else:
        wasted = np.zeros(n)
    ramp = 1 - np.exp(-t / 1200)
    pher_true = np.round(np.maximum(0, 8000 * ramp + rng.normal(0, 50, n)), 1)
    if d > 0:
        pher_false = np.round(np.maximum(
            0, d * 600 * ramp * (1 - 0.5 * defense) + rng.normal(0, 20, n)), 1)
    else:
        pher_false = np.zeros(n)
    suspects = (np.minimum(16, (t / n * 4 * d).astype(int)) if defense and d > 0
                else np.zeros(n, dtype=int))
    states = rng.multinomial(S.N_HONEST, STATE_P, size=n)
    cols = {S.COL_TICK: t, S.COL_FOOD: food, S.COL_WASTED: wasted,
            **dict(zip(S.STATE_COUNT_COLUMNS, states.T)),
            "pher_true_sum": pher_true, "pher_false_sum": pher_false,
            "suspects_total": suspects, S.COL_MOCK: np.ones(n, dtype=int)}
    return {name: cols[name].tolist() for name in S.TICKS_COLUMNS}, food_ticks


def build_robots(d: int, rng: np.random.Generator) -> list[list]:
    n = S.N_HONEST + d
    sec = ROBOT_SECONDS
    honest_idx = rng.integers(0, len(S.STATES_HONEST), (sec, S.N_HONEST))
    det_idx = rng.integers(0, len(S.STATES_DETRACTOR), (sec, d))
    states = np.concatenate([np.array(S.STATES_HONEST)[honest_idx],
                             np.array(S.STATES_DETRACTOR)[det_idx]], axis=1)
    returning = S.STATES_HONEST.index("RETURN")
    carrying = np.concatenate([(honest_idx == returning).astype(int),
                               np.zeros((sec, d), dtype=int)], axis=1)
    false_share = (np.round(rng.uniform(0, 1, (sec, n)), 2) if d > 0 else np.zeros((sec, n)))
    cols = {
        S.COL_TICK: np.repeat(np.arange(1, sec + 1) * S.TICKS_PER_SECOND, n).tolist(),
        S.COL_ROBOT: ([f"hb_{i}" for i in range(S.N_HONEST)] + [f"dt_{j}" for j in range(d)]) * sec,
        S.COL_ROLE: (["honest"] * S.N_HONEST + ["detractor"] * d) * sec,
        "x": np.round(rng.uniform(-2, 2, (sec, n)), 2).ravel().tolist(),
        "y": np.round(rng.uniform(-2, 2, (sec, n)), 2).ravel().tolist(),
        "yaw_deg": np.round(rng.uniform(-180, 180, (sec, n))).astype(int).ravel().tolist(),
        S.COL_STATE: states.ravel().tolist(),
        "carrying": carrying.ravel().tolist(),
        "here": rng.integers(0, 201, (sec, n)).ravel().tolist(),
        "false_share": false_share.ravel().tolist(),
    }
    return [cols[name] for name in S.ROBOTS_COLUMNS]


def build_events(d: int, defense: int, food_ticks: np.ndarray, layout: dict,
                 rng: np.random.Generator) -> list[list]:
    rows: list[tuple] = []

    def near(centres: list, n: int) -> np.ndarray:
        c = np.array(centres)[rng.integers(0, len(centres), n)]
        return c + rng.normal(0, 0.15, (n, 2))

    def add(ticks, event: str, robots: list[str], xy: np.ndarray) -> None:
        rows.extend((int(tk), rb, event, round(float(p[0]), 2), round(float(p[1]), 2))
                    for tk, rb, p in zip(ticks, robots, xy))

    def honest(n: int) -> list[str]:
        return [f"hb_{i}" for i in rng.integers(0, S.N_HONEST, n)]

    def anywhere(n: int) -> np.ndarray:
        return rng.uniform(-2, 2, (n, 2))

    n_food = len(food_ticks)
    nest = np.column_stack([rng.uniform(-2, -1, n_food), rng.uniform(-2, 2, n_food)])
    add(food_ticks, "drop", honest(n_food), nest)
    add(np.maximum(1, food_ticks - 150), "pickup", honest(n_food), near(layout[S.L_SOURCES], n_food))
    add(rng.integers(1, S.TICKS_PER_RUN + 1, 2 * n_food), "follow_start", honest(2 * n_food),
        anywhere(2 * n_food))
    add(rng.integers(1, S.TICKS_PER_RUN + 1, n_food), "peak", honest(n_food),
        near(layout[S.L_SOURCES], n_food))
    if d > 0:
        decoys = layout[S.L_DECOYS][:layout[S.L_NUSED]]
        n = 15 * d
        add(rng.integers(1, S.TICKS_PER_RUN + 1, n), "decoy_reach",
            [f"dt_{j}" for j in rng.integers(0, d, n)], near(decoys, n))
        if defense:
            add(rng.integers(1, S.TICKS_PER_RUN + 1, 3 * d), "suspect_add", honest(3 * d),
                near(decoys, 3 * d))
            add(rng.integers(1, S.TICKS_PER_RUN + 1, 4 * d), "cone_abort", honest(4 * d),
                near(decoys, 4 * d))
    rows.sort(key=lambda r: r[0])
    return [list(col) for col in zip(*rows)] if rows else [[] for _ in S.EVENTS_COLUMNS]


def build_run(d: int, defense: int, seed: int) -> dict:
    rng = np.random.default_rng([GEN_SEED, seed, d + 1, defense + 1])
    layout = build_layout(seed, d)
    ticks, food_ticks = build_ticks(d, defense, seed, rng)
    runid = f"{S.MOCK_PREFIX}{STAMP}_d{d}_def{defense}_s{seed}"
    manifest = {
        S.K_SCHEMA: S.SCHEMA_VERSION, S.K_MOCK: True, S.K_RUNID: runid,
        "code_version": "MOCK", "code_sha": {k: "MOCK" for k in S.CODE_SHA_KEYS},
        "git_commit": "MOCK", "git_dirty": False,
        S.K_PARAMS: {S.P_NDET: d, S.P_DEFENSE: defense, S.P_SEED: seed, S.P_LENGTH: 600,
                     "mock_generator_seed": GEN_SEED},
        S.K_LAYOUT: layout,
        "env": {"machine": "MOCK", "argos": "MOCK", "threads": 0},
        S.K_METRICS: {S.M_FOOD: ticks[S.COL_FOOD][-1], S.M_WASTED: ticks[S.COL_WASTED][-1],
                      S.M_TICKS: S.TICKS_PER_RUN, S.M_COMPLETE: True},
    }
    return {"manifest": manifest, "ticks": [ticks[c] for c in S.TICKS_COLUMNS],
            "robots": build_robots(d, rng),
            "events": build_events(d, defense, food_ticks, layout, rng)}


# ---- I/O edge --------------------------------------------------------------------

def write_csv(path: Path, header: tuple[str, ...], columns: list[list]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(zip(*columns))


def write_run(root: Path, run: dict) -> None:
    folder = root / run["manifest"][S.K_RUNID]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / S.MANIFEST_FILE).write_text(json.dumps(run["manifest"], indent=2) + "\n")
    write_csv(folder / S.TICKS_FILE, S.TICKS_COLUMNS, run["ticks"])
    write_csv(folder / S.ROBOTS_FILE, S.ROBOTS_COLUMNS, run["robots"])
    write_csv(folder / S.EVENTS_FILE, S.EVENTS_COLUMNS, run["events"])


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=OUT_ROOT,
                    help="must be mock/runs (anything else is refused)")
    args = ap.parse_args(argv)
    if args.out.resolve() != OUT_ROOT.resolve():
        print(f"refused: --out must be {OUT_ROOT}, got {args.out.resolve()}")
        return 1
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    n = 0
    for d in S.DETRACTOR_COUNTS:
        for defense in S.DEFENSES:
            for seed in S.SEEDS:
                write_run(OUT_ROOT, build_run(d, defense, seed))
                n += 1
    print(f"wrote {n} MOCK runs to {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
