# Prism Vault — your first-person 3D game

You wake in a glowing observatory. **Find six colored prisms** scattered
through the three parts of the vault, avoid the red danger pads and sentry
crystals, and reach the portal at the **north end** before time runs out.
A curious purple-and-gold clockwork robot watches you from the southern
courtyard. It stands still, waiting for someone to program its brain.
Explore the side balconies with spring pads if you want bonus treasure.

This is a real **Panda3D** game. It uses keyboard/mouse input, a first-person
camera, 3D boxes and gems, jumping, gravity, collisions, animated effects,
and original synthesized music. **No textures or downloaded game assets.**
The default game is playable before you implement any missions.

## Run

From this directory:

```bash
python main.py
```

If Panda3D is not installed:

```bash
python -m pip install 'panda3d>=1.10.15'
python main.py
```

It is the same dependency as the previous `fpx3d` project, with no extra
graphics or audio packages. The game works without a network connection.

For classroom testing on a machine **without Panda3D**, use:

```bash
python main.py --headless --frames 240
python -m unittest discover -s tests -v
```

## Controls

| Key | Action |
| --- | --- |
| **W A S D** | Move through the 3D world |
| **Mouse** | Look around |
| **Arrow keys** | Alternative to mouse look |
| **Space** | Jump |
| **Shift** | Sprint (unlimited until Mission 5) |
| **Tab** | Release/capture mouse, or click to recapture |
| **H** | Show instructions; pauses while open |
| **M** | Mute/unmute music and sounds |
| **R** | Restart the run |
| **Backspace** | Return to your checkpoint if you get stuck (keep progress) |
| **Q / Escape** | Quit |

Use the **objective hint at the bottom left** to find the nearest remaining
prism. The hint tells you its distance and whether it's ahead, behind, left,
or right. The portal only opens after you collect all six required prisms.

### What already works

- A colorful three-section vault with wide paths, wall-mounted guide lights,
  walk-under balconies, sentry crystals, and an animated portal
- Collecting six prisms, tracking progress, unlocking the portal, winning
- Jumping and gravity, forgiving circular wall collision, diagonal movement
  normalization, and raised platforms you can pass beneath
- Spring pads, dangerous red floor pads, three hearts, a timer, and respawn
- Original looping synthesizer music and sound effects, generated from code
- Optional golden bonus gems, checkpoint pads, scanner, drones, and a lift
- A clockwork robot character (already drawn, stationary until programmed)

The final group is deliberately **incomplete** as game mechanics: the
objects are present and rendered, but their rewards, movement, or timing
are exercises for you to implement.

## Navigating the geometry

The layout is intentionally more forgiving than a traditional 3D maze.
Only the **four outer walls** stop sideways motion; large interior
structures and glowing decorations are placed away from major walking
routes. Raised balconies, steps, and the lift are **one-way platforms**:
you can walk underneath them and land on top after jumping. The player
has a circular footprint instead of a square that snags on corners.

If you edit the world and accidentally end up somewhere inaccessible,
press **Backspace** to return to your current checkpoint. Your collected
prisms and timer progress are preserved. Checkpoint activation itself is
still Mission 4; before then, Backspace returns to the starting point.

The active geometry is editable in `world.py`: `BOXES` describes what is
drawn, `WALK_BLOCKERS` identifies the four outer walls, and
`LANDING_PLATFORMS` identifies solid surfaces you can land on. If you later
want to introduce a real interior wall, create a box with
`blocks_walking=True`. Otherwise it stays passable at walking height. This
keeps the visuals and game rules in sync while leaving the starter open.

## Make it your game

First open **`fpx3d/student.py`**. Change `YOUR_VAULT_NAME`. Then change a
color or a crystal location in **`fpx3d/world.py`** and play again.

There are **eight guided missions** with detailed walkthroughs and diagnostic
prints in `student.py`:

1. Give optional golden gems a reward.
2. Make stationary security drones patrol.
3. Make the inactive scanner switch on and off.
4. Turn decorative checkpoint pads into real respawn points.
5. Make the sprint energy bar drain and refill.
6. Make a hovering lift move and carry the player.
7. Give the clockwork robot a Markov-style brain: change its walking state
   occasionally, using probabilities based on its previous state.
8. Make the robot chase you within a configurable detection radius, then
   return to its normal behavior when you escape.

These functions are **already called by the game**. You fill in just the
mechanics. There's also a working `curator_line()` bonus, where you can
write your own dialogue based on game events.

Read [MISSIONS.md](MISSIONS.md) for guided explanations and
[TEACHER_GUIDE.md](TEACHER_GUIDE.md) for a suggested teaching progression.

### When you want less help

Open **`fpx3d/challenge.py`** for **17 independent challenges** and five
code-detective questions. The challenges describe what the player should
experience and concepts you may need, **not where or how to implement it**.

```bash
python -m fpx3d.challenge
```

Examples: a locked side door, a talking statue, timed stealth, a generated
vault, a rival, or a boss. The challenge module does not run in the game
unless you connect code to it yourself. That's part of the exercise.

## Where things live

```text
main.py                Launch (no package installation required)
fpx3d/launch.py        Command line and Panda3D-free headless mode
fpx3d/student.py       Eight guided coding missions (START HERE)
fpx3d/challenge.py     Open-ended goals and code-detective questions
fpx3d/world.py         Objects and locations in the 3D vault
fpx3d/settings.py      Movement speeds, physics, time limit
fpx3d/engine.py        Game state, movement, collision, win conditions
fpx3d/art.py           Geometry, lighting, animations, user interface
fpx3d/game.py          Panda3D window, keyboard, mouse, main game loop
fpx3d/audio.py         Procedural music and effects
```

Most gameplay testing doesn't need Panda3D: `engine.py`, `world.py`, and
`student.py` are ordinary Python. There is no need to touch Panda3D's
vertex-buffer code until you feel ready to explore graphics programming.

Music is generated from Python and temporarily cached in
`~/.cache/fpx3d/audio/` because Panda3D loads sounds from file paths.
**No `.wav` assets are checked into the source repository.**

## Testing

```bash
python -m unittest discover -s tests -v
python main.py --headless --frames 240
```

With Panda3D installed you can also run a short graphical smoke test:

```bash
python main.py --frames 10 --screenshot screenshot.png
```

The game is designed as an editable starter, not a locked game framework.
Every file is yours to change. The `old-versions/` directory is preserved
for historical reference; it is not imported by the new game.
