"""Validate a runs root against schema.py (U1).

Usage: check_runs.py <root> [--log FILE]
Exit 0 when every run passes, 1 otherwise. Each failure line names run, file, column.
The checker holds no column name: all names come from schema.py.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import schema as S

__all__ = ["check_run", "check_root"]

Issue = tuple[str, str]            # (column or key path, message)
Problem = tuple[str, str, str, str]  # (run, file, column, message)
LAYOUT_TOL_M = 1e-6


# ---- pure checks -----------------------------------------------------------------

def header_issues(header: list[str], expected: tuple[str, ...]) -> list[Issue]:
    out = [(c, "expected column is missing") for c in expected if c not in header]
    out += [(c, "unexpected column") for c in header if c not in expected]
    if not out and tuple(header) != expected:
        out.append(("", "columns are in the wrong order"))
    return out


def parse_columns(rows: list[list[str]], types: dict[str, type]
                  ) -> tuple[dict[str, list], list[Issue]]:
    """Cast column by column. Report the first bad value of each column only."""
    width = len(types)
    for i, row in enumerate(rows):
        if len(row) != width:
            return {}, [("", f"row {i + 2} has {len(row)} fields, expected {width}")]
    cols: dict[str, list] = {}
    issues: list[Issue] = []
    for j, (name, typ) in enumerate(types.items()):
        raw = [r[j] for r in rows]
        try:
            cols[name] = [typ(v) for v in raw]
        except ValueError:
            bad = next(i for i, v in enumerate(raw) if not _casts(typ, v))
            issues.append((name, f"row {bad + 2}: {raw[bad]!r} is not {typ.__name__}"))
    return cols, issues


def _casts(typ: type, value: str) -> bool:
    try:
        typ(value)
        return True
    except ValueError:
        return False


def _is_point(p: Any) -> bool:
    return (isinstance(p, list) and len(p) == 2
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in p))


def manifest_issues(m: Any, folder: str) -> list[Issue]:
    if not isinstance(m, dict):
        return [("", "manifest is not a JSON object")]
    out = [(k, "key is missing") for k in S.MANIFEST_KEYS if k not in m]
    out += [(k, "unexpected key") for k in m if k not in S.MANIFEST_KEYS]
    if out:
        return out
    subs = {S.K_PARAMS: S.PARAM_KEYS, S.K_LAYOUT: S.LAYOUT_KEYS, S.K_METRICS: S.METRICS_KEYS,
            "code_sha": S.CODE_SHA_KEYS, "env": S.ENV_KEYS}
    for key, names in subs.items():
        if not isinstance(m[key], dict):
            return [(key, "must be a JSON object")]
        out += [(f"{key}.{n}", "key is missing") for n in names if n not in m[key]]
        if key != S.K_PARAMS:  # params may carry every .argos value
            out += [(f"{key}.{n}", "unexpected key") for n in m[key] if n not in names]
    if out:
        return out
    if m[S.K_SCHEMA] != S.SCHEMA_VERSION:
        out.append((S.K_SCHEMA, f"is {m[S.K_SCHEMA]!r}, expected {S.SCHEMA_VERSION}"))
    if not isinstance(m[S.K_MOCK], bool):
        return out + [(S.K_MOCK, "must be true or false")]
    match = S.RUNID_RE.match(str(m[S.K_RUNID]))
    if not match:
        return out + [(S.K_RUNID, f"{m[S.K_RUNID]!r} does not match the runid pattern")]
    if bool(match["prefix"]) != m[S.K_MOCK]:
        out.append((S.K_RUNID, f"prefix {S.MOCK_PREFIX} must be present exactly when "
                               f"{S.K_MOCK} is true"))
    if m[S.K_RUNID] != folder:
        out.append((S.K_RUNID, f"is {m[S.K_RUNID]!r} but the folder is {folder!r}"))
    p, lay = m[S.K_PARAMS], m[S.K_LAYOUT]
    for name, got in ((S.P_NDET, int(match["d"])), (S.P_DEFENSE, int(match["defense"])),
                      (S.P_SEED, int(match["seed"]))):
        if p[name] != got:
            out.append((f"{S.K_PARAMS}.{name}", f"is {p[name]!r}, runid says {got}"))
    if lay[S.L_SEED] != p[S.P_SEED]:
        out.append((f"{S.K_LAYOUT}.{S.L_SEED}", "must equal the run seed"))
    if p[S.P_NDET] not in S.DECOYS_USED:
        out.append((f"{S.K_PARAMS}.{S.P_NDET}", "is not one of the detractor counts"))
    elif lay[S.L_NUSED] != S.DECOYS_USED[p[S.P_NDET]]:
        out.append((f"{S.K_LAYOUT}.{S.L_NUSED}",
                    f"is {lay[S.L_NUSED]!r}, expected {S.DECOYS_USED[p[S.P_NDET]]}"))
    for name, n in ((S.L_SOURCES, 3), (S.L_DECOYS, 2)):
        pts = lay[name]
        if not (isinstance(pts, list) and len(pts) == n and all(_is_point(q) for q in pts)):
            out.append((f"{S.K_LAYOUT}.{name}", f"must be {n} [x, y] points"))
    return out


def ticks_issues(header: list[str], rows: list[list[str]], m: dict) -> list[Issue]:
    bad = header_issues(header, S.TICKS_COLUMNS)
    if bad:
        return bad
    cols, bad = parse_columns(rows, S.TICKS_TYPES)
    if bad:
        return bad
    n, met = len(rows), m[S.K_METRICS]
    out: list[Issue] = []
    if met[S.M_COMPLETE] is True and n != S.TICKS_PER_RUN:
        out.append((S.COL_TICK, f"{n} rows, expected {S.TICKS_PER_RUN} for a complete run"))
    if met[S.M_TICKS] != n:
        out.append((S.COL_TICK, f"{S.K_METRICS}.{S.M_TICKS} is {met[S.M_TICKS]}, file has {n} rows"))
    if n == 0:
        return out
    if any(b <= a for a, b in zip(cols[S.COL_TICK], cols[S.COL_TICK][1:])):
        out.append((S.COL_TICK, "is not strictly increasing"))
    for name in (S.COL_FOOD, S.COL_WASTED):  # cumulative columns
        v = cols[name]
        if any(b < a for a, b in zip(v, v[1:])):
            out.append((name, "decreases (it is cumulative)"))
    if set(cols[S.COL_MOCK]) != {int(m[S.K_MOCK])}:
        out.append((S.COL_MOCK, f"is not the constant {int(m[S.K_MOCK])} that the manifest "
                                f"{S.K_MOCK} flag says"))
    if cols[S.COL_FOOD][-1] != met[S.M_FOOD]:
        out.append((S.COL_FOOD, f"last row {cols[S.COL_FOOD][-1]} != {S.K_METRICS} {met[S.M_FOOD]}"))
    if not math.isclose(cols[S.COL_WASTED][-1], met[S.M_WASTED], abs_tol=1e-9):
        out.append((S.COL_WASTED, f"last row {cols[S.COL_WASTED][-1]} != {S.K_METRICS} "
                                  f"{met[S.M_WASTED]}"))
    state_cols = S.STATE_COUNT_COLUMNS
    if any(sum(vals) != S.N_HONEST for vals in zip(*(cols[c] for c in state_cols))):
        out.append((state_cols[0], f"state counts do not sum to {S.N_HONEST} honest robots"))
    return out


def robots_issues(header: list[str], rows: list[list[str]], n_det: int) -> list[Issue]:
    bad = header_issues(header, S.ROBOTS_COLUMNS)
    if bad:
        return bad
    cols, bad = parse_columns(rows, S.ROBOTS_TYPES)
    if bad:
        return bad
    out: list[Issue] = []
    per_tick = Counter(cols[S.COL_TICK])
    want = S.N_HONEST + n_det
    if any(c != want for c in per_tick.values()):
        out.append((S.COL_ROBOT, f"every tick must list {want} robots (20 + d, D-005)"))
    if set(cols[S.COL_ROLE]) - set(S.ROLES):
        out.append((S.COL_ROLE, f"value outside {S.ROLES}"))
    if set(cols[S.COL_STATE]) - set(S.STATES_HONEST) - set(S.STATES_DETRACTOR):
        out.append((S.COL_STATE, "value outside the known state names"))
    return out


def events_issues(header: list[str], rows: list[list[str]]) -> list[Issue]:
    bad = header_issues(header, S.EVENTS_COLUMNS)
    if bad:
        return bad
    cols, bad = parse_columns(rows, S.EVENTS_TYPES)
    if bad:
        return bad
    out: list[Issue] = []
    if set(cols.get(S.COL_EVENT, [])) - set(S.EVENT_NAMES):
        out.append((S.COL_EVENT, f"value outside {S.EVENT_NAMES}"))
    return out


def layout_problems(manifests: dict[str, dict]) -> list[Problem]:
    """DESIGN 4: one layout per seed, equal across all cells within 1e-6 m."""
    groups: dict[Any, list[str]] = defaultdict(list)
    for runid, m in manifests.items():
        groups[m[S.K_LAYOUT][S.L_SEED]].append(runid)
    out: list[Problem] = []
    for runids in groups.values():
        ref = manifests[runids[0]][S.K_LAYOUT]
        for runid in runids[1:]:
            lay = manifests[runid][S.K_LAYOUT]
            for name in (S.L_SOURCES, S.L_DECOYS):
                same = len(lay[name]) == len(ref[name]) and all(
                    abs(a - b) <= LAYOUT_TOL_M
                    for p, q in zip(lay[name], ref[name]) for a, b in zip(p, q))
                if not same:
                    out.append((runid, S.MANIFEST_FILE, f"{S.K_LAYOUT}.{name}",
                                f"differs from {runids[0]} (same layout seed)"))
    return out


# ---- I/O edge --------------------------------------------------------------------

def _read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open(newline="") as fh:
        reader = csv.reader(fh)
        return next(reader, []), list(reader)


def check_run(run_dir: Path) -> tuple[list[Problem], dict | None]:
    run, problems = run_dir.name, []

    def add(file: str, issues: list[Issue]) -> None:
        problems.extend((run, file, col, msg) for col, msg in issues)

    absent = [f for f in S.FILES if not (run_dir / f).is_file()]
    for f in absent:
        add(f, [("", "file is missing")])
    manifest = None
    if S.MANIFEST_FILE not in absent:
        try:
            manifest = json.loads((run_dir / S.MANIFEST_FILE).read_text())
        except json.JSONDecodeError as err:
            add(S.MANIFEST_FILE, [("", f"invalid JSON: {err}")])
        else:
            bad = manifest_issues(manifest, run)
            add(S.MANIFEST_FILE, bad)
            if bad:
                manifest = None
    if manifest is None:
        return problems, None
    n_det = manifest[S.K_PARAMS][S.P_NDET]
    for file, check in ((S.TICKS_FILE, lambda h, r: ticks_issues(h, r, manifest)),
                        (S.ROBOTS_FILE, lambda h, r: robots_issues(h, r, n_det)),
                        (S.EVENTS_FILE, events_issues)):
        if file not in absent:
            header, rows = _read_csv(run_dir / file)
            add(file, check(header, rows))
    return problems, manifest


def check_root(root: Path) -> tuple[list[Problem], int]:
    runs = sorted(p for p in root.iterdir() if p.is_dir())
    problems: list[Problem] = []
    manifests: dict[str, dict] = {}
    for run_dir in runs:
        bad, manifest = check_run(run_dir)
        problems += bad
        if manifest is not None:
            manifests[run_dir.name] = manifest
    return problems + layout_problems(manifests), len(runs)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", type=Path)
    ap.add_argument("--log", type=Path, help="also write the printed lines to this file")
    args = ap.parse_args(argv)
    if not args.root.is_dir():
        print(f"FAIL root {args.root} is not a folder")
        return 1
    problems, n_runs = check_root(args.root)
    lines = [f"FAIL run={r} file={f or '-'} column={c or '-'}: {msg}"
             for r, f, c, msg in problems]
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
