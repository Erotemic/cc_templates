# Teacher Notes

## Teaching objective

The RPG is intended to support grades 9–12 with different prior experience
inside one coherent project. Differentiate by demonstrated knowledge, not grade
number alone.

The central requirement is **trustworthy causal feedback**: when a student
predicts what code will do, the check/lab/game should agree about the semantics.

## Validation has two explicit layers

### Structural validation

Importing/compiling `student_game` checks references, ids, target modes, art,
audio, teams, and battles. It does **not** execute student behavior functions.

### Behavior validation

```bash
python main.py --check
```

also runs custom move and AI functions in deterministic contexts that match the
move's targeting rules and encounter rosters. A multi-target move can receive
one target when only one is active; all-allies moves include the user. The
checker also validates named scenario setup without executing its behavior.

This distinction makes it easier to explain *when* student code runs.
Smoke checks sample a few situations; they do not prove that every branch is
correct. Use deliberate scenarios to investigate specific cases.

## Trustworthy scripting contracts

- misspelled command targets are rejected; they never fall through to an
  opponent;
- runtime command validation uses the same rules as `--check`;
- `BattlerView.attack/defense/magic/speed` are effective values used by the
  engine;
- `base_attack/base_defense/base_magic/base_speed` expose original stats;
- AI strategies cannot choose an illegal explicit target for a move;
- declarative moves use `power=`, while scripted moves use `ai_power=` only for
  computer move-selection estimates; the API rejects the misleading combination
  of `power=` with `action=...`;
- scripted moves return status/stat commands instead of mixing an `action`
  function with declarative `effects=[...]`.

## The move lab explains the real engine

The default lab view shows only the inputs, named intermediate observations,
function return, and visible result. This keeps early conditional/loop lessons
focused on the code students are expected to understand.

When deeper inspection is useful, add `--engine-details`. Those damage/healing
details are emitted by `core/rules.py` while the move actually resolves. Do not
duplicate the damage formula in worksheets.

Use:

```bash
python lab.py scenario threshold_25
python lab.py scenario threshold_26
python lab.py scenario threshold_27
python lab.py scenario chain_lightning
python lab.py scenario threshold_25 --engine-details
```

Require a prediction before execution and an explanation afterward.

## Deliberate scenarios

The default gentle workshop battle remains useful for play, but concept lessons
use purposeful setups:

- **threshold_25 / 26 / 27** — boundary conditions;
- **chain_lightning** — two loop iterations, exactly one burned target;
- **target_selection** — raw HP and HP ratio disagree;
- **healing** — injured self and injured ally;
- **balance** — 2v2 experiment where outcomes and scripted branches vary.

The same scenario can be inspected and played:

```bash
python lab.py scenario chain_lightning
python main.py --scenario chain_lightning --teach
```

## Common curriculum

Use [lessons/README.md](lessons/README.md) rather than treating a feature ladder
as the curriculum. The common sequence progresses from supported reading to
independent programming and includes explicit debugging.

Every lesson has prerequisites, prediction, investigation, modification,
independent work, and explanation/transfer. Expected results and common
misconceptions are in [lessons/teacher_key.md](lessons/teacher_key.md).

## Parallel project paths

After the common sequence, let students choose mechanics/boss design,
procedural art, mathematical effects, sound, balance experiments, or software
engineering. See [projects.md](projects.md).

This lets students use the same language concepts for different creative
interests instead of forcing every student through AI, trigonometry, and audio
in the same order.

## Repeatable experiments

`BattleController.restart()` resets the RNG to the battle's original seed.
`--scenario` also reapplies the initial HP/status setup. This makes classroom
comparisons reproducible.

The simulator reports policies and multiple outcomes:

```bash
python simulate.py --scenario balance --runs 50
```

Discuss that reusing seeds reproduces an experiment setup; code changes can
consume random draws in a different order, so seeds do not promise event-by-
event alignment across different programs.

## Classroom workflow

See [setup.md](setup.md). If using VS Code, `.vscode/tasks.json` exposes Check,
Lab, Play, Preview, and Simulate without requiring students to repeatedly type
long commands.

Before a course, validate a known-good environment and freeze it for that term.
For the first classroom use, follow [classroom_pilot.md](classroom_pilot.md) and
measure setup time, time to first meaningful edit, prediction/explanation,
independent debugging, and transfer to a new problem.
