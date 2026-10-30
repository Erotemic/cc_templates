"""Command-line entry point; --headless works WITHOUT installing Panda3D."""

from __future__ import annotations

import argparse
import sys


def run_headless(frames: int) -> int:
    from .engine import Controls, State, objective_hint, step
    state = State()
    for frame in range(frames):
        # Deliberately simple input, not a bot that solves the vault.
        step(state, Controls(forward=1.0 if frame < 150 else 0), 1 / 60)
    print(f"frames={frames} prisms={state.cores_collected}/{state.cores_needed} "
          f"bonus={state.bonus_points} hp={state.hearts} "
          f"time={state.time_left:.1f} pos=({state.player.x:.1f},"
          f"{state.player.y:.1f},{state.player.z:.1f}) "
          f"objective={objective_hint(state)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prism Vault first-person 3D game")
    parser.add_argument("--headless", action="store_true",
                        help="test gameplay without Panda3D or a window")
    parser.add_argument("--frames", type=int, default=0,
                        help="end automatically after N frames")
    parser.add_argument("--screenshot", metavar="PNG",
                        help="save a screenshot on the last graphical frame")
    args = parser.parse_args(argv)
    if args.frames < 0:
        parser.error("--frames cannot be negative")
    if args.headless:
        if args.screenshot:
            parser.error("--screenshot requires graphical mode")
        return run_headless(args.frames or 240)
    if args.screenshot and args.frames == 0:
        parser.error("--screenshot requires --frames")
    try:
        from .game import run
    except ModuleNotFoundError as err:
        if err.name in {"panda3d", "direct"} or err.name.startswith("direct."):
            print("Panda3D is required for graphical play. Try:", file=sys.stderr)
            print("  python -m pip install 'panda3d>=1.10.15'", file=sys.stderr)
            return 1
        raise
    run(frames=args.frames, screenshot=args.screenshot)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
