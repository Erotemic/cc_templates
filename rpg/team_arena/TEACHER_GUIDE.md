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

A private reference controller using **only the documented** `turn` API was
rerun after replacing Tap with ordinary Attack. All results below are from
the actual engine, with 20 seeds and swapped team seats (40 games per
opponent). The reference is not included in student files, examples, or tests.

| Opponent | Seeds 0–19 | Seeds 77–96 | Seeds 151–170 |
|---|---:|---:|---:|
| first_target | 100% | 100% | 100% |
| weakest_first | 100% | 100% | 100% |
| cautious | 100% | 100% | 100% |
| rotating | 100% | 100% | 100% |
| heavy_hitter | 100% | 100% | 100% |
| crowd_control | 95% | 90% | 92.5% |
| engine_heuristic | 85% | 87.5% | 82.5% |

The pass criterion is **at least 80% against each opponent separately**, with
no unfinished games. This is a repeatable finite benchmark, not a guarantee
of optimal play against arbitrary strategies. The examples intentionally have
weaknesses; a simple effective strategy can beat them. A new prefab example
will **not silently change** this challenge; update the named roster and
revalidate any change deliberately.

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
- **D (draw):** a completed tie, if the engine later supports one; 0.5 point.
- **U (unfinished):** reached `--max-steps` with no winner; **0 points for
  both controllers**. Infinite defense does not gain draw points.
- **Error/timeout:** stops the fixture with a diagnostic; not counted as a
  result. Correct the file before publishing the standings.

Results depend on the exact controller files and seed set. Freeze submissions
for the final, choose a seed range, and record that range in the CSV's name or
alongside it. The published `--seed 77` range is a follow-up comparison, **not
an undisclosed test**.

## Operational boundaries

The same `simulate_once()` engine loop now powers both the headless scorer and
recordings. The viewer uses prerecorded decisions and only stores RNG
checkpoints for decisions that consume the battle generator, reducing replay
size. **R reruns saved code** in a bounded subprocess; **P** plays the old
recording. Student prints are limited per decision, and process output is
file-backed so a runaway printer cannot exhaust the parent's RAM.

Process timeouts guard against accidental endless loops, **not malicious
Python**. Only execute code you trust or run untrusted submissions in separate
restricted operating-system containers/accounts without instructor secrets.
For the animated game, `python -m pip install -e ".[classroom]"` provides
pygame and classroom test dependencies. Headless tests can run without it.
