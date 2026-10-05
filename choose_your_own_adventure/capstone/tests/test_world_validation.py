from __future__ import annotations

from copy import deepcopy

import pytest

from engine.game import AdventureGame
from engine.validation import validate_world
from worlds.dust_vault import WORLD_DATA as DUST_VAULT
from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL


def test_shipped_worlds_pass_structural_validation():
    assert validate_world(STAR_CRYSTAL) == []
    assert validate_world(DUST_VAULT) == []


def test_unknown_exit_destination_is_rejected_at_startup():
    world = deepcopy(STAR_CRYSTAL)
    world["rooms"]["village"]["exits"][0]["destination"] = "missing_room"
    with pytest.raises(ValueError, match="unknown room 'missing_room'"):
        AdventureGame(world)


def test_unknown_student_item_reference_is_rejected_at_startup():
    world = deepcopy(STAR_CRYSTAL)
    world["rooms"]["village"].setdefault("choices", []).append(
        {"text": "Take mystery prize", "give_items": ["mystery_prize"]}
    )
    with pytest.raises(ValueError, match="unknown item 'mystery_prize'"):
        AdventureGame(world)


def test_bad_scripted_effect_is_rejected_at_startup():
    world = deepcopy(STAR_CRYSTAL)
    world["rooms"]["village"]["features"].append(
        {
            "type": "ScriptedFeature",
            "name": "broken demo",
            "first_effect": {"type": "TeleportToMarsEffect"},
        }
    )
    with pytest.raises(ValueError, match="unsupported effect type"):
        AdventureGame(world)


def test_student_item_can_omit_zero_value_combat_bonus_fields():
    world = deepcopy(STAR_CRYSTAL)
    world["items"]["student_charm"] = {
        "name": "Student Charm",
        "description": "A simple item with no stat bonuses.",
        "slot": "charm",
    }
    world["player"]["inventory"].append("student_charm")
    world["player"]["equipment"]["charm"] = "student_charm"

    game = AdventureGame(world)

    assert game.player_max_hp == game.player.max_hp
    assert game.player_defense == game.player.defense
    assert game.player_attack_range == (game.player.attack_min, game.player.attack_max)
