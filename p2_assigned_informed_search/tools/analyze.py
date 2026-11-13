"""Paired analysis of one evaluation set (DESIGN 6.2 items 3 to 8, 6.7; D-011, D-015, D-016).

Usage: analyze.py --set S3 --criteria prereg/S3_eval_MOCK.json results/mock/runs.csv
       analyze.py --selfcheck [--criteria FILE]
Writes to <runs.csv folder>/<set>/: improvement.csv, verdict.json, analyze_log.txt, 3 figures.
Mock input gives the suffix _MOCK on every file name and "MOCK DATA" in every title.
Everything that decides a verdict lives in this file, so the recorded sha is the whole rule.
Resample count, bootstrap seed, level and verdict rules come from the criteria file only.
Statistics are numpy only (D-011). Wilcoxon p, Holm p and medians never enter the verdict.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

import analyze_figures
import schema as S

__all__ = ["decide", "bootstrap_interval", "wilcoxon", "holm"]

PROJECT = Path(__file__).resolve().parent.parent
DEFAULT_CRITERIA = PROJECT / "prereg" / "S3_eval_MOCK.json"   # used by --selfcheck only
MOCK_SUFFIX = "_MOCK"
RULE_PATTERN = re.compile(r"^(ci_low|ci_high) (>|<) (-?\d+(?:\.\d+)?)$")
OTHERWISE = "otherwise"
SIGMA_DIFF_FACTORS = {"sqrt(2) * sigma": math.sqrt(2)}   # the only stand-in text accepted
SHARE_BRANCHES = tuple(dict.fromkeys(S.SHARE_COLUMN_OF_BRANCH.values()))
# The criteria file reuses the run-column names `set` and `mock` as its own keys (S.C.set).
CRIT_SET, CRIT_MOCK = S.C.set, S.C.mock
OUT_COLUMNS = (
    S.C.distribution, "n_pairs", "mean_control", "mean_treatment", "median_control",
    "median_treatment", "improvement_pct", "ci_low", "ci_high", "verdict", "wilcoxon_p",
    "holm_p", "diff_mean", "diff_ci_low", "diff_ci_high", "sigma_s1", "detectable_diff",
    "detectable_pct",
)


@dataclass
class Comparison:
    distribution: str
    seeds: list[int]
    control: np.ndarray
    treatment: np.ndarray
    stats: dict[str, Any]
    verdict: str


# ---- pure statistics -------------------------------------------------------------

def decide(ci_low: float, ci_high: float, rules: dict[str, str]) -> str:
    """Verdict word from the interval by the criteria rule texts. Unknown text raises."""
    fallback = [w for w, text in rules.items() if text == OTHERWISE]
    if len(fallback) != 1:
        raise ValueError(f"verdict rules need exactly one '{OTHERWISE}' entry: {rules}")
    bounds = {"ci_low": ci_low, "ci_high": ci_high}
    for word, text in rules.items():
        if text == OTHERWISE:
            continue
        m = RULE_PATTERN.match(text)
        if m is None:
            raise ValueError(f"unknown verdict rule text for '{word}': {text!r}")
        value, op, bound = bounds[m[1]], m[2], float(m[3])
        if (value > bound) if op == ">" else (value < bound):
            return word
    return fallback[0]


def improvement(control: np.ndarray, treatment: np.ndarray) -> float:
    """100 * (mean_treatment - mean_control) / mean_control, a ratio of means."""
    return float(100.0 * (treatment.mean() - control.mean()) / control.mean())


def bootstrap_interval(control: np.ndarray, treatment: np.ndarray, n_resamples: int,
                       seed: int, level: float) -> tuple[float, float, float, float]:
    """Paired percentile interval of the improvement and of the mean difference.

    One index matrix serves both arms (resample unit = seed index). A fresh generator per call
    keeps one distribution's interval independent of which others exist.
    """
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(control), size=(n_resamples, len(control)))
    mean_c, mean_t = control[idx].mean(axis=1), treatment[idx].mean(axis=1)
    pct = [100 * (1 - level) / 2, 100 * (1 - (1 - level) / 2)]
    imp_lo, imp_hi = np.percentile(100.0 * (mean_t - mean_c) / mean_c, pct)
    diff_lo, diff_hi = np.percentile(mean_t - mean_c, pct)
    return float(imp_lo), float(imp_hi), float(diff_lo), float(diff_hi)


def wilcoxon(diff: np.ndarray) -> tuple[float, int, float, float]:
    """Two-sided signed-rank test, normal approximation, tie correction, no continuity term.

    Returns (W+, n nonzero, z, p). Zero differences are dropped. Ties get average ranks.
    """
    d = diff[diff != 0]
    n = len(d)
    if n == 0:
        return 0.0, 0, 0.0, 1.0
    _, inverse, counts = np.unique(np.abs(d), return_inverse=True, return_counts=True)
    avg_rank = np.cumsum(counts) - (counts - 1) / 2.0
    w_plus = float(avg_rank[inverse][d > 0].sum())
    var = n * (n + 1) * (2 * n + 1) / 24.0 - float((counts**3 - counts).sum()) / 48.0
    if var <= 0:
        return w_plus, n, 0.0, 1.0
    z = (w_plus - n * (n + 1) / 4.0) / math.sqrt(var)
    return w_plus, n, z, math.erfc(abs(z) / math.sqrt(2))


def holm(p_values: list[float]) -> list[float]:
    """Holm step-down adjusted p, in the input order."""
    m = len(p_values)
    adjusted, running = [0.0] * m, 0.0
    for rank, i in enumerate(sorted(range(m), key=p_values.__getitem__)):
        running = max(running, min(1.0, (m - rank) * p_values[i]))
        adjusted[i] = running
    return adjusted


# ---- selfcheck -------------------------------------------------------------------

def selfcheck(crit: dict) -> list[str]:
    """Failure lines. Empty list = pass.

    Hand-worked Wilcoxon example (done on paper, not taken from the function):
      d = [2, -1, 2, 3, -3, 4, 5, 5], no zero, n = 8
      |d| sorted 1 | 2 2 | 3 3 | 4 | 5 5  ->  ranks 1 | 2.5 2.5 | 4.5 4.5 | 6 | 7.5 7.5
      positive: 2, 2, 3, 4, 5, 5 -> W+ = 2.5 + 2.5 + 4.5 + 6 + 7.5 + 7.5 = 30.5
      (negative: 1, 3 -> W- = 1 + 4.5 = 5.5; W+ + W- = 36 = 8 * 9 / 2)
      mean = 8 * 9 / 4 = 18
      var  = 8 * 9 * 17 / 24 - 3 * (2^3 - 2) / 48 = 51 - 0.375 = 50.625
      z    = (30.5 - 18) / sqrt(50.625) = 12.5 / 7.11513 = 1.7568
      p    = 2 * (1 - Phi(1.7568)) = 0.0789 (normal table: Phi(1.75) = 0.95994, Phi(1.76) = 0.96080)
    Holm example: p = [0.01, 0.04, 0.03], m = 3 -> sorted .01 .03 .04
      3 * .01 = .03 | max(.03, 2 * .03 = .06) = .06 | max(.06, 1 * .04) = .06
      so adjusted = [0.03, 0.06, 0.06] in input order.
    """
    bad: list[str] = []
    w_plus, n, z, p = wilcoxon(np.array([2, -1, 2, 3, -3, 4, 5, 5], dtype=float))
    if not (w_plus == 30.5 and n == 8 and abs(z - 1.7568) < 5e-4 and abs(p - 0.0789) < 5e-4):
        bad.append(f"wilcoxon: got W+={w_plus} n={n} z={z:.4f} p={p:.4f}, hand value 30.5 8 1.7568 0.0789")
    if not np.allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06]):
        bad.append(f"holm: got {holm([0.01, 0.04, 0.03])}, hand value [0.03, 0.06, 0.06]")
    rule = crit["decision_rule"]
    args = (rule["n_resamples"], rule["bootstrap_seed"], rule["interval_level"])
    base = 100.0 + 5.0 * np.arange(20)
    # q = 1.2 c gives improvement 20 in every resample, so the interval is [20, 20].
    cases = [("improves", 1.2 * base, 20.0), ("worse", 0.8 * base, -20.0),
             ("not resolved", np.tile([110.0, 90.0], 10), 0.0)]
    for word, treatment, point in cases:
        control = base if word != "not resolved" else np.full(20, 100.0)
        lo, hi, _, _ = bootstrap_interval(control, treatment, *args)
        got = decide(lo, hi, crit["verdict"])
        if got != word or abs(improvement(control, treatment) - point) > 1e-9:
            bad.append(f"bootstrap case '{word}': verdict {got}, interval [{lo:.2f}, {hi:.2f}]")
    return bad


# ---- load and pair ---------------------------------------------------------------

def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_runs(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def pick_cells(rows: list[dict[str, str]], crit: dict, set_name: str
               ) -> tuple[dict[tuple[str, str, int], dict[str, str]], list[str]]:
    """Complete runs of the set by (arm, distribution, seed). A later duplicate wins (6.6 item 4)."""
    cells: dict[tuple[str, str, int], dict[str, str]] = {}
    notes: list[str] = []
    for r in sorted((r for r in rows if r[S.C.set] == set_name), key=lambda r: r[S.C.run_id]):
        if r[S.C.complete] != "1":
            notes.append(f"NOTE incomplete run ignored: {r[S.C.run_id]}")
            continue
        key = (r[S.C.arm], r[S.C.distribution], int(r[S.C.seed]))
        if key in cells:
            notes.append(f"NOTE duplicate cell {key}: {cells[key][S.C.run_id]} replaced by {r[S.C.run_id]}")
        cells[key] = r
    return cells, notes


def missing_cells(cells: dict, crit: dict) -> list[str]:
    con = crit["primary_contrast"]
    seeds = range(con["seeds"]["first"], con["seeds"]["last"] + 1)
    return [f"MISSING cell arm={a} distribution={d} seed={s}"
            for d in con["distributions"] for a in (con["control_arm"], con["treatment_arm"])
            for s in seeds if (a, d, s) not in cells]


def sigma_line(rows: list[dict[str, str]], crit: dict, distribution: str, n_pairs: int,
               mean_control: float) -> dict[str, float | None]:
    """sigma of the S1 control arm, and the detectable paired difference (6.2 item 8)."""
    src, noise = crit["noise_line"]["sigma_source"], crit["noise_line"]
    values = [float(r[src["column"]]) for r in rows
              if r[S.C.set] == src[CRIT_SET] and r[S.C.arm] == src[S.C.arm]
              and r[S.C.distribution] == distribution and r[S.C.complete] == "1"]
    if len(values) < 2:
        return {"sigma_s1": None, "detectable_diff": None, "detectable_pct": None}
    sigma = float(np.std(values, ddof=1))
    sigma_diff = SIGMA_DIFF_FACTORS[noise["sigma_diff_stand_in"]] * sigma
    detectable = noise["multiplier"] * sigma_diff / math.sqrt(n_pairs)
    return {"sigma_s1": sigma, "detectable_diff": detectable,
            "detectable_pct": 100.0 * detectable / mean_control}


def compare(rows: list[dict[str, str]], cells: dict, crit: dict, distribution: str
            ) -> Comparison | None:
    con, rule = crit["primary_contrast"], crit["decision_rule"]
    metric = crit["primary_metric"]["column"]
    seeds = sorted(s for (a, d, s) in cells if a == con["control_arm"] and d == distribution
                   and (con["treatment_arm"], d, s) in cells)
    if len(seeds) < 2:
        return None
    control = np.array([float(cells[(con["control_arm"], distribution, s)][metric]) for s in seeds])
    treatment = np.array([float(cells[(con["treatment_arm"], distribution, s)][metric]) for s in seeds])
    lo, hi, d_lo, d_hi = bootstrap_interval(control, treatment, rule["n_resamples"],
                                            rule["bootstrap_seed"], rule["interval_level"])
    _, _, z, p = wilcoxon(treatment - control)
    stats = {
        "n_pairs": len(seeds), "mean_control": float(control.mean()),
        "mean_treatment": float(treatment.mean()), "median_control": float(np.median(control)),
        "median_treatment": float(np.median(treatment)),
        "improvement_pct": improvement(control, treatment), "ci_low": lo, "ci_high": hi,
        "diff_mean": float((treatment - control).mean()), "diff_ci_low": d_lo, "diff_ci_high": d_hi,
        "wilcoxon_z": z, "wilcoxon_p": p,
        **sigma_line(rows, crit, distribution, len(seeds), float(control.mean())),
    }
    return Comparison(distribution, seeds, control, treatment, stats,
                      decide(lo, hi, crit["verdict"]))


def branch_shares(cells: dict, crit: dict) -> dict[tuple[str, str], dict[str, float]]:
    """Mean share per branch for (arm, distribution). Empty cells are skipped (D-016)."""
    con = crit["primary_contrast"]
    out: dict[tuple[str, str], dict[str, float]] = {}
    for arm in (con["control_arm"], con["treatment_arm"]):
        for d in con["distributions"]:
            runs = [r for (a, dist, _), r in cells.items() if a == arm and dist == d]
            means = {b: [float(r[b]) for r in runs if r[b] != ""] for b in SHARE_BRANCHES}
            if all(means.values()):
                out[(arm, d)] = {b.removeprefix("share_"): float(np.mean(v)) for b, v in means.items()}
    return out


# ---- outputs ---------------------------------------------------------------------

def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT))
    except ValueError:
        return str(path.resolve())


def write_outputs(results: list[Comparison], crit: dict, criteria: Path, runs_csv: Path,
                  out: Path, suffix: str, is_mock: bool) -> None:
    con = crit["primary_contrast"]
    csv_rows = []
    for c in results:
        csv_rows.append({S.C.distribution: c.distribution, "verdict": c.verdict,
                         **{k: c.stats[k] for k in OUT_COLUMNS if k in c.stats}})
    with (out / f"improvement{suffix}.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(csv_rows)
    refs = {"criteria_file": rel(criteria), "criteria_sha256": sha256_of(criteria),
            "code_file": rel(Path(__file__)), "code_sha256": sha256_of(Path(__file__))}
    comparisons = [{
        S.C.distribution: c.distribution, "treatment_arm": con["treatment_arm"],
        "control_arm": con["control_arm"], "n_pairs": len(c.seeds), "seeds": c.seeds,
        "paired_differences": (c.treatment - c.control).tolist(), "statistics": c.stats,
        "verdict": c.verdict, **refs} for c in results]
    verdict = {
        "title": ("MOCK DATA. " if is_mock else "") + f"Verdicts of set {crit[CRIT_SET]}",
        CRIT_MOCK: int(is_mock), CRIT_SET: crit[CRIT_SET], "runs_csv": rel(runs_csv),
        "runs_csv_sha256": sha256_of(runs_csv), **refs,
        "multiplicity_line": crit["multiplicity"]["report_line"], "comparisons": comparisons}
    (out / f"verdict{suffix}.json").write_text(json.dumps(verdict, indent=2) + "\n")


def run_analysis(args: argparse.Namespace) -> int:
    crit = json.loads(args.criteria.read_text())
    if args.set != crit[CRIT_SET]:
        print(f"refused: --set {args.set} differs from the criteria file set {crit[CRIT_SET]}")
        return 1
    if crit["improvement"]["kind"] != "ratio_of_means":
        print(f"refused: unknown improvement kind {crit['improvement']['kind']!r}")
        return 1
    rows = read_runs(args.runs_csv)
    kinds = {r[S.C.mock] for r in rows}
    if len(kinds) != 1:
        print(f"refused: mock column holds {sorted(kinds) or 'no rows'}, one value is required")
        return 1
    is_mock = kinds == {"1"}
    if is_mock != bool(crit[CRIT_MOCK]):
        print(f"refused: runs.csv mock={int(is_mock)} but the criteria file mock={crit[CRIT_MOCK]}")
        return 1
    suffix = MOCK_SUFFIX if is_mock else ""
    out = args.runs_csv.parent / args.set
    out.mkdir(parents=True, exist_ok=True)
    cells, lines = pick_cells(rows, crit, args.set)
    lines += missing_cells(cells, crit)
    results = [c for d in crit["primary_contrast"]["distributions"]
               if (c := compare(rows, cells, crit, d)) is not None]
    if not results:
        print("\n".join(lines + ["refused: no distribution has 2 pairs"]))
        return 1
    for c, adj in zip(results, holm([c.stats["wilcoxon_p"] for c in results])):
        c.stats["holm_p"] = adj
    write_outputs(results, crit, args.criteria, args.runs_csv, out, suffix, is_mock)
    analyze_figures.draw_all(results, branch_shares(cells, crit), crit["primary_contrast"],
                             out, suffix, is_mock)
    lines += [f"{c.distribution}: {c.verdict}, improvement {c.stats['improvement_pct']:+.2f} % "
              f"[{c.stats['ci_low']:+.2f}, {c.stats['ci_high']:+.2f}], pairs {len(c.seeds)}"
              for c in results]
    lines.append(f"SUMMARY set={args.set} distributions={len(results)} "
                 f"missing={sum(x.startswith('MISSING') for x in lines)} out={rel(out)}")
    print("\n".join(lines))
    (out / f"analyze_log{suffix}.txt").write_text("\n".join(lines) + "\n")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("runs_csv", type=Path, nargs="?")
    ap.add_argument("--set")
    ap.add_argument("--criteria", type=Path)
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args(argv)
    if args.selfcheck:
        bad = selfcheck(json.loads((args.criteria or DEFAULT_CRITERIA).read_text()))
        print("\n".join(f"FAIL {line}" for line in bad) or "selfcheck passed")
        return 1 if bad else 0
    if not (args.runs_csv and args.set and args.criteria):
        ap.error("runs_csv, --set and --criteria are required without --selfcheck")
    if not args.runs_csv.is_file() or not args.criteria.is_file():
        print("refused: runs_csv or criteria file is not a file")
        return 1
    return run_analysis(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
