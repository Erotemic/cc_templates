"""Regression checks for student edits and the classroom command-line workflows."""

from dataclasses import replace
import random
import sys

import pytest

from rpg_battle.api import add_status, change_stat, damage, heal
from rpg_battle.core.actions import skill_action
from rpg_battle.core.ai import choose_ai_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.rules import resolve_action
from rpg_battle.core.scripting import StudentCodeError, smoke_test_move_script
from rpg_battle.teaching.lab import run_move_lab, run_move_scenario
from rpg_battle.teaching.simulate import simulate_once
from student_game import CONTENT, SCENARIOS


def with_script(script, **move_changes):
    move = replace(CONTENT.moves["workshop_power_strike"], script=script, **move_changes)
    return replace(CONTENT, moves={**CONTENT.moves, move.move_id: move})


@pytest.mark.parametrize(
    "result, message",
    [
        (123, "must return a move command"),
        ([damage(8), 123], "move command #2"),
        (damage("ten"), "power must be a finite number"),
        (damage(float("inf")), "power must be a finite number"),
        (damage(float("nan")), "power must be a finite number"),
        (damage(8, magical="False"), "magical must be True or False"),
        (heal(10, target=123), "target must be"),
        (add_status([], turns=1), "status name must be"),
        (add_status("burn", turns=1.5), "positive integer"),
        (add_status("burn", chance="often"), "chance must be"),
        (change_stat([], 1), "unknown stat"),
        (change_stat("attack", 1.5), "stat stages must be an integer"),
    ],
)
def test_bad_returns_have_source_aware_errors_before_mutation(result, message):
    def student_move(ctx):
        return result

    content = with_script(student_move)
    state = new_battle(content.encounters["workshop"], content=content)
    actor_id = state.teams[0].active_ids[0]
    targets = tuple(state.teams[1].active_ids)
    before = {cid: c.current_hp for cid, c in state.combatants.items()}
    with pytest.raises(StudentCodeError) as error:
        resolve_action(state, skill_action(actor_id, "workshop_power_strike", targets), random.Random(3))
    assert message in str(error.value)
    assert "test_teaching_regressions.py:" in str(error.value)
    assert {cid: c.current_hp for cid, c in state.combatants.items()} == before
    assert any(message in problem for problem in smoke_test_move_script(student_move))


def test_all_allies_smoke_context_includes_the_user():
    def ally_move(ctx):
        assert any(target is ctx.user for target in ctx.targets)
        return heal(1)

    assert smoke_test_move_script(ally_move, target_mode="all_allies") == []


def test_behavior_check_uses_real_target_counts_and_effective_stats():
    def one_enemy(ctx):
        assert len(ctx.targets) == 1
        if "burn" in ctx.user.statuses:
            assert ctx.user.attack == int(ctx.user.base_attack * 0.8)
        return damage(8)

    content = with_script(one_enemy, target_mode="all_enemies")
    content = replace(
        content,
        encounters={"workshop": content.encounters["workshop"]},
        default_encounter_id="workshop",
    )
    assert content.validate_behaviors() == []


def test_all_ally_strategy_accepts_target_order_and_rejects_duplicates():
    def strategy(turn):
        return turn.use("fractal_veil", target=(*turn.allies, turn.user))

    encounter = CONTENT.encounters["frontline_brawl"]
    encounter = replace(encounter, player_team=replace(encounter.player_team, strategy=strategy))
    state = new_battle(encounter, content=CONTENT)
    actor_id = next(cid for cid in state.teams[0].active_ids
                    if state.combatants[cid].spec.char_id == "runesage")
    action = choose_ai_action(state, actor_id)
    assert action.target_ids == tuple(state.teams[0].active_ids)

    state.teams[0].strategy = lambda turn: turn.use("fractal_veil", target=(turn.user, turn.user))
    with pytest.raises(StudentCodeError, match="invalid target"):
        choose_ai_action(state, actor_id)


def test_self_healing_is_a_legal_lab_target():
    result = run_move_lab(
        CONTENT, "healing_light", user_char_id="druid", target_char_ids=["druid"], user_hp=10
    )
    assert result.actor_after == 35
    assert tuple(result.targets_after.values()) == (35,)


def test_self_target_statuses_apply_to_the_actor():
    content = with_script(lambda ctx: damage(8), target_mode="self")
    result = run_move_lab(
        content, "workshop_power_strike", user_char_id="workshop_hero",
        target_char_ids=[], target_statuses=["burn"], seed=3,
    )
    assert result.actor_attack == 7
    assert tuple(result.target_statuses.values()) == (("burn",),)


def test_no_target_move_can_return_a_command_for_its_user():
    content = with_script(lambda ctx: heal(10, target="user"), target_mode="none")
    result = run_move_lab(
        content, "workshop_power_strike", user_char_id="workshop_hero",
        target_char_ids=[], user_hp=10,
    )
    assert result.actor_after == 29
    assert result.target_names == {}


def test_scenario_lab_and_play_share_one_setup():
    scenario = replace(SCENARIOS["threshold_25"], hp_by_character=(("workshop_hero", 32),))
    result = run_move_scenario(CONTENT, scenario)
    state = new_battle(CONTENT.encounters[scenario.encounter_id], content=CONTENT)
    scenario.apply_to_state(state)
    actor_id = state.teams[0].active_ids[0]
    targets = tuple(state.teams[1].active_ids)
    assert result.actor_before == state.combatants[actor_id].current_hp == 32
    events = resolve_action(state, skill_action(actor_id, scenario.move_id, targets), random.Random(scenario.seed))
    assert result.events == events


def test_play_does_not_smoke_test_unrelated_student_code(monkeypatch, capsys):
    from rpg_battle import __main__ as launcher, game

    def unused_move(ctx):
        raise AssertionError("unused function ran")

    content = replace(CONTENT, moves={
        **CONTENT.moves, "desperate_strike": replace(CONTENT.moves["desperate_strike"], script=unused_move)
    })
    launched = []
    monkeypatch.setattr(launcher, "CONTENT", content)
    monkeypatch.setattr(game, "run_game", lambda **kwargs: launched.append(kwargs))
    monkeypatch.setattr(sys, "argv", ["main.py", "--scenario", "threshold_25"])
    launcher.main()
    assert len(launched) == 1

    monkeypatch.setattr(sys, "argv", ["main.py", "--check"])
    with pytest.raises(SystemExit) as error:
        launcher.main()
    assert error.value.code == 2
    assert "unused function ran" in capsys.readouterr().err


def test_lab_reports_runtime_errors_and_can_show_tracebacks(monkeypatch, capsys):
    from rpg_battle.teaching import lab

    content = with_script(lambda ctx: 123)
    monkeypatch.setattr(sys, "argv", ["lab.py", "move"])
    with pytest.raises(SystemExit) as error:
        lab.main(content)
    assert error.value.code == 3
    output = capsys.readouterr().err
    assert "must return a move command" in output
    assert "Traceback (most recent call last)" not in output

    monkeypatch.setattr(sys, "argv", ["lab.py", "move", "--debug-traceback"])
    with pytest.raises(StudentCodeError) as error:
        lab.main(content)
    assert isinstance(error.value.__cause__, TypeError)


def test_simulation_counts_commands_even_when_they_miss():
    content = with_script(lambda ctx: damage(8), accuracy=0)
    hero = replace(content.characters["workshop_hero"], move_ids=("workshop_power_strike",))
    content = replace(content, characters={**content.characters, hero.char_id: hero})
    result = simulate_once(content, "workshop", seed=3, max_steps=10)
    assert result.winner is None
    assert result.scripted_commands
    assert len(result.scripted_commands) == sum(e.get("type") == "miss" for e in result.events)


def test_simulation_damage_counts_hp_lost_without_overkill():
    content = with_script(lambda ctx: damage(1000))
    hero = replace(content.characters["workshop_hero"], move_ids=("workshop_power_strike",))
    content = replace(content, characters={**content.characters, hero.char_id: hero})

    def setup(state):
        state.combatants[state.teams[1].active_ids[0]].current_hp = 3

    result = simulate_once(content, "workshop", seed=3, max_steps=3, state_setup=setup)
    assert result.winner == 0
    assert result.damage_dealt == (3, 0)


def test_game_cleans_up_if_scenario_initialization_fails(monkeypatch):
    import pygame
    from rpg_battle import game

    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")

    def broken_setup(state):
        raise StudentCodeError("bad scenario")

    with pytest.raises(StudentCodeError, match="bad scenario"):
        game.run_game(content=CONTENT, state_setup=broken_setup)
    assert not pygame.get_init()


@pytest.mark.parametrize("hp_setup", [(("typo_hero", 25),), (("workshop_hero", 53),)])
def test_scenario_checker_rejects_silently_changed_setup(hp_setup):
    scenario = replace(SCENARIOS["threshold_25"], hp_by_character=hp_setup)
    assert scenario.validate(CONTENT)
    with pytest.raises(ValueError, match="scenario 'threshold_25'"):
        run_move_scenario(CONTENT, scenario)


def test_checker_reports_broken_named_scenario(monkeypatch, capsys):
    from rpg_battle import __main__ as launcher

    scenario = replace(SCENARIOS["threshold_25"], encounter_id="typo_battle")
    monkeypatch.setattr(launcher, "SCENARIOS", {scenario.scenario_id: scenario})
    monkeypatch.setattr(sys, "argv", ["main.py", "--check"])
    with pytest.raises(SystemExit) as error:
        launcher.main()
    assert error.value.code == 2
    assert "unknown encounter 'typo_battle'" in capsys.readouterr().err
