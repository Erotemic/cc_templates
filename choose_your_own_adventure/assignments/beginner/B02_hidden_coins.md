# B02 — Find hidden coins only once

**Time:** 35–50 minutes · **Start:** `beginner/version1.py` · **Concept:** numeric variables and Boolean state

## New feature

A fallen log in the **forest** hides **three coins**. Searching it the first
time raises the player's gold total; repeating the search must not print more
money. The player can see their gold on every turn.

## Find your starting points (5 minutes)

Play the game and collect the brass key twice—or try to. Notice what
`key_taken` does. Find `player_name`, `inventory`, and `key_taken` near the top
and the status printing inside the loop.

## Build it (25–30 minutes)

1. Add a numeric `gold` variable starting at `0` and a Boolean such as
   `log_searched` starting at `False` **before** the main `while` loop.
2. Print the player's gold near their inventory on every turn.
3. In the forest, offer a **Search the fallen log** action. You may hide it
   after the first search, or keep it visible and report that it is empty.
4. Handle the new action: on the **first** search, increase `gold` by `3`
   and remember that the log was searched. Later searches must never add gold.
5. Leave the forest, return, and make sure the gold total stays the same.

**Hint:** A state variable belongs outside the loop if its value must survive
between turns. `gold = gold + 3` changes a number; `log_searched = True`
remembers an event. You need both ideas here.

## Done when (10-minute playtest)

- [ ] The player starts with zero gold.
- [ ] One search of the log adds exactly three gold.
- [ ] Returning to the forest cannot award three more gold.
- [ ] The original brass key and treasure puzzle still work.

**Stretch:** Show a different message if the player has already searched the
log, without removing the choice from the menu.

**Explain it:** What goes wrong if `gold = 0` appears inside the `while` loop?
Why isn't a number alone enough to remember whether this *particular* reward
was already collected?
