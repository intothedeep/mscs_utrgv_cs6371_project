"""Write .argos files for one cell or the whole sweep from the headless template (U8, U11).

Usage:
  make_sweep.py --cell d,defense,seed --root <runs root>     one file, template values
  make_sweep.py --sweep [--run] [--seeds a-b] [--root R] [--t-lock T]
                                                             8 cells x seeds (default 1-10, 80 runs)
                                                             into runs/sweep/, frozen values
  --cell also takes --t-lock (defense v2 lockout, seconds).
Files go to src/experiments/generated/<runid>.argos. Run one from src/:
    argos3 -c experiments/generated/<runid>.argos
It sets the seed, the cell, the run folder and the stamps (git commit, library hashes).
Why stamps here: C++ has no git access and no hash (DESIGN section 4).
--sweep needs tuning_pick.json and defense_pick.json. It skips cells already complete.
--run runs the new files one at a time, one core, 300 s each (D-013).
"""
from __future__ import annotations

import argparse
import copy
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

import schema as S
from run_results import PROJECT, sha256_hex
from sweep_params import Override, overrides, parse_seeds

__all__ = ["build_argos", "add_detractors", "GENERATED", "SRC", "git_stamp", "load_template", "set_attr"]

SRC = PROJECT / "src"
TEMPLATE = SRC / "experiments" / "pheromone_headless.template.argos"
GENERATED = SRC / "experiments" / "generated"
LIBRARIES = {"code_sha_loop_functions": ("build/loop_functions/pheromone_loop_functions",
                                         "libpheromone_loop_functions.*"),
             "code_sha_controller": ("build/controllers/pheromone_forager", "libpheromone_forager.*")}
PHEROMONE_LF = "loop_functions/pheromone"
DEFENSE_NODE = "controllers/pheromone_forager_controller/params/defense"


def library_sha12(folder: str, pattern: str) -> str:
    found = sorted((SRC / folder).glob(pattern))
    if not found:
        raise SystemExit(f"stop: built library {folder}/{pattern} is missing. Build src/ first")
    return sha256_hex(found[0])[:12]  # a missing library must stop us: no stale hash


def git_stamp() -> tuple[str, bool]:
    """Commit and dirty flag. Dirty looks at src/ only: runs, results and tools do not change a run."""
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT, capture_output=True,
                            text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "src"], cwd=PROJECT,
                           capture_output=True, text=True, check=True).stdout.strip()
    return commit, bool(dirty)


def fresh_runid(d: int, defense: int, seed: int, root: Path) -> str:
    """Same cell twice in one second (judgement arms) must not share a runid: bump the stamp."""
    stamp = datetime.now()
    while True:
        runid = f"{stamp:%Y%m%d-%H%M%S}_d{d}_def{defense}_s{seed}"
        if not (root / runid).exists() and not (GENERATED / f"{runid}.argos").exists():
            return runid
        stamp += timedelta(seconds=1)


def set_attr(tree: ET.ElementTree, path: str, name: str, value: str) -> None:
    node = tree.getroot().find(path)
    if node is None:
        raise SystemExit(f"stop: template has no element {path}")
    node.set(name, value)


def load_template(path: Path = TEMPLATE) -> ET.ElementTree:
    return ET.parse(path)


def add_detractors(tree: ET.ElementTree, d: int) -> None:
    """D-005: d detractors (dt_) are added after the 20 honest robots. Copy of the honest
    controller with role=detractor, and a second <distribute> in the nest.
    Added after the honest block, so honest start poses do not depend on d."""
    if d == 0:
        return
    root = tree.getroot()
    controllers = root.find("controllers")
    honest = controllers.find("pheromone_forager_controller")  # type: ignore[union-attr]
    detractor = copy.deepcopy(honest)
    detractor.set("id", "detractor")  # type: ignore[union-attr]
    detractor.find("params").set("role", "detractor")  # type: ignore[union-attr]
    controllers.append(detractor)  # type: ignore[union-attr]
    arena = root.find("arena")
    block = copy.deepcopy(arena.find("distribute"))  # type: ignore[union-attr]
    block.find("entity").set("quantity", str(d))  # type: ignore[union-attr]
    robot = block.find("entity/foot-bot")  # type: ignore[union-attr]
    robot.set("id", "dt_")  # type: ignore[union-attr]
    robot.find("controller").set("config", "detractor")  # type: ignore[union-attr]
    arena.append(block)  # type: ignore[union-attr]


def build_argos(d: int, defense: int, seed: int, root: Path,
                overrides: tuple[Override, ...] = (), tags: dict[str, str] | None = None
                ) -> tuple[str, Path]:
    """Return (runid, path of the generated .argos). Tags land in manifest params."""
    if d not in S.DETRACTOR_COUNTS or defense not in S.DEFENSES:
        raise SystemExit(f"stop: d in {S.DETRACTOR_COUNTS} and defense in {S.DEFENSES}")
    root = root.resolve()
    tree = load_template()
    runid = fresh_runid(d, defense, seed, root)
    set_attr(tree, "framework/experiment", "random_seed", str(seed))
    set_attr(tree, PHEROMONE_LF, "n_det", str(d))
    set_attr(tree, PHEROMONE_LF, "defense", str(defense))
    set_attr(tree, DEFENSE_NODE, "enabled", "true" if defense else "false")  # the controller reads this
    for key, value in (tags or {}).items():
        set_attr(tree, PHEROMONE_LF, key, value)
    for path, name, value in overrides:
        set_attr(tree, path, name, value)
    add_detractors(tree, d)
    commit, dirty = git_stamp()
    logger = {"root": str(root), "runid": runid, "git_commit": commit,
              "git_dirty": "true" if dirty else "false",
              **{key: library_sha12(*lib) for key, lib in LIBRARIES.items()}}
    ET.SubElement(tree.getroot().find("loop_functions"), "logger", logger)  # type: ignore[arg-type]
    ET.indent(tree)
    GENERATED.mkdir(parents=True, exist_ok=True)
    out = GENERATED / f"{runid}.argos"
    out.write_text('<?xml version="1.0" ?>\n' + ET.tostring(tree.getroot(), encoding="unicode") + "\n")
    return runid, out


def parse_cell(text: str) -> tuple[int, int, int]:
    try:
        d, defense, seed = (int(v) for v in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("use d,defense,seed, for example 0,0,1")
    if defense not in S.DEFENSES or d not in S.DETRACTOR_COUNTS or seed < 1:
        raise argparse.ArgumentTypeError(f"d in {S.DETRACTOR_COUNTS}, defense in {S.DEFENSES}, seed >= 1")
    return d, defense, seed


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--cell", type=parse_cell, help="d,defense,seed")
    mode.add_argument("--sweep", action="store_true", help="8 cells x seeds into runs/sweep/ (80 runs for 1-10)")
    ap.add_argument("--root", type=Path, help="runs root: needed for --cell, default runs/sweep for --sweep")
    ap.add_argument("--run", action="store_true", help="with --sweep: also run the new files")
    ap.add_argument("--seeds", type=parse_seeds, default=S.SEEDS, metavar="a-b",
                    help="with --sweep: seed range, default 1-10")
    ap.add_argument("--t-lock", type=float, help="defense v2 lockout seconds. Default: template value (0)")
    args = ap.parse_args(argv)
    if args.sweep:
        from sweep_plan import ROOT, run_sweep  # late import: sweep_plan uses build_argos from here
        return run_sweep(args.run, args.root or ROOT, args.seeds, args.t_lock)
    if args.root is None:
        ap.error("--cell needs --root")
    set_lock = overrides(t_lock=args.t_lock) if args.t_lock is not None else ()
    runid, out = build_argos(*args.cell, args.root, set_lock)
    print(f"runid={runid}\nargos_file={out}\nrun_folder={args.root.resolve() / runid}")
    print(f"command: cd {SRC} && argos3 -c experiments/generated/{out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
