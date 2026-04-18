#!/usr/bin/env python3
"""Render a battle scene preview to a PNG for layout inspection."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rpg_battle.cli.render_battle_state import main


if __name__ == "__main__":
    main()
