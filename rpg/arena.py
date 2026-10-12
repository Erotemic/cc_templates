#!/usr/bin/env python3
"""Friendly entry point for the student team-controller competition.

From the rpg directory:
    python arena.py list
    python arena.py battle my_team first_target --log
    python arena.py challenge my_team
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from team_arena.cli import main

if __name__ == "__main__":
    main()
