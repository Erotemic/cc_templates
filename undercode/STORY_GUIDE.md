# Build a story with letter maps

Start with **`undercode/story/studio.json`**. It contains a complete small quest:
meet the Story Keeper, collect a bookmark, open the east gate, read the ending,
and return to hear a different greeting. Run it directly:

```bash
python main.py --level studio
```

Change the writing or move a letter in the map. Run `python main.py --check`,
then play again. You can build a whole story without changing a Python file.

## Your first new level

Save this as **`undercode/story/my_room.json`**:

```json
{
  "name": "My first room",
  "map": [
    "############",
    "#@....F....#",
    "#..........#",
    "#..?.......D",
    "############"
  ],
  "legend": {
    "@": {"kind": "spawn", "id": "entrance"},
    "F": {
      "kind": "character",
      "character": "folio",
      "name": "The Librarian",
      "battle": false,
      "text": ["Welcome! What kind of story will you tell?"]
    },
    "?": {"kind": "sign", "name": "A note", "text": "Your story starts here."},
    "D": {"kind": "door", "to": "courtyard", "entry": "camp"}
  }
}
```

```bash
python main.py --check
python main.py --level my_room --entry entrance
```

The file name is the level key. New files are found automatically. To reach it
from the existing world, add a door letter to another room's map and legend:

```json
"M": {"kind": "door", "to": "my_room", "entry": "entrance"}
```

The destination is a **named spawn marker**, not a coordinate pair. Move `@`
anywhere on walkable ground and every door using `entrance` follows it.
Use different symbols/IDs for additional entrances. Place markers away from
doors so arriving players have room to stand. The starting room and marker
are in `undercode/story/_world.json`. R clears story progress for a new run.

## Maps and legends

Rows must have equal lengths: **3–30 columns and 3–16 rows**. Smaller rooms
are centered. Count spaces as tiles; use `g` for grass when spaces are hard to
see. This starter has a single-screen viewport; scrolling is a later project.

The default terrain is `#` wall/tree, `~` water, `.` path, `g` grass, `d` bridge,
and space for grass. Walls and water block movement. All other symbols need
a legend entry. Letters have **no built-in object meanings**: `F` can mean a
character in one room and a door in another. The legend can even override a
terrain symbol. Use one character per symbol, avoiding combining emoji.

Objects stand on path by default. Add `"tile": "g"` for grass underneath, or
use an alias for terrain:

```json
"T": {"kind": "tile", "tile": "#"}
```

| Kind | Fields to start with | Behavior |
| --- | --- | --- |
| `spawn` | `id` | Invisible named arrival point |
| `character` | `character`, optional `name`, `battle`, `text` | Z talks; battle defaults to true |
| `door` | `to`, `entry` | Walk onto it to change levels with a fade |
| `sign` | `name`, `text` | Z reads paged text |
| `item` | `name`, `flag`, `text` | Z collects once; remembers its flag for this run |
| `rest` | optional `name` | Z restores HP and cocoa |
| `trigger` | `on_enter`, optional `name` | Calls a registered Python mechanic on entry |
| `tile` | `tile` | Paints terrain, with no interaction |

A symbol can repeat for terrain, doors or separate objects. Give characters
an explicit unique `id` when their outcome matters; for example `"id": "gate_guard"`.
If you repeat a character symbol, omit its ID for automatic per-instance IDs,
or use different letters with different IDs. Spawn IDs are unique within a
level; explicit character IDs are unique across the story.

## Writing dialogue and choices

`text` can be one string or a list of paragraphs. Long passages are paged
automatically; Z advances and X closes. Movement pauses while reading.
A character with `"battle": false` only talks. Reuse any existing `character`
key for its portrait: `folio`, `ferris`, `prism`, or `echo`.
A battle character with story text first speaks, then offers the normal
accept/decline invitation. With no text, it offers the invitation immediately.

Add choices to a character or sign:

```json
"C": {
  "kind": "character",
  "character": "echo",
  "battle": false,
  "name": "Gate Keeper",
  "text": "Will you carry a message?",
  "choices": [
    {"label": "Yes, I will.", "text": "Thank you!", "set_flags": ["accepted_message"]},
    {"label": "Maybe later.", "text": "I will wait here."}
  ]
}
```

The arrows select; Z commits the choice, sets its flags, and opens its reply.
Keep labels at most 60 characters. Longer lists scroll to the selected choice.
X after choosing closes the reply but does not undo the choice.

A `set_flags` list on the whole dialogue is applied after the last page is
confirmed. Closing early does not set those completion flags. Items are collected
immediately on interaction, even if their description is closed early.

## Remembering what happened

Flags are names you invent, such as `bookmark` or `accepted_message`. An item
sets its `flag`, and choices/completed dialogue can use `set_flags`.
A door can require a flag:

```json
"G": {
  "kind": "door", "to": "my_room", "entry": "entrance",
  "requires": "bookmark",
  "locked_text": "Find the golden bookmark first."
}
```

`requires` also works on characters, signs, items, rests, triggers and choices.
A list such as `["bookmark", "accepted_message"]` requires **all** of them.
Characters/objects remain visible when locked, and show `locked_text` when used;
unavailable choices are hidden. Triggers wait until their conditions are met
on a new entry. Use `spared:gate_guard` or `defeated:gate_guard` to check a
battle outcome using the character's placement `id`. Leaving/losing is neither.
Those two prefixes are reserved for outcome checks, not ordinary flag names.

Use `branches` for a different conversation when progress changes:

```json
"text": "Please find the bookmark.",
"branches": [
  {"requires": "finished_story", "text": "You finished it! What comes next?"},
  {"requires": "bookmark", "text": "You found it. The gate will open now."}
]
```

The **first matching branch replaces the default dialogue**, including its
choices and completion flags. Put the most specific ending first. A branch can
have its own `text`, `choices`, and `set_flags`. The starter supports one choice
followed by a reply, rather than an entire nested dialogue language. Several
conversations with flags are often enough to tell a story.

## Add mechanics when you need them

Open **`undercode/student_mechanics.py`**. Mission 2 gives you the
`warm_light(world, obj)` function, already connected to the Studio's mint oval.
Its effect is intentionally unfinished: follow the inputs, diagnostic and
small steps in its docstring to implement healing and a HUD message. Play
`python main.py --level studio` after each edit. Ordinary fountains still
restore HP while this mission is unfinished.

The engine calls a registry function by name:

```python
WORLD_MECHANICS = {"warm_light": warm_light}
```

Connect it through a legend entry:

```json
"s": {"kind": "trigger", "name": "Warm light", "on_enter": "warm_light"}
```

The function runs once when entering, then again if you leave and return.
It receives the world and the object, so it can read `obj.data`, set
`world.session.flags`, heal, or call `world.tell(...)`. It does not draw.
For a sign, item, character or rest, use `on_interact` instead, which runs on Z
after requirements pass. A mechanic hook is an immediate action; dialogue
completion flags are the right choice for rewards that require reading to the end.

Add your own function and registry name for a new rule. JSON only names
registered functions; it never evaluates Python expressions. For battles and
special defense sequences, continue with `student.py` and [MISSIONS.md](MISSIONS.md).

## Fixing map mistakes

`--check` checks JSON, map sizes, legend fields, character keys, IDs, mechanic
names, door targets and arrival markers before simulating combat content.
Normal launch also validates story files, so a typo produces a terminal error
rather than a half-working level. Unknown symbols report file, row and column.
JSON uses double quotes, `true`/`false`, and no trailing commas or comments.
Restart the game after editing files; levels are read at startup.
