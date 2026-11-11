"""Write the two Qt demo files (d = 2, defense off and on) and capture frames from them (M3-06).

Usage: make_demo.py [--capture [--timeout S]]
Writes src/experiments/pheromone_qt_d2_def0.argos and pheromone_qt_d2_def1.argos from
pheromone_qt.argos, with the frozen values (tuning_pick.json, defense_pick.json), seed 1,
and a <frame_grabbing> block. They write no run log.
--capture runs each demo headless-grabbing from src/ and downscales the frames with sips
into results/real/mvp3/demo/. The Qt window may stay open after the experiment ends, so a
timeout is the normal end of a capture: the frames written so far are kept.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from make_sweep import SRC, add_detractors, load_template, set_attr
from run_results import PROJECT
from sweep_params import overrides
from sweep_plan import frozen_values

DEMO_SEED = 1
DEMO_D = 2
QT_TEMPLATE = SRC / "experiments" / "pheromone_qt.argos"
FRAMES = PROJECT / "runs" / "demo"           # raw frames, git-ignored
OUT = PROJECT / "results" / "real" / "mvp3" / "demo"
FRAME_EVERY_TICKS = 300                       # 6000 ticks give 20 frames
DEFAULT_TIMEOUT_S = 300


def demo_name(defense: int) -> str:
    return f"pheromone_qt_d{DEMO_D}_def{defense}"


def write_demo(defense: int, values: dict[str, float]) -> Path:
    tree = load_template(QT_TEMPLATE)
    set_attr(tree, "framework/experiment", "random_seed", str(DEMO_SEED))
    set_attr(tree, "loop_functions/pheromone", "n_det", str(DEMO_D))
    set_attr(tree, "loop_functions/pheromone", "defense", str(defense))
    set_attr(tree, "controllers/pheromone_forager_controller/params/defense", "enabled",
             "true" if defense else "false")
    for path, name, value in overrides(**values):
        set_attr(tree, path, name, value)
    add_detractors(tree, DEMO_D)
    qt = tree.getroot().find("visualization/qt-opengl")
    if qt is None:
        raise SystemExit("stop: pheromone_qt.argos has no <qt-opengl>")
    qt.set("autoplay", "true")
    ET.SubElement(qt, "frame_grabbing", {
        "directory": str(FRAMES / demo_name(defense)), "base_name": "frame_",
        "headless_grabbing": "true", "headless_frame_size": "1000x1000",
        "headless_frame_rate": str(FRAME_EVERY_TICKS)})
    ET.indent(tree)
    out = SRC / "experiments" / f"{demo_name(defense)}.argos"
    out.write_text('<?xml version="1.0" ?>\n' + ET.tostring(tree.getroot(), encoding="unicode") + "\n")
    return out


def capture(defense: int, timeout_s: int) -> None:
    frames = FRAMES / demo_name(defense)
    frames.mkdir(parents=True, exist_ok=True)
    print(f"capture {demo_name(defense)} (timeout {timeout_s} s)", flush=True)
    try:
        subprocess.run(["argos3", "-c", f"experiments/{demo_name(defense)}.argos"], cwd=SRC,
                       capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        pass  # the window stays open after the experiment ends: the timeout ends the capture
    shots = sorted(frames.glob("*.png"))
    if not shots:
        raise SystemExit(f"stop: no frame in {frames}")
    OUT.mkdir(parents=True, exist_ok=True)
    for i, shot in enumerate(shots):
        dest = OUT / f"d{DEMO_D}_def{defense}_{i:02d}.png"
        subprocess.run(["sips", "-Z", "900", str(shot), "--out", str(dest)], check=True, capture_output=True)
    print(f"{len(shots)} frames -> {OUT}")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    args = ap.parse_args(argv)
    values = frozen_values()
    for defense in (0, 1):
        print(f"wrote {write_demo(defense, values)}")
    if args.capture:
        for defense in (0, 1):
            capture(defense, args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
