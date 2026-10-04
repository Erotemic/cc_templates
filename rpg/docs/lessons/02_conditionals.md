# Lesson 2 — Write a Conditional from a Specification

**Prerequisites:** Lesson 1, functions, return values.

## Specification

Implement this behavior in `power_strike_logic`:

- above 75% HP: power 7;
- from 25% through 75% HP: power 11;
- below 25% HP: power 17.

These boundaries fit Workshop Hero's existing 52 HP exactly:

- 13/52 = 25%;
- 39/52 = 75%.

You do **not** need to change the character's maximum HP for this lesson.

## Worked pattern

Use the shape of `power_strike_logic`, but do not copy its condition unchanged.
Write the cases in an order that makes them easy to reason about.

## Test boundaries

Test one value on each side of both boundaries:

```bash
python lab.py move workshop_power_strike --user-hp 12 --seed 5
python lab.py move workshop_power_strike --user-hp 13 --seed 5
python lab.py move workshop_power_strike --user-hp 14 --seed 5

python lab.py move workshop_power_strike --user-hp 38 --seed 5
python lab.py move workshop_power_strike --user-hp 39 --seed 5
python lab.py move workshop_power_strike --user-hp 40 --seed 5
```

## Independent task

Add a second fact to the decision, such as a status on the target or the round
number.

## Explain / transfer

Explain why checking only one typical value from each region is weaker than
also checking boundary values.
