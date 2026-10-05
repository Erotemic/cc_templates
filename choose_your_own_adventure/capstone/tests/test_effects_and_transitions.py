from __future__ import annotations

from copy import deepcopy

from engine.actions import apply_effect
from engine.game import AdventureGame
from engine.validation import assert_valid_state
from worlds.dust_vault import WORLD_DATA as DUST_VAULT
from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL


def test_warning_move_can_be_cancelled_or_confirmed_without_losing_context():
    game = AdventureGame(STAR_CRYSTAL, seed=0)
    game.player_location = "ruins"
    game.player.add_item("rope")
    index = next(
        i for i, exit_spec in enumerate(game.room["exits"])
        if exit_spec["destination"] == "tower_gate"
    )

    lines = game.apply(f"move:{index}")
    assert game.mode == "confirm_move"
    assert game.pending_exit == ("ruins", index)
    assert any("unstable" in line for line in lines)
    assert_valid_state(game)

    game.apply("move:cancel")
    assert game.player_location == "ruins"
    assert game.mode == "exploration"
    assert game.pending_exit is None
    assert_valid_state(game)

    game.apply(f"move:{index}")
    game.apply("move:confirm")
    assert game.player_location == "tower_gate"
    assert game.pending_exit is None
    assert_valid_state(game)


def test_failed_trade_does_not_partially_mutate_gold_or_inventory():
    game = AdventureGame(STAR_CRYSTAL)
    merchant = game.npcs["Merchant Sella"]
    game.current_npc_name = merchant["name"]
    game.mode = "npc"
    before_player_gold = game.player.gold
    before_merchant_gold = game._npc_actor(merchant).gold
    before_player_items = list(game.player.inventory)
    before_merchant_items = list(game._npc_actor(merchant).inventory)

    lines = game.apply("trade:0")

    assert any("Come back" in line for line in lines)
    assert game.player.gold == before_player_gold
    assert game._npc_actor(merchant).gold == before_merchant_gold
    assert game.player.inventory == before_player_items
    assert game._npc_actor(merchant).inventory == before_merchant_items
    assert_valid_state(game)


def test_riddle_failure_can_kill_player_and_leave_terminal_state_valid():
    game = AdventureGame(STAR_CRYSTAL)
    game.player_location = game.npc_rooms["Tower Guardian"]
    game.current_npc_name = "Tower Guardian"
    game.mode = "riddle"
    game.player.health = 1

    lines = game.submit_riddle_answer("definitely wrong")

    assert any("take" in line.lower() and "damage" in line.lower() for line in lines)
    assert game.lost
    assert game.player.health == 0
    assert game.choices() == []
    assert_valid_state(game)


def test_composite_effect_stops_after_fatal_damage():
    game = AdventureGame(STAR_CRYSTAL)
    game.player.health = 1
    effect = {
        "type": "CompositeEffect",
        "effects": [
            {"type": "DamageCharacterEffect", "target": "player", "amount": 999, "text": None},
            {"type": "GivePlayerItemEffect", "item_ids": ["silver_key"]},
        ],
    }
    apply_effect(game, effect)
    assert game.lost
    assert not game.player.has_item("silver_key")
    assert_valid_state(game)


def test_conditional_and_bounty_branch_effects_take_both_branches():
    game = AdventureGame(DUST_VAULT)
    conditional = {
        "type": "ConditionalEffect",
        "required_flags": ["ready"],
        "blocked_flags": [],
        "required_items": [],
        "success_effect": {"type": "PrintEffect", "lines": ["success"]},
        "failure_effect": {"type": "PrintEffect", "lines": ["failure"]},
    }
    assert apply_effect(game, conditional) == ["failure"]
    game.flags.add("ready")
    assert apply_effect(game, conditional) == ["success"]

    branch = {
        "type": "BranchOnBountyEffect",
        "threshold": 0,
        "clean_effect": {"type": "PrintEffect", "lines": ["clean"]},
        "hot_effect": {"type": "PrintEffect", "lines": ["hot"]},
    }
    assert apply_effect(game, branch) == ["clean"]
    game.bounty = 1
    assert apply_effect(game, branch) == ["hot"]


def test_block_and_unblock_effects_target_only_first_matching_direction():
    game = AdventureGame(DUST_VAULT)
    # Dust Vault deliberately has repeated direction labels. Match the old
    # find_exit() contract rather than mutating every same-named route.
    room_key = next(
        key for key, room in game.world["rooms"].items()
        if len([e for e in room.get("exits", []) if e["direction"] == "north"]) > 1
    )
    north = [e for e in game.world["rooms"][room_key]["exits"] if e["direction"] == "north"]
    assert len(north) > 1

    apply_effect(
        game,
        {"type": "BlockPathEffect", "location_key": room_key, "direction": "north", "reason": "test"},
    )
    assert north[0]["blocked"] is True
    assert all(not e.get("blocked", False) for e in north[1:])

    apply_effect(
        game,
        {"type": "UnblockPathEffect", "location_key": room_key, "direction": "north"},
    )
    assert north[0]["blocked"] is False


def test_end_game_effect_sets_a_stable_terminal_state():
    game = AdventureGame(deepcopy(DUST_VAULT))
    lines = apply_effect(
        game,
        {
            "type": "EndGameEffect",
            "lines": ["You choose the ending."],
            "flags": ["game_won", "ending_test"],
        },
    )
    assert lines == ["You choose the ending."]
    assert game.won and not game.lost
    assert game.ending == "You choose the ending."
    assert game.choices() == []
    assert_valid_state(game)


def test_end_game_effect_can_also_represent_a_loss():
    game = AdventureGame(deepcopy(DUST_VAULT))
    apply_effect(
        game,
        {
            "type": "EndGameEffect",
            "lines": ["The station falls silent."],
            "flags": ["game_lost", "ending_test_loss"],
        },
    )
    assert game.lost and not game.won
    assert game.ending == "The station falls silent."
    assert game.choices() == []
    assert_valid_state(game)


def test_tonic_only_shatters_on_the_authored_broken_crossing_event():
    game = AdventureGame(STAR_CRYSTAL, seed=1)  # first ChanceEffect roll is < 0.30
    game.player_location = "ruins"
    game.player.add_item("rope")
    game.player.add_item("health_tonic")
    before_hp = game.player.health
    index = next(
        i for i, exit_spec in enumerate(game.room["exits"])
        if exit_spec["destination"] == "tower_gate"
    )

    game.apply(f"move:{index}")
    lines = game.apply("move:confirm")

    assert game.player_location == "tower_gate"
    assert game.player.health < before_hp
    assert not game.player.has_item("health_tonic")
    assert any("shatters on the rocks" in line for line in lines)
    assert_valid_state(game)


def test_fatal_on_attempt_effect_does_not_continue_into_move_confirmation():
    world = deepcopy(STAR_CRYSTAL)
    exit_spec = world["rooms"]["village"]["exits"][0]
    exit_spec["warning_text"] = "This route looks deadly. Continue?"
    exit_spec["on_attempt_effect"] = {
        "type": "DamageCharacterEffect",
        "target": "player",
        "amount": 999,
        "text": "A falling stone strikes you before you can leave.",
    }
    game = AdventureGame(world)
    game.player.health = 1

    lines = game.apply("move:0")

    assert game.lost
    assert game.player_location == "village"
    assert game.pending_exit is None
    assert game.mode == "exploration"
    assert not any("Continue?" in line for line in lines)
    assert_valid_state(game)
