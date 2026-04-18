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
