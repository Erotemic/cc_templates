# Teaching with UnderCode

Students should be able to invent a character before understanding the entire
engine. Start story authors in `undercode/story/` using [STORY_GUIDE.md](STORY_GUIDE.md).
They can write conversations, choices and levels by editing JSON. Start students
learning conditionals in `student_sprites.py`; students ready for mechanics can
use `student_mechanics.py` or the battle example in `student.py`.
Open the engine when an extension needs it.

## A first session

For a story-focused class: preview `--level studio`, edit its dialogue and map,
add a linked level, and explain one flag-driven change. For a conditionals class:
use mission 0 in `MISSIONS.md`, `--sprite-task`, and `--check-sprites`. The
exercise's failed checks are intentional until the student completes it. The
normal game and ordinary test suite use the finished four-view reference.

For a battle-mechanics session:

- **5 minutes:** run the game; locate Folio; try ACT, a defense reply, and SPARE.
- **10 minutes:** change Echo's writing/colors and run `--encounter echo`.
- **15 minutes:** edit ripple spacing or warnings; use `--practice ripples`.
- **10 minutes:** explain the pattern's state and `dt`; try two repeatable seeds.
- **5 minutes:** run `--check`, show a playable change, and describe one limitation.

For beginners, keep the character/ACT data as the main surface. Students ready
for functions can edit `choose_echo_pattern`. Classes and composition become
useful when they make an independent pattern or player technique.

`MISSIONS.md` contains guided projects and independent goals. The starting
content is complete, so a partial student extension does not prevent everyone
else from running the template.

## Architecture to point at

The loop is **input → update → draw**. `Controls` separates held movement from
single presses. World and battle consume input only when they own the scene.
The main loop limits long frame stalls and pauses when the window loses focus.

`Game` in `app.py` owns scene transitions. During the fade it updates neither
gameplay model. The destination swaps once under the opaque midpoint; the
interact press cannot select an action in the new scene. Returning from battle
keeps the world position, except that a loss returns to a restored camp.

`Battle` has explicit `Phase` values. Menu selection, the attack sequence,
messages, defense and results each have one place in the state machine.
`Outcome` distinguishes spare, combat, leaving and losing. Dialogue is paged;
revealing a line and advancing it are separate presses.

A `Character` is immutable content plus two callables: its portrait and its
pattern-selection function. `TurnContext` is a read-only snapshot. The selector
returns a new pattern; that pattern owns its own cooldown and wave count.

`Arena` owns collision/damage rules. Pattern classes create projectiles/beams
through a small API. Swept circle collision catches fast bullets, and a damage
cooldown prevents a dense cluster from taking all HP in one frame. Warnings are
non-damaging. Shield direction and gravity movement are reusable arena modes.

A `Weapon` holds a `Strike` factory. The strike reports accuracy and drawing data;
`Battle` converts that accuracy into damage. The timing mini-game does not
reach into enemy health or decide whether to change scenes.

The renderer reads state. It does not change HP, advance patterns, consume
encounter randomness or resolve a turn. Audio observes queued cues and is
optional; losing an audio device does not change the rules.

## Useful boundaries

Keep story **content** in `story/*.json`, battle content in `student.py`,
and new world actions in `student_mechanics.py`. `story.py` compiles letters to
internal tile positions, checks links, and manages paged conversations; students
author named spawn markers rather than coordinates. Conditions are flag/outcome
checks, never executable expressions. Choices commit their flags on selection;
dialogue completion flags commit only on the last confirmed page. Branches
replace the default dialogue; the first matching branch wins.

`World.facing` remembers the last requested walking direction, including when
facing a wall. `sprites.player_view` chooses the dominant axis and `art.courier`
draws a view. `--sprite-task` substitutes the student's selection function;
restart preserves this choice. Rendering never changes walking state.

Put new **rules** in the model that owns them. A story choice should not be checked in drawing code. An attack
pattern should not read keyboard globals, screen pixels or wall-clock time.
Use local arena positions, `dt`, the supplied RNG, and `Controls`.

A new enemy should not need another `if enemy.name == ...` in the engine. New
patterns should not require a global event name, thread, or hidden scheduler.
Call the student's extension explicitly at the boundary where it belongs.

## Running/checking in class

```bash
python main.py --list
python main.py --check
python main.py --level studio
python main.py --sprite-task
python main.py --check-sprites  # intentionally unfinished student exercise
python main.py --encounter echo
python main.py --practice shield --seed 7
python -m unittest discover -s tests -v
```

`--check` deliberately invokes student factories and simulates their behavior.
Imports load and validate story data but do not run student pattern factories. A malformed extension should produce a useful exception in its
own code or a content diagnostic; gameplay exceptions are not swallowed.

The tests verify rules and real routes, not just method names: peaceful and
combat resolutions for every character, scene transfer, leaving/loss/rest,
physics, warnings, timing, registration, render purity, audio and command-line
launches. When a student intentionally changes a rule, update the relevant test
and explain the new expectation.

## School deployment

Copy the complete `undercode/` project folder. Launch `main.py` using the editor's
existing Python interpreter with pygame installed. A separate virtual environment
or editable installation is optional. Existing regular pygame is supported;
pygame-ce is the suggested install when pygame is absent. Do not install both
into one environment because they share the `pygame` import name.

Copy the JSON story directory along with the Python files. All art/audio is local Python code. There are no downloads, font installs,
Cairo dependencies, subprocess tools, file paths tied to this repository, or
writes to protected user folders. Generated music is a short original loop.
Use `--mute` if opening an audio device is undesirable. An unavailable device is
shown in the HUD. The game needs a desktop display for interactive play.

For offline installs, an instructor can download pygame wheels on a matching
OS/Python version with `python -m pip download -r requirements.txt -d wheels`,
then install from the transferred folder using
`python -m pip install --no-index --find-links wheels -r requirements.txt`.

The included art/dialogue/music belongs to this template under the repository
license. Students can replace it with their own work; external resources belong
in a clearly documented asset directory with their applicable attribution.
