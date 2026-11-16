"""Plan real runs: write runs/<set>/<runid>/run.argos for a list of arms (M2-04, DESIGN 6.1, 6.4).

Usage:
  make_runs.py --set S1 --arm cpfa --seeds 1001-1030
  make_runs.py --set S0det --arm vendor --dist random --seeds 3001 --repeat 2
  make_runs.py --set <set> --arm cpfa,qmap-ideaa,qmap-ideab --seeds 1011-1020 \
      --arm-params qmap-ideaa=prereg/params_ideaa.json --arm-params qmap-ideab=prereg/params_ideab.json
A grid file (--grid) is {"factors": {attribute: [level, ...]}}. Every combination of levels becomes
one arm `qmap-g<NN>` with those attributes (D-029). The control arm `cpfa` is added once, shared.
One call plans a whole batch: every listed arm gets the same (distribution, seed) cells, so one
shared control arm (`cpfa`) pairs with every idea arm by seed (D-022).
An arm-params file is a JSON object {attribute: value}. Each pair goes verbatim onto the <CPFA>
node of that arm's run.argos. The switch is set by the arm name, never by the file.
Why this tool does not write manifest.json: run_argos.py is its only writer (M2-05).
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

import schema as S

__all__ = ["PROJECT", "PARAM_SET", "build_argos", "parse_seeds", "plan_cells", "load_arm_params",
           "expand_grid"]

PROJECT = Path(__file__).resolve().parent.parent
TEMPLATE = PROJECT / "src" / "experiments" / "Random_CPFA_r24_tag256_10by10.xml"
PARAM_SET = "xml10"                       # the one CPFA parameter set (D-008)
SWITCH = "InformedSearch"                 # <CPFA> attribute of DESIGN 4.1
BUILD_DIR = {S.ARMS[0]: "build_baseline"}  # vendor arm. Every other arm runs our build.
OUR_BUILD_DIR = "build_ours"
LIB_CONTROLLER = "source/CPFA/libCPFA_controller"
LIB_LOOP = "source/CPFA/libCPFA_loop_functions"
NEST_RADIUS_XML = 0.25                    # D-006 primary reading (effective 0.456 m)
NEST_RADIUS_XML_S4 = 0.137                # D-006 sensitivity reading (effective 0.25 m)
EVAL_SETS = (*S.LAYOUT_SETS, "S5")        # sets that own the evaluation seed block (DESIGN 6.1)
EVAL_SEEDS = S.SET_CELLS[S.LAYOUT_SETS[0]][1]
REFUSED_SEEDS = (0, 1)                    # clock seed and smoke seed (DESIGN 6.1)
REPEAT_SET = "S0det"                      # the only set that repeats a cell on purpose
ARM_NAME = re.compile(rf"^{re.escape(S.ABLATION_ARM_PREFIX)}[a-z0-9-]+$")


# ---- pure ------------------------------------------------------------------------

def parse_seeds(text: str) -> list[int]:
    """'1001-1030' or '1001,1005,1010-1012' to a sorted list without duplicates."""
    seeds: set[int] = set()
    for part in text.split(","):
        lo, _, hi = part.strip().partition("-")
        seeds.update(range(int(lo), int(hi or lo) + 1))
    return sorted(seeds)


def check_arm(arm: str) -> None:
    if arm not in S.ARMS and not ARM_NAME.match(arm):
        raise ValueError(f"arm {arm!r} is not one of {S.ARMS} or {S.ABLATION_ARM_PREFIX}<id> "
                         f"(id: lowercase letters, digits, hyphen)")


def is_informed(arm: str) -> bool:
    return arm.startswith(S.ARMS[2])      # qmap and qmap-<id>


def check_seeds(set_name: str, seeds: list[int]) -> None:
    bad = [s for s in seeds if s in REFUSED_SEEDS]
    if bad:
        raise ValueError(f"seeds {bad} are refused (0 is the clock seed, 1 is the smoke seed)")
    inside = [s for s in seeds if s in EVAL_SEEDS]
    if set_name in EVAL_SETS and len(inside) != len(seeds):
        raise ValueError(f"set {set_name} runs only evaluation seeds {EVAL_SEEDS.start} to "
                         f"{EVAL_SEEDS.stop - 1}, got {[s for s in seeds if s not in EVAL_SEEDS]}")
    if set_name not in EVAL_SETS and inside:
        raise ValueError(f"seeds {inside} belong to the evaluation block "
                         f"({EVAL_SEEDS.start} to {EVAL_SEEDS.stop - 1}). Set {set_name} may not use them")


def plan_cells(set_name: str, arms: list[str], dists: list[str], seeds: list[int],
               repeat: int, arm_params: dict[str, dict[str, str]]) -> list[tuple[str, str, int]]:
    """(arm, distribution, seed) per run, validated. Raises ValueError with the cause."""
    if set_name not in S.SETS:
        raise ValueError(f"set {set_name!r} is not one of {S.SETS}")
    for arm in arms:
        check_arm(arm)
    if len(set(arms)) != len(arms):
        raise ValueError("an arm is listed twice")
    for arm in arm_params:
        if arm not in arms:
            raise ValueError(f"--arm-params names arm {arm!r}, which is not in --arm")
        if arm == S.ARMS[0]:
            raise ValueError("the vendor arm carries no attribute our build adds (DESIGN 10)")
    bad = [d for d in dists if d not in S.DISTRIBUTIONS]
    if bad:
        raise ValueError(f"distribution {bad} is not one of {S.DISTRIBUTIONS}")
    if repeat != 1 and set_name != REPEAT_SET:
        raise ValueError(f"--repeat is for set {REPEAT_SET} only")
    check_seeds(set_name, seeds)
    return [(a, d, s) for a in arms for d in dists for s in seeds for _ in range(repeat)]


def load_arm_params(path: Path) -> dict[str, str]:
    """A JSON object of scalars as XML attribute strings. The switch is not settable here."""
    raw = json.loads(path.read_text())
    if not isinstance(raw, dict) or not all(isinstance(v, (str, int, float)) for v in raw.values()):
        raise ValueError(f"{path}: must be a JSON object of attribute to string or number")
    if SWITCH in raw:
        raise ValueError(f"{path}: {SWITCH} is set by the arm name, remove it")
    return {k: str(v) for k, v in raw.items()}


def expand_grid(path: Path) -> dict[str, dict[str, str]]:
    """arm -> attributes for every level combination of the grid file (D-029)."""
    raw = json.loads(path.read_text())
    factors = raw.get("factors") if isinstance(raw, dict) else None
    if not isinstance(factors, dict) or not factors or not all(
            isinstance(v, list) and v and all(isinstance(x, (str, int, float)) for x in v)
            for v in factors.values()):
        raise ValueError(f'{path}: needs {{"factors": {{attribute: [level, ...]}}}}')
    if SWITCH in factors:
        raise ValueError(f"{path}: {SWITCH} is set by the arm name, remove it")
    names = list(factors)
    combos = itertools.product(*(factors[n] for n in names))
    return {f"{S.ABLATION_ARM_PREFIX}g{i:02d}": {n: str(v) for n, v in zip(names, combo)}
            for i, combo in enumerate(combos, 1)}


def build_argos(template: str, arm: str, distribution: str, seed: int, set_name: str,
                extra: dict[str, str]) -> str:
    """The run.argos text. Library paths are absolute (the run folder is the working directory)."""
    root = ET.fromstring(template)
    build = PROJECT / BUILD_DIR.get(arm, OUR_BUILD_DIR)
    exp = root.find("framework/experiment")
    exp.set("random_seed", str(seed))
    exp.set("length", "0")                      # the loop functions end the run at MaxSimTimeInSeconds
    root.find("controllers/CPFA_controller").set("library", str(build / LIB_CONTROLLER))
    lf = root.find("loop_functions")
    lf.set("library", str(build / LIB_LOOP))
    settings = lf.find("settings")
    settings.set("FoodDistribution", str(S.DISTRIBUTION_CODES[distribution]))
    settings.set("MaxSimTimeInSeconds", str(S.SIM_SECONDS))
    settings.set("NestRadius", str(NEST_RADIUS_XML_S4 if set_name == "S4" else NEST_RADIUS_XML))
    if arm != S.ARMS[0]:
        cpfa = lf.find("CPFA")
        cpfa.set(SWITCH, "1" if is_informed(arm) else "0")
        for name, value in extra.items():
            cpfa.set(name, value)
    ET.indent(root)
    return ET.tostring(root, encoding="unicode", xml_declaration=True) + "\n"


# ---- I/O edge --------------------------------------------------------------------

def existing_cells(folder: Path) -> set[tuple[str, str, int]]:
    cells = set()
    for child in folder.iterdir() if folder.is_dir() else []:
        parsed = S.parse_runid(child.name)
        if parsed:
            cells.add(parsed[2:])
    return cells


def fresh_runid(folder: Path, arm: str, distribution: str, seed: int) -> str:
    """Two runs of one cell in one second (--repeat) must not share a folder: bump the stamp."""
    stamp = datetime.now()
    while True:
        runid = f"{stamp:%Y%m%d-%H%M%S}_{arm}_{distribution}_s{seed}"
        if not (folder / runid).exists():
            return runid
        stamp += timedelta(seconds=1)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--set", required=True, dest="set_name")
    ap.add_argument("--arm", default="", help="comma list. With --grid, the control arm is added if absent")
    ap.add_argument("--grid", type=Path, help="factorial grid file (D-029)")
    ap.add_argument("--dist", default=",".join(S.DISTRIBUTIONS), help="comma list, default all 3")
    ap.add_argument("--seeds", required=True, help="e.g. 1001-1030 or 1001,1005")
    ap.add_argument("--repeat", type=int, default=1, help=f"set {REPEAT_SET} only")
    ap.add_argument("--runs-root", type=Path, default=PROJECT / "runs", help=argparse.SUPPRESS)
    ap.add_argument("--arm-params", action="append", default=[], metavar="ARM=FILE")
    args = ap.parse_args(argv)
    try:
        arms = [a for a in args.arm.split(",") if a]
        arm_params = {}
        if args.grid:
            arm_params = expand_grid(args.grid)
            control = S.ARMS[1]               # shared control: our build, switch off
            arms = [*([control] if control not in arms else []), *arms, *arm_params]
        if not arms:
            raise ValueError("give --arm or --grid")
        for item in args.arm_params:
            arm, _, file = item.partition("=")
            arm_params[arm] = load_arm_params(Path(file))
        cells = plan_cells(args.set_name, arms, args.dist.split(","), parse_seeds(args.seeds),
                           args.repeat, arm_params)
        folder = args.runs_root / args.set_name
        taken = existing_cells(folder)
        dup = [c for c in cells if c in taken] if args.set_name != REPEAT_SET else []
        if dup:
            raise ValueError(f"{len(dup)} cells already have a run under {folder}, first {dup[0]}")
    except (ValueError, OSError, json.JSONDecodeError) as err:
        print(f"refused: {err}")
        return 1
    template = TEMPLATE.read_text()
    for arm, distribution, seed in cells:
        run_dir = folder / fresh_runid(folder, arm, distribution, seed)
        run_dir.mkdir(parents=True)
        (run_dir / S.FILE_ARGOS).write_text(build_argos(template, arm, distribution, seed,
                                                        args.set_name, arm_params.get(arm, {})))
    print(f"wrote {len(cells)} run.argos under {folder}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
