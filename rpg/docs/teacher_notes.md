# Teacher Notes

## Teaching objective

The RPG should support a long runway inside one coherent project. A student can
begin by changing a number in a short file and later program control flow,
loops, algorithms, procedural graphics, mathematical functions, simulations,
and engine internals.

The project is intentionally richer than a minimal tutorial. We reduce the size
of the **starting surface**, not the capability of the underlying game.

## The starting surface

Use `student_game/workshop.py` first.

It is intentionally small and contributes directly to the full `Game` catalog:

```text
student_game/workshop.py
       +
student_game/{moves,characters,art,effects,audio,battles}.py
       |
       v
rpg_battle.api.Game.compile()
       |
       v
validated GameContent
       |
       v
engine (rules / AI / rendering / audio)
```

There is no separate tutorial engine. A concept learned in the workshop carries
into the complete game.

## Three feedback loops

The project now deliberately offers three different feedback loops.

### 1. Validation

```bash
python main.py --check
```

Use this for syntax/content authoring sessions. Custom move functions are
smoke-tested against several deterministic read-only contexts. Structural
mistakes such as returning an integer instead of `damage(...)` appear in the
validation report with the function's source location.

### 2. Deterministic move lab

```bash
python lab.py move workshop_power_strike --user-hp 50 --seed 3
python lab.py move workshop_power_strike --user-hp 10 --seed 3
```

This is the preferred tool when teaching variables, expressions, `if`, return
values, and debugging. It executes the actual rules engine, not a duplicate
formula.

For loops and per-object decisions:

```bash
python lab.py move workshop_chain_lightning \
    --target spirit --target guardian --target-status 2:burn --seed 3
```

### 3. Play and observe

```bash
python main.py --encounter workshop --teach
```

`--teach` prints a high-level trace only when student-authored move functions or
AI strategies execute. Keep `RPG_BATTLE_LOG_LEVEL=DEBUG` as the deeper engine
trace for students who are ready for it.

## Suggested progression

### Values and prediction

Change HP, power, thresholds, colors, or sound frequency. Require a prediction
before the run.

### References and composition

Swap `Move`, `Character`, `Sprite`, `Music`, and `Team` objects. Reinforce that a
variable can refer to a structured object and that programs are composed from
those references.

### Conditionals

Use `power_strike_logic`. Compare two fixed-seed lab runs on opposite sides of
the threshold.

### Loops and lists

Use `chain_lightning_logic`. `BattlerView` objects can safely be passed back as
specific command targets, which makes `for target in ctx.targets:` genuinely
useful rather than decorative syntax.

### Algorithms

Modify `practice_enemy_strategy`. Students can implement threshold policies,
priority rules, target selection, and multi-phase boss behavior using ordinary
Python. Strategy code receives read-only state and returns an action choice.

### Geometry and mathematics

Move into procedural sprites and path effects once students have a reason to
use coordinates, functions, and iteration.

### Experiments and statistics

Use:

```bash
python simulate.py --encounter workshop --runs 100 --seed 0
```

Hold the seed range constant across a change. Discuss independent variables,
randomness, sample size, averages, and why one anecdotal playthrough does not
measure game balance.

### Software architecture

Trace a workshop object through `api.py`, normalized specs, `GameContent`, and
then `rules.py` or `ai.py`. Discuss why the engine accepts content rather than
importing the shipped game.

## Read-only scripting boundary

Move functions receive `MoveContext` / `BattlerView` objects and return command
objects. AI functions receive `TurnContext` and return `turn.use(...)` or
`turn.defend()`.

This is deliberate:

- students write normal control flow;
- functions are easy to run deterministically;
- engine mutation remains centralized;
- one bad function cannot arbitrarily corrupt unrelated battle state;
- later lessons can inspect the implementation of that boundary.

The boundary is a teaching aid, but it is also legitimate software design.

## Keep the engine rich

Do not remove advanced content merely because a beginner does not understand it
yet. Distinguish:

- what students are expected to edit now;
- what they may reuse without understanding yet;
- what they can inspect when they want to go deeper.

The large `student_game/*.py` files are now primarily **libraries and examples**.
Their size is no longer the beginner's starting cognitive load.

## Good project prompts

- Make Power Strike have three health ranges instead of two.
- Write a multi-target move that makes a decision separately for each target.
- Program a boss with at least two visible phases.
- Make an enemy target the battler for which its chosen move is most effective.
- Design a three-character party with distinct roles.
- Create a sprite from at least three geometric primitive types.
- Implement and visualize a mathematical function as a spell path.
- Run 100 fixed-seed simulations before and after a balance change and explain
  what the data does and does not show.

## Advanced areas

These remain appropriate for deeper students or instructor-guided exploration:

- `src/rpg_battle/core/rules.py`
- `src/rpg_battle/core/ai.py`
- `src/rpg_battle/core/scripting.py`
- `src/rpg_battle/battle/battle_scene.py`
- `src/rpg_battle/audio/tracks.py`
- `src/rpg_battle/render/`

They are not off-limits; they simply are not prerequisites for creating
meaningful new content.
