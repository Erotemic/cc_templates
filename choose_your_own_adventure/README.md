# Choose Your Own Adventure

This project teaches text-adventure programming in four levels. Each level has
its own numbered progression so students only see the amount of structure that
is useful for what they are learning now.

```text
choose_your_own_adventure/
    beginner/
        version1.py     one loop and ordinary control flow
        version2.py     extract repeated work into functions

    intermediate/
        version1.py     dataclasses, room data, and function dispatch
        version2.py     a Game object and a small game/UI boundary
        version3.py     a larger game in one self-contained file

    advanced/
        version1.py     extract the larger game into reusable modules
        version2.py     reuse the same game from a Textual frontend
        version3.py     add presentation without changing game rules
        version4.py     build a second world on the same engine
        adventure/      small shared library for the advanced lessons

    capstone/
        version1.py     complete Star Crystal adventure
        version2.py     complete Dust Vault adventure
        engine/         full reusable game mechanics
        worlds/         faithfully ported full worlds + student extension zones

    tests/
    check.py
```

The important boundary is intentional: **beginner and intermediate examples do
not depend on a package.** A student can read, copy, and modify one file without
first understanding modules. Advanced introduces a package because reuse has a
clear purpose. Capstone then shows that the same separation can support a large,
branching game without making ordinary world-building harder.

## Pick a level

### Beginner

Start here if loops, conditionals, lists, dictionaries, and functions are still
new.

| File | New idea |
|---|---|
| `beginner/version1.py` | variables, collections, `while`, `if`, terminal input/output |
| `beginner/version2.py` | functions, parameters, return values, reducing repetition |

Both files contain the **same tiny treasure story**. Compare them directly to
see what functions change without also learning new game rules.

### Intermediate

Start here when functions are comfortable and you are ready to organize a
larger program.

| File | New idea |
|---|---|
| `intermediate/version1.py` | dataclasses, room data, functions stored in a dictionary |
| `intermediate/version2.py` | objects, methods, one owner for runtime state, game/UI separation |
| `intermediate/version3.py` | a larger world, inventory, quest state, combat, conditional choices |

The examples remain self-contained. A student can add an ordinary room or a
story-only choice in the room data; they only need to edit mechanics when they
actually want a new mechanic.

### Advanced

Start here when the single-file architecture makes sense and you want to learn
how a project separates reusable code from content and presentation.

| File | New idea |
|---|---|
| `advanced/version1.py` | modules and real code reuse |
| `advanced/version2.py` | a second Textual frontend using the same game API |
| `advanced/version3.py` | presentation-only ASCII art |
| `advanced/version4.py` | a completely different world using the same engine |

The teaching engine is deliberately small:

```text
advanced/adventure/
    core.py
    art.py
    worlds/
    ui/
```

A world owns rooms and choices. `RoomChoice` is the simple extension point for
story content; world-specific Python functions remain available when a student
wants to invent a new rule.

### Capstone

Capstone means **larger game**, not “you must understand harder Python.”

- `capstone/version1.py` runs the complete Star Crystal world from the original
  advanced game line.
- `capstone/version2.py` runs the complete Dust Vault world from the original
  final game.
- `capstone/worlds/` preserves the authored rooms, exits, NPCs, dialogue,
  trades, riddles, features, encounters, item data, gates, and endings.
- `capstone/engine/` contains the mechanics needed to run those worlds.

Each world file ends with `EXTRA_ROOMS` and `EXTRA_CHOICES`. A student can add a
side room or branch there without reading or modifying the combat, dialogue,
trade, encounter, inventory, or effect machinery.

This is an important design goal: **a student can build a bigger game by writing
more game, not by first becoming an engine programmer.**

## Run the examples

From `choose_your_own_adventure/`:

```bash
python beginner/version1.py
python beginner/version2.py

python intermediate/version1.py
python intermediate/version2.py
python intermediate/version3.py

python advanced/version1.py
python advanced/version3.py
python advanced/version4.py

python capstone/version1.py
python capstone/version2.py
```

`advanced/version2.py` uses the optional Textual package:

```bash
python advanced/version2.py
```

If Textual is unavailable, that example explains which package is missing.
None of the other versions require it.

## Run the checks

```bash
python check.py
python -m pytest -q
```

The tests include complete scripted paths through the teaching games and the
capstones. They also lock the preserved capstone world data with fingerprints
so a future cleanup cannot silently discard authored rooms or branches.

## What should students build on?

### Beginner projects

Copy a file and change it directly: add a choice, item, flag, second ending,
score, or health.

### Intermediate projects

`intermediate/version2.py` and `version3.py` are designed so rooms own simple
story choices. Students can add rooms and choices first, then add handlers only
when they deliberately introduce a new mechanic.

### Advanced projects

Copy a world module under `advanced/adventure/worlds/`. Use `Room` and
`RoomChoice` for ordinary content. Modify `core.py` only when the new idea is
truly a reusable mechanic.

### Capstone projects

Start with one of the full worlds under `capstone/worlds/`. The safest place to
experiment is the extension zone at the bottom:

```python
EXTRA_ROOMS = {
    "observatory": {
        "name": "Old Observatory",
        "description": "Dusty lenses point through a hole in the roof.",
        "exits": [{"direction": "back", "destination": "crossroads"}],
        "choices": [
            {
                "text": "Look through the telescope",
                "result": ["A blue star flickers above the hills."],
            },
        ],
    },
}

EXTRA_CHOICES = {
    "crossroads": [
        {"text": "Climb the hill to the observatory", "go": "observatory"},
    ],
}
```

The engine fills in omitted optional room lists. Students can grow from this
simple form into conditional choices, NPCs, trades, riddles, encounters, and
custom mechanics when they are ready.

## Architecture rules worth preserving

1. **Game rules own state.** UI code should not decide whether an enemy is
   defeated or whether a door opens.
2. **Presentation observes state.** Art may inspect the game; it should not make
   gameplay happen.
3. **Content stays cheap.** Adding a normal room or branch should not require a
   new engine abstraction.
4. **World code may be specific.** A one-off puzzle can be a normal Python
   branch instead of a framework class.
5. **Create abstractions after repetition appears.** More classes do not make a
   program more advanced by themselves.
6. **Prefer composition and functions before inheritance.** Most story variants
   are data plus behavior.

For instructor-facing rationale and lesson prompts, see `TEACHING_GUIDE.md`.
