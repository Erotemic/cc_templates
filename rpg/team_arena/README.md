# Algorithm Arena — RPG team controllers

A small **AI programming tournament** inside the same RPG engine as the full
game. Here, *AI* means a regular Python function that looks at the current
battle and chooses an action. We call the function a **team controller**.
No machine learning, API key, or generative AI is required.

## One-minute start

Run these commands **from the `rpg` directory**:

```bash
python arena.py list
python arena.py moves
python arena.py battle first_target weakest_first --runs 4 --log
python arena.py battle my_team first_target --runs 4 --log
```

Now open `team_arena/players/my_team.py`. Change its one function, save, and
re-run the last command. The two teams have the same character stats, moves,
and starting HP, so the **controller decisions** determine the difference.

For a new experiment that will not erase your previous work:

```bash
python arena.py new clever_team --from first_target
python arena.py battle clever_team cautious --runs 12
python arena.py challenge clever_team --runs 20
```

The `new` command refuses to overwrite an existing file. It copies the
example into `team_arena/players/` so the prefabs remain unchanged.

## Watch your code fight (animated)

**Recommended first activity:** open a real battle window, then make a print
statement appear there. The **left and right controller names**, their Python
**source-file paths**, and the currently acting controller are shown above the
fighters. The **Controller Console** in the lower-left shows what each
controller chose and the lines it printed; the lower-right shows the normal
battle log. Characters animate moves, damage, HP changes, and knockouts using
the original pygame RPG art and battle rules.

```bash
python arena.py watch my_team first_target --seed 3
```

Open `team_arena/players/my_team.py`. Add these lines **inside**
`choose_action(turn)`, before the existing return:

```python
print("I am controlling", turn.user.name)
print("Round", turn.round_number, "HP", turn.user.hp)
```

Save and run the same `watch` command again. Watch your messages appear under
the name **my_team** as the left-side fighters make decisions. They also appear
in the terminal with the source filename and chosen move. Only edit your
own controller; the engine and opponent controller stay unchanged.

**Controls:** SPACE pause/resume, `+`/`-` change speed, R replay the same
recorded match, ESC close. Use `--speed 2` (or up to 8) for a faster match.
Changing the seed changes the fight; re-running after editing your code records
its new decisions.

The viewer first **records one real match in a time-limited subprocess**, then
plays those decisions back with the game's animations. This protects the
window from getting stuck if a student accidentally writes an endless loop.
It's a replay, not a live Python debugger; edits take effect when you close
and launch a new recording. The visual replay never runs student code.
`print()` inside `choose_action` is recorded with its turn; outputs are bounded
per turn to keep the display responsive. Regular tournaments stay headless.

If pygame is missing, install the project from this `rpg` directory:

```bash
python -m pip install -e ".[classroom]"
```

## Your controller's entire API

```python
def choose_action(turn):
    return turn.use("arena_tap", target=turn.enemies[0])
```

This function is called on **every turn** for **both characters** on your
team. It must return **one** of these: `turn.use(move, target=...)` or
`turn.defend()`.

| You can read | Meaning |
|---|---|
| `turn.user` | Fighter acting right now |
| `turn.enemies` | Living enemies on the battlefield (a tuple) |
| `turn.allies` | Other living allies (does not include `turn.user`) |
| `turn.round_number` | Battle round, starting at 1 |
| `turn.available_move_ids` | Moves this fighter actually knows |
| `fighter.hp`, `fighter.max_hp`, `fighter.hp_ratio` | Current health facts |
| `fighter.attack`, `fighter.defense`, `fighter.magic`, `fighter.speed` | Current effective stats |
| `fighter.base_attack`, etc. | Starting stats, ignoring temporary modifiers |
| `fighter.statuses` | Active status names |
| `turn.defend()` | Guard until the game's rules remove guarding |
| `turn.use("arena_crush", target=enemy)` | Use a move the current fighter knows |

Read `python arena.py moves` for the two characters and their **six move
identifiers**. For group-target moves, omit `target`. For single-ally healing,
pass the fighter to heal; it may be `turn.user` or an entry of `turn.allies`.

**Common mistake:** your mage cannot use `arena_crush`. Check membership in
`turn.available_move_ids` before choosing a move that only one fighter has.
**Common mistake:** all teammates do *not* take actions together: the function
runs once per actor's turn.

## Predict, test, improve

1. Open one of `team_arena/prefabs/*.py`. These are deliberately small and
   imperfect, with a specific strength or weakness to notice.
2. Create a new controller with `python arena.py new ...`.
3. Write down a prediction: *What observable change should my controller make?*
4. Run a comparison, look at the wins and losses, and change only one thing.
5. Run the **same seed and runs** again to make a fair comparison.

```bash
python arena.py battle clever_team crowd_control --runs 20 --seed 0
python arena.py challenge clever_team --runs 20 --seed 0
python arena.py tournament clever_team first_target heavy_hitter crowd_control --runs 10
```

Each seed is played twice with left/right team positions reversed. Draws count
half a point. Randomness in damage means **no single game is proof of skill**.
The challenge passes when the controller scores at least **80% against each
prefab separately** on the requested seeds. This is a classroom benchmark,
not a guarantee against every possible opponent or random seed.

For whole-class competitions, explicitly list the entrants or omit them to
include every prefab and every student controller in the directory:

```bash
python arena.py tournament --runs 20 --seed 71 --csv arena_results.csv
```

The CSV stores scores for a spreadsheet or classroom scoreboard. Student
project prompts are in [STUDENT_PROJECTS.md](STUDENT_PROJECTS.md); the
instructor's benchmark notes are in [TEACHER_GUIDE.md](TEACHER_GUIDE.md).

## About code safety and reliable scoring

- Built-in controllers are teaching opponents, **not** optimized opponents.
  Their known weaknesses make measurable beginner projects possible.
- Matches run without graphics, using the RPG's real damage and status rules.
  There is no separate toy combat formula.
- A fresh **worker process per matchup** limits hangs from an accidental
  infinite loop. The default is 30 seconds per fixture; use `--timeout 60`
  for slower classroom computers. A fixture that raises or times out is
  reported as an error, **never silently counted as a loss**.
- This process limit is **not a secure sandbox**. Review code before running
  students' Python files on a shared instructor computer. Use separate
  restricted accounts/containers for submissions from untrusted people.
- Avoid persistent module-level state between calls; your function should
  decide from `turn`. Built-in engine and module-level Python randomness are
  seeded for replay, but arbitrary outside services are not.
- A new game uses the same initial character statistics for both controllers.
  Student controllers do not choose their team composition or alter moves.

## Scope

`arena.py` and `team_arena/` add a teaching activity; they do not modify
`student_game/`, existing RPG encounters, or the graphical battle scene.
The headless tournament runner is the playable feature here. Graphical AI-vs-AI
replay is a separate future enhancement.
