# Build a story in Python

All maps, people, conversations and door links live in `undercode/student_world.py`.
Start with the `"studio"` room and run:

```bash
python main.py --level studio
```

Change a sentence or move a letter, stop and relaunch, then observe the result.
`Room`, `Person` and `Door` are small dataclasses holding named fields. The engine
reads their attributes directly; there is no dictionary schema of hidden options.
The only dictionary you need to author is the room list and each letter legend.

## A new room in the same file

Add this at the bottom of `student_world.py`. Its imports already include these
records and `folio`, a supplied portrait function:

```python
LEVELS["my_room"] = Room(
    name="My first room",
    tiles=[
        "############",
        "#@....F....#",
        "#..........#",
        "#..?.......D",
        "############",
    ],
    legend={
        "@": Spawn(name="entrance"),
        "F": Person(
            name="The Librarian",
            portrait=folio,
            dialogue=Dialogue(text="Welcome! What kind of story will you tell?"),
        ),
        "?": Sign(name="A note", dialogue=Dialogue(text="Your story starts here.")),
        "D": Door(destination_room="courtyard", destination_spawn="camp"),
    },
)
```

```bash
python main.py --overworld --check
python main.py --level my_room --entry entrance
```

`LEVELS["my_room"]` adds a dictionary entry. You can instead copy an existing
entry inside LEVELS. Both ways keep all rooms in this one file. Variables,
comments and ordinary Python functions are welcome.

To reach it on foot, draw a letter in another room and add this to its legend:

```python
"M": Door(destination_room="my_room", destination_spawn="entrance"),
```

Move the `@` and every door using that marker follows it. Named arrivals avoid
editing coordinate pairs. Put markers away from doors to avoid an immediate
return. START_LEVEL and START_ENTRY choose the beginning of a run.

## Terrain and letters

Use rectangular maps with 3–30 columns and 3–16 rows. Smaller maps are centered.
`#` means wall/tree, `~` water, `.` path, `g` grass, `d` bridge, and space grass.
Water and walls block movement. Every other letter needs a legend entry.
You choose its meaning separately in each room, including overriding a default
terrain letter. Objects have `ground="."` by default; choose `ground="g"` for grass.

To alias terrain, import Tile from `.overworld.model` and write:

```python
"T": Tile(ground="#"),
```

The map compiler places records by (column, row); World moves in room pixels.
See ENGINE_GUIDE for why the screen's centered drawing offset belongs to neither.

## People are independent of opponents

A Person needs a name and a portrait function. Add Dialogue for writing; leave
`encounter_id` absent to create a peaceful neighbor. Reuse a supplied portrait
or draw your own in `student_art.py` using the same named parameters.

To offer an encounter, add a link:

```python
"F": Person(
    id="courtyard_librarian",
    name="Folio",
    portrait=folio,
    dialogue=Dialogue(text="One story before we practice."),
    encounter_id="folio",
    invitation="Ready for the pages? Z: practice. X: later.",
),
```

The optional ID identifies this particular neighbor for remembered outcomes.
The encounter ID selects an Opponent in the encounter catalog. They need not
have the same name. Omit the writing for a direct invitation; otherwise the
invitation follows the conversation. X closes without starting an encounter.

Person IDs must be unique across rooms. Without an explicit ID, placement
creates one from the room and map letter's position. Use explicit IDs for
people referenced by story conditions. Spawn names are unique within a room.

## Choices and completion flags

A Dialogue accepts a string or a list of paragraphs. Long passages are paged.
Z advances; X closes. The world pauses walking while a conversation is open.

```python
"C": Person(
    name="Gate Keeper",
    portrait=draw_echo,
    dialogue=Dialogue(
        text="Will you carry a message?",
        choices=[
            Choice(label="Yes, I will.", text="Thank you!", set_flags=["accepted_message"]),
            Choice(label="Maybe later.", text="I will wait here."),
        ],
    ),
),
```

Arrows choose a reply and Z selects it. Its flags are added immediately, then
its reply appears. Cancelling that reply does not undo the choice. Keep labels
at most 60 characters; lists scroll to the selected reply.

`set_flags` on the whole Dialogue applies only after the last page is confirmed.
Closing early does not earn that completion reward. Read Conversation.update to
find the exact commit points; this is a useful example of changing persistent state.

## Items, rests, and flags

An Item sets its flag on collection and disappears. Its description can be
closed without undoing collection. A Rest restores full HP and two cocoa snacks.

```python
"K": Item(name="Golden bookmark", flag="bookmark", text="You found it!"),
"R": Rest(name="A warm place"),
"G": Door(
    destination_room="my_room",
    destination_spawn="entrance",
    required_flag="bookmark",
    locked_text="Find the golden bookmark first.",
),
```

Flags are names in `session.flags`, a normal Python set. `required_flag` also
works on people, signs, items, rests, triggers and choices. Unavailable choices
are hidden; other locked objects remain visible and explain why when used.

Branches change dialogue as the story progresses. The first matching branch
replaces the default text, choices and completion flags:

```python
dialogue=Dialogue(
    text="Please find the bookmark.",
    branches=[
        Branch(required_flag="finished_story", text="What will you write next?"),
        Branch(required_flag="bookmark", text="You found it. The gate is open."),
    ],
)
```

Put the most specific ending first. A Branch can also have choices/set_flags.

## A floor piano to program

The Studio's southeast corner uses `PianoKey(note="C4")` through C5, placed with
letters `1` through `8`. These records are visible, walkable keys, not automatic
triggers. Mission 7 in MISSIONS.md asks you to write player/key collision tests,
choose the frequency, and remember which key was playing. The empty
`student_overworld.update_piano` function is called by World.update each walking
frame. Until you implement it the piano stays silent.

To add keys to another room, use PianoKey records in its legend and draw their
letters. The same student rule can handle them because it reads the current
room's `world.piano_keys`. Audio playback is requested with
`world.play_tone(hz=..., duration=0.4)` and remains optional on school machines.

## Write a condition in ordinary Python

For more than one flag, or a remembered encounter outcome, define a named
function in this same file. It returns a boolean and changes nothing:

```python
from .contracts import Outcome


def librarian_is_a_friend(*, session):
    """Allow the story to react to a specific neighbor's outcome."""
    return session.resolved.get("courtyard_librarian") == Outcome.SPARED
```

Then use `when=librarian_is_a_friend` on a Door, Person, Sign, Item, Rest, Trigger,
or Branch. A record with both `required_flag` and `when` needs both to pass.
The same function could use `and` to require several flags. These are Python
conditionals you can debug; no string expression or special prefix is parsed.
Leaving or losing an encounter does not count as spared or defeated.

## Connect a new action

Mission 3's `warm_light` is already connected to the mint oval:

```python
"s": Trigger(name="Warm light", on_enter=warm_light),
```

Passing `warm_light` gives the engine a function to call later. Writing
`warm_light(...)` would call it while defining the room. The signature is
`def warm_light(*, world, obj):`; named arguments show each input's role.

The engine calls it once per entry. `obj.definition.name` is the authored name;
`obj.tile` is its placed position. Your function may heal with
`world.session.player.heal(amount=3)`, set flags, or show `world.tell(text=...)`.
For a Z action, give a Person/Sign/Item/Rest an `on_interact` function instead.
Requirements pass before actions run. For rewards that require finishing a
conversation, use its completion flags rather than an immediate action.

These hooks are convenient starting places. New kinds of world behavior may
need changes to World.update or a new record/drawing branch. Every engine file
is editable; the independent projects ask you to find those changes yourself.

## Inspect and debug

F2 shows room, position, facing and flags. `--overworld --check` validates room
shape, unknown letters, IDs, required arrival markers and callable mechanics.
`--check` also checks the connections to encounter IDs. An invalid Python keyword
fails at its source call; map mistakes report room, row and column. Normal Python
syntax/import errors keep their file/line traceback.

Stop and relaunch after editing. R starts a fresh run without re-importing code.
The world-only mode can still be opened while encounter code is unfinished.
