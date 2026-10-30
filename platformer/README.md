# Little Platformer

A small **raw pygame** game with three starting levels, collected stars,
locked exits, generated music, and short sound effects. You can play and win
without finishing the student exercises. **No sound files or image assets**
are needed; pygame drawing primitives and Python create everything.

## Play

```bash
cd platformer
python main.py
```

If pygame isn't installed, use your school's existing pygame environment or
`python -m pip install pygame-ce`.

| Key | Action |
| --- | --- |
| A/D or Left/Right | Move |
| Space, **X**, W, or Up | Jump |
| M | Mute/unmute music and effects |
| R | Restart the current room (or from level 1 after winning) |
| Esc | Quit |

Each starting level has stars, a door, a spring, and an enemy. Collect all
stars and touch the door to advance. The original game ends after level 3;
**creating a fourth level is one of the student missions**.

## Guided versus independent work

Open **`platformer/student.py`** first. It has **eleven guided missions**,
numbered from 1 to 11, with explanations, numbered walkthroughs, a debug
print you can enable, and a success check. Mission 0 is simply to rename
the game and recolor the hero.

The first two missions are the original **spring bounce** and **enemy
patrol**. New guided missions invite you to create a fourth level, make
the robot talk when hit or collecting stars, animate transitions, build a
boss fight, compose a second song, add a zoomed following camera, implement
double jumps, animate blue platforms, and create a switch that reveals a
bonus star.

The game already draws the blue platform, red switch, and dormant crowned
boss. You decide how they behave; the level is completable before you do.
A following camera, level transition, hero speech, and second song do not
activate until you edit their guided hooks.

See [MISSIONS.md](MISSIONS.md) for the mission checklist and recommended
order. **`platformer/challenge.py`** contains eight independent goals with
concept hints rather than step-by-step code. Run `python -m
platformer.challenge` to see them.

## Where to look

```text
main.py                  Run the game
platformer/level.py       Editable 24x15 ASCII level maps
platformer/student.py     Eleven guided mission walkthroughs and hooks
platformer/challenge.py   Independent feature goals
platformer/game.py        Keyboard, game events, drawing and optional camera
platformer/sprites.py     Player movement, jumping, gravity, collisions
platformer/sound.py       Music synthesis and mixer playback
platformer/settings.py    Dimensions, physics constants and colors
MISSIONS.md              Mission checklist
TEACHER_GUIDE.md          Classroom pacing and design constraints
```

You can examine and edit any file; the guided hooks just give you a
manageable place to start. To add a level, edit the ASCII maps in
`level.py`. To compose new music, supply MIDI note numbers (no WAV files).

## Tests

```bash
python -m unittest discover -s tests -v
python -m platformer.challenge
python main.py --frames 3 --screenshot screenshot.png
```

The game starts as a fixed-screen platformer. A zooming camera is a **student
project**, not extra complexity required to understand the basic game.
