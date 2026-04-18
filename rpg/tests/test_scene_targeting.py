import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from rpg_battle.battle.battle_scene import BattleScene
from rpg_battle.settings import SCREEN_HEIGHT, SCREEN_WIDTH


def test_single_enemy_still_opens_target_menu() -> None:
    pygame.init()
    try:
        scene = BattleScene(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        scene.event_queue = []
        scene.event_timer = 0.0
        scene.current_event = None
        scene.current_event_timer = 0.0
        scene.ai_think_timer = 0.0

        # Force a player turn with only one enemy remaining on the frontline.
        scene.controller.current_actor_id = scene.controller.state.teams[0].active_ids[0]
        enemy_team = scene.controller.state.teams[1]
        enemy_team.active_ids = enemy_team.active_ids[:1]
        scene._set_root_menu_for_actor(scene.controller.current_actor_id)

        scene._handle_player_move_selection("strike", "attack")

        assert scene.menu_stack[-1].title == "Choose Target"
        assert scene.menu_stack[-1].options == ["AI Slop"]
    finally:
        pygame.quit()


def test_confirm_menu_choice_with_no_menu_does_not_crash() -> None:
    pygame.init()
    try:
        scene = BattleScene(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        scene.menu_stack = []
        scene._confirm_menu_choice()
    finally:
        pygame.quit()
