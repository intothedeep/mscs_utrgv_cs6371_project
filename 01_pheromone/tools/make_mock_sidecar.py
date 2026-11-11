"""MOCK sidecar generator (M6 U5, DESIGN_M6 section 5). Every value is invented. Nothing is simulated.

Writes defense_log.csv into the MOCK runs of mock/runs/ with defense 1 and d in 0, 2 (seeds 1-10), so the
arm table and the judge can run before the real id arm exists (MVP1). Robot ids carry the MOCK_ prefix.
Safety: writes only under mock/runs/. A run folder that is not a MOCK run stops it. Deterministic.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

import schema as S
from run_results import PROJECT
from v6_sidecar import COLUMNS, SIDECAR_FILE

MOCK_ROOT = PROJECT / "mock" / "runs"
GEN_SEED = 20261111
LAST_TICK = S.TICKS_PER_RUN


def rows_for(d: int, seed: int) -> list[list]:
    rng = np.random.default_rng([GEN_SEED, seed, d])
    robots = [(f"MOCK_hb_{i}", "honest") for i in range(S.N_HONEST)] + [(f"MOCK_dt_{i}", "detractor") for i in range(d)]
    isolated: dict[str, int] = {}
    rows: list[list] = []
    for rid, role in robots:
        p = 0.8 if role == "detractor" else 0.1 if d == 0 else 0.0  # fake: detractors mostly isolated, honest rarely at d = 0
        if rng.random() < p:
            tick = int(rng.integers(600, LAST_TICK - 1200))
            isolated[rid] = tick
            rows.append([tick, rid, role, "isolate", 0, 5, 1, 1, "", tick - 50, "peak", int(rng.integers(5, 60)), 0.0, 0.0])
    for rid, role in robots:
        rows.append([LAST_TICK, rid, role, "end_state", -1, 0, int(rid in isolated and isolated[rid] > LAST_TICK - 1200),
                     0, "", -1, "", 0, 0.0, 0.0])
    return sorted(rows, key=lambda r: r[0])


def main() -> int:
    n = 0
    for run in sorted(MOCK_ROOT.iterdir()):
        manifest = json.loads((run / S.MANIFEST_FILE).read_text())
        p = manifest[S.K_PARAMS]
        if manifest[S.K_MOCK] is not True or not run.name.startswith(S.MOCK_PREFIX):
            raise SystemExit(f"stop: {run.name} is not a MOCK run")
        if int(p[S.P_DEFENSE]) != 1 or int(p[S.P_NDET]) not in (0, 2):
            continue
        with (run / SIDECAR_FILE).open("w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(COLUMNS)
            w.writerows(rows_for(int(p[S.P_NDET]), int(p[S.P_SEED])))
        n += 1
    print(f"wrote {n} MOCK sidecars under {MOCK_ROOT.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
