from __future__ import annotations

"""Battle wiring for the small classroom workshop.

This file keeps teams and deliberate lesson encounters out of the first file a
student edits. It is still ordinary authoring code and is a good next stop when
students want to create their own battle setup.
"""

from rpg_battle.api import Battle, Team

from student_game import characters
from student_game.workshop import practice_enemy_strategy, workshop_hero
from student_game.workshop_assets import workshop_theme

workshop_player = Team(
    "Workshop Player",
    id="workshop_player",
    members=[workshop_hero],
    active=[workshop_hero],
)

workshop_enemy = Team(
    "Workshop Opponent",
    id="workshop_enemy",
    members=[characters.spirit],
    active=[characters.spirit],
    controller="computer",
    strategy=practice_enemy_strategy,
)

workshop_enemy_pair = Team(
    "Workshop Pair",
    id="workshop_enemy_pair",
    members=[characters.spirit, characters.guardian],
    active=[characters.spirit, characters.guardian],
    controller="computer",
)

workshop_targeting_player = Team(
    "Workshop Targeting Player",
    id="workshop_targeting_player",
    members=[workshop_hero, characters.ranger],
    active=[workshop_hero, characters.ranger],
)

workshop_healing_player = Team(
    "Workshop Healing Player",
    id="workshop_healing_player",
    members=[characters.druid, workshop_hero],
    active=[characters.druid, workshop_hero],
)

workshop_balance_player = Team(
    "Workshop Balance Player",
    id="workshop_balance_player",
    members=[workshop_hero, characters.ranger],
    active=[workshop_hero, characters.ranger],
)

workshop_battle = Battle(
    "Workshop Practice Battle",
    id="workshop",
    player=workshop_player,
    enemy=workshop_enemy,
    active=(1, 1),
    music=workshop_theme,
)

workshop_chain_battle = Battle(
    "Workshop Chain Lightning",
    id="workshop_chain",
    player=workshop_player,
    enemy=workshop_enemy_pair,
    active=(1, 2),
    music=workshop_theme,
)

workshop_targeting_battle = Battle(
    "Workshop Target Selection",
    id="workshop_targeting",
    player=workshop_targeting_player,
    enemy=workshop_enemy,
    active=(2, 1),
    music=workshop_theme,
)

workshop_healing_battle = Battle(
    "Workshop Healing",
    id="workshop_healing",
    player=workshop_healing_player,
    enemy=workshop_enemy,
    active=(2, 1),
    music=workshop_theme,
)

workshop_balance_battle = Battle(
    "Workshop Balance Experiment",
    id="workshop_balance",
    player=workshop_balance_player,
    enemy=workshop_enemy_pair,
    active=(2, 2),
    music=workshop_theme,
)

TEAMS = [
    workshop_player,
    workshop_enemy,
    workshop_enemy_pair,
    workshop_targeting_player,
    workshop_healing_player,
    workshop_balance_player,
]
BATTLES = [
    workshop_battle,
    workshop_chain_battle,
    workshop_targeting_battle,
    workshop_healing_battle,
    workshop_balance_battle,
]
