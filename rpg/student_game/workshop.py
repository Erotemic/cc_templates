from __future__ import annotations

"""START HERE: a small place to program inside the full RPG.

Everything in this file is real game content. The larger files beside it are a
library you can reuse while you learn. Start by changing one number or one
branch, run ``python main.py --check``, then try one named scenario from the
student guide.
"""

from rpg_battle.api import (
    Battle,
    Character,
    Music,
    Move,
    Palette,
    Sound,
    Sprite,
    Team,
    VisualEffect,
    damage,
)

from student_game import audio, characters, effects, moves

# -------------------------------------------------------------------------
# A complete original content example
# -------------------------------------------------------------------------
# The workshop registers every kind of content it defines. Students can copy
# this pattern when they create their own art, effects, sounds, or music.

workshop_palette = Palette(
    "Workshop Colors",
    id="workshop_colors",
    body=(90, 165, 245),
    accent=(255, 215, 95),
    detail=(28, 40, 70),
)

workshop_sprite = Sprite(
    "Workshop Hero Sprite",
    id="workshop_hero_sprite",
    palette=workshop_palette,
)
workshop_sprite.circle((0, 5), 38, fill="body")
workshop_sprite.polygon([(-28, -18), (0, -55), (28, -18)], fill="accent")
workshop_sprite.face(-3)

workshop_impact = VisualEffect.ring(
    "Workshop Impact",
    id="workshop_impact",
    color=(255, 220, 105),
    duration=0.42,
)

workshop_hit = Sound(
    "Workshop Hit",
    id="workshop_hit",
    waveform="triangle",
    frequency=240.0,
    frequency_end=150.0,
    duration=0.11,
    volume=0.24,
)

workshop_theme = Music.generated(
    "Workshop Theme",
    id="workshop_theme",
    builder="battle_loop_prototype",
    volume=0.30,
)


# -------------------------------------------------------------------------
# Conditionals
# -------------------------------------------------------------------------

def power_strike_logic(ctx):
    """A first conditional: the same move behaves differently at low HP."""

    low_health = ctx.observe("ctx.user.hp_ratio < 0.50", ctx.user.hp_ratio < 0.50)
    if low_health:
        return damage(18)
    return damage(8)


power_strike = Move(
    "Workshop Power Strike",
    id="workshop_power_strike",
    kind="physical",
    # Because this move has an action function, the function's damage(...)
    # commands control real damage. ``power`` remains only an AI estimate.
    power=8,
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
            f"{target.name}: 'burn' in target.statuses",
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
    sprite=workshop_sprite,
    moves=[power_strike, chain_lightning, moves.strike],
    description="A small character definition intended to be edited in class.",
)


# -------------------------------------------------------------------------
# Algorithms / AI
# -------------------------------------------------------------------------

def practice_enemy_strategy(turn):
    """A first algorithm: inspect battle facts and choose an action."""

    if turn.user.hp_ratio < 0.30:
        return turn.defend()

    target = min(turn.enemies, key=lambda enemy: enemy.hp_ratio)
    return turn.use(moves.arc_bolt, target=target)


# -------------------------------------------------------------------------
# Small battles used by the workshop and named teaching scenarios
# -------------------------------------------------------------------------

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


PALETTES = [workshop_palette]
SPRITES = [workshop_sprite]
EFFECTS = [workshop_impact]
SOUNDS = [workshop_hit]
MUSIC = [workshop_theme]
MOVES = [power_strike, chain_lightning]
CHARACTERS = [workshop_hero]
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
