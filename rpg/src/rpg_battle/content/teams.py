from __future__ import annotations

"""Sample party compositions used by encounters and classroom experiments."""

from rpg_battle.core.models import TeamSpec

DEFAULT_PLAYER_TEAM = TeamSpec(
    name="Player Party",
    members=("knight", "druid", "runesage"),
    controller_type="human",
    starting_active=("knight", "druid"),
)
DEFAULT_ENEMY_TEAM = TeamSpec(
    name="Wild Company",
    members=("ai_slop", "spirit", "guardian"),
    controller_type="ai",
    starting_active=("ai_slop", "spirit"),
)
EXTRA_TEAM = TeamSpec(
    name="Arcane Circle",
    members=("mage", "runesage", "druid"),
    controller_type="human",
    starting_active=("mage", "runesage"),
)
