#!/usr/bin/env python3
"""UnderCode launcher. Read undercode/runtime.py for input → update → draw."""

import argparse
import os
from pathlib import Path


def main(argv=None):
    """Select a learning mode or a check, then delegate to its engine/window adapter."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--overworld", action="store_true", help="Work on rooms without loading encounters"
    )
    mode.add_argument(
        "--encounter", metavar="KEY", help="Work on one opponent without loading rooms"
    )
    mode.add_argument(
        "--practice", metavar="PATTERN", help="Work on a defense without loading rooms"
    )
    parser.add_argument("--level", help="Start the overworld in this room")
    parser.add_argument("--entry", help="Choose its named arrival marker")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--check", action="store_true", help="Check engine/content health; not exercise completion"
    )
    parser.add_argument(
        "--check-exercise", choices=("facing", "sprint", "healing", "pulse", "tactics", "all")
    )
    parser.add_argument(
        "--check-sprites", action="store_true", help="Shortcut for --check-exercise facing"
    )
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--mute", action="store_true")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args(argv)
    if args.frames is not None and args.frames <= 0:
        parser.error("--frames must be positive")
    if args.entry and not args.level:
        parser.error("--entry needs --level")
    if args.level and (args.encounter or args.practice):
        parser.error("--level belongs to the overworld")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    try:
        if args.check_sprites or args.check_exercise:
            from undercode.exercises import check_exercises

            return check_exercises(exercise=args.check_exercise or "facing")
        if args.list or args.check:
            from undercode.checks import check_or_list

            return check_or_list(
                listed=args.list,
                world_only=args.overworld,
                encounters_only=bool(args.encounter or args.practice),
            )
        from undercode.app import Game
        from undercode.runtime import run

        game = Game(
            seed=args.seed,
            encounter=args.encounter,
            practice=args.practice,
            level=args.level,
            entry=args.entry,
        )
    except ImportError as error:
        if error.name == "pygame":
            raise SystemExit(
                "UnderCode needs pygame. Use an existing install or run: python -m pip install pygame-ce"
            ) from error
        raise
    except ValueError as error:
        parser.error(str(error))

    # Once play starts, preserve student-code tracebacks instead of treating
    # gameplay exceptions as malformed command-line arguments.
    return run(
        game=game,
        headless=args.headless,
        mute=args.mute,
        frames=args.frames,
        screenshot=args.screenshot,
    )


if __name__ == "__main__":
    raise SystemExit(main())
