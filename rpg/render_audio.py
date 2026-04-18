#!/usr/bin/env python3
"""Render a built-in music track or sound effect to a WAV file."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rpg_battle.cli.render_audio import main


if __name__ == "__main__":
    main()
