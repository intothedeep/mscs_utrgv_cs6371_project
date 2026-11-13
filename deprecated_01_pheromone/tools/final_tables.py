"""Final-results tool (M8-02, part 1): paired contrasts of every confirm block, and the report figures.

Reads saved manifests and verdict files only. Run from 01_pheromone/:
  uv run python tools/final_tables.py

Writes results/real/final/arm_contrasts.csv and four PNG figures (fig_scale only when
results/real/scale/verdict.json exists). Every interval is the g2_stats paired percentile bootstrap
(10,000 resamples, 95 %, fixed seed), so G, L and R here equal the per-block g2_stats.csv files.
G(d) = F(d, arm) - F(d, off) on the same seeds. L(d) = F(0, off) - F(d, off). R(d) = G(d) / L(d).
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np

from analyze import food_by_cell, load_runs, select_cells
from final_figs import fig_cost_vs_gain, fig_honest_isolation, fig_m6_food, fig_scale
from g2_stats import G2Row, g2_rows
from run_results import PROJECT, load_manifests, run_food
from v5_common import ARMS as M5_ARMS, CONFIRM_ROOT as M5_ROOT, CONFIRM_SEEDS as M5_SEEDS, arm_food, read_food
import schema as S

OUT = PROJECT / "results" / "real" / "final"
RUNS = PROJECT / "runs"
M6_ROOT, M6_SEEDS = RUNS / "m6_confirm", tuple(range(321, 361))
M6_ARMS = ("off", "v3", "k1t10", "v5", "id")  # off is the baseline of every contrast
DS = S.DETRACTOR_COUNTS
COLUMNS = ("block", "seeds", "arm", "d", "n", "F_off", "F_arm", "G", "G_lo", "G_hi", "L", "R", "R_lo", "R_hi",
           "source_root")

Food = dict[tuple[int, int], dict[int, float]]  # (d, defense) -> {seed: food}


def rel(p: Path) -> str:
    return str(p.relative_to(PROJECT))


def seeds_label(seeds: tuple[int, ...]) -> str:
    return f"{seeds[0]}-{seeds[-1]}"


def row_dict(block: str, seeds: tuple[int, ...], arm: str, r: G2Row, root: Path) -> dict:
    return {"block": block, "seeds": seeds_label(seeds), "arm": arm, "d": r.d, "n": r.n_seeds, "F_off": r.f_off,
            "F_arm": r.f_on, "G": r.gain, "G_lo": r.gain_lo, "G_hi": r.gain_hi, "L": r.loss, "R": r.share,
            "R_lo": r.share_lo, "R_hi": r.share_hi, "source_root": rel(root)}


def sweep_food(root: Path, seeds: tuple[int, ...]) -> Food:
    """One root holding both defense cells (v3, M4). Stops on a missing cell."""
    cells = select_cells(load_runs(root), seeds)
    if cells["missing"]:
        raise SystemExit(f"stop: {rel(root)} misses {len(cells['missing'])} cells, first {cells['missing'][0]}")
    return food_by_cell(cells["chosen"])


def m6_food(root: Path, defense: int) -> Food:
    """Food of one M6 arm root at its defense value. Stops on a repeat, a seed outside the block or a gap."""
    out: dict[tuple[int, int], dict[int, float]] = {(d, defense): {} for d in DS}
    for m in load_manifests(root):
        p = m[S.K_PARAMS]
        d, s = int(p[S.P_NDET]), int(p[S.P_SEED])
        if int(p[S.P_DEFENSE]) != defense or s not in M6_SEEDS or s in out[(d, defense)]:
            raise SystemExit(f"stop: run {m[S.K_RUNID]} under {rel(root)}: wrong defense, seed or a repeat")
        out[(d, defense)][s] = float(run_food(m))
    if any(len(v) != len(M6_SEEDS) for v in out.values()):
        raise SystemExit(f"stop: {rel(root)} is not {len(M6_SEEDS)} seeds at every d")
    return out


def block_rows(block: str, seeds: tuple[int, ...], arm: str, food: Food, root: Path) -> list[dict]:
    return [row_dict(block, seeds, arm, r, root) for r in g2_rows(food, DS)]


def collect() -> tuple[list[dict], dict[str, dict[int, np.ndarray]]]:
    """All contrast rows, and the M6 food per arm and d (for fig_m6_food)."""
    rows: list[dict] = []
    v3_seeds = tuple(range(1, 11))
    rows += block_rows("v3", v3_seeds, "v3", sweep_food(RUNS / "sweep", v3_seeds), RUNS / "sweep")
    m4_seeds = tuple(range(11, 31))
    for arm, root in (("t10", RUNS / "sweep_v2"), ("t0", RUNS / "sweep_v2_lock0")):
        rows += block_rows("M4", m4_seeds, arm, sweep_food(root, m4_seeds), root)
    raw = read_food(M5_ROOT)
    off5 = arm_food(raw, "off", M5_SEEDS)
    for arm in M5_ARMS:
        if arm != "off":
            rows += block_rows("M5", M5_SEEDS, arm, {**off5, **arm_food(raw, arm, M5_SEEDS)}, M5_ROOT)
    m6 = {arm: m6_food(M6_ROOT / arm, 0 if arm == "off" else 1) for arm in M6_ARMS}
    for arm in M6_ARMS[1:]:
        food = {(d, 0): m6["off"][(d, 0)] for d in DS} | {(d, 1): m6[arm][(d, 1)] for d in DS}
        rows += block_rows("M6", M6_SEEDS, arm, food, M6_ROOT / arm)
    per_arm = {arm: {d: np.array([m6[arm][(d, 0 if arm == "off" else 1)][s] for s in M6_SEEDS]) for d in DS}
               for arm in M6_ARMS}
    return rows, per_arm


def fmt(v: object) -> object:
    if isinstance(v, float):
        return "" if math.isnan(v) else f"{v:.4f}"
    return v


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows, m6_per_arm = collect()
    csv_path = OUT / "arm_contrasts.csv"
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows({k: fmt(v) for k, v in r.items()} for r in rows)
    blocks = sorted({(r["block"], r["arm"]) for r in rows})
    print(f"table  {csv_path}: {len(rows)} rows, {len(blocks)} block-arm pairs")
    figs = [("fig_m6_food", fig_m6_food(m6_per_arm, OUT / "fig_m6_food.png")),
            ("fig_cost_vs_gain", fig_cost_vs_gain(rows, OUT / "fig_cost_vs_gain.png")),
            ("fig_honest_isolation", fig_honest_isolation(PROJECT / "results" / "real" / "id_arm" / "isolation.csv",
                                                          OUT / "fig_honest_isolation.png")),
            ("fig_scale", fig_scale(PROJECT / "results" / "real" / "scale" / "verdict.json", OUT / "fig_scale.png"))]
    for name, path in figs:
        print(f"figure {name}: {path if path else 'skipped'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
