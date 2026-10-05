from __future__ import annotations

from collections import deque

from art.catalog import choose_art
from engine.game import AdventureGame
from engine.river_crossing import PASSENGERS, RiverCrossingState
from engine.validation import assert_valid_state
from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL


def actions(game: AdventureGame) -> set[str]:
    return {choice.action for choice in game.choices()}


def reach_farm(game: AdventureGame) -> None:
    game.apply("move:0")  # village -> crossroads
    farm_choice = next(
        choice for choice in game.choices()
        if "Hearthfield Farm" in choice.text
    )
    game.apply(farm_choice.action)
    assert game.player_location == "hearthfield_farm"


def start_delivery(game: AdventureGame) -> list[str]:
    reach_farm(game)
    game.apply("npc:0")
    lines = game.apply("talk:0")
    assert "river_delivery_active" in game.flags
    game.apply("npc:leave")
    game.apply("move:1")  # farm -> west bank
    assert game.player_location == "river_west"
    return lines


def test_pure_river_state_machine_reaches_solution_without_unsafe_states():
    initial = RiverCrossingState()
    queue = deque([initial])
    seen = {initial}

    while queue:
        state = queue.popleft()
        assert state.unsafe_reason() is None
        passengers = (None, *state.passengers_with_player())
        for passenger in passengers:
            candidate, reason = state.try_cross(passenger)
            if reason is not None:
                assert candidate == state
                continue
            assert candidate.unsafe_reason() is None
            if candidate not in seen:
                seen.add(candidate)
                queue.append(candidate)

    assert any(state.solved for state in seen)
    assert len(seen) >= 8  # enough structure to be more than a scripted sequence


def test_unsafe_crossings_are_rejected_without_mutating_state():
    state = RiverCrossingState()

    for passenger in (None, "wolf", "cabbage"):
        candidate, reason = state.try_cross(passenger)
        assert candidate == state
        assert reason is not None

    candidate, reason = state.try_cross("goat")
    assert reason is None
    assert candidate.player == "east"
    assert candidate.goat == "east"


def test_boat_is_ordinary_travel_when_delivery_quest_is_inactive():
    game = AdventureGame(STAR_CRYSTAL)
    reach_farm(game)
    game.apply("move:1")
    assert game.player_location == "river_west"
    assert not any(action.startswith("river:") for action in actions(game))

    game.apply("move:1")
    assert game.player_location == "river_east"
    assert_valid_state(game)


def test_delivery_quest_turns_boat_into_the_classic_state_machine():
    game = AdventureGame(STAR_CRYSTAL)
    gold_before = game.player.gold
    start_lines = start_delivery(game)
    assert any("wolf, goat, and cabbage" in line.lower() for line in start_lines)
    assert game.goal_text().startswith("Deliver the wolf")
    assert actions(game) >= {"river:alone", "river:wolf", "river:goat", "river:cabbage"}

    initial = game.river_state
    blocked = game.apply("river:wolf")
    assert game.river_state == initial
    assert game.player_location == "river_west"
    assert any("goat and cabbage" in line.lower() for line in blocked)
    key, _, _ = choose_art(game.snapshot(), "\n".join(blocked))
    assert key == "river_crossing_blocked"

    # Classic solution: G -> alone <- W -> G <- C -> alone <- G ->
    sequence = [
        "river:goat",
        "river:alone",
        "river:wolf",
        "river:goat",
        "river:cabbage",
        "river:alone",
        "river:goat",
    ]
    final_lines: list[str] = []
    for action in sequence:
        final_lines = game.apply(action)
        assert_valid_state(game)

    assert game.player_location == "river_east"
    assert "river_delivery_active" not in game.flags
    assert "river_delivery_complete" in game.flags
    assert game.player.gold == gold_before + 20
    assert any("safely on the east bank" in line.lower() for line in final_lines)
    key, _, _ = choose_art(game.snapshot(), "\n".join(final_lines))
    assert key == "river_delivery_complete"

    # Once delivered, the boat is ordinary travel again.
    assert not any(action.startswith("river:") for action in actions(game))
    assert any("boat west" in choice.text.lower() for choice in game.choices())


def test_river_snapshot_exposes_state_without_giving_ui_authority():
    game = AdventureGame(STAR_CRYSTAL)
    start_delivery(game)
    assert game.river_crossing is None
    before = game.river_state
    snapshot = game.snapshot()
    assert snapshot["river_crossing"] == {
        "player": "west",
        "wolf": "west",
        "goat": "west",
        "cabbage": "west",
    }
    assert game.river_state == before
    assert game.river_crossing is None
