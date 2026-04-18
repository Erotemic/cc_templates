from __future__ import annotations

"""Shared render helpers used by the CLI tools."""

from pathlib import Path

import pygame
from loguru import logger

from rpg_battle.audio.engine import AudioEngine
from rpg_battle.cli.common import configure_headless_pygame, ensure_output_path
from rpg_battle.settings import SCREEN_HEIGHT, SCREEN_WIDTH


def init_surface(
    width: int = SCREEN_WIDTH,
    height: int = SCREEN_HEIGHT,
    *,
    headless: bool = True,
) -> pygame.Surface:
    """Initialize pygame and return a surface for rendering.

    In headless mode this returns an offscreen ``Surface``. Otherwise it opens a
    small standalone window so students can see the rendered result right away.
    """

    if headless:
        configure_headless_pygame()
    pygame.init()
    if headless:
        return pygame.Surface((width, height))
    screen = pygame.display.set_mode((width, height))
    return screen


def make_audio() -> AudioEngine:
    """Return a quiet audio engine suitable for development renders."""

    audio = AudioEngine()
    audio.initialize()
    audio.stop_music()
    return audio


def save_surface(surface: pygame.Surface, output: str | Path) -> Path:
    """Write a surface to disk and log the destination."""

    output_path = ensure_output_path(output)
    pygame.image.save(surface, output_path)
    logger.info("Saved render to {}", output_path)
    return output_path


def show_surface(surface: pygame.Surface, *, title: str = "RPG Battle Preview") -> None:
    """Display a rendered surface until the user closes the window.

    This intentionally uses a tiny blocking loop because these tools are meant
    for quick visual inspection rather than interactive editing.
    """

    pygame.display.set_caption(title)
    screen = pygame.display.get_surface()
    if screen is None or screen.get_size() != surface.get_size():
        screen = pygame.display.set_mode(surface.get_size())
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in {
                pygame.K_ESCAPE,
                pygame.K_RETURN,
                pygame.K_SPACE,
            }:
                running = False
        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(30)
