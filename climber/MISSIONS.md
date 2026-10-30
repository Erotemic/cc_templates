# Student missions

These are suggestions, **not** mandatory rules. Rename the game and change
the art first. Then pick the feature that sounds most interesting to you.
Open `climber/student.py` and search for `MISSION`.

## Mission 0 — Make it yours (5 minutes)

1. Change `GAME_TITLE`. Run it and look at the window title and HUD.
2. Change `HERO_COLOR` using three numbers between 0 and 255.
3. Change `TOWER_SEED` and watch the tower layout change.
4. Choose your theme: a wizard tower? climbing a giant tree? a space elevator?

**Think:** if two programs use the same `TOWER_SEED`, why do they get the
same ledges even though the tower is infinite?

## Mission 1 — Wall jumps

**Goal:** while airborne against the side of the tower, press Space to launch
up and away from that wall.

1. Walk to the left or right wall, jump once, then press jump again.
2. Change `if False and jump_pressed:` to `if True and jump_pressed:`
   inside `try_wall_jump()` to inspect `wall_side`, `on_ground`, and `vy`.
3. Write an `if` that checks for a pressed jump, a wall, and no ground.
4. Make `player.vy` negative (up); use `player.wall_side` to decide the
   horizontal push direction. Hint: `-player.wall_side * 360`.
5. Return `True` when a wall jump succeeds, and `False` otherwise.
   The engine uses `True` to preserve the sideways push for 0.16 seconds.

**Stretch:** add a variable tracking an extra jump granted after a wall jump.
Can you decide when it should be consumed and refilled?

## Mission 2 — Ladders are a state

**Goal:** press W while overlapping a ladder to climb, and S to climb down.

1. Walk under a ladder: it is drawn, but W doesn't climb yet.
2. Turn on the diagnostic in `update_ladder_state()` and see what
   `touching_ladder` means.
3. A ladder should only work when the player actually overlaps it.
4. Set `player.climbing = True` when the player is touching a ladder and
   pressing up or down. Set it to `False` otherwise.
5. The engine already disables gravity and sets vertical speed when
   `player.climbing` is True. Why must gravity be turned off?

**Stretch:** once climbing begins, let the player hang motionless when they
release W and S. Make jumping detach from the ladder.

## Mission 3 — Enemy patrols

**Goal:** the pink creatures move back and forth on their ledges.

1. Look at the stationary enemies higher up the tower.
2. Change `if False:` to `if True:` in `move_enemy()` to see their data.
3. Add distance to `enemy.x` each frame. Distance is speed times seconds.
4. Reverse `enemy.direction` when it crosses `left_limit` or `right_limit`.
5. Prevent the enemy from walking off the platform. You may want to clamp
   its position back inside the two limits.

**Stretch:** different enemy speeds, pauses at the edges, and different
behaviors based on the player's distance.

## Mission 4 — The rising floor

**Goal:** a purple danger floor chases the player toward the tower top.

1. In `move_rising_floor()`, turn on the diagnostic to see `hazard_y`.
2. Try subtracting `20 * seconds` from `game.hazard_y` each frame.
3. Watch the danger rise. Why is moving up *subtracting* from Y?
4. Tune the speed. Is the game fun if you stop and think for 30 seconds?
5. Try a rubber band: look at the distance between the danger and the
   player. Move faster when the danger is much farther below the player.

**Stretch:** a difficulty curve that rises faster at higher tiers, a warning
when danger is close, or a safe checkpoint every 20 tiers.

## Mission 5 — Moving platforms

**Goal:** make the **blue ledges with arrows** move back and forth. The first
blue ledge is on tier 2, so you can see it near the beginning of the game.

The game already draws these ledges, treats them as solid from above, and
**carries the player horizontally** when the ledge moves. Only their movement
is unfinished. Open `climber/student.py` and find `move_platform()`.

1. Stand on a blue ledge. Notice that it is currently still.
2. Switch the diagnostic to `if True:` for a few seconds. Find its current
   `x`, `left_limit`, `right_limit`, `direction`, and `speed`.
3. Make a small change each frame: add `platform.direction * platform.speed
   * seconds` to `platform.x`. Run it. Does it keep going?
4. Now handle the right limit: if `platform.x >= platform.right_limit`, set
   its direction to `-1`. Handle the left limit similarly with `+1`.
5. If you notice a jitter at an edge, also clamp `platform.x` to the limit
   when it reaches that edge. Why does this matter with large frame times?
6. Stand on the moving ledge and let go of the movement keys. Confirm that
   you are carried horizontally. Jump and see what changes.

**Stretch:** change speed based on tier. Make platforms reverse on a timer,
or pause at the edges. Moving **vertically** is a harder challenge: you'll
also have to update the player's vertical carrying behavior in `engine.py`.

## Mission 6 — A more interesting infinite tower generator

**Goal:** keep the tower infinite and reachable, but stop having every pair
of ledges exactly 100 pixels apart vertically.

Open `platform_height_offset()` in `climber/student.py`. The tower calls it
from `world.platform_y()`, which already supplies a smoothly varying noise
number between about -1 and +1. No new Python package is needed.

1. Notice that the function currently returns `0.0`. This makes the height
   formula exactly `GROUND_Y - tier * 100` for every tier.
2. Turn on the diagnostic for the first eight tiers and see how `noise`
   changes. Which tiers get a positive or negative number?
3. Return `16 * noise` instead of zero. This makes height offsets vary,
   while keeping the main staircase close to its guaranteed route.
4. Walk or climb and watch the different heights. Compare the gap between
   tier 4 and tier 5; why is it not always 100 anymore?
5. Experiment with the multiplier and speed of the noise in
   `world.platform_y()`. Keep the offset around **-20 to +20 pixels**.
   The normal jump reaches about 159 pixels, and the engine looks for
   platforms close to its expected 100-pixel grid.
6. Run the tests. If you create a much larger or faster pattern, add
   tests that check every consecutive jump is still possible.

**Harder challenge:** look at `world.platform_center()`, which chooses the
platform's left/right position using **two layers of noise**. Change their
speeds and amplitudes, but keep successive tier centers within about 110
pixels. Try combining horizontal variation with tier height. Then look at
`world.side_platform()` and invent optional side routes or different widths.
You can create harder-looking sections while preserving **one reachable
main route** through the tower.

**Important generator idea:** you must get the same tier every time you ask
for it, no matter how far the camera has moved. Calling `random.random()`
each frame is not enough. Use the provided deterministic noise, or make a
new random number generator seeded from `TOWER_SEED` **and the tier number**.
Don't loop through all earlier tiers to find the height of tier 100,000.

## Mission 7 — Pickups and rewards

**Goal:** decide what happens when the player touches a placed pickup.

1. Climb until you see a gold pickup. The tower already places them for you.
2. In `collect_pickup()`, turn on the diagnostic and touch one.
3. First set `pickup.collected = True` so the item disappears.
4. Add `game.pickups_collected += 1` to count it in the HUD.
5. Add a reward. A simple first version is `game.hearts = min(3, game.hearts + 1)`.
6. Try different item ideas by checking `pickup.kind` (`"gem"` or `"heart"`).

**Stretch:** invent checkpoints, temporary power-ups, or different scores.

## Mission 8 — Remember a fall, then roast the player's return

**Goal:** build a simple event-and-state system. A big fall happens **now**;
the heckler says "You're back?" **later**, after you climb back up. You
must write both the detection and the delayed reaction yourself.

Start in `climber/student.py`, inside `update_heckler_comeback()`.
The engine calls this function on **every frame** and gives you four empty
memory slots in `game`:

| Variable | What it remembers |
| --- | --- |
| `game.peak_player_y` | Your highest point so far (smaller Y = higher) |
| `game.comeback_pending` | `True` means you fell and the heckler remembers |
| `game.comeback_peak_y` | The height to reach before the comeback line |
| `game.fall_count` | How many significant falls you have noticed |

### Part A — Detect the event and save a flag

1. Turn on the `if False:` debug print in the function; run, climb a few
   platforms, then fall. Observe `player_y` (current) and `peak_y` (best).
2. Update `game.peak_player_y` with the **smaller** of its existing value
   and `game.player.y`. Hint: Python's `min()` is useful here.
3. Calculate `game.player.y - game.peak_player_y`. When this distance
   reaches **180 pixels**, the player has fallen significantly. A normal
   jump reaches only about 159 pixels above its takeoff point, so just
   jumping and landing should not arm the event.
4. But don't count it every frame! Require `not game.comeback_pending`
   before marking a new fall. On the first detection, save
   `game.comeback_pending = True`, save the previous peak into
   `game.comeback_peak_y`, and increase `game.fall_count` by one.
5. Test **falling without returning**. The flag should stay True, the
   heckler elevator should not move downward, and no comeback line should
   appear yet.

### Part B — Respond later using the saved state

6. In the **same function**, add another `if` using
   `game.comeback_pending`. It must only succeed once you are near the
   remembered height. Hint: compare `game.player.y` with
   `game.comeback_peak_y + 35`. To require a reunion with the elevator,
   also compare `abs(game.player.y - heckler.y)` with `200`.
7. When you return, **clear** `game.comeback_pending = False` and
   `return heckler_comeback_line(game, heckler)` to ask the heckler to
   speak. At the end of the function, `return None` on frames when
   nothing should be said.
8. Try a complete sequence: climb, drop two or more floors, climb back,
   listen to the taunt. Now keep standing there. It should not repeat.
   Drop again and return: it should happen a second time.

**Think about the state machine:** before the fall the player is in the
`READY` state. A large fall moves to `WAITING_FOR_RETURN`; climbing back
triggers the speech event and moves back to `READY`. The saved boolean is
how the code remembers something that happened hundreds of frames ago.

**Bonus:** change the phrase in `heckler_comeback_line()`. Make a different
joke after two falls by checking `game.fall_count`. Try writing down the
sequence of flag values on paper before turning on the debug print.

The engine handles speech animation, sound and speech-bubble placement. It
**does not** implement the detection or memory logic. Until you complete
this mission, falling and returning will **not** trigger a comeback line.

## Bonus — Heckler elevator lines

The heckler on the right wall already rides up with the player. Edit
`student.heckler_line()` to change the regular taunts. It already checks the
player's best tier, failures, and collected pickups. Each distinct line
speaks once; the bubble types and then closes. Add more conditions or
rewrite the character completely.

## Bonus — Make your own sounds

**Goal:** make the game play a melody **you** composed. Sound is generated
in Python at startup: no music downloads or WAV files are needed.

1. Play the game. Listen for the background music and the sound when you jump.
   Press **M** to mute and unmute.
2. Open `climber/synth.py` and find `make_music()`. The `chords` list
   contains four groups: each has chord notes, a bass note, and a short
   **melody** (the last tuple).
3. Change **one note number** in a melody (for example, `74` to `76`).
   These are MIDI pitch numbers: **higher numbers mean higher notes**.
4. Restart `python main.py`. You should hear the changed note immediately.
5. Change several notes, or change `beat = 60 / 112` to a different tempo.
   Can you make the melody feel calm, tense, or triumphant?
6. For sound effects, find `make_effect()`. The jump effect increases its
   `hz` (pitch) over time. Change `510` to `200` and listen again.

**How it works:** `make_music()` creates a list of audio samples,
`to_pcm16()` converts them into bytes, and `audio.py` hands the bytes to
`pygame.mixer.Sound(buffer=...)`. No file is created. If you're curious,
turn on your own diagnostic with `if True: print(frequency(69))` and
check that MIDI pitch 69 is 440 Hz. Turn the print off afterward.

**Stretch:** write a second short melody, introduce a new sound event, or
change the soundtrack after every ten tiers climbed. This requires changes
in both the simulation (which emits events) and the playback layer.

## After the missions: choose an independent challenge

When you're ready for less guidance, open **`climber/challenge.py`**. The
challenges there describe a player-visible goal and concepts to consider,
but do **not** tell you which function to fill in. Finding, changing, and
connecting the code is part of the exercise. You can also invent your own.

Explain what you changed in a short README written in your own words.

