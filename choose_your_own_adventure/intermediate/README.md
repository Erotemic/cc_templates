# Intermediate adventures

These versions organize the program without introducing a reusable package.
Every example is still one self-contained Python file that students can copy
and modify directly.

A rule shared by all three versions: **adding an ordinary room or story-only
choice should be a data edit, not an engine edit.** Add a handler only when the
choice deliberately introduces a new mechanic.

## Version 1 — data-driven game

```bash
python intermediate/version1.py
```

New ideas include a `Player` dataclass, room data, small action functions, and
functions stored in a dictionary. Room `choices` may contain either an existing
`action` or a simple `result` list that needs no handler.

## Version 2 — game object

```bash
python intermediate/version2.py
```

New ideas include `Room`, `RoomChoice`, and `Choice`, one `Game` object that owns
changing state, and a console UI outside the rules.

A simple interaction is just:

```python
RoomChoice(
    "Read the faded sign",
    ("The sign says: KEEP OUT OF THE CAVE.",),
)
```

Put that in a room's `choices=(...)` tuple. `Game.apply()` already knows how to
run it.

## Version 3 — larger single-file game

```bash
python intermediate/version3.py
```

This Star Crystal teaching game adds inventory, quest flags, combat, conditional
choices, and a locked destination while keeping the same `RoomChoice` extension
point.

This is a good starting point for a substantial student project that should
remain understandable in one file. Move to `../advanced/` when splitting
reusable pieces into modules would actually help.
