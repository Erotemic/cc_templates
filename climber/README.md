# Infinity Climber — your game, your code

Climb a tower that **never ends**. The platforms bend around a smooth noise
pattern. Walking, jumping, falling, collisions, and camera scrolling already
work. **You get to invent eight of the mechanics.** This is real pygame, not a
special game-making framework.

## Start in five minutes

```bash
cd climber
python main.py
```

If `pygame` is missing:

```bash
python -m pip install pygame-ce
python main.py
```

Or use an existing installation of regular `pygame`. There is **no** SVG
library, Cairo, image downloader, NumPy, or Pillow dependency. The original
soundtrack and sound effects are synthesized directly from Python code when
pygame starts; there are **no audio assets** to download, generate, or check
into Git. If there is no working sound device, the game still runs silently.

First, open **`climber/student.py`**. Change `GAME_TITLE`, `HERO_COLOR`, and
`TOWER_SEED`. Run it again. This is your tower now: decide its name, colors,
and theme.

## Controls

| Key | Effect |
| --- | --- |
| A/D or Left/Right | Walk |
| Space or Z | Jump |
| W/S or Up/Down | Climb ladders **after** mission 2 |
| H | Show/hide the eight missions |
| M | Mute/unmute music and sounds |
| R | Restart |
| Esc | Quit |

Drag the window edges to resize it. The HUD is beneath the gameplay rather
than covering the ground. You can climb as far as you want; only nearby
platforms are generated.

## Your eight missions

All eight live in **`climber/student.py`**. Each has a step-by-step guide,
example expressions, a TODO, and a diagnostic
`if False:` which you can flip to `if True:` while experimenting.

1. **Wall jump:** check whether you're airborne and touching a side wall;
   launch the player up and away. The engine already supports a short
   horizontal wall-push timer.
2. **Ladders:** use `touching_ladder`, `controls.up`, and `controls.down`
   to set `player.climbing`. The engine already moves climbing players.
3. **Enemy patrols:** move an enemy from one side of its platform to the
   other; reverse direction at its limits.
4. **Rising floor:** subtract from `game.hazard_y` as time passes. If the
   purple danger overtakes the player, the run restarts. Can you make it
   chase the player like a rubber band instead of moving at constant speed?
5. **Moving platforms:** the blue ledges already render and support
   collision and carrying. You supply their back-and-forth movement.
6. **Better tower heights:** the baseline is deliberately a 100-pixel grid.
   Use deterministic smooth noise to vary platform heights without making
   jumps impossible; advanced players can improve the X generator too.
7. **Pickups:** gold treasure is already placed in the tower. Decide what
   happens when the player grabs one by editing `collect_pickup()`.
8. **Heckler comeback event:** implement the *event itself*: detect a big
   fall, save a `comeback_pending` flag, then trigger dialogue only when you
   return to the elevator. The starter provides state fields but no solution.

You can do these in **any order**. See [MISSIONS.md](MISSIONS.md) for a
small-step walkthrough and [TEACHER_GUIDE.md](TEACHER_GUIDE.md) for the
instructor's plan.

## After the guided missions: independent challenges

Open **`climber/challenge.py`** for open-ended projects: breaking platforms,
checkpoints, new enemy types, secret rooms, tower regions, a rival climber,
and more. It also has code-detective questions about how the game works.

`student.py` gives you a named function and a detailed walkthrough.
`challenge.py` gives you a **goal and concepts to think about**, but no
prewritten solution or hooked-up function. Finding where code belongs is
part of those challenges. You can write new functions in `challenge.py`
if you like, but they will not run in the game until **you connect them**.

Read the challenges directly in the file, or print them in your terminal:

```bash
python -m climber.challenge
```

Pick **one** challenge, make a small working version, and explain how you
know it works. You don't need to finish the whole list.


## Where things live

```text
main.py                 Run the game
climber/student.py       Guided missions with step-by-step instructions
climber/challenge.py     Independent challenges and code-detective prompts
climber/game.py          The real pygame window, keyboard, and loop
climber/engine.py        Player movement, gravity, collisions, camera
climber/world.py         Infinite platforms, ladders, and placed pickups
climber/art.py           Graphics, pickups, heckler, background, HUD
climber/audio.py         Play music/effects using pygame.mixer
climber/synth.py         Original melodies and sound effects made from code
climber/settings.py      The physics constants
```

**Not a locked engine:** you can edit every file. Start with `student.py`
so you can finish a mechanic without sorting through the window code first.
When you're ready to find the right code on your own, pick a challenge in
`challenge.py`. The regular pygame event loop is still in `game.py`.


## Heckler conversations

The heckler rides upward on the right wall and stays at that height if you
fall. Speech appears letter by letter in a bubble attached to the elevator,
with little synthesized mumble notes during typing. After the line finishes,
it lingers briefly and disappears. A line is not repeated every frame.
More taunts unlock when you reach higher tiers.

To customize the heckler, edit `heckler_line()` in `climber/student.py`.
Mission 8 asks **you to program the fall-and-return event**. Right now
there is no automatic comeback dialogue. In `update_heckler_comeback()`,
notice a significant fall, set a state flag, then recognize the later
return and emit a dialogue line. The text is supplied as an example in
`heckler_comeback_line()`, but it cannot play until you implement the event.

## Music and sound

The starter includes an **original looping melody** and short sound effects
for jumping, landing, pickups, damage, restarting, every ten tiers climbed,
and the heckler's speech. Press
**M** to mute or unmute; the HUD displays the current sound status.
On startup, `climber/synth.py` uses Python's standard library to generate
short signed-16 audio buffers in memory. `climber/audio.py` feeds those bytes
to `pygame.mixer`. No WAV files, NumPy, conversion commands, or external tools
are needed. The music loops until you quit, and the game works if audio
initialization fails.

To compose your own music, edit the note numbers or rhythms in
`climber/synth.py` and restart. See **Bonus: Make your own sounds** in
[MISSIONS.md](MISSIONS.md) for a walkthrough.


## Testing / teacher tools

Run these without pygame installed:

```bash
python main.py --headless --frames 240
python -m unittest discover -s tests -v
```

With pygame installed, the tests also open a dummy SDL window and render
frames, catching constructor/startup mistakes. To take a screenshot:

```bash
python main.py --frames 3 --screenshot screenshot.png
```

You can turn this folder into **your own project repository** by copying
`climber/` outside `cc_templates` and running `git init` in the new folder.
