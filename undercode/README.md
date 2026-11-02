# UnderCode: learn how a game works, then make it yours

A pygame learning project with two independently runnable systems: a tile-based
overworld and an Undertale-inspired encounter system. The starter supplies
walking, collisions, dialogue, turn menus and worked attack patterns. Students
implement missing behavior, trace the engine, and build their own mechanics.

```bash
python main.py --overworld
python main.py --encounter echo
python main.py --practice pulse
```

Requires Python 3.10+ and pygame or pygame-ce. An existing pygame installation is
fine. If needed: `python -m pip install pygame-ce`. Copy this whole folder to use
it as a separate project. Art, fonts and synthesized sound are local; there are
no downloads, SVG/Cairo dependencies, or build steps. Use `--mute` when desired.

## Choose where to begin

- **Explore code:** read [ENGINE_GUIDE.md](ENGINE_GUIDE.md), then follow one frame
  through `runtime.py` and `app.py`, then [World.update](undercode/overworld/world.py)
  or [Encounter.update](undercode/encounters/encounter.py).
- **Learn by building:** open [MISSIONS.md](MISSIONS.md). Overworld tasks
  use ordinary functions; encounter tasks introduce timers, tactics and mouse hit tests.
- **Tell a story:** all rooms, dialogue, choices and door links are in
  [student_world.py](undercode/student_world.py). Follow [STORY_GUIDE.md](STORY_GUIDE.md).
- **Go beyond exercises:** [CHALLENGES.md](CHALLENGES.md) asks you to locate and
  extend the engine yourself. Every source file is editable.

The learner is expected to know variables, conditionals, loops and basic
functions. The engine guide introduces records, methods, callbacks and phases
when there is a concrete game problem for them to solve.

## What is unfinished on purpose?

| Task | Student implementation | Visible addition |
| --- | --- | --- |
| Facing | `student_overworld.choose_player_view` | Left, right and back views while walking |
| Sprint | `student_overworld.movement_speed` | Shift changes speed; releasing it restores walking |
| Healing | `student_overworld.warm_light` | The Studio's mint oval restores HP on entry |
| Pulse | `student_encounters.LanternPulse.update` | Warned, timed sparks cross the defense arena |
| Tactics | `student_encounters.choose_echo_pattern` | Echo changes patterns on later turns |
| Mouse | `student_encounters.clicked_button` | Click action buttons and visible submenu rows |
| Piano | `student_overworld.update_piano` | Detect floor-key collisions and play matching pitches |

These functions are called in normal gameplay. The Courier initially looks
down, the light has no effect, Pulse has no sparks, and Echo repeats Ripples.
Encounter buttons respond to the keyboard until the mouse task is implemented.
Other rooms, conversations, fountains, and example defenses work immediately.
The starting courtyard has a floor piano and a repair sign. C4 works as a
head start; students generalize its collision and note logic to repair seven keys. The game never imports teacher solutions.

## Controls and observation

| Input | Meaning |
| --- | --- |
| Arrows / WASD | Held movement; single presses navigate menus |
| Z / Enter / Space | Talk, read, confirm, time a strike; jump in gravity defense |
| X / Backspace | Close world dialogue; go back in menus; reveal encounter text |
| Shift | Sprint after implementing its task |
| Left mouse click | Encounter menu buttons after implementing mission 6 |
| F1 | Controls guide; pauses gameplay |
| F2 | Inspect mode, phase/room, HP, facing and story flags |
| Tab | Select an encounter technique while walking |
| M | Mute/unmute |
| R | Fresh run, or restart the isolated encounter/pattern |
| Escape | Quit |

Start by walking up from camp to Folio. Z opens an invitation; a second press
accepts it. In the encounter, ACT → Listen builds understanding. After two
helpful replies, SPARE can end it peacefully. FIGHT uses a timing mini-game.
The fountain restores HP/cocoa. The north path reaches the observatory; its east
path reaches the Studio quest. Story progress is remembered only for this run.
An isolated encounter ends on a result screen; R retries without loading rooms.

## Three different checks

```bash
python main.py --check                     # engine/content health
python main.py --overworld --check         # rooms only
python main.py --encounter echo --check    # encounters only
python main.py --check-exercise facing     # YOUR task implementation
python main.py --check-exercise mouse      # mission 6: mouse buttons
python main.py --check-exercise piano      # mission 7: collisions and notes
python main.py --check-exercise all
python -m unittest discover -s tests -v    # regression suite
```

Exercise checks intentionally report unfinished work in the starter. Engine
checks can pass before any task is complete. The regression suite uses teacher
examples in some tests to verify that extension points work; that is separate
from checking your own solution. `--check-sprites` is a shortcut for facing.

Stop and launch again after editing code. R resets state but does not re-import
Python files. `--list` lists room, encounter and practice IDs. `--level studio
--entry entrance` previews a named room/marker.

## How the source is organized

| File / folder | Responsibility |
| --- | --- |
| `main.py` | Select a mode or check; hand over to the window adapter |
| `undercode/runtime.py` | pygame input → update → draw → audio |
| `undercode/app.py` | Active mode, fades, and explicit request/result handoffs |
| `undercode/contracts.py` | Small records used to connect the two systems |
| `undercode/model.py` | The one persistent Player and this run's story progress |
| `undercode/controls.py` | Held directions versus one-frame presses |
| **`undercode/overworld/world.py`** | Read `World.update` first: walking, collisions, interactions and room requests |
| `undercode/overworld/` | Room records, map placement and world drawing |
| **`undercode/encounters/encounter.py`** | Read `Encounter.update` first: phases, choices, turns and outcomes |
| `undercode/encounters/` | Opponent definitions, attacks, defense physics and encounter drawing |
| `undercode/dialogue.py` | Conversation definitions, pages, choices and completion flags |
| `undercode/student_world.py` | All rooms and story writing in one file |
| `undercode/student_overworld.py` | Guided world behavior functions |
| `undercode/student_encounters.py` | Echo and guided encounter behavior |
| `undercode/student_art.py`, `art.py` | Editable portrait and supplied drawing examples |
| `undercode/settings.py` | Title, player name, and logical screen size |
| `undercode/presentation.py`, `view.py` | Shared drawing tools and selection of the active renderer |
| `undercode/audio.py` | Optional generated sound, outside the rule engines |

A peaceful Person is independent of an Opponent. It can have an optional
`encounter_id` to connect them. Player HP has one owner shared by world and
encounter; the arena does not copy health back and forth.

## Classroom machines

Normal play needs a desktop. A missing audio device does not stop the game.
For a VM, SSH session or automated check without a display:

```bash
python main.py --headless --mute --frames 60 --screenshot preview.png
```

Regular pygame and pygame-ce are checked on Linux; test your classroom's actual
interpreter and display setup. See [TEACHER_GUIDE.md](TEACHER_GUIDE.md) for lesson
planning, deployment, and how to separate student handouts from answer examples.
Original code, art, writing and synthesized music use the [Apache 2.0 license](LICENSE).
