#!/usr/bin/env python3
"""Top-level runner for the classroom RPG project.

This lets students launch the game from the project root with:

    python run_game.py

It adds the local ``src/`` directory to ``sys.path`` so the project can be run
without first installing the package into a virtual environment.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rpg_battle.__main__ import main


if __name__ == "__main__":
    main()
