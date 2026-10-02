from __future__ import annotations

"""Teams and launchable battles. This is where characters become a game."""

from rpg_battle.api import Battle, Team

from student_game import audio, characters

default_player = Team(
    'Player Party',
    id='default_player',
    members=[
        characters.knight,
        characters.druid,
        characters.runesage,
    ],
    controller='human',
    active=[
        characters.knight,
        characters.runesage,
    ],
)

default_enemy = Team(
    'Wild Company',
    id='default_enemy',
    members=[
        characters.ai_slop,
        characters.spirit,
        characters.guardian,
    ],
    controller='computer',
    active=[
        characters.ai_slop,
        characters.spirit,
    ],
)

extra = Team(
    'Arcane Circle',
    id='extra',
    members=[
        characters.mage,
        characters.runesage,
        characters.druid,
    ],
    controller='human',
    active=[
        characters.mage,
        characters.runesage,
    ],
)

boss_enemy = Team(
    'Boss Court',
    id='boss_enemy',
    members=[
        characters.ai_slop,
        characters.guardian,
        characters.spirit,
    ],
    controller='computer',
    active=[
        characters.ai_slop,
    ],
)

full_player = Team(
    'Hero Vanguard',
    id='full_player',
    members=[
        characters.knight,
        characters.druid,
        characters.runesage,
    ],
    controller='human',
    active=[
        characters.knight,
        characters.druid,
        characters.runesage,
    ],
)

full_enemy = Team(
    'Glitch Front',
    id='full_enemy',
    members=[
        characters.ai_slop,
        characters.spirit,
        characters.guardian,
    ],
    controller='computer',
    active=[
        characters.ai_slop,
        characters.spirit,
        characters.guardian,
    ],
)

duel_enemy = Team(
    'Solo Spirit',
    id='duel_enemy',
    members=[
        characters.spirit,
    ],
    controller='computer',
    active=[
        characters.spirit,
    ],
)

blues_enemy = Team(
    'Midnight Assembly',
    id='blues_enemy',
    members=[
        characters.spirit,
        characters.guardian,
        characters.ai_slop,
    ],
    controller='computer',
    active=[
        characters.spirit,
        characters.guardian,
    ],
)

boss_ai_slop_enemy = Team(
    'AI Slop Prime',
    id='boss_ai_slop_enemy',
    members=[
        characters.ai_slop_prime,
    ],
    controller='computer',
    active=[
        characters.ai_slop_prime,
    ],
)

boss_null_hydra_enemy = Team(
    'Null Hydra',
    id='boss_null_hydra_enemy',
    members=[
        characters.null_hydra,
    ],
    controller='computer',
    active=[
        characters.null_hydra,
    ],
)

TEAMS = [
    default_player,
    default_enemy,
    extra,
    boss_enemy,
    full_player,
    full_enemy,
    duel_enemy,
    blues_enemy,
    boss_ai_slop_enemy,
    boss_null_hydra_enemy,
]

default = Battle(
    'Classroom Skirmish',
    id='default',
    encounter_id='classroom_skirmish',
    player=default_player,
    enemy=default_enemy,
    active=(2, 2),
    music=audio.bluesy_overhaul,
)

training_duel = Battle(
    'Training Duel',
    id='training_duel',
    player=default_player,
    enemy=duel_enemy,
    active=(1, 1),
    music=audio.training_battle,
)

frontline_brawl = Battle(
    'Frontline Brawl',
    id='frontline_brawl',
    player=full_player,
    enemy=full_enemy,
    active=(3, 3),
    music=audio.soft_dungeon_crawl,
)

blues_night = Battle(
    'Blues Night Ambush',
    id='blues_night',
    player=extra,
    enemy=blues_enemy,
    active=(2, 2),
    music=audio.bluesy_overhaul,
)

boss_ai_slop = Battle(
    'Boss Battle: AI Slop Prime',
    id='boss_ai_slop',
    player=full_player,
    enemy=boss_ai_slop_enemy,
    active=(3, 1),
    music=audio.boss_battle_frenzy,
)

boss_null_hydra = Battle(
    'Boss Battle: Null Hydra',
    id='boss_null_hydra',
    player=full_player,
    enemy=boss_null_hydra_enemy,
    active=(3, 1),
    music=audio.boss_battle_frenzy,
)

BATTLES = [
    default,
    training_duel,
    frontline_brawl,
    blues_night,
    boss_ai_slop,
    boss_null_hydra,
]

DEFAULT_BATTLE = default
