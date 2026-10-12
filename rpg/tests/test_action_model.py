"""One action model for student controllers, menus and AI.

Validate actual behavior and rules rather than relying on source or menu text.
"""

from dataclasses import replace
import random

import pytest

from rpg_battle.core.actions import attack_action, defend_action, skill_action
from rpg_battle.core.ai import choose_ai_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.models import BattleAction
from rpg_battle.core.rules import resolve_action, validate_action
from rpg_battle.core.scripting import StudentCodeError, build_turn_context
from student_game import CONTENT
from student_game.catalog import GAME
from student_game import moves


def make_turn():
    state = new_battle(CONTENT.default_encounter, content=CONTENT)
    actor = state.teams[0].active_ids[0]
    return state, actor, build_turn_context(state, actor)


def test_every_fighter_can_attack_without_learning_a_skill():
    assert not CONTENT.validate_structure()
    assert all(CONTENT.basic_attack_move_id not in char.move_ids
               for char in CONTENT.characters.values())
    state, actor, turn = make_turn()
    assert turn.attack().kind == "attack"
    assert turn.attack().move_id is None
    assert turn.defend() == defend_action(actor)
    events = resolve_action(state, turn.attack(target=turn.enemies[0]), random.Random(9))
    move = next(event for event in events if event["type"] == "move")
    assert move["move_id"] == CONTENT.basic_attack_move_id
    assert move["move_name"] == "Attack"
    assert "attacks" in move["text"]


def test_student_and_builtin_actions_are_the_same_objects_and_effects():
    state, actor, turn = make_turn()
    target_id = state.teams[1].active_ids[0]
    basic = attack_action(actor, (target_id,))
    student = turn.attack(target=turn.enemies[0])
    assert student == basic
    state.teams[0].strategy = lambda context: context.attack(target=context.enemies[0])
    from_ai = choose_ai_action(state, actor, random.Random(8))
    assert from_ai == basic
    state_2, _, _ = make_turn()
    a = resolve_action(state, from_ai, random.Random(8))
    b = resolve_action(state_2, basic, random.Random(8))
    assert a == b
    assert {cid: c.current_hp for cid, c in state.combatants.items()} == {
        cid: c.current_hp for cid, c in state_2.combatants.items()
    }


def test_skill_is_separate_and_use_is_backward_compatible():
    state, actor, turn = make_turn()
    assert turn.skill("shield_bash", target=turn.enemies[0]) == turn.use(
        "shield_bash", target=turn.enemies[0]
    )
    assert turn.skill("shield_bash").kind == "skill"
    with pytest.raises(ValueError, match="does not know the skill"):
        turn.skill("arc_bolt", target=turn.enemies[0])
    with pytest.raises(TypeError, match="target"):
        turn.attack(target="enemy")
    assert isinstance(turn.attack(), BattleAction)
    assert isinstance(turn.skill("shield_bash"), BattleAction)


@pytest.mark.parametrize("action_factory, error", [
    (lambda actor, enemy: skill_action(actor, "arc_bolt", (enemy,)), "does not know skill"),
    (lambda actor, enemy: attack_action(actor, (enemy,), move_id="shield_bash"), "Attack does not select a skill"),
    (lambda actor, enemy: attack_action(actor, (actor,)), "invalid target"),
    (lambda actor, enemy: attack_action(actor, (enemy, enemy)), "invalid target"),
    (lambda actor, enemy: defend_action(actor).__class__(actor, "defend", target_ids=(enemy,)), "Defend does not use"),
])
def test_illegal_actions_fail_before_mutation_or_randomness(action_factory, error):
    state, actor, _ = make_turn()
    enemy = state.teams[1].active_ids[0]
    before = [(cid, c.current_hp, c.defending) for cid, c in state.combatants.items()]
    rng = random.Random(23)
    rng_before = rng.getstate()
    with pytest.raises(ValueError, match=error):
        resolve_action(state, action_factory(actor, enemy), rng)
    assert [(cid, c.current_hp, c.defending) for cid, c in state.combatants.items()] == before
    assert rng.getstate() == rng_before


def test_reorders_complete_group_targets_once_and_rejects_missing_target():
    encounter = CONTENT.encounters["frontline_brawl"]
    state = new_battle(encounter, content=CONTENT)
    actor = next(cid for cid in state.teams[0].active_ids
                 if state.combatants[cid].spec.char_id == "runesage")
    turn = build_turn_context(state, actor)
    action = turn.skill("fractal_veil", target=(*turn.allies, turn.user))
    assert validate_action(state, action).target_ids == tuple(state.teams[0].active_ids)
    with pytest.raises(ValueError, match="invalid target"):
        validate_action(state, turn.skill("fractal_veil", target=(turn.user, turn.user)))


def test_directly_returning_wrong_actor_or_missing_skill_gets_student_error():
    state, actor, _ = make_turn()
    state.teams[0].strategy = lambda turn: BattleAction(actor_id="another", kind="attack")
    with pytest.raises(StudentCodeError, match="another fighter"):
        choose_ai_action(state, actor)
    state.teams[0].strategy = lambda turn: skill_action(actor, "arc_bolt")
    with pytest.raises(StudentCodeError, match="does not know skill"):
        choose_ai_action(state, actor)


def test_zero_learned_skills_is_valid_because_attack_is_universal():
    bare = replace(CONTENT.characters["knight"], move_ids=())
    content = replace(CONTENT, characters={**CONTENT.characters, "knight": bare})
    assert not content.validate_structure()
    state = new_battle(content=content)
    actor = state.teams[0].active_ids[0]
    turn = build_turn_context(state, actor)
    assert turn.available_move_ids == frozenset()
    assert resolve_action(state, turn.attack(), random.Random(1))


def test_basic_attack_is_configured_on_game_not_presentation():
    assert GAME.basic_attack is moves.strike
    assert not hasattr(CONTENT.presentation, "basic_attack_move_id")
    # Existing authored games that set presentation.basic_attack can still compile.
    legacy = replace(GAME, basic_attack=None,
                     presentation=replace(GAME.presentation, basic_attack=moves.strike))
    assert legacy.compile().basic_attack_move_id == moves.strike.move_id
    with pytest.raises(ValueError, match="set basic_attack"):
        replace(GAME, basic_attack=None).compile()
    knight = CONTENT.characters["knight"]
    broken = replace(CONTENT, characters={**CONTENT.characters,
                     "knight": replace(knight, move_ids=(*knight.move_ids,
                                                          CONTENT.basic_attack_move_id))})
    assert any("standard Attack must not also appear" in str(issue)
               for issue in broken.validate_structure())
