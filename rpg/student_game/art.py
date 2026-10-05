from __future__ import annotations

"""Still character frames. Change one frame and preview it immediately."""

from rpg_battle.api import CharacterArt, CodeSpriteFrame, FrameAnimation, Palette, SvgSpriteFrame

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
    body=(70, 116, 72),
    accent=(175, 207, 92),
    eye=(239, 250, 198),
    detail=(35, 55, 40),
    id='verdant',
    extra={
        'leaf_dark': (43, 83, 55),
        'leaf_mid': (93, 145, 70),
        'leaf_light': (197, 221, 114),
        'bark': (104, 74, 50),
        'bark_light': (158, 117, 73),
        'seed': (245, 204, 92),
        'seed_light': (255, 239, 161),
        'flower': (205, 120, 143),
        'shadow': (29, 49, 35),
    },
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
    body=(56, 61, 116),
    accent=(201, 211, 239),
    eye=(244, 250, 255),
    detail=(25, 27, 60),
    id='moon',
    extra={
        'void': (14, 16, 39),
        'robe_shadow': (37, 39, 82),
        'robe_light': (90, 92, 157),
        'moon_blue': (126, 170, 220),
        'moon_light': (235, 241, 255),
        'star': (174, 211, 246),
        'ember': (236, 132, 66),
        'ember_light': (255, 220, 148),
    },
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

# Mist Spirit uses a colder, lower-contrast palette than the project's friendly
# default ghosts.  The sprite is built around negative space, a porcelain mask,
# and layered vapor ribbons rather than a conventional body.
mist_spirit_palette = Palette(
    'Mist Spirit',
    body=(99, 112, 148),
    accent=(190, 216, 229),
    eye=(221, 255, 242),
    detail=(43, 49, 76),
    id='mist_spirit_palette',
    extra={
        'void': (23, 27, 43),
        'fog_shadow': (66, 76, 110),
        'fog_mid': (131, 151, 180),
        'fog_light': (221, 235, 238),
        'porcelain': (229, 231, 224),
        'porcelain_shadow': (177, 186, 191),
        'glow': (153, 239, 220),
        'spark': (111, 192, 211),
        'crack': (77, 88, 119),
    },
)

rune = Palette(
    'Rune',
    body=(102, 124, 156),
    accent=(245, 198, 120),
    eye=(247, 248, 255),
    detail=(51, 60, 81),
    id='rune',
)

rune_sage = Palette(
    'Rune Sage',
    body=(55, 64, 96),
    accent=(202, 156, 73),
    eye=(223, 255, 244),
    detail=(25, 28, 47),
    id='rune_sage',
    extra={
        'robe_shadow': (34, 39, 66),
        'robe_light': (82, 96, 132),
        'stone': (97, 105, 126),
        'stone_light': (132, 142, 160),
        'rune': (81, 224, 207),
        'rune_light': (176, 255, 235),
        'gold_light': (242, 205, 111),
        'void': (12, 14, 27),
    },
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
    body=(66, 34, 76),
    accent=(181, 70, 132),
    eye=(252, 228, 245),
    detail=(30, 17, 38),
    id='velvet',
    extra={
        'velvet_dark': (41, 22, 52),
        'velvet_light': (115, 58, 126),
        'lining': (213, 105, 163),
        'mask': (229, 204, 219),
        'thorn': (92, 126, 83),
        'thorn_light': (159, 184, 116),
        'hex': (239, 132, 187),
        'moon': (208, 190, 232),
        'void': (17, 12, 26),
    },
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
    body=(125, 96, 58),
    accent=(213, 166, 71),
    eye=(255, 233, 165),
    detail=(48, 37, 28),
    id='menace',
    extra={
        'stone_dark': (78, 63, 47),
        'stone_mid': (145, 118, 76),
        'stone_light': (184, 153, 96),
        'patina': (64, 153, 145),
        'patina_light': (112, 208, 185),
        'glyph': (246, 201, 98),
        'void': (27, 24, 22),
        'ember': (211, 77, 48),
    },
)

cryptid = Palette(
    'Cryptid',
    body=(49, 85, 78),
    accent=(107, 154, 119),
    eye=(255, 232, 164),
    detail=(23, 43, 42),
    id='cryptid',
    extra={
        'night': (17, 31, 34),
        'fur_shadow': (34, 63, 60),
        'fur_light': (80, 116, 104),
        'moss': (115, 150, 83),
        'branch': (87, 64, 49),
        'lantern': (241, 185, 99),
        'lantern_light': (255, 237, 178),
        'mist': (151, 186, 178),
        'mist_light': (198, 216, 205),
    },
)

PALETTES = [
    dawn,
    verdant,
    storm,
    moon,
    crystal,
    mist,
    mist_spirit_palette,
    rune,
    rune_sage,
    slop,
    slop_prime,
    corsair,
    velvet,
    siren,
    raider,
    menace,
    cryptid,
]

def _draw_knight_dawn(frame: CodeSpriteFrame, *, sword_tip: tuple[int, int] | None = None) -> CodeSpriteFrame:
    """Draw one Knight of Dawn frame.

    The attack frames reuse the same drawing function and only change the sword
    tip. This keeps the frame-by-frame example small enough for students to
    compare directly.
    """

    frame.polygon([(-28, 14), (0, -52), (28, 14)], fill='accent', outline='detail', width=2)
    frame.rect((0, 14), (68, 78), fill='body', outline='detail', width=2, border_radius=10)
    frame.rect((0, -8), (46, 52), fill='accent', outline='detail', width=2, border_radius=10)
    frame.rect((-40, 10), (24, 48), fill='accent', outline='detail', width=2, border_radius=10)
    frame.line([(-40, -12), (-40, 34)], color='detail', width=4)
    frame.circle((-12, -14), 6, fill='eye', outline='detail', width=1)
    frame.circle((12, -14), 6, fill='eye', outline='detail', width=1)
    frame.line([(-12, -14), (-12, -12)], color='detail', width=2)
    frame.line([(12, -14), (12, -12)], color='detail', width=2)
    frame.polyline([(-12, 2), (0, 8), (12, 2)], color='detail', width=2)
    if sword_tip is not None:
        # A simple sword makes the frame changes obvious: raised, forward, down.
        frame.line([(28, 18), sword_tip], color='detail', width=8)
        frame.line([(28, 18), sword_tip], color='accent', width=4)
        frame.line([(22, 14), (34, 22)], color='detail', width=5)
    return frame


knight_dawn_idle_frame = _draw_knight_dawn(
    CodeSpriteFrame('Knight Dawn Idle', dawn, id='knight_dawn_idle')
)
knight_dawn_attack_1_frame = _draw_knight_dawn(
    CodeSpriteFrame('Knight Dawn Attack 1', dawn, id='knight_dawn_attack_1'),
    sword_tip=(61, -48),
)
knight_dawn_attack_2_frame = _draw_knight_dawn(
    CodeSpriteFrame('Knight Dawn Attack 2', dawn, id='knight_dawn_attack_2'),
    sword_tip=(88, -7),
)
knight_dawn_attack_3_frame = _draw_knight_dawn(
    CodeSpriteFrame('Knight Dawn Attack 3', dawn, id='knight_dawn_attack_3'),
    sword_tip=(76, 44),
)

# This is the complete frame-animation example. Hurt and faint are deliberately
# omitted, so students can see that missing states fall back to the idle frame.
knight_dawn_art = CharacterArt(
    'Knight Dawn Art',
    id='knight_dawn',
    idle=knight_dawn_idle_frame,
    attack=FrameAnimation(
        frames=[
            knight_dawn_attack_1_frame,
            knight_dawn_attack_2_frame,
            knight_dawn_attack_3_frame,
        ],
        fps=8,
        loop=False,
    ),
)

# Compatibility name used by older exercises.
knight_dawn = knight_dawn_art

verdant_druid = CodeSpriteFrame('Verdant Druid', verdant, id='verdant_druid', scale=0.50)

# Verdant Druid is a walking seed-shrine: part masked wanderer, part young
# tree.  The character is intentionally not a conventional green-robed wizard.
# A crooked branch crown, broad leaf mantle, hanging seed lantern, root-split
# cloak, and a glowing germinating heart give the silhouette its own language.

# Rooted lower cloak: the dark back mass establishes a bell-shaped silhouette,
# then overlapping leaf/root plates split it into an organic three-pronged hem.
verdant_druid.polygon(
    [(-48, 10), (-64, 59), (-54, 102), (-29, 91), (-9, 118), (4, 91), (27, 111), (39, 83), (61, 96), (58, 54), (43, 8)],
    fill='shadow', outline='detail', width=3,
)
verdant_druid.polygon(
    [(-38, 9), (-49, 55), (-38, 88), (-20, 80), (-7, 104), (4, 79), (22, 98), (31, 73), (47, 82), (46, 48), (34, 9)],
    fill='body', outline='leaf_dark', width=2,
)
verdant_druid.polygon([(-35, 36), (-50, 68), (-33, 84), (-12, 69), (-6, 31)], fill='leaf_mid', outline='leaf_dark', width=2)
verdant_druid.polygon([(8, 31), (18, 74), (35, 88), (43, 62), (31, 34)], fill='leaf_dark', outline='detail', width=2)
verdant_druid.polygon([(-9, 42), (1, 82), (13, 45), (4, 24)], fill='leaf_light', outline='body', width=2)

# Broad asymmetrical mantle made from leaves rather than shoulders.  The left
# leaf turns upward while the right leaf droops, keeping the pose from feeling
# like a mirrored icon.
verdant_druid.polygon([(-69, 4), (-91, -15), (-82, -43), (-49, -36), (-20, -10), (-33, 20)], fill='leaf_dark', outline='detail', width=3)
verdant_druid.polygon([(-63, 0), (-78, -15), (-70, -33), (-49, -27), (-28, -8), (-38, 12)], fill='leaf_mid', outline='leaf_dark', width=2)
verdant_druid.line([(-70, -28), (-48, -10), (-34, 7)], color='leaf_light', width=3)
verdant_druid.polygon([(27, -8), (57, -31), (89, -19), (83, 9), (57, 28), (35, 18)], fill='leaf_mid', outline='detail', width=3)
verdant_druid.polygon([(35, -5), (58, -23), (78, -15), (73, 4), (55, 17), (40, 12)], fill='leaf_light', outline='leaf_dark', width=2)
verdant_druid.line([(43, 5), (61, -8), (75, -13)], color='body', width=3)

# Wooden seed-mask.  It is narrow and elongated, with two tiny luminous slits
# instead of the project's friendly default face.
verdant_druid.polygon(
    [(-27, -56), (-15, -79), (5, -88), (25, -73), (29, -47), (17, -25), (-2, -18), (-23, -31)],
    fill='bark', outline='detail', width=3,
)
verdant_druid.polygon(
    [(-20, -54), (-10, -71), (5, -77), (18, -66), (21, -48), (12, -32), (-2, -27), (-16, -37)],
    fill='bark_light', outline='bark', width=2,
)
verdant_druid.polygon([(-11, -55), (-4, -59), (-1, -52), (-7, -48)], fill='eye', outline='detail', width=1)
verdant_druid.polygon([(7, -58), (14, -54), (10, -47), (4, -51)], fill='eye', outline='detail', width=1)
verdant_druid.line([(-2, -71), (2, -62), (-1, -54)], color='detail', width=2)
verdant_druid.line([(0, -28), (6, -38), (4, -47)], color='bark', width=2)

# Branch crown / antlers: thick bark under-strokes with thinner lit branches.
# Buds and leaves are deliberately sparse so the silhouette stays readable.
_left_branch = [(-14, -73), (-38, -94), (-58, -102), (-73, -119)]
_right_branch = [(15, -72), (40, -91), (59, -89), (78, -108)]
for branch in (_left_branch, _right_branch):
    verdant_druid.polyline(branch, color='detail', width=8)
    verdant_druid.polyline(branch, color='bark', width=5)
verdant_druid.line([(-42, -96), (-48, -115)], color='bark', width=5)
verdant_druid.line([(-57, -101), (-67, -89)], color='bark', width=5)
verdant_druid.line([(42, -91), (48, -111)], color='bark', width=5)
verdant_druid.line([(58, -90), (66, -76)], color='bark', width=5)
verdant_druid.polygon([(-54, -120), (-45, -126), (-39, -116), (-47, -109)], fill='leaf_light', outline='leaf_dark', width=1)
verdant_druid.polygon([(-76, -123), (-69, -132), (-60, -125), (-67, -116)], fill='leaf_mid', outline='leaf_dark', width=1)
verdant_druid.polygon([(43, -116), (50, -125), (59, -118), (51, -108)], fill='leaf_light', outline='leaf_dark', width=1)
verdant_druid.polygon([(76, -112), (84, -119), (91, -110), (83, -102)], fill='leaf_mid', outline='leaf_dark', width=1)
verdant_druid.circle((-65, -90), 5, fill='flower', outline='detail', width=1)
verdant_druid.circle((68, -76), 4, fill='seed', outline='detail', width=1)

# Germinating heart / seed shrine at the chest.  Concentric shapes make this the
# visual focus and connect naturally to the character's healing role.
verdant_druid.circle((0, 8), 19, fill='leaf_dark', outline='detail', width=2)
verdant_druid.circle((0, 8), 13, fill='seed', outline='bark', width=2)
verdant_druid.ellipse((0, 7), (11, 17), fill='seed_light', outline='seed', width=1)
verdant_druid.line([(0, -1), (0, -12)], color='leaf_light', width=3)
verdant_druid.polygon([(0, -11), (-10, -17), (-4, -25), (3, -17)], fill='leaf_light', outline='leaf_dark', width=1)
verdant_druid.polygon([(1, -11), (10, -19), (14, -12), (7, -6)], fill='leaf_mid', outline='leaf_dark', width=1)

# A crooked staff grows from the right side and carries a hanging seed lantern.
# The lantern gives the support/healer silhouette an immediate gameplay cue.
_staff = [(54, 22), (72, 4), (67, -21), (82, -42), (74, -64)]
verdant_druid.polyline(_staff, color='detail', width=9)
verdant_druid.polyline(_staff, color='bark', width=6)
verdant_druid.line([(79, -43), (96, -49)], color='bark', width=5)
verdant_druid.line([(95, -49), (95, -30)], color='detail', width=3)
verdant_druid.ellipse((95, -20), (20, 27), fill='seed', outline='detail', width=2)
verdant_druid.ellipse((95, -22), (10, 15), fill='seed_light', outline='seed', width=1)
verdant_druid.polygon([(87, -34), (94, -43), (101, -34), (95, -29)], fill='leaf_light', outline='leaf_dark', width=1)

# The opposite side is a living thorn-vine rather than a second arm.
verdant_druid.polyline([(-49, 19), (-70, 31), (-77, 52), (-67, 70), (-83, 87)], color='detail', width=8)
verdant_druid.polyline([(-48, 19), (-68, 31), (-74, 51), (-64, 69), (-80, 85)], color='leaf_dark', width=5)
verdant_druid.polygon([(-72, 39), (-84, 35), (-76, 48)], fill='leaf_light', outline='detail', width=1)
verdant_druid.polygon([(-66, 68), (-55, 73), (-67, 78)], fill='leaf_mid', outline='detail', width=1)
verdant_druid.polygon([(-80, 83), (-93, 86), (-84, 95)], fill='leaf_light', outline='detail', width=1)

# A few spores and drifting seeds keep the air around the druid alive without
# filling every empty space.
verdant_druid.circle((-91, -61), 4, fill='seed_light', outline='leaf_dark', width=1)
verdant_druid.circle((-102, -47), 2, fill='seed', outline='leaf_dark', width=1)
verdant_druid.circle((105, 7), 3, fill='seed_light', outline='leaf_dark', width=1)
verdant_druid.circle((85, 44), 2, fill='flower', outline='leaf_dark', width=1)
verdant_druid.circle((-93, 61), 3, fill='flower', outline='leaf_dark', width=1)


storm_ranger = CodeSpriteFrame('Storm Ranger', storm, id='storm_ranger')
storm_ranger.ellipse((0, 8), (70, 88), fill='body', outline='detail', width=2)
storm_ranger.polygon([(-36, -10), (-8, -58), (18, -16)], fill='accent', outline='detail', width=2)
storm_ranger.line([(34, -32), (52, 28)], color='detail', width=5)
storm_ranger.line([(14, -10), (44, 8)], color='accent', width=3)
storm_ranger.circle((-12, -14), 6, fill='eye', outline='detail', width=1)
storm_ranger.circle((12, -14), 6, fill='eye', outline='detail', width=1)
storm_ranger.line([(-12, -14), (-12, -12)], color='detail', width=2)
storm_ranger.line([(12, -14), (12, -12)], color='detail', width=2)
storm_ranger.polyline([(-12, 2), (0, 8), (12, 2)], color='detail', width=2)

# The face is intentionally a separate component.  Keeping the face geometry
# together makes it easy to preserve two eyes, nose, mouth, ears, and skin tone
# even as the hood, hair, or cloak are redesigned around it.
def _draw_moon_mage_face(sprite: CodeSpriteFrame) -> None:
    sprite.polygon(
        [(-32, -193), (-12, -205), (14, -203), (33, -187), (35, -146),
         (24, -114), (0, -96), (-22, -110), (-36, -143)],
        fill='skin', outline='detail', width=3,
    )
    sprite.ellipse((-35, -155), (11, 28), fill='skin', outline='detail', width=2)
    sprite.ellipse((37, -155), (11, 28), fill='skin', outline='detail', width=2)

    # Brows and two fully separate eyes.
    sprite.line([(-25, -170), (-11, -174)], color='brow', width=3)
    sprite.line([(13, -174), (27, -170)], color='brow', width=3)
    sprite.ellipse((-18, -162), (18, 12), fill='eye_white', outline='detail', width=2)
    sprite.ellipse((20, -162), (18, 12), fill='eye_white', outline='detail', width=2)
    sprite.ellipse((-17, -162), (8, 9), fill='eye', outline='detail', width=1)
    sprite.ellipse((21, -162), (8, 9), fill='eye', outline='detail', width=1)
    sprite.ellipse((-16, -162), (3, 4), fill='pupil', outline='pupil', width=1)
    sprite.ellipse((22, -162), (3, 4), fill='pupil', outline='pupil', width=1)

    # Nose, mouth, and cheek highlights.
    sprite.line([(1, -162), (-2, -143), (4, -141)], color='nose', width=2)
    sprite.polyline([(-10, -128), (-1, -125), (9, -129)], color='lip', width=2)
    sprite.polyline([(-7, -123), (1, -121), (7, -124)], color='lip_shadow', width=1)
    sprite.line([(-26, -147), (-23, -140)], color='skin_hi', width=2)
    sprite.line([(24, -148), (22, -141)], color='skin_hi', width=2)


# Ported from the successful PIL concept: a grounded human battlemage with a
# readable face, hair, hands, legs, boots, hood, split cloak, and moon staff.
# Moon Mage is the SVG port of the original classroom PIL design.
# Keeping the art in one vector file makes it approachable for students who
# want to work visually rather than edit Python drawing coordinates.
moon_mage = SvgSpriteFrame(
    'Moon Mage',
    'assets/sprites/moon_mage.svg',
    id='moon_mage',
    scale=0.16,
    flash_color=(180, 232, 255),
)

crystal_guardian = CodeSpriteFrame('Crystal Guardian', crystal, id='crystal_guardian')
crystal_guardian.polygon([(-40, 10), (-14, -44), (14, -44), (40, 10), (20, 52), (-20, 52)], fill='body', outline='detail', width=2)
crystal_guardian.polygon([(-12, -52), (0, -74), (12, -52)], fill='accent', outline='detail', width=2)
crystal_guardian.polygon([(-54, 4), (-34, -20), (-26, 22)], fill='accent', outline='detail', width=2)
crystal_guardian.polygon([(54, 4), (34, -20), (26, 22)], fill='accent', outline='detail', width=2)
crystal_guardian.circle((-12, -10), 6, fill='eye', outline='detail', width=1)
crystal_guardian.circle((12, -10), 6, fill='eye', outline='detail', width=1)
crystal_guardian.line([(-12, -10), (-12, -8)], color='detail', width=2)
crystal_guardian.line([(12, -10), (12, -8)], color='detail', width=2)
crystal_guardian.polyline([(-12, 6), (0, 12), (12, 6)], color='detail', width=2)

mist_spirit = CodeSpriteFrame('Mist Spirit', mist_spirit_palette, id='mist_spirit', scale=0.46)

# Mist Spirit is an empty presence held together by drifting veils.  It has no
# ordinary face or torso: a cracked mask hangs inside a dark aperture while long
# vapor ribbons fold around it and trail into three independent tails.

# Distant vapor strokes establish a wide, drifting silhouette before the denser
# body layers are painted over them.
mist_spirit.polyline([(-104, 22), (-126, 0), (-111, -27), (-82, -43), (-63, -68)], color='fog_shadow', width=10)
mist_spirit.polyline([(-103, 21), (-124, 0), (-109, -26), (-81, -42), (-62, -67)], color='fog_mid', width=5)
mist_spirit.polyline([(77, -64), (104, -47), (119, -19), (111, 8), (132, 33)], color='fog_shadow', width=9)
mist_spirit.polyline([(77, -63), (102, -46), (117, -19), (109, 8), (130, 32)], color='accent', width=4)
mist_spirit.polyline([(-92, 55), (-117, 70), (-120, 91), (-100, 103)], color='fog_shadow', width=8)
mist_spirit.polyline([(88, 49), (114, 65), (122, 88), (108, 106)], color='fog_mid', width=7)

# Detached mist knots make the outer vapor feel discontinuous rather than like
# tentacles attached to a hidden round body.
mist_spirit.ellipse((-115, -47), (22, 12), fill='fog_mid', outline='fog_shadow', width=1)
mist_spirit.circle((-130, -57), 5, fill='fog_light', outline='fog_mid', width=1)
mist_spirit.ellipse((118, -47), (18, 10), fill='accent', outline='fog_shadow', width=1)
mist_spirit.circle((135, -38), 4, fill='glow', outline='fog_mid', width=1)
mist_spirit.ellipse((-126, 57), (18, 10), fill='body', outline='fog_shadow', width=1)
mist_spirit.circle((126, 59), 5, fill='fog_light', outline='fog_mid', width=1)

# Three forked tail masses form the lower silhouette.  They overlap instead of
# joining at one point, leaving narrow dark seams that keep the spirit airy.
mist_spirit.polygon([(-45, 24), (-15, 31), (-8, 77), (-36, 118), (-61, 104), (-50, 69)], fill='fog_shadow', outline='detail', width=2)
mist_spirit.polygon([(-14, 27), (17, 29), (30, 77), (9, 128), (-15, 109), (-5, 72)], fill='body', outline='detail', width=2)
mist_spirit.polygon([(15, 28), (45, 20), (62, 61), (53, 108), (27, 119), (31, 72)], fill='fog_mid', outline='detail', width=2)
mist_spirit.polygon([(-38, 38), (-21, 43), (-20, 86), (-37, 105), (-44, 91)], fill='body', outline='fog_shadow', width=1)
mist_spirit.polygon([(6, 39), (18, 42), (19, 83), (8, 111), (0, 89)], fill='fog_mid', outline='body', width=1)
mist_spirit.polygon([(31, 34), (43, 30), (52, 62), (46, 91), (34, 100)], fill='fog_light', outline='fog_mid', width=1)

# A broad asymmetric mantle of fog frames the face aperture.
mist_spirit.polygon([(-70, -7), (-54, -45), (-24, -68), (7, -65), (30, -48), (64, -34), (76, -3), (57, 26), (21, 38), (-21, 35), (-55, 22)], fill='fog_shadow', outline='detail', width=2)
mist_spirit.polygon([(-62, -7), (-46, -39), (-19, -56), (9, -53), (29, -39), (55, -27), (65, -4), (50, 18), (18, 28), (-18, 26), (-46, 17)], fill='body', outline='fog_shadow', width=2)
mist_spirit.polygon([(-53, -4), (-38, -31), (-16, -45), (6, -42), (22, -30), (46, -20), (54, -2), (42, 11), (14, 18), (-15, 17), (-38, 10)], fill='void', outline='detail', width=2)

# Broken halo strokes orbit the aperture without closing into a conventional
# magic circle.  Their unequal lengths reinforce the character's patient drift.
mist_spirit.polyline([(-72, -53), (-49, -76), (-18, -87), (12, -84)], color='accent', width=5)
mist_spirit.polyline([(-71, -52), (-48, -74), (-18, -85), (10, -82)], color='fog_light', width=2)
mist_spirit.polyline([(27, -81), (52, -69), (69, -49)], color='fog_mid', width=6)
mist_spirit.polyline([(29, -80), (52, -67), (67, -48)], color='accent', width=2)
mist_spirit.line([(-83, -37), (-73, -27)], color='glow', width=3)
mist_spirit.line([(78, -38), (86, -25)], color='spark', width=3)

# The porcelain mask is intentionally off-center and faceted.  Its lower edge
# ends before the mantle does, so it reads as an object suspended in the mist.
mist_spirit.polygon([(-23, -57), (5, -61), (27, -45), (31, -19), (18, 3), (-3, 14), (-24, 3), (-36, -20), (-34, -40)], fill='porcelain_shadow', outline='detail', width=2)
mist_spirit.polygon([(-20, -55), (4, -58), (23, -43), (26, -20), (14, 0), (-3, 9), (-20, 0), (-31, -20), (-29, -39)], fill='porcelain', outline='crack', width=2)

# A single diamond eye gives the spirit a fixed, unreadable gaze rather than the
# project's default friendly two-eye face.
mist_spirit.polygon([(-3, -37), (8, -28), (-2, -17), (-14, -27)], fill='glow', outline='detail', width=2)
mist_spirit.polygon([(-1, -32), (4, -28), (-1, -23), (-6, -27)], fill='eye', outline='glow', width=1)
mist_spirit.circle((2, -28), 2, fill='void', outline='void', width=1)

# Fine cracks make the mask feel old and brittle without turning them into a
# literal mouth or second eye.
mist_spirit.polyline([(10, -52), (5, -43), (11, -37), (8, -30)], color='crack', width=2)
mist_spirit.polyline([(-23, -13), (-14, -8), (-12, 0), (-4, 6)], color='crack', width=2)
mist_spirit.polyline([(20, -9), (13, -5), (12, 2)], color='porcelain_shadow', width=2)

# A luminous tear hangs below the mask and anchors the eye vertically.
mist_spirit.line([(-1, 9), (-1, 24)], color='glow', width=2)
mist_spirit.circle((-1, 29), 5, fill='glow', outline='detail', width=1)
mist_spirit.circle((-2, 27), 2, fill='eye', outline='eye', width=1)

# Calligraphic veil strokes cross in front of the lower body.  Parallel dark and
# light lines fake depth using only the classroom-friendly primitive API.
mist_spirit.polyline([(-73, 19), (-91, 36), (-79, 54), (-50, 60), (-26, 53)], color='detail', width=9)
mist_spirit.polyline([(-72, 18), (-89, 36), (-77, 52), (-49, 58), (-25, 51)], color='accent', width=5)
mist_spirit.polyline([(34, 45), (61, 37), (78, 48), (76, 67), (99, 77)], color='detail', width=8)
mist_spirit.polyline([(35, 43), (60, 36), (76, 48), (74, 65), (98, 75)], color='fog_light', width=4)
mist_spirit.polyline([(-39, 75), (-58, 83), (-69, 99)], color='fog_mid', width=6)
mist_spirit.polyline([(26, 86), (43, 95), (54, 111)], color='accent', width=5)

# Small floating shards/motes provide a visual rhythm around the broad ribbons.
mist_spirit.polygon([(-84, -70), (-76, -75), (-70, -67), (-78, -61)], fill='glow', outline='detail', width=1)
mist_spirit.polygon([(76, -74), (84, -68), (80, -58), (71, -64)], fill='fog_light', outline='detail', width=1)
mist_spirit.polygon([(-99, 0), (-92, -6), (-85, -1), (-91, 7)], fill='spark', outline='detail', width=1)
mist_spirit.polygon([(91, 13), (98, 7), (105, 13), (98, 20)], fill='glow', outline='detail', width=1)
mist_spirit.circle((-67, 79), 4, fill='fog_light', outline='fog_mid', width=1)
mist_spirit.circle((70, 89), 3, fill='glow', outline='fog_mid', width=1)
mist_spirit.circle((-101, 37), 3, fill='spark', outline='fog_shadow', width=1)
mist_spirit.circle((108, 43), 4, fill='accent', outline='fog_shadow', width=1)
mist_spirit.circle((-48, -83), 3, fill='glow', outline='fog_shadow', width=1)
mist_spirit.circle((50, -81), 2, fill='fog_light', outline='fog_shadow', width=1)

# Sparse internal strokes suggest slow circulation inside the veils.
mist_spirit.polyline([(-42, -1), (-30, 6), (-22, 15)], color='fog_mid', width=2)
mist_spirit.polyline([(31, 1), (23, 10), (17, 20)], color='accent', width=2)
mist_spirit.polyline([(-25, 55), (-13, 62), (-9, 74)], color='fog_light', width=2)
mist_spirit.polyline([(23, 55), (16, 65), (17, 76)], color='fog_shadow', width=2)

runesage = CodeSpriteFrame('Runesage', rune_sage, id='runesage', scale=0.52)

# Rune Sage is a floating geometer rather than a conventional robed person.
# The design is assembled from the same primitives students can use: polygons
# build the faceted robe and hood, doubled lines make the broken astrolabe halo,
# and tiny line motifs become readable, non-textual runes.

# Broken astrolabe / theorem halo.  Dark under-strokes keep the geometry
# readable against every battle background; the luminous inner strokes make it
# feel like suspended notation instead of a physical wheel.
_halo_segments = [
    [(-92, -38), (-76, -72), (-42, -96)],
    [(-30, -104), (0, -116), (30, -104)],
    [(42, -96), (76, -72), (92, -38)],
    [(96, -22), (102, 12), (88, 40)],
    [(72, 58), (44, 78), (22, 84)],
    [(-22, 84), (-44, 78), (-72, 58)],
    [(-88, 40), (-102, 12), (-96, -22)],
]
for segment in _halo_segments:
    runesage.line(segment, color='detail', width=9)
    runesage.line(segment, color='rune', width=3)

# Small calibration marks around the halo make the ring feel diagrammatic.
for p1, p2 in [
    ((-82, -57), (-70, -49)),
    ((-58, -86), (-52, -72)),
    ((0, -116), (0, -101)),
    ((58, -86), (52, -72)),
    ((82, -57), (70, -49)),
    ((98, 4), (84, 4)),
    ((60, 68), (52, 55)),
    ((-60, 68), (-52, 55)),
    ((-98, 4), (-84, 4)),
]:
    runesage.line([p1, p2], color='gold_light', width=3)

# Long floating robe: a dark outer silhouette, then offset slate facets so the
# figure reads as layered stone/cloth instead of one flat triangle.
runesage.polygon(
    [(-46, 8), (-66, 70), (-45, 102), (-18, 116), (0, 98), (18, 116), (45, 102), (66, 70), (46, 8)],
    fill='robe_shadow', outline='detail', width=3,
)
runesage.polygon(
    [(-34, 10), (-44, 68), (-18, 94), (0, 82), (18, 94), (44, 68), (34, 10)],
    fill='body', outline='detail', width=2,
)
runesage.polygon(
    [(-12, 18), (-16, 76), (0, 88), (16, 76), (12, 18)],
    fill='robe_light', outline='detail', width=2,
)
# Split lower hems create a memorable forked silhouette.
runesage.polygon([(-43, 70), (-58, 104), (-30, 95), (-15, 72)], fill='stone', outline='detail', width=2)
runesage.polygon([(43, 70), (58, 104), (30, 95), (15, 72)], fill='stone', outline='detail', width=2)

# Broad mantle gives the otherwise narrow figure a strong shoulder line.
runesage.polygon(
    [(-72, -4), (-48, -37), (-25, -29), (0, -43), (25, -29), (48, -37), (72, -4), (49, 20), (0, 12), (-49, 20)],
    fill='stone', outline='detail', width=3,
)
runesage.polygon(
    [(-62, -7), (-45, -27), (-20, -20), (0, -31), (20, -20), (45, -27), (62, -7), (43, 8), (0, 2), (-43, 8)],
    fill='stone_light', outline='body', width=2,
)
# Gold mantle edge.
runesage.line([(-65, -2), (-46, 15), (0, 7), (46, 15), (65, -2)], color='accent', width=5)
runesage.line([(-65, -2), (-46, 15), (0, 7), (46, 15), (65, -2)], color='gold_light', width=2)

# Faceted hood and deep face aperture.  The single diamond eye makes the face
# icon-like rather than conventionally human.
runesage.polygon(
    [(-37, -58), (-23, -88), (0, -105), (23, -88), (37, -58), (29, -25), (0, -12), (-29, -25)],
    fill='body', outline='detail', width=3,
)
runesage.polygon(
    [(-25, -58), (-13, -78), (0, -87), (13, -78), (25, -58), (18, -35), (0, -25), (-18, -35)],
    fill='void', outline='detail', width=2,
)
# Eye aura, iris diamond, and tiny pupil.
runesage.circle((0, -56), 15, fill='rune', outline='detail', width=2)
runesage.circle((0, -56), 10, fill='void', outline='rune_light', width=2)
runesage.polygon([(0, -68), (9, -56), (0, -44), (-9, -56)], fill='rune_light', outline='gold_light', width=2)
runesage.polygon([(0, -63), (4, -56), (0, -49), (-4, -56)], fill='detail', outline='detail', width=1)
# Brow/hood seams point toward the eye.
runesage.line([(-27, -66), (-12, -60)], color='stone_light', width=3)
runesage.line([(27, -66), (12, -60)], color='stone_light', width=3)
runesage.line([(0, -87), (0, -72)], color='accent', width=3)

# Central theorem glyph on the robe: a spine with mirrored branches and a
# floating diamond.  It is intentionally symbolic, not alphabetic text.
runesage.line([(0, 18), (0, 68)], color='rune', width=4)
runesage.line([(0, 30), (-16, 42), (-26, 34)], color='rune_light', width=3)
runesage.line([(0, 30), (16, 42), (26, 34)], color='rune_light', width=3)
runesage.line([(0, 50), (-12, 60)], color='accent', width=3)
runesage.line([(0, 50), (12, 60)], color='accent', width=3)
runesage.polygon([(0, 67), (7, 75), (0, 83), (-7, 75)], fill='gold_light', outline='detail', width=2)

# Left orbiting tablet: angular slate with a sampled-wave glyph.
runesage.polygon(
    [(-96, -8), (-82, -25), (-61, -20), (-57, 6), (-74, 21), (-96, 12)],
    fill='robe_shadow', outline='detail', width=3,
)
runesage.polygon(
    [(-89, -7), (-79, -17), (-67, -14), (-65, 3), (-75, 12), (-88, 7)],
    fill='stone_light', outline='accent', width=2,
)
runesage.polyline([(-84, 0), (-79, -7), (-74, 4), (-69, -5)], color='rune', width=3)
# Three detached chips imply that the tablets are levitating fragments.
runesage.polygon([(-107, -16), (-101, -22), (-95, -17), (-101, -10)], fill='accent', outline='detail', width=1)
runesage.polygon([(-105, 22), (-98, 17), (-92, 23), (-99, 29)], fill='rune', outline='detail', width=1)

# Right orbiting instrument: a ring/diamond construction with a square-wave
# glyph.  It deliberately differs from the left side to avoid mirror symmetry.
runesage.circle((84, 4), 24, fill='accent', outline='detail', width=3)
runesage.circle((84, 4), 17, fill='void', outline='gold_light', width=2)
runesage.polygon([(84, -12), (100, 4), (84, 20), (68, 4)], fill='body', outline='rune', width=2)
runesage.polyline([(74, 6), (78, 6), (78, -2), (86, -2), (86, 7), (94, 7)], color='rune_light', width=3)
runesage.circle((104, 30), 4, fill='rune_light', outline='detail', width=1)
runesage.circle((112, 20), 3, fill='accent', outline='detail', width=1)

# Two small geometric "hands" hover under the mantle.  Their orientation makes
# the pose feel composed and intentional without literal arms.
runesage.polygon([(-55, 31), (-43, 20), (-31, 31), (-43, 44)], fill='accent', outline='detail', width=2)
runesage.polygon([(-43, 25), (-37, 31), (-43, 38), (-49, 31)], fill='rune_light', outline='detail', width=1)
runesage.line([(-43, 44), (-47, 54)], color='rune', width=3)
runesage.polygon([(53, 26), (65, 36), (55, 49), (42, 38)], fill='stone_light', outline='detail', width=2)
runesage.polygon([(51, 33), (58, 37), (53, 43), (47, 39)], fill='gold_light', outline='detail', width=1)

# Sparse floating notation around the lower robe gives depth without turning
# the character into visual noise.
for center, radius, fill in [
    ((-76, 57), 4, 'rune'),
    ((74, 66), 5, 'accent'),
    ((-68, 82), 3, 'gold_light'),
    ((71, 90), 3, 'rune_light'),
]:
    runesage.circle(center, radius, fill=fill, outline='detail', width=1)
runesage.polygon([(-89, 73), (-82, 66), (-75, 73), (-82, 80)], fill='body', outline='rune', width=2)
runesage.polygon([(79, 48), (86, 42), (93, 49), (86, 56)], fill='robe_shadow', outline='accent', width=2)

# A final narrow gold line pulls the eye down the silhouette and ties the hood,
# mantle, and robe together.
runesage.line([(0, -25), (0, 7)], color='gold_light', width=2)
runesage.line([(-25, 95), (0, 82), (25, 95)], color='accent', width=3)

ai_slop = CodeSpriteFrame('Ai Slop', slop, id='ai_slop')
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
# It intentionally uses only the same readable CodeSpriteFrame primitives students use:
# overlapping ellipses for volume, polygons for panels/shards, circles for eyes,
# and doubled lines for the angular glitch limbs.
ai_slop_prime = CodeSpriteFrame('Ai Slop Prime', slop_prime, id='ai_slop_prime')

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

null_hydra = CodeSpriteFrame('Null Hydra', rune, id='null_hydra')
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

star_corsair = CodeSpriteFrame('Star Corsair', corsair, id='star_corsair')
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

# Velvet Hexer is a courtly silhouette: high collar, fitted bodice, layered
# velvet skirts, and moth-ritual ornaments instead of a faceless cape mass.
velvet_hexer = CodeSpriteFrame('Velvet Hexer', velvet, id='velvet_hexer', scale=0.48)

# Back train and outer skirts.
velvet_hexer.polygon([(-19, -8), (-56, 12), (-76, 52), (-64, 93), (-20, 108), (-9, 70)], fill='velvet_dark', outline='detail', width=3)
velvet_hexer.polygon([(19, -8), (55, 12), (77, 51), (64, 95), (19, 108), (8, 70)], fill='velvet_dark', outline='detail', width=3)
velvet_hexer.polygon([(-16, 4), (-43, 21), (-54, 51), (-47, 82), (-18, 91), (-8, 63)], fill='lining', outline='detail', width=2)
velvet_hexer.polygon([(16, 4), (44, 21), (55, 51), (48, 83), (18, 92), (8, 63)], fill='accent', outline='detail', width=2)

# Dress, waist, and bodice.
velvet_hexer.polygon([(-15, -27), (-29, -8), (-35, 42), (-28, 93), (-6, 114), (13, 114), (33, 94), (36, 44), (29, -8), (15, -27)], fill='body', outline='detail', width=4)
velvet_hexer.polygon([(-9, -17), (-14, 26), (-11, 87), (0, 107), (10, 88), (13, 24), (9, -17)], fill='velvet_light', outline='detail', width=2)
velvet_hexer.polygon([(-20, -5), (-5, 6), (7, 6), (20, -5), (12, -20), (-11, -20)], fill='lining', outline='detail', width=2)
velvet_hexer.line([(-4, 6), (6, 16), (-4, 27), (6, 38), (-4, 49)], color='hex', width=2)

# Sleeves and gloved hands.
velvet_hexer.polygon([(-22, -16), (-47, -1), (-42, 25), (-14, 11)], fill='velvet_light', outline='detail', width=2)
velvet_hexer.polygon([(22, -16), (47, -1), (43, 25), (14, 11)], fill='lining', outline='detail', width=2)
velvet_hexer.line([(-41, 18), (-56, 39)], color='thorn', width=4)
velvet_hexer.circle((-59, 43), 5, fill='mask', outline='detail', width=1)
velvet_hexer.line([(42, 18), (58, 39)], color='thorn', width=4)
velvet_hexer.circle((61, 43), 5, fill='mask', outline='detail', width=1)

# Face, hair, and collar.
velvet_hexer.polygon([(-34, -35), (-22, -62), (0, -74), (23, -63), (35, -34), (24, -12), (0, -6), (-22, -12)], fill='void', outline='detail', width=3)
velvet_hexer.ellipse((0, -40), (18, 22), fill='mask', outline='detail', width=2)
velvet_hexer.polygon([(-24, -45), (-17, -65), (-4, -77), (9, -75), (18, -66), (24, -47), (18, -24), (3, -18), (-13, -22)], fill='velvet_dark', outline='detail', width=2)
velvet_hexer.line([(-6, -42), (-1, -44)], color='detail', width=2)
velvet_hexer.line([(4, -44), (10, -42)], color='detail', width=2)
velvet_hexer.polyline([(-4, -28), (0, -25), (5, -28)], color='hex', width=2)
velvet_hexer.polygon([(-29, -53), (-48, -43), (-37, -22), (-19, -27)], fill='body', outline='detail', width=2)
velvet_hexer.polygon([(28, -53), (49, -43), (38, -21), (18, -26)], fill='body', outline='detail', width=2)

# Thorn circlet.
velvet_hexer.polyline([(-13, -71), (-3, -86), (8, -78), (18, -91)], color='thorn', width=4)
velvet_hexer.line([(-2, -86), (-9, -97)], color='thorn_light', width=2)
velvet_hexer.line([(8, -79), (18, -76)], color='thorn_light', width=2)
velvet_hexer.circle((18, -91), 3, fill='hex', outline='detail', width=1)

# Ritual moth panes and hanging seals.
velvet_hexer.ellipse((-77, 7), (20, 28), fill='accent', outline='detail', width=2)
velvet_hexer.ellipse((-77, 7), (10, 15), fill='void', outline='hex', width=2)
velvet_hexer.circle((-77, 5), 3, fill='eye', outline='detail', width=1)
velvet_hexer.ellipse((77, 7), (20, 28), fill='lining', outline='detail', width=2)
velvet_hexer.ellipse((77, 7), (10, 15), fill='void', outline='hex', width=2)
velvet_hexer.circle((77, 5), 3, fill='eye', outline='detail', width=1)
velvet_hexer.line([(-66, 55), (-66, 85)], color='thorn_light', width=2)
velvet_hexer.polygon([(-76, 92), (-66, 78), (-56, 92), (-66, 106)], fill='hex', outline='detail', width=2)
velvet_hexer.line([(66, 56), (66, 84)], color='thorn_light', width=2)
velvet_hexer.polygon([(56, 91), (66, 77), (76, 91), (66, 106)], fill='moon', outline='detail', width=2)
velvet_hexer.circle((-35, 70), 4, fill='thorn_light', outline='detail', width=1)
velvet_hexer.circle((34, 73), 4, fill='thorn', outline='detail', width=1)


siren_engine = CodeSpriteFrame('Siren Engine', siren, id='siren_engine')
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

# Space Pirate intentionally uses an SVG instead of Python drawing primitives.
# This gives art-focused students a second authoring path: edit the vector file
# directly in a text editor or a tool such as Inkscape, then rerun the same
# character preview command used for procedural sprites.
space_pirate = SvgSpriteFrame(
    'Space Pirate',
    'assets/sprites/space_pirate.svg',
    id='space_pirate',
    scale=0.16,
    flash_color=(84, 225, 255),
)

# Tiny Ancient Menace is now a compact scarab-idol: half relic, half scuttling
# machine, with a tiny body trying very hard to project monumental authority.
tiny_ancient_menace = CodeSpriteFrame('Tiny Ancient Menace', menace, id='tiny_ancient_menace', scale=0.52)

# Crown-shrine shell.
tiny_ancient_menace.polygon([(-34, -38), (-11, -76), (17, -76), (38, -38), (46, -4), (40, 46), (16, 71), (-16, 71), (-39, 48), (-47, -6)], fill='stone_dark', outline='detail', width=4)
tiny_ancient_menace.polygon([(-26, -33), (-9, -63), (13, -63), (28, -34), (34, -5), (31, 39), (12, 59), (-12, 59), (-31, 40), (-36, -6)], fill='body', outline='detail', width=3)
tiny_ancient_menace.polygon([(-18, -60), (-7, -91), (7, -91), (18, -60)], fill='accent', outline='detail', width=3)
tiny_ancient_menace.polygon([(-7, -72), (0, -86), (8, -72), (0, -58)], fill='glyph', outline='stone_dark', width=2)

# Face niche and central eye.
tiny_ancient_menace.polygon([(-20, -17), (0, -31), (21, -17), (18, 12), (0, 27), (-18, 12)], fill='void', outline='detail', width=3)
tiny_ancient_menace.ellipse((0, -11), (18, 12), fill='eye', outline='patina', width=2)
tiny_ancient_menace.circle((0, -11), 5, fill='ember', outline='detail', width=1)
tiny_ancient_menace.line([(-12, 18), (-4, 24), (9, 19)], color='detail', width=2)

# Carved chest plates and glyphs.
tiny_ancient_menace.polygon([(-22, 31), (-3, 24), (0, 41), (-17, 48)], fill='stone_mid', outline='detail', width=2)
tiny_ancient_menace.polygon([(4, 24), (23, 31), (18, 48), (0, 41)], fill='stone_light', outline='detail', width=2)
tiny_ancient_menace.line([(-13, 34), (-6, 34), (-6, 43), (2, 43), (2, 51)], color='patina_light', width=3)
tiny_ancient_menace.line([(13, 34), (7, 40), (14, 48)], color='glyph', width=2)

# Scuttling scarab legs.
for leg in [
    [(-27, 4), (-48, 0), (-60, 12), (-51, 30)],
    [(-30, 23), (-53, 24), (-64, 42), (-51, 55)],
    [(-25, 44), (-46, 55), (-48, 74), (-31, 81)],
    [(27, 4), (48, 0), (60, 13), (51, 31)],
    [(31, 22), (53, 25), (64, 43), (52, 55)],
    [(25, 44), (46, 56), (48, 74), (31, 81)],
]:
    tiny_ancient_menace.polyline(leg, color='stone_dark', width=5)
for foot in [(-51, 30), (-51, 55), (-31, 81), (51, 31), (52, 55), (31, 81)]:
    tiny_ancient_menace.circle(foot, 4, fill='accent', outline='detail', width=1)

# Floating tablets and chips.
tiny_ancient_menace.rect((-70, -24), (14, 16), fill='stone_mid', outline='detail', width=2, border_radius=1)
tiny_ancient_menace.rect((70, -30), (12, 14), fill='patina', outline='detail', width=2, border_radius=1)
tiny_ancient_menace.rect((-79, 13), (9, 9), fill='glyph', outline='detail', width=1, border_radius=1)
tiny_ancient_menace.circle((62, -58), 4, fill='patina_light', outline='detail', width=1)
tiny_ancient_menace.polygon([(-34, -3), (-26, -15), (-18, 1), (-29, 13)], fill='patina', outline='detail', width=1)
tiny_ancient_menace.polygon([(18, 46), (31, 37), (28, 58), (17, 63)], fill='patina', outline='detail', width=1)
tiny_ancient_menace.ellipse((0, 91), (86, 10), fill='void', outline='void', width=1)


# Cryptid Friend is a plush midnight creature with enormous ears, a lantern belly,
# and long arms that make her read as odd but gentle instead of ominous.
cryptid_friend = CodeSpriteFrame('Cryptid Friend', cryptid, id='cryptid_friend', scale=0.47)

# Oversized ear-fins define the silhouette.
cryptid_friend.polygon([(-24, -39), (-71, -103), (-108, -86), (-95, -35), (-50, -6)], fill='accent', outline='detail', width=4)
cryptid_friend.polygon([(-39, -37), (-73, -86), (-91, -78), (-78, -39), (-48, -14)], fill='mist', outline='detail', width=2)
cryptid_friend.polygon([(23, -39), (71, -104), (109, -85), (95, -34), (49, -6)], fill='accent', outline='detail', width=4)
cryptid_friend.polygon([(38, -37), (73, -86), (91, -77), (77, -39), (48, -14)], fill='mist_light', outline='detail', width=2)

# Round fluffy body.
cryptid_friend.polygon([(-50, -17), (-62, 21), (-53, 66), (-24, 108), (0, 95), (24, 108), (52, 66), (61, 21), (50, -17), (18, -42), (-17, -42)], fill='fur_shadow', outline='detail', width=4)
cryptid_friend.polygon([(-38, -10), (-47, 23), (-40, 58), (-18, 88), (-1, 78), (17, 89), (39, 58), (46, 23), (38, -10), (14, -29), (-13, -29)], fill='body', outline='detail', width=3)
cryptid_friend.polygon([(-33, 32), (-15, 23), (-3, 34), (12, 24), (31, 35), (34, 60), (16, 76), (0, 66), (-18, 76), (-34, 60)], fill='fur_light', outline='detail', width=2)

# Shadow face with three warm eyes.
cryptid_friend.ellipse((0, -26), (44, 35), fill='night', outline='detail', width=3)
cryptid_friend.circle((-15, -29), 6, fill='eye', outline='detail', width=1)
cryptid_friend.circle((2, -34), 9, fill='lantern_light', outline='detail', width=1)
cryptid_friend.circle((19, -27), 5, fill='eye', outline='detail', width=1)
cryptid_friend.circle((-13, -28), 2, fill='detail', outline='detail', width=1)
cryptid_friend.circle((4, -33), 3, fill='detail', outline='detail', width=1)
cryptid_friend.circle((20, -26), 2, fill='detail', outline='detail', width=1)
cryptid_friend.polyline([(-9, -12), (-1, -8), (10, -12)], color='mist', width=2)

# Long arms and soft paws.
cryptid_friend.line([(-40, 2), (-77, 34), (-84, 78)], color='fur_shadow', width=12)
cryptid_friend.line([(-76, 34), (-93, 58)], color='body', width=5)
cryptid_friend.ellipse((-85, 86), (22, 18), fill='accent', outline='detail', width=2)
cryptid_friend.line([(40, 3), (76, 34), (84, 78)], color='fur_shadow', width=12)
cryptid_friend.line([(76, 34), (94, 58)], color='body', width=5)
cryptid_friend.ellipse((86, 86), (22, 18), fill='accent', outline='detail', width=2)

# Lantern belly.
cryptid_friend.polygon([(-18, 9), (0, -3), (19, 10), (16, 37), (0, 51), (-16, 36)], fill='lantern', outline='detail', width=3)
cryptid_friend.polygon([(-9, 13), (0, 7), (10, 13), (9, 30), (0, 39), (-9, 29)], fill='lantern_light', outline='lantern', width=1)
cryptid_friend.circle((0, 21), 4, fill='eye', outline='lantern', width=1)

# Small feet and a looped tail with glowing tuft.
cryptid_friend.polygon([(-27, 93), (-6, 86), (-2, 103), (-25, 108)], fill='fur_shadow', outline='detail', width=2)
cryptid_friend.polygon([(6, 86), (27, 93), (25, 108), (2, 103)], fill='fur_shadow', outline='detail', width=2)
cryptid_friend.polyline([(42, 55), (74, 64), (93, 86), (72, 99), (47, 91)], color='accent', width=7)
cryptid_friend.polyline([(43, 57), (72, 66), (88, 84), (70, 94), (49, 88)], color='mist', width=3)
cryptid_friend.circle((93, 86), 7, fill='lantern', outline='detail', width=2)
cryptid_friend.circle((92, 84), 3, fill='lantern_light', outline='lantern', width=1)

# Speckles and little night motes.
cryptid_friend.circle((-32, 54), 4, fill='moss', outline='detail', width=1)
cryptid_friend.circle((35, 57), 4, fill='moss', outline='detail', width=1)
cryptid_friend.circle((-69, 104), 3, fill='mist', outline='detail', width=1)
cryptid_friend.circle((68, 103), 3, fill='mist_light', outline='detail', width=1)
cryptid_friend.circle((-95, -8), 4, fill='mist', outline='detail', width=1)
cryptid_friend.circle((98, -11), 4, fill='mist_light', outline='detail', width=1)


ART_ASSETS = [
    knight_dawn_art,
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

# Compatibility names used by older exercises.
SPRITE_ASSETS = ART_ASSETS
SPRITES = ART_ASSETS
