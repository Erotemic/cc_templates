# B01 — Build an orchard to explore

**Time:** 35–45 minutes · **Start:** `beginner/version1.py` · **Concept:** dictionaries and `if`/`elif`

## New feature

The player can walk **east from the village into an orchard**, look at an old
tree, and walk back. The original key-and-treasure adventure must still work.

## Find your starting points (5 minutes)

Run `python assignments/work/B01.py`. Find the `rooms` dictionary, the
`if player_location == ...` menu branches, and the `if action == ...` action
tree. They each do a different job: *describe*, *offer*, and *carry out* an
action.

## Build it (25 minutes)

1. Add an `"orchard"` description to the `rooms` dictionary. A dictionary key
   must match the location stored in `player_location`.
2. Add a new menu option in the **village** for walking east. Give it a distinct
   action label, just like `go_forest`.
3. Add the **orchard** branch to the menu. It should offer **Look at the old
   tree** and **Return west to the village**.
4. Add branches to the action tree: one moves into the orchard, another moves
   back to the village, and looking at the tree prints a clue or short scene.
5. Play once, read the new scene, return to the village, and then get the
   original treasure.

**Hint:** A menu option *only describes* an action. Nothing happens until your
`if action == ...` branch handles its action label. If a room's name is
misspelled in one place, the program may try to look up a missing dictionary
key.

## Done when (10-minute playtest)

- [ ] The orchard is reachable from the village, and its description appears.
- [ ] Looking at the tree produces a message without changing rooms.
- [ ] Returning to the village works; the original treasure can still be won.
- [ ] Typing `quit` exits normally.

**Stretch:** Put a second, different thing to inspect in the orchard. Why does
it need a separate action label?

**Explain it:** What happens if you add an orchard description but forget its
menu branch? What happens if you add a menu option but not an action handler?
