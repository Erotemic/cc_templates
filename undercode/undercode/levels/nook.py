"""The Reading Nook: edit the map letters, dialogue, and Python helper calls here."""

from ..building import door, level, sign, spawn

# Each map letter gets its meaning from the legend below.
LEVEL = level(
    "The Reading Nook",
    tiles=[
        "############",
        "#gggggggggg#",
        "#gggggggggg#",
        "D.@...?....#",
        "#gggggggggg#",
        "#gggggggggg#",
        "#gggggggggg#",
        "############",
    ],
    legend={
        "@": spawn("entrance"),
        "D": door("studio", "east"),
        "?": sign(
            "The last page",
            [
                "You place the bookmark between two blank pages. There is room here for your own adventure.",
                "Return to the Story Keeper to hear what changed.",
            ],
            set_flags=["finished_story"],
        ),
    },
)
