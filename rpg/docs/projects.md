# Project Directions After the Common Lessons

Students do not need to follow one feature ladder after the common sequence.
Choose a direction that gives the programming concepts a purpose.

## Game mechanics / boss design

Build conditional attacks, support moves, statuses, target-selection rules, or
a multi-phase boss. Use named scenarios and fixed seeds to demonstrate each
phase deliberately.

## Character art

There are two intentionally different art paths.

**Python procedural art:** use repeated shapes, symmetry, coordinates, helper
functions, and loops to create a coherent character family. Refactor repeated
drawing ideas into functions only after the repetition is visible.

**SVG vector art:** edit `student_game/assets/sprites/space_pirate.svg` directly
in a text editor or vector editor. This path introduces vector geometry,
layering, fill/stroke styling, groups, and transforms without requiring students
to express every visual change as Python. Preview it with
`python render_character.py space_pirate`.

## Effects and mathematics

Start with piecewise paths and coordinate functions. Extend into sine waves,
triangle/square waves, damping, harmonics, or other functions when appropriate.
`cycles=1` consistently means one full period for periodic built-in paths.

## Sound

Investigate frequency, duration, envelopes, waveforms, and repetition through
audible changes. Students can treat sound generation as another expression- and
function-based system.

## Experiments and balance

Use `python simulate.py --scenario balance --runs 50`. Make one change, predict
its effect, reuse the seed range, and compare wins, rounds, remaining HP, damage,
and scripted damage/healing command counts. These counts include commands
whose attacks miss; they describe commands returned, not automatic code coverage.

## Software engineering / engine exploration

Follow a question into the engine. Examples:

- Where does `damage(10)` become an HP change?
- How does guarding alter the calculation?
- Where is a target declared legal?
- Why are behavior functions given read-only views?

Change one engine rule, write or update a test, and explain the path from
student API to engine implementation.
