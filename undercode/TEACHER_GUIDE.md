# Teach ownership of the engine

UnderCode assumes variables, conditionals, loops and functions; classes may be
new. Start with a player-visible problem, then show the minimal state and code
needed to explain it. The engine is part of the curriculum. Students may edit
any file and should eventually locate an extension without a preselected hook.

## Two independent learning routes

World students start with `--overworld`, `student_overworld.py`, and the frame
trace in ENGINE_GUIDE. Encounter students start with `--encounter echo`, its
phase diagram, and `student_encounters.py`. `--practice pulse` isolates a defense.
They share a Player record and an explicit coordinator, not each other's models.
A syntax error in a room authoring file does not stop an encounter exercise, and
an unfinished opponent does not stop walking and story work. Accepting a linked
encounter deliberately asks the coordinator to load the other system.

A peaceful Person has its own art/writing and no Opponent dependency. All rooms
remain together in `student_world.py`. Opponent definitions and their examples
are in the encounter catalog, with editable Echo in `student_encounters.py`.
The named records use keyword arguments, so their data can be read at each call.
Mouse mission 6 is independent of the pattern tasks. The adapter supplies logical
click coordinates; the student implements hit testing. Ask them to predict a hit,
a miss, a boundary, and a scrolled index before enabling the mouse behavior.

## A first hour

| Time | Activity | Evidence of understanding |
| --- | --- | --- |
| 0–10 | Play, rename, change a story line; choose world or encounters | Identify one desired behavior |
| 10–20 | Predict one frame or turn and inspect F2 | Explain input versus persistent state |
| 20–40 | Implement one mission in small steps | Show a visible addition and a failing case |
| 40–50 | Read the caller and a nearby engine rule | Explain who owns the state |
| 50–60 | Change the rule creatively and describe the next project | Transfer the idea beyond the recipe |

Do not require all tasks or hand a student the entire architecture at once.
Use their feature to motivate the next concept. For an advanced student, begin
with a challenge and have them discover the engine boundaries through the work.

## Scaffolding that fades

1. **Worked trace:** walk through one input → update → drawing path. Ask for a
   prediction before revealing the next line. ENGINE_GUIDE supplies three traces.
2. **Guided implementation:** use the inline inputs/walkthrough/TODO/checks.
   Facing teaches conditionals, sprint teaches units, healing teaches events,
   Pulse teaches per-instance state, tactics teaches functions returning objects, and mouse buttons teach a loop
   over geometry records plus the difference between index zero and no result.
3. **Partial specification:** change writing after a choice, add a new room,
   combine conditions, or vary a pattern without exact step-by-step code.
4. **Independent extension:** CHALLENGES names a goal and questions, not a callback.
   Locating the state and connecting the new behavior are part of the task.

Avoid accepting a pasted solution as the only evidence. Ask the student to
predict an edge case, identify the caller, change a requirement, and explain
what would go wrong if a relevant line were removed. A diagnostic is useful
only if they can say what value they expect before running it.

## Whole-engine reading

Start at the relevant engine's short update method; follow named steps rather
than reading every drawing primitive. Modules document ownership and call paths.
Comments explain timing, coordinate systems, ordering, and reasons for guards.
A comment restating an assignment is less useful than explaining its consequence.

The central concepts are ordinary Python: records for data; methods operating
on an instance; enums for a finite set of phases; functions passed as callbacks;
and a factory constructing a new object. Drawing helpers share a UI base class
only for text/panel reuse. There is no scene framework or event bus to learn.

Encourage students to keep keywords on project-owned calls, choose names with
units/meaning, and make side effects visible. Pygame's own drawing API sometimes
uses positional parameters; document that geometry rather than wrapping every
library function in another abstraction.

## Assessment and checks

`--check` checks content and the engines. Add `--overworld` for maps only or
`--encounter echo` for encounters only. It intentionally invokes pattern factories.
`--check-exercise NAME` runs the actual student's function; failed checks are
expected before a mission is complete. They check behavior rather than source
spelling. Students designing a different rule should explain and update its
exercise acceptance examples accordingly.

The regression suite checks engine behavior, input presses/holds, independent
mode launches, route outcomes, rendering, sound and genuine custom story rules.
Some tests inject completed instructor examples to establish the wiring. Passing
those tests does not mean the student implemented the feature. The progress
checker never substitutes a teacher solution.

`teacher/solutions.py` is for instructor comparison after an attempt. Gameplay
never imports it. You may omit teacher material from a play-only handout; keep
it with the tests for regression work. Debug output/checkers can demonstrate
completion; a student explanation and a transfer task demonstrate understanding.

## Acceptance for an independent student project

Ask the student to demonstrate that they can trace one frame, add a peaceful
person and linked room, build an isolated defense, explain a remembered flag,
and add one rule beyond the supplied TODOs. They need not preserve the supplied
characters or complete the whole mission list. Credit clear reasoning and a
small working design, including evidence for a limitation.

## School deployment

Copy the whole project folder and run main.py using the editor's existing
Python 3.10+ interpreter. Regular pygame or pygame-ce works; install only one
because they share the pygame import name. No external art generation, system
fonts, SVG/Cairo, NumPy, Pillow or network connection is required at runtime.

A desktop is required for interactive play. Audio can be absent; use --mute to
skip opening a device. Use --headless --mute --frames 60 for automated checks.
For offline installation, obtain pygame wheels on a matching OS/Python, transfer
them, and use pip's --no-index/--find-links options. Check your actual school
machines locally even when Linux tests pass.

R clears this run's state; it does not reload source. Stop and relaunch after
editing. Original code, art/writing and generated music use the included license.
