"""ALL rooms and story writing live here. Start by changing one sentence.

Room/Person/Door are dataclasses: named records, not a special scripting language.
Every call uses keywords so you can read each value's purpose at its use site.
To add a room, copy a LEVELS entry, give it a new key, then link a Door to a Spawn.
The overworld can run this file without importing any encounter definitions.
"""

from .overworld.model import Room, Spawn, Person, Door, Sign, Item, Rest, Trigger, PianoKey
from .dialogue import Dialogue, Choice, Branch
from .art import folio, ferris, prism
from .student_art import draw_echo
from .student_overworld import warm_light

LEVELS = {
    "courtyard": Room(
        name="Lantern Courtyard",
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
            "#ggg.R.@.g?ggg..gggggg!gggggg#",
            "#ggggggggggggg..ggg12345678gg#",
            "#ggggggggggggg..ggggggggggggg#",
            "##############################",
        ],
        legend={
            "@": Spawn(name="camp"),
            "a": Spawn(name="north"),
            "F": Person(name="Folio", portrait=folio, id="folio", encounter_id="folio"),
            "B": Person(name="Ferris", portrait=ferris, id="ferris", encounter_id="ferris"),
            "R": Rest(),
            # Visible floor keys: C4 works; mission 7 asks students to repair the remaining keys.
            "1": PianoKey(note="C4"),
            "2": PianoKey(note="D4"),
            "3": PianoKey(note="E4"),
            "4": PianoKey(note="F4"),
            "5": PianoKey(note="G4"),
            "6": PianoKey(note="A4"),
            "7": PianoKey(note="B4"),
            "8": PianoKey(note="C5"),
            "!": Sign(
                name="Piano notice",
                dialogue=Dialogue(
                    text="A piano, but most of the keys seem broken. Maybe we can fix it?"
                ),
            ),
            "N": Door(destination_room="garden", destination_spawn="south"),
            "?": Sign(
                name="Trail guide",
                dialogue=Dialogue(
                    text=[
                        "North: the observatory. East of its pond: a story to help finish.",
                        "Z reads signs and talks to neighbors. X puts a conversation down.",
                    ]
                ),
            ),
        },
    ),
    "garden": Room(
        name="Quiet Observatory",
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
            "a": Spawn(name="south"),
            "b": Spawn(name="east"),
            "P": Person(name="Prism", portrait=prism, id="prism", encounter_id="prism"),
            "E": Person(name="Echo", portrait=draw_echo, id="echo", encounter_id="echo"),
            "R": Rest(),
            "S": Door(destination_room="courtyard", destination_spawn="north"),
            "W": Door(destination_room="studio", destination_spawn="entrance"),
        },
    ),
    "studio": Room(
        name="The Story Studio",
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
            "@": Spawn(name="entrance"),
            "D": Door(destination_room="garden", destination_spawn="east"),
            "C": Person(
                name="Story Keeper",
                portrait=draw_echo,
                id="keeper",
                dialogue=Dialogue(
                    text=["Every story needs a beginning. Will you help light the reading nook?"],
                    choices=[
                        Choice(
                            label="I will help.",
                            text="Thank you! Find the golden bookmark, then walk through the east gate.",
                            set_flags=["promised_help"],
                        ),
                        Choice(
                            label="Tell me more.",
                            text="A bookmark is waiting below the path. The east gate opens when you collect it.",
                        ),
                    ],
                    branches=[
                        Branch(
                            required_flag="finished_story",
                            text="A beginning, a choice, and an ending. What will you write next?",
                        ),
                        Branch(
                            required_flag="bookmark",
                            text="You found it! The reading nook is through the east gate.",
                        ),
                    ],
                ),
            ),
            "?": Sign(
                name="An unfinished page",
                dialogue=Dialogue(
                    text=[
                        "This room is written in student_world.py. Each letter has a meaning in its legend.",
                        "Try moving a letter, rewriting a line, or adding a new room. The game engine can stay exactly as it is.",
                    ]
                ),
            ),
            "K": Item(
                name="Golden bookmark",
                flag="bookmark",
                text="You found a golden bookmark. The east gate can open now.",
            ),
            "G": Door(
                destination_room="nook",
                destination_spawn="entrance",
                locked_text="The gate needs a golden bookmark. Look below the path.",
                required_flag="bookmark",
            ),
            "s": Trigger(on_enter=warm_light, name="Warm light"),
            "b": Spawn(name="east"),
        },
    ),
    "nook": Room(
        name="The Reading Nook",
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
            "@": Spawn(name="entrance"),
            "D": Door(destination_room="studio", destination_spawn="east"),
            "?": Sign(
                name="The last page",
                dialogue=Dialogue(
                    text=[
                        "You place the bookmark between two blank pages. There is room here for your own adventure.",
                        "Return to the Story Keeper to hear what changed.",
                    ],
                    set_flags=["finished_story"],
                ),
            ),
        },
    ),
}

START_LEVEL = "courtyard"

START_ENTRY = "camp"
