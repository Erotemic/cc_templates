#!/usr/bin/env python3
"""Run Peakshift from its folder, with no editable install required."""

from __future__ import annotations

import argparse
import sys

from peakshift.app import run_graphical, run_headless
from peakshift.levels import ROOMS


def main(argv=None):
    parser = argparse.ArgumentParser(description="Peakshift classroom game")
    parser.add_argument("--headless", action="store_true", help="physics only, no pygame needed")
    parser.add_argument("--frames", type=int, default=0, help="quit after N frames")
    parser.add_argument("--screenshot", help="save the last frame to this PNG")
    parser.add_argument("--room", choices=tuple(ROOMS), help="begin at this authored room")
    args = parser.parse_args(argv)
    if args.frames < 0:
        parser.error("--frames cannot be negative")
    if args.headless:
        if args.screenshot:
            parser.error("--screenshot requires graphical mode")
        return run_headless(args.frames or 240, room=args.room)
    try:
        return run_graphical(frames=args.frames, screenshot=args.screenshot, room=args.room)
    except ModuleNotFoundError as exc:
        if exc.name == "pygame":
            print("Install pygame: python -m pip install pygame-ce", file=sys.stderr)
            return 1
        raise


if __name__ == "__main__":
    raise SystemExit(main())
