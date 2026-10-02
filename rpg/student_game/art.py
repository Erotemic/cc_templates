from __future__ import annotations

"""Characters are drawn from simple shapes. Change these and preview immediately."""

from rpg_battle.api import Palette, Sprite

dawn = Palette(
    'Dawn',
    body=(92, 118, 196),
    accent=(247, 210, 126),
    eye=(245, 244, 255),
    detail=(55, 61, 97),
    id='dawn',
)

verdant = Palette(
    'Verdant',
    body=(77, 152, 101),
    accent=(182, 222, 124),
    eye=(244, 255, 241),
    detail=(44, 87, 53),
    id='verdant',
)

storm = Palette(
    'Storm',
    body=(87, 133, 176),
    accent=(184, 230, 245),
    eye=(243, 250, 255),
    detail=(42, 72, 112),
    id='storm',
)

moon = Palette(
    'Moon',
    body=(133, 110, 197),
    accent=(225, 215, 255),
    eye=(255, 248, 255),
    detail=(74, 52, 126),
    id='moon',
)

crystal = Palette(
    'Crystal',
    body=(115, 190, 205),
    accent=(215, 246, 255),
    eye=(240, 255, 255),
    detail=(50, 100, 110),
    id='crystal',
)

mist = Palette(
    'Mist',
    body=(159, 152, 198),
    accent=(226, 226, 248),
    eye=(250, 249, 255),
    detail=(90, 86, 125),
    id='mist',
)

rune = Palette(
    'Rune',
    body=(102, 124, 156),
    accent=(245, 198, 120),
    eye=(247, 248, 255),
    detail=(51, 60, 81),
    id='rune',
)

slop = Palette(
    'Slop',
    body=(148, 150, 126),
    accent=(228, 133, 186),
    eye=(245, 255, 214),
    detail=(76, 62, 95),
    id='slop',
)

corsair = Palette(
    'Corsair',
    body=(94, 92, 165),
    accent=(246, 204, 118),
    eye=(250, 246, 255),
    detail=(49, 42, 91),
    id='corsair',
)

velvet = Palette(
    'Velvet',
    body=(98, 66, 112),
    accent=(205, 179, 232),
    eye=(252, 245, 255),
    detail=(55, 32, 68),
    id='velvet',
)

siren = Palette(
    'Siren',
    body=(123, 164, 184),
    accent=(220, 236, 244),
    eye=(246, 252, 255),
    detail=(62, 88, 104),
    id='siren',
)

raider = Palette(
    'Raider',
    body=(123, 92, 82),
    accent=(236, 162, 107),
    eye=(250, 243, 236),
    detail=(63, 44, 40),
    id='raider',
)

menace = Palette(
    'Menace',
    body=(123, 111, 79),
    accent=(241, 202, 98),
    eye=(250, 243, 220),
    detail=(69, 58, 33),
    id='menace',
)

cryptid = Palette(
    'Cryptid',
    body=(115, 154, 137),
    accent=(203, 234, 216),
    eye=(246, 255, 248),
    detail=(54, 84, 70),
    id='cryptid',
)

PALETTES = [
    dawn,
    verdant,
    storm,
    moon,
    crystal,
    mist,
    rune,
    slop,
    corsair,
    velvet,
    siren,
    raider,
    menace,
    cryptid,
]

knight_dawn = Sprite('Knight Dawn', dawn, id='knight_dawn')
knight_dawn.polygon([(-28, 14), (0, -52), (28, 14)], fill='accent', outline='detail', width=2)
knight_dawn.rect((0, 14), (68, 78), fill='body', outline='detail', width=2, border_radius=10)
knight_dawn.rect((0, -8), (46, 52), fill='accent', outline='detail', width=2, border_radius=10)
knight_dawn.rect((-40, 10), (24, 48), fill='accent', outline='detail', width=2, border_radius=10)
knight_dawn.line([(-40, -12), (-40, 34)], color='detail', width=4)
knight_dawn.circle((-12, -14), 6, fill='eye', outline='detail', width=1)
knight_dawn.circle((12, -14), 6, fill='eye', outline='detail', width=1)
knight_dawn.line([(-12, -14), (-12, -12)], color='detail', width=2)
knight_dawn.line([(12, -14), (12, -12)], color='detail', width=2)
knight_dawn.polyline([(-12, 2), (0, 8), (12, 2)], color='detail', width=2)

verdant_druid = Sprite('Verdant Druid', verdant, id='verdant_druid')
verdant_druid.ellipse((0, 12), (76, 90), fill='body', outline='detail', width=2)
verdant_druid.polygon([(-26, -36), (-6, -56), (0, -28)], fill='accent', outline='detail', width=2)
verdant_druid.polygon([(26, -36), (6, -56), (0, -28)], fill='accent', outline='detail', width=2)
verdant_druid.line([(-20, 20), (0, 42), (20, 20)], color='detail', width=3)
verdant_druid.polyline([(-38, -4), (-56, -28), (-52, 26)], color='detail', width=4)
verdant_druid.circle((-12, -10), 6, fill='eye', outline='detail', width=1)
verdant_druid.circle((12, -10), 6, fill='eye', outline='detail', width=1)
verdant_druid.line([(-12, -10), (-12, -8)], color='detail', width=2)
verdant_druid.line([(12, -10), (12, -8)], color='detail', width=2)
verdant_druid.polyline([(-12, 6), (0, 12), (12, 6)], color='detail', width=2)

storm_ranger = Sprite('Storm Ranger', storm, id='storm_ranger')
storm_ranger.ellipse((0, 8), (70, 88), fill='body', outline='detail', width=2)
storm_ranger.polygon([(-36, -10), (-8, -58), (18, -16)], fill='accent', outline='detail', width=2)
storm_ranger.line([(34, -32), (52, 28)], color='detail', width=5)
storm_ranger.line([(14, -10), (44, 8)], color='accent', width=3)
storm_ranger.circle((-12, -14), 6, fill='eye', outline='detail', width=1)
storm_ranger.circle((12, -14), 6, fill='eye', outline='detail', width=1)
storm_ranger.line([(-12, -14), (-12, -12)], color='detail', width=2)
storm_ranger.line([(12, -14), (12, -12)], color='detail', width=2)
storm_ranger.polyline([(-12, 2), (0, 8), (12, 2)], color='detail', width=2)

moon_mage = Sprite('Moon Mage', moon, id='moon_mage')
moon_mage.ellipse((0, 12), (74, 92), fill='body', outline='detail', width=2)
moon_mage.circle((0, -46), 20, fill='accent', outline='detail', width=2)
moon_mage.polyline([(-20, -28), (0, -42), (20, -28)], color='detail', width=3)
moon_mage.circle((28, -32), 8, fill='accent', outline='detail', width=2)
moon_mage.circle((-30, 32), 10, fill='accent', outline='detail', width=2)
moon_mage.circle((-12, -8), 6, fill='eye', outline='detail', width=1)
moon_mage.circle((12, -8), 6, fill='eye', outline='detail', width=1)
moon_mage.line([(-12, -8), (-12, -6)], color='detail', width=2)
moon_mage.line([(12, -8), (12, -6)], color='detail', width=2)
moon_mage.polyline([(-12, 8), (0, 14), (12, 8)], color='detail', width=2)

crystal_guardian = Sprite('Crystal Guardian', crystal, id='crystal_guardian')
crystal_guardian.polygon([(-40, 10), (-14, -44), (14, -44), (40, 10), (20, 52), (-20, 52)], fill='body', outline='detail', width=2)
crystal_guardian.polygon([(-12, -52), (0, -74), (12, -52)], fill='accent', outline='detail', width=2)
crystal_guardian.polygon([(-54, 4), (-34, -20), (-26, 22)], fill='accent', outline='detail', width=2)
crystal_guardian.polygon([(54, 4), (34, -20), (26, 22)], fill='accent', outline='detail', width=2)
crystal_guardian.circle((-12, -10), 6, fill='eye', outline='detail', width=1)
crystal_guardian.circle((12, -10), 6, fill='eye', outline='detail', width=1)
crystal_guardian.line([(-12, -10), (-12, -8)], color='detail', width=2)
crystal_guardian.line([(12, -10), (12, -8)], color='detail', width=2)
crystal_guardian.polyline([(-12, 6), (0, 12), (12, 6)], color='detail', width=2)

mist_spirit = Sprite('Mist Spirit', mist, id='mist_spirit')
mist_spirit.ellipse((0, 8), (78, 88), fill='body', outline='detail', width=2)
mist_spirit.ellipse((0, 26), (56, 40), fill='accent', outline='detail', width=2)
mist_spirit.polyline([(-30, 20), (-10, 44), (8, 20), (28, 44)], color='detail', width=3)
mist_spirit.circle((-28, -30), 7, fill='accent', outline='detail', width=2)
mist_spirit.circle((28, -36), 9, fill='accent', outline='detail', width=2)
mist_spirit.circle((-12, -16), 6, fill='eye', outline='detail', width=1)
mist_spirit.circle((12, -16), 6, fill='eye', outline='detail', width=1)
mist_spirit.line([(-12, -16), (-12, -14)], color='detail', width=2)
mist_spirit.line([(12, -16), (12, -14)], color='detail', width=2)
mist_spirit.polyline([(-12, 0), (0, 6), (12, 0)], color='detail', width=2)

runesage = Sprite('Runesage', rune, id='runesage')
runesage.circle((0, 10), 40, fill='body', outline='detail', width=2)
runesage.circle((0, 10), 28, fill='accent', outline='detail', width=2)
runesage.polyline([(-42, -30), (-18, -50), (0, -30), (18, -50), (42, -30)], color='accent', width=3)
runesage.line([(-52, 16), (52, 16)], color='detail', width=3)
runesage.polyline([(-30, 28), (-14, 14), (0, 28), (14, 14), (30, 28)], color='accent', width=3)
runesage.circle((-12, -8), 6, fill='eye', outline='detail', width=1)
runesage.circle((12, -8), 6, fill='eye', outline='detail', width=1)
runesage.line([(-12, -8), (-12, -6)], color='detail', width=2)
runesage.line([(12, -8), (12, -6)], color='detail', width=2)
runesage.polyline([(-12, 8), (0, 14), (12, 8)], color='detail', width=2)

ai_slop = Sprite('Ai Slop', slop, id='ai_slop')
ai_slop.ellipse((0, 8), (82, 88), fill='body', outline='detail', width=2)
ai_slop.polygon([(-18, -52), (18, -46), (32, -10), (-26, -18)], fill='accent', outline='detail', width=2)
ai_slop.rect((-48, 12), (16, 42), fill='accent', outline='detail', width=2, border_radius=5)
ai_slop.rect((46, -6), (18, 52), fill='accent', outline='detail', width=2, border_radius=5)
ai_slop.line([(-46, 8), (-78, -4), (-64, 30), (-88, 36)], color='detail', width=4)
ai_slop.line([(46, -2), (82, -26), (68, 12), (98, 6)], color='detail', width=4)
ai_slop.polygon([(-8, 26), (10, 18), (26, 34), (-2, 42)], fill='accent', outline='detail', width=2)
ai_slop.circle((-26, -8), 5, fill='eye', outline='detail', width=1)
ai_slop.circle((16, -2), 7, fill='eye', outline='detail', width=1)
ai_slop.line([(-30, 22), (-2, 32), (18, 18), (30, 34)], color='detail', width=3)
ai_slop.rect((-12, -34), (10, 10), fill='accent', outline='detail', width=2, border_radius=2)
ai_slop.rect((32, 24), (12, 12), fill='accent', outline='detail', width=2, border_radius=2)

ai_slop_prime = Sprite('Ai Slop Prime', slop, id='ai_slop_prime')
ai_slop_prime.ellipse((0, 0), (112, 104), fill='body', outline='detail', width=2)
ai_slop_prime.polygon([(-34, -66), (22, -60), (48, -18), (-42, -24)], fill='accent', outline='detail', width=2)
ai_slop_prime.rect((-62, 10), (20, 54), fill='accent', outline='detail', width=2, border_radius=4)
ai_slop_prime.rect((58, -8), (22, 62), fill='accent', outline='detail', width=2, border_radius=4)
ai_slop_prime.line([(-60, 8), (-104, -10), (-84, 34), (-116, 44)], color='detail', width=4)
ai_slop_prime.line([(58, -4), (104, -30), (84, 14), (122, 8)], color='detail', width=4)
ai_slop_prime.circle((-30, -12), 7, fill='eye', outline='detail', width=1)
ai_slop_prime.circle((10, -6), 8, fill='eye', outline='detail', width=1)
ai_slop_prime.circle((38, 10), 6, fill='eye', outline='detail', width=1)
ai_slop_prime.line([(-36, 30), (-6, 42), (18, 26), (36, 44)], color='detail', width=4)
ai_slop_prime.rect((-16, -40), (12, 12), fill='accent', outline='detail', width=2, border_radius=2)
ai_slop_prime.rect((36, 28), (14, 14), fill='accent', outline='detail', width=2, border_radius=2)

null_hydra = Sprite('Null Hydra', rune, id='null_hydra')
null_hydra.ellipse((0, 8), (108, 96), fill='body', outline='detail', width=2)
null_hydra.polygon([(-58, -8), (-30, -54), (-8, -6)], fill='accent', outline='detail', width=2)
null_hydra.polygon([(0, -18), (18, -70), (32, -10)], fill='accent', outline='detail', width=2)
null_hydra.polygon([(50, -4), (72, -50), (88, 6)], fill='accent', outline='detail', width=2)
null_hydra.line([(-48, 14), (-82, 44), (-66, 72)], color='detail', width=4)
null_hydra.line([(0, 20), (-10, 64), (12, 90)], color='detail', width=4)
null_hydra.line([(52, 18), (92, 54), (72, 84)], color='detail', width=4)
null_hydra.circle((-28, -18), 6, fill='eye', outline='detail', width=1)
null_hydra.circle((18, -26), 7, fill='eye', outline='detail', width=1)
null_hydra.circle((58, -12), 6, fill='eye', outline='detail', width=1)
null_hydra.polyline([(-34, 30), (-12, 40), (8, 24), (28, 42), (48, 28)], color='detail', width=3)
null_hydra.circle((-60, 36), 8, fill='accent', outline='detail', width=2)
null_hydra.circle((62, 42), 10, fill='accent', outline='detail', width=2)

star_corsair = Sprite('Star Corsair', corsair, id='star_corsair')
star_corsair.ellipse((0, 10), (78, 88), fill='body', outline='detail', width=2)
star_corsair.polyline([(-52, -34), (-14, -54), (24, -48), (52, -30)], color='accent', width=5)
star_corsair.polygon([(-8, -60), (0, -82), (12, -56)], fill='accent', outline='detail', width=2)
star_corsair.line([(28, -8), (64, 8)], color='accent', width=4)
star_corsair.line([(-22, 36), (12, 46), (34, 28)], color='detail', width=3)
star_corsair.rect((-34, 18), (18, 42), fill='accent', outline='detail', width=2, border_radius=4)
star_corsair.circle((-12, -14), 6, fill='eye', outline='detail', width=1)
star_corsair.circle((12, -14), 6, fill='eye', outline='detail', width=1)
star_corsair.line([(-12, -14), (-12, -12)], color='detail', width=2)
star_corsair.line([(12, -14), (12, -12)], color='detail', width=2)
star_corsair.polyline([(-12, 2), (0, 8), (12, 2)], color='detail', width=2)

velvet_hexer = Sprite('Velvet Hexer', velvet, id='velvet_hexer')
velvet_hexer.ellipse((0, 12), (70, 96), fill='body', outline='detail', width=2)
velvet_hexer.polyline([(-24, -50), (0, -68), (24, -50)], color='accent', width=4)
velvet_hexer.polyline([(-40, -6), (-22, 46), (0, 28), (22, 50), (40, -6)], color='accent', width=3)
velvet_hexer.circle((-36, -18), 6, fill='accent', outline='detail', width=2)
velvet_hexer.circle((36, -4), 6, fill='accent', outline='detail', width=2)
velvet_hexer.polyline([(-20, 24), (-4, 8), (12, 24), (28, 8)], color='detail', width=3)
velvet_hexer.circle((-12, -16), 6, fill='eye', outline='detail', width=1)
velvet_hexer.circle((12, -16), 6, fill='eye', outline='detail', width=1)
velvet_hexer.line([(-12, -16), (-12, -14)], color='detail', width=2)
velvet_hexer.line([(12, -16), (12, -14)], color='detail', width=2)
velvet_hexer.polyline([(-12, 0), (0, 6), (12, 0)], color='detail', width=2)

siren_engine = Sprite('Siren Engine', siren, id='siren_engine')
siren_engine.ellipse((0, 6), (74, 94), fill='body', outline='detail', width=2)
siren_engine.circle((0, -40), 20, fill='accent', outline='detail', width=2)
siren_engine.polyline([(-34, -22), (-20, -48), (-8, -22)], color='detail', width=3)
siren_engine.polyline([(34, -22), (20, -48), (8, -22)], color='detail', width=3)
siren_engine.circle((-34, 6), 8, fill='accent', outline='detail', width=2)
siren_engine.circle((34, 6), 8, fill='accent', outline='detail', width=2)
siren_engine.polyline([(-18, 44), (0, 64), (18, 44)], color='accent', width=4)
siren_engine.line([(-10, -18), (-10, 38)], color='detail', width=2)
siren_engine.line([(10, -18), (10, 38)], color='detail', width=2)
siren_engine.circle((-12, -12), 6, fill='eye', outline='detail', width=1)
siren_engine.circle((12, -12), 6, fill='eye', outline='detail', width=1)
siren_engine.line([(-12, -12), (-12, -10)], color='detail', width=2)
siren_engine.line([(12, -12), (12, -10)], color='detail', width=2)
siren_engine.polyline([(-12, 4), (0, 10), (12, 4)], color='detail', width=2)

space_pirate = Sprite('Space Pirate', raider, id='space_pirate')
space_pirate.ellipse((0, 10), (80, 92), fill='body', outline='detail', width=2)
space_pirate.polygon([(-40, -24), (-10, -60), (20, -18)], fill='accent', outline='detail', width=2)
space_pirate.line([(-34, 34), (-10, 54), (18, 24)], color='detail', width=3)
space_pirate.rect((34, 12), (20, 52), fill='accent', outline='detail', width=2, border_radius=3)
space_pirate.circle((16, -16), 8, fill='accent', outline='detail', width=2)
space_pirate.line([(44, -10), (58, 28), (74, 18)], color='detail', width=3)
space_pirate.line([(-28, -8), (-50, 6), (-40, 42)], color='accent', width=3)
space_pirate.circle((-12, -14), 6, fill='eye', outline='detail', width=1)
space_pirate.circle((12, -14), 6, fill='eye', outline='detail', width=1)
space_pirate.line([(-12, -14), (-12, -12)], color='detail', width=2)
space_pirate.line([(12, -14), (12, -12)], color='detail', width=2)
space_pirate.polyline([(-12, 2), (0, 8), (12, 2)], color='detail', width=2)

tiny_ancient_menace = Sprite('Tiny Ancient Menace', menace, id='tiny_ancient_menace')
tiny_ancient_menace.circle((0, 18), 30, fill='body', outline='detail', width=2)
tiny_ancient_menace.polyline([(-20, -12), (-8, -36), (0, -18), (8, -36), (20, -12)], color='accent', width=4)
tiny_ancient_menace.circle((-28, -6), 6, fill='accent', outline='detail', width=2)
tiny_ancient_menace.circle((28, -2), 6, fill='accent', outline='detail', width=2)
tiny_ancient_menace.polyline([(-18, 44), (-8, 24), (0, 44), (8, 24), (18, 44)], color='detail', width=3)
tiny_ancient_menace.line([(-20, 20), (-36, 34)], color='detail', width=3)
tiny_ancient_menace.line([(20, 20), (36, 34)], color='detail', width=3)
tiny_ancient_menace.circle((-12, 2), 6, fill='eye', outline='detail', width=1)
tiny_ancient_menace.circle((12, 2), 6, fill='eye', outline='detail', width=1)
tiny_ancient_menace.line([(-12, 2), (-12, 4)], color='detail', width=2)
tiny_ancient_menace.line([(12, 2), (12, 4)], color='detail', width=2)
tiny_ancient_menace.polyline([(-12, 18), (0, 24), (12, 18)], color='detail', width=2)

cryptid_friend = Sprite('Cryptid Friend', cryptid, id='cryptid_friend')
cryptid_friend.ellipse((0, 14), (82, 92), fill='body', outline='detail', width=2)
cryptid_friend.polyline([(-24, -40), (-16, -60), (-8, -40)], color='accent', width=3)
cryptid_friend.polyline([(24, -40), (16, -60), (8, -40)], color='accent', width=3)
cryptid_friend.polygon([(-36, 12), (-56, -8), (-46, 30)], fill='accent', outline='detail', width=2)
cryptid_friend.polygon([(36, 12), (56, -8), (46, 30)], fill='accent', outline='detail', width=2)
cryptid_friend.polyline([(-28, 34), (-10, 54), (10, 54), (28, 34)], color='accent', width=4)
cryptid_friend.circle((-30, -12), 5, fill='accent', outline='detail', width=2)
cryptid_friend.circle((30, -8), 5, fill='accent', outline='detail', width=2)
cryptid_friend.circle((-12, -10), 6, fill='eye', outline='detail', width=1)
cryptid_friend.circle((12, -10), 6, fill='eye', outline='detail', width=1)
cryptid_friend.line([(-12, -10), (-12, -8)], color='detail', width=2)
cryptid_friend.line([(12, -10), (12, -8)], color='detail', width=2)
cryptid_friend.polyline([(-12, 6), (0, 12), (12, 6)], color='detail', width=2)

SPRITES = [
    knight_dawn,
    verdant_druid,
    storm_ranger,
    moon_mage,
    crystal_guardian,
    mist_spirit,
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
