# Instructor guide: Infinity Climber

## Why a starter instead of a blank pygame window?

The student is right that starting from raw pygame is possible. **This
starter is raw pygame**: `game.py` opens the window, receives events, and
updates/draws each frame. It does *not* hide pygame behind a teaching DSL.

In a one-hour session, writing window setup, gravity, horizontal collision,
platform landing, camera scrolling, endless generation, and rendering leaves
little time for a student to make meaningful game decisions. The starter
supplies those parts but leaves eight visible features unfinished.

The risk is that the student feels they are modifying *your* game. Avoid that
by making the very first task a real creative choice: new title, colors,
procedural seed, and a theme they choose. Let them rename functions or draw
their own character if they prefer. Never require all eight missions.

## One-hour session proposal

| Time | Activity | Ownership |
| --- | --- | --- |
| 0–10 min | Play, ask them what this tower should be called | Decide genre, name, visual style |
| 10–15 min | Change `student.py` title, colors and seed | Immediate, visible change |
| 15–35 min | Student picks **one** mission | Implement their first mechanic |
| 35–50 min | Debug using the `if False` prints | Predict, experiment, revise |
| 50–60 min | Playtest, write down the next idea | Choose the next session's goals |

Don't automatically have them start with wall jumps; ladders and enemy
movement involve simpler conditionals. Let the student choose.

## Eight exercises: minimal learning targets

- **Wall jumps:** boolean logic, sign, velocity, short-lived state.
  `wall_side` uses -1 (left), +1 (right), 0 (neither). Negative `vy` is up.
- **Ladders:** state machine, collision as a precondition, gravity overridden
  while climbing.
- **Enemies:** `distance = speed * time`, mutable state, boundary checks.
- **Rising floor:** changing values each frame, world Y conventions,
  catch-up behavior and game balancing.
- **Moving platforms:** position over time, reversing at boundaries, and
  testing moving collision. Blue ledges already render, collide, and carry
  the player horizontally, so the student only writes their movement.
- **Better tower heights:** deterministic pseudo-randomness, smooth noise,
  reachability constraints, and designing a more interesting generator.
  The baseline vertical gap remains 100 px until they change the hook.
- **Pickups:** event hooks, state changes, and rewarding exploration. The
  tower already places treasure; the student decides what collecting it does.
- **Comeback event:** detect the fall, set and later consume a state flag,
  and trigger a one-time dialogue event. The student owns both conditions,
  the state transition, and the event; the engine only speaks returned text.

The stubs do not contain full solutions. The heckler dialogue is also editable in `student.py` for a light-weight bonus writing task. The engine exposes exactly the
variables needed to learn each mechanic and already responds when they are
modified. To teach a mechanic, ask the student to predict what the debug
print will say before switching `if False` to `if True`.

## Independent challenges: transfer, not another worksheet

The eight missions in `climber/student.py` are now explicitly guided:
inputs and outputs, example calculations, a TODO, debug prints, and visible
success checks. The TODOs remain unfinished. Use those missions to teach
conditionals, movement, collision, and state across frames.

`climber/challenge.py` is the **next stage**, not another set of callbacks.
It contains 18 optional feature/design challenges and five code-detective
questions. Each names a result the student can show you and a few related
concepts. It deliberately DOES NOT say which file or function to edit, and
nothing in that module is imported by gameplay automatically. Students
must find an appropriate place to implement and connect their changes.
They can also replace a prompt with something they invent.

For a one-hour session, offer a choice of just two or three challenges,
not all 18 at once. Breaking platforms, checkpoints, a second enemy, and
new heckler reactions build naturally on the guided missions. The
challenge difficulty labels are rough; scope matters more than the label.

Try **questions before instructions** when someone gets stuck:

1. What should a player SEE if this works? What would disprove it?
2. What needs to be remembered from one frame to the next?
3. Does something already in the game behave similarly?
4. What part of the game would need to know about the new behavior?

Avoid jumping directly to a filename or code sample. Offer those only if
the student is blocked after experimenting. Have the student demonstrate
the result, explain one design choice, and describe a bug they fixed.
The code-detective questions are also valid independent work; they require
no new feature and reward reading and understanding unfamiliar code.

**Testing note:** the height-generator tests now validate deterministic,
reachable gaps instead of assuming every tier stays exactly 100 pixels
apart. A student should not see a regression merely because they completed
Mission 6 with valid bounded noise.

## Showing the raw pygame foundation

The whole loop is short enough to trace together:

```text
main.py
  -> climber/game.py: run_graphical()       events + pygame display
      -> climber/engine.py: update()        physics and eight hooks
          -> climber/student.py            the learner's code
      -> climber/audio.py: SoundBoard      music and event sounds
      -> climber/art.py: Painter.draw()     image on the screen
```

For a more independent student, challenge them to change the pygame loop,
physics constants, platform colors, or `world.platform_center()` directly.
The project does not require them to stay inside `student.py`.

## Visuals and school computers

Art is authored entirely with pygame shapes (`rect`, `line`, `circle`,
`polygon`, `ellipse`). There is no runtime asset conversion and no SVG or
Cairo dependency. Existing `pygame` or `pygame-ce` installations both work.
If pygame is missing, try `python -m pip install pygame-ce` where packages
can be installed. Otherwise, copy an appropriately installed environment
or use a school-approved pygame setup. The headless tests don't need pygame.

The tower generator uses a small reproducible value-noise implementation
and makes only nearby platforms. A full noise package would add a dependency
without helping the teaching objective. The continuous main path is more
important than completely unconstrained randomness: baseline tier spacing
is 100 px, while a normal jump rises about 159 px, and successive centers
wander less than 110 px. The generated path is tested across 2,000 tiers.

For mission 6 the student changes `platform_height_offset(tier, noise)`.
Offsetting the absolute height with a bounded noise value avoids computing
all earlier tiers and preserves the tower's bounded-memory design. Encourage
small offsets (around +/-20 px). The existing tier-streaming search includes
padding for such changes, but not for arbitrarily large offsets.

For mission 5, the student changes `move_platform(platform, seconds)`.
Blue platforms are stationary by default. The engine already handles
colliding with them and riding them horizontally. They appear at tier 2 and
then every six tiers, so the student can find one without climbing far.

## Heckler speech and fall-recovery exercise

The elevator never moves down to follow a fall. Dialogue is handled as a
small state machine in `engine.py`: start a line, reveal characters at a
fixed rate, hold the completed line, then close it. A short silence separates
lines. No text is drawn when the message is empty. `art.py` locates the
bubble from the heckler's world coordinates minus `game.camera_y`, so the
bubble and its tail move with the character rather than sticking to a screen
position. `synth.py` generates three quiet mumble sounds; `audio.py` plays
one every few typed characters.

For mission 8, the `Game` dataclass provides four student-owned fields:
`peak_player_y`, `comeback_pending`, `comeback_peak_y`, and `fall_count`.
The engine **does not** detect falls or reunions. It calls
`student.update_heckler_comeback(game, heckler)` every frame, even while
another speech bubble is active. By default that function returns `None`;
no comeback taunt occurs until the student adds code.

Help the student design two transitions before they implement them:

```text
READY
  significant fall: save last highest Y and mark comeback_pending=True
       |
       v
WAITING_FOR_RETURN
  climb back to remembered Y: clear the flag and return the heckler line
       |
       v
READY
```

A 180-pixel drop is a useful starting threshold; a normal jump rises
about 159 pixels. During discussion, emphasize why `comeback_pending`
prevents a single long fall from being counted on every frame, and why
clearing the flag prevents speech from triggering repeatedly when the
player stands near the elevator. The student may use the example text in
`heckler_comeback_line()` or write their own.

When the student's function returns a non-empty string, the engine queues
it until the current speech and cooldown finish. A queue is necessary
because a reunion can occur while the heckler is already talking. This
mechanism is *not* the event detection; it is only presentation logic.

For the lesson, first have the student observe the diagnostic without
changing state. Then implement detection and verify that a fall sets the
flag without causing immediate speech. Only after that, add the return
condition, clear the flag, and play the comeback. For testing, confirm
that ordinary jumps are ignored and the same return triggers only once.

## Sound and school computers

Audio uses the same `pygame.mixer` mechanism as the `rpg` template. Rather
than checking in any WAV files, `climber/synth.py` composes an original
four-bar melody and six gameplay effects plus three speech blips at startup, in memory, using only
Python's standard library. `climber/audio.py` turns the generated signed-16
sample buffers into pygame Sounds and loops the melody on a reserved channel.
The loop and effects are synthesized **once at startup**, not every frame.

The graphical launcher calls `pygame.mixer.pre_init()` before
`pygame.init()` to request a known 22050-Hz, 16-bit stereo format. If the
mixer isn't available (for example, when testing with no sound device),
the game runs silently. Press M to mute the loop and effects.

**Suggested bonus lesson:** edit one of the melody's MIDI notes in
`climber/synth.py`, restart, and compare. Students can also examine how
`make_effect()` sweeps the pitch upward for a jump. No commands to render
files and no new school-machine dependencies are involved.

## Getting a standalone student repo

Keep the reference in `cc_templates/climber`. When the student is ready to
own it, copy the folder to their repository and let them change everything.
For example, from the parent of `cc_templates`:

```bash
cp -R cc_templates/climber infinity-climber
cd infinity-climber
git init
git add .
git commit -m "Start my tower game"
```

The copy retains no dependency on `cc_templates`; the project runs as-is.

## Tests

```bash
cd climber
python -m unittest discover -s tests -v
python main.py --headless --frames 240
```

These check the base engine and all eight extension points without testing
for a particular student solution. They also test generated PCM
audio, mixer playback/muting, and the silent/no-audio fallback. When pygame is installed, they
render a graphical frame and exercise a larger window using dummy SDL.
