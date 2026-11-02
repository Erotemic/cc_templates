# Teaching with UnderCode

Students should be able to invent a character before understanding the entire
engine. Start story authors in `undercode/student_world.py` using [STORY_GUIDE.md](STORY_GUIDE.md).
They can write conversations, choices and levels using Python helper calls. Start students
learning conditionals in `student_sprites.py`; students ready for mechanics can
use `student_mechanics.py` or the battle example in `student.py`.
Open the engine when an extension needs it.

## A first session

For coding, use the four guided missions in [MISSIONS.md](MISSIONS.md).
Each function includes its inputs, an incremental walkthrough, an opt-in
`if False:` diagnostic, TODOs and visible acceptance checks, following the
Infinity Climber format. A student's implementation changes **normal play**:

| Mission | Function | Starter behavior | Student adds |
| --- | --- | --- | --- |
| 1 | `student_sprites.choose_player_view` | Always down | Four directional views |
| 2 | `student_mechanics.warm_light` | No effect | Healing and feedback on entry |
| 3 | `student.LanternPulse.update` | Empty arena | Timed, warned moving sparks |
| 4 | `student.choose_echo_pattern` | Always Ripples | Pulse after the opening turn |

Give mission 1 a session of its own: predict x/y values, observe diagnostic
output, implement one direction, then the other directions, then diagonals.
Use `--check-sprites` after trying the game. Failed exercise checks are expected
in the starter. The normal test suite checks the engine independently of
whether students have completed the missions.

Missions 2 and 3 are independent of mission 1; mission 4 builds on mission 3.
For story authors, edit Python level definitions using [STORY_GUIDE.md](STORY_GUIDE.md) and preview
`--level studio`. Clearly distinguish story customization from programming new
behavior. Both are useful, but they teach different things.

**Instructor examples:** `teacher/solutions.py` has completed versions for
comparison. Gameplay never imports them and there is no flag that substitutes
them for student work. The tests inject these examples to verify that completing
the TODOs changes the actual rendering, trigger and battle paths. Consider
omitting the teacher folder from a student handout after preparing your copy;
it is not needed to play. Keep it if you want students to run the supplied
regression suite, which uses the examples as extension fixtures.

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

Keep all room maps, legends, dialogue and door links in `student_world.py`,
battle content in `student.py`, and new world actions in `student_mechanics.py`.
`LEVELS` contains the room definitions; the starting marker is in the same file.
`building.py` provides small documented functions returning ordinary dictionaries;
students can use Python variables, comments and lists while authoring.
Triggers and interaction hooks take functions directly, so a student can trace
`trigger(warm_light)` to the function they implement. `story.py` compiles letters
to internal tile positions, checks links, and manages paged conversations; students
author named spawn markers rather than coordinates. Conditions are flag/outcome
checks, never executable expressions. Choices commit their flags on selection;
dialogue completion flags commit only on the last confirmed page. Branches
replace the default dialogue; the first matching branch wins.

`World.facing` remembers the last requested walking direction, including when
facing a wall. `student_sprites.choose_player_view` chooses the view and `art.courier`
draws it. The student function is used on every normal world frame, including
after restart. Rendering never changes walking state.

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
python main.py --check-sprites  # mission 1 progress; unfinished in starter
python main.py --encounter echo
python main.py --practice pulse  # mission 3; no sparks until implemented
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

Copy `student_world.py` along with the other Python files. All art/audio is local Python code. There are no downloads, font installs,
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
