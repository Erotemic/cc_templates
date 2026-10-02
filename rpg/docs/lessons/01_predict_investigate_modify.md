# Lesson 1 — Read, Predict, Investigate, Modify

**Prerequisites:** variables, numbers, comparisons, `if`.

Open `student_game/workshop.py` and find `power_strike_logic`.

## Predict

Without running the code, predict which damage power is returned when Workshop
Hero has 25, 26, and 27 HP out of 52.

## Investigate

Run:

```bash
python lab.py scenario threshold_25
python lab.py scenario threshold_26
python lab.py scenario threshold_27
```

For each run, identify:

1. the HP ratio;
2. the boolean condition;
3. the command returned by the function;
4. the effective attack and defense used by the engine;
5. the resulting HP change.

## Modify

Change the comparison expression from `< 0.50` to `<= 0.50`. Update the text
label passed to `ctx.observe` as well; that label describes the condition but
does not execute it. Predict which one of the three cases changes, then rerun
them.

## Independent task

Make Power Strike have three health bands of your own design.

## Explain / transfer

Write a short explanation of why 26/52 behaves differently for `< 0.5` and
`<= 0.5`. Then write a non-game example where a boundary condition matters.
