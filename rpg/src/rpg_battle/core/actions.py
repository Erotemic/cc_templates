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


def item_action(actor_id: str, item_id: str, target_ids: tuple[str, ...] = ()) -> BattleAction:
    """Build an item action.

    Inventory is not exposed in the classroom UI yet, but this helper shows the
    shape a future item-use command should take. Students can call this from the
    battle scene once they add an "Item" menu branch.
    """
    return BattleAction(actor_id=actor_id, kind="item", item_id=item_id, target_ids=target_ids)
