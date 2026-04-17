from __future__ import annotations

"""Simple AI for the general actor-and-target battle system."""

import random

from rpg_battle.content.moves import MOVES
from rpg_battle.core.actions import attack_action, defend_action, skill_action, switch_action
from rpg_battle.core.battle_state import get_combatant, living_ally_ids, living_enemy_ids
from rpg_battle.core.models import BattleAction, BattleState
from rpg_battle.core.rules import legal_replacement_targets, legal_switch_targets
from rpg_battle.core.targeting import get_valid_target_groups


def choose_ai_action(
    state: BattleState,
    actor_id: str,
    rng: random.Random | None = None,
) -> BattleAction:
    rng = rng or random.Random()
    actor = get_combatant(state, actor_id)
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
            move = MOVES[move_id]
            if move.kind == "heal":
                groups = get_valid_target_groups(state, actor_id, move.target_mode)
                target_ids = tuple(groups[0]) if groups else (actor_id,)
                if move.target_mode == "single_ally":
                    target_ids = (weakest_ally.combatant_id,)
                return skill_action(actor_id, move_id, target_ids=target_ids)
        switch_targets = legal_switch_targets(state, actor_id)
        if switch_targets and weakest_enemy.current_hp > weakest_enemy.spec.max_hp * 0.4:
            best_switch = max(
                switch_targets,
                key=lambda combatant_id: get_combatant(state, combatant_id).current_hp,
            )
            return switch_action(actor_id, best_switch)

    for move_id in actor.spec.move_ids:
        move = MOVES[move_id]
        if move.kind in {"physical", "magical"} and move.target_mode == "single_enemy":
            if weakest_enemy.current_hp <= move.power + 6:
                return skill_action(actor_id, move_id, target_ids=(weakest_enemy.combatant_id,))

    utility = [
        move_id
        for move_id in actor.spec.move_ids
        if MOVES[move_id].kind in {"buff", "debuff", "status"}
    ]
    if utility and rng.random() < 0.3:
        move_id = rng.choice(utility)
        move = MOVES[move_id]
        groups = get_valid_target_groups(state, actor_id, move.target_mode)
        if move.target_mode == "single_enemy":
            target_ids = (weakest_enemy.combatant_id,)
        elif move.target_mode == "single_ally":
            target_ids = (weakest_ally.combatant_id,)
        else:
            target_ids = tuple(groups[0]) if groups else ()
        return skill_action(actor_id, move_id, target_ids=target_ids)

    attacks = [
        move_id for move_id in actor.spec.move_ids if MOVES[move_id].kind in {"physical", "magical"}
    ]
    if attacks:
        move_id = rng.choice(attacks)
        move = MOVES[move_id]
        groups = get_valid_target_groups(state, actor_id, move.target_mode)
        if move.target_mode == "single_enemy":
            target_ids = (weakest_enemy.combatant_id,)
        else:
            target_ids = tuple(groups[0]) if groups else ()
        return skill_action(actor_id, move_id, target_ids=target_ids)
    if rng.random() < 0.25:
        return defend_action(actor_id)
    return attack_action(actor_id, target_ids=(weakest_enemy.combatant_id,))


def choose_ai_replacement(state: BattleState, team_index: int) -> str | None:
    targets = legal_replacement_targets(state, team_index)
    if not targets:
        return None
    return max(targets, key=lambda combatant_id: get_combatant(state, combatant_id).current_hp)
