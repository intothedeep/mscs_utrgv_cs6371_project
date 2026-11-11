"""Figures of the final report (M8-02). Reads saved outputs only; the caller passes the numbers.

Each function writes one PNG and returns its path, or None when its input file is missing.
Style: figures.md (legend below the axes so it never covers the suptitle, units on axes, short title, text >= 7 pt).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display: charts go to files
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from g2_stats import BOOT_SEED, N_BOOT  # noqa: E402

__all__ = ["boot_mean_interval", "fig_m6_food", "fig_cost_vs_gain", "fig_honest_isolation", "fig_scale"]

COLORS = {"off": "#7f7f7f", "v3": "#4c78a8", "k1t10": "#f58518", "v5": "#54a24b", "id": "#b279a2"}
MARKERS = {"M5": "o", "M6": "s"}
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3, "axes.axisbelow": True})


def boot_mean_interval(x: np.ndarray) -> tuple[float, float, float]:
    """Mean and 95 % percentile bootstrap interval over seeds (same N_BOOT and BOOT_SEED as g2_stats)."""
    idx = np.random.default_rng(BOOT_SEED).integers(0, len(x), size=(N_BOOT, len(x)))
    lo, hi = np.percentile(x[idx].mean(axis=1), [2.5, 97.5])
    return float(x.mean()), float(lo), float(hi)


def _save(fig: plt.Figure, path: Path) -> Path:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def fig_m6_food(food: dict[str, dict[int, np.ndarray]], out: Path) -> Path:
    """food[arm][d] = food per seed. Mean food per run against detractor count, one line per arm."""
    fig, ax = plt.subplots(figsize=(7, 4.5), layout="constrained")
    arms = list(food)
    for i, arm in enumerate(arms):
        ds = sorted(food[arm])
        m = np.array([boot_mean_interval(food[arm][d]) for d in ds])
        x = np.array(ds) + 0.06 * (i - (len(arms) - 1) / 2)  # offset so whiskers do not overlap
        ax.errorbar(x, m[:, 0], yerr=[m[:, 0] - m[:, 1], m[:, 2] - m[:, 0]], label=arm, color=COLORS[arm],
                    marker="o", capsize=3, lw=1.2)
    ax.set_xticks(sorted(food[arms[0]]))
    ax.set_xlabel("Detractor robots d (count)")
    ax.set_ylabel("Food collected per run (items)")
    fig.suptitle("M6 confirm: food by arm (mean, 95 % interval)")
    fig.legend(*ax.get_legend_handles_labels(), loc="outside lower center", ncol=len(arms))
    return _save(fig, out)


def fig_cost_vs_gain(rows: list[dict], out: Path) -> Path:
    """x = cost G(0), y = gain G(2), one point per arm of M5 and M6, whiskers = 95 % intervals."""
    by = {(r["block"], r["arm"], r["d"]): r for r in rows if r["block"] in MARKERS}
    fig, ax = plt.subplots(figsize=(7, 5), layout="constrained")
    for (block, arm, d), r0 in sorted(by.items()):
        if d != 0:
            continue
        r2 = by[(block, arm, 2)]
        color = COLORS.get(arm, "#333333")
        ax.errorbar(r0["G"], r2["G"], xerr=[[r0["G"] - r0["G_lo"]], [r0["G_hi"] - r0["G"]]],
                    yerr=[[r2["G"] - r2["G_lo"]], [r2["G_hi"] - r2["G"]]], marker=MARKERS[block],
                    color=color, capsize=3, lw=1, ms=7)
        ax.annotate(arm, (r0["G"], r2["G"]), textcoords="offset points", xytext=(6, 5), fontsize=8)
    ax.axhline(0, color="k", lw=0.6)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_xlabel("d = 0 cost G(0) = F(on) - F(off) (food items per run)")
    ax.set_ylabel("d = 2 gain G(2) = F(on) - F(off) (food items per run)")
    fig.suptitle("Cost at d = 0 against gain at d = 2")
    handles = [plt.Line2D([], [], ls="", marker=m, color="#555555", label=f"{b} confirm") for b, m in MARKERS.items()]
    fig.legend(handles=handles, loc="outside lower center", ncol=len(handles))
    return _save(fig, out)


def fig_honest_isolation(isolation_csv: Path, out: Path) -> Path | None:
    """ID arm, one dot per run: honest and detractor robots isolated at d = 0, 1, 2, 4."""
    if not isolation_csv.is_file():
        print(f"note: {isolation_csv} is missing, fig_honest_isolation skipped")
        return None
    with isolation_csv.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    ds = sorted({int(r["d"]) for r in rows})
    rng = np.random.default_rng(0)  # jitter only
    fig, ax = plt.subplots(figsize=(7, 4.5), layout="constrained")
    for off, key, color, label in ((-0.15, "honest_isolated", "#4c78a8", "honest robots isolated"),
                                   (0.15, "det_isolated", "#e45756", "detractors isolated")):
        for i, d in enumerate(ds):
            v = np.array([float(r[key]) for r in rows if int(r["d"]) == d])
            ax.scatter(i + off + rng.uniform(-0.08, 0.08, len(v)), v, s=10, alpha=0.5, color=color,
                       label=label if i == 0 else None)
            ax.hlines(v.mean(), i + off - 0.12, i + off + 0.12, color="k", lw=2)
    ax.plot([], [], color="k", lw=2, label="mean over runs")
    ax.set_xticks(range(len(ds)), [str(d) for d in ds])
    ax.set_xlabel("Detractor robots d (count)")
    ax.set_ylabel("Robots isolated per run (count)")
    fig.suptitle("ID arm: isolations per run (40 runs per d)")
    fig.legend(*ax.get_legend_handles_labels(), loc="outside lower center", ncol=3)
    return _save(fig, out)


def fig_scale(verdict: Path, out: Path) -> Path | None:
    """M7: per-robot gain G/N at N = 20 and 40 per arm, mean and 95 % interval over seeds."""
    if not verdict.is_file():
        print(f"note: {verdict} is missing, fig_scale skipped")
        return None
    gain = json.loads(verdict.read_text())["metric_G_per_robot"]
    ns = ("n20", "n40")
    fig, ax = plt.subplots(figsize=(6, 4.5), layout="constrained")
    for i, arm in enumerate(gain):
        m = np.array([boot_mean_interval(np.array(gain[arm]["G_per_robot_per_seed"][n])) for n in ns])
        x = np.arange(2) + 0.06 * (i - (len(gain) - 1) / 2)
        ax.errorbar(x, m[:, 0], yerr=[m[:, 0] - m[:, 1], m[:, 2] - m[:, 0]], marker="o", capsize=3,
                    color=COLORS.get(arm, "#333333"), label=arm)
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xticks(range(2), ["N = 20 (d = 2)", "N = 40 (d = 4)"])
    ax.set_xlim(-0.4, 1.4)
    ax.set_xlabel("Honest robots N (count) and 10 % detractors")
    ax.set_ylabel("Gain per robot G/N (food items per robot)")
    fig.suptitle("M7: per-robot gain at two team sizes")
    fig.legend(*ax.get_legend_handles_labels(), loc="outside lower center", ncol=len(gain))
    return _save(fig, out)
