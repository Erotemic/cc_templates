from __future__ import annotations

from dataclasses import replace
import random

import pytest

from rpg_battle.api import heal
from rpg_battle.battle.battle_controller import BattleController
from rpg_battle.core.actions import skill_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.effects import effective_stat
from rpg_battle.core.rules import resolve_action
from rpg_battle.core.scripting import (
    BattlerView,
    StudentCodeError,
    build_move_context,
    smoke_test_ai_strategy,
    smoke_test_move_script,
)
from rpg_battle.render.effect_builder import PathProfile, evaluate_path_y
from rpg_battle.teaching.lab import run_move_scenario
from rpg_battle.teaching.simulate import simulate_many
from student_game import CONTENT, SCENARIOS
from student_game import workshop, workshop_assets
from student_game.catalog import GAME


def test_unknown_command_target_is_rejected_during_check() -> None:
    def bad_target(ctx):
        return heal(10, target="usr")  # type: ignore[arg-type]

    problems = smoke_test_move_script(bad_target, target_mode="single_enemy")
    assert any("unknown target 'usr'" in problem for problem in problems)


def test_unknown_command_target_is_rejected_at_runtime_too() -> None:
    def bad_target(ctx):
        return heal(10, target="usr")  # type: ignore[arg-type]

    move = replace(
        CONTENT.moves["workshop_power_strike"],
        move_id="bad_target_runtime",
        script=bad_target,
    )
    content = replace(CONTENT, moves={**CONTENT.moves, move.move_id: move})
    state = new_battle(content.encounters["workshop"], content=content)
    actor_id = state.teams[0].active_ids[0]
    target_id = state.teams[1].active_ids[0]
    with pytest.raises(StudentCodeError, match="unknown target 'usr'"):
        resolve_action(
            state,
            skill_action(actor_id, move.move_id, target_ids=(target_id,)),
            random.Random(0),
        )


def test_single_target_smoke_test_supplies_exactly_one_target() -> None:
    def requires_one(ctx):
        if len(ctx.targets) != 1:
            raise ValueError("expected one target")
        return heal(1, target=ctx.targets[0])

    assert smoke_test_move_script(requires_one, target_mode="single_enemy") == []


def test_behavior_smoke_test_uses_authored_view_ranges() -> None:
    seen = []

    def inspect_context(ctx):
        seen.append((ctx.user.max_hp, ctx.user.attack, ctx.targets[0].max_hp))
        return heal(1, target="user")

    user = BattlerView(
        "Authored Hero", 73, 73, 17, 9, 4, 8, frozenset(), "authored_user"
    )
    target = BattlerView(
        "Authored Target", 91, 91, 5, 14, 3, 2, frozenset(), "authored_target"
    )
    assert smoke_test_move_script(
        inspect_context,
        target_mode="single_enemy",
        user=user,
        targets=(target,),
    ) == []
    assert seen
    assert all(max_hp == 73 for max_hp, _, _ in seen)
    assert {attack for _, attack, _ in seen} == {17, 13}  # burn reduces effective attack
    assert all(target_max_hp == 91 for _, _, target_max_hp in seen)


def test_ai_smoke_test_rejects_enemy_target_for_self_move() -> None:
    def bad_strategy(turn):
        return turn.use("stone_ward", target=turn.enemies[0])

    problems = smoke_test_ai_strategy(
        bad_strategy,
        user_name="Crystal Guardian",
        available_move_ids=frozenset({"stone_ward"}),
        move_target_modes={"stone_ward": "self"},
    )
    assert any("invalid target" in problem for problem in problems)


def test_battler_view_exposes_effective_and_base_stats() -> None:
    state = new_battle(CONTENT.encounters["workshop"], content=CONTENT)
    actor_id = state.teams[0].active_ids[0]
    target_id = state.teams[1].active_ids[0]
    actor = state.combatants[actor_id]
    from rpg_battle.core.models import StatusState

    actor.statuses["burn"] = StatusState("burn", 3)
    context = build_move_context(state, actor_id, (target_id,))
    assert context.user.base_attack == actor.spec.attack
    assert context.user.attack == effective_stat(actor, "attack")
    assert context.user.attack < context.user.base_attack


def test_game_compile_does_not_execute_student_behavior() -> None:
    calls = []

    def counted(ctx):
        calls.append(ctx.user.name)
        return heal(1, target="user")

    changed_move = replace(workshop.power_strike, action=counted)
    moves = [changed_move if move is workshop.power_strike else move for move in GAME.moves]
    compiled = replace(GAME, moves=moves).compile()
    assert calls == []
    compiled.validate_behaviors()
    assert calls


def test_scripted_move_has_no_misleading_power_advisory() -> None:
    notes = "\n".join(str(note) for note in CONTENT.advisories())
    assert "Workshop Power Strike" not in notes
    assert workshop.power_strike.power is None
    assert workshop.power_strike.ai_power == 8


def test_cycles_one_means_one_full_sine_period() -> None:
    profile = PathProfile(mode="sine", amplitude=10, cycles=1)
    assert evaluate_path_y(profile, 0.0) == pytest.approx(0.0)
    assert evaluate_path_y(profile, 0.25) == pytest.approx(10.0)
    assert evaluate_path_y(profile, 0.5) == pytest.approx(0.0, abs=1e-9)
    assert evaluate_path_y(profile, 0.75) == pytest.approx(-10.0)
    assert evaluate_path_y(profile, 1.0) == pytest.approx(0.0, abs=1e-9)


def test_named_threshold_scenarios_hit_both_branches() -> None:
    low = SCENARIOS["threshold_25"]
    exact = SCENARIOS["threshold_26"]
    low_result = run_move_scenario(CONTENT, low)
    exact_result = run_move_scenario(CONTENT, exact)
    low_power = [
        event["command_power"]
        for event in low_result.events
        if event.get("scripted") and event.get("type") == "damage"
    ]
    exact_power = [
        event["command_power"]
        for event in exact_result.events
        if event.get("scripted") and event.get("type") == "damage"
    ]
    assert low_power == [18]
    assert exact_power == [8]


def test_chain_scenario_exercises_both_loop_decisions() -> None:
    scenario = SCENARIOS["chain_lightning"]
    result = run_move_scenario(CONTENT, scenario)
    powers = [
        event["command_power"]
        for event in result.events
        if event.get("scripted") and event.get("type") == "damage"
    ]
    assert powers == [8, 14]


def test_healing_lab_uses_an_actual_ally_target() -> None:
    scenario = SCENARIOS["healing"]
    result = run_move_scenario(CONTENT, scenario)
    assert next(iter(result.targets_after.values())) > next(iter(result.targets_before.values()))
    assert result.actor_after == result.actor_before


def test_restart_reuses_original_seed() -> None:
    controller = BattleController(CONTENT.encounters["workshop"], seed=123, content=CONTENT)
    first = controller.rng.random()
    controller.restart()
    assert controller.rng.random() == first


def test_workshop_registers_every_content_kind_it_defines() -> None:
    assert workshop_assets.workshop_palette.palette_id in CONTENT.palettes
    assert workshop_assets.workshop_sprite.sprite_id in CONTENT.sprites
    assert workshop_assets.workshop_impact.effect_id in CONTENT.effects
    assert workshop_assets.workshop_hit.sound_id in CONTENT.sound_effects
    assert workshop_assets.workshop_theme.music_id in CONTENT.music_tracks


def test_balance_scenario_exercises_both_power_strike_branches() -> None:
    scenario = SCENARIOS["balance"]
    results = simulate_many(
        CONTENT,
        scenario.encounter_id,
        runs=20,
        seed=scenario.seed,
        state_setup=scenario.apply_to_state,
    )
    powers = {
        event["command_power"]
        for result in results
        for event in result.events
        if event.get("move_id") == "workshop_power_strike"
        and event.get("type") == "damage"
    }
    assert {8, 18} <= powers
