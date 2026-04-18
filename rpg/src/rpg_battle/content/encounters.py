from __future__ import annotations

"""Encounter presets.

Each encounter starts as a small dictionary so students can add title, teams,
limits, or music one key at a time.
"""

from rpg_battle.content.audio import DEFAULT_BATTLE_TRACK
from rpg_battle.content.teams import DEFAULT_ENEMY_TEAM, DEFAULT_PLAYER_TEAM
from rpg_battle.core.models import EncounterSpec

ENCOUNTERS: dict[str, EncounterSpec] = {}

default: dict[str, object] = {}
default["encounter_id"] = "classroom_skirmish"
default["title"] = "Classroom Skirmish"
default["player_team"] = DEFAULT_PLAYER_TEAM
default["enemy_team"] = DEFAULT_ENEMY_TEAM
default["active_limits"] = (2, 2)
default["music_track_id"] = DEFAULT_BATTLE_TRACK
ENCOUNTERS["default"] = EncounterSpec(**default)

DEFAULT_ENCOUNTER = ENCOUNTERS["default"]
