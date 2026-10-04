# RPG Python Cheatsheet

Keep this open while working in `student_game/workshop.py`. You do not need to
memorize the API.

## Read battle facts

```python
ctx.user.hp
ctx.user.max_hp
ctx.user.hp_ratio
ctx.user.attack          # effective value used right now
ctx.user.base_attack     # character-sheet value
ctx.user.statuses

ctx.target               # first target, or None
ctx.targets              # all targets
```

`attack`, `defense`, `magic`, and `speed` are effective values. `base_attack`,
`base_defense`, `base_magic`, and `base_speed` are the unmodified values.

## Tell the engine what should happen

```python
return damage(10)
return damage(10, magical=True)
return heal(12, target="user")
return add_status("burn", turns=2)
return change_stat("defense", 1)
```

Valid command targets are:

```python
"user"
"targets"
a_target_from_ctx_targets
```

Misspelled target names are errors; they never silently choose a different
battler.

## Conditional pattern

```python
def my_move(ctx):
    low_health = ctx.user.hp_ratio < 0.5
    if low_health:
        return damage(18)
    return damage(8)
```

The workshop uses `ctx.observe("low_health", low_health)` when it wants the lab
to display a named intermediate fact. The name is only a label; the Python
expression determines the value.

## Loop pattern

```python
def my_move(ctx):
    commands = []
    for target in ctx.targets:
        commands.append(damage(8, target=target))
    return commands
```

## Enemy strategy pattern

```python
def my_strategy(turn):
    if turn.user.hp_ratio < 0.3:
        return turn.defend()

    target = turn.enemies[0]
    for enemy in turn.enemies[1:]:
        if enemy.hp_ratio < target.hp_ratio:
            target = enemy

    return turn.use(moves.arc_bolt, target=target)
```

## Scripted move power

For a normal move, `power=10` is the power the engine uses.

For a move with `action=my_function`, the function's returned `damage(...)` or
`heal(...)` command controls the real amount. If computer-controlled characters
need a rough strength estimate for that scripted move, use `ai_power=...`.

## Fast feedback

```bash
python main.py --check
python lab.py scenario threshold_25
python lab.py scenario chain_lightning
python main.py --scenario threshold_25 --teach
python simulate.py --scenario balance --runs 50
```

The default lab output stays focused on your Python and the visible result. Add
`--engine-details` when you want the effective stats, damage/healing formula,
normalized commands, and battle events:

```bash
python lab.py scenario threshold_25 --engine-details
```

Add `--debug-traceback` when you intentionally want the full Python traceback
from a student-authored runtime function.
