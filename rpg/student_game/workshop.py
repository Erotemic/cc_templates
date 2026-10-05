from __future__ import annotations

"""START HERE: the small part of the RPG intended for early class editing.

Everything here runs in the full game, but this file deliberately focuses on
ordinary Python: values, functions, conditionals, loops, lists, and a simple
algorithm. Art/audio setup and battle wiring live in neighboring support files
so they do not distract from the first programming lessons.
"""

from rpg_battle.api import Character, Move, damage

from student_game import audio, characters, effects, moves
from student_game.workshop_assets import (
    workshop_hit,
    workshop_impact,
    workshop_frame,
)


# -------------------------------------------------------------------------
# Conditionals
# -------------------------------------------------------------------------

def power_strike_logic(ctx):
    """A first conditional: the same move behaves differently at low HP."""

    low_health = ctx.observe("low_health", ctx.user.hp_ratio < 0.50)
    if low_health:
        return damage(18)
    return damage(8)


power_strike = Move(
    "Workshop Power Strike",
    id="workshop_power_strike",
    kind="physical",
    ai_power=8,
    animation=workshop_impact,
    sound=workshop_hit,
    action=power_strike_logic,
)


# -------------------------------------------------------------------------
# Loops
# -------------------------------------------------------------------------

def chain_lightning_logic(ctx):
    """A first loop: choose a different command for each target."""

    commands = []
    for target in ctx.targets:
        burning = ctx.observe(
            f"{target.name} burning",
            "burn" in target.statuses,
        )
        if burning:
            commands.append(damage(14, magical=True, target=target))
        else:
            commands.append(damage(8, magical=True, target=target))
    return commands


chain_lightning = Move(
    "Workshop Chain Lightning",
    id="workshop_chain_lightning",
    kind="magical",
    ai_power=8,
    target="all_enemies",
    animation=effects.arc,
    sound=audio.arc_bolt,
    action=chain_lightning_logic,
)


# -------------------------------------------------------------------------
# A character built from reusable pieces
# -------------------------------------------------------------------------

workshop_hero = Character(
    "Workshop Hero",
    id="workshop_hero",
    role="student hero",
    hp=52,
    attack=9,
    defense=7,
    magic=9,
    speed=7,
    art=workshop_frame,
    moves=[power_strike, chain_lightning, moves.strike],
    description="A small character definition intended to be edited in class.",
)


# -------------------------------------------------------------------------
# Algorithms / AI
# -------------------------------------------------------------------------

def practice_enemy_strategy(turn):
    """Inspect battle facts and choose one action."""

    if turn.user.hp_ratio < 0.30:
        return turn.defend()

    # Find the enemy with the lowest fraction of HP remaining.
    target = turn.enemies[0]
    for enemy in turn.enemies[1:]:
        if enemy.hp_ratio < target.hp_ratio:
            target = enemy

    return turn.use(moves.arc_bolt, target=target)


MOVES = [power_strike, chain_lightning]
CHARACTERS = [workshop_hero]
