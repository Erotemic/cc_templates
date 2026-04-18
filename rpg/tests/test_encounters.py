from rpg_battle.content.encounters import ENCOUNTERS
from rpg_battle.core.battle_state import new_battle


def test_boss_encounter_exists() -> None:
    encounter = ENCOUNTERS["boss_ai_slop"]
    assert encounter.active_limits == (3, 1)
    assert encounter.music_track_id == "boss_battle_frenzy"


def test_second_boss_encounter_exists() -> None:
    encounter = ENCOUNTERS["boss_null_hydra"]
    assert encounter.active_limits == (3, 1)
    assert encounter.music_track_id == "boss_battle_frenzy"


def test_boss_encounter_has_no_enemy_reserve_members() -> None:
    state = new_battle(ENCOUNTERS["boss_ai_slop"])
    assert state.teams[1].reserve_ids == []


def test_multiple_encounter_templates_exist() -> None:
    for key in [
        "default",
        "training_duel",
        "frontline_brawl",
        "blues_night",
        "boss_ai_slop",
        "boss_null_hydra",
    ]:
        assert key in ENCOUNTERS
