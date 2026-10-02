# Early Python curriculum

This folder contains small programs that can be used before, beside, or between
larger demos in this repository.

The sequence is intentionally **not a fixed syllabus**. A class may spend much
more time on one idea, skip ahead to a motivating demo, or return to an earlier
lesson after seeing a larger program. The goal is to give students a few small
programs where the code they are expected to understand is easy to see.

`main_keywords.py` remains the broad survey example. It is useful as a map of
Python: students can see many language features together without being expected
to understand all of them yet. These lessons complement that file; they do not
replace it.

## Suggested classroom rhythm

For each small program:

1. **Predict** what a line or change will do.
2. **Run** the program and observe what actually happens.
3. **Change** one part of the program.
4. **Explain** why the behavior changed.
5. **Build** one small addition without copying a finished answer.

The prediction step matters. It turns editing into reasoning about the program
instead of guessing until something works.

## Suggested starting sequence

| File | Main idea | A useful first task |
| --- | --- | --- |
| `01_first_program.py` | execution, input, variables, `if` | add a third door |
| `02_values_and_expressions.py` | values, assignment, arithmetic, comparisons | change the coin rule |
| `03_more_choices.py` | `if` / `elif` / `else` | add another weather choice |
| `04_for_loops.py` | repetition with `for` and `range` | change the countdown or repeat a message |
| `05_lists.py` | keeping several values together | add/remove backpack items |
| `06_functions.py` | naming reusable actions and returning values | write a new function |
| `07_small_adventure.py` | combining the earlier ideas | add a new location or item |

`main_keywords.py` can be shown at almost any point in this sequence. Early on,
it can be treated as a preview: "you know a few of these pieces already; the
rest are things we will learn." Later, students can return to it and identify
more of what they see.

## 01: First program

The first lesson is deliberately a complete interactive program rather than an
isolated syntax example. Students should be able to run it immediately and then
change something visible.

Questions to ask before editing:

- Which line runs first?
- Where does the program stop and wait for the user?
- What value does `door` hold after the user types `red`?
- What do you predict will happen if the user types `green`?

Possible changes:

- Rewrite the story without changing the program structure.
- Swap the outcomes for the red and blue doors.
- Add a third door using `elif` after seeing lesson 03.

## 02: Values and expressions

This lesson slows down and names some of the pieces that appeared in the first
program: strings, numbers, variables, assignment, arithmetic expressions, and
comparison expressions.

Good questions:

- What is the difference between `coins = 3` and `coins == 3`?
- What value does `coins + coins_found` produce?
- What value does `coins >= goal` produce?
- What changes if `coins_found` is negative?

## 03: More choices

This makes branching the focus rather than merely using it as part of a story.
Students should trace exactly one path through an `if` / `elif` / `else` chain.

A useful exercise is to add a new case and decide where it belongs. Then ask
what happens for an input that has no special case.

## 04: For loops

Start with a fixed number of repetitions. The important mental model is that the
indented block runs again with a new value for the loop variable.

Have students write down the expected output before running the program. Then
change the `range(...)` arguments and explain the new sequence.

## 05: Lists

Lists connect naturally to loops: a program can keep several related values and
perform the same action for each one.

Do not require students to memorize every list operation. The early goal is to
understand that a variable can refer to a collection and that a loop can visit
its elements.

## 06: Functions

The main idea is "give a useful piece of work a name." Parameters let the same
code work with different values, and `return` lets a function produce a value
that other code can use.

A good depth exercise is to trace one function call on paper: identify the
argument, parameter value, expression result, returned value, and the line that
receives it.

## 07: Small adventure

This is the first integration exercise. It intentionally stays small enough to
read from top to bottom. Students have already seen each main mechanism in a
smaller setting.

Possible extensions:

- Add another path and another item.
- Add a function that describes a location.
- Require two items instead of one to open the final door.
- Add a score and update it when the player finds something.
- After loops have had more practice, turn the story into a game that continues
  until the player chooses to stop.

## Going deeper instead of going wider

The files above are entry points, not completion criteria. Before adding another
Python feature, it can be more useful to spend time asking students to:

- predict output without running the code;
- trace variable values line by line;
- find and explain a bug;
- make two different implementations of the same behavior;
- explain code to another student;
- start from a blank file and recreate a small program from requirements.

Larger demos in this repository can then provide motivation and show where these
small ideas lead without requiring every line of the larger program to be
understood at once.
