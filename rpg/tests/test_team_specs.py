from student_game import CONTENT

DEFAULT_ENCOUNTER = CONTENT.default_encounter
from rpg_battle.core.battle_state import new_battle


def test_team_spec_controls_starting_active_members() -> None:
    state = new_battle(DEFAULT_ENCOUNTER)
    player_names = [state.combatants[cid].spec.char_id for cid in state.teams[0].active_ids]
    enemy_names = [state.combatants[cid].spec.char_id for cid in state.teams[1].active_ids]
    assert player_names == ["knight", "runesage"]
    assert enemy_names == ["ai_slop", "spirit"]


from rpg_battle.core.battle_state import (
    bring_reserve_to_active,
    mark_fainted,
    living_reserve_ids,
    slot_of,
    new_battle,
)


def test_active_slots_stay_stable_after_ko_and_replacement() -> None:
    state = new_battle(DEFAULT_ENCOUNTER)
    player_team = state.teams[0]
    first_id, second_id = player_team.active_ids
    assert slot_of(state, first_id) == 0
    assert slot_of(state, second_id) == 1

    mark_fainted(state, first_id)
    assert slot_of(state, second_id) == 1

    reserve_id = living_reserve_ids(state, 0)[0]
    assert bring_reserve_to_active(state, 0, reserve_id) is True
    assert slot_of(state, reserve_id) == 0
    assert slot_of(state, second_id) == 1
