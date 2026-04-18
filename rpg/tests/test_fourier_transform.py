import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from rpg_battle.content.encounters import ENCOUNTERS
from rpg_battle.core.actions import skill_action
from rpg_battle.core.battle_state import get_combatant, new_battle
from rpg_battle.core.rules import finish_round, resolve_action
from rpg_battle.render.signal_transform import apply_signal_transforms


def test_fourier_transform_cycles_render_state() -> None:
    state = new_battle(ENCOUNTERS["boss_null_hydra"])
    actor_id = state.teams[0].active_ids[2]
    target_id = state.teams[1].active_ids[0]

    resolve_action(state, skill_action(actor_id, "fourier_transform", (target_id,)), random.Random(0))
    target = get_combatant(state, target_id)
    assert target.render_transforms["fourier"] == 1
    assert "fourier_domain" in target.statuses
    assert "fourier_reflection" not in target.statuses

    finish_round(state)
    assert target.render_transforms["fourier"] == 1
    assert "fourier_domain" in target.statuses

    resolve_action(state, skill_action(actor_id, "fourier_transform", (target_id,)), random.Random(0))
    assert target.render_transforms["fourier"] == 2
    assert "fourier_domain" not in target.statuses
    assert "fourier_reflection" in target.statuses

    resolve_action(state, skill_action(actor_id, "fourier_transform", (target_id,)), random.Random(0))
    assert target.render_transforms["fourier"] == 3
    assert "fourier_domain" in target.statuses
    assert "fourier_reflection" in target.statuses

    resolve_action(state, skill_action(actor_id, "fourier_transform", (target_id,)), random.Random(0))
    assert "fourier" not in target.render_transforms
    assert "fourier_domain" not in target.statuses
    assert "fourier_reflection" not in target.statuses


def test_fourier_phase_two_matches_spatial_flip() -> None:
    pygame.init()
    try:
        surface = pygame.Surface((6, 5), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        surface.set_at((1, 1), (255, 0, 0, 255))
        surface.set_at((4, 2), (0, 255, 0, 255))
        surface.set_at((2, 4), (0, 0, 255, 255))

        reflected = apply_signal_transforms(surface, {"fourier": 2})
        expected = pygame.transform.flip(surface, True, True)

        assert pygame.image.tostring(reflected, "RGBA") == pygame.image.tostring(expected, "RGBA")
    finally:
        pygame.quit()
