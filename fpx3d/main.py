#!/usr/bin/env python3
"""Run the game without installing the project.

Usage:

    python main.py

This works straight from the project folder so you can play before
learning about ``pip install -e .`` and packaging.
"""

from __future__ import annotations

import sys

DEPENDENCIES = ["panda3d>=1.10.15"]


def _missing_dependency(exc: ModuleNotFoundError) -> None:
    print(f"ERROR: Missing Python package '{exc.name}'.", file=sys.stderr)
    print(file=sys.stderr)
    print("This game needs the following packages installed:", file=sys.stderr)
    for dep in DEPENDENCIES:
        print(f"  - {dep}", file=sys.stderr)
    print(file=sys.stderr)
    print("Install them with:", file=sys.stderr)
    quoted = " ".join(f"'{dep}'" for dep in DEPENDENCIES)
    print(f"  pip install {quoted}", file=sys.stderr)
    sys.exit(1)


try:
    from fpx3d.game import main
except ModuleNotFoundError as exc:
    _missing_dependency(exc)


if __name__ == "__main__":
    main()
