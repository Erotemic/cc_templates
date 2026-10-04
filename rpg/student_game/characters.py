from __future__ import annotations

"""Characters connect stats, art, and moves with direct Python references."""

from rpg_battle.api import Character

from student_game import art, moves

knight = Character(
    'Knight of Dawn',
    id='knight',
    role='defender',
    hp=58,
    attack=10,
    defense=9,
    magic=4,
    speed=4,
    sprite=art.knight_dawn,
    moves=[
        moves.shield_bash,
        moves.stone_ward,
        moves.strike,
    ],
    description='A steadfast defender.',
)

druid = Character(
    'Verdant Druid',
    id='druid',
    role='support',
    hp=50,
    attack=6,
    defense=6,
    magic=9,
    speed=6,
    sprite=art.verdant_druid,
    moves=[
        moves.healing_light,
        moves.thorn_bind,
        moves.strike,
    ],
    description='A healer who slows foes with nature magic.',
)

ranger = Character(
    'Storm Ranger',
    id='ranger',
    role='striker',
    hp=46,
    attack=9,
    defense=5,
    magic=5,
    speed=10,
    sprite=art.storm_ranger,
    moves=[
        moves.arc_bolt,
        moves.wind_step,
        moves.strike,
    ],
    description='Fast and accurate.',
)

mage = Character(
    'Moon Mage',
    id='moon_mage',
    role='mage',
    hp=44,
    attack=5,
    defense=4,
    magic=11,
    speed=7,
    sprite=art.moon_mage,
    moves=[
        moves.arc_bolt,
        moves.ember,
        moves.strike,
    ],
    description='A focused spellcaster.',
)

moon_mage = mage

guardian = Character(
    'Crystal Guardian',
    id='guardian',
    role='tank',
    hp=62,
    attack=8,
    defense=10,
    magic=6,
    speed=4,
    sprite=art.crystal_guardian,
    moves=[
        moves.stone_ward,
        moves.shield_bash,
        moves.strike,
    ],
    description='A magical construct of crystal and light.',
)

spirit = Character(
    'Mist Spirit',
    id='spirit',
    role='controller',
    hp=42,
    attack=5,
    defense=5,
    magic=10,
    speed=5,
    sprite=art.mist_spirit,
    moves=[
        moves.mist_veil,
        moves.arc_bolt,
        moves.strike,
    ],
    description='Elusive and patient.',
)

runesage = Character(
    'Runesage',
    id='runesage',
    role='arcane',
    hp=45,
    attack=4,
    defense=5,
    magic=12,
    speed=8,
    sprite=art.runesage,
    moves=[
        moves.sine_wave,
        moves.square_pulse,
        moves.fractal_veil,
        moves.fourier_transform,
    ],
    description='A pattern mage whose spells are built from geometry.',
)

ai_slop = Character(
    'AI Slop',
    id='ai_slop',
    role='aberration',
    hp=52,
    attack=7,
    defense=6,
    magic=10,
    speed=3,
    sprite=art.ai_slop,
    moves=[
        moves.gradient_descent,
        moves.regularization,
        moves.artifact_burst,
    ],
    description='A strange synthetic ooze with mismatched hands and unstable artifacts.',
)

ai_slop_prime = Character(
    'AI Slop Prime',
    id='ai_slop_prime',
    role='boss',
    hp=96,
    attack=9,
    defense=8,
    magic=13,
    speed=3,
    sprite=art.ai_slop_prime,
    moves=[
        moves.gradient_descent,
        moves.regularization,
        moves.artifact_burst,
    ],
    description='A swollen, overtrained version of AI Slop that floods the screen with artifacts.',
)

null_hydra = Character(
    'Null Hydra',
    id='null_hydra',
    role='boss',
    hp=104,
    attack=8,
    defense=9,
    magic=14,
    speed=4,
    sprite=art.null_hydra,
    moves=[
        moves.singularity_coil,
        moves.pixel_storm,
        moves.entropy_shield,
    ],
    description='A many-eyed glitch serpent that spits zigzags and pixel storms.',
)

star_corsair = Character(
    'Star Corsair',
    id='star_corsair',
    role='striker',
    hp=48,
    attack=10,
    defense=5,
    magic=6,
    speed=9,
    sprite=art.star_corsair,
    moves=[
        moves.strike,
        moves.wind_step,
        moves.shield_bash,
    ],
    description='A swaggering duelist who looks dangerous on purpose.',
)

velvet_hexer = Character(
    'Velvet Hexer',
    id='velvet_hexer',
    role='controller',
    hp=46,
    attack=4,
    defense=5,
    magic=12,
    speed=7,
    sprite=art.velvet_hexer,
    moves=[
        moves.arc_bolt,
        moves.thorn_bind,
        moves.mist_veil,
    ],
    description='An elegant moon-and-thorn caster with a perfectly composed stare.',
)

siren_engine = Character(
    'Siren Engine',
    id='siren_engine',
    role='support',
    hp=50,
    attack=5,
    defense=6,
    magic=10,
    speed=6,
    sprite=art.siren_engine,
    moves=[
        moves.arc_bolt,
        moves.healing_light,
        moves.mist_veil,
    ],
    description='A machine singer that feels graceful and uncanny at the same time.',
)

space_pirate = Character(
    'Space Pirate',
    id='space_pirate',
    role='raider',
    hp=52,
    attack=9,
    defense=6,
    magic=5,
    speed=8,
    sprite=art.space_pirate,
    moves=[
        moves.strike,
        moves.shield_bash,
        moves.artifact_burst,
    ],
    description='A rough outlaw draped in scavenged star-tech and trophies.',
)

tiny_ancient_menace = Character(
    'Tiny Ancient Menace',
    id='tiny_ancient_menace',
    role='trickster',
    hp=40,
    attack=5,
    defense=6,
    magic=11,
    speed=8,
    sprite=art.tiny_ancient_menace,
    moves=[
        moves.square_pulse,
        moves.entropy_shield,
        moves.gradient_descent,
    ],
    description='A pocket ruin-lord with an ancient glare and a terrible attitude.',
)

cryptid_friend = Character(
    'Cryptid Friend',
    id='cryptid_friend',
    role='support',
    hp=47,
    attack=5,
    defense=6,
    magic=9,
    speed=7,
    sprite=art.cryptid_friend,
    moves=[
        moves.healing_light,
        moves.thorn_bind,
        moves.mist_veil,
    ],
    description='A warm, watchful companion that nobody can quite classify.',
)

CHARACTERS = [
    knight,
    druid,
    ranger,
    mage,
    guardian,
    spirit,
    runesage,
    ai_slop,
    ai_slop_prime,
    null_hydra,
    star_corsair,
    velvet_hexer,
    siren_engine,
    space_pirate,
    tiny_ancient_menace,
    cryptid_friend,
]
