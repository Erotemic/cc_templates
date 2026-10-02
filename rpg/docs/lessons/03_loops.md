# Lesson 3 — Trace a Loop and Build a Result List

**Prerequisites:** lists, `for`, `append`, conditionals.

Open `chain_lightning_logic`.

## Predict

In the named scenario, Mist Spirit is not burned and Crystal Guardian is.
Predict the command power produced for each target.

## Investigate

```bash
python lab.py scenario chain_lightning
```

Follow the output target by target. Match each loop iteration to one command and
one HP change.

## Modify

Change the burned-target bonus. Rerun the same scenario without changing its
seed or initial statuses.

## Independent task

Write a multi-target move that makes at least three different decisions based
on target facts.

## Explain / transfer

Describe why the function builds a list of commands instead of returning from
the first loop iteration.
