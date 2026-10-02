from __future__ import annotations

"""START HERE: a small place to program inside the full RPG.

Everything in this file is real game content.  The larger files beside it are a
library you can reuse while you learn.  Start by changing one number or one
branch, run ``python main.py --check``, then try the practice battle:

    python main.py --encounter workshop

Useful experiments:

* Change the 0.50 health threshold in ``power_strike_logic``.
* Change the two powers in ``chain_lightning_logic``.
* Add another ``if`` to ``practice_enemy_strategy``.
* Give ``workshop_hero`` a move from ``student_game/moves.py``.
"""

from rpg_battle.api import Battle, Character, Move, Team, damage

from student_game import art, audio, characters, effects, moves


def power_strike_logic(ctx):
    """A first conditional: the same move behaves differently at low HP."""

    if ctx.user.hp_ratio < 0.50:
        return damage(18)
    return damage(8)


power_strike = Move(
    "Workshop Power Strike",
    id="workshop_power_strike",
    kind="physical",
    power=8,
    animation=effects.impact,
    sound=audio.attack_basic,
    action=power_strike_logic,
)


def chain_lightning_logic(ctx):
    """A first loop: choose a different command for each target."""

    commands = []
    for target in ctx.targets:
        if "burn" in target.statuses:
            commands.append(damage(14, magical=True, target=target))
        else:
            commands.append(damage(8, magical=True, target=target))
    return commands


chain_lightning = Move(
    "Workshop Chain Lightning",
    id="workshop_chain_lightning",
    kind="magical",
    power=8,
    target="all_enemies",
    animation=effects.arc,
    sound=audio.arc_bolt,
    action=chain_lightning_logic,
)


workshop_hero = Character(
    "Workshop Hero",
    id="workshop_hero",
    role="student hero",
    hp=52,
    attack=9,
    defense=7,
    magic=9,
    speed=7,
    sprite=art.knight_dawn,
    moves=[power_strike, chain_lightning, moves.strike],
    description="A small character definition intended to be edited in class.",
)


def practice_enemy_strategy(turn):
    """A first algorithm: inspect battle facts and choose an action."""

    if turn.user.hp_ratio < 0.30:
        return turn.defend()

    target = min(turn.enemies, key=lambda enemy: enemy.hp_ratio)
    return turn.use(moves.arc_bolt, target=target)


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

workshop_battle = Battle(
    "Workshop Practice Battle",
    id="workshop",
    player=workshop_player,
    enemy=workshop_enemy,
    active=(1, 1),
    music=audio.training_battle,
)


MOVES = [power_strike, chain_lightning]
CHARACTERS = [workshop_hero]
TEAMS = [workshop_player, workshop_enemy]
BATTLES = [workshop_battle]
