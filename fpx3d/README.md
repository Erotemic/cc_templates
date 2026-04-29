# First Person 3D Game

A bright first-person 3D Python game built directly with Panda3D, a real Python
game engine.

Run through the cavern, collect every crystal, avoid the red hazard pads, and
jump through the portal before time runs out.

## Install

```bash
pip install -e .
```

## Run

```bash
crystal-cavern-dash
```

or:

```bash
python -m fpx3d
```

## Controls

- `WASD`: move
- `Mouse`: look around
- `Space`: jump
- `Left Shift`: sprint
- `R`: restart
- `Q` or `Esc`: quit

## One-Hour Student Mods

Open `src/fpx3d/game.py` and try one of these:

- Add another crystal to `CRYSTAL_SPOTS`.
- Move a hazard in `HAZARD_PADS`.
- Make the timer longer or shorter with `ROUND_TIME_SECONDS`.
- Change the arena colors in `THEME`.
- Turn music on or off with `AUDIO_ENABLED`.
- Change `MUSIC_VOLUME` or `SFX_VOLUME`.
- Add a new jump pad to `JUMP_PADS`.
- Make crystals worth more points in `collect_crystal`.
- Add another landmark tower in `LANDMARKS`.

The best first mod is adding one crystal, then moving the portal farther away.

## Why Panda3D?

Panda3D is more professional than a beginner wrapper, but it still lets students
write normal Python. This template keeps the engine details in helper functions
so the first edits can be simple level and rule changes.

## Music and Sound

The game generates its own background music and sound effects from Python code,
similar to the RPG template in this repository. The first run writes WAV files to
`~/.cache/fpx3d/audio/`, then Panda3D plays them from there.
