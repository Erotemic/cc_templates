from __future__ import annotations

import pygame
from loguru import logger

from rpg_battle.audio.engine import AudioEngine
from rpg_battle.battle.battle_scene import BattleScene
from rpg_battle.settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE


def run_game() -> None:
    """Run the main pygame loop for the battle scene."""
    logger.info("Starting {}", TITLE)
    pygame.init()
    audio = AudioEngine()
    audio.initialize()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    scene = BattleScene(screen.get_rect(), audio=audio)

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
