from __future__ import annotations

"""Target-resolution helpers for the general active+reserve battle model."""

from loguru import logger

from rpg_battle.core.battle_state import living_ally_ids, living_enemy_ids
from rpg_battle.core.models import BattleState, TargetMode


def get_valid_target_groups(
    state: BattleState,
    actor_id: str,
    target_mode: TargetMode,
) -> list[list[str]]:
    logger.debug("Resolving target groups for actor={} mode={}", actor_id, target_mode)
    if target_mode == "self":
        return [[actor_id]]
    if target_mode == "single_enemy":
        return [[target_id] for target_id in living_enemy_ids(state, actor_id)]
    if target_mode == "single_ally":
        return [[target_id] for target_id in living_ally_ids(state, actor_id, include_self=True)]
    if target_mode == "all_enemies":
        targets = living_enemy_ids(state, actor_id)
        return [targets] if targets else []
    if target_mode == "all_allies":
        targets = living_ally_ids(state, actor_id, include_self=True)
        return [targets] if targets else []
    if target_mode == "none":
        return [[]]
    return []


def get_valid_targets(state: BattleState, actor_id: str, target_mode: TargetMode) -> list[str]:
    groups = get_valid_target_groups(state, actor_id, target_mode)
    if target_mode in {"single_enemy", "single_ally"}:
        return [group[0] for group in groups if group]
    if groups:
        return groups[0]
    return []
