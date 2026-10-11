# I07 — Open the tower by pacifying the spider

**Time:** 50–60 minutes · **Start:** `intermediate/version3.py` · **Concept:** Boolean conditions and alternate quest paths

## New feature

Players can avoid fighting the ruin spider. They can collect **`"spider bait"`**
in the forest and use it to **pacify** the spider at the ruins. They still need
the `"tower key"` to enter the tower. The original fight-and-key solution must
continue to work.

## Find your starting points (5 minutes)

Read the `gate_open` condition in `Game.choices()`, the ruins actions, the
`spider_defeated` flag, and `apply_world_action()`. The goal is to express two
valid solutions without making a second copy of the entire game.

## Build it (30–40 minutes)

1. Offer **`"take_bait"`** in the forest until it has been collected; this
   adds one `"spider bait"` item to inventory.
2. Offer **`"calm_spider"`** at the ruins while the spider is still active
   and the player has the bait. It consumes the bait, adds the flag
   **`"spider_pacified"`**, and gives a story result without entering combat.
3. After pacifying, the **Fight spider** choice should disappear. The player
   must still be able to fight instead of pacifying if they prefer.
4. Change the tower's gate condition to require `"tower key"` **and**
   **either** `"spider_defeated"` **or** `"spider_pacified"`.
5. Test that bait alone cannot open the tower without the key, then collect
   the key through the normal moon-herb trade and enter peacefully.
6. Start a second game and complete the original combat solution.

**Hint:** Parentheses make the condition clear: the key is required in all
cases, while the spider obstacle has two solutions. Do not set
`"spider_defeated"` when the spider is pacified: those are different events.

## Done when

- [ ] The forest bait can be taken once and used once.
- [ ] Pacifying the spider avoids combat and disables the fight choice.
- [ ] The gate stays locked without the tower key, even after pacifying.
- [ ] Both the peaceful route and the original combat route can win.

**Stretch:** Adjust `describe()` so it describes a calm spider after pacifying,
instead of still saying that one guards the tower.

**Explain it:** What is the difference between `(has_key and defeated) or
pacified` and `has_key and (defeated or pacified)`? Which describes your rule?

**Check:** `python assignments/check.py I07`.
