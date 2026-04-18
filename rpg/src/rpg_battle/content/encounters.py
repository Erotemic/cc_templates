from __future__ import annotations

"""Encounter presets.

Each encounter starts as a small dictionary so students can add title, teams,
limits, or music one key at a time.
"""

from rpg_battle.content.audio import DEFAULT_BATTLE_TRACK
from rpg_battle.content.teams import DEFAULT_ENEMY_TEAM, DEFAULT_PLAYER_TEAM, TEAMS
from rpg_battle.core.models import EncounterSpec

ENCOUNTERS: dict[str, EncounterSpec] = {}


def add_encounter(key: str, spec_dict: dict[str, object]) -> None:
    ENCOUNTERS[key] = EncounterSpec(**spec_dict)


default: dict[str, object] = {}
default["encounter_id"] = "classroom_skirmish"
default["title"] = "Classroom Skirmish"
default["player_team"] = DEFAULT_PLAYER_TEAM
default["enemy_team"] = DEFAULT_ENEMY_TEAM
default["active_limits"] = (2, 2)
default["music_track_id"] = DEFAULT_BATTLE_TRACK
add_encounter("default", default)

DEFAULT_ENCOUNTER = ENCOUNTERS["default"]

training_duel: dict[str, object] = {}
training_duel["encounter_id"] = "training_duel"
training_duel["title"] = "Training Duel"
training_duel["player_team"] = DEFAULT_PLAYER_TEAM
training_duel["enemy_team"] = TEAMS["duel_enemy"]
training_duel["active_limits"] = (1, 1)
training_duel["music_track_id"] = "training_battle"
add_encounter("training_duel", training_duel)

frontline_brawl: dict[str, object] = {}
frontline_brawl["encounter_id"] = "frontline_brawl"
frontline_brawl["title"] = "Frontline Brawl"
frontline_brawl["player_team"] = TEAMS["full_player"]
frontline_brawl["enemy_team"] = TEAMS["full_enemy"]
frontline_brawl["active_limits"] = (3, 3)
frontline_brawl["music_track_id"] = "soft_dungeon_crawl"
add_encounter("frontline_brawl", frontline_brawl)

blues_night: dict[str, object] = {}
blues_night["encounter_id"] = "blues_night"
blues_night["title"] = "Blues Night Ambush"
blues_night["player_team"] = TEAMS["extra"]
blues_night["enemy_team"] = TEAMS["blues_enemy"]
blues_night["active_limits"] = (2, 2)
blues_night["music_track_id"] = "bluesy_overhaul"
add_encounter("blues_night", blues_night)

boss_ai_slop: dict[str, object] = {}
boss_ai_slop["encounter_id"] = "boss_ai_slop"
boss_ai_slop["title"] = "Boss Battle: AI Slop Prime"
boss_ai_slop["player_team"] = TEAMS["full_player"]
boss_ai_slop["enemy_team"] = TEAMS["boss_ai_slop_enemy"]
boss_ai_slop["active_limits"] = (3, 1)
boss_ai_slop["music_track_id"] = "boss_battle_frenzy"
add_encounter("boss_ai_slop", boss_ai_slop)

boss_null_hydra: dict[str, object] = {}
boss_null_hydra["encounter_id"] = "boss_null_hydra"
boss_null_hydra["title"] = "Boss Battle: Null Hydra"
boss_null_hydra["player_team"] = TEAMS["full_player"]
boss_null_hydra["enemy_team"] = TEAMS["boss_null_hydra_enemy"]
boss_null_hydra["active_limits"] = (3, 1)
boss_null_hydra["music_track_id"] = "boss_battle_frenzy"
add_encounter("boss_null_hydra", boss_null_hydra)
