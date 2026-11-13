"""Single Python copy of the run schema (DESIGN.md sections 5.1, 6.4, 6.5; schema_version 1).

Why one copy: mock and real runs write the same files, and every tool reads the
names from here. A renamed column then fails in one place. Tools never type a
column or key as a string. They read it as an attribute: `S.C.arm`, `S.Q.branch`.
"""
from __future__ import annotations

import re
from types import SimpleNamespace

__all__ = [
    "SCHEMA_VERSION", "SIM_SECONDS", "MOCK_PREFIX", "MOCK_MARK", "METRICS_TAG",
    "ARMS", "ABLATION_ARM_PREFIX", "DISTRIBUTIONS", "DISTRIBUTION_CODES", "BRANCHES",
    "SETS", "SET_CELLS", "LAYOUT_SETS",
    "RUN_FILES", "FILE_ARGOS", "FILE_STDOUT", "FILE_MANIFEST", "FILE_FORAGE", "FILE_QUERIES",
    "FILE_POINTS", "HEADER_ONLY_ARMS",
    "RUNS_COLUMNS", "QUERIES_COLUMNS", "QUERIES_TYPES", "QUERIES_REQUIRED",
    "FORAGE_COLUMNS", "POINTS_COLUMNS", "POINTS_TYPES",
    "MANIFEST_KEYS", "LIB_SHA_KEYS", "ENV_KEYS", "PARAM_KEYS", "METRICS_KEYS",
    "SHARE_COLUMN_OF_BRANCH", "QUERY_ANSWER_BRANCHES",
    "C", "Q", "F", "P", "K", "L", "E", "PA", "MT",
    "SCORE_PATTERN", "RUNID_PATTERN", "parse_score", "parse_runid", "KIND_MOCK", "KIND_REAL",
]

SCHEMA_VERSION = 1
SIM_SECONDS = 720                 # MaxSimTimeInSeconds (DESIGN 6.1)
MOCK_PREFIX = "MOCK_"             # runid prefix of every mock run
KIND_MOCK, KIND_REAL = "mock", "real"   # folder names: mock/runs, results/mock, results/real
MOCK_MARK = "MOCK"                # value of every mock string that would be a hash or a name
METRICS_TAG = "IS_METRICS"        # prefix of the one stdout line our build prints with run totals

ARMS = ("vendor", "cpfa", "qmap")
ABLATION_ARM_PREFIX = "qmap-"     # arm = qmap-<ablation> in S5
DISTRIBUTIONS = ("random", "powerlaw", "clustered")
DISTRIBUTION_CODES = {"random": 0, "clustered": 1, "powerlaw": 2}  # xml10 FoodDistribution
BRANCHES = ("fidelity", "pheromone", "map", "fallback_random", "random")

# Sets of PLAN "Fixed paths". Each has its own run root under runs/ (or mock/runs/).
SETS = ("S0", "S0det", "S0v2", "S1", "S2", "S3", "S4", "S5", "SMK")
# Cells DESIGN 6.1 fixes: arms and seeds per set, for all 3 distributions. S0det repeats a
# cell on purpose. S2 and S5 have no fixed cell list. They are absent here.
SET_CELLS: dict[str, tuple[tuple[str, ...], range]] = {
    "S0": (("vendor", "cpfa"), range(3001, 3006)),
    "S0v2": (("vendor", "cpfa"), range(3001, 3006)),
    "S1": (("cpfa",), range(1001, 1031)),
    "S3": (("cpfa", "qmap"), range(2001, 2051)),
    "S4": (("cpfa", "qmap"), range(2001, 2051)),
    "SMK": (("qmap",), range(1001, 1002)),
}
LAYOUT_SETS = ("S3", "S4")        # DESIGN 6.6 items 5 and 6

# DESIGN 6.4: the 6 files of one run folder.
FILE_ARGOS, FILE_STDOUT, FILE_MANIFEST = "run.argos", "stdout.log", "manifest.json"
FILE_FORAGE, FILE_QUERIES, FILE_POINTS = "forage_per_minute.csv", "queries.csv", "points.csv"
RUN_FILES = (FILE_ARGOS, FILE_STDOUT, FILE_MANIFEST, FILE_FORAGE, FILE_QUERIES, FILE_POINTS)
# A file with a header and no row is valid only for these arms (D-014, D-015).
HEADER_ONLY_ARMS = {FILE_QUERIES: ("vendor",), FILE_POINTS: ("vendor", "cpfa")}


def _names(names: tuple[str, ...]) -> SimpleNamespace:
    """Attribute access to a name list. A name missing from the list raises AttributeError."""
    return SimpleNamespace(**{n: n for n in names})


# DESIGN 6.5, table order.
RUNS_COLUMNS = (
    "schema_version", "mock", "run_id", "set", "arm", "distribution", "seed",
    "collected", "sim_time_s", "complete", "code_commit", "git_dirty",
    "lib_sha_controller", "lib_sha_loop", "nest_radius_xml", "nest_radius_eff", "layout_sha",
    "n_departures", "share_fidelity", "share_pheromone", "share_map", "share_random",
    "travel_s", "search_s", "n_queries", "points_inserted", "nodes_total_end",
    "leaves_total_end", "ops_per_query_median", "ops_per_query_max", "us_per_query_median",
    "targets_reached_share", "wall_s",
)

# DESIGN 5.1. Cost and target columns stay empty on rows that ran no map query.
QUERIES_TYPES: dict[str, type] = {
    "t_s": float, "robot": str, "branch": str, "nodes_visited": int, "nodes_total": int,
    "leaves_total": int, "points_inserted_total": int, "query_us": float, "target_x": float,
    "target_y": float, "dist_m": float, "reached": int,
}
QUERIES_COLUMNS = tuple(QUERIES_TYPES)
QUERIES_REQUIRED = ("t_s", "robot", "branch")
FORAGE_COLUMNS = ("minute", "collected")   # collected is cumulative at the end of the minute
POINTS_TYPES: dict[str, type] = {"t_s": float, "robot": str, "x": float, "y": float}
POINTS_COLUMNS = tuple(POINTS_TYPES)

# DESIGN 6.4 plus rules/measurement.md 2.1 (code_version, code_sha, params, env, metrics).
# Keys that sit in the single-run summary reuse its name. Run id comes from the folder name.
MANIFEST_KEYS = (
    "schema_version", "mock", "set", "arm", "distribution", "seed",
    "git_commit", "git_dirty", "lib_sha", "xml_sha", "prereg_sha",
    "nest_radius_xml", "nest_radius_eff", "respawn", "param_set", "layout_sha", "wall_s",
    "code_version", "code_sha", "params", "env", "metrics",
)
LIB_SHA_KEYS = ("controller", "loop")
ENV_KEYS = ("machine", "argos", "threads")
PARAM_KEYS = ("random_seed", "max_sim_time_s", "food_distribution")  # runs may add more
# Totals the harness takes from the score line and the METRICS_TAG line. None = not printed.
METRICS_KEYS = ("collected", "sim_time_s", "complete", "n_departures", "travel_s", "search_s")

# Branch value -> share column. A failed map query ends in a random target, so it counts
# as random: the four shares then sum to 1. Open question to the architect (hand-back).
SHARE_COLUMN_OF_BRANCH = {
    "fidelity": "share_fidelity", "pheromone": "share_pheromone", "map": "share_map",
    "fallback_random": "share_random", "random": "share_random",
}
QUERY_ANSWER_BRANCHES = ("map", "fallback_random")  # rows where the map was asked

C, Q, F, P = (_names(RUNS_COLUMNS), _names(QUERIES_COLUMNS), _names(FORAGE_COLUMNS),
              _names(POINTS_COLUMNS))
K, L, E, PA, MT = (_names(MANIFEST_KEYS), _names(LIB_SHA_KEYS), _names(ENV_KEYS),
                   _names(PARAM_KEYS), _names(METRICS_KEYS))

# DESIGN 6.4. Groups: 1 score, 2 simulated seconds, 3 random seed. The METRICS_TAG line starts
# with letters, so it cannot match.
SCORE_PATTERN = re.compile(r"^\s*([0-9.]+), ([0-9.]+), (\d+)\s*$", re.MULTILINE)
RUNID_PATTERN = re.compile(
    rf"^(?P<mock>{MOCK_PREFIX})?(?P<stamp>\d{{8}}-\d{{6}})_(?P<arm>[a-z0-9-]+)"
    rf"_(?P<distribution>{'|'.join(DISTRIBUTIONS)})_s(?P<seed>\d+)$")


def parse_score(text: str) -> tuple[int, float, int] | None:
    """(collected, sim seconds, seed) of the last score line in stdout, or None."""
    found = SCORE_PATTERN.findall(text)
    if not found:
        return None
    score, sim_time, seed = found[-1]
    return round(float(score)), float(sim_time), int(seed)


def parse_runid(name: str) -> tuple[bool, str, str, str, int] | None:
    """(is_mock, stamp, arm, distribution, seed) of a run folder name, or None."""
    m = RUNID_PATTERN.match(name)
    if m is None:
        return None
    return bool(m["mock"]), m["stamp"], m["arm"], m["distribution"], int(m["seed"])
