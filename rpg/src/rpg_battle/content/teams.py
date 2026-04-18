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
default_player["starting_active"] = ("knight", "runesage")
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


boss_enemy: dict[str, object] = {}
boss_enemy["name"] = "Boss Court"
boss_enemy["members"] = ("ai_slop", "guardian", "spirit")
boss_enemy["controller_type"] = "ai"
boss_enemy["starting_active"] = ("ai_slop",)
TEAMS["boss_enemy"] = TeamSpec(**boss_enemy)

full_player: dict[str, object] = {}
full_player["name"] = "Hero Vanguard"
full_player["members"] = ("knight", "druid", "runesage")
full_player["controller_type"] = "human"
full_player["starting_active"] = ("knight", "druid", "runesage")
TEAMS["full_player"] = TeamSpec(**full_player)

full_enemy: dict[str, object] = {}
full_enemy["name"] = "Glitch Front"
full_enemy["members"] = ("ai_slop", "spirit", "guardian")
full_enemy["controller_type"] = "ai"
full_enemy["starting_active"] = ("ai_slop", "spirit", "guardian")
TEAMS["full_enemy"] = TeamSpec(**full_enemy)

duel_enemy: dict[str, object] = {}
duel_enemy["name"] = "Solo Spirit"
duel_enemy["members"] = ("spirit",)
duel_enemy["controller_type"] = "ai"
duel_enemy["starting_active"] = ("spirit",)
TEAMS["duel_enemy"] = TeamSpec(**duel_enemy)

blues_enemy: dict[str, object] = {}
blues_enemy["name"] = "Midnight Assembly"
blues_enemy["members"] = ("spirit", "guardian", "ai_slop")
blues_enemy["controller_type"] = "ai"
blues_enemy["starting_active"] = ("spirit", "guardian")
TEAMS["blues_enemy"] = TeamSpec(**blues_enemy)

boss_ai_slop_enemy: dict[str, object] = {}
boss_ai_slop_enemy["name"] = "AI Slop Prime"
boss_ai_slop_enemy["members"] = ("ai_slop_prime",)
boss_ai_slop_enemy["controller_type"] = "ai"
boss_ai_slop_enemy["starting_active"] = ("ai_slop_prime",)
TEAMS["boss_ai_slop_enemy"] = TeamSpec(**boss_ai_slop_enemy)

boss_null_hydra_enemy: dict[str, object] = {}
boss_null_hydra_enemy["name"] = "Null Hydra"
boss_null_hydra_enemy["members"] = ("null_hydra",)
boss_null_hydra_enemy["controller_type"] = "ai"
boss_null_hydra_enemy["starting_active"] = ("null_hydra",)
TEAMS["boss_null_hydra_enemy"] = TeamSpec(**boss_null_hydra_enemy)
