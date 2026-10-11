# I04 — Unlock a hidden watchtower route

**Time:** 45–60 minutes · **Start:** `intermediate/version2.py` · **Concept:** state-dependent legal actions

## New feature

A **watchtower** is reachable from the forest **only after speaking with the
villager**. Before hearing about it, the game doesn't offer the route and
rejects an attempt to use it directly. Once discovered, the route stays known.

## Find your starting points (5 minutes)

Look at `Room`, `ROOMS`, and `Game.choices()`. Notice that `Game.apply()`
checks whether an action appears in the legal-choice list. A hidden exit
therefore needs a *game rule*, not a change to the console menu.

## Build it (30–40 minutes)

1. Add a new `Room` with key exactly **`"watchtower"`**, an exit back to the
   forest, and at least one `RoomChoice` that describes what the player sees.
2. Add an exit from the forest to the watchtower. It should use the normal
   action ID **`"go:watchtower"`** that exits generate automatically.
3. Add a Boolean to `Game.__init__()` that remembers whether the player has
   learned the secret route. It starts `False`.
4. When `talk_villager` happens inside `Game.apply()`, set that Boolean to
   `True` and mention the route. Keep the existing clue about the brass key.
5. In `Game.choices()`, **filter out** the watchtower exit until that Boolean
   is `True`. Do not put that condition in `run_console()`.
6. Verify that knowing the route survives moving between rooms.

**Hint:** `Game.choices()` already loops over `room.exits`. A short condition
that skips the watchtower destination before appending its `Choice` is enough.

## Done when

- [ ] The watchtower route is initially absent from the forest choices.
- [ ] Trying `Game.apply("go:watchtower")` early raises `ValueError`.
- [ ] Talking to the villager makes the route available from the forest.
- [ ] The watchtower interaction and return route work; treasure still works.

**Stretch:** Make the watchtower's story text different after finding the key.

**Explain it:** Why do game rules belong in `Game.choices()` rather than
`choose()` or `run_console()`?

**Check:** `python assignments/check.py I04`.
