"""Build the whole world here: room maps, neighbors, doors, and story writing.

To add a room:
1. Copy an entry in LEVELS below and give it a new key, such as 'my_room'.
2. Edit its name, map letters, and legend. Keep a spawn('entrance') marker.
3. Add door('my_room', 'entrance') to another room's map and legend.
Run python main.py --check, then --level my_room to preview your room.
All rooms share this file; no extra files or imports are needed to add one.
"""

from .building import branch, choice, door, item, level, person, rest, sign, spawn, trigger
from .student_mechanics import warm_light

# Map letters get their meanings from each room's legend.
# Room keys below are the names used by doors and --level.
LEVELS = {
    "courtyard": level(
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
    ),
    "garden": level(
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
    ),
    "studio": level(
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
                    "This room is written in student_world.py. Each letter has a meaning in its legend.",
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
    ),
    "nook": level(
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
    ),
}

START_LEVEL = "courtyard"
START_ENTRY = "camp"  # The name of a spawn(...) marker in that room.
