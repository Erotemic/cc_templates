# Lesson 2 — Write a Conditional from a Specification

**Prerequisites:** Lesson 1, functions, return values.

## Specification

Implement this behavior in `power_strike_logic`:

- above 70% HP: power 7;
- from 30% through 70% HP: power 11;
- below 30% HP: power 17.

## Worked pattern

Use the shape of `power_strike_logic`, but do not copy its condition unchanged.
Write the cases in an order that makes them easy to reason about.

## Test boundaries

For this experiment, set `workshop_hero`'s `hp=100` so the 30% and 70% boundaries
can be represented exactly with integer HP. Test 29, 30, 31, 69, 70, and 71 HP
using the move lab with a fixed seed, for example:

```bash
python lab.py move workshop_power_strike --user-hp 30 --seed 5
```

The named `threshold_25/26/27` scenarios were designed for a 52-HP hero; use the
explicit move command for this experiment. With maximum HP 52, neither 30% nor
70% falls on an integer HP value.

## Independent task

Add a second fact to the decision, such as a status on the target or the round
number.

## Explain / transfer

Explain why checking only one typical value from each region is weaker than
also checking boundary values.
