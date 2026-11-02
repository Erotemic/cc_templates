"""Lantern Courtyard: edit the map letters, dialogue, and Python helper calls here."""

from ..building import door, level, person, rest, sign, spawn

# Each map letter gets its meaning from the legend below.
LEVEL = level(
    "Lantern Courtyard",
    tiles=[
        "##############NN##############",
        "#ggggggggggggg..ggggggggggggg#",
        "#ggggggggggggga.ggggggggggggg#",
        "#gg~~~d~~~gggg..ggggggggggggg#",
        "#gg~~~d~~~gggg..ggggggggggggg#",
        "#gg~~~d~~~gggg..ggggggggggggg#",
        "#gg~~~d~~~gggg..ggggggggggggg#",
        "#ggggggggggggg..ggggggggggggg#",
        "#ggggggggggggg..ggggggggggggg#",
        "#gg.....F..................gg#",
        "#gg....................B...gg#",
        "#ggggggggggggg..ggggggggggggg#",
        "#ggg.R.@.g?ggg..ggggggggggggg#",
        "#ggggggggggggg..ggggggggggggg#",
        "#ggggggggggggg..ggggggggggggg#",
        "##############################",
    ],
    legend={
        "@": spawn("camp"),
        "a": spawn("north"),
        "F": person("folio", id="folio"),
        "B": person("ferris", id="ferris"),
        "R": rest(),
        "N": door("garden", "south"),
        "?": sign(
            "Trail guide",
            [
                "North: the observatory. East of its pond: a story to help finish.",
                "Z reads signs and talks to neighbors. X puts a conversation down.",
            ],
        ),
    },
)
