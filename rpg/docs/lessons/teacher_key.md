# Teacher Notes for the Common Sequence

## Lesson 1

Expected Power Strike command powers before modification:

- 25/52: 18 (`25 / 52 < 0.5` is true)
- 26/52: 8 (`26 / 52 == 0.5`, so `< 0.5` is false)
- 27/52: 8

Changing `<` to `<=` changes the exactly-half case. A common misconception is
thinking “half health” automatically belongs to the low-health branch without
reading the comparison operator. `ctx.observe("low_health", ...)` names the fact
shown by the lab; the expression itself determines the value.

## Lesson 2

Look for logically complete, non-overlapping regions. Students often create a
gap or write the broadest condition first, making later branches unreachable.
Ask them to test each boundary from both sides.

The lesson keeps the hero at 52 maximum HP and deliberately uses 25% and 75%
because those are exact integer boundaries: 13/52 and 39/52. Expected powers
for 12/13/14/38/39/40 HP are 17/11/11/11/11/7.

## Lesson 3

The supplied chain-lightning scenario deliberately has two targets and exactly
one burned target. Expected scripted command powers are 8 for Mist Spirit and
14 for Crystal Guardian. A common bug is returning inside the loop, which
processes only the first target.

## Lesson 4

The invalid target `"usr"` must be rejected by `--check`; it must never fall
through to the selected opponent. Distinguish errors Python can detect from
logic errors that require a specification and deliberate tests.

## Lesson 5

In the supplied setup, Storm Ranger has lower raw HP (19 < 20), while Workshop
Hero has lower HP ratio (20/52 < 19/46). The shipped strategy uses an explicit
loop to find the smallest HP ratio and therefore chooses Workshop Hero. After
students understand that algorithm, `min(..., key=...)` can be introduced as a
concise Python refactor.

## Lesson 6

Assess explanation as well as game polish. A student should be able to point to
inputs, control flow, returned command(s), and the engine result. Originality
can come from behavior, art, sound, balance, or composition; do not require the
same kind of project from everyone.

## Differentiation

Differentiate by demonstrated knowledge rather than grade number:

- supported: modify concrete values and existing conditions;
- core: write functions and loops from behavioral specifications;
- extension: compare algorithms, write tests, use simulations, or inspect
  engine rules;
- open: add a new mechanic or engine capability with tests.
