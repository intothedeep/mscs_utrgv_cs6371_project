"""Figures of analyze.py (DESIGN 6.7). Drawing only: every number arrives from analyze.py.

Layout rules (rules/figures.md): legend outside above the axes, constrained layout,
numbers in the empty headroom above the data, one legend per figure.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from plot_style import ARM_COLOR, title_of

if TYPE_CHECKING:
    from analyze import Comparison

__all__ = ["draw_all"]

HEADROOM = 0.30          # share of the data span kept empty above the data for the numbers
JITTER_SD, JITTER_SEED = 0.04, 0   # fixed, so two runs draw the same points


def _label(c: Comparison) -> str:
    s = c.stats
    return f"{c.verdict}\n{s['improvement_pct']:+.1f} % [{s['ci_low']:+.1f}, {s['ci_high']:+.1f}]"


def _finish(fig: Any, handles: list, title: str, path: Path) -> None:
    # matplotlib 3.11 draws suptitle and an outside legend on top of each other, so the title
    # rides as the legend title: title first, legend row below it, axes under both.
    legend = fig.legend(handles=handles, title=title, loc="outside upper center",
                        ncol=len(handles), frameon=False)
    legend.get_title().set_fontweight("bold")
    fig.savefig(path)
    plt.close(fig)


def boxplot_3dist(results: list[Comparison], con: dict, path: Path, is_mock: bool) -> None:
    ctl, trt = con["control_arm"], con["treatment_arm"]
    fig, ax = plt.subplots(figsize=(9, 5.2), layout="constrained")
    rng = np.random.default_rng(JITTER_SEED)
    for i, c in enumerate(results):
        for arm, values, dx in ((ctl, c.control, -0.2), (trt, c.treatment, 0.2)):
            box = ax.boxplot([values], positions=[i + dx], widths=0.32, patch_artist=True,
                             showfliers=False, medianprops={"color": "black"})
            box["boxes"][0].set_facecolor(ARM_COLOR[arm])
            box["boxes"][0].set_alpha(0.55)
            ax.scatter(i + dx + rng.normal(0, JITTER_SD, len(values)), values, s=9,
                       color=ARM_COLOR[arm], edgecolor="black", linewidth=0.3, zorder=3)
    top = max(max(c.control.max(), c.treatment.max()) for c in results)
    bottom = min(min(c.control.min(), c.treatment.min()) for c in results)
    span = top - bottom
    for i, c in enumerate(results):
        ax.text(i, top + 0.04 * span, _label(c), ha="center", va="bottom", fontsize=8)
    ax.set_ylim(bottom - 0.05 * span, top + HEADROOM * span)
    ax.set_xticks(range(len(results)), [c.distribution for c in results])
    ax.set_ylabel("Items collected at 720 s")
    ax.set_xlabel("Food distribution")
    handles = [Patch(facecolor=ARM_COLOR[ctl], alpha=0.55, label=f"{ctl} (baseline)"),
               Patch(facecolor=ARM_COLOR[trt], alpha=0.55, label=trt),
               Line2D([], [], marker="o", linestyle="", color="gray", markeredgecolor="black",
                      markersize=4, label="one seed")]
    _finish(fig, handles, title_of(f"{trt} vs {ctl}: items collected, improvement and "
                                       "95 % interval above each pair", is_mock), path)


def paired_diff(results: list[Comparison], con: dict, path: Path, is_mock: bool) -> None:
    trt, ctl = con["treatment_arm"], con["control_arm"]
    fig, ax = plt.subplots(figsize=(9, 4.6), layout="constrained")
    xs = np.arange(len(results))
    mean = np.array([c.stats["diff_mean"] for c in results])
    lo = np.array([c.stats["diff_ci_low"] for c in results])
    hi = np.array([c.stats["diff_ci_high"] for c in results])
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.errorbar(xs, mean, yerr=[mean - lo, hi - mean], fmt="o", color=ARM_COLOR[trt],
                capsize=5, markersize=6, linewidth=1.5)
    top, bottom = max(hi.max(), 0), min(lo.min(), 0)
    span = (top - bottom) or 1.0
    for x, m, a, b in zip(xs, mean, lo, hi):
        ax.text(x, top + 0.05 * span, f"{m:+.1f}\n[{a:+.1f}, {b:+.1f}]", ha="center",
                va="bottom", fontsize=8)
    ax.set_ylim(bottom - 0.1 * span, top + HEADROOM * span)
    ax.set_xlim(-0.6, len(results) - 0.4)
    ax.set_xticks(xs, [c.distribution for c in results])
    ax.set_ylabel(f"Mean paired difference, {trt} minus {ctl} (items)")
    ax.set_xlabel("Food distribution")
    handles = [Line2D([], [], marker="o", color=ARM_COLOR[trt],
                      label="mean paired difference with 95 % interval"),
               Line2D([], [], color="black", linestyle="--", label="no difference")]
    _finish(fig, handles, title_of(f"Paired difference per distribution ({trt} minus {ctl})",
                                       is_mock), path)


def branch_shares(shares: dict[tuple[str, str], dict[str, float]], con: dict, path: Path,
                  is_mock: bool) -> None:
    arms = [con["control_arm"], con["treatment_arm"]]
    dists = [d for d in con["distributions"] if any((a, d) in shares for a in arms)]
    fig, axes = plt.subplots(1, len(dists), figsize=(9.5, 4.2), sharey=True, layout="constrained",
                             squeeze=False)
    branches = list(next(iter(shares.values())))
    top = max(v for s in shares.values() for v in s.values())
    for ax, d in zip(axes[0], dists):
        for k, arm in enumerate(arms):
            if (arm, d) not in shares:
                continue
            vals = [shares[(arm, d)][b] for b in branches]
            xs = np.arange(len(branches)) + (k - 0.5) * 0.38
            ax.bar(xs, vals, width=0.38, color=ARM_COLOR[arm], edgecolor="black", linewidth=0.4)
            for x, v in zip(xs, vals):
                ax.text(x, v + 0.01, f"{100 * v:.0f}", ha="center", va="bottom", fontsize=7)
        ax.set_title(d)
        ax.set_xticks(range(len(branches)), branches)
        ax.set_ylim(0, top * 1.2)
    axes[0][0].set_ylabel("Share of nest departures")
    fig.supxlabel("Branch that chose the target (random includes fallback_random; labels in %)")
    handles = [Patch(facecolor=ARM_COLOR[a], edgecolor="black", label=a) for a in arms]
    _finish(fig, handles, title_of("Departures per branch, both arms", is_mock), path)


def draw_all(results: list[Comparison], shares: dict, con: dict, out: Path, suffix: str,
             is_mock: bool) -> None:
    boxplot_3dist(results, con, out / f"fig_boxplot_3dist{suffix}.png", is_mock)
    paired_diff(results, con, out / f"fig_paired_diff{suffix}.png", is_mock)
    branch_shares(shares, con, out / f"fig_branch_shares{suffix}.png", is_mock)
