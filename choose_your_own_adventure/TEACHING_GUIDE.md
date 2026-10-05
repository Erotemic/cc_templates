# Instructor guide

## Teaching objective

The repository shows a path from ordinary Python control flow to a reusable game
architecture **without making world-building progressively harder**. The
filesystem is part of the lesson:

1. **Beginner:** ordinary control flow and functions, no custom classes.
2. **Intermediate:** structured data, objects, state ownership, and a larger
   self-contained program.
3. **Advanced:** modules, a reusable library, multiple frontends, presentation,
   and multiple worlds.
4. **Capstone:** full-size authored games on a more capable engine, while adding
   an ordinary room or story choice remains a data-editing task.

The numbering restarts inside each level. A student can also stop at any level
and build a substantial project there.

## A curriculum-wide authoring rule

From intermediate onward, **rooms should own ordinary story choices**.

A student adding:

- another room;
- another exit;
- a descriptive interaction;
- a branch that prints text;

should not have to modify engine dispatch code. New engine code is justified
when the student intentionally invents a new reusable mechanic.

This is both pedagogically useful and representative of real data-driven game
architecture.

## Beginner

### Version 1 — trace one loop

Ask students to identify persistent state, changing state, choice construction,
and where a selected choice changes the game.

A useful bug exercise is why menu validation checks `1 <= number`: Python's
`list[-1]` makes the reason concrete.

### Version 2 — extract functions

Diff against version 1. The story did not change. Discuss parameters, return
values, repeated jobs, and when a function should mutate state.

Do not introduce classes yet.

## Intermediate

### Version 1 — separate data and behavior

Focus on `Player`, `ROOMS`, action functions, and functions stored in
`ACTION_HANDLERS`. A room may also contain a simple data-only choice with
`text` and `result`; a handler is only needed for a real mechanic.

### Version 2 — one object owns runtime state

The core API is:

```python
Game.describe()
Game.choices()
Game.apply(action)
```

The console loop stays outside `Game`. `RoomChoice` gives students a direct
place to add story content without extending `Game.apply()`.

A useful exercise is to write a tiny robot player or test that wins without
calling `input()`.

### Version 3 — scale the same ideas

This adds quest flags, inventory, conditional choices, combat, a locked path,
and win/loss state, while staying in one file. `RoomChoice` still handles simple
story interactions.

The architecture remains intentionally direct. Combat is not a hierarchy of
mode classes, and story actions are not a class hierarchy of effects.

## Advanced

### Version 1 — modules are justified by reuse

Compare `intermediate/version3.py` with:

- `advanced/adventure/core.py`;
- `advanced/adventure/worlds/star_crystal.py`;
- `advanced/adventure/ui/console.py`.

The lesson is not “more files are better.” The lesson is that multiple programs
now reuse these responsibilities.

`RoomChoice` remains available after the split, so modularization does not make
ordinary content harder to author.

### Version 2 — second frontend

The Textual UI is synchronous from the game's point of view:
button → `game.apply()` → redraw.

This avoids teaching threads, monkey-patched `input()`, stdout interception, and
queues as if they were inherent to GUI architecture.

### Version 3 — presentation observes state

ASCII art may inspect the room or current enemy, but it does not control game
outcomes.

### Version 4 — prove the reuse

Dust Vault uses the same engine and console UI while supplying different rooms,
quest conditions, item logic, and combat content.

## Capstone

Capstone exists because a teaching example and a game children actually want to
explore do not have to be the same size.

The two capstone worlds preserve the authored content from the original deep
versions rather than replacing them with demonstration-sized substitutes:

- Star Crystal: the full location graph, items, NPCs, dialogue topics, trades,
  riddles, features, gates, encounters, and story branches.
- Dust Vault: the full station and planetary maps, items, NPCs, dialogue,
  criminal/bounty paths, encounters, equipment, trades, expedition gates, and
  multiple endings.

The engine is separated into descriptively named modules under
`capstone/engine/`; there is deliberately no module called `rich.py`. The
capstone also restores the strongest presentation work from the original line:
a direct Textual frontend, complete Star Crystal scene/character art, and a new
full Dust Vault art pass. Unlike the original v5-v8 bridge, the UI does not
need threads, patched `input()`, stdout capture, or queues because the cleaned
engine already exposes choices and results directly.

The UI progression is still pedagogically useful: `snapshot()` demonstrates a
read-only presentation model, `OptionList` demonstrates event-driven input,
and the art selector demonstrates that presentation can react to semantic state
without causing game outcomes.

### Student extension zones

Each capstone world ends with `EXTRA_ROOMS` and `EXTRA_CHOICES`. Start students
there. A minimal room needs only a name, description, exits, and optional simple
choices. Missing item/NPC/feature collections normalize to empty collections.

This means a student can meaningfully expand a serious game before understanding
combat, dialogue, trading, encounters, or the effect interpreter.

### Fidelity and three reachability repairs

The original authored world records are preserved and regression-tested by a
canonical fingerprint. The port intentionally makes three narrow repairs where
the original prose described a path that the old interaction engine did not
actually expose:

1. Solving the Tower Guardian's riddle now lets the player take the Star
   Crystal nonviolently, as the guardian's success text says.
2. Solving Custodian Echo's riddle now lets the player take the Grave Core
   nonviolently, as its success text says.
3. Hearing Rafe's post-vault offer records that the offer was heard, making the
   authored landing-beacon corporate ending reachable.

These repairs change reachability, not the preserved authored world fields.
The capstone also preserves the original between-turn reaction model: bounty
encounters can fire after leaving an NPC, closing inventory, looting, or using a
feature instead of only after room-to-room movement. Dead NPCs expose only
corpse/loot interactions, enemy surrender keeps the original Spare/Kill branch,
and looting remains item-by-item. Sunmeadow's fountain is one deliberate polish
change: resting there is now a full heal, represented by an explicit data flag.
Tests exercise these contracts, the Star Crystal solution, Dust Vault clean/hot
station branches, and all three authored Dust Vault endings.

### Testing as a capstone topic

Testing is intentionally visible inside `capstone/tests/` instead of being only
in instructor infrastructure. This is a useful point to introduce several
software-engineering ideas with concrete failures students can understand:

- **boundary validation:** `engine/validation.py` catches broken world data at
  construction time;
- **state invariants:** combat, riddle, loot, surrender, inventory, and movement
  modes each have facts that must remain true after every action;
- **regression tests:** when a real bug is fixed, keep the smallest test that
  would have caught it;
- **scenario tests:** complete player journeys verify that individually correct
  mechanics compose into a working story;
- **simulation/fuzz testing:** `capstone/simulate.py` chooses only legal actions
  but combines them in many orders humans would not manually try;
- **dependency injection:** the console accepts input/output callables, so the
  actual frontend can be tested without a terminal;
- **optional dependencies:** core gameplay and all headless tests run without
  Textual, while `--ui textual` produces a clear installation error if the
  package is absent.

An instructive exercise is to deliberately break one invariant—for example,
leave `combat_npc_name` populated after combat—and observe that a state-machine
test or simulation catches it even if an ordinary playthrough appears fine.

## Concepts intentionally deferred

Do not add these merely to make the architecture look sophisticated:

- a class hierarchy for every state mutation;
- one engine subclass per game mode;
- one NPC subclass per personality;
- a second custom story language when ordinary data/functions are enough;
- event buses for local calls that are already clear;
- dependency-injection frameworks;
- async/threading solely to connect UI and game;
- inheritance where a function or data value is enough.

The capstone engine does interpret the original games' scripted effect records
because that is needed to preserve their existing content. Students do not need
to use that machinery for ordinary new rooms and choices.

## Student project tracks

### Story / writing

Add rooms, descriptive interactions, conversations, secrets, and branching
endings without changing mechanics.

### Programming

Add puzzles, status effects, reusable inventory behavior, procedural encounters,
or an automated player.

### UI / art

Improve an existing ASCII portrait/scene, add art for a student-created room,
modify the full capstone Textual layout, or create another frontend against the
same game API. Students can work entirely in `capstone/art/` without changing
mechanics.

### Engine

Add save/load, deterministic replay, or generalize a mechanic only after
multiple worlds demonstrate real repetition.


## Capstone state-machine case study: wolf, goat, and cabbage

The Hearthfield Farm delivery quest is intentionally a small state machine
inside a much larger game. `capstone/engine/river_crossing.py` is a good file to
read after students understand functions and dataclasses: the complete puzzle
state fits on one screen, transitions are pure, and unsafe transitions are
rejected before mutation. `capstone/tests/test_river_crossing.py` then shows the
same idea at two scales: exhaustively exploring reachable pure states and
driving the quest through the real `AdventureGame` API.

The teaching point is not the specific riddle. It is that a complicated game
can still contain small subsystems with crisp state, invariants, and tests.
