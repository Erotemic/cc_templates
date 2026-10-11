# I03 — Give the game a field-notes journal

**Time:** 45–60 minutes · **Start:** `intermediate/version2.py` · **Concept:** object-owned state and sets

## New feature

A new **Field notes** action, available in **every room**, reports the rooms
visited so far. The game itself records visits and returns the journal text;
the console layer only displays it.

## Find your starting points (5 minutes)

Trace `Game.__init__()`, `Game.choices()`, `Game.apply()`, and `run_console()`.
The `Game` object must own state because future frontends should get the same
answers without guessing what happened.

## Build it (30–40 minutes)

1. Add a `visited` **set** to `Game`, initially containing `"village"`.
2. When `Game.apply()` performs a `go:` movement, update `visited` with the
   newly entered location. Visiting the same room twice must not change the
   number of entries.
3. Make `Game.choices()` include an action whose ID is exactly **`"journal"`**
   in every room, with a friendly menu label such as **Read field notes**.
4. When `Game.apply("journal")` runs, **return a list of strings** containing
   all visited locations. Don't print, move, or change state there. Sorting
   the set produces stable output order.
5. Walk through forest and cave, then read the notes again; each visited
   location should be listed once.

**Hint:** `self.visited.add(self.player.location)` works because sets do not
store duplicates. `Game.apply()` already validates actions with `choices()`;
remember to make `journal` legal before adding its handler.

## Done when

- [ ] Initially field notes mention only the village.
- [ ] Traveling to forest and cave records both rooms without duplicates.
- [ ] `journal` returns lines without printing or changing location.
- [ ] The original chest can still be opened.

**Stretch:** Include the count of visited rooms in the journal.

**Explain it:** Why does `visited` belong to `Game` rather than
`run_console()`? What tradeoff do you make by using a set instead of a list?

**Check:** `python assignments/check.py I03`.
