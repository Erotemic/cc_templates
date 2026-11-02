"""Quiet Observatory: edit the map letters, dialogue, and Python helper calls here."""

from ..building import door, level, person, rest, spawn

# Each map letter gets its meaning from the legend below.
LEVEL = level(
    "Quiet Observatory",
    tiles=[
        "##############################",
        "#ggggggggggggg..ggggggggggggg#",
        "#ggggggggggggg..gggg~~~~~~ggg#",
        "#gggggggggggggR.gggg~~~~~~ggg#",
        "#ggggg##gggggg..gggg~~~~~~ggg#",
        "#ggggg##gggggg..gggg~~~~~~ggg#",
        "#ggggggggggggg..ggggggggggggg#",
        "#ggggggggggggg..ggggggggggggg#",
        "#gg......P.................bgW",
        "#gg...................E....gg#",
        "#ggggggggggggg..ggggggggggggg#",
        "#ggggggggggggg..ggggggggggggg#",
        "#ggggggggggggg..gggggg##ggggg#",
        "#ggggggggggggga.gggggg##ggggg#",
        "#ggggggggggggg..ggggggggggggg#",
        "##############SS##############",
    ],
    legend={
        "a": spawn("south"),
        "b": spawn("east"),
        "P": person("prism", id="prism"),
        "E": person("echo", id="echo"),
        "R": rest(),
        "S": door("courtyard", "north"),
        "W": door("studio", "entrance"),
    },
)
