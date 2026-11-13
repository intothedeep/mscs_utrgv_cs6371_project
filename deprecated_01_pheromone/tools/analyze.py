"""Analysis (U3, DESIGN 4.2): recovered loss share R(d) from a runs root.

Usage: analyze.py <root> [--out DIR] [--seeds a-b]   (default seeds 1-10)
Also writes food_by_cell, wasted_by_cell charts and events_by_cell.csv (cell_report.py).
Reads manifests (metrics equal the last ticks row, check_runs.py enforces that), and events.csv for the cell counts.
Stops when the root mixes mock and real runs. Mock output goes to results/mock/,
real output to results/real/. A mock chart is stamped MOCK DATA in title and file name.
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display: charts go to files
import matplotlib.pyplot as plt  # noqa: E402

import schema as S  # noqa: E402
from cell_report import NOTES, write_cell_outputs  # noqa: E402
from g2_stats import G2Row, g2_rows  # noqa: E402
from sweep_params import parse_seeds  # noqa: E402

__all__ = ["load_runs", "select_cells", "SUMMARY_COLUMNS", "SUMMARY_FILE", "STATS_FILE", "LOG_FILE"]

PROJECT = Path(__file__).resolve().parent.parent
SUMMARY_COLUMNS = (S.K_RUNID, S.COL_MOCK, S.P_NDET, S.P_DEFENSE, S.P_SEED, S.M_FOOD,
                   S.M_WASTED, S.M_COMPLETE)
SUMMARY_FILE, STATS_FILE, LOG_FILE = "summary.csv", "g2_stats.csv", "analyze_log.txt"
CHART_BAR = "#4c78a8"


# ---- pure helpers ----------------------------------------------------------------

def single_mock_flag(runs: list[dict]) -> bool:
    flags = {r["mock"] for r in runs}
    if len(flags) != 1:
        raise SystemExit(f"stop: mixed {S.K_MOCK} flags under one root: {sorted(map(str, flags))}")
    return flags.pop()


def check_out_side(out: Path, mock: bool) -> None:
    """Why: mock output must never land in results/real/, nor real output in results/mock/."""
    wrong = "real" if mock else "mock"
    if (PROJECT / "results" / wrong).resolve() in (out.resolve(), *out.resolve().parents):
        raise SystemExit(f"stop: {S.COL_MOCK}={int(mock)} output may not go under results/{wrong}/")


def select_cells(runs: list[dict], seeds: tuple[int, ...] = S.SEEDS) -> dict:
    """Cell check: one complete run per cell. A duplicate keeps the latest complete run.
    seeds: the expected seed set. Default 1-10 (G1); defense v2 passes 11-30 (D-030)."""
    by_cell: dict[tuple, list[dict]] = defaultdict(list)
    ignored = []
    for r in runs:
        if r["d"] in S.DETRACTOR_COUNTS and r["defense"] in S.DEFENSES and r["seed"] in seeds:
            by_cell[(r["d"], r["defense"], r["seed"])].append(r)
        else:
            ignored.append(r["runid"])
    chosen, duplicates, incomplete = {}, [], []
    for key, rs in by_cell.items():
        done = sorted((r for r in rs if r["complete"] is True),
                      key=lambda r: r["runid"].removeprefix(S.MOCK_PREFIX))  # stamp first
        incomplete += [r["runid"] for r in rs if r["complete"] is not True]
        if done:
            chosen[key] = done[-1]
            duplicates += [r["runid"] for r in done[:-1]]
    expected = [(d, f, s) for d in S.DETRACTOR_COUNTS for f in S.DEFENSES for s in seeds]
    return {"chosen": chosen, "expected": expected,
            "missing": [k for k in expected if k not in chosen],
            "duplicates": duplicates, "incomplete": incomplete, "ignored": ignored}


def food_by_cell(chosen: dict) -> dict[tuple[int, int], dict[int, float]]:
    food: dict = defaultdict(dict)
    for (d, defense, seed), r in chosen.items():
        food[(d, defense)][seed] = r["food"]
    return food


def _num(v: float) -> str:
    return "n/a" if isinstance(v, float) and math.isnan(v) else f"{v:.2f}"


def log_lines(root: Path, mock: bool, n_runs: int, cells: dict, rows: list[G2Row]) -> list[str]:
    lines = [f"ANALYZE root={root} runs={n_runs} {S.COL_MOCK}={int(mock)}",
             f"CELLS expected={len(cells['expected'])} present={len(cells['chosen'])} "
             f"missing={len(cells['missing'])} duplicates={len(cells['duplicates'])} "
             f"incomplete={len(cells['incomplete'])} ignored={len(cells['ignored'])}"]
    lines += [f"MISSING d={d} defense={f} seed={s}" for d, f, s in cells["missing"]]
    lines += [f"DUPLICATE {x}" for x in cells["duplicates"]]
    lines += [f"INCOMPLETE {x}" for x in cells["incomplete"]]
    lines += [f"IGNORED {x}" for x in cells["ignored"]]
    for r in rows:
        if r.d == 0:
            lines.append(f"DEFENSE_COST d=0 n_seeds={r.n_seeds} F_off={_num(r.f_off)} "
                         f"F_on={_num(r.f_on)} F_on_minus_F_off={_num(r.gain)} "
                         f"[{_num(r.gain_lo)}, {_num(r.gain_hi)}]")
        else:
            lines.append(f"G2 d={r.d} n_seeds={r.n_seeds} L={_num(r.loss)} "
                         f"[{_num(r.loss_lo)}, {_num(r.loss_hi)}] G={_num(r.gain)} "
                         f"[{_num(r.gain_lo)}, {_num(r.gain_hi)}] R={_num(r.share)} "
                         f"[{_num(r.share_lo)}, {_num(r.share_hi)}] {r.note}".rstrip())
    return lines


# ---- I/O edge --------------------------------------------------------------------

def load_runs(root: Path) -> list[dict]:
    runs = []
    for path in sorted(root.glob(f"*/{S.MANIFEST_FILE}")):
        try:
            m = json.loads(path.read_text())
            prm, met = m[S.K_PARAMS], m[S.K_METRICS]
            runs.append({"runid": m[S.K_RUNID], "mock": m[S.K_MOCK], "d": prm[S.P_NDET],
                         "defense": prm[S.P_DEFENSE], "seed": prm[S.P_SEED],
                         "food": met[S.M_FOOD], "wasted": met[S.M_WASTED],
                         "complete": met[S.M_COMPLETE]})
        except (json.JSONDecodeError, KeyError, TypeError) as err:
            raise SystemExit(f"stop: cannot read manifest {path}: {err!r}")
    return runs


def write_summary(path: Path, runs: list[dict]) -> None:
    with path.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(SUMMARY_COLUMNS)
        for r in sorted(runs, key=lambda r: r["runid"]):
            w.writerow([r["runid"], int(r["mock"]), r["d"], r["defense"], r["seed"],
                        r["food"], r["wasted"], r["complete"]])


def write_stats(path: Path, rows: list[G2Row]) -> None:
    names = [f.name for f in dataclasses.fields(G2Row)]
    with path.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(names)
        for r in rows:
            w.writerow([getattr(r, n) for n in names])


def draw_chart(path: Path, rows: list[G2Row], mock: bool) -> None:
    shown = [r for r in rows if r.d > 0]
    fig, ax = plt.subplots(figsize=(6.5, 4.4), layout="constrained")
    labeled = False
    for x, r in enumerate(shown):
        if r.resolved:
            ax.bar(x, r.share, color=CHART_BAR, width=0.5, capsize=6,
                   yerr=[[r.share - r.share_lo], [r.share_hi - r.share]],
                   label=None if labeled else "recovered loss share R(d), whisker = 95 % interval")
            labeled = True
        else:  # DESIGN 4.2: no R(d) when the loss may be 0
            text = "no data" if r.n_seeds == 0 else "loss not resolved"
            ax.text(x, 0.05, text, ha="center", va="bottom")
    ax.axhline(1.0, color="0.5", linestyle="--", label="full recovery (R = 1)")
    ax.axhline(0.0, color="0.7", linewidth=0.8)
    ok = [r for r in shown if r.resolved]
    ax.set_ylim(min([0.0] + [r.share_lo for r in ok]) - 0.1,
                max([1.0] + [r.share_hi for r in ok]) + 0.1)
    ax.set_xticks(range(len(shown)), [f"d = {r.d}" for r in shown])
    ax.set_xlabel("detractors added to the 20 honest robots (d)")
    ax.set_ylabel("recovered loss share R(d)")
    n_seeds = max([r.n_seeds for r in shown] + [0])
    title = f"G2 recovered loss share, {n_seeds} seeds"
    ax.set_title(f"MOCK DATA: {title}" if mock else title)
    # Legend below the axes: the title above stays readable (rules/figures.md, no overlap).
    fig.legend(loc="outside lower center", ncol=1)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", type=Path)
    ap.add_argument("--out", type=Path, help="default: results/mock or results/real by the flag")
    ap.add_argument("--seeds", type=parse_seeds, default=S.SEEDS, metavar="a-b",
                    help="expected seed range, default 1-10. Defense v2 confirmation: 11-30")
    args = ap.parse_args(argv)
    if not args.root.is_dir():
        raise SystemExit(f"stop: {args.root} is not a folder")
    runs = load_runs(args.root)
    if not runs:
        raise SystemExit(f"stop: no run manifest under {args.root}")
    mock = single_mock_flag(runs)  # mixing guard: stops before anything is written
    out = args.out or PROJECT / "results" / ("mock" if mock else "real")
    check_out_side(out, mock)
    out.mkdir(parents=True, exist_ok=True)
    cells = select_cells(runs, args.seeds)
    rows = g2_rows(food_by_cell(cells["chosen"]), S.DETRACTOR_COUNTS)
    write_summary(out / SUMMARY_FILE, runs)
    write_stats(out / STATS_FILE, rows)
    chart = out / ("g2_recovered_share_MOCK.png" if mock else "g2_recovered_share.png")
    draw_chart(chart, rows, mock)
    extra = write_cell_outputs(out, args.root, cells["chosen"], mock) if cells["chosen"] else []
    lines = log_lines(args.root, mock, len(runs), cells, rows)
    lines += [f"NOTE {note}" for note in NOTES]
    lines.append(f"OUTPUT chart={chart} summary={out / SUMMARY_FILE} stats={out / STATS_FILE}"
                 + "".join(f" {p.name}={p}" for p in extra))
    (out / LOG_FILE).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
