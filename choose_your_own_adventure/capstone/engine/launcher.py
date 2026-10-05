"""Choose the capstone frontend without coupling it to game rules."""

from __future__ import annotations

import argparse
import importlib.util

from .console import run_console
from .game import AdventureGame


def textual_available() -> bool:
    return importlib.util.find_spec("textual") is not None


def run_game(game: AdventureGame, argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--ui",
        choices=("auto", "textual", "console"),
        default="auto",
        help="frontend to use (default: Textual when installed, otherwise console)",
    )
    args = parser.parse_args(argv)

    has_textual = textual_available()
    if args.ui == "textual" and not has_textual:
        parser.error(
            "Textual is not installed. Install it with 'python -m pip install textual' "
            "or run with '--ui console'."
        )

    use_textual = args.ui == "textual" or (args.ui == "auto" and has_textual)
    if use_textual:
        from .textual_app import run_textual

        run_textual(game)
    else:
        if args.ui == "auto" and not has_textual:
            print("Textual is not installed; using the console UI.")
            print("For the full capstone interface: python -m pip install textual")
        run_console(game)
