from rpg_battle.core.actions import item_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.models import EncounterSpec, InventoryEntry, TeamSpec


def test_item_action_shape():
    action = item_action("actor_0", "potion", target_ids=("target_1",))
    assert action.kind == "item"
    assert action.item_id == "potion"
    assert action.target_ids == ("target_1",)


def test_team_inventory_copies_into_battle_state():
    player = TeamSpec(
        name="Player",
        members=("knight",),
        controller_type="human",
        starting_active=("knight",),
        inventory=(InventoryEntry(item_id="potion", quantity=2),),
    )
    enemy = TeamSpec(
        name="Enemy",
        members=("spirit",),
        controller_type="ai",
        starting_active=("spirit",),
    )
    encounter = EncounterSpec(
        encounter_id="inventory_test",
        title="Inventory Test",
        player_team=player,
        enemy_team=enemy,
        active_limits=(1, 1),
        music_track_id=None,
    )

    state = new_battle(encounter)
    assert state.teams[0].inventory[0].item_id == "potion"
    assert state.teams[0].inventory[0].quantity == 2
    assert state.teams[1].inventory == []
