from __future__ import annotations

"""Battle-state construction and helper functions."""

from collections.abc import Iterable
from typing import TYPE_CHECKING

from loguru import logger

from rpg_battle.core.models import (
    BattleState,
    CombatContent,
    CombatantState,
    EncounterSpec,
    ReplacementRequest,
    TeamBattleState,
    TeamSpec,
    InventoryEntry,
)

if TYPE_CHECKING:
    from rpg_battle.catalog import GameContent
    from rpg_battle.core.trace import TraceSink


def _build_team_state(
    team_index: int,
    team_spec: TeamSpec,
    active_limit: int,
    requested_active: tuple[str, ...] | None,
    content: CombatContent,
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
        strategy=team_spec.strategy,
        active_slots=[None] * active_limit,
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
            spec=content.characters[char_id],
            team_index=team_index,
        )
        team_state.roster_ids.append(combatant_id)
        if member_index < len(requested_active):
            team_state.active_slots[member_index] = combatant_id
        combatants[combatant_id] = combatant
    return team_state, combatants


def new_battle(
    encounter: EncounterSpec | None = None,
    *,
    content: GameContent | CombatContent | None = None,
    teaching_trace: "TraceSink | None" = None,
) -> BattleState:
    """Build a fresh battle state from an encounter and explicit content bundle."""
    if content is None:
        # Keep the convenience factory for early lessons, but importing core
        # modules alone must not load the rendering/audio-aware game catalog.
        from rpg_battle.catalog import get_default_content
        content = get_default_content()
    if encounter is None:
        if isinstance(content, CombatContent):
            raise ValueError("Provide an encounter when using CombatContent")
        encounter = content.default_encounter
    combat_content = (
        content if isinstance(content, CombatContent) else
        CombatContent(
            characters=content.characters,
            moves=content.moves,
            basic_attack_move_id=content.basic_attack_move_id,
        )
    )
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
            content=combat_content,
        )
        teams.append(team_state)
        combatants.update(team_combatants)
    state = BattleState(
        teams=teams,
        combatants=combatants,
        content=combat_content,
        teaching_trace=teaching_trace,
    )
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


def slot_of(state: BattleState, combatant_id: str) -> int | None:
    """Find a fighter's active slot, or None if the fighter is not fielded."""
    combatant = get_combatant(state, combatant_id)
    slots = state.teams[combatant.team_index].active_slots
    return next((index for index, cid in enumerate(slots) if cid == combatant_id), None)


def is_active(state: BattleState, combatant_id: str) -> bool:
    """A fighter is active precisely when present in a frontline slot."""
    return slot_of(state, combatant_id) is not None


def team_defeated(state: BattleState, team_index: int) -> bool:
    """A team loses only when every member of its full roster has zero HP."""
    team = state.teams[team_index]
    return not any(get_combatant(state, cid).alive for cid in team.roster_ids)


def vacant_active_slots(state: BattleState, team_index: int) -> int:
    return state.teams[team_index].active_slots.count(None)


def first_vacant_slot(state: BattleState, team_index: int) -> int | None:
    """Return the first vacant fixed battlefield slot, if any."""
    slots = state.teams[team_index].active_slots
    return next((index for index, cid in enumerate(slots) if cid is None), None)


def _move_to_end_of_roster(team: TeamBattleState, combatant_id: str) -> None:
    """Keep old switch semantics: a switched-out fighter joins the reserve tail."""
    team.roster_ids.remove(combatant_id)
    team.roster_ids.append(combatant_id)


def move_active_to_reserve(state: BattleState, combatant_id: str) -> None:
    combatant = get_combatant(state, combatant_id)
    team = state.teams[combatant.team_index]
    slot = slot_of(state, combatant_id)
    if slot is None:
        return
    team.active_slots[slot] = None
    if combatant.alive:
        _move_to_end_of_roster(team, combatant_id)


def bring_reserve_to_active(state: BattleState, team_index: int, combatant_id: str) -> bool:
    team = state.teams[team_index]
    slot_index = first_vacant_slot(state, team_index)
    if (
        combatant_id not in team.reserve_ids
        or slot_index is None
        or not get_combatant(state, combatant_id).alive
    ):
        return False
    team.active_slots[slot_index] = combatant_id
    logger.debug(
        "Promoted reserve {} to active slot {} on team {}",
        combatant_id, slot_index, team_index,
    )
    return True


def replace_active_with_reserve(
    state: BattleState,
    actor_id: str,
    switch_in_id: str,
) -> bool:
    actor = get_combatant(state, actor_id)
    team = state.teams[actor.team_index]
    slot_index = slot_of(state, actor_id)
    if (
        slot_index is None
        or switch_in_id not in team.reserve_ids
        or not get_combatant(state, switch_in_id).alive
    ):
        return False
    team.active_slots[slot_index] = switch_in_id
    _move_to_end_of_roster(team, actor_id)
    logger.debug("Swapped {} out for {} in slot {}", actor_id, switch_in_id, slot_index)
    return True


def mark_fainted(state: BattleState, combatant_id: str) -> None:
    """Knock out a fighter and vacate its slot without renumbering others."""
    combatant = get_combatant(state, combatant_id)
    logger.info("Marking {} as fainted", combatant.spec.name)
    combatant.current_hp = 0
    slot_index = slot_of(state, combatant_id)
    if slot_index is not None:
        state.teams[combatant.team_index].active_slots[slot_index] = None


def ensure_replacement_request(state: BattleState, team_index: int) -> None:
    missing = vacant_active_slots(state, team_index)
    if missing <= 0 or not living_reserve_ids(state, team_index):
        return
    for index, request in enumerate(state.pending_replacements):
        if request.team_index == team_index:
            # Multiple simultaneous knockouts can create additional vacant
            # slots before the first replacement decision is handled.
            if request.slots_to_fill != missing:
                state.pending_replacements[index] = ReplacementRequest(
                    team_index=team_index, slots_to_fill=missing,
                )
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
    return [get_combatant(state, cid).spec.name for cid in living_reserve_ids(state, team_index)]


def living_team_indices(state: BattleState) -> list[int]:
    return [index for index in range(len(state.teams)) if not team_defeated(state, index)]


def combatant_name_map(state: BattleState, combatant_ids: Iterable[str]) -> list[str]:
    return [get_combatant(state, combatant_id).spec.name for combatant_id in combatant_ids]


def validate_placement(state: BattleState) -> None:
    """Check the sole authoritative placement representation.

    This check is useful in tests and debugging, not a per-frame tax. Each
    fighter belongs to exactly one roster; active slots reference living members
    of that roster, and no fighter occupies two slots.
    """
    roster_members: set[str] = set()
    for team_index, team in enumerate(state.teams):
        if len(team.active_slots) != team.active_limit:
            raise ValueError(f"Team {team_index}: active slot count differs from active limit")
        if len(set(team.roster_ids)) != len(team.roster_ids):
            raise ValueError(f"Team {team_index}: duplicate roster member")
        for cid in team.roster_ids:
            if cid not in state.combatants:
                raise ValueError(f"Team {team_index}: unknown roster fighter {cid!r}")
            if cid in roster_members:
                raise ValueError(f"Fighter {cid!r} belongs to multiple rosters")
            roster_members.add(cid)
            if state.combatants[cid].team_index != team_index:
                raise ValueError(f"Fighter {cid!r} belongs to the wrong team")
        active = team.active_ids
        if len(set(active)) != len(active):
            raise ValueError(f"Team {team_index}: fighter occupies multiple slots")
        for cid in active:
            if cid not in team.roster_ids or not state.combatants[cid].alive:
                raise ValueError(f"Team {team_index}: invalid active fighter {cid!r}")
    if roster_members != set(state.combatants):
        raise ValueError("Battle combatants and team rosters disagree")
