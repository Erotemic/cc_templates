# I01 — Build a lookout using room data

**Time:** 30–45 minutes · **Start:** `intermediate/version1.py` · **Concept:** structured data and data-only choices

## New feature

A **lookout** above the forest lets the player peer through a telescope and
then return. The telescope prints a scene without requiring any new action
handler function.

## Find your starting points (5 minutes)

Locate `ROOMS`, `build_choices()`, and the `room:` branch of `handle_action()`.
Observe that a choice with `"result"` but no `"action"` gets handled as room
data. The goal is **not** to write another Python handler.

## Build it (20–30 minutes)

1. Add a room with the dictionary key **`"lookout"`** in `ROOMS`, including
   `description`, `exits`, and `choices` fields.
2. Give the forest an exit pointing to `"lookout"`, and the lookout a return
   exit to `"forest"`.
3. Add a **telescope** choice in the lookout using a dictionary with a `text`
   field and a nonempty `result` list. Do **not** add an action handler for
   the telescope.
4. Test walking from the village to the forest, from the forest to the
   lookout, using the telescope, returning, and completing the original game.

**Hint:** `build_choices()` automatically creates an action like `room:0` for
a data-only choice. `handle_action()` already knows how to find its result.
Copy the shape of an existing room to avoid missing dictionary keys.

## Done when

- [ ] `ROOMS["lookout"]` contains a playable room.
- [ ] A forest exit leads there and a lookout exit returns to the forest.
- [ ] Inspecting the telescope returns a description; no new handler exists.
- [ ] The original key-and-chest puzzle still works.

**Stretch:** Add a second room-only action, such as inspecting a weather vane.

**Explain it:** Why is a dictionary entry enough for a story-only choice, but
not for a choice that adds an item to inventory?

**Check:** `python assignments/check.py I01`.
