from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
ADVANCED = ROOT / "advanced"


def load_module(relative_path: str, module_name: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_intermediate_version1_accepts_a_data_only_room_choice():
    module = load_module("intermediate/version1.py", "cya_authoring_intermediate_v1")
    module.ROOMS["village"]["choices"].append(
        {"text": "Read the notice board", "result": ["FOUND: one very patient goat."]}
    )
    player = module.Player()
    state = {"key_taken": False, "game_won": False}
    choices = module.build_choices(player, state)
    action = next(action for text, action in choices if text == "Read the notice board")
    assert module.handle_action(action, player, state) == ["FOUND: one very patient goat."]


def test_intermediate_game_object_accepts_new_room_without_new_handler():
    module = load_module("intermediate/version2.py", "cya_authoring_intermediate_v2")
    module.ROOMS["village"].exits["through the blue door"] = "student_room"
    module.ROOMS["student_room"] = module.Room(
        key="student_room",
        description="A room added by copying one data block.",
        exits={"back to the village": "village"},
        choices=(
            module.RoomChoice("Look under the desk", ("You find a dragon doodle.",)),
        ),
    )
    game = module.Game()
    game.apply("go:student_room")
    choice = next(choice for choice in game.choices() if choice.text == "Look under the desk")
    assert game.apply(choice.action) == ["You find a dragon doodle."]


def test_intermediate_larger_game_keeps_same_simple_room_choice_contract():
    module = load_module("intermediate/version3.py", "cya_authoring_intermediate_v3")
    module.ROOMS["village"].exits["through the blue door"] = "student_room"
    module.ROOMS["student_room"] = module.Room(
        "student_room",
        "Student Room",
        "A room added without changing combat or quest code.",
        {"back to the village": "village"},
        choices=(
            module.RoomChoice("Open the notebook", ("The first page says: KEEP GOING.",)),
        ),
    )
    game = module.Game()
    game.apply("go:student_room")
    choice = next(choice for choice in game.choices() if choice.text == "Open the notebook")
    assert game.apply(choice.action) == ["The first page says: KEEP GOING."]


def test_advanced_world_can_grow_without_editing_the_engine():
    sys.path.insert(0, str(ADVANCED))
    try:
        from adventure.core import AdventureGame, Room, RoomChoice
        from adventure.worlds.star_crystal import STAR_CRYSTAL_WORLD

        world = deepcopy(STAR_CRYSTAL_WORLD)
        world.rooms["village"].exits["through the blue door"] = "student_room"
        world.rooms["student_room"] = Room(
            "student_room",
            "Student Room",
            "A modular room added entirely in world content.",
            {"back to the village": "village"},
            choices=(RoomChoice("Read the wall", ("Someone wrote HELLO in chalk.",)),),
        )
        game = AdventureGame(world)
        game.apply("go:student_room")
        choice = next(choice for choice in game.choices() if choice.text == "Read the wall")
        assert game.apply(choice.action) == ["Someone wrote HELLO in chalk."]
    finally:
        sys.path.remove(str(ADVANCED))
