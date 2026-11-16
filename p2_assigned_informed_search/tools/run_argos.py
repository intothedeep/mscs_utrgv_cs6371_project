"""Run the run.argos files of a root one at a time and write each run's files (M2-05, DESIGN 6.4).

Usage: OMP_NUM_THREADS=1 uv run python tools/run_argos.py <root>
<root> is runs, runs/<set> or one run folder. A folder with a manifest.json is skipped, unless the
manifest marks a failed run (then it runs again). Sequential on purpose (D-002, one core).
Each argos3 call has its own timeout (TIMEOUT_S). This script is exempt from the 300 s Python cap.
A failed run does not stop the batch (D-022). It gets a manifest with complete 0, no totals and
params.failed = the reason, plus header-only CSVs. check_runs.py then reports it. The exit code is
nonzero when any run failed. The vendor ForageData file appends, so an old results/ folder is
renamed to x_results_<n> before a re-run (soft delete, never rm).
This script is the only writer of manifest.json. It runs on the standard library only.
Assumed interfaces of our build (M2-03): the IS_METRICS line (key=value tokens) and, in the run
folder, queries.csv and points.csv. CODE_VERSION in CPFA_loop_functions.cpp.
"""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import run_io
import schema as S
from make_runs import PARAM_SET, PROJECT

__all__ = ["run_folder", "parse_forage", "parse_metrics_line", "build_manifest"]

TIMEOUT_S = 120
ARGOS_COMMAND = ["argos3", "-n", "-c", S.FILE_ARGOS]
RESULTS_DIR = "results"
NEST_RADIUS_LINE = re.compile(r"^NestRadius=([0-9.eE+-]+)\s*$", re.MULTILINE)
METRIC_TOKEN = re.compile(r"(\w+)=(\S+)")
# Keys of the IS_METRICS line (assumed format of M2-03).
TAG_TRAVEL, TAG_SEARCH, TAG_DEPARTURES, TAG_LAYOUT = (
    "travel_ticks", "search_ticks", "n_departures", "layout_sha")
CODE_VERSION = re.compile(r'CODE_VERSION\s*=\s*"([^"]+)"')
LOOP_SOURCE = PROJECT / "src" / "source" / "CPFA" / "CPFA_loop_functions.cpp"
VENDOR_LOOP_SOURCE = PROJECT / "vendor" / "Collision_Free_CPFA" / "source" / "CPFA" / "CPFA_loop_functions.cpp"
RESPAWN = 1                                  # D-007
LIB_SUFFIXES = (".dylib", ".so")


# ---- pure: parse and build -------------------------------------------------------

def parse_forage(text: str) -> list[int]:
    """Cumulative per-minute counts from a vendor ForageData line 'Forage: a, b, c'.

    The vendor writes the increase of each minute. The schema column is cumulative."""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) != 1:
        raise ValueError(f"ForageData has {len(lines)} lines, expected 1")
    body = lines[0].split(":", 1)[-1]
    total, out = 0, []
    for token in body.split(","):
        total += int(token)
        out.append(total)
    return out


def parse_metrics_line(stdout: str) -> dict[str, str] | None:
    for line in stdout.splitlines():
        if line.startswith(S.METRICS_TAG):
            return dict(METRIC_TOKEN.findall(line))
    return None


def read_argos(text: str) -> dict[str, Any]:
    """What the manifest needs from run.argos."""
    root = ET.fromstring(text)
    cpfa = root.find("loop_functions/CPFA")
    return {
        "ticks_per_second": int(root.find("framework/experiment").get("ticks_per_second")),
        "threads": int(root.find("framework/system").get("threads")),
        "nest_radius_xml": float(root.find("loop_functions/settings").get("NestRadius")),
        "controller_lib": root.find("controllers/CPFA_controller").get("library"),
        "loop_lib": root.find("loop_functions").get("library"),
        "cpfa_attributes": dict(cpfa.attrib) if cpfa is not None else {},
    }


def build_manifest(identity: dict[str, Any], argos: dict[str, Any], stamp: dict[str, Any],
                   outcome: dict[str, Any]) -> dict[str, Any]:
    """manifest.json from four parts. `outcome` holds metrics and the failure reason (or None)."""
    params = {S.PA.random_seed: identity["seed"], S.PA.max_sim_time_s: S.SIM_SECONDS,
              S.PA.food_distribution: S.DISTRIBUTION_CODES[identity["distribution"]],
              "cpfa_attributes": argos["cpfa_attributes"]}
    if outcome["failed"]:
        params["failed"] = outcome["failed"]
    return {
        S.K.schema_version: S.SCHEMA_VERSION, S.K.mock: 0, S.K.set: identity["set"],
        S.K.arm: identity["arm"], S.K.distribution: identity["distribution"],
        S.K.seed: identity["seed"], S.K.git_commit: stamp["git_commit"],
        S.K.git_dirty: stamp["git_dirty"], S.K.lib_sha: stamp["lib_sha"],
        S.K.xml_sha: stamp["xml_sha"], S.K.prereg_sha: None,
        S.K.nest_radius_xml: argos["nest_radius_xml"], S.K.nest_radius_eff: outcome["nest_radius_eff"],
        S.K.respawn: RESPAWN, S.K.param_set: PARAM_SET, S.K.layout_sha: outcome["layout_sha"],
        S.K.wall_s: outcome["wall_s"], S.K.code_version: stamp["code_version"],
        S.K.code_sha: stamp["code_sha"], S.K.params: params,
        S.K.env: {S.E.machine: stamp["machine"], S.E.argos: stamp["argos_version"],
                  S.E.threads: argos["threads"]},
        S.K.metrics: outcome["metrics"],
    }


def read_outcome(identity: dict[str, Any], argos: dict[str, Any], stdout: str,
                 forage_text: str | None, wall_s: float, run_files: dict[str, bool]) -> dict[str, Any]:
    """Metrics and failure reason from the saved outputs. Never raises: a problem is the reason."""
    out: dict[str, Any] = {"failed": None, "wall_s": round(wall_s, 2), "nest_radius_eff": None,
                           "layout_sha": None, "forage": [],
                           "metrics": {S.MT.collected: None, S.MT.sim_time_s: None, S.MT.complete: 0,
                                       S.MT.n_departures: None, S.MT.travel_s: None,
                                       S.MT.search_s: None}}
    score = S.parse_score(stdout)
    nest = NEST_RADIUS_LINE.search(stdout)
    if score is None:
        out["failed"] = "no line matches the score pattern in stdout.log"
        return out
    if nest is None:
        out["failed"] = "no NestRadius= line in stdout.log"
        return out
    collected, sim_time, _ = score
    out["nest_radius_eff"] = float(nest.group(1))
    met = out["metrics"]
    met[S.MT.collected], met[S.MT.sim_time_s] = collected, sim_time
    met[S.MT.complete] = int(sim_time >= S.SIM_SECONDS)
    try:
        out["forage"] = parse_forage(forage_text or "")
    except ValueError as err:
        out["failed"] = f"ForageData: {err}"
        return out
    if identity["arm"] == S.ARMS[0]:
        return out
    tag = parse_metrics_line(stdout)
    absent = [f for f, ok in run_files.items() if not ok]
    if tag is None or absent or not {TAG_TRAVEL, TAG_SEARCH, TAG_DEPARTURES, TAG_LAYOUT} <= tag.keys():
        out["failed"] = f"our build wrote no {S.METRICS_TAG} line with its 4 keys, or lacks {absent}"
        return out
    out["layout_sha"] = tag[TAG_LAYOUT]
    met[S.MT.n_departures] = int(tag[TAG_DEPARTURES])
    met[S.MT.travel_s] = round(int(tag[TAG_TRAVEL]) / argos["ticks_per_second"], 2)
    met[S.MT.search_s] = round(int(tag[TAG_SEARCH]) / argos["ticks_per_second"], 2)
    return out


# ---- I/O edge --------------------------------------------------------------------

def sha12(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def find_library(base: str) -> Path | None:
    for suffix in LIB_SUFFIXES:
        if Path(base + suffix).is_file():
            return Path(base + suffix)
    return None


def write_csv(path: Path, header: tuple[str, ...], rows: list[list[Any]]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def git_stamp() -> tuple[str, int]:
    """Commit and dirty flag. Dirty looks at src/ only: runs, results and tools do not change a run."""
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT, capture_output=True,
                            text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "src"], cwd=PROJECT,
                           capture_output=True, text=True, check=True).stdout.strip()
    return commit, int(bool(dirty))


def code_stamp(arm: str) -> tuple[str, str]:
    """(code_version, code_sha). Our build reads the CODE_VERSION constant. The vendor has none."""
    if arm == S.ARMS[0]:
        return S.ARMS[0], sha12(VENDOR_LOOP_SOURCE)
    found = CODE_VERSION.search(LOOP_SOURCE.read_text())
    if found is None:
        raise SystemExit(f"stop: no CODE_VERSION constant in {LOOP_SOURCE}")
    return found.group(1), sha12(LOOP_SOURCE)


def argos_version() -> str:
    done = subprocess.run([ARGOS_COMMAND[0], "--version"], capture_output=True, text=True)
    return (done.stdout or done.stderr).strip().splitlines()[0]


def retire_results(run_dir: Path) -> None:
    """Soft delete: a vendor result file appends, so a re-run needs a clean results/."""
    old = run_dir / RESULTS_DIR
    if old.exists():
        n = 1
        while (run_dir / f"x_{RESULTS_DIR}_{n}").exists():
            n += 1
        old.rename(run_dir / f"x_{RESULTS_DIR}_{n}")


def run_folder(run_dir: Path, command: list[str], env_stamp: dict[str, Any]) -> str | None:
    """Run one folder, write its files. Returns the failure reason or None."""
    argos = read_argos((run_dir / S.FILE_ARGOS).read_text())
    parsed = S.parse_runid(run_dir.name)
    identity = {"set": run_dir.parent.name, "arm": parsed[2], "distribution": parsed[3], "seed": parsed[4]}
    retire_results(run_dir)
    (run_dir / RESULTS_DIR).mkdir()
    for name in (S.FILE_QUERIES, S.FILE_POINTS):   # a stale file must not pass for this run
        if (run_dir / name).exists():
            (run_dir / name).rename(run_dir / f"x_{name}")
    started = time.perf_counter()
    try:
        done = subprocess.run(command, cwd=run_dir, capture_output=True, text=True, timeout=TIMEOUT_S)
        stdout, problem = done.stdout, (f"argos3 exited {done.returncode}" if done.returncode else None)
        (run_dir / S.FILE_STDOUT).write_text(done.stdout + done.stderr)
    except subprocess.TimeoutExpired as err:
        stdout, problem = (err.stdout or b"").decode(errors="replace"), f"timeout after {TIMEOUT_S} s"
        (run_dir / S.FILE_STDOUT).write_text(stdout)
    wall_s = time.perf_counter() - started
    forage = sorted((run_dir / RESULTS_DIR).glob("*ForageData.txt"))
    forage_text = forage[0].read_text() if len(forage) == 1 else None
    run_files = {n: (run_dir / n).is_file() for n in (S.FILE_QUERIES, S.FILE_POINTS)}
    outcome = read_outcome(identity, argos, stdout, forage_text, wall_s, run_files)
    if len(forage) != 1 and not outcome["failed"]:
        outcome["failed"] = f"{len(forage)} ForageData files in results/, expected 1"
    outcome["failed"] = problem or outcome["failed"]
    libs = [find_library(argos["controller_lib"]), find_library(argos["loop_lib"])]
    if any(lib is None for lib in libs):
        raise SystemExit(f"stop: a library of {run_dir.name} is missing")
    code_version, code_sha = code_stamp(identity["arm"])
    stamp = {**env_stamp, "xml_sha": sha12(run_dir / S.FILE_ARGOS), "code_version": code_version,
             "code_sha": code_sha,
             "lib_sha": {S.L.controller: sha12(libs[0]), S.L.loop: sha12(libs[1])}}
    manifest = build_manifest(identity, argos, stamp, outcome)
    if outcome["failed"]:
        forage_rows = []
    else:
        forage_rows = [[i + 1, v] for i, v in enumerate(outcome["forage"])]
    write_csv(run_dir / S.FILE_FORAGE, S.FORAGE_COLUMNS, forage_rows)
    for name, header in ((S.FILE_QUERIES, S.QUERIES_COLUMNS), (S.FILE_POINTS, S.POINTS_COLUMNS)):
        if identity["arm"] == S.ARMS[0] or outcome["failed"] or not (run_dir / name).is_file():
            write_csv(run_dir / name, header, [])   # vendor (D-014) and failed runs: header only
    (run_dir / S.FILE_MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n")
    return outcome["failed"]


def pending_runs(root: Path) -> list[Path]:
    runs = [root] if (root / S.FILE_ARGOS).is_file() else run_io.find_run_dirs(root)
    out = []
    for run_dir in runs:
        if not (run_dir / S.FILE_ARGOS).is_file():
            continue
        if (run_dir / S.FILE_MANIFEST).is_file():
            if "failed" not in run_io.read_manifest(run_dir)[S.K.params]:
                continue
        out.append(run_dir)
    return out


def preflight(runs: list[Path]) -> str | None:
    """Reason to stop before any run: argos3 or a library is missing."""
    if shutil.which(ARGOS_COMMAND[0]) is None:
        return f"{ARGOS_COMMAND[0]} is not on PATH"
    for run_dir in runs:
        argos = read_argos((run_dir / S.FILE_ARGOS).read_text())
        for lib in (argos["controller_lib"], argos["loop_lib"]):
            if find_library(lib) is None:
                return f"library {lib} ({LIB_SUFFIXES}) is missing, needed by {run_dir.name}. Build first"
    return None


def main(argv: list[str]) -> int:
    if len(argv) != 1 or not Path(argv[0]).is_dir():
        print(__doc__)
        return 2
    runs = pending_runs(Path(argv[0]))
    reason = preflight(runs)
    if reason:
        print(f"stop: {reason}")
        return 2
    commit, dirty = git_stamp()
    env_stamp = {"git_commit": commit, "git_dirty": dirty, "argos_version": argos_version(),
                 "machine": f"{platform.system()} {platform.machine()}"}
    failed: list[tuple[str, str]] = []
    for i, run_dir in enumerate(runs, 1):
        print(f"[{i}/{len(runs)}] {run_dir.name}", flush=True)
        reason = run_folder(run_dir, ARGOS_COMMAND, env_stamp)
        if reason:
            print(f"  FAILED: {reason}", flush=True)
            failed.append((run_dir.name, reason))
    print(f"SUMMARY ran={len(runs)} failed={len(failed)}")
    for name, why in failed:
        print(f"  failed {name}: {why}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
