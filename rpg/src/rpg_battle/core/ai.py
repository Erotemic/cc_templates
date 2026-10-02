from __future__ import annotations

"""AI for the general actor-and-target battle system.

Teams may use the built-in heuristic AI or provide a small student-authored
strategy function.  Strategy functions inspect a read-only ``TurnContext`` and
return ``turn.use(...)`` or ``turn.defend()``.
"""

import random

from loguru import logger

from rpg_battle.core.actions import attack_action, defend_action, skill_action, switch_action
from rpg_battle.core.battle_state import get_combatant, living_ally_ids, living_enemy_ids
from rpg_battle.core.models import BattleAction, BattleState
from rpg_battle.core.rules import legal_replacement_targets, legal_switch_targets
from rpg_battle.core.scripting import BattlerView, Defend, UseMove, build_turn_context
from rpg_battle.core.targeting import get_valid_target_groups
from rpg_battle.teaching.trace import emit_trace


def _view_target_ids(
    target: BattlerView | tuple[BattlerView, ...],
) -> tuple[str, ...]:
    if isinstance(target, BattlerView):
        return (target._combatant_id,)
    return tuple(view._combatant_id for view in target)


def _action_from_strategy(
    state: BattleState,
    actor_id: str,
    decision: UseMove | Defend,
) -> BattleAction:
    if isinstance(decision, Defend):
        return defend_action(actor_id)
    if not isinstance(decision, UseMove):
        raise TypeError(
            "AI strategy functions must return turn.use(...) or turn.defend(); "
            f"received {type(decision).__name__}"
        )
    if state.content is None:
        raise RuntimeError("BattleState is missing its GameContent bundle")
    actor = get_combatant(state, actor_id)
    if decision.move_id not in actor.spec.move_ids:
        raise ValueError(f"{actor.spec.name} does not know move {decision.move_id!r}")
    move = state.content.moves[decision.move_id]
    groups = [tuple(group) for group in get_valid_target_groups(state, actor_id, move.target_mode)]
    if decision.target == "auto":
        target_ids = groups[0] if groups else ()
    else:
        target_ids = _view_target_ids(decision.target)
        if target_ids not in groups:
            readable = [
                [get_combatant(state, target_id).spec.name for target_id in group]
                for group in groups
            ]
            raise ValueError(
                f"{actor.spec.name}'s strategy chose an invalid target for {move.name}; "
                f"legal targets are {readable}"
            )
    return skill_action(actor_id, decision.move_id, target_ids=target_ids)


def _choose_student_strategy_action(state: BattleState, actor_id: str) -> BattleAction | None:
    actor = get_combatant(state, actor_id)
    strategy = state.teams[actor.team_index].strategy
    if strategy is None:
        return None
    context = build_turn_context(state, actor_id)
    strategy_name = getattr(strategy, "__name__", "custom strategy")
    emit_trace(state, f"calling AI strategy {strategy_name} for {actor.spec.name}")
    if context.enemies:
        emit_trace(
            state,
            "visible enemies: "
            + ", ".join(
                f"{enemy.name} hp={enemy.hp}/{enemy.max_hp}" for enemy in context.enemies
            ),
        )
    decision = strategy(context)
    emit_trace(state, f"AI strategy returned {decision!r}")
    return _action_from_strategy(state, actor_id, decision)


def choose_ai_action(
    state: BattleState,
    actor_id: str,
    rng: random.Random | None = None,
) -> BattleAction:
    rng = rng or random.Random()
    if state.content is None:
        raise RuntimeError("BattleState is missing its GameContent bundle")

    scripted_action = _choose_student_strategy_action(state, actor_id)
    if scripted_action is not None:
        return scripted_action

    actor = get_combatant(state, actor_id)
    logger.debug("AI evaluating turn for {}", actor.spec.name)
    enemies = living_enemy_ids(state, actor_id)
    allies = living_ally_ids(state, actor_id, include_self=True)
    if not enemies:
        return defend_action(actor_id)

    enemy_targets = [get_combatant(state, target_id) for target_id in enemies]
    ally_targets = [get_combatant(state, target_id) for target_id in allies]
    weakest_enemy = min(enemy_targets, key=lambda target: target.current_hp)
    weakest_ally = min(ally_targets, key=lambda target: target.current_hp / target.spec.max_hp)

    if actor.current_hp <= actor.spec.max_hp * 0.35:
        for move_id in actor.spec.move_ids:
            move = state.content.moves[move_id]
            if move.kind == "heal":
                groups = get_valid_target_groups(state, actor_id, move.target_mode)
                target_ids = tuple(groups[0]) if groups else (actor_id,)
                if move.target_mode == "single_ally":
                    target_ids = (weakest_ally.combatant_id,)
                action = skill_action(actor_id, move_id, target_ids=target_ids)
                logger.info("AI chose heal action: {}", action)
                return action
        switch_targets = legal_switch_targets(state, actor_id)
        if switch_targets and weakest_enemy.current_hp > weakest_enemy.spec.max_hp * 0.4:
            best_switch = max(
                switch_targets,
                key=lambda combatant_id: get_combatant(state, combatant_id).current_hp,
            )
            return switch_action(actor_id, best_switch)

    for move_id in actor.spec.move_ids:
        move = state.content.moves[move_id]
        if move.kind in {"physical", "magical"} and move.target_mode == "single_enemy":
            if weakest_enemy.current_hp <= move.power + 6:
                return skill_action(actor_id, move_id, target_ids=(weakest_enemy.combatant_id,))

    utility = [
        move_id
        for move_id in actor.spec.move_ids
        if state.content.moves[move_id].kind in {"buff", "debuff", "status"}
    ]
    if utility and rng.random() < 0.3:
        move_id = rng.choice(utility)
        move = state.content.moves[move_id]
        groups = get_valid_target_groups(state, actor_id, move.target_mode)
        if move.target_mode == "single_enemy":
            target_ids = (weakest_enemy.combatant_id,)
        elif move.target_mode == "single_ally":
            target_ids = (weakest_ally.combatant_id,)
        else:
            target_ids = tuple(groups[0]) if groups else ()
        return skill_action(actor_id, move_id, target_ids=target_ids)

    attacks = [
        move_id
        for move_id in actor.spec.move_ids
        if state.content.moves[move_id].kind in {"physical", "magical"}
    ]
    if attacks:
        move_id = rng.choice(attacks)
        move = state.content.moves[move_id]
        groups = get_valid_target_groups(state, actor_id, move.target_mode)
        if move.target_mode == "single_enemy":
            target_ids = (weakest_enemy.combatant_id,)
        else:
            target_ids = tuple(groups[0]) if groups else ()
        return skill_action(actor_id, move_id, target_ids=target_ids)
    if rng.random() < 0.25:
        action = defend_action(actor_id)
        logger.info("AI chose fallback action: {}", action)
        return action
    action = attack_action(actor_id, target_ids=(weakest_enemy.combatant_id,))
    logger.info("AI chose fallback action: {}", action)
    return action


def choose_ai_replacement(state: BattleState, team_index: int) -> str | None:
    targets = legal_replacement_targets(state, team_index)
    if not targets:
        logger.debug("AI found no legal replacements for team {}", team_index)
        return None
    replacement = max(
        targets, key=lambda combatant_id: get_combatant(state, combatant_id).current_hp
    )
    logger.info("AI chose replacement {} for team {}", replacement, team_index)
    return replacement
