# Choose Your Own Adventure

This project teaches text-adventure programming in three levels. Each level
has its own numbered progression, so students only see the amount of structure
that is useful for what they are learning now.

```text
choose_your_own_adventure/
    beginner/
        version1.py     one loop and ordinary control flow
        version2.py     extract repeated work into functions

    intermediate/
        version1.py     dataclasses, data, and function dispatch
        version2.py     a Game object and a small game/UI boundary
        version3.py     a larger game in one self-contained file

    advanced/
        version1.py     extract the larger game into reusable modules
        version2.py     reuse the same game from a Textual frontend
        version3.py     add presentation without changing game rules
        version4.py     build a second world on the same engine

        adventure/      shared library used by the advanced versions

    tests/
    check.py
```

The important boundary is intentional: **beginner and intermediate examples do
not depend on the shared `adventure` library.** A student can read, copy, and
modify one file without first understanding a package. The package appears only
when the advanced lessons are specifically teaching why modules and reuse are
useful.

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

The first two intermediate examples still use the same tiny treasure story.
`version3.py` then scales those ideas into the larger Star Crystal adventure,
but deliberately keeps everything in one file.

### Advanced

Start here when the single-file architecture makes sense and you want to learn
how a real project separates reusable code from content and presentation.

| File | New idea |
|---|---|
| `advanced/version1.py` | modules and real code reuse |
| `advanced/version2.py` | a second Textual frontend using the same game API |
| `advanced/version3.py` | presentation-only ASCII art |
| `advanced/version4.py` | a completely different world using the same engine |

The shared package lives beside these examples:

```text
advanced/adventure/
    core.py
        reusable state, choices, movement, and combat

    worlds/
        star_crystal.py
        dust_vault.py
        story data and story-specific Python rules

    ui/
        console.py
        textual_app.py
        two frontends for the same game object

    art.py
        optional presentation
```

`advanced/version4.py` is intentionally small. Its second world reuses the
library instead of copying the engine. That is the payoff for introducing the
package at this level.

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

The tests include complete scripted solutions for the tiny adventure, Star
Crystal, and Dust Vault. Once rules are separated from `input()` and `print()`,
code can play the game too.

## What should students build on?

### Beginner projects

Copy a file from `beginner/` and change it directly:

- add another choice;
- add an item;
- make a choice appear only after something happened;
- add a second ending;
- add score or health.

### Intermediate projects

Copy an intermediate version and add:

- a new room;
- an NPC interaction;
- a puzzle;
- another enemy;
- a new item that changes which choices are legal;
- another ending.

`intermediate/version3.py` is the best starting point for a substantial game
that should still be understandable as one file.

### Advanced projects

Do **not** copy the engine. Copy a world module such as:

```text
advanced/adventure/worlds/dust_vault.py
```

A world supplies ordinary Python data and functions such as:

- `ROOMS`;
- `ENEMIES`;
- `describe_extra()`;
- `get_choices()`;
- `handle_action()`;
- `on_enemy_defeated()`.

The advanced architecture deliberately prefers normal Python functions and
composition over an invented effects language or a large inheritance tree.

## Architecture rules worth preserving

1. **Game rules own state.** UI code should not decide whether an enemy is
   defeated or whether a door opens.
2. **Presentation observes state.** Art can look at the current room; it should
   not make gameplay happen.
3. **World code may be specific.** A one-off puzzle can be a normal Python
   branch instead of a framework class.
4. **Create abstractions after repetition appears.** More classes do not make a
   program more advanced by themselves.
5. **Prefer composition and functions before inheritance.** Most story variants
   are data plus behavior.

For instructor-facing rationale and lesson prompts, see `TEACHING_GUIDE.md`.
