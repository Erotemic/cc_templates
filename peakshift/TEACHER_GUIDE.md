# Peakshift — teacher guide

## Goal and differentiation

Peakshift uses the feel of a precision movement game to motivate Python, not
to demand perfect reflexes. The core is already playable, so students can
focus on specific programs rather than struggling to write a game loop.

Unlike the existing Infinity Climber, levels are **authored**. A lesson can
refer to exactly the same gap, crystal, or platform on every computer. Like
UnderCode, `Room` records and a dictionary express map layout and links.
For student code, the narrow hooks in `student.py` keep entry cost low.

## Suggested progression

| Period | Goals | Evidence |
| --- | --- | --- |
| 1 (45 min) | Play / customize / berry scoring / timer | New title, working counter, explanation of `+=` |
| 2 (45 min) | Crystals and moving platforms | Conditional refill; platform reverses at both edges |
| 3 (45 min) | Breakable blocks, wind, or a first custom room | A mechanic with a clear test and revised behavior |
| 4–5 (optional) | Author/playtest room 5, independent challenge | External playtest, map and code review |

Assignments are **choices**, not prerequisites. A beginner can finish
missions 0/1/6; an experienced student can pursue map design or engine
extensions. Group work: one student authors levels, another programs a
mechanic, a third playtests and writes a short bug report.

## Student success checks

- One berry increments the displayed score once, not every animation frame.
- A crystal refills only when needed; one dash can become two with a crystal.
- Moving platform stays inside its x-limits and carries the player.
- Crumbling tile falls away after standing long enough, and comes back on death.
- Wind applies a noticeable horizontal push only while inside the zone.
- Timer advances in seconds, not frames.
- A new room loads through an explicit `next_room` link and is finishable.

Tests in `tests/` check **baseline engine behavior and hook wiring**; they do
not reject unimplemented missions as failures. After a student finishes one
mission, manually or automatically check the corresponding success criterion.

## Map design guidance

The view displays 24 columns × 15 rows, with 32 pixels per tile. Rooms have
24 columns and 20–31 authored rows; the camera follows the climber vertically.
Students may author any height from 15 rows upward. Spawns,
exits, checkpoints, platform runs, jump-through ledges, and hazards use letters. The validator
reports map-shape errors with row and column references, and unknown
`next_room` destinations by name. This is a *syntactic* validator; no
algorithm can guarantee a platforming level feels fair. Have students play
their rooms and obtain peer feedback.

The starter includes four distinct rooms: Trailhead (an early spike and gap,
then two climbable cliffs), Switchbacks (a 19-tile-high narrow wall-jump
shaft with two resting ledges), Skybridge (two true gaps, a tall central
pillar, and a horizontal dash), and Lantern Ridge (three successive towers,
long falls, and two checkpoints). All rock faces have real collision geometry;
missing bottom rows do not introduce an invisible floor. The player can
hold **C** against a rock face and press **up/down** to climb, with a finite
stamina pool replenished on landing. Jumping off a wall works without grabbing.
Climb and camera code are supplied, not student prerequisites. Optional mechanics are not
needed to unlock exits.

## Files and concepts

Students begin in `student.py`; guided mission functions explain their
parameters, outputs, and TODOs. `levels.py` is data modeling; `physics.py`
contains coordinate geometry, speed, collision, and state; `app.py` is event
handling and the game loop; `art.py` draws shapes; `audio.py` synthesizes an
original tune and events. Advanced students can open those files once they
have experimented with the narrow hooks.

For a 10-minute demonstration: print `player.x`, `player.vx`, and `seconds`
for a handful of frames. Predict the next position based on velocity and
elapsed time. Draw an arrow for positive and negative Y; negative Y velocity
means moving **up** because screen Y increases downward. Then compare with
a dash and discuss why speed is measured per second rather than per frame.

## Reliability and accessibility

Launch without a network connection once pygame is installed. The game
uses basic system fonts and pygame drawing; missing audio devices are fine.
No student exercise requires a separate asset pipeline or image generator.
`python main.py --headless --frames 240` requires no pygame whatsoever.

`python -m unittest discover -s tests -v` exercises map validation, movement,
spikes, checkpoints, room transitions, hooks, and a real CLI launch. Run
`python main.py --frames 3 --screenshot screenshot.png` to check rendering in
a pygame-capable environment. The app scales to resized windows without
changing collision coordinates.

Allow students to use `--room` to practice a mechanic rather than forcing a
full campaign replay. Students who cannot perform fast inputs can still
learn from the headless simulation, level authoring, and mission tests.
A further accessibility extension is configurable speed or assist mode.

## Playtest the authored routes

`tests/test_physics.py` includes recorded input sequences that complete each
room without dying and without solving student TODOs. These are reachability
regressions, not a substitute for first-time student playtesting. The tests
also verify that empty gaps cause a true fall, cliff-grabbing can lift the
player, and grip stamina runs out.

Room-building questions to give students: How far apart can two facing walls
be while remaining wall-jumpable? Where would you place a checkpoint after a
long climb? Can you use a pit to teach dash timing without making the level
impossible for someone who has not yet coded crystal refills? Let students
change the geometry and compare their predictions with actual play.
