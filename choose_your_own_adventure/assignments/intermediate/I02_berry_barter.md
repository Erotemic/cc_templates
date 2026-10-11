# I02 — Trade a wild berry for a lucky charm

**Time:** 45–60 minutes · **Start:** `intermediate/version1.py` · **Concept:** dispatching functions and updating shared state

## New feature

The forest contains one **`"wild berry"`** to pick. A villager will trade it
for a **`"lucky charm"`**. Picking again must not duplicate berries, and
trading must remove the berry. This is a *real mechanic*, so it belongs in
functions referenced by `ACTION_HANDLERS`.

## Find your starting points (5 minutes)

Read `search_stump()`, `open_chest()`, `ACTION_HANDLERS`, `build_choices()`, and
the `state` dictionary in `main()`. Follow how an action label gets from a
room's `choices` list into a handler function.

## Build it (30–40 minutes)

1. Add a state entry named **`"berry_taken"`**, initially `False`, to the
   dictionary created in `main()`. The player has an `inventory` list already.
2. Add a forest action with ID **`"pick_berry"`**, and a village action with
   ID **`"trade_berry"`**. Put these into the rooms' `choices` lists.
3. Write `pick_berry(player, state)`: the first pickup adds one `"wild berry"`
   and records `berry_taken = True`. Later attempts give no more berries.
4. Write `trade_berry(player, state)`: it refuses a trade if no berry is held;
   otherwise it removes the berry and awards a `"lucky charm"`. Repeating
   the trade cannot duplicate the charm.
5. Register both functions in `ACTION_HANDLERS` so the existing dispatch
   mechanism can call them. Keep the original key-and-chest handlers intact.

**Hint:** Prefer returning a list of story messages from each handler to
printing from inside the function, following the existing handlers' pattern.
You can make a choice disappear when completed, but it's also fine to leave
it visible and respond that there is nothing left to collect or trade.

## Done when

- [ ] The first pickup adds exactly one wild berry; more pickups add none.
- [ ] Trading without a berry does not award a charm.
- [ ] A successful trade removes the berry and adds exactly one lucky charm.
- [ ] The original treasure route remains possible.

**Stretch:** Make the villager's text acknowledge the charm on a later visit.

**Explain it:** What happens if you define a function but forget to register
it in `ACTION_HANDLERS`? Why can't a data-only `result` change inventory?

**Check:** `python assignments/check.py I02`.
