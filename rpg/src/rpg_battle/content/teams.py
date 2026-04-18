from __future__ import annotations

"""Sample party compositions used by encounters and classroom experiments.

Each team definition starts as an empty dictionary so students can grow it in a
step-by-step way before converting it into a :class:`TeamSpec`.
"""

from rpg_battle.core.models import TeamSpec

TEAMS: dict[str, TeamSpec] = {}

default_player: dict[str, object] = {}
default_player["name"] = "Player Party"
default_player["members"] = ("knight", "druid", "runesage")
default_player["controller_type"] = "human"
default_player["starting_active"] = ("knight", "druid")
TEAMS["default_player"] = TeamSpec(**default_player)

default_enemy: dict[str, object] = {}
default_enemy["name"] = "Wild Company"
default_enemy["members"] = ("ai_slop", "spirit", "guardian")
default_enemy["controller_type"] = "ai"
default_enemy["starting_active"] = ("ai_slop", "spirit")
TEAMS["default_enemy"] = TeamSpec(**default_enemy)

extra: dict[str, object] = {}
extra["name"] = "Arcane Circle"
extra["members"] = ("mage", "runesage", "druid")
extra["controller_type"] = "human"
extra["starting_active"] = ("mage", "runesage")
TEAMS["extra"] = TeamSpec(**extra)

DEFAULT_PLAYER_TEAM = TEAMS["default_player"]
DEFAULT_ENEMY_TEAM = TEAMS["default_enemy"]
EXTRA_TEAM = TEAMS["extra"]
