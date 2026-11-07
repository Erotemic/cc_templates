# Peakshift — student missions

Play the four rooms once. Then open `peakshift/student.py`. You can do the
missions in any order. Each is a real function called by the game, not a fake
example. Don't change five things at once; run the game after each edit.

## Start: make the game your own (5 minutes)

Change `GAME_TITLE`, `HERO_COLOR`, `SCARF_COLOR`, and `SKY_COLOR`. Each color
has three integer values, red/green/blue, between 0 and 255. Predict what
changing a value will do. Run the game to check.

## 1. Berry collector (10 minutes)

Find the berry at the start of Trailhead. Touch it: it disappears but your
`BERRIES` counter stays 0. Open `collect_berry(game)`. What does `game.berries`
mean? Write the one line that increments it. Demonstrate that touching a berry
twice does not score twice. Try awarding points instead of counting berries.

**Concepts:** variables, assignment, addition, events.

## 2. Dash crystals (15 minutes)

Play Switchbacks with `python main.py --room switchbacks`. Dash once in the
air; the dash indicator reads `USED`. The lavender diamond is a crystal.
Open `refill_dash_from_crystal(player)`: give back a charge **only** when
`player.dashes == 0`; return `True` in that case. Test a dash, a crystal,
then a second dash before landing. What happens if you touch a crystal with
a full dash? Choose the behavior intentionally.

**Concepts:** conditions, comparison, truth values, return values.

## 3. Moving platform (20 minutes)

Start at `--room divide`. The blue bridge is solid from above, but does not
move yet. Open `move_platform(platform, seconds)`. Move by `speed * seconds`
with a signed `direction`. Reverse direction at both limits and clamp
position so the platform never drifts out of its track. Ride it, then jump
off. Check that the bridge isn't moving faster on a slow computer.

**Concepts:** state, signed numbers, inequalities, speed × time.

## 4. Crumbling ledge (20 minutes)

Start at `--room ridge`. Brown ledges support the player from above. In
`update_crumble(block, seconds, standing)`, accumulate seconds only while
standing on them. When the timer exceeds 0.45 seconds, set `broken` to
`True`. Make a prediction: what happens if you leave before the timer
finishes? Try both a reset-on-leave and a pause-on-leave rule. Why does each
feel different?

**Concepts:** booleans, timers, state machines.

## 5. Wind tunnel (10 minutes)

The turquoise wind marker in Lantern Ridge is currently visual-only. Write a
function that returns 700 when `inside_wind` is true and zero when it is
false. The engine already multiplies that acceleration by time. What does a
negative return value do? Why is returning a value different from directly
moving the hero?

**Concepts:** functions, parameters, outputs, sign.

## 6. Speedrun clock (5 minutes)

At the lower-right of the HUD, TIME stays 0.0 by default. Add seconds into
`game.elapsed`. Why is `elapsed += 1` wrong? Why does the correct clock run
similarly at 30 FPS and 60 FPS? Try beating your time.

**Concepts:** incremental changes, units, frame independence.

## 7. Author a fifth room (30–50 minutes)

Copy an existing `Room` in `levels.py`, give it a new name, and edit its tile
rows. Every row has exactly 24 characters; there are exactly 15 rows. Include
one `P` and one `G`. Add it to `ROOMS` with a new key. Connect the previous
last room's `next_room` to your key. Make this course fair with the mechanics
that work **before** the optional missions. Try the new room with
`python main.py --room your_new_key` (replace with your key).

Try **two playtests**: your own run and someone else's first attempt. What
could they infer from the level without reading your code? Can they finish
without using optional crystals, wind, or moving platforms?

**Concepts:** strings, data modeling, dictionaries, debugging, iteration.

## Independent work

Use `python -m peakshift.challenge` for capstones with no prewired function
or walkthrough. Your submission should show the game running, one snippet
of the code you changed, and a short explanation of how you tested it.
