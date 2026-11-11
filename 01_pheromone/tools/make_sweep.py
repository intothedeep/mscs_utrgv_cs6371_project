"""Write one .argos file for one cell from the headless template (U8, single-cell mode).

Usage: make_sweep.py --cell d,defense,seed --root <runs root>
The file goes to src/experiments/generated/<runid>.argos. Run it from src/:
    argos3 -c experiments/generated/<runid>.argos
It sets the seed, the cell, the run folder and the stamps (git commit, library hashes).
Why stamps here: C++ has no git access and no hash (DESIGN section 4).
The 80-run mode (--sweep) comes with M3-04.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

from run_results import PROJECT, sha256_hex
import schema as S

__all__ = ["Override", "build_argos", "GENERATED"]

SRC = PROJECT / "src"
TEMPLATE = SRC / "experiments" / "pheromone_headless.template.argos"
GENERATED = SRC / "experiments" / "generated"
LIBRARIES = {"code_sha_loop_functions": ("build/loop_functions/pheromone_loop_functions",
                                         "libpheromone_loop_functions.*"),
             "code_sha_controller": ("build/controllers/pheromone_forager", "libpheromone_forager.*")}
PHEROMONE_LF = "loop_functions/pheromone"
Override = tuple[str, str, str]  # (element path from <argos-configuration>, attribute, value)


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


def build_argos(d: int, defense: int, seed: int, root: Path,
                overrides: tuple[Override, ...] = (), tags: dict[str, str] | None = None
                ) -> tuple[str, Path]:
    """Return (runid, path of the generated .argos). Tags land in manifest params."""
    if d != 0:
        raise SystemExit("stop: d > 0 needs the detractor controller (M3-01)")
    root = root.resolve()
    tree = ET.parse(TEMPLATE)
    runid = fresh_runid(d, defense, seed, root)
    set_attr(tree, "framework/experiment", "random_seed", str(seed))
    set_attr(tree, PHEROMONE_LF, "n_det", str(d))
    set_attr(tree, PHEROMONE_LF, "defense", str(defense))
    for key, value in (tags or {}).items():
        set_attr(tree, PHEROMONE_LF, key, value)
    for path, name, value in overrides:
        set_attr(tree, path, name, value)
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
    ap.add_argument("--cell", required=True, type=parse_cell, help="d,defense,seed")
    ap.add_argument("--root", required=True, type=Path, help="runs root, for example runs/smoke")
    args = ap.parse_args(argv)
    runid, out = build_argos(*args.cell, args.root)
    print(f"runid={runid}\nargos_file={out}\nrun_folder={args.root.resolve() / runid}")
    print(f"command: cd {SRC} && argos3 -c experiments/generated/{out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
