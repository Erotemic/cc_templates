from __future__ import annotations

"""Factories for common battle actions."""

from rpg_battle.core.models import BattleAction


def attack_action(actor_id: str, target_ids: tuple[str, ...] = ()) -> BattleAction:
    return BattleAction(actor_id=actor_id, kind="attack", move_id="strike", target_ids=target_ids)


def defend_action(actor_id: str) -> BattleAction:
    return BattleAction(actor_id=actor_id, kind="defend")


def skill_action(
    actor_id: str,
    move_id: str,
    target_ids: tuple[str, ...] = (),
) -> BattleAction:
    return BattleAction(actor_id=actor_id, kind="skill", move_id=move_id, target_ids=target_ids)


def switch_action(actor_id: str, switch_in_id: str) -> BattleAction:
    return BattleAction(actor_id=actor_id, kind="switch", switch_in_id=switch_in_id)
