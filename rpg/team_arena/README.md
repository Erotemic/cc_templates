# AI Team Arena — make your code fight

**Start with one file:** [`players/my_team.py`](players/my_team.py). Your team
controller is a Python function called `choose_action(turn)`. Both fighters on
your team call it when their turn arrives. The game handles everything else.
No machine learning or online service is involved.

## 1. Watch your code

From the **`rpg` directory**, run:

```bash
python arena.py
```

You'll see your team (`my_team`) battle `first_target`. Each side is labeled
with its Python controller filename. The active fighter's action and your
`print(...)` messages appear in the **Controller Console** while the real RPG
animations play. A VS Code task named **RPG Arena: Watch** does the same thing.

**Edit** `team_arena/players/my_team.py`, **save**, then press **R** in the
battle window. R reruns the saved code in a separate timeout-limited process and
starts a **new** fight. If you make an error, the previous battle stays open
and the terminal explains the error. Fix it, save, and press R again.

| Key | What it does |
|---|---|
| **R** | Rerun your saved Python code (same teams and seed) |
| **P** | Replay the existing recorded fight *without* running code again |
| **Space** | Pause/resume |
| **N** | While paused, advance one decision and its animation |
| **+ / -** | Speed up / slow down |
| **Esc** | Close the battle window |

Want a different opponent? `python arena.py watch my_team heavy_hitter --seed 4`

## 2. Your whole programming interface

```python
def choose_action(turn):
    print("I am", turn.user.name, "with", turn.user.hp, "HP")
    return turn.attack(target=turn.enemies[0])
```

- `turn.user` — the fighter acting right now.
- `turn.enemies` / `turn.allies` — living opponents / other teammates.
- `turn.available_move_ids` — learned skills this fighter knows.
- `turn.round_number` — current round (starting at 1).
- A fighter has `name`, `hp`, `max_hp`, `hp_ratio`, `attack`, `defense`,
  `magic`, `speed`, and `statuses`.
- `turn.attack(target=enemy)` — regular physical Attack; every fighter can do it.
- `turn.defend()` — defend; every fighter can do it.
- `turn.skill("arena_crush", target=enemy)` — use a learned skill. Only choose
  skills in `turn.available_move_ids`. The older `turn.use(...)` still works.

**Both characters have different skills.** Try `python arena.py moves` to see
what each knows. Attack and Defend are always available, not listed as skills.
Some skills affect every enemy (omit `target`); healing skills need an ally or
`turn.user` as their target.

## 3. Experiment and compete

```bash
python arena.py battle my_team first_target --runs 4
python arena.py challenge my_team
python arena.py new my_second_team --from my_team
python arena.py tournament --csv class_results.csv
```

- **battle** compares controllers over multiple seeds, swapping team sides.
- **challenge** requires at least **80% score against each of seven fixed
  prefabs**, with no unfinished matches. This is achievable, not a guarantee
  about other opponents or random seeds.
- **new** makes a new editable file; it **will not overwrite** an old one.
- **tournament** runs a round robin of student files in `players/` by default.
  The quick default is two seeds per side. Use `--runs 20` for final scoring;
  add `--include-prefabs` to include examples. Pairings and progress are shown.

A match stopped at the step limit is **unfinished (U)**, not a draw. It earns
neither side points. Completed draws (D) would award half a point, but this RPG
currently has no drawn-battle ending. Errors and timeouts stop the fixture and
are **not counted as losses**.

### Where to go next

[STUDENT_PROJECTS.md](STUDENT_PROJECTS.md) has six projects with observable
features to add to your controller. The instructor-only tournament setup is
in [TEACHER_GUIDE.md](TEACHER_GUIDE.md). Read the small examples in
[`prefabs/`](prefabs/) whenever you need inspiration.

### Setup and safety

The visual game requires pygame. From the `rpg` directory, install with:

```bash
python -m pip install -e ".[classroom]"
```

`python arena.py battle` also runs without a graphical display. Student code
runs in a separate process so accidental endless loops can time out. **This
is not a security sandbox:** run only reviewed/trusted student programs, or
use OS isolation for submissions from untrusted users.
