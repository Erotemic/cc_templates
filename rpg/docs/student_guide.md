# Student Guide: Learn Python by Building an RPG

This project is a real battle game, but you are not expected to understand the
whole engine before making something interesting.

Start in:

```text
student_game/workshop.py
```

Keep [CHEATSHEET.md](CHEATSHEET.md) nearby.

## First feedback loop

Before playing, check your game:

```bash
python main.py --check
```

Then use a deliberate experiment instead of hoping a normal battle happens to
exercise your code:

```bash
python lab.py scenario threshold_25
python lab.py scenario chain_lightning
python lab.py scenario target_selection
```

The lab uses the real rules engine. Its default view stays focused on the
programming idea:

1. the input facts;
2. values/conditions observed by the function;
3. the function's return value;
4. the resulting HP changes.

When you want to inspect how the engine turns a returned command into exact
damage or healing, add `--engine-details`:

```bash
python lab.py scenario threshold_25 --engine-details
```

Play the same setup with:

```bash
python main.py --scenario threshold_25 --teach
```

Restarting the battle reuses the same seed and scenario state so you can compare
an edit against the same starting conditions.

## Common lessons

Follow [lessons/README.md](lessons/README.md) for the shared programming path:

- read and predict existing code;
- investigate boundary values;
- write conditionals from specifications;
- trace loops and build result lists;
- diagnose syntax/runtime/logic bugs;
- design a decision-making algorithm;
- create and explain an original behavior.

After that, choose a project direction from [projects.md](projects.md).

## Named scenarios

### Threshold boundaries

```bash
python lab.py scenario threshold_25
python lab.py scenario threshold_26
python lab.py scenario threshold_27
```

These make `<` versus `<=` visible around exactly half of 52 HP.

### Loop decisions

```bash
python lab.py scenario chain_lightning
```

There are two targets and exactly one starts burned, so both branches of the
loop execute.

### Target-selection algorithm

```bash
python lab.py scenario target_selection
```

The two possible targets are deliberately chosen so “lowest raw HP” and
“lowest HP ratio” give different answers.

### Healing references

```bash
python lab.py scenario healing
```

The Druid and an ally both start injured. The move lab constructs a real ally
relationship for this move; it does not pretend an opponent is an ally target.

### Balance experiment

```bash
python simulate.py --scenario balance --runs 50
```

The simulator reports wins, rounds, remaining HP, damage, move counts, and
which scripted damage/healing commands were returned, including attacks that
missed. Direct damage totals count actual HP lost and exclude status ticks.
Battles reaching the simulation step limit are reported as unfinished; use
`--max-steps` to change that limit.

## What custom move fields mean

For a normal declarative move, `power=` controls the engine calculation.

For a move with `action=my_function`, the commands returned by the function
control the real behavior. For example:

```python
def my_function(ctx):
    return damage(18)
```

Here `damage(18)` controls the damage power. Scripted moves therefore do not
accept `power=` at all. If a computer-controlled character needs a rough
strength estimate when choosing among scripted moves, use the explicitly named
`ai_power=` field instead. That estimate never changes what the function
returns.

## Effective versus base stats

Student scripting views expose both:

```python
ctx.user.attack       # effective attack used by the rules right now
ctx.user.base_attack  # original character-sheet attack
```

Burn, temporary stat changes, guarding, and similar mechanics can make them
different. Add `--engine-details` in the move lab when you want to inspect both.

## Debugging

`--check` executes student behavior functions in deterministic contexts *only
when you explicitly request a check*. Merely importing/compiling the game does
not run your move or AI functions.

If student runtime code crashes during a played battle, the launcher shows a
short source-aware error. To see the complete traceback:

```bash
python main.py --scenario threshold_25 --debug-traceback
```

## Creating completely new content

The first file stays small on purpose:

- `student_game/workshop.py` contains the move functions, character, and simple
  strategy used in the common lessons;
- `workshop_assets.py` contains the workshop's palette, sprite frame, effect, sound,
  and music;
- `workshop_battles.py` contains teams and battles.

Together they demonstrate registration for every supported content type without
putting all of that wiring in front of a student learning their first
conditional. `student_game/catalog.py` combines those lists with the larger
reference game, so original workshop content remains first-class registered
game content.

## Going deeper

When you want to know *why* something happens, follow one question downward:

```text
student_game/workshop.py
  -> rpg_battle.api
  -> core.scripting
  -> core.rules / core.ai
```

For example, search for `_damage_calculation` in `core/rules.py` after the lab
has shown you the same calculation as a readable trace.
