# Instructor guide: Prism Vault (fpx3d)

## The goal

A student asked why they shouldn't start from raw pygame or a blank 3D
window. They *can*, but keyboard input, camera rotation, collision,
gravity, asset creation and scene construction consume the class before
there's time to create anything they can call their own.

This is normal Panda3D, not a separate student-only scripting language.
The starter handles the foundations while reserving **eight real gameplay
mechanics** for the student. Even the Panda3D details are readable and
editable as their experience grows.

The initial game is **playable without completing a mission**: six prisms
unlock an exit, a timer counts down, pads boost or hurt, and crystals spin
above their pedestals. Colored archways mark regions, wall-mounted lights help navigation, and
the HUD points toward the next prism. There are optional raised balconies and bonuses so students
can explore rather than just running to one objective.

## One hour

| Minutes | Activity | Student owns |
| --- | --- | --- |
| 0–10 | Explore, understand the objective, describe favorite mechanic | Playtest and feedback |
| 10–15 | Rename the vault and move/recolor a crystal | Immediate creative decision |
| 15–35 | Choose one guided mission, read its inputs and outputs | First implementation |
| 35–50 | Turn on diagnostic, predict, test, fix | Debugging |
| 50–60 | Demonstrate what changed, choose next goal | Explain and plan |

Suggested first missions: golden gem rewards (event + counter) or drone
patrols (update + boundary conditions). Checkpoints teach state that must
be remembered across later events. Scanner timing teaches modulo and
periodic behavior. Stamina teaches `dt`, clamping, and balancing. The lift
introduces carrying and collision without requiring the student to write
full collision code. The new clockwork robot then introduces **probabilistic
state transitions** (Mission 7) and **distance-based chasing** (Mission 8).
Both are visible immediately as a stationary character with a detection
circle, so the student's code causes an obvious change.

The printed diagnostics are optional and default off. Encourage the student
to predict the print before turning it on. Don't demand that every mission
be implemented; let the student pick the part that interests them.

## Why the code is divided this way

```text
Panda3D window (game.py)            handle keyboard and mouse
  -> game state and rules (engine.py)     jump, collide, collect, win
      -> student.py                       student-written behavior
  -> world.py                       locations and 3D object data
  -> art.py                         geometry and HUD
  -> audio.py                       original sound synthesis
```

There is a critical separation between `world.py` and `art.py`: the same
plain Python box specs determine both what is drawn and which surfaces
block walking or allow landing. This avoids mismatched invisible walls
while keeping decorative art from trapping the camera. `engine.py` can be imported, tested, and debugged without
opening a Panda3D window or installing graphics packages.

The active code is divided by responsibility, not buried inside one large
`game.py`. `old-versions/` remains in the repo for historical comparison
but is not imported.

## Forgiving level geometry and recovery

The prior layout let players snag on corner approximations and raised boxes:
side collision treated balconies and the lift as walls. This version
separates **lateral collision** from **landing surfaces**. The four outer
walls are the only `world.WALK_BLOCKERS`; `world.LANDING_PLATFORMS` still
allows the player to jump onto raised ledges. The player has a circular
footprint, movement is split into small steps, and diagonal movement slides
along boundaries. Balconies now sit above standing head height, and tall
arch columns, corner towers, and opaque guide posts are moved to the edges
of the walkable room. This preserves visual landmarks without confusing
3D collision with decorations.

**Backspace** invokes `recover_position()`: it returns the player to the
saved checkpoint without resetting collectibles or the timer. That keeps
experiments with modified `world.py` from ending in a frustrating restart.
The student still owns activating new checkpoints in Mission 4.

## Robot exercises: decisions, then movement

There is one visible 3D Clockwork Watcher near the starting area. Its body,
face, glowing eyes, and detection ring are made out of existing Panda3D
cube/line geometry. It is stationary by default; close contact hurts, but
it does not chase until a student implements it.

The two new hooks are intentionally narrow:

- `guardian_markov(guardian, seconds)` chooses a persistent state from
  idle/north/south/east/west and sets the requested movement direction.
  The guardian has a seeded `random.Random`, a state string, and a decision
  timer. Encourage probability weights based on the *previous* state.
- `guardian_chase(guardian, player, seconds)` decides whether the player is
  inside a radius. When it returns `True`, chase movement overrides the
  Markov mission. When it returns `False`, the Markov hook runs. Both are
  unfinished in the starter.

In either case, the engine handles `speed * seconds`, normalizes diagonal
movement, prevents escape from the room, and keeps the 3D art synchronized.
The first task is a state-transition lesson, not a 3D collision lesson;
the second introduces distance, Pythagoras, and an if/else policy.

For a shorter class, start with a two-state Markov chain (idle and east)
and add more directions only when that works. If the student finds random
weighting confusing, let them first choose from states uniformly, then
ask how to favor one transition from another.

## Independent challenges

`fpx3d/challenge.py` contains 17 feature/design goals and five code-reading
questions. Unlike `student.py`, these are **not already connected to game
callbacks**. Hints are conceptual: events, state, geometry, decision rules,
feedback. Students must locate the right code themselves and explain why
they chose that location. One goal can yield many implementations.

Try asking these before giving a filename:

- What should the player see when the feature works?
- What should the game remember between frames?
- Does the game already contain a similar system?
- How would you test the smallest version of that feature?

Code-detective questions reward reading the real engine, even when no new
feature is written. For more advanced students, move beyond `student.py`
and encourage direct edits to `engine.py`, `art.py`, and `world.py`.

## Running on school computers

Keep the existing single graphical dependency, `panda3d>=1.10.15`. No SVG,
Cairo, image model, texture package, or third-party sound synthesizer is
needed. Music and effects are synthesized with Python and cached as WAV
files in `~/.cache/fpx3d/audio/` on first playback. These are never
checked into the project and never required at development time.
If audio can't initialize, the game continues without it.

The game supports keyboard-based looking (arrow keys) as well as mouse look,
so students with difficult trackpads can still navigate. Tab releases the
mouse pointer; clicking the game recaptures it.

For debugging and CI, run the simulation without Panda3D:

```bash
cd fpx3d
python -m unittest discover -s tests -v
python main.py --headless --frames 240
```

When Panda3D is installed, run a graphical smoke test as well:

```bash
python main.py --frames 10 --screenshot screenshot.png
```

The pure-Python tests check baseline win/lose rules and extension points
without prescribing one particular student solution. Optional challenges
may change the game substantially; treat tests as helpful regression checks,
not as constraints on the student's design.
