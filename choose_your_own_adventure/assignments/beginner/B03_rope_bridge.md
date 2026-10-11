# B03 — Cross a bridge only with a rope

**Time:** 45–60 minutes · **Start:** `beginner/version1.py` · **Concept:** list membership and conditional rules

## New feature

The forest leads to a **ridge across a broken rope bridge**. The player can
collect a `"rope"` in the village. Without the rope, the bridge refuses to let
them cross; with it, they can visit the ridge and return. The cave's original
path remains open.

## Find your starting points (5 minutes)

Look for `inventory.append("brass key")` and `"brass key" in inventory`.
Those two statements provide almost all the new programming ideas you need.

## Build it (30–40 minutes)

1. Add a new `"ridge"` description to `rooms`.
2. Add a village choice to **Take the rope**. When handled, append `"rope"`
   to `inventory`. Make sure choosing it twice doesn't create two ropes.
3. Add a forest choice to **Cross the broken bridge**. Keep this option
   visible even when the player has no rope; it gives useful feedback.
4. When the bridge action is selected, test whether `"rope" in inventory`.
   Without it, explain that the bridge is unsafe and **leave the player in the
   forest**. With it, set the location to `"ridge"`.
5. In the ridge, provide a way to return to the forest. Check the original
   forest–cave–chest route afterward.

**Hint:** You can use `if "rope" in inventory:` just like the chest checks for
the brass key. Prefer a condition over adding another almost-identical list of
menu choices for players with and without the rope.

## Done when (10-minute playtest)

- [ ] Crossing without a rope fails, but the game continues normally.
- [ ] The rope can be collected once and is visible in the inventory.
- [ ] Crossing with a rope reaches the ridge; returning works.
- [ ] The cave treasure still requires the brass key.

**Stretch:** Make the ridge contain a message or collectible that the player
can only discover after crossing.

**Explain it:** Why must the rope check happen when the action is performed,
not only when the status is printed?
