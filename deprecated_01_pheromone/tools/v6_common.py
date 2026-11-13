"""Shared constants and readers of the M6 ID arm (D-040, D-043, D-048, DESIGN_M6.md, prereg/defense_id_arm.md).

One place for the arms, seed blocks, roots, the margin, the prereg values and the manifest reader,
so the run tool, the arm table and the judge cannot disagree. Reads manifests only.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

import schema as S
from make_sweep import build_argos, git_stamp
from run_argos import run_argos_files
from run_results import PROJECT, load_manifests, require_committed, run_food
from sweep_params import manifest_key, overrides
from sweep_plan import frozen_values, move_incomplete_runs, same_code

__all__ = ["Arm", "ARMS", "ARM_ORDER", "SMOKE_SEEDS", "CHECK_SEEDS", "CONFIRM_SEEDS", "DS", "PREREG", "MARGIN_CSV",
           "RUNS", "RESULTS", "VERDICT", "SMOKE_ROOT", "CHECK_ROOT", "CONFIRM_ROOT", "INVARIANCE_ROOT",
           "read_margin", "prereg_values", "require_prereg", "plan_runs_v6", "read_arm_runs", "arm_root"]


@dataclass(frozen=True)
class Arm:
    mode: str      # <pheromone defense_mode>
    defense: int   # <pheromone defense>: 0 only for off (DESIGN_M6 Table 5)
    k: int         # controller confirm_k (inert for off and id)
    t_lock: int    # controller t_lock seconds (inert for off and id)


# v5 = the M5 primary arm (k2, t10), PREREG of defense v5. A different M5 freeze needs a product-manager D-row.
ARMS: dict[str, Arm] = {"off": Arm("off", 0, 1, 0), "v3": Arm("v3", 1, 1, 0),
                        "k1t10": Arm("v5", 1, 1, 10),  # mode v5 runs the controller rule with these k, t_lock. D-052: best no-ID arm by the D-050 rule
                        "v5": Arm("v5", 1, 2, 10), "id": Arm("id", 1, 1, 0)}
ARM_ORDER = tuple(ARMS)
SMOKE_SEEDS = (900,)                              # D-048 D6: a throwaway block outside D-043
CHECK_SEEDS = tuple(range(301, 311))              # D-043, arm check
CONFIRM_SEEDS = tuple(range(321, 361))            # D-043, used once
DS = S.DETRACTOR_COUNTS
RUNS = PROJECT / "runs"
SMOKE_ROOT, CHECK_ROOT = RUNS / "m6_smoke", RUNS / "m6_check"
CONFIRM_ROOT, INVARIANCE_ROOT = RUNS / "m6_confirm", RUNS / "invariance_v6"
PREREG = PROJECT / "prereg" / "defense_id_arm.md"
MARGIN_CSV = PROJECT / "results" / "real" / "m6_margin.csv"
RESULTS = PROJECT / "results" / "real" / "id_arm"
VERDICT = RESULTS / "verdict.json"
FIXED_MARGIN = 1.5                                # D-048 D1 fallback


def arm_root(base: Path, arm: str) -> Path:
    """One run root per arm: the arms share one runid key (DESIGN_M6 section 6)."""
    return base / arm


def read_margin() -> float:
    """The p95 margin of results/real/m6_margin.csv (summary, each, pick), else 1.5 (D-048 D1)."""
    if not MARGIN_CSV.is_file():
        return FIXED_MARGIN
    with MARGIN_CSV.open(newline="") as fh:
        for row in csv.DictReader(fh):
            if (row["scope"], row["variant"], row["proxy"], row["metric"]) == ("summary", "each", "pick", "margin_p95"):
                return float(row["value"])
    raise SystemExit(f"stop: {MARGIN_CSV.name} has no summary/each/pick/margin_p95 row")


def prereg_values() -> tuple[str, float, float]:
    """(best no-ID arm, margin, eps) written in the prereg. A placeholder stops the caller."""
    text = PREREG.read_text()
    found = {k: re.search(rf"^- {k}: (\S+)", text, re.M) for k in ("Best no-ID arm", "Margin", "Eps")}
    missing = [k for k, m in found.items() if m is None]
    if missing:
        raise SystemExit(f"stop: {PREREG.name} has no line '- {missing[0]}: <value>'")
    best, margin, eps = (found[k].group(1) for k in ("Best no-ID arm", "Margin", "Eps"))  # type: ignore[union-attr]
    if best not in ("off", "v3", "k1t10", "v5"):
        raise SystemExit(f"stop: {PREREG.name} must name the best no-ID arm (off, v3, k1t10 or v5) before any M6 run, got {best}")
    try:
        margin_v, eps_v = float(margin), float(eps)
    except ValueError:
        raise SystemExit(f"stop: {PREREG.name} margin and eps must be numbers, got {margin} and {eps}")
    return best, margin_v, eps_v


def require_prereg() -> tuple[str, float]:
    """The check and confirm stages: prereg committed and unchanged, margin equal to the saved csv."""
    require_committed(PREREG)
    best, margin, _eps = prereg_values()
    if abs(margin - read_margin()) > 1e-9:
        raise SystemExit(f"stop: prereg margin {margin} differs from {MARGIN_CSV.name} ({read_margin()})")
    return best, margin


def expected_params(arm: str, margin: float) -> dict[str, str]:
    """Manifest params an arm run must carry, on top of the frozen ones."""
    a = ARMS[arm]
    out = {"defense_mode": a.mode, manifest_key("confirm_k"): str(a.k), manifest_key("t_lock"): str(a.t_lock),
           manifest_key("enabled"): "false" if a.mode in ("off", "id") else "true"}
    if arm == "id":
        out["id_margin"] = f"{margin:g}"
    return out


def _same(actual: str | None, want: str) -> bool:
    if actual is None:
        return False
    try:
        return float(actual) == float(want)
    except ValueError:
        return actual == want


def is_done(manifests: list[dict], cell: tuple[int, int, int], arm: str, margin: float, commit: str) -> bool:
    """A complete run with this cell, mode, values and code (same rule as sweep_plan.is_done)."""
    want = {**{manifest_key(n): f"{v:g}" for n, v in frozen_values().items()}, **expected_params(arm, margin)}
    for m in manifests:
        p = m[S.K_PARAMS]
        if ((p[S.P_NDET], p[S.P_DEFENSE], p[S.P_SEED]) == cell and m[S.K_METRICS][S.M_COMPLETE] is True
                and same_code(m["git_commit"], commit) and all(_same(p.get(k), v) for k, v in want.items())):
            return True
    return False


def plan_runs_v6(root: Path, jobs: list[tuple[tuple[int, int, int], str]], margin: float, run: bool) -> int:
    """Write a .argos file for each (cell, arm) job with no complete run in root. Run them if asked.

    Own planner: sweep_plan.plan_runs casts every value to float and passes no tags, but the
    mode and the controller enabled flag are strings (DESIGN_M6 section 6).
    """
    move_incomplete_runs(root)
    commit, _ = git_stamp()
    done = load_manifests(root)
    frozen = frozen_values()
    files: list[Path] = []
    for cell, arm in jobs:
        if is_done(done, cell, arm, margin, commit):
            continue
        a = ARMS[arm]
        values: dict[str, float | str] = {**frozen, "confirm_k": a.k, "t_lock": float(a.t_lock)}
        if a.mode == "id":
            values["enabled"] = "false"  # build_argos sets enabled from defense: the id arm needs 1 and false
        tags = {"defense_mode": a.mode, **({"id_margin": f"{margin:g}"} if arm == "id" else {})}
        runid, path = build_argos(*cell, root, overrides(**values), tags)
        files.append(path)
        print(f"{arm} d={cell[0]} defense={cell[1]} seed={cell[2]}: {runid}")
    print(f"{len(jobs) - len(files)} of {len(jobs)} jobs already complete, {len(files)} to run")
    if run:
        run_argos_files(files)
    return 0


def read_arm_runs(root: Path, arm: str, margin: float) -> dict[tuple[int, int], tuple[int, Path]]:
    """(d, seed) -> (food, run folder) of one arm root. Stops on a wrong mode, value, code or a repeat."""
    a, out = ARMS[arm], {}
    want = expected_params(arm, margin)
    for m in load_manifests(root):
        p, rid = m[S.K_PARAMS], m[S.K_RUNID]
        bad = [k for k, v in want.items() if not _same(p.get(k), v)]
        if bad or int(p[S.P_DEFENSE]) != a.defense or m["code_version"] != "v6":
            raise SystemExit(f"stop: run {rid} under {root.name} does not match arm {arm} (params {bad}, code {m['code_version']})")
        key = (int(p[S.P_NDET]), int(p[S.P_SEED]))
        if key in out:
            raise SystemExit(f"stop: {key} appears twice under {root}")
        out[key] = (run_food(m), root / rid)
    return out
