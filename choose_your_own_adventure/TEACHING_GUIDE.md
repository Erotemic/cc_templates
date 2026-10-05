# Instructor guide

## Teaching objective

The repository shows a path from ordinary Python control flow to a small,
transferable game architecture. The directory structure is part of the lesson:
students should not have to look past a reusable package before they have a
reason to learn what a package is.

The progression is therefore grouped by conceptual level:

1. **Beginner:** ordinary control flow and functions, no custom classes.
2. **Intermediate:** structured data, objects, state ownership, and a larger
   self-contained program.
3. **Advanced:** modules, a reusable library, multiple frontends, presentation,
   and multiple worlds.

The numbering restarts inside each level. This avoids implying that every
student must climb through nine files before starting a project.

## Beginner

### Version 1 — trace one loop

Ask students to identify:

- state that persists between turns;
- state that changes;
- where choices are built;
- where the selected choice changes state.

A useful bug exercise is to ask why menu validation checks `1 <= number` instead
of only `number <= len(choices)`. Python's `list[-1]` makes the answer concrete.

### Version 2 — extract functions

Diff against beginner version 1. The story did not change.

Good questions:

- Which repeated jobs became named functions?
- What information must a function receive as parameters?
- When should a function return a result instead of changing outer state?

Do not introduce classes yet.

## Intermediate

### Version 1 — separate data and behavior

Focus on:

- `Player` as a record of related state;
- `ROOMS` as data;
- action functions;
- functions as dictionary values in `ACTION_HANDLERS`.

This is an opportunity to teach that functions are values in Python without
requiring a framework.

### Version 2 — one object owns runtime state

The key API is:

```python
Game.describe()
Game.choices()
Game.apply(action)
```

The console loop stays outside `Game`.

A strong exercise is to write a tiny robot player or test that wins without
calling `input()`. This motivates backend/frontend separation before students
see a second UI.

### Version 3 — scale the same ideas

This is the first substantial game. It adds:

- quest flags;
- inventory;
- conditional choices;
- combat state;
- a locked path;
- win/loss state.

The architecture remains intentionally direct. Combat is not a hierarchy of
engine-state classes. Story actions are not `Effect` objects. World-specific
branches are allowed to be world-specific branches.

## Advanced

### Version 1 — modules are justified by reuse

The advanced level begins precisely where a library becomes useful. Compare
`intermediate/version3.py` with:

- `advanced/adventure/core.py`;
- `advanced/adventure/worlds/star_crystal.py`;
- `advanced/adventure/ui/console.py`.

The lesson is not "more files are better." The lesson is that multiple programs
will now reuse these responsibilities.

### Version 2 — second frontend

The Textual UI is synchronous from the game's point of view:
button → `game.apply()` → redraw.

This avoids teaching threads, monkey-patched `input()`, stdout interception, and
queues as if they were inherent to GUI architecture.

### Version 3 — presentation observes state

ASCII art may inspect the room or current enemy, but it does not control
outcomes. Rendering is not the authority for gameplay rules.

### Version 4 — prove the reuse

Dust Vault uses the same engine and console UI while supplying different rooms,
quest conditions, item logic, and combat content.

This is where students should feel the payoff of the package introduced in
advanced version 1.

## Concepts intentionally deferred

Do not add these merely to make the architecture look sophisticated:

- an `Effect` class hierarchy for every state mutation;
- one `Engine` subclass per game mode;
- one NPC subclass per personality;
- a custom story scripting language;
- event buses for local calls that are already clear;
- dependency-injection frameworks;
- async/threading solely to connect UI and game;
- inheritance where a function or data value is enough.

These can become legitimate later if a concrete requirement makes them useful.

## Student project tracks

After intermediate version 2, students do not all need the same destination.

### Story / writing track

- add rooms and branching endings;
- write conversations;
- create conditional choices based on flags.

### Programming track

- add a puzzle mechanic;
- create a reusable inventory helper;
- add status effects to combat;
- write an automated player or solver.

### UI / art track

- improve the console renderer;
- add ASCII scenes;
- modify the Textual layout;
- create another frontend against the same Game API.

### Engine track

- add a save/load representation;
- add deterministic randomness behind an injected RNG;
- generalize something only after two worlds genuinely repeat it.

The engine track should justify abstractions with concrete repetition rather
than design-pattern vocabulary alone.
