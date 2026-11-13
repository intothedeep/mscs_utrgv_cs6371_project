"""Validate a runs root against schema.py (DESIGN 6.6 items 1 to 6).

Usage: check_runs.py <root> [--log FILE]
Root: `runs`, `mock/runs`, or one set folder. Exit 0 when every run passes, 1 otherwise.
Each failure line names run, file and column or key. The checker holds no column name.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import run_io
import schema as S

__all__ = ["check_root", "check_run"]

Issue = tuple[str, str]                # (column or key, message)
Problem = tuple[str, str, str, str]    # (run, file, column, message)
HEX12 = re.compile(r"^[0-9a-f]{12}$")
SIM_TIME_TOL_S = 1e-6


def is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# ---- pure checks -----------------------------------------------------------------

def header_issues(header: list[str], expected: tuple[str, ...]) -> list[Issue]:
    out = [(c, "expected column is missing") for c in expected if c not in header]
    out += [(c, "unexpected column") for c in header if c not in expected]
    if not out and tuple(header) != expected:
        out.append(("", "columns are in the wrong order"))
    return out


def parse_columns(rows: list[list[str]], types: dict[str, type], required: tuple[str, ...]
                  ) -> tuple[dict[str, list], list[Issue]]:
    """Cast column by column. A cell outside `required` may be empty (None). First bad cell only."""
    width = len(types)
    for i, row in enumerate(rows):
        if len(row) != width:
            return {}, [("", f"row {i + 2} has {len(row)} fields, expected {width}")]
    cols: dict[str, list] = {}
    issues: list[Issue] = []
    for j, (name, typ) in enumerate(types.items()):
        out: list = []
        for i, row in enumerate(rows):
            cell = row[j]
            if cell == "" and name not in required:
                out.append(None)
                continue
            try:
                out.append(typ(cell))
            except ValueError:
                issues.append((name, f"row {i + 2}: {cell!r} is not {typ.__name__}"))
                break
        else:
            cols[name] = out
    return cols, issues


def manifest_issues(m: Any, folder: str, parent_set: str | None) -> list[Issue]:
    if not isinstance(m, dict):
        return [("", "manifest is not a JSON object")]
    out = [(k, "key is missing") for k in S.MANIFEST_KEYS if k not in m]
    out += [(k, "unexpected key") for k in m if k not in S.MANIFEST_KEYS]
    if out:
        return out
    subs = {S.K.lib_sha: S.LIB_SHA_KEYS, S.K.env: S.ENV_KEYS, S.K.params: S.PARAM_KEYS,
            S.K.metrics: S.METRICS_KEYS}
    for key, names in subs.items():
        if not isinstance(m[key], dict):
            return [(key, "must be a JSON object")]
        out += [(f"{key}.{n}", "key is missing") for n in names if n not in m[key]]
        if key != S.K.params:  # params may carry every .argos value
            out += [(f"{key}.{n}", "unexpected key") for n in m[key] if n not in names]
    if out:
        return out
    if m[S.K.schema_version] != S.SCHEMA_VERSION:
        out.append((S.K.schema_version, f"is {m[S.K.schema_version]!r}, expected {S.SCHEMA_VERSION}"))
    if m[S.K.mock] not in (0, 1) or isinstance(m[S.K.mock], bool):
        return out + [(S.K.mock, "must be the integer 0 or 1")]
    runid = S.parse_runid(folder)
    if runid is None:
        return out + [("runid", f"folder name {folder!r} does not match the runid pattern")]
    is_mock, _, run_arm, run_dist, run_seed = runid
    if is_mock != bool(m[S.K.mock]):
        out.append(("runid", f"prefix {S.MOCK_PREFIX} must be present exactly when "
                             f"{S.K.mock} is 1"))
    for key, got in ((S.K.arm, run_arm), (S.K.distribution, run_dist), (S.K.seed, run_seed)):
        if m[key] != got:
            out.append((key, f"is {m[key]!r}, runid says {got!r}"))
    arm = m[S.K.arm]
    if arm not in S.ARMS and not (arm.startswith(S.ABLATION_ARM_PREFIX) and
                                  len(arm) > len(S.ABLATION_ARM_PREFIX)):
        out.append((S.K.arm, f"{arm!r} is not one of {S.ARMS} or {S.ABLATION_ARM_PREFIX}<name>"))
    if m[S.K.set] not in S.SETS:
        out.append((S.K.set, f"{m[S.K.set]!r} is not one of {S.SETS}"))
    elif parent_set is not None and m[S.K.set] != parent_set:
        out.append((S.K.set, f"is {m[S.K.set]!r} but the run sits in folder {parent_set!r}"))
    p = m[S.K.params]
    if p[S.PA.random_seed] != m[S.K.seed]:
        out.append((f"{S.K.params}.{S.PA.random_seed}", "must equal the run seed"))
    if p[S.PA.food_distribution] != S.DISTRIBUTION_CODES.get(m[S.K.distribution]):
        out.append((f"{S.K.params}.{S.PA.food_distribution}", "does not match the distribution"))
    if not is_number(m[S.K.git_dirty]) or m[S.K.git_dirty] not in (0, 1):
        out.append((S.K.git_dirty, "must be the integer 0 or 1"))
    if not m[S.K.mock]:  # real runs carry real hashes
        for name, value in ((f"{S.K.lib_sha}.{n}", m[S.K.lib_sha][n]) for n in S.LIB_SHA_KEYS):
            if not (isinstance(value, str) and HEX12.match(value)):
                out.append((name, "must be 12 hex characters in a real run"))
    return out


def score_issues(stdout: str, m: dict, forage_last: int | None) -> list[Issue]:
    """DESIGN 6.6 item 2: metrics.collected = score line = last per-minute row."""
    met = m[S.K.metrics]
    score = S.parse_score(stdout)
    if score is None:
        return [("", "no line matches the score pattern")]
    collected, sim_time, seed = score
    out: list[Issue] = []
    if met[S.MT.collected] != collected:
        out.append((f"{S.K.metrics}.{S.MT.collected}",
                    f"is {met[S.MT.collected]!r} but the score line says {collected}"))
    if forage_last is not None and forage_last != collected:
        out.append((S.F.collected, f"last per-minute row {forage_last} != score line {collected}"))
    if not (is_number(met[S.MT.sim_time_s])
            and abs(met[S.MT.sim_time_s] - sim_time) <= SIM_TIME_TOL_S):
        out.append((f"{S.K.metrics}.{S.MT.sim_time_s}",
                    f"is {met[S.MT.sim_time_s]!r} but the score line says {sim_time}"))
    if seed != m[S.K.seed]:
        out.append((S.K.seed, f"is {m[S.K.seed]!r} but the score line says {seed}"))
    if met[S.MT.complete] != int(sim_time >= S.SIM_SECONDS):
        out.append((f"{S.K.metrics}.{S.MT.complete}",
                    f"is {met[S.MT.complete]!r} but sim time is {sim_time} of {S.SIM_SECONDS} s"))
    return out


def forage_issues(header: list[str], rows: list[list[str]]) -> tuple[list[Issue], int | None]:
    bad = header_issues(header, S.FORAGE_COLUMNS)
    if bad:
        return bad, None
    cols, bad = parse_columns(rows, {S.F.minute: int, S.F.collected: int}, S.FORAGE_COLUMNS)
    if bad:
        return bad, None
    if not rows:
        return [("", "no per-minute row")], None
    out: list[Issue] = []
    if cols[S.F.minute] != list(range(1, len(rows) + 1)):
        out.append((S.F.minute, "must count 1, 2, 3, ... with no gap"))
    v = cols[S.F.collected]
    if any(b < a for a, b in zip(v, v[1:])):
        out.append((S.F.collected, "decreases (it is cumulative)"))
    return out, v[-1]


def rows_issues(file: str, header: list[str], rows: list[list[str]], expected: tuple[str, ...],
                types: dict[str, type], required: tuple[str, ...], arm: str) -> list[Issue]:
    bad = header_issues(header, expected)
    if bad:
        return bad
    cols, bad = parse_columns(rows, types, required)
    if bad:
        return bad
    out: list[Issue] = []
    if not rows and arm not in S.HEADER_ONLY_ARMS[file]:
        out.append(("", f"header only, allowed just for arm {S.HEADER_ONLY_ARMS[file]}"))
    if S.Q.branch in cols and set(cols[S.Q.branch]) - set(S.BRANCHES):
        out.append((S.Q.branch, f"value outside {S.BRANCHES}"))
    return out


def cell_problems(kept: dict[str, tuple[str, dict]]) -> list[Problem]:
    """DESIGN 6.6 item 4: one line per (set, arm, distribution) that misses seeds."""
    present = {(m[S.K.set], m[S.K.arm], m[S.K.distribution], m[S.K.seed]) for _, m in kept.values()}
    sets = {m[S.K.set] for _, m in kept.values()}
    out: list[Problem] = []
    for name in sorted(sets & S.SET_CELLS.keys()):
        arms, seeds = S.SET_CELLS[name]
        for arm in arms:
            for dist in S.DISTRIBUTIONS:
                missing = [s for s in seeds if (name, arm, dist, s) not in present]
                if missing:
                    out.append((f"set {name}", "-", f"{S.K.arm}={arm} {S.K.distribution}={dist}",
                                f"{len(missing)} of {len(seeds)} cells missing, seeds {missing}"))
    return out


def keep_latest(runs: dict[str, tuple[str, dict]]) -> tuple[dict[str, tuple[str, dict]], list[str]]:
    """DESIGN 6.6 item 4: a duplicate cell keeps the latest complete run (runid stamp order)."""
    groups: dict[tuple, list[str]] = defaultdict(list)
    for folder, (_, m) in runs.items():
        groups[(m[S.K.set], m[S.K.arm], m[S.K.distribution], m[S.K.seed])].append(folder)
    kept, notes = {}, []
    for key, folders in groups.items():
        best = max(folders, key=lambda f: (runs[f][1][S.K.metrics][S.MT.complete],
                                           S.parse_runid(f)[1], f))
        kept[best] = runs[best]
        notes += [f"NOTE run={f}: duplicate of {best}, not used for the cell checks"
                  for f in folders if f != best]
    return kept, notes


def pairing_problems(kept: dict[str, tuple[str, dict]]) -> list[Problem]:
    """DESIGN 6.6 items 5 and 6, for S3 and S4 only."""
    out: list[Problem] = []
    for name in S.LAYOUT_SETS:
        runs = {f: m for f, (_, m) in kept.items() if m[S.K.set] == name}
        by_layout: dict[tuple, dict[Any, list[str]]] = defaultdict(lambda: defaultdict(list))
        for folder, m in runs.items():
            by_layout[(m[S.K.distribution], m[S.K.seed])][m[S.K.layout_sha]].append(folder)
            if m[S.K.git_dirty] != 0:
                out.append((folder, S.FILE_MANIFEST, S.K.git_dirty, f"is {m[S.K.git_dirty]}, set {name} needs 0"))
            if m[S.K.layout_sha] is None:
                out.append((folder, S.FILE_MANIFEST, S.K.layout_sha, f"is empty, set {name} needs it"))
        for (dist, seed), shas in by_layout.items():
            if len(shas) > 1:
                out.append((f"set {name}", S.FILE_MANIFEST, S.K.layout_sha,
                            f"{S.K.distribution}={dist} {S.K.seed}={seed} differs across arms: "
                            f"{dict(shas)}"))
        for key in (S.K.prereg_sha, S.K.git_commit):
            values = {m[key] for m in runs.values()}
            if len(values) > 1:
                out.append((f"set {name}", S.FILE_MANIFEST, key,
                            f"runs carry {len(values)} different values: {sorted(map(str, values))}"))
    return out


# ---- I/O edge --------------------------------------------------------------------

def check_run(run_dir: Path) -> tuple[list[Problem], dict | None]:
    run, problems = run_dir.name, []

    def add(file: str, issues: list[Issue]) -> None:
        problems.extend((run, file, col, msg) for col, msg in issues)

    absent = [f for f in S.RUN_FILES if not (run_dir / f).is_file()]
    add("-", [("", f"{f} is missing") for f in absent])
    if S.FILE_MANIFEST in absent:
        return problems, None
    try:
        m = run_io.read_manifest(run_dir)
    except json.JSONDecodeError as err:
        add(S.FILE_MANIFEST, [("", f"invalid JSON: {err}")])
        return problems, None
    parent = run_dir.parent.name
    bad = manifest_issues(m, run, parent if parent in S.SETS else None)
    add(S.FILE_MANIFEST, bad)
    if bad:
        return problems, None
    arm = m[S.K.arm]
    forage_last = None
    if S.FILE_FORAGE not in absent:
        bad, forage_last = forage_issues(*run_io.read_csv(run_dir / S.FILE_FORAGE))
        add(S.FILE_FORAGE, bad)
    if S.FILE_STDOUT not in absent:
        add(S.FILE_STDOUT, score_issues((run_dir / S.FILE_STDOUT).read_text(), m, forage_last))
    if S.FILE_QUERIES not in absent:
        add(S.FILE_QUERIES, rows_issues(S.FILE_QUERIES, *run_io.read_csv(run_dir / S.FILE_QUERIES),
                                        S.QUERIES_COLUMNS, S.QUERIES_TYPES, S.QUERIES_REQUIRED, arm))
    if S.FILE_POINTS not in absent:
        add(S.FILE_POINTS, rows_issues(S.FILE_POINTS, *run_io.read_csv(run_dir / S.FILE_POINTS),
                                       S.POINTS_COLUMNS, S.POINTS_TYPES, S.POINTS_COLUMNS, arm))
    return problems, m


def mixed_root_problem(root: Path, manifests: dict[str, dict]) -> Problem | None:
    """DESIGN 6.6 item 3: one root holds only mock = 1 or only mock = 0."""
    kinds: dict[int, list[str]] = defaultdict(list)
    for folder, m in manifests.items():
        if isinstance(m, dict) and m.get(S.K.mock) in (0, 1):
            kinds[m[S.K.mock]].append(folder)
    if len(kinds) < 2:
        return None
    return (str(root), S.FILE_MANIFEST, S.K.mock,
            f"root mixes {len(kinds[1])} mock runs ({kinds[1][0]}, ...) and "
            f"{len(kinds[0])} real runs ({kinds[0][0]}, ...). The check stops")


def check_root(root: Path) -> tuple[list[Problem], list[str], int]:
    run_dirs = run_io.find_run_dirs(root)
    raw: dict[str, dict] = {}
    for run_dir in run_dirs:
        try:
            m = run_io.read_manifest(run_dir)
        except (OSError, json.JSONDecodeError):
            continue  # check_run names the cause
        if isinstance(m, dict):
            raw[run_dir.name] = m
    mixed = mixed_root_problem(root, raw)
    if mixed:
        return [mixed], [], len(run_dirs)
    problems: list[Problem] = []
    manifests: dict[str, tuple[str, dict]] = {}
    for run_dir in run_dirs:
        bad, manifest = check_run(run_dir)
        problems += bad
        if manifest is not None:
            manifests[run_dir.name] = (str(run_dir), manifest)
    kept, notes = keep_latest(manifests)
    return problems + cell_problems(kept) + pairing_problems(kept), notes, len(run_dirs)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", type=Path)
    ap.add_argument("--log", type=Path, help="also write the printed lines to this file")
    args = ap.parse_args(argv)
    if not args.root.is_dir():
        print(f"FAIL root {args.root} is not a folder")
        return 1
    problems, notes, n_runs = check_root(args.root)
    lines = [f"FAIL run={r} file={f or '-'} column={c or '-'}: {msg}" for r, f, c, msg in problems]
    lines += notes
    if n_runs == 0:
        lines.append(f"FAIL root {args.root} holds no run folder")
    failed = len({p[0] for p in problems})
    lines.append(f"SUMMARY runs={n_runs} failed={failed} problems={len(problems)}")
    print("\n".join(lines))
    if args.log:
        args.log.parent.mkdir(parents=True, exist_ok=True)
        args.log.write_text("\n".join(lines) + "\n")
    return 1 if problems or n_runs == 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
