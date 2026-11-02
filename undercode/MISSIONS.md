# Make UnderCode yours

The normal game works. The sprite exercise has its own opt-in practice mode;
you can leave it unfinished and still play normally. Make one small change,
test it, then explain it.

## 0. Face the direction you walk

**Task:** show a different view when the Courier walks up, down, left or right.
Open **`undercode/student_sprites.py`** and run:

```bash
python main.py --sprite-task
python main.py --check-sprites
```

The exercise starts with only the down-facing case. Complete
`choose_player_view(facing)`, returning `"up"`, `"down"`, `"left"`, or `"right"`.
The drawing code already has all four views: your job is to choose one.

1. Read `x, y = facing`. On a screen, positive x means right and positive y
   means down. Predict the view for `(0, -1)` and `(-1, 0)` before coding.
2. Add conditions for up, left and right. The down case is worked for you.
3. Walk in all four directions, then stop. The idle character should keep
   looking in the last direction: the world already remembers `facing`.
4. Handle diagonal movement by choosing the axis with the largest absolute
   value. When magnitudes tie, use the vertical view. `(0, 0)` falls back to down.
5. Run `--check-sprites` until all eight checks pass. It exits with a failure
   status while the exercise is unfinished; ordinary `--check` remains independent.

**Explain:** why use facing rather than position? Why should releasing keys
not reset the view? What happens if the player faces a wall?

**Stretch:** customize each drawing in `art.courier`, or add two walking frames
per view using `time` and `walking`. Keep drawing separate from collision rules.
The working reference is `undercode/sprites.py`; the normal game uses it.

## 0b. Tell a story before adding mechanics

Follow [STORY_GUIDE.md](STORY_GUIDE.md). Change the Story Keeper's writing in
`studio.json`, move the bookmark by moving its letter, and test both choices.
Then copy the small example into a new JSON file and link a door to its named
entrance. Add an ending that changes a later conversation with a flag.

**Check:** travel both ways, read/close dialogue, try the locked door before
and after collecting its item, and restart to confirm the story starts fresh.
Run `--check` after every edit. No coordinate pairs or Python are needed.

**Stretch:** copy `warm_light` in `student_mechanics.py`, change its rule, and
connect its registry name to a trigger or `on_interact` hook in the map legend.

## 1. A character with a point of view

Open `undercode/student.py` and edit Echo's `name`, `description`, `greeting`,
`goodbye` and ACT replies. Keep the key `echo` for this first experiment, so its
room placement continues to work.

```bash
python main.py --encounter echo
```

Make one ACT helpful, one neutral and one funny. `calm` controls how much an ACT
builds understanding. The total needed is `calm_needed` on the character.

**Check:** can a player understand how to reach SPARE from the writing? Does a
combat finish still work? Does Echo have a distinct voice?

## 2. A readable attack pattern

In `RippleLanes`, change `spawn_interval`, projectile speed, colors, or which
lanes are left open. The interval must stay positive. `warmup` shows a warning
before a projectile becomes dangerous.

```bash
python main.py --practice ripples --seed 7
python main.py --check
```

`dt` is elapsed **seconds**, not frames. `arena.width` and `arena.height` describe
the local playfield; do not hard-code window coordinates into a pattern.

**Check:** can you show where the player can safely move before each wave? Try
the same seed twice. A difficult pattern should still be readable and possible.

## 3. A character that changes their reply

Add a selection rule to `choose_echo_pattern`. `context` contains `turn`,
`enemy_hp`, `enemy_max_hp` and `calm`.

For example, import `ClockworkHops` from `.patterns` and return it after a turn
threshold, while returning `RippleLanes()` before that threshold. Or make the
pattern gentler when the player has built understanding.

**Check:** each selection must return a **new instance**. Reusing one pattern
object carries old cooldowns into the next turn. Describe the rule in words
before writing the condition. `--check` exercises several turn contexts.

## 4. Your own special defense

Create another `DefensePattern` class in `student.py`. Copy the shape of
`RippleLanes`, then replace the actual mechanic. A few ideas:

- Alternating left/right projectiles with one clear safe lane.
- A beam that warns first, then sweeps a small area.
- A gravity/jump sequence with an occasional high projectile to stand under.
- A shield sequence whose direction order follows a musical phrase.

Register a preview key in `EXTRA_PATTERNS` and connect the factory to a character
through `choose_pattern`. Adding a registry entry alone makes the preview
available; it does not put the pattern into someone's battle.

**Check:** ensure hazards expire, warnings precede danger, and the hint matches
the control mode. Test losing, retrying and returning to the menu.

## 5. A new technique for the player

Read `TimingStrike` and `RhythmStrike` in `attacks.py`. Both expose the same
contract while implementing different timing rules.

Start with a faster/slower focus strike, then make a different target layout or
beat sequence. Keep the result in `[0, 1]`. A missed input must finish eventually
and score zero; one beat must not award points repeatedly when Z is spammed.

Register a new `Weapon` in `content.py` and select it with Tab in the overworld.
Damage stays in `battle.py`; the sequence supplies accuracy, not direct HP edits.

**Check:** compare no input, early input, perfect input, late input and repeated
input. Can another character use your technique without special engine code?

## 6. A new neighbor and a new place

Copy a character definition, choose a unique key, and add it to
`EXTRA_CHARACTERS`. In a level's JSON map, draw a new letter and give it a legend:

```json
"N": {"kind": "character", "id": "my_neighbor", "character": "my_character_key"}
```

Add a new level file and doors using named markers if the story needs another
place. The character key chooses the battle definition; `id` remembers this
neighbor's outcome. Use `"requires": "spared:my_neighbor"` in a later dialogue
branch or on a door. See [STORY_GUIDE.md](STORY_GUIDE.md) for examples.

Run `--check` for malformed maps, duplicate IDs, invalid doors, unknown symbols
and pattern/strike factory errors.

**Check:** go there on foot, decline the invitation, accept it, spare the
character, return, and speak again. Repeat with a combat finish and with leaving
practice. Do transitions preserve the right player position and story state?

## Independent projects

Choose a goal and find the right connection points yourself: a dash with a
cooldown, a parry window, a moving arena boundary, a multi-stage boss, a party
member, a scrolling overworld, accessible remappable controls, a nested dialogue editor,
or a save format with a version number. Keep the smallest playable version and
add a regression check that would catch a real mistake in your new rule.
