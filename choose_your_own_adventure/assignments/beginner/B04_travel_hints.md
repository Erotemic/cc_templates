# B04 — Ask for a hint wherever you are

**Time:** 30–45 minutes · **Start:** `beginner/version2.py` · **Concept:** function parameters and return values

## New feature

Every room offers **Ask for a hint**. The answer changes with the room and
what the player has already found. In the forest, a player who has the key
should receive a different hint from one who has not found it.

## Find your starting points (5 minutes)

Read `show_status(...)`, `choose(...)`, and `main()`. Observe how `main()`
passes information into functions and receives an action back from `choose()`.

## Build it (20–25 minutes)

1. Write a function such as `hint_for(location, inventory)` **above** `main()`.
   It receives information about the player, chooses a hint using `if`/`elif`,
   and **returns a string**. It should not call `input()`.
2. Make it return a useful hint for the village, forest, and cave. In the
   forest, check whether `"brass key" in inventory` to give two different
   hints.
3. After building the location's ordinary choices, add the same **Ask for a
   hint** menu option to every room.
4. Add one handler to the existing action tree that calls `hint_for(...)`
   with the current state and prints the returned message.
5. Ask for hints before finding the key and after finding it. No inventory
   item or flag should be consumed by asking.

**Hint:** A function can contain `return "Look behind the stump"`; the caller
can then `print(hint_for(...))`. The function's arguments should describe the
current state, not be global variables it secretly edits.

## Done when (10-minute playtest)

- [ ] Hints are available in all three original rooms.
- [ ] The forest hint changes after collecting the key.
- [ ] Asking for a hint doesn't move the player, win the game, or modify items.
- [ ] The original puzzle remains playable.

**Stretch:** Add a hint for the cave that differs depending on whether the
player holds the brass key.

**Explain it:** What is the difference between `return hint` and `print(hint)`?
Why is `inventory` a useful parameter to this function?
