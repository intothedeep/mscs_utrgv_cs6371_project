"""Per-cell outputs of analyze.py (M3-05): food and wasted-time bar charts, event counts, notes.

One bar pair per detractor count (defense off, defense on). Dots are the single seeds.
Reads manifests (through the chosen runs) and events.csv. Pure helpers plus one I/O function.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import schema as S  # noqa: E402

__all__ = ["NOTES", "EVENTS_FILE", "write_cell_outputs"]

EVENTS_FILE = "events_by_cell.csv"
COUNTED_EVENTS = ("suspect_add", "cone_abort", "decoy_reach")
COLORS = ("#4c78a8", "#f58518")
# The three limits the report must state (DESIGN section 7 R10, R11, and D-009).
NOTES = (
    "R10: the d detractors are added to the 20 honest robots (D-005). They also crowd the arena, "
    "so part of the loss at d > 0 is crowding, not deception.",
    "D-009: d = 1, 2, 4 use 1, 2, 2 decoys. Going from d = 2 to d = 4 raises the trail refresh rate, "
    "not the number of decoys.",
    "R11: the cells of one seed share the layout (sources and decoys). Robot starts can differ "
    "across cells because the robot count differs, so the bootstrap pairs cells on layout, "
    "not on every robot start.",
)


def by_cell(chosen: dict, field: str) -> dict[tuple[int, int], list[float]]:
    cells: dict = defaultdict(list)
    for (d, defense, _seed), run in sorted(chosen.items()):
        cells[(d, defense)].append(run[field])
    return cells


def bar_chart(path: Path, title: str, ylabel: str, cells: dict[tuple[int, int], list[float]]) -> None:
    fig, ax = plt.subplots(figsize=(6.8, 4.4), layout="constrained")
    width = 0.38
    for defense, color in zip(S.DEFENSES, COLORS):
        for x, d in enumerate(S.DETRACTOR_COUNTS):
            values = cells.get((d, defense), [])
            if not values:
                continue
            pos = x + (defense - 0.5) * width
            ax.bar(pos, sum(values) / len(values), width=width * 0.9, color=color, alpha=0.75,
                   label=f"defense {'on' if defense else 'off'}" if x == 0 else None)
            ax.plot([pos] * len(values), values, "k.", markersize=3)
    ax.set_xticks(range(len(S.DETRACTOR_COUNTS)), [f"d = {d}" for d in S.DETRACTOR_COUNTS])
    ax.set_xlabel("detractors added to the 20 honest robots (d)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.legend(loc="outside lower center", ncol=2)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def event_means(root: Path, chosen: dict) -> dict[tuple[int, int], dict[str, float]]:
    """Mean events per run, per cell, for the counted event names."""
    totals: dict = defaultdict(Counter)
    runs: Counter = Counter()
    for (d, defense, _seed), run in chosen.items():
        path = root / run["runid"] / S.EVENTS_FILE
        if not path.is_file():
            raise SystemExit(f"stop: {path} is missing for a chosen run")
        with path.open(newline="") as fh:
            totals[(d, defense)].update(r[S.COL_EVENT] for r in csv.DictReader(fh))
        runs[(d, defense)] += 1
    return {cell: {e: totals[cell][e] / runs[cell] for e in COUNTED_EVENTS} for cell in runs}


def write_cell_outputs(out: Path, root: Path, chosen: dict, mock: bool) -> list[Path]:
    """Write the two charts and the event table. Returns the files written."""
    assert set(COUNTED_EVENTS) <= set(S.EVENT_NAMES)
    stamp, suffix = ("MOCK DATA: ", "_MOCK") if mock else ("", "")
    food = out / f"food_by_cell{suffix}.png"
    wasted = out / f"wasted_by_cell{suffix}.png"
    bar_chart(food, f"{stamp}food collected per cell (dots = seeds)", "food_collected (items in 600 s)",
              by_cell(chosen, "food"))
    bar_chart(wasted, f"{stamp}wasted robot-seconds per cell (dots = seeds)", "wasted_robot_seconds",
              by_cell(chosen, "wasted"))
    table = out / EVENTS_FILE
    means = event_means(root, chosen)
    with table.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow([S.P_NDET, S.P_DEFENSE, "runs", *(f"mean_{e}" for e in COUNTED_EVENTS)])
        for (d, defense), m in sorted(means.items()):
            n = sum(1 for k in chosen if k[0] == d and k[1] == defense)
            w.writerow([d, defense, n, *(f"{m[e]:.2f}" for e in COUNTED_EVENTS)])
    return [food, wasted, table]
