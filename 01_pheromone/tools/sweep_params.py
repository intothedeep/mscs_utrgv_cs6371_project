"""Names of the tunable .argos values: where each lives and how it shows up in a manifest.

One table, so make_sweep, the tuning scripts and the sweep skip check agree.
Manifest params keep every .argos value: loop-function attributes under their own name,
controller attributes as controller_<node>_<attribute> (run_info_reader.cpp).
"""
from __future__ import annotations

__all__ = ["Override", "PARAM_SITES", "overrides", "manifest_key", "parse_seeds"]

Override = tuple[str, str, str]  # (element path from <argos-configuration>, attribute, value)

_LF = "loop_functions/pheromone"
_CTRL = "controllers/pheromone_forager_controller/params"
PARAM_SITES: dict[str, tuple[str, str]] = {
    "half_life_s": (_LF, "half_life_s"),
    "lambda_dep": (f"{_CTRL}/pheromone", "lambda_dep"),
    "follow_enabled": (f"{_CTRL}/pheromone", "follow_enabled"),
    "t_end": (f"{_CTRL}/pheromone", "t_end"),
    "r_suspect": (f"{_CTRL}/defense", "r_suspect"),
    "alpha_cone_deg": (f"{_CTRL}/defense", "alpha_cone_deg"),
    "d_cone": (f"{_CTRL}/defense", "d_cone"),
    "enabled": (f"{_CTRL}/defense", "enabled"),
    "t_lock": (f"{_CTRL}/defense", "t_lock"),  # v4 lockout seconds (D-028)
}


def overrides(**values: float | str) -> tuple[Override, ...]:
    """Values by short name. Numbers are written with :g, so 0.077 stays 0.077."""
    return tuple((*PARAM_SITES[name], f"{v:g}" if isinstance(v, float) else str(v))
                 for name, v in values.items())


def manifest_key(name: str) -> str:
    path, attr = PARAM_SITES[name]
    return attr if path == _LF else f"controller_{path.rsplit('/', 1)[1]}_{attr}"




def parse_seeds(text: str) -> tuple[int, ...]:
    """'a-b' -> seeds a to b inclusive. D-030: the seed range is a CLI option, not a schema column."""
    try:
        first, last = (int(v) for v in text.split("-"))
    except ValueError:
        raise ValueError("use a-b, for example 11-30")
    if first < 1 or last < first:
        raise ValueError("seeds need 1 <= a <= b")
    return tuple(range(first, last + 1))
