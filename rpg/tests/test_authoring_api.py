from __future__ import annotations

from dataclasses import replace
import random

import pytest

from student_game import CONTENT
from student_game import characters, moves
from student_game.catalog import GAME
from rpg_battle.api import Battle, Move, Palette, Sprite, Team
from rpg_battle.catalog import ContentValidationError, format_validation_report
from rpg_battle.core.actions import attack_action, skill_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.models import EncounterSpec, TeamSpec
from rpg_battle.core.rules import resolve_action


def _script_damage_at_hp(hp: int) -> int:
    player = TeamSpec(
        name="Script Test Heroes",
        members=(characters.knight.character_id,),
        starting_active=(characters.knight.character_id,),
    )
    enemy = TeamSpec(
        name="Script Test Enemy",
        members=(characters.spirit.character_id,),
        controller_type="ai",
        starting_active=(characters.spirit.character_id,),
    )
    encounter = EncounterSpec(
        encounter_id="script_test",
        title="Script Test",
        player_team=player,
        enemy_team=enemy,
        active_limits=(1, 1),
        music_track_id=CONTENT.default_battle_track,
    )
    state = new_battle(encounter, content=CONTENT)
    actor_id = state.teams[0].active_ids[0]
    target_id = state.teams[1].active_ids[0]
    state.combatants[actor_id].current_hp = hp
    events = resolve_action(
        state,
        skill_action(actor_id, moves.desperate_strike.move_id, target_ids=(target_id,)),
        random.Random(17),
    )
    damage_events = [event for event in events if event["type"] == "damage"]
    assert len(damage_events) == 1
    return damage_events[0]["amount"]


def test_custom_move_function_can_use_normal_python_branching() -> None:
    healthy_damage = _script_damage_at_hp(characters.knight.hp)
    desperate_damage = _script_damage_at_hp(10)
    assert desperate_damage > healthy_damage



def test_scripted_move_separates_real_power_from_ai_estimate() -> None:
    def scripted(ctx):
        from rpg_battle.api import damage

        return damage(12)

    move = Move("Scripted", action=scripted, ai_power=7)
    compiled = move.compile()
    assert compiled.power == 7

    misleading = Move("Misleading", action=scripted, power=7)
    with pytest.raises(ContentValidationError, match="cannot use power"):
        misleading.compile()


def test_declarative_move_rejects_ai_power() -> None:
    move = Move("Normal", power=7, ai_power=5)
    with pytest.raises(ContentValidationError, match="ai_power is only for moves with action"):
        move.compile()

def test_student_game_uses_direct_object_references() -> None:
    assert characters.knight.moves[0] is moves.shield_bash
    assert characters.knight.sprite.sprite_id == "knight_dawn"
    assert CONTENT.characters["knight"].move_ids == ("shield_bash", "stone_ward", "strike")


def test_sprite_authored_scale_compiles_for_layout_fitting() -> None:
    palette = Palette("Test", body=(1, 2, 3), accent=(4, 5, 6))
    sprite = Sprite("Large Drawing", palette, scale=0.5).circle((0, 0), 20)
    compiled = sprite.compile()
    assert compiled["scale"] == 0.5
    assert compiled["shapes"][0]["radius"] == 20


def test_validation_report_is_short_and_actionable() -> None:
    broken = replace(CONTENT, default_battle_track="missing_song")
    issues = broken.validate()
    report = format_validation_report(issues)
    assert 'default battle music "missing_song" is not defined' in report
    assert "Your game has 1 problem:" in report


def test_duplicate_ids_get_a_student_facing_error() -> None:
    duplicate = Move("Another Strike", id="strike", power=1)
    broken_game = replace(GAME, moves=[*GAME.moves, duplicate])
    with pytest.raises(ContentValidationError, match="two objects use the id 'strike'"):
        broken_game.compile()


def test_unregistered_team_is_reported_by_validation() -> None:
    outsider = Team(
        "Unregistered Opponent",
        members=[characters.spirit],
        controller="computer",
    )
    battle = Battle(
        "Broken Battle",
        player=GAME.teams[0],
        enemy=outsider,
    )
    broken_game = replace(GAME, battles=[*GAME.battles, battle])
    with pytest.raises(ContentValidationError, match="enemy team is not registered"):
        broken_game.compile()


def test_basic_attack_is_game_content_not_a_hard_coded_move_id() -> None:
    alternate = replace(
        CONTENT,
        presentation=replace(
            CONTENT.presentation,
            basic_attack_move_id=moves.arc_bolt.move_id,
        ),
    )
    state = new_battle(content=alternate)
    actor_id = state.teams[0].active_ids[0]
    target_id = state.teams[1].active_ids[0]
    events = resolve_action(
        state,
        attack_action(actor_id, target_ids=(target_id,)),
        random.Random(2),
    )
    move_events = [event for event in events if event["type"] == "move"]
    assert move_events[0]["move_id"] == moves.arc_bolt.move_id


def test_presentation_refs_are_validated() -> None:
    broken = replace(
        CONTENT,
        presentation=replace(CONTENT.presentation, menu_confirm_sound_id="missing_blip"),
    )
    report = format_validation_report(broken.validate())
    assert 'menu confirm sound "missing_blip" is not defined' in report
