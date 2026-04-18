from __future__ import annotations

"""Battle-state construction and helper functions."""

from collections.abc import Iterable

from loguru import logger

from rpg_battle.content.characters import CHARACTERS
from rpg_battle.content.encounters import DEFAULT_ENCOUNTER
from rpg_battle.core.models import (
    BattleState,
    CombatantState,
    EncounterSpec,
    ReplacementRequest,
    TeamBattleState,
    TeamSpec,
    InventoryEntry,
)


def _build_team_state(
    team_index: int,
    team_spec: TeamSpec,
    active_limit: int,
    requested_active: tuple[str, ...] | None,
) -> tuple[TeamBattleState, dict[str, CombatantState]]:
    requested_active = (
        requested_active or team_spec.starting_active or team_spec.members[:active_limit]
    )
    logger.debug(
        "Building team {} with active_limit={} requested_active={}",
        team_spec.name,
        active_limit,
        requested_active,
    )
    requested_active = tuple(requested_active[:active_limit])
    requested_set = set(requested_active)

    team_state = TeamBattleState(
        team_index=team_index,
        name=team_spec.name,
        controller_type=team_spec.controller_type,
        active_limit=active_limit,
        inventory=[
            InventoryEntry(item_id=entry.item_id, quantity=entry.quantity)
            for entry in team_spec.inventory
        ],
    )
    combatants: dict[str, CombatantState] = {}

    ordered_members = list(requested_active) + [
        char_id for char_id in team_spec.members if char_id not in requested_set
    ]
    for member_index, char_id in enumerate(ordered_members):
        logger.debug(
            "Creating combatant template {} for team {} at roster index {}",
            char_id,
            team_spec.name,
            member_index,
        )
        combatant_id = f"t{team_index}_c{member_index}"
        combatant = CombatantState(
            combatant_id=combatant_id,
            spec=CHARACTERS[char_id],
            team_index=team_index,
            active=char_id in requested_set and len(team_state.active_ids) < active_limit,
        )
        if combatant.active:
            combatant.slot_index = len(team_state.active_ids)
            team_state.active_ids.append(combatant_id)
        else:
            team_state.reserve_ids.append(combatant_id)
        combatants[combatant_id] = combatant
    return team_state, combatants


def new_battle(encounter: EncounterSpec = DEFAULT_ENCOUNTER) -> BattleState:
    """Build a fresh battle state from a declarative encounter spec."""
    logger.info("Constructing new battle for encounter {}", encounter.encounter_id)
    teams: list[TeamBattleState] = []
    combatants: dict[str, CombatantState] = {}
    for team_index, (team_spec, active_limit) in enumerate(
        zip((encounter.player_team, encounter.enemy_team), encounter.active_limits, strict=True)
    ):
        requested_active = team_spec.starting_active
        team_state, team_combatants = _build_team_state(
            team_index=team_index,
            team_spec=team_spec,
            active_limit=active_limit,
            requested_active=requested_active,
        )
        teams.append(team_state)
        combatants.update(team_combatants)
    state = BattleState(teams=teams, combatants=combatants)
    logger.info(
        "New battle ready: teams={} combatants={}",
        [team.name for team in teams],
        len(combatants),
    )
    return state


def get_combatant(state: BattleState, combatant_id: str) -> CombatantState:
    return state.combatants[combatant_id]


def get_team(state: BattleState, team_index: int) -> TeamBattleState:
    return state.teams[team_index]


def active_combatants(state: BattleState, team_index: int) -> list[CombatantState]:
    return [get_combatant(state, cid) for cid in state.teams[team_index].active_ids]


def living_active_ids(state: BattleState, team_index: int) -> list[str]:
    return [cid for cid in state.teams[team_index].active_ids if get_combatant(state, cid).alive]


def living_reserve_ids(state: BattleState, team_index: int) -> list[str]:
    return [cid for cid in state.teams[team_index].reserve_ids if get_combatant(state, cid).alive]


def all_living_active_ids(state: BattleState) -> list[str]:
    return [
        cid
        for team_index in range(len(state.teams))
        for cid in living_active_ids(state, team_index)
    ]


def living_enemy_ids(state: BattleState, actor_id: str) -> list[str]:
    actor = get_combatant(state, actor_id)
    return [
        cid
        for team_index, team in enumerate(state.teams)
        if team_index != actor.team_index
        for cid in living_active_ids(state, team_index)
    ]


def living_ally_ids(
    state: BattleState,
    actor_id: str,
    *,
    include_self: bool = True,
) -> list[str]:
    actor = get_combatant(state, actor_id)
    allies = living_active_ids(state, actor.team_index)
    if include_self:
        return allies
    return [cid for cid in allies if cid != actor_id]


def vacant_active_slots(state: BattleState, team_index: int) -> int:
    team = state.teams[team_index]
    occupied_slots = {
        get_combatant(state, combatant_id).slot_index
        for combatant_id in team.active_ids
        if get_combatant(state, combatant_id).slot_index is not None
    }
    return max(0, team.active_limit - len(occupied_slots))


def first_vacant_slot(state: BattleState, team_index: int) -> int | None:
    """Return the first open battlefield slot for a team, if any."""

    team = state.teams[team_index]
    occupied_slots = {
        get_combatant(state, combatant_id).slot_index
        for combatant_id in team.active_ids
        if get_combatant(state, combatant_id).slot_index is not None
    }
    for slot_index in range(team.active_limit):
        if slot_index not in occupied_slots:
            return slot_index
    return None


def move_active_to_reserve(state: BattleState, combatant_id: str) -> None:
    combatant = get_combatant(state, combatant_id)
    team = state.teams[combatant.team_index]
    if combatant_id in team.active_ids:
        team.active_ids.remove(combatant_id)
    if combatant.alive and combatant_id not in team.reserve_ids:
        team.reserve_ids.append(combatant_id)
    combatant.active = False
    combatant.slot_index = None


def bring_reserve_to_active(state: BattleState, team_index: int, combatant_id: str) -> bool:
    team = state.teams[team_index]
    slot_index = first_vacant_slot(state, team_index)
    if combatant_id not in team.reserve_ids or slot_index is None:
        return False
    team.reserve_ids.remove(combatant_id)
    team.active_ids.append(combatant_id)
    combatant = get_combatant(state, combatant_id)
    combatant.active = True
    combatant.slot_index = slot_index
    logger.debug(
        "Promoted reserve {} to active slot {} on team {}",
        combatant_id,
        slot_index,
        team_index,
    )
    return True


def replace_active_with_reserve(
    state: BattleState,
    actor_id: str,
    switch_in_id: str,
) -> bool:
    actor = get_combatant(state, actor_id)
    team = state.teams[actor.team_index]
    if actor_id not in team.active_ids or switch_in_id not in team.reserve_ids:
        return False
    list_index = team.active_ids.index(actor_id)
    team.active_ids[list_index] = switch_in_id
    team.reserve_ids.remove(switch_in_id)
    if actor.alive:
        team.reserve_ids.append(actor_id)
    actor.active = False
    preserved_slot = actor.slot_index
    actor.slot_index = None
    incoming = get_combatant(state, switch_in_id)
    incoming.active = True
    incoming.slot_index = preserved_slot
    logger.debug("Swapped {} out for {} in slot {}", actor_id, switch_in_id, preserved_slot)
    return True


def mark_fainted(state: BattleState, combatant_id: str) -> None:
    combatant = get_combatant(state, combatant_id)
    logger.info("Marking {} as fainted", combatant.spec.name)
    combatant.fainted = True
    combatant.active = False
    team = state.teams[combatant.team_index]
    if combatant_id in team.active_ids:
        team.active_ids.remove(combatant_id)
    if combatant_id in team.reserve_ids:
        team.reserve_ids.remove(combatant_id)


def ensure_replacement_request(state: BattleState, team_index: int) -> None:
    missing = vacant_active_slots(state, team_index)
    if missing <= 0 or not living_reserve_ids(state, team_index):
        return
    for request in state.pending_replacements:
        if request.team_index == team_index:
            return
    state.pending_replacements.append(
        ReplacementRequest(team_index=team_index, slots_to_fill=missing)
    )
    logger.info("Queued replacement request for team {} with {} open slots", team_index, missing)


def clear_replacement_request(state: BattleState, team_index: int) -> None:
    state.pending_replacements = [
        request for request in state.pending_replacements if request.team_index != team_index
    ]


def reserve_names(state: BattleState, team_index: int) -> list[str]:
    return [get_combatant(state, cid).spec.name for cid in state.teams[team_index].reserve_ids]


def living_team_indices(state: BattleState) -> list[int]:
    return [index for index, team in enumerate(state.teams) if not team.defeated()]


def combatant_name_map(state: BattleState, combatant_ids: Iterable[str]) -> list[str]:
    return [get_combatant(state, combatant_id).spec.name for combatant_id in combatant_ids]
