# UnderCode

**A small world. A conversation. A pattern to learn.**

UnderCode is an original, Undertale-inspired pygame starter for students who
want to build characters, conversations, timed attacks, and unusual defense
sequences. Walking, rooms and battles work; four guided code missions let
students add missing features to the game they actually play.

```bash
cd undercode
python main.py
```

Requires **Python 3.10+** and **pygame or pygame-ce**. Use an existing pygame
installation. If pygame is missing and installing packages is allowed:

```bash
python -m pip install pygame-ce
```

The folder runs by itself, including when launched from another working
directory. No package installation of UnderCode, build step, Internet access,
SVG/Cairo library, NumPy, Pillow, asset downloads, or system fonts are needed.
All portraits, scenery, music and sound cues are drawn or synthesized in Python.
Audio is optional; `python main.py --mute` does not open an audio device.

## Your first five minutes

1. Walk upward from camp to **Folio**, the open-book librarian. Press **Z** to
   talk, then **Z** to accept a practice encounter. **X** declines.
2. Read the introduction. **Z** first reveals the text, then advances it.
3. Choose **FIGHT**, **ACT**, **ITEM**, or **SPARE**. Try ACT → Listen.
4. During the reply, follow the defense hint. Hazards signal their arrival.
5. Listening twice fills the understanding bar. Choose SPARE → Spare to make
   a friend, or try the timed FIGHT sequence to finish the practice match.
6. The fade returns you to exactly where you were walking. The lantern fountain
   near camp restores HP and cocoa. The north path leads to two more neighbors.

For story writing, open **[undercode/story/studio.json](undercode/story/studio.json)**
and follow **[STORY_GUIDE.md](STORY_GUIDE.md)**. Move a letter, rewrite a line,
or add a room with its own legend. `python main.py --level studio` previews it.

**Start coding:** open **[undercode/student_sprites.py](undercode/student_sprites.py)**.
The Courier currently always faces down. Mission 1 guides you through choosing
left/right/up views; each change appears in the normal game. Read the inputs,
walkthrough, diagnostics and TODOs beside the function, then test with
`python main.py` and `python main.py --check-sprites`.

The other guided missions add a healing light, implement a new warned defense,
and make Echo change tactics. See **[MISSIONS.md](MISSIONS.md)**.

For battle mechanics, open **[undercode/student.py](undercode/student.py)**. Change Echo's name,
colors, greeting, or ripple interval. Run again. Echo lives in the Quiet
Observatory, through the north doorway.

## What students implement

1. **Directional views:** the Courier starts facing down; add the missing cases.
2. **Healing light:** the Studio trigger is wired up; implement its healing/message.
3. **Lantern Pulse:** the pattern is registered but empty; implement its timer,
   warning and moving projectiles.
4. **Changing tactics:** add the rule that selects Pulse after Echo's first turn.

These are unfinished student functions called by normal gameplay. The inline
steps guide implementation, rather than enabling a finished feature with a flag.
Other rooms, story choices and example defenses remain available while you work.

## What is already playable

- Four connected letter-map rooms with collisions, named door destinations,
  conversations, fountains and fades between rooms and encounters.
- Story-only characters, signs, choices, flags, collectibles and locked gates
  authored in JSON; optional registered Python mechanics.
- Four supplied walking drawings; students implement choosing their direction.
- Four original characters: Folio, Ferris, Prism and the editable Echo.
- FIGHT timing with a single focus strike or a three-beat rhythm strike.
- ACT choices that build understanding, SPARE, leaving practice, healing items,
  combat victories, and a forgiving return to camp after a loss.
- Free movement through falling pages; gravity/jump defense against low gears;
  a directional shield against incoming sparks; and telegraphed beam lanes.
- Seeded pattern randomness, damage cooldowns and swept projectile collision.
- Original procedural portraits, overworld art, a quiet soundtrack and cues.
- Pause-on-focus-loss, a help overlay, resizing with preserved aspect ratio,
  and explicit display/audio diagnostics for classroom machines.

Each encounter can be resolved by combat or by understanding the character.
Neighbors remember the outcome for this run and offer rematches. There are no
on-disk saves; **R starts a fresh run**.

## Controls

| Key | Action |
| --- | --- |
| Arrows / WASD | Walk; navigate menus; move or face a shield during defense |
| Z / Enter / Space | Talk, confirm, reveal/advance text, time a strike, jump in gravity mode |
| X / Backspace | Cancel a conversation; go back in a submenu; reveal dialogue |
| Tab, in the overworld | Switch Focus / Three Beat attack techniques |
| F1 | Open/close the guide; gameplay pauses while it is open |
| M | Mute/unmute when audio is available |
| R | Fresh run, or restart the encounter/pattern chosen on the command line |
| Escape | Quit |

Menu actions and jumps respond to **presses**. Movement and shield direction
respond to **held keys**. A transition freezes both scenes, so accepting a
conversation does not also select the first battle action.

## Test your idea without walking there

```bash
python main.py --list
python main.py --level studio
python main.py --check-sprites  # reports progress on mission 1
python main.py --encounter echo
python main.py --practice ripples
python main.py --practice pulse  # empty until you implement mission 3
python main.py --practice hops
python main.py --practice shield
python main.py --practice lanes
python main.py --seed 42
python main.py --check
```

`--practice` goes straight into one defense pattern; R retries it. Afterward,
ACT → Try the pattern again repeats it. `--check` validates room/content data
and simulates registered pattern and attack factories, including character
pattern choices. Importing the package does not open a window/mixer or run a
student pattern.

For machines or CI without a desktop:

```bash
python main.py --headless --mute --practice shield --frames 90 --screenshot preview.png
python -m unittest discover -s tests -v
```

Normal play needs a real desktop. An SSH terminal without display forwarding
cannot display a window; the launcher explains that instead of running
invisibly. Headless runs intentionally have no visible window. A missing audio
device is reported in the HUD and does not stop play.

## Where to edit

| File | Responsibility |
| --- | --- |
| **`undercode/story/*.json`** | Draw levels with letters, place people/doors and write dialogue/choices |
| **`undercode/student_sprites.py`** | Mission 1: implement directional views in normal play |
| **`undercode/student_mechanics.py`** | Mission 2: implement the Story Studio healing light |
| **`undercode/student.py`** | Missions 3–4: implement Lantern Pulse and Echo's changing tactics |
| `undercode/content.py` | Register battle characters, techniques and practice keys; load story files |
| `undercode/patterns.py` | Four worked defense-pattern classes |
| `undercode/attacks.py` | Player timing/ rhythm mini-games and their small extension contract |
| `undercode/model.py` | Character, ACT, weapon, room, player and session data |
| `undercode/battle.py` | Explicit battle phases, menus, turns, damage and outcomes |
| `undercode/arena.py` | Shared soul movement, hazard physics, shields and collision rules |
| `undercode/story.py` | Validate/compile level files and manage paged story dialogue |
| `undercode/sprites.py` | Directional-view acceptance examples |
| `teacher/solutions.py` | Instructor examples, never loaded by gameplay |
| `undercode/world.py` | Overworld movement, collisions, conversations and doors |
| `undercode/app.py` | Own the active scene; freeze and swap scenes during fades |
| `undercode/view.py`, `art.py` | Read-only UI and original portrait/scenery drawing |
| `undercode/audio.py` | Optional synthesized audio, isolated from game rules |
| `main.py` | Input → update → draw loop and launch options |

The template uses ordinary dataclasses, enums, functions and small classes.
Characters choose patterns through a function; a new pattern does not need a
new branch in the battle engine. There is no custom scripting language, global
broadcast system, or thread scheduler to learn before making a character.

See **[MISSIONS.md](MISSIONS.md)** for extension steps and
**[TEACHER_GUIDE.md](TEACHER_GUIDE.md)** for classroom use and architecture.

## Extending the game

**A character:** copy `ECHO` in `student.py`, give it a unique `key`, add it to
`EXTRA_CHARACTERS`, then add a character letter in a level JSON legend.
Its `character` selects the definition; an optional unique `id` remembers that
specific neighbor's battle outcome. Run `--check`, then `--encounter your_key`.

**A defense:** subclass `DefensePattern`. Give it a name, hint, duration and
optional `Mode.GRAVITY` or `Mode.SHIELD`. Keep its clock/state on `self`.
`update(arena, dt)` can use `arena.spawn(...)`, `arena.beam(...)`, `arena.rng`,
and the soul's local position. Add a key to `EXTRA_PATTERNS` to preview it with
`--practice`. Return a new instance from the character's `choose_pattern` hook.
The examples show cooldowns, reachable safe lanes, warnings and mode changes.

**A special player attack:** implement the `Strike` contract in `attacks.py`:
`update(dt, controls)`, `done`, a `score` from 0 to 1, and `view()` returning a
`StrikeView`. Add a `Weapon` with that factory in `content.py`. Tab selects it in
the overworld; the battle controller applies damage without knowing its class.

**A room/story:** copy a level JSON in `undercode/story/`, draw a rectangular
letter map, and add its legend. Doors link to named spawn markers; new files
are discovered automatically. Dialogue choices, flags, conditional branches,
collectibles and locked doors require no Python. Follow [STORY_GUIDE.md](STORY_GUIDE.md).
Use `student_mechanics.py` for new rules connected through `on_interact` / `on_enter`.

## Scope and validation

This is an original teaching template with practice encounters, not a finished
long-form RPG. It has no inventory editor, pathfinding, online features,
automatic saves or external asset pipeline. Those can be student projects.

The tests cover complete peaceful/combat routes through the real patterns,
transitions, loss/leave behavior, timed strikes, item limits, shield direction,
jumping, warned hazards, fast-bullet collisions, seeded spawns, extension
registration, every portrait/menu/mode, audio samples/muting, and launch paths.
Regular pygame 2.6.1 and pygame-ce 2.5.8 are checked on Linux/Python 3.13;
school Windows/macOS installations should get a local smoke check.

Original UnderCode code, character designs, dialogue, art and synthesized music
are included under the repository's [Apache 2.0 license](LICENSE).
