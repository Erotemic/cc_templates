# Peakshift — build a precision platformer in Python

**Peakshift** is a small, playable, Celeste-inspired movement game with **authored
rooms** rather than an infinite tower. Its purpose is to teach high-school
students real Python by letting them change interesting mechanics of a game
that already works. This is an independent classroom starter, not a Celeste
clone: the rooms, character, visuals, and generated music are original.

You start with working **running, variable-height jumping, coyote time, jump
buffering, wall sliding, wall jumping, eight-direction dashing, spikes,
checkpoints, death/respawn, and four connected authored rooms**. You can finish
all four rooms without completing a single coding assignment. Optional
mechanics are visible in the maps but await student code.

## Play in five minutes

```bash
cd peakshift
python -m pip install pygame-ce
python main.py
```

If pygame is already available, skip installation. Everything is drawn in
pygame; there are **no image files, sample downloads, audio files, or extra
packages**. The original soundtrack is generated from Python on startup. It
runs silently when audio is unavailable.

| Key | Action |
| --- | --- |
| A / D or left / right | Run |
| Space or Z | Jump; hold for higher jumps |
| X or Shift | Dash once until landing (aim with WASD or arrows) |
| W / S or up / down | Aim dash vertically or diagonally |
| H | Controls / help |
| P | Pause |
| M | Mute |
| R | Restart current room; after winning, restart campaign |
| Esc | Quit |

Resize the window freely. The HUD is below the level so it never obscures
spikes or your feet.

## What you get to program

Open **`peakshift/student.py`**. The game calls these six functions already:

| Mission | What you change | Python ideas |
| --- | --- | --- |
| 0. Make it yours | Name / hero / scarf / sky colors | values, tuples |
| 1. Berry score | Add to a score when a berry is touched | variables, `+=` |
| 2. Dash crystals | Refill an empty dash charge | `if`, `return`, booleans |
| 3. Moving platform | Travel and reverse between limits | velocity × time, conditions |
| 4. Crumble tiles | Break after standing for a while | timers, state |
| 5. Wind | Push horizontally in wind zones | functions, input/output |
| 6. Speedrun timer | Add elapsed seconds | accumulators, frame rate |
| 7. Your own level | Add an authored room and link its exit | strings, lists, dictionaries |

The **first six mechanics start unfinished on purpose**. Berries disappear,
crystals sparkle, moving platforms hold you up, brown ledges support the player, wind
has a visual effect, and the timer reads 0.0 until you add code. None of these
features blocks finishing the campaign. Each guided function includes a
short walkthrough, diagnostic print, and a way to check success. You can do
them in any order.

## Authored levels, like UnderCode

Open **`peakshift/levels.py`**. Every room has a `Room` record with a name,
`tiles` (15 rows of 24 characters), a gameplay hint, and an explicit
`next_room` destination. The `ROOMS` dictionary connects the rooms into a
course. To make a new level, copy one Room, edit its letter map, and connect
its key. See the exact symbol legend at the top of `levels.py`.

```text
..P......^^...........G.
########################
```

`P` is the spawn; `^` are spikes; `G` is the exit; `#` is rock; `=` is a jump-through ledge. Other symbols
include a checkpoint, refill crystal, berry, moving platform, crumble tile,
and wind. The checker reports the room, row, and column of map mistakes.

Levels are **fixed and authored**, not procedural. You can deliberately
place challenges around specific mechanics, then playtest whether each route
can actually be completed. A fast retry matters more than punishing lives:
death immediately respawns you at the last checkpoint.

## Files to explore

```text
main.py                  Run the game; optional testing switches
peakshift/student.py      All guided missions (start here)
peakshift/levels.py       Four editable, authored rooms and map checker
peakshift/physics.py      Velocity, jumping, dash, collision, respawn
peakshift/art.py          Shapes, mountain backgrounds, HUD, effects
peakshift/audio.py        Synthesized song and game sounds
peakshift/app.py          Keys, window, loop, drawing, headless mode
peakshift/settings.py     Movement constants (all pixels and seconds)
peakshift/challenge.py    Open-ended extension ideas, no starter functions
MISSIONS.md              Classroom-ready guided missions
TEACHER_GUIDE.md         Lesson sequencing, constraints, grading ideas
```

This is **ordinary pygame**, not a custom visual game-creation language. If
you want, edit any file. Start with the narrow hooks so your first changes
don't require understanding the event loop. Later, investigate the engine
for an independent challenge.

## Test without a window

```bash
python main.py --headless --frames 240
python -m unittest discover -s tests -v
python -m peakshift.challenge
```

The headless simulation and all unit tests work **without pygame**. To open
a particular room or capture a picture when pygame is installed:

```bash
python main.py --room divide
python main.py --frames 3 --screenshot screenshot.png
```

## Learning notes

This is optimized for first- and second-year Python students, not for
reproducing every advanced Celeste technique. Most early edits touch just
one function and one concept. It is okay to change constants and create
new rooms without finishing all missions. For a harder capstone, pick an
independent challenge from `peakshift/challenge.py` and explain how you
tested it.
