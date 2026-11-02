# Build the missing features

Run **`python main.py`**. Movement, rooms, conversations, battles and sound work.
The Courier always looks down, the Story Studio's light does not heal, and the
new Lantern Pulse defense has no sparks. **You implement those features.**
The game already calls your functions; finishing a TODO changes normal play.

Each mission has **YOUR INPUTS**, a **WALKTHROUGH**, diagnostics you can turn on,
and **TEST IT** checks directly beside its code. Work on one small step, run
again, and explain the result. No special exercise mode is needed.

## Mission 0 — Make it yours

Change `GAME_TITLE`, `PLAYER_NAME`, and Echo's writing in `undercode/student.py`.
Run again and find your changes. This is customization; the next four missions
ask you to implement behavior that is missing from the starter.

## Mission 1 — Face the direction you walk

**Open:** `undercode/student_sprites.py` → `choose_player_view(facing)`.
**Goal:** left, right and up walking gain their own views in the actual game.
The art already exists, but choosing its view is your job.

1. Run `python main.py`. Walk left, then up. Notice the face still looks down.
2. Read **YOUR INPUT** in the function. Set its diagnostic `if False:` to
   `if True:` briefly. Compare x and y while pressing each direction.
3. Write one condition for left: when x is negative, return `"left"`.
   Run the game. Confirm that you have added a visible feature.
4. Add right and up. Keep `return "down"` for the remaining direction.
5. Try diagonals. Use `abs(x)` and `abs(y)` to choose the strongest axis;
   ties choose vertical. The inline walkthrough explains where this belongs.
6. Run `python main.py --check-sprites`. All eight examples should pass.
   This command reports unfinished work; `--check` checks engine/content health.

**Test it:** all four directions, diagonal movement, stopping, and facing a wall.
Idle should keep the last view. `World` already remembers facing, so you do not
need to store another copy in the drawing code.

**Explain:** why use facing instead of position? Why is up a negative y?
**Stretch:** change each drawing in `art.courier`, or add walking frames.

## Mission 2 — Give a place an effect

**Open:** `undercode/student_mechanics.py` → `warm_light(world, obj)`.
**Goal:** entering the mint oval restores up to 3 HP and reports the actual gain.

1. Run `python main.py --level studio`. Walk onto the mint oval below the path.
   It is connected to your function, but its effect is unfinished.
2. Enable the diagnostic. Read the function's **YOUR INPUTS** section.
3. Store the player in a local variable. Call `player.heal(3)` and keep what
   it returns. The existing method caps HP; you supply when and why it is used.
4. Show the returned amount with `world.tell(...)` and an f-string.
5. Test at low HP, near maximum HP, and full HP. The inline walkthrough shows
   how to make a temporary low-HP experiment; remove the setup line afterward.

**Test it:** enter at 5/20 → 8/20; stand still → still 8/20; leave and return →
11/20. At 19/20 it reports 1, and at full HP it reports 0. The engine handles
entry detection; your function supplies the mechanic.

**Explain:** why use the returned healing amount rather than always saying 3?
**Stretch:** require a flag, charge a snack, or make the light work once per run.

## Mission 3 — Create a warned defense

**Open:** `undercode/student.py` → `LanternPulse.update(arena, dt)`.
**Goal:** sparks warn at the left edge, then travel right at timed intervals.

1. Run `python main.py --practice pulse`. At first this arena has no hazards.
2. Enable the diagnostic and read **YOUR INPUTS**. Subtract `dt` from
   `self.cooldown`; watch it decrease instead of staying at 0.3.
3. When the cooldown reaches zero, call `arena.spawn(...)`. The inline
   walkthrough gives a starting position, velocity and warning time to try.
4. In the same branch, add 0.8 seconds to the cooldown. Otherwise the function
   creates a spark every frame instead of one per interval.
5. Add the `arena.elapsed < 3.0` condition so there is time for sparks to cross
   and leave before the defense ends. Test moving above/below their path.

`RippleLanes` in the same file is a worked example to investigate. You implement
**LanternPulse**, whose timer and projectile code are intentionally unfinished.
The factory is registered already, so you can see each change immediately.

**Test it:** warnings before movement, repeated sparks at a steady interval,
room to dodge, eventual cleanup, and R restarting the timer. Run `--check`.
**Explain:** why subtract seconds instead of a fixed amount per frame?
**Stretch:** alternate heights or edges, or leave gaps between several sparks.

## Mission 4 — Let a character change tactics

**Open:** `undercode/student.py` → `choose_echo_pattern(context)`.
**Goal:** Echo uses Ripples first, then your Lantern Pulse on later turns.

1. Complete mission 3 first. Run `python main.py --encounter echo`.
2. Use ITEM or ACT, survive a defense, then take another turn. Enable the
   selector's diagnostic and notice that `context.turn` starts at 0.
3. Before the existing fallback, add a condition for `context.turn >= 1`.
4. Return a **new** `LanternPulse()` in that branch. Keep `RippleLanes()` for
   the opening turn. The inline walkthrough explains the other context fields.
5. Play again: the arena title and hazards should change on the second defense.

**Test it:** opening defense = Ripples; next defense = Pulse. Restart returns
to Ripples. Each call constructs a fresh instance so timers do not leak.
**Explain:** how is selecting a pattern different from updating its projectiles?
**Stretch:** respond to understanding (`calm`) or remaining HP instead of turn.

## Story project — Build a new place

Follow [STORY_GUIDE.md](STORY_GUIDE.md). This project uses story data rather than
implementing engine rules. Move letters, write conversations and choices, add a
Python level file, register it in `student_world.py`, and connect a door to its
named entrance. Set a flag in one place and use it to change a later conversation
or open a gate.

**Test it:** travel both ways, close/read dialogue, try locked gates before and
after collecting an item, and restart for a fresh story. Run `--check`.

## After the guided missions — Independent projects

These projects give you a goal; finding and connecting the code is part of the
work. Start with a small playable version and explain how you tested it.

- **A new neighbor:** define a character, register it in `EXTRA_CHARACTERS`,
  and place it using a letter in a level legend. Give it distinctive ACT choices
  and a new defense sequence. Check peaceful, combat, leave and loss outcomes.
- **A special player technique:** investigate the `Strike` contract in
  `attacks.py`. Implement a timing mechanic, register its `Weapon` in `content.py`,
  and test misses, perfect timing and repeated inputs. Tab selects weapons.
- **A bigger adventure:** a dash with a cooldown, moving world characters,
  scrolling levels, a multi-stage boss, remappable controls, a nested dialogue
  editor, or saved progress with a versioned format.

All files are editable. The guided functions give you a first place to work;
you can extend the game beyond them once you understand their boundaries.
