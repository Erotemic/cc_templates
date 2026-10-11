# I05 — Find and drink a healing potion

**Time:** 45–60 minutes · **Start:** `intermediate/version3.py` · **Concept:** inventory conditions and clamping numbers

## New feature

A **`"healing potion"`** can be collected once in the forest. Outside
combat, an injured player may choose **Drink healing potion** to recover
**6 HP**. One potion is consumed. HP must never exceed `max_hp`.

## Find your starting points (5 minutes)

Read `Player`, the `forest` part of `Game.choices()`, `Game.apply_world_action()`,
and the `rest` action. Notice that `Game.apply()` validates legal choices and
that the player already has `hp`, `max_hp`, and `inventory`.

## Build it (30–40 minutes)

1. Add a flag to remember whether the forest potion has been collected, or
   use the player's `flags` set.
2. Offer a forest action with ID **`"take_potion"`** until the player has
   taken the potion. It adds one `"healing potion"` to inventory.
3. Offer an action with ID **`"drink_potion"`** in every **noncombat room**
   when the player has a potion **and** `hp < max_hp`.
4. Handle both actions through the normal `Game.apply()` /
   `apply_world_action()` route. Drinking removes one potion and increases HP
   by 6, but caps it at `max_hp` with `min(...)`.
5. Get hurt by the ruin spider, retreat, collect the potion, and drink it.
   Confirm that no second potion is available at the forest.

**Hint:** A condition in `choices()` controls whether an action can be used.
A branch in `apply_world_action()` performs the actual mutation. You need
both, but not a new game class.

## Done when

- [ ] Collecting the forest potion is possible exactly once.
- [ ] Drink is unavailable when healthy, when there is no potion, or in combat.
- [ ] Drinking while hurt consumes a potion and heals up to 6 HP, not beyond max.
- [ ] The original Star Crystal winning route remains possible.

**Stretch:** Make the healing amount a named constant instead of repeating `6`.

**Explain it:** What bug would `self.player.hp += 6` introduce if the player
had only lost one HP? Why must the action be illegal during combat?

**Check:** `python assignments/check.py I05`.
