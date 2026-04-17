from rpg_battle.content.encounters import DEFAULT_ENCOUNTER
from rpg_battle.core.battle_state import new_battle


def test_team_spec_controls_starting_active_members() -> None:
    state = new_battle(DEFAULT_ENCOUNTER)
    player_names = [state.combatants[cid].spec.char_id for cid in state.teams[0].active_ids]
    enemy_names = [state.combatants[cid].spec.char_id for cid in state.teams[1].active_ids]
    assert player_names == ["knight", "druid"]
    assert enemy_names == ["ai_slop", "spirit"]


from rpg_battle.core.battle_state import (
    bring_reserve_to_active,
    get_combatant,
    mark_fainted,
    new_battle,
)
from rpg_battle.content.encounters import DEFAULT_ENCOUNTER


def test_active_slots_stay_stable_after_ko_and_replacement() -> None:
    state = new_battle(DEFAULT_ENCOUNTER)
    player_team = state.teams[0]
    first_id, second_id = player_team.active_ids
    assert get_combatant(state, first_id).slot_index == 0
    assert get_combatant(state, second_id).slot_index == 1

    mark_fainted(state, first_id)
    assert get_combatant(state, second_id).slot_index == 1

    reserve_id = player_team.reserve_ids[0]
    assert bring_reserve_to_active(state, 0, reserve_id) is True
    assert get_combatant(state, reserve_id).slot_index == 0
    assert get_combatant(state, second_id).slot_index == 1
