from __future__ import annotations

"""Encounter presets.

Each encounter chooses how many frontline combatants are active at once. The
same battle engine handles 1v1, 2v2, 3v3, and beyond by changing these limits.
Teams themselves now own their preferred starting frontline so students can edit
rosters in one place.
"""

from rpg_battle.content.audio import DEFAULT_BATTLE_TRACK
from rpg_battle.content.teams import DEFAULT_ENEMY_TEAM, DEFAULT_PLAYER_TEAM
from rpg_battle.core.models import EncounterSpec

DEFAULT_ENCOUNTER = EncounterSpec(
    encounter_id="classroom_skirmish",
    title="Classroom Skirmish",
    player_team=DEFAULT_PLAYER_TEAM,
    enemy_team=DEFAULT_ENEMY_TEAM,
    active_limits=(2, 2),
    music_track_id=DEFAULT_BATTLE_TRACK,
)
