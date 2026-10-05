from __future__ import annotations

from copy import deepcopy

from art.catalog import choose_art
from engine.actions import apply_effect
from engine.game import AdventureGame
from engine.validation import assert_valid_state, validate_state
from simulate import simulate_world
from worlds.dust_vault import WORLD_DATA as DUST_VAULT
from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL


def test_deterministic_random_walks_preserve_state_invariants():
    """Stress many legal transitions without requiring any frontend."""
    for label, world in [
        ("Star Crystal", STAR_CRYSTAL),
        ("Dust Vault", DUST_VAULT),
    ]:
        result = simulate_world(label, world, runs=10, steps=120, seed=100)
        assert result.runs == 10
        assert result.actions > 500
        assert result.transitions


def test_combat_death_clears_all_combat_context():
    game = AdventureGame(STAR_CRYSTAL, seed=0)
    enemy = game.make_temp_npc(
        "Test Golem",
        20,
        999,
        999,
        0,
        "A deliberately overpowered test enemy.",
        aggression=100,
        reward_gold=0,
        defeat_lines=[],
    )
    game.start_combat("Test Golem", temporary=enemy)
    game.player.health = 1

    game.apply("combat:defend")

    assert game.lost
    assert game.player.health == 0
    assert game.mode == "exploration"
    assert game.combat_npc_name is None
    assert game.combat_temporary is None
    assert game.current_npc_name is None
    assert game.choices() == []
    assert_valid_state(game)


def test_environmental_damage_can_end_the_game_without_a_ui_loop():
    game = AdventureGame(STAR_CRYSTAL)
    game.player.health = 1
    lines = apply_effect(
        game,
        {
            "type": "DamageCharacterEffect",
            "target": "player",
            "amount": 999,
            "text": "The ledge collapses beneath you.",
        },
    )
    assert lines[0] == "The ledge collapses beneath you."
    assert game.lost
    assert game.player.health == 0
    assert game.choices() == []
    assert_valid_state(game)


def test_removing_last_equipped_hp_item_clamps_current_health():
    game = AdventureGame(STAR_CRYSTAL)
    game.player.add_item("guard_coat")
    game.player.equipment["armor"] = "guard_coat"
    game.player.health = game.player_max_hp
    assert game.player.health == 110

    assert game.remove_actor_item(game.player, "guard_coat")

    assert game.player.equipment["armor"] is None
    assert game.player_max_hp == 100
    assert game.player.health == 100
    assert_valid_state(game)


def test_removing_one_of_two_identical_items_keeps_equipped_copy():
    game = AdventureGame(STAR_CRYSTAL)
    game.player.add_item("guard_coat")
    game.player.add_item("guard_coat")
    game.player.equipment["armor"] = "guard_coat"

    assert game.remove_actor_item(game.player, "guard_coat")
    assert game.player.inventory.count("guard_coat") == 1
    assert game.player.equipment["armor"] == "guard_coat"

    assert game.remove_actor_item(game.player, "guard_coat")
    assert game.player.equipment["armor"] is None
    assert_valid_state(game)


def test_full_health_tonic_is_not_offered_or_consumed():
    game = AdventureGame(STAR_CRYSTAL)
    game.give_player_item("health_tonic")
    assert game.player.health == game.player_max_hp

    game.apply("inventory")
    assert "use:health_tonic" not in {choice.action for choice in game.choices()}

    before = list(game.player.inventory)
    lines = game.use_consumable(game.player, "health_tonic")
    assert lines == ["Tav is already at full health."]
    assert game.player.inventory == before
    assert_valid_state(game)


def test_equipping_an_already_equipped_item_is_not_a_menu_choice():
    game = AdventureGame(STAR_CRYSTAL)
    game.player.add_item("guard_coat")
    game.player.equipment["armor"] = "guard_coat"
    game.apply("inventory")
    actions = {choice.action for choice in game.choices()}
    assert "equip:guard_coat" not in actions
    assert "unequip:armor" in actions


def test_tonic_pickup_does_not_select_the_shatter_scene():
    game = AdventureGame(STAR_CRYSTAL)
    lines = game.give_player_item("health_tonic")
    key, _, _ = choose_art(game.snapshot(), "\n".join(lines))
    assert key != "item_shatter"

    key, _, _ = choose_art(
        game.snapshot(),
        "One of your Health Tonics shatters on the rocks.",
    )
    assert key == "item_shatter"


def test_state_validator_reports_corruption_clearly():
    game = AdventureGame(STAR_CRYSTAL)
    game.combat_npc_name = "Bandit Nox"
    errors = validate_state(game)
    assert any("combat-only context leaked" in error for error in errors)


def test_illegal_action_does_not_mutate_state():
    game = AdventureGame(deepcopy(STAR_CRYSTAL))
    before = game.snapshot()
    try:
        game.apply("definitely:not:legal")
    except ValueError:
        pass
    else:
        raise AssertionError("illegal action was accepted")
    assert game.snapshot() == before


def test_common_ui_transitions_return_immediate_feedback():
    """Menu selections must explain themselves in the same transaction."""
    game = AdventureGame(STAR_CRYSTAL)

    lines = game.apply("inventory")
    assert lines == ["You open your inventory and equipment."]
    lines = game.apply("inventory:back")
    assert lines == ["You close your inventory and return to the adventure."]

    elder_index = next(
        i for i, npc in enumerate(game.room["npcs"])
        if npc["name"] == "Elder Mira"
    )
    lines = game.apply(f"npc:{elder_index}")
    assert lines == ["You approach Elder Mira."]
    lines = game.apply("npc:leave")
    assert lines == ["You step away from Elder Mira."]

    destination = game.world["rooms"][game.room["exits"][0]["destination"]]["name"]
    lines = game.apply("move:0")
    assert any(destination in line for line in lines)


def test_every_randomly_selected_action_has_same_turn_feedback():
    """Regression for actions that appeared to resolve one click late."""
    for label, world in [
        ("Star Crystal", STAR_CRYSTAL),
        ("Dust Vault", DUST_VAULT),
    ]:
        # drive_random_game itself asserts that every action result is nonblank.
        result = simulate_world(label, world, runs=8, steps=180, seed=700)
        assert result.actions > 500
