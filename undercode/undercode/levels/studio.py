"""The Story Studio: edit the map letters, dialogue, and Python helper calls here."""

from ..building import branch, choice, door, item, level, person, sign, spawn, trigger
from ..student_mechanics import warm_light

# Each map letter gets its meaning from the legend below.
LEVEL = level(
    "The Story Studio",
    tiles=[
        "####################",
        "#gggggggggggggggggg#",
        "#gggggggggggggggggg#",
        "#gggggggggggggggggg#",
        "D.@...C..........b.G",
        "#gggggggggggggggggg#",
        "#gggggggggggggggggg#",
        "#gg?ggggggKgggggggg#",
        "#gggggggggggggggggg#",
        "#gggggggsgggggggggg#",
        "#gggggggggggggggggg#",
        "####################",
    ],
    legend={
        "@": spawn("entrance"),
        "D": door("garden", "east"),
        "C": person(
            "echo",
            id="keeper",
            name="Story Keeper",
            battle=False,
            text=["Every story needs a beginning. Will you help light the reading nook?"],
            choices=[
                choice(
                    "I will help.",
                    "Thank you! Find the golden bookmark, then walk through the east gate.",
                    set_flags=["promised_help"],
                ),
                choice(
                    "Tell me more.",
                    "A bookmark is waiting below the path. The east gate opens when you collect it.",
                ),
            ],
            branches=[
                branch(
                    "finished_story",
                    "A beginning, a choice, and an ending. What will you write next?",
                ),
                branch("bookmark", "You found it! The reading nook is through the east gate."),
            ],
        ),
        "?": sign(
            "An unfinished page",
            [
                "This room is written in levels/studio.py. Each letter has a meaning in its legend.",
                "Try moving a letter, rewriting a line, or adding a new room. The game engine can stay exactly as it is.",
            ],
        ),
        "K": item(
            "Golden bookmark",
            "bookmark",
            "You found a golden bookmark. The east gate can open now.",
        ),
        "G": door(
            "nook",
            "entrance",
            requires="bookmark",
            locked_text="The gate needs a golden bookmark. Look below the path.",
        ),
        "s": trigger(warm_light, name="Warm light"),
        "b": spawn("east"),
    },
)
