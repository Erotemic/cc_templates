# Guided missions: build your own Prism Vault

Start in **`fpx3d/student.py`**. Each unfinished function already has a
walkthrough, an `if False:` diagnostic that you can turn on, and a TODO.
Your task is to fill in just the student function, run the game, and see
the change. You can choose the missions in any order.

A game is a loop. At 60 FPS it runs about 60 times each second. If a
function runs every frame, multiplying by `seconds` keeps movement steady
on different computers. Changing state now affects what happens later.

## First five minutes: take ownership

Change `YOUR_VAULT_NAME` in `student.py`. Run the game and see the new
name in the HUD. Then find a prism in `world.CORES` and change its
position, or change its color. The numbers in a 3D position are
`(x, y, z)` where **z is height**.

## Mission 1: Golden gem rewards

Required prisms already count toward opening the exit. Bonus golden gems
are optional. Stand on a balcony to get one or find the one near the south
wall. Currently the gem disappears but has no benefit.

**Goal:** give the player an actual reward when touching one.

Think about: the difference between an event (touching a gem) and a
persistent value (score, health, or time). An item should be rewarded
once, not every frame. The engine already removes it once; you decide
the reward. Test it by collecting two gems in one run.

## Mission 2: Patrol drone

Two pink sentries are already visible, but they don't move. Make one travel
back and forth between its limits. Speed is distance *per second*; direction
is +1 or -1. The diagnostic shows you those numbers. Try moving before you
implement the turn-around rules; notice what goes wrong.

**Goal:** make the movement repeat forever without escaping the bounds.

## Mission 3: Pulse scanner

The scanner circle in the center is harmless until you switch it on. The
engine already knows how to hurt the player if `scanner.active` is True.
Make it dangerous during only part of a repeating cycle, so the player
can learn when to cross it safely.

**Goal:** a visibly predictable on/off hazard with a safe interval.

## Mission 4: Checkpoints

The blue pads are waiting to be activated. Make standing on one remember
its position as the respawn point. Test it by taking three hits and observing
where you return. What state must persist even after the player moves away?

**Goal:** the latest visited checkpoint is used after running out of health.

## Mission 5: Sprint stamina

Sprint currently never runs out, although the HUD already shows 100%. Make
it decrease while Shift is held and recover when the player walks normally.
Test whether sprint stops at zero, then rest until it recovers.

**Goal:** the meter stays between 0 and 100 and runs at the same rate at
different frame rates.

## Mission 6: Moving lift

A blue hovering platform already supports collision and carries the player
when it changes position. You only need to make its `x` move inside a
range, then turn around at either end. Try riding it without touching WASD.

**Goal:** a smooth back-and-forth ride with no falling off at the ends.

## Mission 7: Give the clockwork guard a Markov brain

Find the little purple-and-gold robot in the southern courtyard. It is
already built out of 3D geometry and hurts you if you touch it, but it
stands still. You will make it occasionally pick a new behavior.

A **state** is what the guard is doing *right now*: `idle`, `north`,
`south`, `east`, or `west`. A **transition** chooses what the next state
should be. In a simple Markov chain, that next choice depends on the
**current** state, not the guard's entire history.

Open `guardian_markov()` in `fpx3d/student.py`.

1. Begin by making its decision timer count down. When the timer expires,
   choose a state and reset it to a small number of seconds. Nothing needs
   to change on frames when the timer hasn't expired.
2. Start with a random choice among the five states, then improve it:
   change the **probabilities depending on the current state**. Perhaps
   an idling robot is likely to keep idling, and a moving robot is likely
   to turn or continue forward.
3. Translate the chosen state into `move_x` and `move_y` values. The
   engine takes care of actually walking, so this doesn't require
   Panda3D math or code for collision avoidance.
4. Try different probabilities. Can you make a cautious guard? A restless
   guard? A guard that changes direction only every few seconds?

**Goal:** the guard sometimes pauses, sometimes wanders, and behaves
according to the state-transition rules *you* chose. Its seeded random
number generator makes your experiments repeatable.

## Mission 8: Make the guard chase you within a radius

Once you understand the state machine, add a second behavior: chasing.
This is also possible without completing Mission 7; otherwise the robot
will simply stand still when the player is too far away.

Open `guardian_chase()` in `fpx3d/student.py`.

1. Observe how the player and guard each have an `(x, y)` position.
   Calculate the difference in their positions and their distance.
2. Compare that distance to `guardian.detection_radius`. The faint circle
   around the guard helps show the range in the world.
3. **Inside** the radius, request movement toward the player. Return
   `True` to tell the engine that chase mode is active.
4. **Outside** the radius, return `False` so the Markov behavior (if you
   implemented it) can take over. The eyes change color while chasing.
5. Test approaching and escaping. What happens if the player jumps onto
   a ledge? How could you make the chase fairer or more interesting?

**Goal:** the robot notices you nearby and pursues you, then goes back
to normal once you get away. The engine prevents it from walking through
the arena walls; your code controls *decisions*, not rendering.

## Bonus: Make the Curator talk

The `curator_line()` function is working from the start. For each event
(jump, prism collected, hurt, checkpoint, portal open, win) you can return
a string to replace the default message. Add a condition using something
the game remembers, such as `state.cores_collected`, `state.hearts`, or
`state.time_left`.

## Bonus: make the vault soundtrack yours

The music already works; it is composed from numbers in `fpx3d/audio.py`.
Find `make_music()` and its four groups of chord notes and melody notes.
Change ONE melody number (higher numbers make a higher note), restart the
program, and compare. Try a different tempo by changing `BEAT = 60 / 112`.

Panda3D reads audio from small cached WAV files in your home directory, but
nothing is checked into the project. The cache name changes automatically
when you edit the Python audio source, so the game plays the new version.

## After guided work: independent challenges

Open `fpx3d/challenge.py`, or run `python -m fpx3d.challenge`.
It presents goals and concepts but no names of functions to fill in.
You choose which files, data, and methods to change. For each new feature:
show that it works, explain a design decision, and tell someone about a
bug you encountered.
