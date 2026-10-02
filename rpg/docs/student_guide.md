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

The lab uses the real rules engine. It separates:

1. the input facts;
2. values/conditions observed by the function;
3. the function's original return value;
4. the normalized commands the engine executes;
5. the actual damage/healing calculation;
6. the resulting HP changes.

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
which scripted command powers actually ran.

## What custom move fields mean

For a normal declarative move, `power=` controls the engine calculation.

For a move with `action=my_function`, the commands returned by the function
control the real behavior. For example:

```python
def my_function(ctx):
    return damage(18)
```

Here `damage(18)` controls the damage power. A `power=` value on the `Move`
remains useful to the built-in AI as an estimate, but changing it does not
change the command your Python function returns. `python main.py --check`
prints a teaching note when this distinction matters.

## Effective versus base stats

Student scripting views expose both:

```python
ctx.user.attack       # effective attack used by the rules right now
ctx.user.base_attack  # original character-sheet attack
```

Burn, temporary stat changes, guarding, and similar mechanics can make them
different. The move lab prints both when relevant.

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

The workshop demonstrates registration for every supported content type:

```python
PALETTES = [...]
SPRITES = [...]
EFFECTS = [...]
SOUNDS = [...]
MUSIC = [...]
MOVES = [...]
CHARACTERS = [...]
TEAMS = [...]
BATTLES = [...]
```

`student_game/catalog.py` combines all of these workshop lists with the larger
reference game. That means original workshop art/audio/effects are first-class
registered game content rather than one-off objects that fail validation later.

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
