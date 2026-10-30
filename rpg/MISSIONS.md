# RPG guided missions

The game already has animations, sounds, mana, teams, and legal battle moves.
Your job is to implement **four unfinished decisions** in
[`student_game/student.py`](student_game/student.py). Each one is used by a
real playable encounter. You can complete them in any order.

Start by checking the project works:

```bash
python main.py --check
```

For each mission, run the **lab first** to read the battle facts. Then play
the scenario and watch what the character does. Turn on the `if False:` print
inside the mission you're working on if you need more information.

| Mission | Battle to play | Deliberately unfinished behavior | Main idea |
| --- | --- | --- | --- |
| 1. Confused Healer | `healer_injured` | The healer attacks while its friend is hurt | Choose from allies, conditions, mana |
| 2. Cowardly Enemy | `coward_low_hp` | The creature attacks when it should defend | Health ratios and branching |
| 3. Cursed Sword | `sword_low_hp` | The sword hurts enemies but never curses them | Returning more than one command |
| 4. Boss Phases | `boss_low_hp` | The boss only uses its basic attack | Strategy choices and phase conditions |

## Mission 1 — Confused Healer

```bash
python lab.py scenario healer_injured
python main.py --scenario healer_injured --teach
```

The **Distracted Healer** belongs to the enemy team, beside a badly injured
Shieldbearer. Both have ready-made animations, and the healer knows
*Healing Light*. You do **not** have to write healing math or animation. It
just never chooses to use the spell.

Find `healer_strategy(turn)` in `student_game/student.py`. The inputs tell
you which teammates are hurt and which moves are affordable. Build the
condition that chooses healing over attacking. Try the comparison scenario:

```bash
python lab.py scenario healer_healthy
python main.py --scenario healer_healthy --teach
```

A completed healer should cast on an injured ally, but not waste mana on
someone who already has full health.

## Mission 2 — Cowardly Enemy

```bash
python lab.py scenario coward_low_hp
python main.py --scenario coward_low_hp --teach
```

The **Timid Wisp** is nearly knocked out. It knows how to defend already,
but its Python strategy always selects Attack. Add a condition so it defends
when it's sufficiently injured and attacks otherwise.

Compare with `coward_healthy` to make sure it still attacks when safe.

## Mission 3 — Cursed Sword

```bash
python lab.py scenario sword_low_hp
python main.py --scenario sword_low_hp --teach
```

The **Cursebound Knight** can already select the *Cursed Sword* in the move
menu. It plays its animation and deals damage. But the function backing the
move returns only `damage(9)`.

Modify `cursed_sword_logic(ctx)` so it also causes an effect when an
interesting condition is true. One option is to curse enemies while the
knight is below half HP. A move can return a **list of commands**; one can
cause damage and another can apply a status.

Compare against `sword_healthy`; keep the normal hit working in both cases.

## Mission 4 — Boss Phases

```bash
python lab.py scenario boss_low_hp
python main.py --scenario boss_low_hp --teach
```

The **Phase Warden** looks like a boss, has animated magic skills, and enough
mana to use them—but it always performs its ordinary Attack. Teach it to
change strategy based on HP, round number, or another condition. The boss
already knows *Gradient Descent*, *Regularization*, and *Artifact Burst*.

Try `boss_healthy` as a comparison. An encounter should remain playable
before and after you implement a phase.

## When you're ready for less guidance

Try `python student_game/challenge.py`, or open
[`student_game/challenge.py`](student_game/challenge.py). It contains
open-ended missions and concepts to consider, **not implementation steps**.
Finding where code belongs is part of those challenges.

For each completed feature, demonstrate it, explain the code you changed,
and describe one problem you encountered while testing.
