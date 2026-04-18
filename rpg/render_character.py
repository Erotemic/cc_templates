#!/usr/bin/env python3
"""Render one classroom RPG character sprite to a PNG preview."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rpg_battle.cli.render_character import main


if __name__ == "__main__":
    main()
