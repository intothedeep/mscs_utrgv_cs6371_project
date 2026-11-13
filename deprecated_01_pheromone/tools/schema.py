"""Single Python copy of the log schema (DESIGN.md section 4, schema_version 1).

Why one copy: mock and real runs write the same files, and every tool reads the
column names from here. A renamed column then fails in one place.
"""
from __future__ import annotations

import re

__all__ = [
    "SCHEMA_VERSION", "TICKS_PER_RUN", "TICKS_PER_SECOND", "N_HONEST", "MOCK_PREFIX",
    "FILES", "MANIFEST_FILE", "TICKS_FILE", "ROBOTS_FILE", "EVENTS_FILE",
    "TICKS_TYPES", "TICKS_COLUMNS", "STATE_COUNT_COLUMNS", "ROBOTS_TYPES", "ROBOTS_COLUMNS",
    "EVENTS_TYPES", "EVENTS_COLUMNS", "EVENT_NAMES",
    "MANIFEST_KEYS", "CODE_SHA_KEYS", "PARAM_KEYS", "LAYOUT_KEYS", "ENV_KEYS", "METRICS_KEYS",
    "K_SCHEMA", "K_MOCK", "K_RUNID", "K_PARAMS", "K_LAYOUT", "K_METRICS",
    "P_NDET", "P_DEFENSE", "P_SEED", "P_LENGTH", "L_SEED", "L_SOURCES", "L_DECOYS", "L_NUSED",
    "M_FOOD", "M_WASTED", "M_TICKS", "M_COMPLETE",
    "COL_TICK", "COL_FOOD", "COL_WASTED", "COL_MOCK", "COL_ROBOT", "COL_ROLE", "COL_STATE",
    "COL_EVENT", "ROLES", "STATES_HONEST", "STATES_DETRACTOR",
    "DETRACTOR_COUNTS", "DEFENSES", "SEEDS", "DECOYS_USED", "RUNID_RE",
]

SCHEMA_VERSION = 1
TICKS_PER_SECOND = 10
TICKS_PER_RUN = 600 * TICKS_PER_SECOND  # length 600 s (DESIGN Table 2)
N_HONEST = 20                           # detractors are added to these (D-005)
MOCK_PREFIX = "MOCK_"

MANIFEST_FILE, TICKS_FILE, ROBOTS_FILE, EVENTS_FILE = (
    "manifest.json", "ticks.csv", "robots.csv", "events.csv")
FILES = (MANIFEST_FILE, TICKS_FILE, ROBOTS_FILE, EVENTS_FILE)

# Column names that tools read by name (everything else is only iterated).
COL_TICK, COL_FOOD, COL_WASTED, COL_MOCK = (
    "tick", "food_collected", "wasted_robot_seconds", "mock")
COL_ROBOT, COL_ROLE, COL_STATE, COL_EVENT = "robot_id", "role", "state", "event"

# Table 3: ticks.csv, one row per tick. Dict order is the column order.
TICKS_TYPES: dict[str, type] = {
    COL_TICK: int, COL_FOOD: int, COL_WASTED: float,
    "n_rest": int, "n_search": int, "n_follow": int, "n_end": int, "n_return": int,
    "pher_true_sum": float, "pher_false_sum": float, "suspects_total": int,
    COL_MOCK: int,
}
TICKS_COLUMNS = tuple(TICKS_TYPES)
STATE_COUNT_COLUMNS = tuple(c for c in TICKS_COLUMNS if c.startswith("n_"))  # honest robots per state

# Table 4: the other two files.
ROBOTS_TYPES: dict[str, type] = {
    COL_TICK: int, COL_ROBOT: str, COL_ROLE: str, "x": float, "y": float,
    "yaw_deg": float, COL_STATE: str, "carrying": int, "here": float, "false_share": float,
}
ROBOTS_COLUMNS = tuple(ROBOTS_TYPES)
EVENTS_TYPES: dict[str, type] = {
    COL_TICK: int, COL_ROBOT: str, COL_EVENT: str, "x": float, "y": float,
}
EVENTS_COLUMNS = tuple(EVENTS_TYPES)
EVENT_NAMES = ("pickup", "drop", "follow_start", "peak", "suspect_add", "cone_abort",
               "decoy_reach")

ROLES = ("honest", "detractor")  # role prefixes hb_ and dt_ (DESIGN 2.1)
STATES_HONEST = ("REST", "SEARCH", "FOLLOW", "END_SEARCH", "RETURN")
# DESIGN 3.3: REST, GO_DECOY, wait 2 s at the decoy, RETURN_LAY. The wait gets its own name.
STATES_DETRACTOR = ("REST", "GO_DECOY", "WAIT_DECOY", "RETURN_LAY")

# manifest.json (DESIGN section 4). Tuples are the exact key sets.
K_SCHEMA, K_MOCK, K_RUNID, K_PARAMS, K_LAYOUT, K_METRICS = (
    "schema_version", "mock", "runid", "params", "layout", "metrics")
MANIFEST_KEYS = (K_SCHEMA, K_MOCK, K_RUNID, "code_version", "code_sha", "git_commit",
                 "git_dirty", K_PARAMS, K_LAYOUT, "env", K_METRICS)
CODE_SHA_KEYS = ("loop_functions", "controller")
P_NDET, P_DEFENSE, P_SEED, P_LENGTH = "n_det", "defense", "seed", "length_s"
PARAM_KEYS = (P_NDET, P_DEFENSE, P_SEED, P_LENGTH)  # required; real runs add every .argos value
L_SEED, L_SOURCES, L_DECOYS, L_NUSED = "layout_seed", "sources", "decoys", "n_decoys_used"
LAYOUT_KEYS = (L_SEED, L_SOURCES, L_DECOYS, L_NUSED, "radius_m")
ENV_KEYS = ("machine", "argos", "threads")
M_FOOD, M_WASTED, M_TICKS, M_COMPLETE = (
    COL_FOOD, COL_WASTED, "ticks", "complete")  # metrics must equal the last ticks.csv row
METRICS_KEYS = (M_FOOD, M_WASTED, M_TICKS, M_COMPLETE)

# The 8 cells x 10 seeds of G1, and decoys used per detractor count (D-009).
DETRACTOR_COUNTS = (0, 1, 2, 4)
DEFENSES = (0, 1)
SEEDS = tuple(range(1, 11))
DECOYS_USED = {0: 0, 1: 1, 2: 2, 4: 2}

RUNID_RE = re.compile(
    rf"^(?P<prefix>{MOCK_PREFIX})?(?P<stamp>\d{{8}}-\d{{6}})"
    r"_d(?P<d>\d+)_def(?P<defense>[01])_s(?P<seed>\d+)$")
