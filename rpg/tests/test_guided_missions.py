"""Four RPG guided missions are integrated with real battle rules.

Tests deliberately do NOT expect a particular student solution. A correct
healer, coward, sword, or boss implementation must still pass these checks.
"""

from __future__ import annotations

import random
import subprocess
import sys
from pathlib import Path

import pytest

from rpg_battle.core.ai import choose_ai_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.rules import validate_action
from rpg_battle.teaching.lab import run_move_lab
from rpg_battle.teaching.simulate import simulate_once
from student_game import CONTENT, SCENARIOS
from student_game import guided_battles, student


FOUR_BATTLES = (
    "lesson_healer_battle", "lesson_coward_battle",
    "lesson_sword_battle", "lesson_boss_battle",
)
EIGHT_SCENARIOS = (
    "healer_injured", "healer_healthy", "coward_low_hp",
    "coward_healthy", "sword_low_hp", "sword_healthy",
    "boss_low_hp", "boss_healthy",
)


def test_all_four_battles_are_playable_registered_content():
    for battle in FOUR_BATTLES:
        encounter = CONTENT.encounters[battle]
        state = new_battle(encounter, content=CONTENT)
        assert len(state.teams) == 2
        assert state.teams[0].active_ids
        assert state.teams[1].active_ids
        assert state.outcome == "ongoing"


def test_each_scenario_is_valid_and_applies_its_starting_hp():
    for name in EIGHT_SCENARIOS:
        scenario = SCENARIOS[name]
        assert scenario.validate(CONTENT) == [], name
        state = new_battle(CONTENT.encounters[scenario.encounter_id], content=CONTENT)
        scenario.apply_to_state(state)
        by_name = {b.spec.char_id: b for b in state.combatants.values()}
        for char_id, hp in scenario.hp_by_character:
            assert by_name[char_id].current_hp == hp
        assert state.outcome == "ongoing"


def test_healer_is_present_with_injured_ally_and_a_real_spell():
    scenario = SCENARIOS["healer_injured"]
    state = new_battle(CONTENT.encounters[scenario.encounter_id], content=CONTENT)
    scenario.apply_to_state(state)
    ally_ids = state.teams[1].active_ids
    healer = next(state.combatants[cid] for cid in ally_ids
                  if state.combatants[cid].spec.char_id == "lesson_healer")
    friend = next(state.combatants[cid] for cid in ally_ids
                  if state.combatants[cid].spec.char_id == "lesson_shieldbearer")
    assert friend.hp_ratio() < 0.30
    assert "healing_light" in healer.spec.move_ids
    assert healer.current_mana >= CONTENT.moves["healing_light"].mana_cost
    # Dispatch through the real strategy and verify legality, NOT Attack vs Heal.
    result = choose_ai_action(state, healer.combatant_id, random.Random(1))
    assert validate_action(state, result).actor_id == healer.combatant_id


@pytest.mark.parametrize("scenario_name", (
    "coward_low_hp", "coward_healthy", "boss_low_hp", "boss_healthy",
))
def test_enemy_strategies_return_legal_turns(scenario_name):
    scenario = SCENARIOS[scenario_name]
    state = new_battle(CONTENT.encounters[scenario.encounter_id], content=CONTENT)
    scenario.apply_to_state(state)
    enemy_actor = state.teams[1].active_ids[0]
    result = choose_ai_action(state, enemy_actor, random.Random(3))
    assert validate_action(state, result).actor_id == enemy_actor


def test_sword_is_an_equipped_scripted_move_with_real_damage():
    move = CONTENT.moves["lesson_cursed_sword"]
    assert move.script is student.cursed_sword_logic
    assert move.target_mode == "single_enemy"
    assert "lesson_cursed_sword" in CONTENT.characters["lesson_swordfighter"].move_ids
    result = run_move_lab(
        CONTENT, "lesson_cursed_sword",
        user_char_id="lesson_swordfighter", target_char_ids=["spirit"],
        user_hp=18, seed=5,
    )
    assert result.targets_after
    assert all(result.targets_after[k] < before
               for k, before in result.targets_before.items())


@pytest.mark.parametrize("scenario_name", (
    "healer_injured", "coward_low_hp", "sword_low_hp", "boss_low_hp",
))
def test_scenarios_run_to_completion_without_pygame(scenario_name):
    scenario = SCENARIOS[scenario_name]
    result = simulate_once(
        CONTENT, scenario.encounter_id, seed=5,
        state_setup=scenario.apply_to_state, max_steps=600,
    )
    assert result.outcome != "ongoing"
    assert result.winner in (0, 1, None)


def test_independent_challenge_board_does_not_import_pygame():
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "student_game/challenge.py"],
        cwd=project_root, capture_output=True, text=True, check=True,
    )
    assert "INDEPENDENT RPG CHALLENGES" in result.stdout
    assert "Charge and release" in result.stdout


def test_prior_workshop_and_default_game_are_unchanged():
    assert CONTENT.default_encounter_id == "default"
    assert "workshop" in CONTENT.encounters
    assert "workshop_power_strike" in CONTENT.moves
    assert CONTENT.encounters["lesson_sword_battle"].player_team.name == "Cursed Sword Hero"
