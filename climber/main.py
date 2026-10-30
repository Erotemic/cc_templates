#!/usr/bin/env python3
"""Launch with ``python main.py``. No editable install or asset downloads."""

from __future__ import annotations

import argparse
import sys

from climber.game import run_graphical, run_headless


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Infinity Climber")
    parser.add_argument("--headless", action="store_true",
                        help="run a short simulation without pygame")
    parser.add_argument("--frames", type=int, default=0,
                        help="close automatically after N frames")
    parser.add_argument("--screenshot", metavar="PNG",
                        help="save last graphical frame to a PNG file")
    args = parser.parse_args(argv)
    if args.frames < 0:
        parser.error("--frames must be nonnegative")
    if args.headless:
        if args.screenshot:
            parser.error("--screenshot requires the graphical mode")
        return run_headless(args.frames or 240)
    try:
        return run_graphical(frames=args.frames, screenshot=args.screenshot)
    except ModuleNotFoundError as error:
        if error.name == "pygame":
            print("This game needs pygame. Try: python -m pip install pygame-ce",
                  file=sys.stderr)
            return 1
        raise


if __name__ == "__main__":
    raise SystemExit(main())
