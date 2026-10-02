# Lesson 2 — Write a Conditional from a Specification

**Prerequisites:** Lesson 1, functions, return values.

## Specification

Create a move with this behavior:

- above 70% HP: power 7;
- from 30% through 70% HP: power 11;
- below 30% HP: power 17.

## Worked pattern

Use the shape of `power_strike_logic`, but do not copy its condition unchanged.
Write the cases in an order that makes them easy to reason about.

## Test boundaries

Choose values just below, exactly on, and just above each boundary. Use the move
lab to check them with a fixed seed.

## Independent task

Add a second fact to the decision, such as a status on the target or the round
number.

## Explain / transfer

Explain why checking only one typical value from each region is weaker than
also checking boundary values.
