from __future__ import annotations

"""Sample party compositions used by encounters and classroom experiments."""

from rpg_battle.core.models import TeamSpec

TEAMS: dict[str, TeamSpec] = {}

TEAMS["default_player"] = TeamSpec(
    name="Player Party",
    members=("knight", "druid", "runesage"),
    controller_type="human",
    starting_active=("knight", "druid"),
)

TEAMS["default_enemy"] = TeamSpec(
    name="Wild Company",
    members=("ai_slop", "spirit", "guardian"),
    controller_type="ai",
    starting_active=("ai_slop", "spirit"),
)

TEAMS["extra"] = TeamSpec(
    name="Arcane Circle",
    members=("mage", "runesage", "druid"),
    controller_type="human",
    starting_active=("mage", "runesage"),
)

DEFAULT_PLAYER_TEAM = TEAMS["default_player"]
DEFAULT_ENEMY_TEAM = TEAMS["default_enemy"]
EXTRA_TEAM = TEAMS["extra"]
