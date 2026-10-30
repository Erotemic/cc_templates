# Guided missions — Little Platformer

**Start with `platformer/student.py`.** It contains the full walkthroughs,
`if False:` diagnostic prints, and `TODO(student)` markers. This file is a
checklist, not a replacement for the comments in the source.

Keep the three original levels playable as you learn. You don't need to
finish every mission; choose what you'd like to build. M is mute, X or Space
is jump, R restarts the room.

| # | Mission | Start here | Demonstrate success |
| - | - | - | - |
| 0 | Rename and recolor your robot | `student.py` constants | Your changes appear in the window |
| 1 | Make the spring bounce | `student.bounce_from_pad` | Standing on orange pad launches you |
| 2 | Make enemies patrol | `student.move_enemy` | Purple creature reverses at its limits |
| 3 | **Add level 4** | `level.py` maps and `LEVELS` | Reach and finish a fourth room |
| 4 | **Hero talks on events** | `student.hero_speech` | Star and enemy cause different speech bubbles |
| 5 | **Animate level changes** | `TRANSITION_SECONDS`, `student.draw_transition` | A visible animation plays before the next room |
| 6 | **Boss battle** | `student.update_boss` | A real fight unlocks the door when boss HP reaches zero |
| 7 | **Write a new song** | `student.level_melody`, `sound.py` | One level plays your original melody |
| 8 | **Following zoom camera** | `student.camera_view` | Zoomed-in room follows hero; HUD stays still |
| 9 | **Double jump** | `student.try_double_jump` | Two jumps in the air, reset on landing |
| 10 | **Moving platforms** | `student.move_platform` | Blue platform moves and carries the hero |
| 11 | **Secret switch** | `student.activate_switch` | Touch red switch once, reveal bonus star |

## Suggested order

Try **1, 2, 4, 9, 3** for shorter exercises. **7 and 11** are good small
projects once you're comfortable with variables and lists. **5, 8, and 6**
need more time, because you're adding an animation, transforming the camera,
or building a new game rule.

The game starts with visible unfinished elements: a purple enemy and orange
pad in every room, a blue platform and red switch in level 2, and a crowned
boss in level 3. These won't all do something until you write their code.
The fourth level and custom song should be **your own work**, not supplied
as completed examples.

## Testing your work

After each mission:

1. Tell someone what you expect the game to do.
2. Enable the diagnostic print in the corresponding function. Test it.
3. Edit a few lines. Test again. Compare with your prediction.
4. When it works, turn off the print and show someone the result.
5. Run `python -m unittest discover -s tests -v` and fix genuine errors.

When you want **less guidance**, try `python -m platformer.challenge`.
Those independent challenges tell you the goal and important concepts,
but do not tell you which function to edit.
