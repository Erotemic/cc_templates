# Teaching Little Platformer

## Scope

The default is still a small raw pygame game: three fixed 24x15 ASCII maps,
walking, jumping, stars, doors, a stationary enemy, an inert spring, and
memory-generated music/effects. There is no sprite-sheet build or file-based
audio pipeline. No student implementation is required to finish level 3.

There are now **eleven guided missions**, plus eight independent challenges.
Not all eleven are expected in one class, or even one semester. They form a
menu. The student keeps ownership of how the finished game looks and plays.

## Suggested progression

| Session goal | Missions | Concepts |
| --- | --- | --- |
| First hour | 0, then 1 or 2 | Read real code; variables, movement, conditions |
| Short feature | 4 or 9 | Event -> speech; reset a flag on landing |
| Level design | 3 | ASCII maps, lists/tuples, verification |
| World interaction | 11 | Trigger an event once; remember it in state |
| Physical motion | 10 | Frame time, reverse direction, carrying a passenger |
| Creative audio | 7 | MIDI notes, lists, synthesis |
| Larger project | 5, 8 or 6 | Animation, coordinate transforms, combat state |

The guided comments in `platformer/student.py` specify the variables a
student can inspect, numbered steps, and **a visible success criterion**.
They do not implement the mission. Encourage students to predict diagnostic
values before changing each `if False:` to `if True:`.

## What has been prepared (not completed)

- **Fourth level:** level.py explains how to append another map and name.
  Map validation and backgrounds support additional levels; the student
  writes the actual map. The win banner uses the number of maps.
- **Hero reactions:** the engine calls `hero_speech` after hurt/star events,
  and displays a temporary bubble near the player if a string is returned.
- **Transitions:** setting `TRANSITION_SECONDS` enables a pause between
  levels; `draw_transition` is left for the student to animate it.
- **Boss:** a `B` marker in level 3 draws a large crowned enemy. The
  student's `update_boss` defines health loss and attacks. Activating a
  living boss blocks the exit; the baseline leaves it inactive.
- **New song:** the mixer can change tracks based on `level_melody` without
  audio assets. The original track remains the default everywhere.
- **Camera:** the draw pipeline can crop/scale based on `camera_view`, but
  the default (480,300,1.0) shows the complete level, with fixed HUD.
- **Double jump:** the player has a `extra_jump_used` state bit; the student
  defines consumption and reset in `try_double_jump`.
- **Moving platforms:** an `M` tile in level 2 creates a stationary blue
  platform that already supports collision and horizontal carrying.
- **Switch:** an `S` tile in level 2 calls `activate_switch`; the student
  makes a one-time state change and reveals a prepared bonus star.

The original two exercises (bounce and enemy patrol) remain unchanged.
`challenge.py` avoids repeating guided double jump or moving platforms
in the independent board; it now includes crumbling platforms and a
speedrun challenge instead.

## Preserving student ownership

Use prompts such as "How can you make sure it only happens once?" rather
than writing the condition. Ask students to explain a changed value and
its effect onscreen. Small completed features count more than partially
implemented advanced ones. In particular, boss and camera missions can
reasonably take multiple classes.

A clean learning path is:

```text
main.py -> game.py (events and draw loop) -> student.py (chosen hook)
                                      -> sprites.py (movement/collision)
                                      -> level.py (map data)
                                      -> sound.py (synthesizer)
```

## Validation

```bash
cd platformer
python -m unittest discover -s tests -v
python main.py --frames 3 --screenshot screenshot.png
```

Pygame-independent tests cover maps, audio, and exercise contracts. With
pygame installed, the GUI tests also exercise collision, transitions,
camera, and startup through SDL's dummy video/audio drivers.
