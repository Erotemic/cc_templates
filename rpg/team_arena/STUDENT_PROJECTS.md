# Team-controller projects (30–60 minutes each)

Each project must add **a decision your controller did not make before**.
Students start with `team_arena/players/my_team.py`, not engine internals.
Work through the projects in order. Try one change at a time, run `python
arena.py`, and press **R** after every save. Explain what changed *in the
fight*, not just which Python lines changed.

## Project 0 — My code is fighting (20–30 min)

**Add:** Your own visible decision and `print(...)` explanation.

1. Run `python arena.py`; look for `my_team` and its Python filename.
2. Edit `my_team.py`: change a move, the target, or when you defend.
3. Print the fighter's HP and your reason for the choice.
4. Save, press **R**, and find **your output and new move** in the animation.

**Complete when:** A teammate can point to the moment your code's change takes
effect and can find your printed explanation. **Concept:** functions, returns,
printing. **Stretch:** Change your behavior on a particular round.

## Project 1 — Two characters, different skills (30–45 min)

**Add:** A decision that depends on **which skills the current fighter knows**.
Both the Guardian and Mage can `turn.attack(...)` as often as they like, but
neither knows every special skill. Make each fighter choose a learned skill
when appropriate, instead of only using Attack.

```bash
python arena.py moves
python arena.py battle my_team first_target --runs 20
```

**Complete when:** Both fighters visibly use different legal skills and your
score against `first_target` reaches **80%** over 40 games (20 seeds, two
sides). **Concept:** `if`, `in`, sets. **Clue:** Power is not the only factor;
physical and magical characters have different stats.

## Project 2 — Read the room (30–45 min)

**Add:** A target-selection rule that **reacts to changing enemy facts**.
Targeting the first enemy forever does not satisfy the project.

```bash
python arena.py watch my_team heavy_hitter --seed 6
python arena.py battle my_team heavy_hitter --runs 20
```

**Complete when:** You can show two situations (different rounds, seeds, or
matchups) where your rule chooses a different target because of what it sees.
Print the target and the values that informed your decision. Aim for **80%**
against `heavy_hitter`. **Concept:** loops, comparisons, choosing an item from
a collection. **Clue:** Knocking out one opponent removes future enemy turns.

## Project 3 — One target or a group? (45–60 min)

**Add:** A conditional decision between a move targeting **one enemy** and a
move targeting **all living enemies**. The rule must actually use **both**
kinds of move in different situations; an always-attack bot is not enough.

```bash
python arena.py moves
python arena.py watch my_team crowd_control --seed 8
python arena.py battle my_team crowd_control --runs 20
```

**Complete when:** You can demonstrate a group attack and a focused attack,
explain what condition selected each, and measure whether the change helped
against `crowd_control`. No fixed win-rate requirement: sometimes a group
attack is **worse**, and discovering that is a valid result. **Concept:**
conditionals, tradeoffs, testing a hypothesis.

## Project 4 — Beat the prefab lineup (45–60 min)

**Add:** One controller that makes strong, legal decisions against **all seven
prefab opponents**; this may require revisiting or even discarding earlier
tactics that didn't work.

```bash
python arena.py challenge my_team --runs 20 --seed 0
```

**Complete when:** Your score is **at least 80% against EACH prefab** and no
battle is unfinished. A reference strategy has passed this exact challenge
using only the documented `turn` API; it is intentionally not provided.

**Clues, not instructions:** What costs you the most turns? When does an
enemy stop being a threat? Does healing help more than finishing an attack?
Do the same moves suit both characters? Try `--seed 77` after developing with
seed 0 to see whether the improvement generalizes.

**Concept:** combined heuristics, experiments, and debugging. **Explain:**
Which opponent forced you to revise your strategy?

## Project 5 — Team-controller tournament (30–60 min)

**Add:** A new saved version of your controller and a repeatable comparison
against classmates, not just one lucky visual victory.

```bash
python arena.py new contender_v2 --from my_team
python arena.py tournament --runs 2 --seed 71 --csv class_results.csv
```

A teacher can select entrants explicitly and increase `--runs` for finals.
Before competing, write a prediction. Afterwards, compare the standings and
explain one result. Then improve **one** decision and compare versions using
the same seeds. **Concept:** experiment design, reproducibility, fair scoring.

**Hand-in:** Your editable `.py` file, one new behavior you implemented, one
interesting observation from a visual battle, and the seeds used to measure
results. Do **not** modify `prefabs/` or engine code for these projects.
