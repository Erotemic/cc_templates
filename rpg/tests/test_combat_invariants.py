"""Engine contracts, exercised without graphics or special classroom machinery.

Tests describe observable behavior rather than source layout or user-facing copy.
"""

from dataclasses import replace
import random

import pytest

from rpg_battle.api import add_status, change_stat, damage, heal
from rpg_battle.battle.battle_controller import BattleController
from rpg_battle.core.actions import attack_action, skill_action
from rpg_battle.core.battle_state import get_combatant, living_enemy_ids, new_battle
from rpg_battle.core.models import EncounterSpec, MoveEffect, StatusState, TeamSpec
from rpg_battle.core.rules import finish_round, resolve_action
from rpg_battle.teaching.simulate import simulate_once
from student_game import CONTENT


def content_with_move(*, kind, power=0, target_mode="single_enemy", script=None,
                      effects=(), accuracy=1.0):
    original = CONTENT.moves["workshop_power_strike"]
    move = replace(original, kind=kind, power=power, target_mode=target_mode,
                   script=script, effects=effects, accuracy=accuracy)
    hero = replace(CONTENT.characters["workshop_hero"], magic=0)
    return replace(
        CONTENT,
        moves={**CONTENT.moves, move.move_id: move},
        characters={**CONTENT.characters, hero.char_id: hero},
    )


def play(content, *, seed=1, target_mode="single_enemy", hp=25):
    state = new_battle(content.encounters["workshop"], content=content)
    actor_id = state.teams[0].active_ids[0]
    target_id = (actor_id if target_mode == "self" else state.teams[1].active_ids[0])
    get_combatant(state, target_id).current_hp = hp
    events = resolve_action(
        state, skill_action(actor_id, "workshop_power_strike", (target_id,)),
        random.Random(seed),
    )
    return state, events, target_id


def effects_and_hp(state, target_id, events):
    target = get_combatant(state, target_id)
    return target.current_hp, dict(target.temp_bonuses), dict(target.statuses), [
        (event["type"], event.get("amount"), event.get("hp_before"),
         event.get("hp_after"))
        for event in events
        if event["type"] in {"damage", "heal", "miss"}
    ]


def test_controller_rejects_other_fighters_action_without_consuming_turn():
    session = BattleController(content=CONTENT, seed=4)
    session.advance_to_next_turn()  # round announced
    session.advance_to_next_turn()  # current fighter selected
    actor_id = session.current_actor_id
    assert actor_id is not None
    other = next(cid for cid in session.state.combatants
                 if session.state.combatants[cid].team_index !=
                 session.state.combatants[actor_id].team_index)
    before_hp = {cid: c.current_hp for cid, c in session.state.combatants.items()}
    before_rng = session.rng.getstate()
    with pytest.raises(ValueError, match="Wrong acting fighter"):
        session.submit_action(attack_action(other, (actor_id,)))
    assert {cid: c.current_hp for cid, c in session.state.combatants.items()} == before_hp
    assert session.rng.getstate() == before_rng
    assert session.current_actor_id == actor_id
    enemies = living_enemy_ids(session.state, actor_id)
    assert enemies
    events = session.submit_action(attack_action(actor_id, (enemies[0],)))
    assert session.current_actor_id is None
    assert any(event["type"] == "damage" for event in events)


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4, 9])
def test_script_and_declaration_share_damage_and_accuracy(seed):
    definition = content_with_move(kind="magical", power=11, accuracy=0.7)
    scripted = content_with_move(kind="magical", power=11, accuracy=0.7,
                                 script=lambda ctx: damage(11, magical=True))
    a, events_a, tid_a = play(definition, seed=seed)
    b, events_b, tid_b = play(scripted, seed=seed)
    assert effects_and_hp(a, tid_a, events_a) == effects_and_hp(b, tid_b, events_b)
    for events in (events_a, events_b):
        for event in events:
            if event["type"] == "damage":
                assert event["hp_before"] >= event["hp_after"] >= 0
                assert event["hp_lost"] == event["hp_before"] - event["hp_after"]


def test_script_and_declaration_share_healing_floor_and_snapshots():
    declared = content_with_move(kind="heal", power=0, target_mode="self")
    scripted = content_with_move(kind="heal", power=0, target_mode="self",
                                 script=lambda ctx: heal(0))
    a, events_a, tid_a = play(declared, target_mode="self", hp=4)
    b, events_b, tid_b = play(scripted, target_mode="self", hp=4)
    assert effects_and_hp(a, tid_a, events_a) == effects_and_hp(b, tid_b, events_b)
    healing = next(e for e in events_a if e["type"] == "heal")
    assert healing["hp_before"] == 4
    assert healing["amount"] == 8
    assert healing["hp_after"] == 12


@pytest.mark.parametrize("seed", [0, 1, 3])
def test_script_and_declaration_share_secondary_effect_rules(seed):
    declared = content_with_move(kind="status", target_mode="single_enemy", effects=(
        MoveEffect(status="burn", chance=0.75, duration=3),
        MoveEffect(stat="defense", stages=-1, chance=0.4),
    ))
    scripted = content_with_move(kind="status", target_mode="single_enemy", script=lambda ctx: [
        add_status("burn", turns=3, chance=0.75),
        change_stat("defense", -1, chance=0.4),
    ])
    a, events_a, tid_a = play(declared, seed=seed)
    b, events_b, tid_b = play(scripted, seed=seed)
    assert effects_and_hp(a, tid_a, events_a) == effects_and_hp(b, tid_b, events_b)


def simultaneous_poison_content():
    def defend(turn):
        return turn.defend()

    battle = EncounterSpec(
        "poison_draw", "Poison draw",
        TeamSpec("Red", ("workshop_hero",), controller_type="ai", strategy=defend),
        TeamSpec("Blue", ("workshop_hero",), controller_type="ai", strategy=defend),
        (1, 1),
    )
    return replace(CONTENT, encounters={**CONTENT.encounters, battle.encounter_id: battle})


def poison_setup(state):
    for fighter in state.combatants.values():
        fighter.current_hp = 1
        fighter.statuses["poison"] = StatusState("poison", 2)


def test_simultaneous_ko_is_terminal_draw_not_running_battle():
    content = simultaneous_poison_content()
    state = new_battle(content.encounters["poison_draw"], content=content)
    poison_setup(state)
    events = finish_round(state)
    endings = [event for event in events if event["type"] == "battle_end"]
    assert len(endings) == 1
    assert endings[0]["outcome"] == state.outcome == "draw"
    assert state.winner is None
    assert len([event for event in events if event["type"] == "ko"]) == 2
    assert not state.pending_replacements
    assert finish_round(state) == []
    assert not resolve_action(state, attack_action("t0_c0", ("t1_c0",)))


def test_simulator_reports_real_draw_and_distinguishes_step_limit():
    content = simultaneous_poison_content()
    draw_result = simulate_once(content, "poison_draw", state_setup=poison_setup,
                                max_steps=20)
    assert draw_result.outcome == "draw"
    assert draw_result.winner is None
    assert sum(event["type"] == "battle_end" for event in draw_result.events) == 1
    assert all("hp_after" in event for event in draw_result.events
               if event["type"] == "status_tick")
    unfinished = simulate_once(content, "poison_draw", max_steps=2)
    assert unfinished.outcome == "ongoing"
    assert unfinished.winner is None
    assert not any(event["type"] == "battle_end" for event in unfinished.events)


def test_multiple_damage_events_preserve_intermediate_hp_states():
    content = content_with_move(
        kind="physical", power=0,
        script=lambda ctx: [damage(6), damage(9)],
    )
    state, events, target_id = play(content, seed=5, hp=45)
    hits = [event for event in events if event["type"] == "damage"]
    assert len(hits) == 2
    assert hits[0]["hp_before"] == 45
    assert hits[0]["hp_after"] == hits[1]["hp_before"]
    assert hits[1]["hp_after"] == get_combatant(state, target_id).current_hp


def test_core_has_no_reverse_dependency_on_ui_or_teaching():
    import ast
    from pathlib import Path

    core = Path(__file__).resolve().parents[1] / "src/rpg_battle/core"
    for module_path in core.glob("*.py"):
        tree = ast.parse(module_path.read_text(encoding="utf8"))
        dependencies = [
            node.module for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        ]
        dependencies.extend(
            alias.name
            for node in ast.walk(tree) if isinstance(node, ast.Import)
            for alias in node.names
        )
        assert not any(
            name == "student_game" or name.startswith((
                "rpg_battle.teaching", "rpg_battle.render", "rpg_battle.battle"
            ))
            for name in dependencies
        ), module_path.name
