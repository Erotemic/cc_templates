from __future__ import annotations

import ast
from copy import deepcopy
from pathlib import Path

import pytest

from engine.game import AdventureGame
from engine.validation import validate_world
from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL


ROOT = Path(__file__).resolve().parents[1]


def test_mode_changes_have_one_authority():
    """New modes should not reintroduce scattered context assignments."""
    source = (ROOT / "engine" / "game.py").read_text()
    tree = ast.parse(source)
    owners: list[str] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.function = "<module>"

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            previous = self.function
            self.function = node.name
            self.generic_visit(node)
            self.function = previous

        def visit_Assign(self, node: ast.Assign) -> None:
            for target in node.targets:
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                    and target.attr == "mode"
                ):
                    owners.append(self.function)
            self.generic_visit(node)

    Visitor().visit(tree)
    assert owners == ["__init__", "_transition_mode"]


def test_terminal_choice_finishes_before_automatic_encounters():
    world = deepcopy(STAR_CRYSTAL)
    world["rooms"]["village"].setdefault("choices", []).insert(
        0,
        {
            "text": "Finish the test adventure",
            "result": ["Victory."],
            "set_flags": ["game_won"],
        },
    )
    world["encounters"].insert(
        0,
        {
            "name": "forest_small_spider",
            "locations": ["village"],
            "chance": 1.0,
            "handler": "handle_forest_spider_encounter",
        },
    )

    game = AdventureGame(world)
    assert game.apply("roomchoice:0") == ["Victory."]
    assert game.won
    assert game.mode == "exploration"
    assert game.combat_npc_name is None


def test_duplicate_loose_items_produce_one_unambiguous_action():
    world = deepcopy(STAR_CRYSTAL)
    world["rooms"]["village"]["items"] = ["health_tonic", "health_tonic"]
    game = AdventureGame(world)

    take_choices = [choice for choice in game.choices() if choice.action.startswith("take:")]
    assert [(choice.action, choice.text) for choice in take_choices] == [
        ("take:health_tonic", "Take Health Tonic x2")
    ]
    game.apply("take:health_tonic")
    assert [choice.text for choice in game.choices() if choice.action.startswith("take:")] == [
        "Take Health Tonic"
    ]


@pytest.mark.parametrize(
    "mutate, expected",
    [
        (
            lambda world: world["rooms"]["village"]["exits"][0].pop("direction"),
            "direction must be a non-empty string",
        ),
        (
            lambda world: world["rooms"]["village"]["features"][0].pop("name"),
            "name must be a non-empty string",
        ),
        (
            lambda world: world["rooms"]["crossroads"]["choices"][0].pop("text"),
            "text must be a non-empty string",
        ),
        (
            lambda world: world["rooms"]["village"]["npcs"][0]["base_stats"].pop("defense"),
            "base_stats is missing required field 'defense'",
        ),
        (
            lambda world: world["rooms"]["village"]["npcs"][2]["trade_offers"][0].pop("wants_gold"),
            "missing required field 'wants_gold'",
        ),
    ],
)
def test_world_validation_rejects_shapes_that_would_crash_later(mutate, expected):
    world = deepcopy(STAR_CRYSTAL)
    mutate(world)
    errors = validate_world(world)
    assert any(expected in error for error in errors), errors
    with pytest.raises(ValueError, match="Invalid adventure world"):
        AdventureGame(world)


@pytest.mark.parametrize(
    "mutate, expected",
    [
        (lambda world: world["rooms"]["village"].__setitem__("npcs", None), "npcs must be a list"),
        (lambda world: world["rooms"]["village"].__setitem__("features", "bad"), "features must be a list"),
        (lambda world: world["player"].__setitem__("equipment", []), "player.equipment must be a dictionary"),
        (lambda world: world.__setitem__("encounters", {}), "world.encounters must be a list"),
    ],
)
def test_validator_reports_bad_collection_types_instead_of_crashing(mutate, expected):
    world = deepcopy(STAR_CRYSTAL)
    mutate(world)
    errors = validate_world(world)
    assert any(expected in error for error in errors), errors


def test_action_boundary_fails_fast_on_corrupt_runtime_context():
    game = AdventureGame(STAR_CRYSTAL)
    game.current_npc_name = "Elder Mira"  # impossible while exploring
    with pytest.raises(AssertionError, match="Invalid adventure state"):
        game.apply("inventory")


def test_story_behavior_is_not_keyed_to_port_provenance():
    world = deepcopy(STAR_CRYSTAL)
    world["source_version"] = "renamed-or-new-source.py"
    game = AdventureGame(world)
    assert game.goal_text() == "Talk to Elder Mira."


def test_old_story_name_couplings_are_out_of_the_core_engine():
    source = (ROOT / "engine" / "game.py").read_text()
    for token in [
        'source == "version4.py"',
        'source == "version8.py"',
        'name == "Bandit Nox"',
        '"Tower Guardian": "star_crystal"',
        '"Custodian Echo": "grave_core"',
        'npc["name"] == "Crystal Spider"',
    ]:
        assert token not in source


def test_story_rule_references_are_validated():
    world = deepcopy(STAR_CRYSTAL)
    world["story_rules"]["riddle_reward_items"]["Missing Guardian"] = ["missing_item"]
    errors = validate_world(world)
    assert any("unknown NPC 'Missing Guardian'" in error for error in errors)
    assert any("unknown item 'missing_item'" in error for error in errors)


def test_invalid_equipment_slot_is_rejected_at_world_boundary():
    world = deepcopy(STAR_CRYSTAL)
    world["items"]["iron_sword"]["slot"] = "wepon"
    errors = validate_world(world)
    assert any("invalid" in error and "wepon" in error for error in errors)
