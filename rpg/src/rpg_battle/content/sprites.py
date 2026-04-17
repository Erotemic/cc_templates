from __future__ import annotations

"""Procedural battler sprite catalog.

Each sprite recipe is added individually so students can build one monster or
hero at a time and keep nearby comments or helper variables with that entry.
"""

from rpg_battle.content.presets import circle, ellipse, line, polygon, polyline, rect, simple_face

SPRITES: dict[str, dict[str, object]] = {}

SPRITES["knight_dawn"] = {
    "palette": "dawn",
    "shapes": [
        polygon([(-28, 14), (0, -52), (28, 14)], fill="accent"),
        rect((0, 14), (68, 78), fill="body"),
        rect((0, -8), (46, 52), fill="accent"),
        rect((-40, 10), (24, 48), fill="accent"),
        line([(-40, -12), (-40, 34)], color="detail", width=4),
    ]
    + simple_face(-14),
}

SPRITES["verdant_druid"] = {
    "palette": "verdant",
    "shapes": [
        ellipse((0, 12), (76, 90), fill="body"),
        polygon([(-26, -36), (-6, -56), (0, -28)], fill="accent"),
        polygon([(26, -36), (6, -56), (0, -28)], fill="accent"),
        line([(-20, 20), (0, 42), (20, 20)], color="detail", width=3),
        polyline([(-38, -4), (-56, -28), (-52, 26)], color="detail", width=4),
    ]
    + simple_face(-10),
}

SPRITES["storm_ranger"] = {
    "palette": "storm",
    "shapes": [
        ellipse((0, 8), (70, 88), fill="body"),
        polygon([(-36, -10), (-8, -58), (18, -16)], fill="accent"),
        line([(34, -32), (52, 28)], color="detail", width=5),
        line([(14, -10), (44, 8)], color="accent", width=3),
    ]
    + simple_face(-14),
}

SPRITES["moon_mage"] = {
    "palette": "moon",
    "shapes": [
        ellipse((0, 12), (74, 92), fill="body"),
        circle((0, -46), 20, fill="accent"),
        polyline([(-20, -28), (0, -42), (20, -28)], color="detail", width=3),
        circle((28, -32), 8, fill="accent"),
        circle((-30, 32), 10, fill="accent"),
    ]
    + simple_face(-8),
}

SPRITES["crystal_guardian"] = {
    "palette": "crystal",
    "shapes": [
        polygon([(-40, 10), (-14, -44), (14, -44), (40, 10), (20, 52), (-20, 52)], fill="body"),
        polygon([(-12, -52), (0, -74), (12, -52)], fill="accent"),
        polygon([(-54, 4), (-34, -20), (-26, 22)], fill="accent"),
        polygon([(54, 4), (34, -20), (26, 22)], fill="accent"),
    ]
    + simple_face(-10),
}

SPRITES["mist_spirit"] = {
    "palette": "mist",
    "shapes": [
        ellipse((0, 8), (78, 88), fill="body"),
        ellipse((0, 26), (56, 40), fill="accent"),
        polyline([(-30, 20), (-10, 44), (8, 20), (28, 44)], color="detail", width=3),
        circle((-28, -30), 7, fill="accent"),
        circle((28, -36), 9, fill="accent"),
    ]
    + simple_face(-16),
}

SPRITES["runesage"] = {
    "palette": "rune",
    "shapes": [
        circle((0, 10), 40, fill="body"),
        circle((0, 10), 28, fill="accent"),
        polyline([(-42, -30), (-18, -50), (0, -30), (18, -50), (42, -30)], color="accent", width=3),
        line([(-52, 16), (52, 16)], color="detail", width=3),
        polyline([(-30, 28), (-14, 14), (0, 28), (14, 14), (30, 28)], color="accent", width=3),
    ]
    + simple_face(-8),
}

SPRITES["ai_slop"] = {
    "palette": "slop",
    "shapes": [
        ellipse((0, 8), (82, 88), fill="body"),
        polygon([(-18, -52), (18, -46), (32, -10), (-26, -18)], fill="accent"),
        rect((-48, 12), (16, 42), fill="accent", border_radius=5),
        rect((46, -6), (18, 52), fill="accent", border_radius=5),
        line([(-46, 8), (-78, -4), (-64, 30), (-88, 36)], color="detail", width=4),
        line([(46, -2), (82, -26), (68, 12), (98, 6)], color="detail", width=4),
        polygon([(-8, 26), (10, 18), (26, 34), (-2, 42)], fill="accent"),
        circle((-26, -8), 5, fill="eye", outline="detail", width=1),
        circle((16, -2), 7, fill="eye", outline="detail", width=1),
        line([(-30, 22), (-2, 32), (18, 18), (30, 34)], color="detail", width=3),
        rect((-12, -34), (10, 10), fill="accent", border_radius=2),
        rect((32, 24), (12, 12), fill="accent", border_radius=2),
    ],
}
