from __future__ import annotations

"""Procedural battler sprite catalog.

Each sprite recipe starts with an empty dictionary. Students can add a palette,
append a few shapes, run the renderer, then keep iterating.
"""

from rpg_battle.content.presets import circle, ellipse, line, polygon, polyline, rect, simple_face

SPRITES: dict[str, dict[str, object]] = {}

knight_dawn: dict[str, object] = {}
knight_dawn["palette"] = "dawn"
knight_dawn["shapes"] = []
knight_dawn["shapes"].append(polygon([(-28, 14), (0, -52), (28, 14)], fill="accent"))
knight_dawn["shapes"].append(rect((0, 14), (68, 78), fill="body"))
knight_dawn["shapes"].append(rect((0, -8), (46, 52), fill="accent"))
knight_dawn["shapes"].append(rect((-40, 10), (24, 48), fill="accent"))
knight_dawn["shapes"].append(line([(-40, -12), (-40, 34)], color="detail", width=4))
knight_dawn["shapes"].extend(simple_face(-14))
SPRITES["knight_dawn"] = knight_dawn

verdant_druid: dict[str, object] = {}
verdant_druid["palette"] = "verdant"
verdant_druid["shapes"] = []
verdant_druid["shapes"].append(ellipse((0, 12), (76, 90), fill="body"))
verdant_druid["shapes"].append(polygon([(-26, -36), (-6, -56), (0, -28)], fill="accent"))
verdant_druid["shapes"].append(polygon([(26, -36), (6, -56), (0, -28)], fill="accent"))
verdant_druid["shapes"].append(line([(-20, 20), (0, 42), (20, 20)], color="detail", width=3))
verdant_druid["shapes"].append(
    polyline([(-38, -4), (-56, -28), (-52, 26)], color="detail", width=4)
)
verdant_druid["shapes"].extend(simple_face(-10))
SPRITES["verdant_druid"] = verdant_druid

storm_ranger: dict[str, object] = {}
storm_ranger["palette"] = "storm"
storm_ranger["shapes"] = []
storm_ranger["shapes"].append(ellipse((0, 8), (70, 88), fill="body"))
storm_ranger["shapes"].append(polygon([(-36, -10), (-8, -58), (18, -16)], fill="accent"))
storm_ranger["shapes"].append(line([(34, -32), (52, 28)], color="detail", width=5))
storm_ranger["shapes"].append(line([(14, -10), (44, 8)], color="accent", width=3))
storm_ranger["shapes"].extend(simple_face(-14))
SPRITES["storm_ranger"] = storm_ranger

moon_mage: dict[str, object] = {}
moon_mage["palette"] = "moon"
moon_mage["shapes"] = []
moon_mage["shapes"].append(ellipse((0, 12), (74, 92), fill="body"))
moon_mage["shapes"].append(circle((0, -46), 20, fill="accent"))
moon_mage["shapes"].append(polyline([(-20, -28), (0, -42), (20, -28)], color="detail", width=3))
moon_mage["shapes"].append(circle((28, -32), 8, fill="accent"))
moon_mage["shapes"].append(circle((-30, 32), 10, fill="accent"))
moon_mage["shapes"].extend(simple_face(-8))
SPRITES["moon_mage"] = moon_mage

crystal_guardian: dict[str, object] = {}
crystal_guardian["palette"] = "crystal"
crystal_guardian["shapes"] = []
crystal_guardian["shapes"].append(
    polygon([(-40, 10), (-14, -44), (14, -44), (40, 10), (20, 52), (-20, 52)], fill="body")
)
crystal_guardian["shapes"].append(polygon([(-12, -52), (0, -74), (12, -52)], fill="accent"))
crystal_guardian["shapes"].append(polygon([(-54, 4), (-34, -20), (-26, 22)], fill="accent"))
crystal_guardian["shapes"].append(polygon([(54, 4), (34, -20), (26, 22)], fill="accent"))
crystal_guardian["shapes"].extend(simple_face(-10))
SPRITES["crystal_guardian"] = crystal_guardian

mist_spirit: dict[str, object] = {}
mist_spirit["palette"] = "mist"
mist_spirit["shapes"] = []
mist_spirit["shapes"].append(ellipse((0, 8), (78, 88), fill="body"))
mist_spirit["shapes"].append(ellipse((0, 26), (56, 40), fill="accent"))
mist_spirit["shapes"].append(
    polyline([(-30, 20), (-10, 44), (8, 20), (28, 44)], color="detail", width=3)
)
mist_spirit["shapes"].append(circle((-28, -30), 7, fill="accent"))
mist_spirit["shapes"].append(circle((28, -36), 9, fill="accent"))
mist_spirit["shapes"].extend(simple_face(-16))
SPRITES["mist_spirit"] = mist_spirit

runesage: dict[str, object] = {}
runesage["palette"] = "rune"
runesage["shapes"] = []
runesage["shapes"].append(circle((0, 10), 40, fill="body"))
runesage["shapes"].append(circle((0, 10), 28, fill="accent"))
runesage["shapes"].append(
    polyline([(-42, -30), (-18, -50), (0, -30), (18, -50), (42, -30)], color="accent", width=3)
)
runesage["shapes"].append(line([(-52, 16), (52, 16)], color="detail", width=3))
runesage["shapes"].append(
    polyline([(-30, 28), (-14, 14), (0, 28), (14, 14), (30, 28)], color="accent", width=3)
)
runesage["shapes"].extend(simple_face(-8))
SPRITES["runesage"] = runesage

ai_slop: dict[str, object] = {}
ai_slop["palette"] = "slop"
ai_slop["shapes"] = []
ai_slop["shapes"].append(ellipse((0, 8), (82, 88), fill="body"))
ai_slop["shapes"].append(polygon([(-18, -52), (18, -46), (32, -10), (-26, -18)], fill="accent"))
ai_slop["shapes"].append(rect((-48, 12), (16, 42), fill="accent", border_radius=5))
ai_slop["shapes"].append(rect((46, -6), (18, 52), fill="accent", border_radius=5))
ai_slop["shapes"].append(line([(-46, 8), (-78, -4), (-64, 30), (-88, 36)], color="detail", width=4))
ai_slop["shapes"].append(line([(46, -2), (82, -26), (68, 12), (98, 6)], color="detail", width=4))
ai_slop["shapes"].append(polygon([(-8, 26), (10, 18), (26, 34), (-2, 42)], fill="accent"))
ai_slop["shapes"].append(circle((-26, -8), 5, fill="eye", outline="detail", width=1))
ai_slop["shapes"].append(circle((16, -2), 7, fill="eye", outline="detail", width=1))
ai_slop["shapes"].append(line([(-30, 22), (-2, 32), (18, 18), (30, 34)], color="detail", width=3))
ai_slop["shapes"].append(rect((-12, -34), (10, 10), fill="accent", border_radius=2))
ai_slop["shapes"].append(rect((32, 24), (12, 12), fill="accent", border_radius=2))
SPRITES["ai_slop"] = ai_slop

ai_slop_prime: dict[str, object] = {}
ai_slop_prime["palette"] = "slop"
ai_slop_prime["shapes"] = []
ai_slop_prime["shapes"].append(ellipse((0, 0), (112, 104), fill="body"))
ai_slop_prime["shapes"].append(
    polygon([(-34, -66), (22, -60), (48, -18), (-42, -24)], fill="accent")
)
ai_slop_prime["shapes"].append(rect((-62, 10), (20, 54), fill="accent", border_radius=4))
ai_slop_prime["shapes"].append(rect((58, -8), (22, 62), fill="accent", border_radius=4))
ai_slop_prime["shapes"].append(
    line([(-60, 8), (-104, -10), (-84, 34), (-116, 44)], color="detail", width=4)
)
ai_slop_prime["shapes"].append(
    line([(58, -4), (104, -30), (84, 14), (122, 8)], color="detail", width=4)
)
ai_slop_prime["shapes"].append(circle((-30, -12), 7, fill="eye", outline="detail", width=1))
ai_slop_prime["shapes"].append(circle((10, -6), 8, fill="eye", outline="detail", width=1))
ai_slop_prime["shapes"].append(circle((38, 10), 6, fill="eye", outline="detail", width=1))
ai_slop_prime["shapes"].append(
    line([(-36, 30), (-6, 42), (18, 26), (36, 44)], color="detail", width=4)
)
ai_slop_prime["shapes"].append(rect((-16, -40), (12, 12), fill="accent", border_radius=2))
ai_slop_prime["shapes"].append(rect((36, 28), (14, 14), fill="accent", border_radius=2))
SPRITES["ai_slop_prime"] = ai_slop_prime

null_hydra: dict[str, object] = {}
null_hydra["palette"] = "rune"
null_hydra["shapes"] = []
null_hydra["shapes"].append(ellipse((0, 8), (108, 96), fill="body"))
null_hydra["shapes"].append(polygon([(-58, -8), (-30, -54), (-8, -6)], fill="accent"))
null_hydra["shapes"].append(polygon([(0, -18), (18, -70), (32, -10)], fill="accent"))
null_hydra["shapes"].append(polygon([(50, -4), (72, -50), (88, 6)], fill="accent"))
null_hydra["shapes"].append(line([(-48, 14), (-82, 44), (-66, 72)], color="detail", width=4))
null_hydra["shapes"].append(line([(0, 20), (-10, 64), (12, 90)], color="detail", width=4))
null_hydra["shapes"].append(line([(52, 18), (92, 54), (72, 84)], color="detail", width=4))
null_hydra["shapes"].append(circle((-28, -18), 6, fill="eye", outline="detail", width=1))
null_hydra["shapes"].append(circle((18, -26), 7, fill="eye", outline="detail", width=1))
null_hydra["shapes"].append(circle((58, -12), 6, fill="eye", outline="detail", width=1))
null_hydra["shapes"].append(
    polyline([(-34, 30), (-12, 40), (8, 24), (28, 42), (48, 28)], color="detail", width=3)
)
null_hydra["shapes"].append(circle((-60, 36), 8, fill="accent"))
null_hydra["shapes"].append(circle((62, 42), 10, fill="accent"))
SPRITES["null_hydra"] = null_hydra


star_corsair: dict[str, object] = {}
star_corsair["palette"] = "corsair"
star_corsair["shapes"] = []
star_corsair["shapes"].append(ellipse((0, 10), (78, 88), fill="body"))
star_corsair["shapes"].append(
    polyline([(-52, -34), (-14, -54), (24, -48), (52, -30)], color="accent", width=5)
)
star_corsair["shapes"].append(polygon([(-8, -60), (0, -82), (12, -56)], fill="accent"))
star_corsair["shapes"].append(line([(28, -8), (64, 8)], color="accent", width=4))
star_corsair["shapes"].append(line([(-22, 36), (12, 46), (34, 28)], color="detail", width=3))
star_corsair["shapes"].append(rect((-34, 18), (18, 42), fill="accent", border_radius=4))
star_corsair["shapes"].extend(simple_face(-14))
SPRITES["star_corsair"] = star_corsair

velvet_hexer: dict[str, object] = {}
velvet_hexer["palette"] = "velvet"
velvet_hexer["shapes"] = []
velvet_hexer["shapes"].append(ellipse((0, 12), (70, 96), fill="body"))
velvet_hexer["shapes"].append(polyline([(-24, -50), (0, -68), (24, -50)], color="accent", width=4))
velvet_hexer["shapes"].append(
    polyline([(-40, -6), (-22, 46), (0, 28), (22, 50), (40, -6)], color="accent", width=3)
)
velvet_hexer["shapes"].append(circle((-36, -18), 6, fill="accent"))
velvet_hexer["shapes"].append(circle((36, -4), 6, fill="accent"))
velvet_hexer["shapes"].append(
    polyline([(-20, 24), (-4, 8), (12, 24), (28, 8)], color="detail", width=3)
)
velvet_hexer["shapes"].extend(simple_face(-16))
SPRITES["velvet_hexer"] = velvet_hexer

siren_engine: dict[str, object] = {}
siren_engine["palette"] = "siren"
siren_engine["shapes"] = []
siren_engine["shapes"].append(ellipse((0, 6), (74, 94), fill="body"))
siren_engine["shapes"].append(circle((0, -40), 20, fill="accent"))
siren_engine["shapes"].append(
    polyline([(-34, -22), (-20, -48), (-8, -22)], color="detail", width=3)
)
siren_engine["shapes"].append(polyline([(34, -22), (20, -48), (8, -22)], color="detail", width=3))
siren_engine["shapes"].append(circle((-34, 6), 8, fill="accent"))
siren_engine["shapes"].append(circle((34, 6), 8, fill="accent"))
siren_engine["shapes"].append(polyline([(-18, 44), (0, 64), (18, 44)], color="accent", width=4))
siren_engine["shapes"].append(line([(-10, -18), (-10, 38)], color="detail", width=2))
siren_engine["shapes"].append(line([(10, -18), (10, 38)], color="detail", width=2))
siren_engine["shapes"].extend(simple_face(-12))
SPRITES["siren_engine"] = siren_engine

space_pirate: dict[str, object] = {}
space_pirate["palette"] = "raider"
space_pirate["shapes"] = []
space_pirate["shapes"].append(ellipse((0, 10), (80, 92), fill="body"))
space_pirate["shapes"].append(polygon([(-40, -24), (-10, -60), (20, -18)], fill="accent"))
space_pirate["shapes"].append(line([(-34, 34), (-10, 54), (18, 24)], color="detail", width=3))
space_pirate["shapes"].append(rect((34, 12), (20, 52), fill="accent", border_radius=3))
space_pirate["shapes"].append(circle((16, -16), 8, fill="accent"))
space_pirate["shapes"].append(line([(44, -10), (58, 28), (74, 18)], color="detail", width=3))
space_pirate["shapes"].append(line([(-28, -8), (-50, 6), (-40, 42)], color="accent", width=3))
space_pirate["shapes"].extend(simple_face(-14))
SPRITES["space_pirate"] = space_pirate

tiny_ancient_menace: dict[str, object] = {}
tiny_ancient_menace["palette"] = "menace"
tiny_ancient_menace["shapes"] = []
tiny_ancient_menace["shapes"].append(circle((0, 18), 30, fill="body"))
tiny_ancient_menace["shapes"].append(
    polyline([(-20, -12), (-8, -36), (0, -18), (8, -36), (20, -12)], color="accent", width=4)
)
tiny_ancient_menace["shapes"].append(circle((-28, -6), 6, fill="accent"))
tiny_ancient_menace["shapes"].append(circle((28, -2), 6, fill="accent"))
tiny_ancient_menace["shapes"].append(
    polyline([(-18, 44), (-8, 24), (0, 44), (8, 24), (18, 44)], color="detail", width=3)
)
tiny_ancient_menace["shapes"].append(line([(-20, 20), (-36, 34)], color="detail", width=3))
tiny_ancient_menace["shapes"].append(line([(20, 20), (36, 34)], color="detail", width=3))
tiny_ancient_menace["shapes"].extend(simple_face(2))
SPRITES["tiny_ancient_menace"] = tiny_ancient_menace

cryptid_friend: dict[str, object] = {}
cryptid_friend["palette"] = "cryptid"
cryptid_friend["shapes"] = []
cryptid_friend["shapes"].append(ellipse((0, 14), (82, 92), fill="body"))
cryptid_friend["shapes"].append(
    polyline([(-24, -40), (-16, -60), (-8, -40)], color="accent", width=3)
)
cryptid_friend["shapes"].append(polyline([(24, -40), (16, -60), (8, -40)], color="accent", width=3))
cryptid_friend["shapes"].append(polygon([(-36, 12), (-56, -8), (-46, 30)], fill="accent"))
cryptid_friend["shapes"].append(polygon([(36, 12), (56, -8), (46, 30)], fill="accent"))
cryptid_friend["shapes"].append(
    polyline([(-28, 34), (-10, 54), (10, 54), (28, 34)], color="accent", width=4)
)
cryptid_friend["shapes"].append(circle((-30, -12), 5, fill="accent"))
cryptid_friend["shapes"].append(circle((30, -8), 5, fill="accent"))
cryptid_friend["shapes"].extend(simple_face(-10))
SPRITES["cryptid_friend"] = cryptid_friend
