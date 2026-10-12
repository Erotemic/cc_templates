"""Mana is authoritative combat state; controllers only request actions."""

from dataclasses import replace
import random

import pytest

from rpg_battle.battle.session import BattleSession
from rpg_battle.core.actions import attack_action, defend_action, skill_action, switch_action
from rpg_battle.core.ai import choose_ai_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.mana import ATTACK_MANA_RECOVERY, DEFEND_MANA_RECOVERY
from rpg_battle.core.rules import resolve_action
from rpg_battle.core.scripting import build_turn_context
from student_game import CONTENT
from team_arena.engine import ARENA_ID, GUARDIAN, MAGE, content_for_match
from team_arena.recording import record_match, verify_replay


def arena_state():
    bundle = content_for_match("left", None, "right", None)
    state = new_battle(bundle.encounters[ARENA_ID], content=bundle)
    return state


def fighter(state, team=0, index=0):
    return state.combatants[state.teams[team].active_ids[index]]


def test_every_fighter_starts_with_own_full_mana_and_public_readonly_view():
    state = arena_state()
    guardian, mage = fighter(state), fighter(state, 0, 1)
    assert guardian.current_mana == guardian.spec.max_mana == GUARDIAN.max_mana
    assert mage.current_mana == mage.spec.max_mana == MAGE.max_mana
    turn = build_turn_context(state, guardian.combatant_id)
    assert turn.user.mana == guardian.current_mana
    assert turn.user.max_mana == guardian.spec.max_mana
    assert turn.user.mana_ratio == 1.0
    assert turn.skill_costs["arena_crush"] == 6
    assert turn.can_use("arena_crush")
    assert not turn.can_use("arena_spark")
    with pytest.raises(TypeError):
        turn.skill_costs["arena_crush"] = 0


def test_skill_spends_before_move_and_only_for_actor():
    state = arena_state()
    actor = fighter(state)
    mage = fighter(state, 0, 1)
    target = fighter(state, 1, 0)
    events = resolve_action(state, skill_action(actor.combatant_id, "arena_crush",
                                                 (target.combatant_id,)), random.Random(2))
    assert actor.current_mana == GUARDIAN.max_mana - 6
    assert mage.current_mana == MAGE.max_mana
    assert target.current_mana == GUARDIAN.max_mana
    change = next(e for e in events if e["type"] == "mana")
    assert (change["mana_before"], change["mana_after"], change["amount"]) == (12, 6, -6)
    assert [e["type"] for e in events].index("mana") < [e["type"] for e in events].index("move")


def test_invalid_skill_cannot_change_state_rng_or_consume_session_turn():
    bundle = content_for_match("left", None, "right", None)
    session = BattleSession(bundle.encounters[ARENA_ID], content=bundle, seed=8)
    for _ in range(5):
        if session.request is not None:
            break
        session.next_step()
    request = session.request
    assert request is not None and request.kind == "action"
    actor = session.state.combatants[request.actor_id]
    actor.current_mana = 1
    skill = "arena_crush" if "arena_crush" in actor.spec.move_ids else "arena_spark"
    before_hp = {cid: c.current_hp for cid, c in session.state.combatants.items()}
    before_rng = session.rng.getstate()
    with pytest.raises(ValueError, match="Attack or Defend"):
        session.submit_action(skill_action(actor.combatant_id, skill))
    assert session.rng.getstate() == before_rng
    assert {cid: c.current_hp for cid, c in session.state.combatants.items()} == before_hp
    assert actor.current_mana == 1
    assert session.request == request
    with pytest.raises(ValueError, match="Attack or Defend"):
        build_turn_context(session.state, actor.combatant_id).skill(skill)
    assert not build_turn_context(session.state, actor.combatant_id).can_use(skill)
    assert session.submit_action(attack_action(actor.combatant_id))
    assert actor.current_mana == 1 + ATTACK_MANA_RECOVERY


def test_attack_and_defend_regen_are_capped_and_cost_nothing():
    state = arena_state()
    actor = fighter(state)
    enemy = fighter(state, 1, 0)
    actor.current_mana = 0
    events = resolve_action(state, attack_action(actor.combatant_id, (enemy.combatant_id,)))
    assert actor.current_mana == ATTACK_MANA_RECOVERY
    assert any(e["type"] == "mana" and e["amount"] == ATTACK_MANA_RECOVERY for e in events)
    events = resolve_action(state, defend_action(actor.combatant_id))
    assert actor.current_mana == ATTACK_MANA_RECOVERY + DEFEND_MANA_RECOVERY
    assert actor.defending
    assert any(e["type"] == "mana" and e["amount"] == DEFEND_MANA_RECOVERY for e in events)
    events = resolve_action(state, defend_action(actor.combatant_id))
    assert actor.current_mana == actor.spec.max_mana
    assert any(e["type"] == "mana" and e["amount"] == 2 for e in events)
    events = resolve_action(state, attack_action(actor.combatant_id, (enemy.combatant_id,)))
    assert actor.current_mana == actor.spec.max_mana
    assert not any(e["type"] == "mana" for e in events)


def test_unaffordable_skill_still_rejected_for_direct_core_action():
    state = arena_state()
    actor = fighter(state)
    actor.current_mana = 0
    enemy = fighter(state, 1, 0)
    with pytest.raises(ValueError, match="needs 6 MP"):
        resolve_action(state, skill_action(actor.combatant_id, "arena_crush",
                                           (enemy.combatant_id,)))
    assert actor.current_mana == 0


def test_switching_preserves_mana_for_reserve_fighters():
    bundle = content_for_match("left", None, "right", None)
    encounter = replace(bundle.encounters[ARENA_ID], active_limits=(1, 1))
    state = new_battle(encounter, content=bundle)
    active_id, reserve_id = state.teams[0].active_ids[0], state.teams[0].reserve_ids[0]
    state.combatants[active_id].current_mana = 1
    state.combatants[reserve_id].current_mana = 4
    resolve_action(state, switch_action(active_id, reserve_id))
    assert state.combatants[active_id].current_mana == 1
    assert state.combatants[reserve_id].current_mana == 4


def test_content_validation_catches_invalid_costs_and_impossible_skill():
    move = CONTENT.moves["arc_bolt"]
    for cost in (-1, 1.5, True):
        c = replace(CONTENT, moves={**CONTENT.moves, move.move_id:
                                    replace(move, mana_cost=cost)})
        assert any("mana_cost" in str(issue) for issue in c.validate_structure())
    mage = CONTENT.characters["moon_mage"]
    c = replace(CONTENT, characters={**CONTENT.characters, mage.char_id:
                                    replace(mage, max_mana=1)})
    assert any("costs" in str(issue) for issue in c.validate_structure())
    for bad in (-1, 2.5, True):
        c = replace(CONTENT, characters={**CONTENT.characters, mage.char_id:
                                        replace(mage, max_mana=bad)})
        assert any("mana" in str(issue) for issue in c.validate_structure())
    basic = CONTENT.moves[CONTENT.basic_attack_move_id]
    c = replace(CONTENT, moves={**CONTENT.moves, basic.move_id: replace(basic, mana_cost=1)})
    assert any("basic Attack" in str(issue) for issue in c.validate_structure())


def test_builtin_ai_never_selects_unaffordable_skills():
    state = arena_state()
    mage = fighter(state, 1, 1)
    mage.current_mana = 0
    action = choose_ai_action(state, mage.combatant_id, random.Random(4))
    assert action.kind in {"attack", "defend", "switch"}


def test_mana_changes_are_part_of_real_arena_replay():
    record = record_match("heavy_hitter", "first_target", seed=4)
    assert verify_replay(record)[0] == record["winner"]
    assert any(step["type"] == "action" and step["max_mana"] > 0
               for step in record["steps"])
    assert any("MP]" in step["description"] for step in record["steps"]
               if step["type"] == "action" and step["action"]["kind"] == "skill")


def test_scripted_skill_charges_once_even_for_multiple_effects():
    from rpg_battle.api import damage
    from rpg_battle.core.models import MoveSpec

    state = arena_state()
    actor = fighter(state)
    target = fighter(state, 1, 0)
    old_move = state.content.moves["arena_crush"]
    new_move = replace(old_move, script=lambda ctx: (damage(4), damage(6)), mana_cost=5)
    state.content = replace(state.content, moves={
        **state.content.moves, old_move.move_id: new_move,
    })
    before = actor.current_mana
    events = resolve_action(state, skill_action(actor.combatant_id, "arena_crush",
                                                 (target.combatant_id,)))
    assert actor.current_mana == before - 5
    assert sum(e["type"] == "damage" for e in events) == 2
    assert sum(e["type"] == "mana" for e in events) == 1


def test_skill_cost_applies_on_miss_not_per_hit():
    state = arena_state()
    actor = fighter(state)
    target = fighter(state, 1, 0)
    move = state.content.moves["arena_crush"]
    state.content = replace(state.content, moves={
        **state.content.moves, move.move_id: replace(move, accuracy=0.0),
    })
    hp = target.current_hp
    before_mana = actor.current_mana
    events = resolve_action(state, skill_action(actor.combatant_id, "arena_crush",
                                                 (target.combatant_id,)), random.Random(2))
    assert target.current_hp == hp
    assert any(e["type"] == "miss" for e in events)
    assert actor.current_mana == before_mana - move.mana_cost
