# Build your story in Python

Open **`undercode/levels/studio.py`**. It describes a small quest using Python
function calls: meet the Story Keeper, collect a bookmark, open the east gate,
read the ending, and return to hear a different greeting.

```bash
python main.py --level studio
```

Change a sentence or move a map letter. Run `python main.py --check`, then play
again. Level files are ordinary Python: you can use comments, variables, lists,
dictionaries and functions as you learn them.

## Your first new level

Save this as **`undercode/levels/my_room.py`**:

```python
"""My first story level."""

from ..building import level, spawn, person, sign, door

LIBRARIAN_NAME = "The Librarian"  # Change this and run again.

LEVEL = level(
    "My first room",
    tiles=[
        "############",
        "#@....F....#",
        "#..........#",
        "#..?.......D",
        "############",
    ],
    legend={
        "@": spawn("entrance"),
        "F": person(
            "folio",
            name=LIBRARIAN_NAME,
            battle=False,
            text=["Welcome! What kind of story will you tell?"],
        ),
        "?": sign("A note", "Your story starts here."),
        "D": door("courtyard", "camp"),
    },
)
```

A **list** (`[...]`) stores the map rows in order. A **dictionary** (`{...}`)
connects each letter to its meaning. A **function call**, such as
`door("courtyard", "camp")`, describes the object to put there. Named arguments
such as `battle=False` let you change just the options you need.

Open **`undercode/student_world.py`**. Add `my_room` to the existing import:

```python
from .levels import courtyard, garden, nook, studio, my_room
```

Add one entry to `LEVELS`, keeping the existing entries:

```python
LEVELS = {
    "courtyard": courtyard.LEVEL,
    "garden": garden.LEVEL,
    "nook": nook.LEVEL,
    "studio": studio.LEVEL,
    "my_room": my_room.LEVEL,
}
```

```bash
python main.py --check
python main.py --level my_room --entry entrance
```

The dictionary key `"my_room"` is the level name that doors and the command line
use. To reach it from the existing world, add a letter to another level's map
and its legend:

```python
"M": door("my_room", "entrance"),
```

Doors arrive at **named markers**. Move `@` anywhere on walkable ground and all
doors using `"entrance"` arrive there. Use different letters and marker names
for additional entrances. Put markers away from doors so arriving players have
room to stand. `START_LEVEL` and `START_ENTRY` in `student_world.py` choose the
beginning of a run. R clears progress and starts again.

## Maps and legends

Rows must be equally wide: **3–30 columns and 3–16 rows**. Smaller rooms are
centered. Spaces count as tiles; use `g` for grass if that is easier to read.
Scrolling maps can be a later programming project.

Default terrain: `#` wall/tree, `~` water, `.` path, `g` grass, `d` bridge, and
space for grass. Walls and water block movement. Every other symbol needs a
legend entry. Letters have **no built-in object meaning**: `F` can be a person
in one level and a door in another. The legend can override terrain letters too.
Use one character per symbol, avoiding combining emoji.

Objects stand on path by default. Add `tile="g"` for grass underneath, or
alias terrain with any letter:

```python
"T": terrain("#"),
"F": person("folio", tile="g"),
```

Import the helpers you use from `..building` at the top of the level file.
Every helper has a docstring explaining its arguments.

| Function call | What the player finds |
| --- | --- |
| `spawn("entrance")` | Invisible named arrival marker |
| `person("folio")` | A neighbor offering a battle |
| `person("echo", battle=False, text="Hello!")` | A story-only neighbor |
| `door("garden", "south")` | A door to a named marker in another level |
| `sign("Notice", "Welcome!")` | A sign read with Z |
| `item("Bookmark", "bookmark", "You found it!")` | A collectible that sets a flag |
| `rest()` | A fountain that restores HP and cocoa with Z |
| `trigger(warm_light, name="Warm light")` | A place that calls your Python function on entry |
| `terrain("#")` | A wall/tree under any chosen map letter |

A symbol can repeat for terrain, doors or separate objects. Give a character a
unique `id` when its battle outcome matters:

```python
"G": person("ferris", id="gate_guard"),
```

To repeat the same character art in several places, omit `id` for automatic
per-instance IDs, or use different letters with different IDs. Spawn names are
unique within a level; explicit character IDs are unique across the story.

## Dialogue and choices

`text` accepts a string or list of paragraphs. Long passages are paged
automatically; Z advances and X closes. Movement pauses while reading.
Existing character keys are `folio`, `ferris`, `prism`, and `echo`. A story-only
neighbor can reuse any portrait with `battle=False` and its own `name`/writing.

A battle character with story text speaks before offering the normal
accept/decline invitation. Without story text, it offers the invitation immediately.

Add a choice list using Python calls:

```python
"C": person(
    "echo",
    battle=False,
    name="Gate Keeper",
    text="Will you carry a message?",
    choices=[
        choice("Yes, I will.", "Thank you!", set_flags=["accepted_message"]),
        choice("Maybe later.", "I will wait here."),
    ],
),
```

The arrows select; Z commits the choice, sets its flags, and opens the reply.
Keep labels at most 60 characters. Longer lists scroll. X after choosing closes
the reply but does not undo that choice.

`set_flags` on the whole conversation applies after its last page is confirmed.
Closing early does not set those completion flags. Items are collected on
interaction, even if their description is closed early.

## Remembering what happened

A flag is a name you invent, such as `"bookmark"` or `"accepted_message"`.
An item sets its flag; choices and completed dialogue can use `set_flags`.
Check a flag on a door:

```python
"G": door(
    "my_room",
    "entrance",
    requires="bookmark",
    locked_text="Find the golden bookmark first.",
),
```

`requires` also works on people, signs, items, rests, triggers and choices.
A list such as `requires=["bookmark", "accepted_message"]` requires **all**
flags. Locked people/objects remain visible and show `locked_text` when used;
unavailable choices are hidden. Triggers check conditions when you enter.

Use `requires="spared:gate_guard"` or `"defeated:gate_guard"` to check a
battle outcome by placement `id`. Leaving/losing is neither. Those two prefixes
are reserved for outcome checks, so use other names for ordinary flags.

For a greeting that changes as the story progresses, add branches:

```python
"C": person(
    "echo",
    battle=False,
    text="Please find the bookmark.",
    branches=[
        branch("finished_story", "You finished it! What comes next?"),
        branch("bookmark", "You found it. The gate will open now."),
    ],
),
```

The **first matching branch replaces the default conversation**, including its
choices and completion flags. Put the most specific ending first. A branch may
have its own `choices` and `set_flags`. The starter supports a choice followed
by a reply; several conversations with flags let you build a longer story.

## Connect your own Python mechanics

Mission 2 in **`undercode/student_mechanics.py`** provides an unfinished
`warm_light(world, obj)` function. The Studio already connects it to its mint
oval; follow the inline walkthrough to implement healing and feedback.
Ordinary fountains work while this mission is unfinished.

Connect your function in a level with a normal import and function argument:

```python
from ..building import trigger
from ..student_mechanics import warm_light

# Inside your legend:
"s": trigger(warm_light, name="Warm light"),
```

Pass **`warm_light`**, without parentheses. You are giving the engine a function
to call later. `warm_light(...)` would call it immediately while defining the level.
The engine calls `warm_light(world, obj)` once on entry, then again if you leave
and return. The function can inspect `obj.data`, change `world.session.flags`,
heal, or show `world.tell(...)`; it does not draw a frame.

For an action when Z is pressed, pass an `on_interact` function:

```python
from ..student_mechanics import your_action

"?": sign("A curious sign", "Something happened.", on_interact=your_action),
```

Write `your_action(world, obj)` yourself, then import it. Requirements are
checked before the action runs. Use dialogue completion flags for rewards that
require reading to the end. For attacks and defenses, continue with the guided
missions in [MISSIONS.md](MISSIONS.md).

## Testing and finding mistakes

`--check` validates Python level definitions, map dimensions, legend fields,
character keys, IDs, callable hooks, door destinations and named arrival markers.
Normal launch checks story content too. Unknown letters report the level, row
and column. Python syntax/import errors show the usual file and line traceback;
fix that line, then run again. Stop and relaunch after editing: definitions are
built at startup; R resets progress without re-importing files. Use comments to explain your story and variables for repeated writing.
