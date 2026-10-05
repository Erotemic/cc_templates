from __future__ import annotations

import ast
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CAPSTONE = ROOT / "capstone"
sys.path.insert(0, str(CAPSTONE))

from art.catalog import DUST_EVENT_RULES, STAR_EVENT_RULES, choose_art
from art.dust_vault import DUST_VAULT_ART
from art.star_crystal import REDRAWN_ART, STAR_CRYSTAL_ART
from engine.game import AdventureGame
from worlds.dust_vault import WORLD_DATA as DUST_VAULT
from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL


ORIGINAL_STAR_ART_KEYS = {
    "ruins_stumble", "bramble_push", "dark_cave_blocked", "broken_crossing",
    "tower_gate_unlock", "forest_whisper_hint", "trail_reopened", "serve_time",
    "jail_release", "first_tower_visit", "bandit_surrenders",
    "player_surrender_accepted", "player_surrender_rejected",
    "guardian_trial_passed", "guardian_trial_failed", "spider_web_cleared",
    "return_crystal", "fountain_restored", "fountain_rest",
    "quest_complete_cheer", "guard_arrest", "item_shatter", "mercy_choice",
    "loc::village", "loc::crossroads", "loc::forest", "loc::garden",
    "loc::lake", "loc::cave_entrance", "loc::cave_depths", "loc::ruins",
    "loc::tower_gate", "loc::tower_top", "loc::jail",
    "npc::elder_mira::alive", "npc::elder_mira::dead",
    "npc::guard_halwen::alive", "npc::guard_halwen::dead",
    "npc::merchant_sella::alive", "npc::merchant_sella::dead",
    "npc::fisher_rowan::alive", "npc::fisher_rowan::dead",
    "npc::bandit_nox::alive", "npc::bandit_nox::dead",
    "npc::crystal_spider::alive", "npc::crystal_spider::dead",
    "npc::tower_guardian::alive", "npc::tower_guardian::dead",
    "npc::small_spider::alive", "npc::small_spider::dead",
}


def slug(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def test_all_original_star_crystal_art_is_preserved_and_polished():
    assert set(STAR_CRYSTAL_ART) == ORIGINAL_STAR_ART_KEYS
    assert len(STAR_CRYSTAL_ART) == 50
    assert "ELDER MIRA" in STAR_CRYSTAL_ART["npc::elder_mira::alive"]
    assert all(max(map(len, art.splitlines())) <= 64 for art in STAR_CRYSTAL_ART.values())
    assert all(not art.splitlines()[1].strip() == "\\" for art in STAR_CRYSTAL_ART.values())
    assert {key for key, _ in STAR_EVENT_RULES} == {
        key for key in ORIGINAL_STAR_ART_KEYS
        if not key.startswith("loc::") and not key.startswith("npc::")
    }
    scenario_keys = {key for key in ORIGINAL_STAR_ART_KEYS if "::" not in key}
    assert scenario_keys <= set(REDRAWN_ART)


def test_dust_vault_has_art_for_every_room_and_character():
    expected_locations = {f"loc::{room_key}" for room_key in DUST_VAULT["rooms"]}
    assert expected_locations <= set(DUST_VAULT_ART)

    npc_names = {
        npc["name"]
        for room in DUST_VAULT["rooms"].values()
        for npc in room.get("npcs", [])
    } | {"Patrol Drone", "Glass Maw"}
    for name in npc_names:
        for state in ("alive", "dead"):
            assert f"npc::{slug(name)}::{state}" in DUST_VAULT_ART

    assert {key for key, _ in DUST_EVENT_RULES} <= set(DUST_VAULT_ART)
    assert all(max(map(len, art.splitlines())) <= 64 for art in DUST_VAULT_ART.values())


def test_elder_mira_portrait_is_selected_when_player_approaches_her():
    game = AdventureGame(STAR_CRYSTAL)
    game.apply("npc:0")
    key, title, drawing = choose_art(game.snapshot())
    assert key == "npc::elder_mira::alive"
    assert "Elder Mira" in title
    assert "ELDER MIRA" in drawing


def test_capstone_snapshot_restores_goal_and_ui_state_without_terminal_io():
    game = AdventureGame(STAR_CRYSTAL)
    snapshot = game.snapshot()
    assert snapshot["goal"] == "Talk to Elder Mira."
    assert snapshot["location_key"] == "village"
    assert snapshot["attack"] == game.player_attack_range
    assert snapshot["equipment"]
    assert snapshot["focus_npc_name"] is None


def test_capstone_textual_frontend_restores_v6_v7_features_without_legacy_bridge():
    source = (CAPSTONE / "engine" / "textual_app.py").read_text()
    for feature in [
        "OptionList", "RichLog", "Input", "#ascii_art", "#current_event",
        "#history", "toggle_log", "clear_history", "toggle_art",
        "number keys 1-9", "submit_riddle_answer", "choose_art",
        "set_interval", "stream_queue",
    ]:
        assert feature in source

    for legacy_bridge in [
        "threading", "queue.Queue", "redirect_stdout", "redirect_stderr",
        "builtins.input", "monkey-patch",
    ]:
        assert legacy_bridge not in source

    tree = ast.parse(source)
    assert tree is not None


def test_capstone_versions_use_the_shared_ui_launcher():
    for name in ["version1.py", "version2.py"]:
        source = (CAPSTONE / name).read_text()
        assert "from engine.launcher import run_game" in source
        assert "run_game(make_game())" in source


def test_student_added_npc_gets_a_generic_portrait_without_engine_changes():
    game = AdventureGame(STAR_CRYSTAL)
    snapshot = game.snapshot()
    snapshot.update(
        focus_npc_name="Student Ranger",
        focus_npc_state="alive",
        focus_npc_mood="friendly",
    )
    key, title, drawing = choose_art(snapshot)
    assert key == "npc::student_ranger::alive"
    assert "Student Ranger" in title
    assert "Student Ranger" in drawing
