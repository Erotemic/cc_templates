from __future__ import annotations

import os
import sys

from loguru import logger


def configure_logging() -> None:
    """Configure a friendly terminal logger for classroom debugging.

    The format is intentionally short enough for students to scan while they are
    stepping through the battle loop in a terminal.
    """
    logger.remove()
    level = os.environ.get("RPG_BATTLE_LOG_LEVEL", "INFO").upper()
    logger.add(
        sys.stderr,
        level=level,
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
    )
