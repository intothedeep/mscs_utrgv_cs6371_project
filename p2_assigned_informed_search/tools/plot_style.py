"""The one style module of every figure (rules/visualization.md 5, rules/figures.md 5, 6).

An arm keeps its color in every figure. The baseline arms are gray.
Importing this module is enough: it selects the Agg backend and sets the rc values.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (after the backend choice)
from matplotlib import font_manager  # noqa: E402

__all__ = ["ARM_COLOR", "SERIES_COLOR", "FONT_FAMILY", "FIG_DPI", "MOCK_TITLE_PREFIX", "title_of"]

ARM_COLOR = {"vendor": "#5f5f5f", "cpfa": "#9a9a9a", "qmap": "#0072b2"}
FONT_FAMILY = ["Noto Sans KR", "NanumGothic", "Apple SD Gothic Neo", "DejaVu Sans"]
FIG_DPI = 150
SERIES_COLOR = "#4d4d4d"   # bars that are not an arm (counts, checks)
MOCK_TITLE_PREFIX = "MOCK DATA: "

# Only installed families go to matplotlib: a missing one makes it warn on every lookup.
_INSTALLED = {f.name for f in font_manager.fontManager.ttflist}

plt.rcParams.update({
    "font.family": [f for f in FONT_FAMILY if f in _INSTALLED],
    "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "axes.grid": True, "grid.color": "#e3e3e3", "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": FIG_DPI,
})


def title_of(text: str, is_mock: bool) -> str:
    return (MOCK_TITLE_PREFIX if is_mock else "") + text
