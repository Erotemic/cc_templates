# Team controller tournament — instructor notes

**Vocabulary:** Students write an **AI team controller**, meaning a small
hand-written decision algorithm. We make no claims about machine learning.

### Lesson boundaries

All activity lives in `team_arena/` and the new `arena.py` entry point. The
original game and workshop stay in place. Prefabs are intentionally imperfect
and short enough to read during a lesson; students copy one into `players/`
and experiment there. The same function decides for both roles, teaching
students to check move availability and observe battle facts.

Use [STUDENT_PROJECTS.md](STUDENT_PROJECTS.md) for the printable worksheets.
Students should **not** be shown a worked solution to Project 4: it is a
discovery task. However, the pass requirement has been validated rather than
invented from intuition.

### Known-outcome challenge and validity

For the supplied content, a controller that makes sensible role-specific
attack choices and focuses danger can clear the Project 4 target. The
benchmark was checked on both seat orientations using the actual simulator.
The opponent list includes **all** `team_arena/prefabs/*.py` plus the
`engine_heuristic` fallback in the existing RPG. No enemy is allowed stronger
stats, a different team, or illegal actions.

The **published pass requirement** is 80% points (wins + half draws) against
**every prefab separately** over seeds 0–19 with both orientations. This is a
meaningful finite benchmark, not a mathematical guarantee of winning every
future seed or of being unbeatable by another student.

An independently authored reference controller was tested with the exact
arena balance distributed in this overlay. The percentages below are from
40 games *per opponent, per seed range* (20 seeds x two seats). The reference
implementation is deliberately **not** included in the student material.

| Prefab | Seeds 0-19 | Seeds 77-96 |
|---|---:|---:|
| `first_target` | 100% | 100% |
| `weakest_first` | 100% | 100% |
| `cautious` | 100% | 100% |
| `rotating` | 100% | 100% |
| `heavy_hitter` | 100% | 100% |
| `crowd_control` | 95% | 90% |
| `engine_heuristic` | 97.5% | 100% |

These are empirical regression baselines, not promised student scores. Some
student controllers may find different tactics that work better or worse.

To reproduce a grade, always use one shared command, such as:

```bash
python arena.py challenge contender --runs 20 --seed 0
```

For a **holdout check** after students develop using seed 0, use `--seed 77`.
This is useful to illustrate overfitting to a finite seed set; it should not
be described as an unseen test if the seed has already been disclosed.

### Facilitating projects

| Project | Expected added behavior | Suggested grading evidence |
|---|---|---|
| 0 | Student-authored function controls a fighter | Event log shows a new action |
| 1 | Legal moves differ between team roles | 80% score vs `first_target` |
| 2 | Target choice responds to battle facts | 80% score vs `heavy_hitter` plus explanation |
| 3 | Reasoned policy for group vs focused damage | 80% score vs `crowd_control` plus explanation |
| 4 | One general controller beats all prefabs | `challenge` passes each row, not just average |
| 5 | Experimental result with fixed seeds | CSV + comparison of prediction to data |

Scores alone do not measure whether the student used the intended programming
concept. Combine the empirical result with a code review or short explanation.
The starter examples are **not** full reference solutions and need not beat
each other in a particular order.

### Classroom tournament settings

Select student controllers explicitly when possible:

```bash
python arena.py tournament first_target heavy_hitter crowd_control contender --runs 20 --seed 71 --csv arena_results.csv
```

- Keep `--runs`, `--seed`, roster, and code snapshot constant for everyone.
- One seed is played from each orientation to limit seat advantage.
- Display wins/losses/draws *and* score; draws count half a point.
- If student code raises, calls an unavailable move, or times out, the fixture
  stops with an error. The operator fixes the file, not silently records
  losses. Tournament CSV is written only after a complete successful run.
- Runner error timeout is per pairing (default 30s), so adapt it to slow PCs.
- The worker helps with mistakes such as `while True`, but it is not secure
  against malicious Python. Do not execute unknown submissions with the
  instructor's credentials or network privileges. Use isolated restricted
  environments for untrusted participants.
- The engine uses Python module-level RNG seeding for local `random` calls;
  student code should otherwise be stateless and only use `turn`.

### Future expansions (not required for this overlay)

Graphical replays, multiple arenas, alternate starting rosters, tournament
brackets, and true sandboxing are separate features. Keeping the first release
headless makes students' code edits and measured outcomes central.

## Projector-friendly visual matches and print() debugging

The headless tournament is for scoring many matchups. For a class exhibition,
open any one pairing in pygame:

```bash
python arena.py watch my_team crowd_control --seed 71 --speed 2
python arena.py watch first_target weakest_first --seed 5
```

Both teams use the normal RPG's character animations, sound, health bars and
attack effects. The **top of each team panel** identifies its controller and
source file; the active panel is outlined. The **Controller Console** shows
which fighter is executing `choose_action`, its choice, and the student's
`print()` messages, replayed with that exact decision. Messages are also
printed to the terminal, prefixed with controller/source/round/actor. The
normal battle log remains visible on the right.

A useful warm-up is to have students add `print(turn.user.name, turn.user.hp)`
to their own file, then ask them to predict the next action *before* it happens.
SPACE pauses; +/- changes speed; R replays the same recorded fight; ESC closes.

Each spectator match is first simulated in a time-limited worker. The pygame
process receives a recording of moves and prints, and never executes student
functions itself. Thus an accidental `while True` raises a timeout before
opening the window rather than freezing a displayed battle. This is **not a
security sandbox** for malicious code: review submissions and use appropriate
OS isolation for untrusted student programs. Long tournaments stay headless.
On each code change, relaunch `watch` to regenerate the recording. Windows
require pygame; install with `python -m pip install -e ".[classroom]"`.
