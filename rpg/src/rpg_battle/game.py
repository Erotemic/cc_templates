from __future__ import annotations

from typing import Final

import pygame
from loguru import logger

from rpg_battle.audio.engine import AudioEngine
from rpg_battle.battle.battle_scene import BattleScene
from rpg_battle.core.models import EncounterSpec
from rpg_battle.settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE

DEFAULT_WINDOW_SIZE: Final[tuple[int, int]] = (SCREEN_WIDTH, SCREEN_HEIGHT)


def run_game(*, encounter: EncounterSpec | None = None, title: str = TITLE) -> None:
    """Run the main pygame loop for the battle scene.

    Parameters
    ----------
    encounter:
        Optional encounter override assembled by the top-level CLI.
    title:
        Window title. The CLI can change this when launching alternate setups.
    """

    logger.info("Starting {}", title)
    pygame.init()
    audio = AudioEngine()
    audio.initialize()
    pygame.display.set_caption(title)
    screen = pygame.display.set_mode(DEFAULT_WINDOW_SIZE)
    clock = pygame.time.Clock()
    scene = BattleScene(screen.get_rect(), audio=audio, encounter=encounter)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Received window close event")
                running = False
            else:
                scene.handle_event(event)
        scene.update(dt)
        scene.draw(screen)
        pygame.display.flip()
        if scene.should_quit:
            logger.info("Scene requested quit")
            running = False

    audio.stop_music()
    pygame.quit()
    logger.info("Game shut down cleanly")
