# B05 — Keep a travel journal

**Time:** 45–60 minutes · **Start:** `beginner/version2.py` · **Concept:** lists, loops, and helper functions

## New feature

The player can select **Read travel journal** in any room to see every room
visited so far, **in the order it was first visited**. Returning to a room
must not add a duplicate entry.

## Find your starting points (5 minutes)

Find the `rooms` dictionary, the changing `player_location`, and the action
handlers in `main()`. Notice that a variable declared *inside* `main()` can
remain alive for the entire game loop.

## Build it (30–40 minutes)

1. Add a `visited` list in `main()` that initially contains `"village"`.
2. Whenever an action **actually moves** the player to another room, add
   the new location to the list *only if it is not already present*.
3. Write a helper function such as `journal_text(visited, rooms)` that
   builds and **returns a string** describing the visited rooms. Use a loop
   to build the text (or a list of lines) from `visited`.
4. Add **Read travel journal** to every room's menu and handle it by printing
   the value returned by the helper. The journal must not move the player.
5. Follow `village → forest → cave → forest → village` and read the journal.
   It should have **three entries** in first-visit order.

**Hint:** `if player_location not in visited:` stops duplicate entries. Do
this just after changing the player's location. Be careful not to reset the
list inside the `while` loop.

## Done when (10-minute playtest)

- [ ] Initially the journal contains only the village.
- [ ] Forest and cave are recorded after visiting them.
- [ ] Revisiting a room doesn't add duplicate entries or reorder old ones.
- [ ] Looking at the journal doesn't move the player; the treasure still works.

**Stretch:** Add a count of the unique rooms visited to the journal output.

**Explain it:** Why does the list need to be updated *after movement* rather
than only when a player asks to read it? Why use a list here instead of a
single string?
