from __future__ import annotations

from dataclasses import replace
import random

from rpg_battle.core.actions import skill_action
from rpg_battle.core.ai import choose_ai_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.models import EncounterSpec, StatusState, TeamSpec
from rpg_battle.core.rules import resolve_action
from rpg_battle.teaching.lab import run_move_lab
from rpg_battle.teaching.simulate import simulate_many
from student_game import CONTENT
from student_game import characters, workshop


def test_workshop_is_real_registered_game_content() -> None:
    assert "workshop_power_strike" in CONTENT.moves
    assert "workshop_chain_lightning" in CONTENT.moves
    assert "workshop_hero" in CONTENT.characters
    assert "workshop" in CONTENT.encounters


def test_move_lab_is_deterministic_and_exposes_conditional_behavior() -> None:
    healthy = run_move_lab(
        CONTENT,
        "workshop_power_strike",
        user_char_id="workshop_hero",
        target_char_ids=["spirit"],
        user_hp=50,
        seed=7,
    )
    healthy_again = run_move_lab(
        CONTENT,
        "workshop_power_strike",
        user_char_id="workshop_hero",
        target_char_ids=["spirit"],
        user_hp=50,
        seed=7,
    )
    desperate = run_move_lab(
        CONTENT,
        "workshop_power_strike",
        user_char_id="workshop_hero",
        target_char_ids=["spirit"],
        user_hp=10,
        seed=7,
    )
    assert healthy.targets_after == healthy_again.targets_after
    healthy_damage = (
        next(iter(healthy.targets_before.values()))
        - next(iter(healthy.targets_after.values()))
    )
    desperate_damage = (
        next(iter(desperate.targets_before.values()))
        - next(iter(desperate.targets_after.values()))
    )
    assert desperate_damage > healthy_damage
    assert any("power_strike_logic" in line for line in healthy.trace_lines)


def test_script_loop_can_target_each_battler_view_once() -> None:
    player = TeamSpec(
        name="Loop Tester",
        members=("workshop_hero",),
        starting_active=("workshop_hero",),
    )
    enemy = TeamSpec(
        name="Two Targets",
        members=("spirit", "guardian"),
        starting_active=("spirit", "guardian"),
        controller_type="ai",
    )
    encounter = EncounterSpec(
        encounter_id="loop_test",
        title="Loop Test",
        player_team=player,
        enemy_team=enemy,
        active_limits=(1, 2),
    )
    state = new_battle(encounter, content=CONTENT)
    actor_id = state.teams[0].active_ids[0]
    targets = tuple(state.teams[1].active_ids)
    state.combatants[targets[1]].statuses["burn"] = StatusState("burn", 3)

    events = resolve_action(
        state,
        skill_action(actor_id, "workshop_chain_lightning", target_ids=targets),
        random.Random(3),
    )
    damage_events = [event for event in events if event["type"] == "damage"]
    assert len(damage_events) == 2
    assert {event["target_id"] for event in damage_events} == set(targets)


def test_student_enemy_strategy_uses_normal_python_branching() -> None:
    state = new_battle(CONTENT.encounters["workshop"], content=CONTENT)
    enemy_id = state.teams[1].active_ids[0]

    action = choose_ai_action(state, enemy_id, random.Random(0))
    assert action.kind == "skill"
    assert action.move_id == "arc_bolt"

    state.combatants[enemy_id].current_hp = 1
    action = choose_ai_action(state, enemy_id, random.Random(0))
    assert action.kind == "defend"


def test_headless_simulator_repeats_from_the_same_seed() -> None:
    first = simulate_many(CONTENT, "workshop", runs=3, seed=11)
    second = simulate_many(CONTENT, "workshop", runs=3, seed=11)
    assert [(result.winner, result.rounds) for result in first] == [
        (result.winner, result.rounds) for result in second
    ]


def test_check_reports_bad_custom_move_return_with_source_location() -> None:
    def bad_move(ctx):
        return 123

    broken_move = replace(workshop.power_strike, action=bad_move)
    broken_moves = dict(CONTENT.moves)
    broken_moves[broken_move.move_id] = broken_move.compile()
    broken = replace(CONTENT, moves=broken_moves)
    report = "\n".join(str(issue) for issue in broken.validate())
    assert "custom function" in report
    assert "must return a move command" in report


def test_check_smoke_tests_student_ai_strategy() -> None:
    def bad_strategy(turn):
        return 123

    broken_team = replace(CONTENT.teams["workshop_enemy"], strategy=bad_strategy)
    broken_teams = dict(CONTENT.teams)
    broken_teams["workshop_enemy"] = broken_team
    broken = replace(CONTENT, teams=broken_teams)
    report = "\n".join(str(issue) for issue in broken.validate())
    assert "strategy" in report
    assert "turn.use(...) or turn.defend()" in report
