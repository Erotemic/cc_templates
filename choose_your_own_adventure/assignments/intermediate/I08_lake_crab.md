# I08 — Add a lake crab with its own reward

**Time:** 50–60 minutes · **Start:** `intermediate/version3.py` · **Concept:** data-driven mechanics and fixing an over-specific assumption

## New feature

The lake has a **`"lake_crab"`** enemy. Fighting it is optional. The crab has
**8 HP** and deals **1 damage per hit**. Defeating it awards **3 gold**, and
the crab cannot be fought a second time. Beating the crab must **not** unlock
the tower: that still requires defeating the spider (or other rules added in
separate assignments).

## Find your starting points (5 minutes)

Read the `EnemySpec` dataclass, `ENEMIES`, `Game.start_combat()`,
`Game.attack_enemy()`, and the lake/ruins branches in `Game.choices()` and
`Game.apply_world_action()`.

## Build it (30–40 minutes)

1. Add an `EnemySpec` entry with key **`"lake_crab"`**, 8 HP, and attack 1.
2. Offer an optional **`"fight_crab"`** action at the lake before the crab
   is defeated. Make it call `start_combat("lake_crab")`.
3. Change the defeat branch of `attack_enemy()`: it currently sets
   `"spider_defeated"` for *every* enemy. Award that flag **only for the
   `"ruin_spider"`**. For `"lake_crab"`, set `"crab_defeated"` and award
   exactly three gold instead.
4. Hide the fight choice after the crab is defeated. Keep normal Attack and
   Run behavior for both encounters.
5. Beat the crab, confirm the gold increased, then visit the ruins. The
   spider should still be there and the tower should still require its rules.

**Hint:** The key in `self.combat_enemy` identifies the encounter while it is
happening. Save it in `defeated_key` *before* setting `self.combat_enemy = None`.
The existing method already does that for the spider's message.

## Done when

- [ ] The lake crab can be fought once, with 8 HP and 1 damage per attack.
- [ ] Defeating it gives 3 gold and records `"crab_defeated"`.
- [ ] Defeating the crab does not set `"spider_defeated"` or bypass the gate.
- [ ] The original spider, key, and Star Crystal story still work.

**Stretch:** Improve the Run message so it mentions whether you escaped from
the crab or the spider, without changing combat mechanics.

**Explain it:** Why did `attack_enemy()` appear correct with only one enemy,
and what made that implementation wrong after adding a second?

**Check:** `python assignments/check.py I08`.
