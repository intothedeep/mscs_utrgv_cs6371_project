"""Pure G2 statistics (DESIGN 4.2): ratio of means and a paired percentile bootstrap.

No file access. analyze.py feeds it the food_collected values per cell.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

__all__ = ["G2Row", "g2_rows", "N_BOOT", "BOOT_SEED"]

N_BOOT = 10_000     # resamples of the seed index (DESIGN 4.2)
BOOT_SEED = 20261128  # fixed, so the same logs give the same intervals
NAN = math.nan

Food = dict[tuple[int, int], dict[int, float]]  # (d, defense) -> {seed: food_collected}


@dataclass(frozen=True)
class G2Row:
    """One detractor count. d = 0 is the defense-cost row: gain = F(0, on) - F(0, off)."""
    d: int
    n_seeds: int
    f_off: float
    f_on: float
    loss: float
    loss_lo: float
    loss_hi: float
    gain: float
    gain_lo: float
    gain_hi: float
    share: float
    share_lo: float
    share_hi: float
    resolved: bool
    note: str


def _interval(x: np.ndarray) -> tuple[float, float]:
    lo, hi = np.nanpercentile(x, [2.5, 97.5])
    return float(lo), float(hi)


def _row(d: int, base: np.ndarray, off: np.ndarray, on: np.ndarray,
         rng: np.random.Generator) -> G2Row:
    """base, off, on: food per common seed for cells (0, off), (d, off), (d, on)."""
    n = len(base)
    idx = rng.integers(0, n, size=(N_BOOT, n))  # one index draw, shared by all three cells
    mean_b, mean_off, mean_on = (a[idx].mean(axis=1) for a in (base, off, on))
    gain_b = mean_on - mean_off
    gain = float(on.mean() - off.mean())
    g_lo, g_hi = _interval(gain_b)
    if d == 0:  # defense cost row: no loss, no share
        return G2Row(0, n, float(off.mean()), float(on.mean()), NAN, NAN, NAN,
                     gain, g_lo, g_hi, NAN, NAN, NAN, False, "defense cost")
    loss_b = mean_b - mean_off
    loss = float(base.mean() - off.mean())
    l_lo, l_hi = _interval(loss_b)
    if not l_lo > 0:  # DESIGN 4.2: resolved only when the whole interval is above 0 (L > 0)
        return G2Row(d, n, float(off.mean()), float(on.mean()), loss, l_lo, l_hi,
                     gain, g_lo, g_hi, NAN, NAN, NAN, False, f"loss not resolved at {d}")
    with np.errstate(divide="ignore", invalid="ignore"):
        share_b = np.where(loss_b != 0, gain_b / loss_b, np.nan)
    s_lo, s_hi = _interval(share_b)
    return G2Row(d, n, float(off.mean()), float(on.mean()), loss, l_lo, l_hi,
                 gain, g_lo, g_hi, gain / loss, s_lo, s_hi, True, "")


def g2_rows(food: Food, detractor_counts: tuple[int, ...]) -> list[G2Row]:
    """Rows for d = 0 (defense cost) and each d > 0. Missing cells give n_seeds = 0."""
    rng = np.random.default_rng(BOOT_SEED)
    rows = []
    for d in detractor_counts:
        base_off = food.get((0, 0), {})
        cells = [base_off, food.get((d, 0), {}), food.get((d, 1), {})]
        if d == 0:  # cost needs only the two d = 0 cells
            cells = [base_off, base_off, food.get((0, 1), {})]
        seeds = sorted(set.intersection(*(set(c) for c in cells)))
        if not seeds:
            rows.append(G2Row(d, 0, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN,
                              False, f"cells missing at {d}"))
            continue
        base, off, on = (np.array([c[s] for s in seeds], dtype=float) for c in cells)
        rows.append(_row(d, base, off, on, rng))
    return rows
