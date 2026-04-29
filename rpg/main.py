#!/usr/bin/env python3
"""Run the game without installing the project.

Usage:

    python main.py

This works straight from the project folder so you can play before
learning about ``pip install -e .`` and packaging. It adds the local
``src/`` directory to ``sys.path`` so imports resolve without an install.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


DEPENDENCIES = ["pygame>=2.5", "numpy>=1.24", "loguru>=0.7", "rich>=13.7"]


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
    from rpg_battle.__main__ import main
except ModuleNotFoundError as exc:
    _missing_dependency(exc)


if __name__ == "__main__":
    main()
