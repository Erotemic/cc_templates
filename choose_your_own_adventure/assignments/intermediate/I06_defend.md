# I06 — Add a defend action to combat

**Time:** 40–55 minutes · **Start:** `intermediate/version3.py` · **Concept:** branching on combat state and numerical bounds

## New feature

During combat, the player can **Defend** instead of attacking. On that turn,
the spider hits for **1 HP instead of 2 HP**, the spider takes no damage, and
combat continues. This defensive bonus applies to **only that one turn**.
Outside combat, Defend must not appear as an option.

## Find your starting points (5 minutes)

Follow the combat branch in `Game.choices()`, the `combat:attack` dispatch in
`Game.apply()`, and `Game.attack_enemy()` with `ENEMIES`.

## Build it (25–35 minutes)

1. While combat is active, add `Choice("combat:defend", "Defend")` next to
   Attack and Run. It must not be offered in normal rooms.
2. Handle **`"combat:defend"`** inside `Game.apply()` by calling a small
   method, or by implementing a short branch there.
3. Defending does **not** damage `combat_hp`. Instead, the enemy attacks for
   `max(0, enemy.attack - 1)` damage. Reduce player HP by that amount, but
   never below zero.
4. Return text describing the attack. If the player reaches zero HP, apply
   the same loss behavior as a normal attack.
5. Defend once, then Attack. Notice that Attack still uses its usual
   retaliation damage: defending did not permanently weaken the enemy.

**Hint:** `enemy = ENEMIES[self.combat_enemy]` gives you the current enemy's
statistics. Keep the code within the `Game` object's state and behavior.

## Done when

- [ ] Defend is available only during combat.
- [ ] Defend causes 1 HP loss against the spider and 0 spider HP loss.
- [ ] The next normal Attack still causes the spider's usual 2 HP retaliation.
- [ ] Combat can still be won or lost normally; the Star Crystal is reachable.

**Stretch:** Refactor repeated death handling into a *small* method only if
both attack paths now repeat exactly the same rules.

**Explain it:** Why can Defend be a new `Choice` and method without creating a
new class of enemies or actions?

**Check:** `python assignments/check.py I06`.
