from __future__ import annotations

"""Shared helpers for lightweight development render commands."""

import os
from pathlib import Path

import pygame
from loguru import logger

from rpg_battle.audio.engine import AudioEngine
from rpg_battle.settings import SCREEN_HEIGHT, SCREEN_WIDTH


def configure_headless_pygame() -> None:
    """Configure pygame to run without opening a real window or audio device."""

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def init_surface(width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT) -> pygame.Surface:
    """Initialize pygame and return an offscreen surface for rendering."""

    configure_headless_pygame()
    pygame.init()
    return pygame.Surface((width, height))


def make_audio() -> AudioEngine:
    """Return a quiet audio engine suitable for headless development renders."""

    audio = AudioEngine()
    audio.initialize()
    audio.stop_music()
    return audio


def save_surface(surface: pygame.Surface, output: str | Path) -> Path:
    """Write a surface to disk and log the destination."""

    output_path = Path(output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, output_path)
    logger.info("Saved render to {}", output_path)
    return output_path
