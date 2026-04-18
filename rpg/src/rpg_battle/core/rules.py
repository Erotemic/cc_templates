from __future__ import annotations

"""Battle rules for the general active+reserve combat model."""

import random

from loguru import logger

from rpg_battle.content.moves import MOVES
from rpg_battle.core.battle_state import (
    all_living_active_ids,
    bring_reserve_to_active,
    clear_replacement_request,
    ensure_replacement_request,
    get_combatant,
    living_reserve_ids,
    mark_fainted,
    replace_active_with_reserve,
)
from rpg_battle.core.effects import effective_stat
from rpg_battle.core.events import make_event
from rpg_battle.core.models import BattleAction, BattleState, CombatantState, StatusState
from rpg_battle.core.transforms import get_transform_spec, is_transform_status, transform_status_names
from rpg_battle.core.targeting import get_valid_target_groups

ACTION_PRIORITY = {"switch": 2, "defend": 1, "attack": 0, "skill": 0}


def legal_switch_targets(state: BattleState, actor_id: str) -> list[str]:
    actor = get_combatant(state, actor_id)
    return living_reserve_ids(state, actor.team_index)


def legal_replacement_targets(state: BattleState, team_index: int) -> list[str]:
    return living_reserve_ids(state, team_index)


def _accuracy_check(rng: random.Random, accuracy: float) -> bool:
    return rng.random() <= accuracy


def _damage_amount(
    move_power: int,
    attacker: CombatantState,
    defender: CombatantState,
    magical: bool,
    rng: random.Random,
) -> int:
    attack_stat = effective_stat(attacker, "magic" if magical else "attack")
    defense_stat = effective_stat(defender, "defense")
    base = move_power + attack_stat * 1.4 - defense_stat * 0.8
    variance = rng.uniform(0.9, 1.1)
    damage = max(1, int(base * variance))
    if defender.defending:
        damage = max(1, int(damage * 0.6))
    return damage


def _apply_damage(target: CombatantState, amount: int) -> int:
    target.current_hp = max(0, target.current_hp - amount)
    return amount


def _apply_heal(target: CombatantState, amount: int) -> int:
    before = target.current_hp
    target.current_hp = min(target.spec.max_hp, target.current_hp + amount)
    return target.current_hp - before


def _target_display_name(state: BattleState, target_ids: list[str]) -> str:
    names = [get_combatant(state, target_id).spec.name for target_id in target_ids]
    if not names:
        return "nobody"
    if len(names) == 1:
        return names[0]
    return ", ".join(names)


def _apply_transform_effect(
    target: CombatantState,
    effect_token: str,
    events: list[dict],
) -> None:
    spec = get_transform_spec(effect_token)
    if spec is None:
        return
    current_phase = target.render_transforms.get(spec.transform_id, 0)
    new_phase = (current_phase + 1) % spec.cycle_length
    if new_phase == 0:
        target.render_transforms.pop(spec.transform_id, None)
    else:
        target.render_transforms[spec.transform_id] = new_phase
    for status_name in transform_status_names(spec):
        target.statuses.pop(status_name, None)
    for status_name in spec.state_statuses[new_phase]:
        target.statuses[status_name] = StatusState(status_name, -1)
    events.append(
        make_event(
            "status",
            team=target.team_index,
            target_id=target.combatant_id,
            target_name=target.spec.name,
            status=spec.transform_id,
            transform_id=spec.transform_id,
            transform_phase=new_phase,
            text=f"{target.spec.name} {spec.state_text[new_phase]}",
        )
    )


def _apply_effects(
    target: CombatantState,
    move_id: str,
    events: list[dict],
    rng: random.Random,
) -> None:
    move = MOVES[move_id]
    for effect in move.effects:
        if effect.status and rng.random() <= effect.chance:
            transform_spec = get_transform_spec(effect.status)
            if transform_spec is not None:
                _apply_transform_effect(target, effect.status, events)
            else:
                target.statuses[effect.status] = StatusState(effect.status, effect.duration)
                events.append(
                    make_event(
                        "status",
                        team=target.team_index,
                        target_id=target.combatant_id,
                        target_name=target.spec.name,
                        status=effect.status,
                        text=f"{target.spec.name} is affected by {effect.status.title()}!",
                    )
                )
        if effect.stat and rng.random() <= effect.chance:
            target.temp_bonuses[effect.stat] = (
                target.temp_bonuses.get(effect.stat, 0) + effect.stages
            )
            sign = "+" if effect.stages >= 0 else ""
            events.append(
                make_event(
                    "stat",
                    team=target.team_index,
                    target_id=target.combatant_id,
                    target_name=target.spec.name,
                    stat=effect.stat,
                    stages=effect.stages,
                    text=f"{target.spec.name}'s {effect.stat.title()} {sign}{effect.stages}.",
                )
            )


def _maybe_skip_for_stun(
    actor: CombatantState,
    events: list[dict],
    rng: random.Random,
) -> bool:
    if "stun" in actor.statuses and rng.random() < 0.5:
        events.append(
            make_event(
                "skip",
                team=actor.team_index,
                actor_id=actor.combatant_id,
                actor_name=actor.spec.name,
                text=f"{actor.spec.name} is stunned and loses the turn.",
            )
        )
        return True
    return False


def _update_winner(state: BattleState, events: list[dict]) -> None:
    living_team_indices = [
        team_index
        for team_index, team in enumerate(state.teams)
        if team.active_ids or team.reserve_ids
    ]
    if len(living_team_indices) == 1:
        state.winner = living_team_indices[0]
        events.append(
            make_event(
                "battle_end",
                winner=state.winner,
                text=f"{state.teams[state.winner].name} wins the battle!",
            )
        )


def _collect_faints(state: BattleState, events: list[dict]) -> None:
    active_ids = [combatant_id for team in state.teams for combatant_id in list(team.active_ids)]
    for combatant_id in active_ids:
        combatant = get_combatant(state, combatant_id)
        if combatant.current_hp > 0 or combatant.fainted:
            continue
        mark_fainted(state, combatant_id)
        events.append(
            make_event(
                "ko",
                team=combatant.team_index,
                target_id=combatant_id,
                target_name=combatant.spec.name,
                text=f"{combatant.spec.name} falls in battle.",
            )
        )
        ensure_replacement_request(state, combatant.team_index)
        if legal_replacement_targets(state, combatant.team_index):
            events.append(
                make_event(
                    "replacement_needed",
                    team=combatant.team_index,
                    text=f"{state.teams[combatant.team_index].name} must send in a replacement.",
                )
            )
    _update_winner(state, events)


def _default_target_ids(state: BattleState, actor_id: str, move_id: str) -> tuple[str, ...]:
    move = MOVES[move_id]
    groups = get_valid_target_groups(state, actor_id, move.target_mode)
    return tuple(groups[0]) if groups else ()


def build_round_turn_queue(state: BattleState, rng: random.Random | None = None) -> list[str]:
    rng = rng or random.Random()
    living_ids = all_living_active_ids(state)
    order = sorted(
        living_ids,
        key=lambda combatant_id: (
            -effective_stat(get_combatant(state, combatant_id), "speed"),
            rng.random(),
        ),
    )
    logger.info("Built round {} queue: {}", state.round_number, order)
    return order


def make_round_start_event(state: BattleState) -> dict:
    return make_event(
        "round_start",
        round_number=state.round_number,
        text=f"Round {state.round_number}",
    )


def make_turn_start_event(state: BattleState, actor_id: str) -> dict:
    actor = get_combatant(state, actor_id)
    return make_event(
        "turn_start",
        team=actor.team_index,
        actor_id=actor_id,
        actor_name=actor.spec.name,
        text=f"It is {actor.spec.name}'s turn.",
    )


def resolve_replacement(state: BattleState, team_index: int, combatant_id: str) -> list[dict]:
    logger.info("Resolving replacement: team={} combatant={}", team_index, combatant_id)
    if not bring_reserve_to_active(state, team_index, combatant_id):
        return []
    clear_replacement_request(state, team_index)
    combatant = get_combatant(state, combatant_id)
    return [
        make_event(
            "replacement_joined",
            team=team_index,
            combatant_id=combatant_id,
            text=f"{combatant.spec.name} joins the frontline!",
        )
    ]


def _process_switch(state: BattleState, action: BattleAction, events: list[dict]) -> None:
    if action.switch_in_id is None:
        return
    actor = get_combatant(state, action.actor_id)
    logger.info("Resolving action kind={} actor={}", action.kind, actor.spec.name)
    if not replace_active_with_reserve(state, action.actor_id, action.switch_in_id):
        logger.debug(
            "Switch failed for actor={} switch_in={}", action.actor_id, action.switch_in_id
        )
        return
    incoming = get_combatant(state, action.switch_in_id)
    events.append(
        make_event(
            "switch",
            team=actor.team_index,
            actor_id=actor.combatant_id,
            actor_name=actor.spec.name,
            new_combatant_id=incoming.combatant_id,
            text=f"{actor.spec.name} switches out for {incoming.spec.name}!",
        )
    )


def _process_defend(actor: CombatantState, events: list[dict]) -> None:
    actor.defending = True
    actor.statuses["guarded"] = StatusState("guarded", 1)
    events.append(
        make_event(
            "defend",
            team=actor.team_index,
            actor_id=actor.combatant_id,
            actor_name=actor.spec.name,
            text=f"{actor.spec.name} braces for impact.",
        )
    )


def _process_move(
    state: BattleState,
    action: BattleAction,
    events: list[dict],
    rng: random.Random,
) -> None:
    actor = get_combatant(state, action.actor_id)
    logger.info("Resolving action kind={} actor={}", action.kind, actor.spec.name)
    move_id = action.move_id or "strike"
    move = MOVES[move_id]
    target_ids = tuple(action.target_ids) or _default_target_ids(state, actor.combatant_id, move_id)
    logger.info(
        "Processing move: actor={} move={} targets={}",
        actor.spec.name,
        move.name,
        target_ids,
    )
    events.append(
        make_event(
            "move",
            team=actor.team_index,
            actor_id=actor.combatant_id,
            actor_name=actor.spec.name,
            move_id=move.move_id,
            move_name=move.name,
            animation=move.animation,
            sound_id=move.sound_id or move.move_id,
            target_ids=list(target_ids),
            text=f"{actor.spec.name} uses {move.name} on {_target_display_name(state, list(target_ids))}!",
        )
    )

    if move.target_mode == "none":
        return

    for target_id in target_ids:
        target = get_combatant(state, target_id)
        if not target.alive:
            continue
        if move.kind in {"physical", "magical"} and not _accuracy_check(rng, move.accuracy):
            events.append(
                make_event(
                    "miss",
                    team=actor.team_index,
                    actor_id=actor.combatant_id,
                    target_id=target_id,
                    text=f"{actor.spec.name}'s move misses {target.spec.name}.",
                )
            )
            continue
        if move.kind == "heal":
            amount = _apply_heal(target, max(8, move.power + effective_stat(actor, "magic")))
            logger.debug("Heal applied: target={} amount={}", target.spec.name, amount)
            events.append(
                make_event(
                    "heal",
                    team=target.team_index,
                    actor_id=actor.combatant_id,
                    target_id=target_id,
                    target_name=target.spec.name,
                    amount=amount,
                    text=f"{target.spec.name} recovers {amount} HP.",
                )
            )
            _apply_effects(target, move_id, events, rng)
            continue
        if move.kind in {"physical", "magical"}:
            magical = move.kind == "magical"
            damage = _damage_amount(move.power, actor, target, magical, rng)
            _apply_damage(target, damage)
            logger.debug("Damage applied: target={} amount={}", target.spec.name, damage)
            events.append(
                make_event(
                    "damage",
                    team=target.team_index,
                    actor_id=actor.combatant_id,
                    target_id=target_id,
                    target_name=target.spec.name,
                    amount=damage,
                    text=f"{target.spec.name} takes {damage} damage.",
                )
            )
            _apply_effects(target, move_id, events, rng)
            continue
        _apply_effects(target, move_id, events, rng)


def _status_tick(battler: CombatantState, events: list[dict]) -> None:
    expired: list[str] = []
    for name, status in list(battler.statuses.items()):
        if name == "poison" and battler.alive:
            damage = max(2, battler.spec.max_hp // 12)
            _apply_damage(battler, damage)
            events.append(
                make_event(
                    "status_tick",
                    team=battler.team_index,
                    target_id=battler.combatant_id,
                    target_name=battler.spec.name,
                    amount=damage,
                    status=name,
                    text=f"{battler.spec.name} suffers poison damage.",
                )
            )
        elif name == "burn" and battler.alive:
            damage = max(1, battler.spec.max_hp // 16)
            _apply_damage(battler, damage)
            events.append(
                make_event(
                    "status_tick",
                    team=battler.team_index,
                    target_id=battler.combatant_id,
                    target_name=battler.spec.name,
                    amount=damage,
                    status=name,
                    text=f"{battler.spec.name} is singed by burn.",
                )
            )
        if is_transform_status(name):
            continue
        status.duration -= 1
        if status.duration <= 0:
            expired.append(name)
    for name in expired:
        del battler.statuses[name]
        events.append(
            make_event(
                "status_end",
                team=battler.team_index,
                target_id=battler.combatant_id,
                target_name=battler.spec.name,
                status=name,
                text=f"{name.title()} fades from {battler.spec.name}.",
            )
        )


def reset_defending_flags(state: BattleState) -> None:
    for combatant_id in all_living_active_ids(state):
        get_combatant(state, combatant_id).defending = False


def resolve_action(
    state: BattleState,
    action: BattleAction,
    rng: random.Random | None = None,
) -> list[dict]:
    rng = rng or random.Random()
    events: list[dict] = []
    if state.winner is not None:
        return events
    actor = get_combatant(state, action.actor_id)
    logger.info("Resolving action kind={} actor={}", action.kind, actor.spec.name)
    if not actor.alive or not actor.active:
        return events
    if _maybe_skip_for_stun(actor, events, rng):
        return events
    if action.kind == "switch":
        _process_switch(state, action, events)
    elif action.kind == "defend":
        _process_defend(actor, events)
    elif action.kind == "item":
        # Inventory has not been surfaced in the classroom UI yet. When
        # students add item support, route their new action kind through a
        # `_process_item(...)` helper here so items share the same event flow as
        # moves: declaration -> animation -> consequences.
        raise NotImplementedError("Item actions are scaffolded but not implemented yet.")
    else:
        _process_move(state, action, events, rng)
    _collect_faints(state, events)
    _update_winner(state, events)
    return events


def finish_round(state: BattleState) -> list[dict]:
    logger.info("Finishing round {}", state.round_number)
    events: list[dict] = []
    for combatant_id in list(all_living_active_ids(state)):
        battler = get_combatant(state, combatant_id)
        if battler.alive:
            _status_tick(battler, events)
    _collect_faints(state, events)
    _update_winner(state, events)
    if state.winner is None:
        state.round_number += 1
    return events
