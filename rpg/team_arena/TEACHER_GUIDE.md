# Instructor notes — AI Team Arena

Students edit **only** `team_arena/players/my_team.py` at first. The arena is a
regular Python team-controller function, not machine learning. The recommended
first lesson is: **open file → run `python arena.py` → edit → save → press R →
watch the changed decision and its prints**. A VS Code task launches the same
window. Use N while paused to study a single decision and its animation.

For student projects, see [STUDENT_PROJECTS.md](STUDENT_PROJECTS.md). Each
project asks for observable behavior, not particular source text. Score alone
does not prove a student has implemented targeting or group-vs-single logic;
watch their fight and ask them to explain what their code observed.

## Known-outcome final challenge

`python arena.py challenge my_team --runs 20 --seed 0` evaluates **seven
frozen opponents**: `first_target`, `weakest_first`, `cautious`, `rotating`,
`heavy_hitter`, `crowd_control`, and `engine_heuristic`.

A private reference controller using **only the documented** `turn` API
was re-evaluated after adding mana. The currently published challenge uses
20 seeds and swapped seats (40 games per opponent), starting at seed 0.
The private controller is **not** included in student files or tests.

| Opponent | Score (seeds 0–19) |
|---|---:|
| first_target | 100% |
| weakest_first | 100% |
| cautious | 100% |
| rotating | 100% |
| heavy_hitter | 85% |
| crowd_control | 92.5% |
| engine_heuristic | 80% |

The exact challenge remains achievable on the published seed range. Other
seed ranges produced different results (in particular the heuristic and
crowd-control opponents can be harder), so do **not** retain the old
pre-mana success claims. Winning one finite evaluation is not proof of a
universally strong algorithm. Students should validate improvements on a
second seed range, and instructors may use larger samples for finals.

Mana changes the objective: every fighter has an individual, persistent MP
pool; Skills cost MP; Attack restores up to 3 MP; Defend restores up to 7 MP.
Student policies must select legal affordable moves. The published baseline
controller is deliberately elementary, so Project 4 explicitly exercises
resource decisions apart from overall tournament scoring.

The pass criterion remains **at least 80% against each opponent separately**,
with no unfinished games. The roster is fixed; adding new prefab examples
will not silently change grading.

## Class tournament

```bash
python arena.py tournament --runs 2 --seed 71 --csv class_results.csv
python arena.py watch my_team contender_v2 --seed 71
```

By default the tournament includes **student files only**, plus `first_target`
when there is just one student. Use explicit names to curate entrants or
`--include-prefabs` to add all example controllers. Defaults are short so 24
students don't require thousands of games before getting a first result.
Increase `--runs` for a final. The tool prints the number of fixtures and
progress, and swaps seats for each seed.

- **Wins/losses:** ordinary completed battles.
- **D (draw):** a completed simultaneous knockout; 0.5 point.
- **U (unfinished):** reached `--max-steps` with no winner; **0 points for
  both controllers**. Infinite defense does not gain draw points.
- **Error/timeout:** stops the fixture with a diagnostic; not counted as a
  result. Correct the file before publishing the standings.

Results depend on the exact controller files and seed set. Freeze submissions
for the final, choose a seed range, and record that range in the CSV's name or
alongside it. The published `--seed 77` range is a follow-up comparison, **not
an undisclosed test**.

## Operational boundaries

The same `BattleSession` lifecycle powers the headless scorer, normal pygame
game, and arena replay. `simulate_once()` also supplies the recorder's
student-choice/print hooks. The viewer uses prerecorded decisions and only stores RNG
checkpoints for decisions that consume the battle generator, reducing replay
size. **R reruns saved code** in a bounded subprocess; **P** plays the old
recording. Student prints are limited per decision, and process output is
file-backed so a runaway printer cannot exhaust the parent's RAM.

Process timeouts guard against accidental endless loops, **not malicious
Python**. Only execute code you trust or run untrusted submissions in separate
restricted operating-system containers/accounts without instructor secrets.
For the animated game, `python -m pip install -e ".[classroom]"` provides
pygame and classroom test dependencies. Headless tests can run without it.
