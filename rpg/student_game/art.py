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

# AI Slop Prime deliberately keeps the Slop family colors, but pushes them
# farther apart so the boss can support layering, highlights, and readable
# embedded machinery without becoming a different species.
slop_prime = Palette(
    'Slop Prime',
    body=(151, 153, 119),
    accent=(226, 102, 176),
    eye=(247, 255, 205),
    detail=(64, 47, 82),
    id='slop_prime',
    extra={
        'body_shadow': (112, 112, 88),
        'body_light': (190, 190, 145),
        'accent_dark': (153, 65, 126),
        'accent_light': (246, 155, 207),
        'glitch': (255, 91, 198),
        'core': (221, 255, 156),
        'void': (39, 31, 51),
    },
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
    slop_prime,
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

# AI Slop Prime is the same synthetic-ooze idea pushed into a boss silhouette.
# It intentionally uses only the same readable Sprite primitives students use:
# overlapping ellipses for volume, polygons for panels/shards, circles for eyes,
# and doubled lines for the angular glitch limbs.
ai_slop_prime = Sprite('Ai Slop Prime', slop_prime, id='ai_slop_prime')

# Ground contact and lower shadow.  The wide puddle makes Prime feel heavy and
# keeps the irregular upper silhouette readable instead of looking like a ball.
ai_slop_prime.ellipse((0, 66), (174, 34), fill='body_shadow', outline='detail', width=3)
ai_slop_prime.ellipse((-58, 70), (64, 24), fill='body', outline='detail', width=2)
ai_slop_prime.ellipse((62, 72), (74, 22), fill='body', outline='detail', width=2)
ai_slop_prime.ellipse((-94, 68), (34, 15), fill='body_light', outline='body', width=1)
ai_slop_prime.ellipse((99, 70), (31, 13), fill='body_light', outline='body', width=1)

# Outer sludge mass, then a brighter inner mass.  Several asymmetric lobes break
# the contour so the boss reads as unstable liquid rather than a smooth mascot.
ai_slop_prime.ellipse((0, 5), (158, 132), fill='body_shadow', outline='detail', width=4)
ai_slop_prime.ellipse((-3, -3), (142, 116), fill='body', outline='detail', width=3)
ai_slop_prime.ellipse((-49, -48), (61, 52), fill='body', outline='detail', width=3)
ai_slop_prime.ellipse((12, -57), (78, 49), fill='body', outline='detail', width=3)
ai_slop_prime.ellipse((58, -36), (49, 66), fill='body', outline='detail', width=3)
ai_slop_prime.ellipse((-70, 18), (46, 70), fill='body', outline='detail', width=3)
ai_slop_prime.ellipse((73, 24), (43, 64), fill='body', outline='detail', width=3)

# Slime drips and splashes extend the silhouette past the core body.
ai_slop_prime.polygon([(-66, 35), (-82, 60), (-69, 57), (-61, 79), (-51, 50)], fill='body', outline='detail', width=2)
ai_slop_prime.polygon([(60, 40), (74, 66), (80, 52), (91, 75), (90, 34)], fill='body', outline='detail', width=2)
ai_slop_prime.polygon([(-27, 53), (-19, 91), (-8, 69), (3, 94), (11, 55)], fill='body', outline='detail', width=2)
ai_slop_prime.circle((-103, 46), 11, fill='body', outline='detail', width=2)
ai_slop_prime.circle((-116, 56), 6, fill='body_light', outline='detail', width=1)
ai_slop_prime.circle((105, 43), 10, fill='body', outline='detail', width=2)
ai_slop_prime.circle((118, 54), 5, fill='body_light', outline='detail', width=1)

# Wet highlights are separate shapes instead of a gradient so the sprite still
# advertises how far simple geometry can be pushed.
ai_slop_prime.ellipse((-29, -47), (38, 14), fill='body_light', outline='body_light', width=0)
ai_slop_prime.ellipse((31, -53), (27, 10), fill='body_light', outline='body_light', width=0)
ai_slop_prime.ellipse((-57, -9), (15, 31), fill='body_light', outline='body_light', width=0)
ai_slop_prime.ellipse((61, -12), (11, 25), fill='body_light', outline='body_light', width=0)
ai_slop_prime.circle((-74, 42), 5, fill='body_light', outline='body_light', width=0)
ai_slop_prime.circle((78, 47), 4, fill='body_light', outline='body_light', width=0)

# Side modules are deliberately mismatched.  They suggest failed synthetic
# hardware embedded in the ooze rather than symmetrical armor.
ai_slop_prime.rect((-76, -11), (31, 70), fill='accent_dark', outline='detail', width=3, border_radius=8)
ai_slop_prime.rect((-73, -15), (23, 54), fill='accent', outline='accent_light', width=2, border_radius=6)
ai_slop_prime.rect((-73, -30), (14, 15), fill='accent_light', outline='detail', width=2, border_radius=3)
ai_slop_prime.line([(-83, 2), (-63, 2)], color='detail', width=3)
ai_slop_prime.line([(-83, 12), (-66, 12)], color='detail', width=3)

ai_slop_prime.polygon([(68, -36), (88, -25), (91, 34), (68, 46), (61, 21)], fill='accent_dark', outline='detail', width=3)
ai_slop_prime.polygon([(72, -27), (83, -20), (84, 27), (70, 34), (67, 16)], fill='accent', outline='accent_light', width=2)
ai_slop_prime.rect((77, -8), (11, 17), fill='accent_light', outline='detail', width=2, border_radius=2)
ai_slop_prime.line([(72, 9), (83, 14)], color='detail', width=3)

# The broken crown/brace is a strong identifying shape.  Drawing each segment
# twice gives it a dark structural edge with a hot-pink signal running through.
_prime_crown = [(-58, -66), (-24, -83), (5, -68), (31, -91), (56, -66)]
ai_slop_prime.line(_prime_crown, color='detail', width=10)
ai_slop_prime.line(_prime_crown, color='accent', width=4)
ai_slop_prime.rect((35, -72), (19, 18), fill='accent', outline='detail', width=3, border_radius=3)
ai_slop_prime.rect((35, -72), (9, 8), fill='accent_light', outline='accent_light', width=0, border_radius=2)

# Three eyes keep the original Slop identity, but Prime gets layered sockets,
# different sizes, and offset pupils so the expression is more intentional.
ai_slop_prime.circle((-39, -16), 15, fill='accent_dark', outline='detail', width=2)
ai_slop_prime.circle((-39, -16), 11, fill='eye', outline='detail', width=2)
ai_slop_prime.circle((-42, -18), 3, fill='core', outline='core', width=0)
ai_slop_prime.circle((-36, -14), 2, fill='void', outline='void', width=0)

ai_slop_prime.circle((3, -23), 20, fill='accent_dark', outline='detail', width=3)
ai_slop_prime.circle((3, -23), 15, fill='eye', outline='detail', width=2)
ai_slop_prime.circle((-2, -28), 4, fill='core', outline='core', width=0)
ai_slop_prime.circle((7, -20), 3, fill='void', outline='void', width=0)

ai_slop_prime.circle((46, -11), 16, fill='accent_dark', outline='detail', width=2)
ai_slop_prime.circle((46, -11), 12, fill='eye', outline='detail', width=2)
ai_slop_prime.circle((42, -15), 3, fill='core', outline='core', width=0)
ai_slop_prime.circle((50, -8), 2, fill='void', outline='void', width=0)

# Pixel tears around the eye sockets make the clean circles look as if the
# generated image is breaking through a low-resolution mask.
ai_slop_prime.rect((-55, -26), (8, 8), fill='glitch', outline='glitch', width=0, border_radius=0)
ai_slop_prime.rect((-49, -33), (6, 6), fill='accent_light', outline='accent_light', width=0, border_radius=0)
ai_slop_prime.rect((20, -33), (8, 8), fill='glitch', outline='glitch', width=0, border_radius=0)
ai_slop_prime.rect((25, -25), (6, 6), fill='accent_light', outline='accent_light', width=0, border_radius=0)
ai_slop_prime.rect((58, -19), (7, 7), fill='glitch', outline='glitch', width=0, border_radius=0)

# The large jaw-like artifact plate is the boss's focal piece.  It is visibly
# cracked and partially swallowed by slime instead of being a flat pink block.
ai_slop_prime.polygon([(-57, 18), (-16, 14), (25, 17), (59, 27), (49, 58), (11, 65), (-39, 60)], fill='accent_dark', outline='detail', width=3)
ai_slop_prime.polygon([(-50, 22), (-15, 19), (22, 22), (52, 30), (43, 51), (9, 58), (-34, 54)], fill='accent', outline='accent_light', width=2)
ai_slop_prime.polygon([(-4, 20), (7, 31), (0, 42), (14, 56)], fill='accent_light', outline='detail', width=2)
ai_slop_prime.line([(25, 24), (17, 34), (29, 42), (22, 55)], color='detail', width=2)
ai_slop_prime.rect((-27, 39), (17, 17), fill='void', outline='detail', width=2, border_radius=3)
ai_slop_prime.rect((-27, 39), (9, 9), fill='glitch', outline='glitch', width=0, border_radius=1)

# Slime visibly spills over the machinery so the plates feel embedded.
ai_slop_prime.ellipse((-49, 18), (18, 31), fill='body', outline='detail', width=2)
ai_slop_prime.circle((-45, 34), 6, fill='body', outline='detail', width=1)
ai_slop_prime.ellipse((47, 24), (15, 26), fill='body', outline='detail', width=2)
ai_slop_prime.circle((45, 39), 5, fill='body_light', outline='body', width=1)

# Four glitch limbs make the silhouette boss-sized.  Each has a dark chassis
# and a thinner magenta signal trace, matching the crown construction above.
_prime_left_arm = [(-78, -10), (-116, -31), (-100, 4), (-132, 20)]
ai_slop_prime.line(_prime_left_arm, color='detail', width=9)
ai_slop_prime.line(_prime_left_arm, color='glitch', width=3)
ai_slop_prime.circle((-132, 20), 8, fill='body', outline='detail', width=2)
ai_slop_prime.circle((-137, 26), 4, fill='body_light', outline='body', width=1)

_prime_right_arm = [(80, -8), (117, -40), (102, -4), (133, 3)]
ai_slop_prime.line(_prime_right_arm, color='detail', width=9)
ai_slop_prime.line(_prime_right_arm, color='glitch', width=3)
ai_slop_prime.circle((133, 3), 8, fill='body', outline='detail', width=2)
ai_slop_prime.circle((139, 8), 4, fill='body_light', outline='body', width=1)

_prime_left_leg = [(-56, 55), (-92, 92), (-75, 116), (-111, 108)]
ai_slop_prime.line(_prime_left_leg, color='detail', width=10)
ai_slop_prime.line(_prime_left_leg, color='accent', width=4)
ai_slop_prime.ellipse((-111, 108), (28, 12), fill='body', outline='detail', width=2)

_prime_right_leg = [(56, 55), (88, 92), (78, 119), (116, 111)]
ai_slop_prime.line(_prime_right_leg, color='detail', width=10)
ai_slop_prime.line(_prime_right_leg, color='accent', width=4)
ai_slop_prime.ellipse((116, 111), (30, 12), fill='body', outline='detail', width=2)

# Loose artifact fragments sell the unstable/generated quality without making
# the main face harder to read.
ai_slop_prime.rect((-106, -48), (12, 12), fill='accent', outline='detail', width=2, border_radius=1)
ai_slop_prime.rect((-119, -58), (6, 6), fill='glitch', outline='glitch', width=0, border_radius=0)
ai_slop_prime.polygon([(101, -57), (111, -66), (119, -53), (108, -47)], fill='accent_light', outline='detail', width=2)
ai_slop_prime.rect((113, 43), (9, 9), fill='glitch', outline='glitch', width=0, border_radius=0)
ai_slop_prime.rect((-91, 83), (8, 8), fill='accent_light', outline='detail', width=1, border_radius=1)
ai_slop_prime.rect((83, 82), (7, 7), fill='accent', outline='detail', width=1, border_radius=1)
ai_slop_prime.circle((-124, 39), 4, fill='body', outline='detail', width=1)
ai_slop_prime.circle((125, 30), 3, fill='body_light', outline='body', width=1)

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
