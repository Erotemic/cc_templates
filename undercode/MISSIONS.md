# Guided work: predict, build, observe, explain

You own the game. Rename it in `settings.py`, change some writing in
`student_world.py`, and choose a feature you want to add. The exercises below
teach different ideas; they are not a list you must finish before inventing one.

For each mission: predict the result, change a small piece of code, run it,
inspect F2 state or a brief diagnostic, and explain what you observed. The
inline walkthroughs identify inputs and outputs; [ENGINE_GUIDE.md](ENGINE_GUIDE.md)
shows the caller and the surrounding rules. Keep diagnostics short and turn
them off after observing. All implementations affect normal play.

## Overworld route

Run `python main.py --overworld`. Open `student_overworld.py` beside
`overworld/engine.py`. These tasks use ordinary functions; no pattern class is
needed. The supplied engine still supports walking, rooms and conversations.

### 1. A different view for each direction

**Concept:** conditionals and return values. **Function:** `choose_player_view`.

Predict x/y while walking left and up. Find the call in `World.move`. Add the
left case first, run, then add right and up. Keep down as a fallback. For
diagonals, select the stronger absolute axis; equal strengths use vertical.

```bash
python main.py --check-exercise facing
```

Test four directions, diagonals, idle, and facing a wall. Explain why position
alone cannot tell you which way a stationary person faces. The function should
return a view name; it should not move the character or read keyboard globals.

**Transfer:** change the supplied art in `art.courier`, or add walking frames.

### 2. Sprint while holding Shift

**Concept:** held input, units, and separating a decision from its application.
**Function:** `movement_speed`.

Read the multiplication in `World.move`. Predict distance for 0.1 seconds at
155 pixels/second. Return 230 when `controls.sprint_held` is true; preserve 155
otherwise. The engine applies the returned speed to the same collision rules.

```bash
python main.py --check-exercise sprint
```

Compare walking and sprinting, release Shift, move diagonally and against a
wall. Explain why speed should be multiplied by seconds exactly once.

**Transfer:** add stamina by locating appropriate state and update code yourself.

### 3. Heal once on entry

**Concept:** shared mutable state and an event that occurs between frames.
**Function:** `warm_light`. Run `python main.py --level studio`.

The mint oval is wired to your unfinished function. Find `update_triggers` in
the world engine before editing. Store the player, call `heal(amount=3)`, keep
the returned gain, and show it through `world.tell(text=...)`.

```bash
python main.py --check-exercise healing
```

At 5/20 HP, enter → 8; stand still → 8; leave/return → 11. At 19/20 report 1,
and at full HP report 0. For a temporary low-HP experiment, assign HP once in
your function, observe, then remove that setup line. Or visit after damage.
Explain what remembers last frame's occupancy and why a callback should not
run on every frame merely because the player is still nearby.

**Transfer:** require a story flag or design a one-use reward.

## Encounter route

Run `python main.py --encounter echo`. Read the turn trace in ENGINE_GUIDE and
watch its phases with F2. Before coding, change an ACT's `reply` and `calm` in
Echo's definition; predict when SPARE becomes available. Trace `choose` to find
where the values affect the turn. This is a reading experiment, not a new hook.

### 4. Build the empty Lantern Pulse pattern

**Concept:** an instance's timer, elapsed time, and repeated events.
**Class:** `student_encounters.LanternPulse`. Read a worked pattern alongside it.

```bash
python main.py --practice pulse
python main.py --check-exercise pulse
```

The arena initially has no sparks. Subtract `seconds` from its cooldown. When
the cooldown is ready and `arena.elapsed < 3.0`, spawn a right-moving spark at
x=8, y=arena.height/2, vx=160, vy=0, warmup=0.5. Use named arguments. Add 0.8 to
the cooldown in that same branch so another spark waits for its interval.

Test warning before movement, repeated sparks, a dodge route, final cleanup,
and R resetting the timer. Explain why the pattern creates hazards while Arena
moves/removes them. Explain what `self` refers to and why two instances must
have separate cooldowns. Try another direction or height after this works.

### 5. Let Echo change tactics

**Concept:** functions returning new objects from read-only context.
**Function:** `choose_echo_pattern`. This builds on the previous mission.

Use ITEM or ACT and survive two turns. Observe `context.turn` starting at zero.
Before the fallback, return a new `LanternPulse()` when the turn is at least 1.
Keep `RippleLanes()` for the opening. Play again and observe the title/hazards.

```bash
python main.py --check-exercise tactics
```

Test the opening, next turn, restart, and fresh pattern instances. Explain why
the selector does not advance projectiles. Then choose a rule of your own using
understanding or remaining opponent HP instead of turn number.

### 6. Make encounter buttons clickable

**Concept:** a loop over records, rectangle hit tests, and returning a selected index.
**Function:** `student_encounters.clicked_button`. This task is independent of
Pulse and tactics; students comfortable with loops can choose it first.

```bash
python main.py --encounter echo
python main.py --check-exercise mouse
```

Read the greeting with Z. At first, clicking ACT does nothing. Keyboard controls
still work. Read `Encounter.update_menu` to find the call to your function, and
`encounters/menu.py` to see the button records. Drawing uses those same rectangles.

1. Predict which `(x, y)` coordinates fall inside the ACT rectangle. Is the
   point the pointer position now, or the position saved when the button was pressed?
2. The function receives `mouse_position` and a list of currently visible buttons.
   Its worked guard already returns None when there is no click.
3. Loop over every button. Use `button.rect.collidepoint(mouse_position)` to
   ask whether the click is inside its rectangle.
4. Return `button.index` when it matches. Keep the final `return None` **after**
   the loop, so missing FIGHT still lets you test ACT, ITEM, and SPARE.
5. Run the checker and play. The unfinished starter passes 6/12 examples because
   it already ignores outside/missing clicks; implement the successful hits.

**Test it:** click every main button, then a submenu row and Back. A click should
select once; holding the mouse must not repeat the action. Click a gap and the
black letterbox margins, resize the window, and try again. Z/arrows must still
work. Clicks during text or defense do not act as confirm/jump inputs.

**Explain:** why must the engine check `clicked is not None` instead of
`if clicked`? Index 0 is FIGHT, a real choice. In a long ACT list, keyboard-scroll
first: the bottom visible row might be option 9, so return the record's index,
not its position in the visible list. Pygame includes left/top edges and excludes
right/bottom edges; predict those checker results before running it.

**Read the whole path:** runtime captures a left-button press and undoes window
scaling; Controls carries that logical point; your function chooses a button;
Encounter applies the same `choose()` used by the keyboard; drawing shows the
result. The engine returns after that choice so the click cannot also confirm
the submenu it just opened. No teacher solution is used during normal play.

**Transfer:** add hover feedback, wheel scrolling, or clickable story choices.
Locate their update and drawing paths yourself; those need additional rules.

## Fading the scaffolding

Pick one task with fewer instructions: make a sign change its writing after a
choice, create a peaceful person, add a linked room, or build a second pattern
with different warnings. Use the record docstrings and the engine tour to find
what you need, then write a small test/example in the style of `tests/test_story.py`.

Next pick an independent project from [CHALLENGES.md](CHALLENGES.md). Those tasks
do not supply a hooked-up function. Choosing where a rule belongs is part of
learning to extend an engine.

`--check` checks content/engine health. `--check-exercise ...` runs your actual
code and reports unfinished behavior. Regression tests that inject teacher
examples do not certify a student's solution. Explain and demonstrate yours.
