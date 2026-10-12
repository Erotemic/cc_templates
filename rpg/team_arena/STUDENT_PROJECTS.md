# Build your own team controller — student projects

Every project **adds a behavior your previous controller did not have**. Your
code runs in the real RPG battle engine, not a pretend example. Work in your
own `team_arena/players/*.py` file; do not edit the prefabs or the battle
engine. The projects build on each other: each new file copies your previous
project so you can compare versions. Each project is designed for roughly **30–60 minutes** after students
know how to use a function and a conditional.

## Project 0 — My First AI (20–30 min)

**New feature:** A fighter whose actions come from your own Python function.

Starting point: `team_arena/players/my_team.py`.

1. Run `python arena.py battle my_team first_target --runs 4 --log`.
2. Find `choose_action`. Change which action the fighter chooses.
3. Re-run the battle; confirm that the log shows your new action.
4. Run `python arena.py list` and confirm your file appears as a student entry.

**Programming idea:** functions and returning values. **Finished when:** the
battle log contains your modified choice, with no invalid-action errors.

**Extension:** Make the controller behave differently on a specific round.

## Project 1 — More Than One Move (30–45 min)

**New feature:** Characters use actions suited to their own move lists, rather
than both using the same weak move.

```bash
python arena.py new move_picker --from first_target
python arena.py moves
python arena.py battle move_picker first_target --runs 20 --seed 0
```

**Goal:** Score at least **80%** against `first_target` across 40 matches
(20 seeds, two seats each). Test both characters, not just one.

**Design clues:** The characters know different moves. A move's `power` alone
is not its final damage; character stats also matter. `turn.available_move_ids`
lets your function check what's legal. The `arena.py moves` display is your
reference. Your finished AI should not crash when either character acts.

**Programming idea:** membership tests and conditionals. **Explain:** Why is
one hard-coded move name not sufficient for every character?

## Project 2 — Choosing a Threat (30–45 min)

**New feature:** Your target depends on information about the enemy, not just
where the enemy appears in the list.

```bash
python arena.py new threat_hunter --from move_picker
python arena.py battle threat_hunter heavy_hitter --runs 20 --seed 0
```

**Goal:** Score at least **80%** against `heavy_hitter`. Unlike the prefab
`heavy_hitter` (which you can read), your controller must sometimes choose a
**different enemy** when
the situation changes. Explain what makes an enemy a good target.

**Design clues:** You can compare enemy health, speed, defense, or potential
damage. Think about whether two injured opponents are more dangerous than
one defeated opponent. Which enemy can you remove from the fight sooner?

**Programming idea:** iteration, comparisons, and selecting the best element
of a collection. **Explain:** What makes your selection adapt to changes
in enemy health?

## Project 3 — Tactics Against Groups (45–60 min)

**New feature:** Your controller handles the choice between damaging a whole
group and concentrating damage on one opponent.

```bash
python arena.py new squad_tactics --from threat_hunter
python arena.py moves
python arena.py battle squad_tactics crowd_control --runs 20 --seed 0
```

**Goal:** Score at least **80%** against `crowd_control`. Observe how many
enemies are alive and watch which attacks land before a fighter is knocked out.
Show your teacher two battle situations in which your controller makes a
*different tactical choice* based on what it observes.

**Design clues:** Group moves spread their effect. Single-target moves
concentrate it. A KO takes away an opponent's future turns. Which approach
looks good on the first round? Does it stay good later? You may keep a group
move in your controller, but you do not have to.

**Programming idea:** algorithms, nested conditions, and tradeoffs.
**Explain:** When can a move with lower total damage still improve your
chance of winning?

## Project 4 — Defeat Every Prefab (45–60 min)

**New feature:** A single robust team controller that works against *all*
of the built-in styles, including the RPG engine's own heuristic AI.

```bash
python arena.py new contender --from squad_tactics
python arena.py challenge contender --runs 20 --seed 0
```

**Goal:** Your score must reach **80% or better against EACH prefab**. A
single overall average is not enough. The command prints separate results and
says `CHALLENGE PASSED` only after all requirements are met.

This challenge **has a tested solution** using only the currently documented
`TurnContext` information and normal Python control flow. You are not given
that solution. Develop a hypothesis, inspect logs, and iterate.

You may discover that techniques from Projects 1–3 work better in combination.
You should not need external packages, a large model, access to internal game
state, or new combat rules.

**Programming idea:** combining conditionals, loops, and heuristics into a
single decision algorithm. **Explain:** Which prefab was hardest to beat?
Did one improvement help against one opponent but hurt against another?

**Extension:** Run another test with `--seed 77` to investigate whether your
improvement holds on a different set of random battles.

## Project 5 — A Classroom Tournament (30–60 min)

**New feature:** Your controller competes in a class leaderboard, with a
repeatable, recorded evaluation rather than an anecdotal victory.

```bash
python arena.py tournament move_picker threat_hunter squad_tactics contender --runs 20 --seed 71 --csv arena_results.csv
```

Use only controller names that actually exist in your class. Your teacher may
choose a common seed and run count for everyone. Before the tournament, write
one sentence predicting which other AI yours will defeat. Afterward, compare
your prediction to the CSV standings and explain one surprise.

**Programming idea:** experiments, reproducibility, fair comparisons, and
reading tabular results. **Extension:** Improve your controller, but save its
old version first. Then compare both versions under the same seeds.

## Checklist before turning in

- My file is under `team_arena/players/` and exports `choose_action(turn)`.
- Every action is returned with `turn.use(...)` or `turn.defend()`.
- Both characters can play without throwing an exception.
- I can state **what behavior I added**, not just what lines I changed.
- I recorded the seed and number of matches, not just a single win.
- I can explain my strategy in plain English without needing to read code.
