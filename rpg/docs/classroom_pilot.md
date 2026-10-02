# Classroom Pilot Checklist

This project is intended for grades 9–12, but the repository cannot establish
learning outcomes by itself. Use a small classroom pilot before treating a
lesson sequence as settled.

## What to measure

Record aggregate classroom observations rather than grading students by speed.
Useful signals include:

- **setup time** — how long until a student can run `python main.py --check`;
- **time to first meaningful edit** — how long until an intentional code change
  produces the predicted game/lab change;
- **prediction and explanation** — whether students can state what a short piece
  of code will do and explain the observed result afterward;
- **debugging independence** — whether students can use the error message, lab,
  cheatsheet, or breakpoint before asking an instructor to diagnose the issue;
- **transfer** — whether students can reproduce the same idea in a new move or a
  small non-RPG problem rather than only editing the worked example.

Engagement and game polish are useful observations, but they do not substitute
for evidence that students understand the programming idea.

## Suggested pilot checkpoints

### Checkpoint 1: boundary condition

Use `threshold_25`, `threshold_26`, and `threshold_27` from Lesson 1. Ask students
to predict all three before running the lab. Record the misconceptions that
appear around `<` versus `<=` and exactly-half health.

### Checkpoint 2: loop trace

Use `chain_lightning`. Ask students to explain why the two enemies receive
commands with different powers. Then change which target begins burned without
changing the loop body.

### Checkpoint 3: debugging

Use the deliberate mistakes in Lesson 4. Note whether the student can distinguish
syntax, runtime, and logic errors and which feedback surface actually helps.

### Checkpoint 4: independent creation

Give the constraints from Lesson 6 without a prescribed implementation. Ask the
student to demonstrate one custom behavior and explain its inputs, branch/loop
logic, returned commands, and observed engine result.

### Checkpoint 5: transfer

Give a short problem outside the RPG that uses the same concept. For example,
after the health-threshold lesson, ask for a function that classifies a numeric
score into three bands with explicit boundary cases.

## After the pilot

Revise the lessons based on recurring evidence, not one-off preferences. In
particular, look for:

- instructions students repeatedly misread;
- APIs that produce errors they cannot connect to their edit;
- scenarios that fail to exercise the intended branch or loop;
- steps that require unexplained software-engineering knowledge;
- concepts students can modify by imitation but cannot explain or transfer.

Keep successful open-ended extensions even when different students solve them in
different ways. The objective is independent programming, not convergence on one
teacher-authored solution.
