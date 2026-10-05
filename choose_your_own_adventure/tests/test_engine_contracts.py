from __future__ import annotations

from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
ADVANCED = ROOT / "advanced"
sys.path.insert(0, str(ADVANCED))

from adventure.core import AdventureGame
from adventure.worlds.star_crystal import make_star_crystal_game


def test_illegal_actions_are_rejected_before_world_code_runs():
    game = make_star_crystal_game()
    with pytest.raises(ValueError):
        game.apply("take_crystal")


def test_game_exposes_state_choices_and_actions_without_a_ui():
    game = make_star_crystal_game()
    assert isinstance(game, AdventureGame)
    assert game.describe()
    assert game.choices()
    assert all(choice.action and choice.text for choice in game.choices())


def test_art_is_observation_only():
    from adventure.art import star_crystal_art

    game = make_star_crystal_game()
    before = (
        game.player.location,
        game.player.hp,
        list(game.player.inventory),
        set(game.player.flags),
    )
    art = star_crystal_art(game)
    after = (
        game.player.location,
        game.player.hp,
        list(game.player.inventory),
        set(game.player.flags),
    )
    assert art
    assert after == before
