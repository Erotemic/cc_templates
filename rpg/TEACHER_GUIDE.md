# RPG guided missions — teacher notes

The existing workshop in `student_game/workshop.py` is left intact. Its
worked examples teach basic control flow. The **new** `student_game/student.py`
contains four genuinely unfinished callbacks. Supporting characters and battle
wiring live in `student_game/guided_battles.py` so students can focus on
ordinary Python instead of rendering, registering characters, or combat math.

## Suggested lesson flow

Start in a predetermined scenario, predict what the character ought to do,
then compare with its actual behavior. Have the student enable one diagnostic
print, read the values, implement one small condition, and replay the same
scenario. `python main.py --check` tests authored behavior without opening
a pygame window; the lab prints context and choices. In the graphical game,
`--teach` adds additional trace output to the terminal.

| Mission | Student edit | Prediction and success check |
| --- | --- | --- |
| Confused Healer | `healer_strategy` | Injured shieldbearer should be healed; healthy party shouldn't consume mana |
| Cowardly Enemy | `coward_strategy` | Low HP => Defend; healthy => Attack |
| Cursed Sword | `cursed_sword_logic` | Injured wielder might apply burn; all cases still deal damage |
| Boss Phases | `boss_strategy` | Different legal actions at high/low HP; low mana still has a fallback |

The healer is intentionally **on the opponent's team**. The enemy team
contains a healer and a shieldbearer, both with real sprites and battle
animations. One team-wide AI strategy delegates the healer's turns to the
student hook and gives the shieldbearer a safe basic attack. Do not let the
student start by modifying this wiring; first establish that their chosen
action is visible in battle.

The sword's special effect is deliberately absent. The engine already
interprets scripted `damage(...)` and `add_status(...)` commands, and the
sword's animation is present. The student only decides which commands to
return.

The boss uses an ordinary attack until its strategy changes; it already
has three animated skills, including an all-enemy move. No need to create
new 2D art to make phases visible.

All four encounters work as ordinary playable battles if students never
implement the hooks. The behavior is intentionally simple, not broken.
Don't require all four missions in one class.

## Checks and boundaries

Use `python -m pytest -q tests/test_guided_missions.py` for focused
regressions, and `python -m pytest -q` for the entire RPG. The new tests
validate battle/scenario integration and legal actions without requiring the
unfinished hooks to return a particular solution: a student who correctly
implements a mission should not break the scaffold tests.

The pygame graphical path can only be checked on a computer with pygame
installed. The headless content check (`python main.py --check`) and the
teaching labs run without a display. Keep the six older lesson documents
and the team-arena competition exercises available as independent tracks.
