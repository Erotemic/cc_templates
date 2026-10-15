"""Fighter placement is team-owned, not copied into per-fighter flags.

These tests cover changes to roster/slots, not incidental messages or file text.
"""

from copy import deepcopy

import pytest

from rpg_battle.battle.session import BattleSession
from rpg_battle.core.actions import defend_action
from rpg_battle.core.battle_state import (
    bring_reserve_to_active,
    ensure_replacement_request,
    first_vacant_slot,
    is_active,
    living_reserve_ids,
    mark_fainted,
    move_active_to_reserve,
    new_battle,
    replace_active_with_reserve,
    slot_of,
    team_defeated,
    vacant_active_slots,
    validate_placement,
)
from rpg_battle.core.models import EncounterSpec, TeamSpec
from student_game import CONTENT


ROSTER = ("guardian", "runesage", "knight", "moon_mage", "ranger")


def encounter_with_slots(active: int) -> EncounterSpec:
    return EncounterSpec(
        "placement", "Formation slots",
        TeamSpec("A", ROSTER), TeamSpec("B", ROSTER), (active, active),
    )


@pytest.mark.parametrize("active_count", [1, 2, 3, 4])
def test_slots_are_the_only_source_of_active_membership(active_count: int):
    state = new_battle(encounter_with_slots(active_count), content=CONTENT)
    validate_placement(state)
    for team_index, team in enumerate(state.teams):
        assert len(team.roster_ids) == len(ROSTER)
        assert len(team.active_slots) == active_count
        assert team.active_slots == team.active_ids
        assert len(living_reserve_ids(state, team_index)) == len(ROSTER) - active_count
        for position, combatant_id in enumerate(team.active_ids):
            assert slot_of(state, combatant_id) == position
            assert is_active(state, combatant_id)
        for combatant_id in living_reserve_ids(state, team_index):
            assert slot_of(state, combatant_id) is None
            assert not is_active(state, combatant_id)
        # Compatibility lists are derived snapshots, not independently mutable.
        copy_of_active = team.active_ids
        copy_of_active.clear()
        assert len(team.active_ids) == active_count


def test_faint_and_replacement_keep_survivor_slots_fixed():
    state = new_battle(encounter_with_slots(3), content=CONTENT)
    team = state.teams[0]
    first, middle, last = team.active_ids
    reserve = living_reserve_ids(state, 0)[0]
    mark_fainted(state, middle)
    assert team.active_slots == [first, None, last]
    assert first_vacant_slot(state, 0) == 1
    assert vacant_active_slots(state, 0) == 1
    assert not is_active(state, middle)
    assert not state.combatants[middle].alive
    assert middle not in living_reserve_ids(state, 0)
    assert bring_reserve_to_active(state, 0, reserve)
    assert team.active_slots == [first, reserve, last]
    assert not bring_reserve_to_active(state, 0, middle)
    validate_placement(state)


def test_switch_preserves_slot_and_previous_reserve_queue_order():
    state = new_battle(encounter_with_slots(2), content=CONTENT)
    team = state.teams[0]
    first, second = team.active_ids
    reserve_1, reserve_2, reserve_3 = living_reserve_ids(state, 0)
    assert replace_active_with_reserve(state, first, reserve_1)
    assert team.active_slots == [reserve_1, second]
    assert living_reserve_ids(state, 0) == [reserve_2, reserve_3, first]
    assert replace_active_with_reserve(state, second, reserve_2)
    assert team.active_slots == [reserve_1, reserve_2]
    assert living_reserve_ids(state, 0) == [reserve_3, first, second]
    validate_placement(state)


def test_illegal_placements_leave_state_intact():
    state = new_battle(encounter_with_slots(2), content=CONTENT)
    team = state.teams[0]
    member = team.active_ids[0]
    reserve = living_reserve_ids(state, 0)[0]
    foreign = state.teams[1].active_ids[0]
    before = deepcopy(state)
    assert not replace_active_with_reserve(state, member, foreign)
    assert not replace_active_with_reserve(state, member, member)
    assert not bring_reserve_to_active(state, 0, foreign)
    assert not bring_reserve_to_active(state, 0, member)
    assert state == before
    assert replace_active_with_reserve(state, member, reserve)
    validate_placement(state)


def test_team_defeat_depends_on_hp_not_membership_counters():
    state = new_battle(encounter_with_slots(1), content=CONTENT)
    team = state.teams[0]
    active = team.active_ids[0]
    mark_fainted(state, active)
    assert not team_defeated(state, 0)
    assert not state.combatants[active].alive
    assert team.reserve_ids  # Historical roster still includes knocked-out IDs.
    assert len(living_reserve_ids(state, 0)) == len(ROSTER) - 1
    for member in list(living_reserve_ids(state, 0)):
        mark_fainted(state, member)
    assert team_defeated(state, 0)
    assert living_reserve_ids(state, 0) == []
    assert team.active_slots == [None]
    validate_placement(state)


def test_session_keeps_valid_placement_after_every_step_and_action():
    session = BattleSession(encounter_with_slots(3), content=CONTENT, seed=11)
    for _ in range(40):
        validate_placement(session.state)
        if session.finished:
            break
        step = session.next_step()
        validate_placement(session.state)
        if step.request is None:
            continue
        if step.request.kind == "replacement":
            assert step.request.choices
            session.submit(step.request.choices[0])
        else:
            assert step.request.actor_id is not None
            session.submit(defend_action(step.request.actor_id))
        validate_placement(session.state)


def test_placement_validator_catches_duplicate_and_unowned_slots():
    state = new_battle(encounter_with_slots(2), content=CONTENT)
    team = state.teams[0]
    first = team.active_slots[0]
    team.active_slots[1] = first
    with pytest.raises(ValueError, match="multiple slots"):
        validate_placement(state)
    team.active_slots[1] = state.teams[1].active_slots[0]
    with pytest.raises(ValueError, match="invalid active fighter"):
        validate_placement(state)


def test_explicitly_vacated_slot_can_be_reoccupied():
    state = new_battle(encounter_with_slots(2), content=CONTENT)
    active = state.teams[0].active_slots[1]
    assert active is not None
    move_active_to_reserve(state, active)
    assert state.teams[0].active_slots[1] is None
    assert state.combatants[active].alive
    ensure_replacement_request(state, 0)
    assert state.pending_replacements[0].slots_to_fill == 1
    assert bring_reserve_to_active(state, 0, active)  # now at the back of reserve queue
    assert state.teams[0].active_slots[1] == active
    validate_placement(state)


def test_multiple_simultaneous_knockouts_request_each_replacement():
    session = BattleSession(encounter_with_slots(3), content=CONTENT, seed=4)
    left = session.state.teams[0]
    first, second, survivor = left.active_ids
    mark_fainted(session.state, first)
    ensure_replacement_request(session.state, 0)
    mark_fainted(session.state, second)
    ensure_replacement_request(session.state, 0)
    assert session.state.pending_replacements[0].slots_to_fill == 2
    assert left.active_slots == [None, None, survivor]

    first_request = session.request
    assert first_request is not None and first_request.kind == 'replacement'
    first_reserve = first_request.choices[0]
    session.submit(first_reserve)
    assert left.active_slots == [first_reserve, None, survivor]
    assert session.state.pending_replacements[0].slots_to_fill == 1

    second_request = session.request
    assert second_request is not None and second_request.kind == 'replacement'
    second_reserve = second_request.choices[0]
    assert second_reserve != first_reserve
    session.submit(second_reserve)
    assert left.active_slots == [first_reserve, second_reserve, survivor]
    assert session.request is None
    assert session.state.pending_replacements == []
    validate_placement(session.state)
