from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CAPSTONE = ROOT / "capstone"
sys.path.insert(0, str(CAPSTONE))

from engine.game import AdventureGame
from worlds.dust_vault import WORLD_DATA as DUST_VAULT
from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL


STAR_ROOMS = (
    "village", "crossroads", "forest", "garden", "lake", "cave_entrance",
    "cave_depths", "ruins", "tower_gate", "tower_top", "jail",
)
DUST_ROOMS = (
    "berth", "lounge", "service", "annex", "archive", "shuttle", "brig",
    "survey_pad", "crash_gully", "windbreak", "relay", "habitat", "pump",
    "ravine", "drill", "crater", "gallery", "vault",
)


def preserved_fingerprint(data, room_keys):
    clean = deepcopy(data)
    clean["rooms"] = {key: clean["rooms"][key] for key in room_keys}
    for room in clean["rooms"].values():
        # ``choices`` is the one intentional new authoring field. It was not
        # present in the original world object.
        room.pop("choices", None)
    payload = json.dumps(clean, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def test_full_original_world_data_is_preserved():
    assert preserved_fingerprint(STAR_CRYSTAL, STAR_ROOMS) == (
        "84e757fb33a541bea4ca8c5c89e6880d03411995d39bd163f1a1162ec6106299"
    )
    assert preserved_fingerprint(DUST_VAULT, DUST_ROOMS) == (
        "94a38d98362ece7168c44a88ab2c705d6286c11d07ae9cc1f1c5b1b430034c21"
    )


def act(game, action):
    legal = {choice.action for choice in game.choices()}
    assert action in legal, (action, game.player_location, game.mode, sorted(legal))
    lines = game.apply(action)
    if game.mode == "confirm_move":
        lines += game.apply("move:confirm")
    return lines


def pick(game, text):
    matches = [choice for choice in game.choices() if text.lower() in choice.text.lower()]
    assert len(matches) == 1, (text, [(c.action, c.text) for c in game.choices()])
    return act(game, matches[0].action)


def move(game, destination):
    for index, exit_spec in enumerate(game.room.get("exits", [])):
        if exit_spec["destination"] == destination:
            return act(game, f"move:{index}")
    raise AssertionError((game.player_location, destination, game.room.get("exits", [])))


def test_star_crystal_full_story_has_a_nonviolent_guardian_solution():
    game = AdventureGame(STAR_CRYSTAL, seed=0)
    for action in ["npc:0", "talk:0", "npc:leave", "move:0", "move:1"]:
        act(game, action)
    for item in ["moonleaf_herb", "rope", "iron_sword", "health_tonic"]:
        act(game, f"take:{item}")
    for action in [
        "inventory", "equip:iron_sword", "inventory:back", "move:0", "move:2",
        "npc:0", "trade:0", "npc:leave", "move:0", "move:1", "move:2",
        "move:1", "npc:0", "npc:attack",
    ]:
        act(game, action)
    while game.mode == "combat":
        act(game, "combat:attack")
    for action in [
        "npc:loot", "npc:leave", "move:0", "move:0", "move:0", "move:3",
        "move:1", "move:1", "npc:0", "riddle",
    ]:
        act(game, action)
    game.submit_riddle_answer("river")
    assert game.player.has_item("star_crystal")
    act(game, "npc:leave")
    for action in ["move:0", "move:0", "move:0", "move:0", "npc:0"]:
        act(game, action)
    return_choice = next(c for c in game.choices() if c.text == "Return the Star Crystal")
    act(game, return_choice.action)
    assert game.won


def dust_to_core(*, seed=0, learn_truth=False):
    game = AdventureGame(DUST_VAULT, seed=seed)
    move(game, "lounge")
    pick(game, "Rafe Mercer")
    pick(game, "Ask about the job")
    act(game, "npc:leave")
    move(game, "service")
    move(game, "annex")
    pick(game, "security panel")
    move(game, "archive")
    pick(game, "Payroll Shard")
    move(game, "annex")
    move(game, "service")
    move(game, "shuttle")
    pick(game, "extraction skiff")
    act(game, "inventory")
    pick(game, "Cutter Rifle")
    act(game, "inventory:back")
    move(game, "windbreak")
    pick(game, "Orla Quist")
    pick(game, "Line Spool")
    act(game, "npc:leave")
    move(game, "relay")
    pick(game, "survey mast")
    move(game, "windbreak")
    move(game, "pump")
    pick(game, "bridge control")
    move(game, "ravine")
    move(game, "drill")
    pick(game, "Cade Voss")
    act(game, "npc:attack")
    while game.mode == "combat":
        act(game, "combat:attack")
    act(game, "trade:1")
    act(game, "npc:leave")
    move(game, "ravine")
    move(game, "pump")
    move(game, "windbreak")
    move(game, "habitat")
    if learn_truth:
        pick(game, "Juno Hale")
        pick(game, "what the survey team found")
        act(game, "npc:leave")
    move(game, "crater")
    move(game, "gallery")
    move(game, "vault")
    pick(game, "Custodian Echo")
    pick(game, "riddle")
    game.submit_riddle_answer("a lie")
    act(game, "npc:leave")
    assert game.player.has_item("grave_core")
    return game


def test_dust_vault_all_three_authored_endings_are_reachable():
    corporate = dust_to_core()
    move(corporate, "gallery")
    move(corporate, "crater")
    assert "rafe_offer_heard" in corporate.flags
    move(corporate, "habitat")
    move(corporate, "windbreak")
    pick(corporate, "landing beacon")
    assert corporate.won and "ending_corporate" in corporate.flags

    broadcast = dust_to_core(learn_truth=True)
    move(broadcast, "gallery")
    move(broadcast, "crater")
    move(broadcast, "habitat")
    pick(broadcast, "archive uplink")
    assert broadcast.won and "ending_broadcast" in broadcast.flags

    bury = dust_to_core()
    move(bury, "gallery")
    move(bury, "crater")
    pick(bury, "collapse charges")
    assert bury.won and "ending_bury" in bury.flags


def test_dust_vault_clean_and_hot_station_paths_both_work():
    clean = AdventureGame(DUST_VAULT, seed=0)
    move(clean, "lounge")
    pick(clean, "Rafe Mercer")
    pick(clean, "Ask about the job")
    act(clean, "npc:leave")
    move(clean, "service"); move(clean, "annex"); pick(clean, "security panel")
    move(clean, "archive"); pick(clean, "Payroll Shard")
    move(clean, "annex"); move(clean, "service"); move(clean, "shuttle")
    pick(clean, "extraction skiff")
    assert clean.player_location == "survey_pad"
    assert "promoted" in clean.flags and "stranded" not in clean.flags

    hot = AdventureGame(DUST_VAULT, seed=0)
    move(hot, "lounge")
    pick(hot, "Rafe Mercer")
    pick(hot, "Ask about the job")
    act(hot, "npc:leave")
    move(hot, "service"); move(hot, "annex"); pick(hot, "security panel")
    move(hot, "archive"); pick(hot, "Payroll Shard"); pick(hot, "red locker")
    assert hot.bounty > 0
    move(hot, "annex")
    # The hot route intentionally attracts the station patrol. Resolve that
    # authored encounter before continuing to the shuttle.
    while hot.mode == "combat":
        act(hot, "combat:attack")
    move(hot, "service"); move(hot, "shuttle")
    pick(hot, "extraction skiff")
    assert hot.player_location == "crash_gully"
    assert "stranded" in hot.flags and "promoted" not in hot.flags


def test_capstone_student_can_add_room_and_choice_without_engine_changes():
    world = deepcopy(STAR_CRYSTAL)
    world["rooms"]["village"]["exits"].append(
        {"direction": "through a blue door", "destination": "student_room"}
    )
    world["rooms"]["student_room"] = {
        "name": "Student Room",
        "description": "A room added without changing the engine.",
        "exits": [{"direction": "back", "destination": "village"}],
        "choices": [
            {"text": "Look under the desk", "result": ["You find a doodle of a dragon."]}
        ],
    }
    game = AdventureGame(world)
    move(game, "student_room")
    lines = pick(game, "Look under the desk")
    assert lines == ["You find a doodle of a dragon."]


def test_capstone_game_rules_do_not_read_or_write_the_terminal():
    import ast

    source = (CAPSTONE / "engine" / "game.py").read_text()
    tree = ast.parse(source)
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "input" not in called_names
    assert "print" not in called_names
