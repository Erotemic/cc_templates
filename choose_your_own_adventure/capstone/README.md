# Capstone adventures

Capstone contains the complete, content-heavy games. It is not a signal that a
student must understand every engine subsystem before contributing.

- `version1.py` runs the complete **Star Crystal** world from the original deep
  game line.
- `version2.py` runs the complete **Dust Vault** world from the original final
  game.
- `engine/` contains the reusable mechanics.
- `worlds/` contains the faithfully ported authored worlds.

There is deliberately no `rich.py`: module names describe responsibilities
(`game.py`, `models.py`, `actions.py`, `console.py`) rather than how large a game
happens to be.

## Easiest way to add content

Go to the bottom of a world file and use `EXTRA_ROOMS` / `EXTRA_CHOICES`.
Students do not have to navigate the large preserved original dictionaries.

```python
EXTRA_ROOMS = {
    "old_observatory": {
        "name": "Old Observatory",
        "description": "Dusty lenses point at a hole in the roof.",
        "exits": [
            {"direction": "south", "destination": "crossroads"},
        ],
        "choices": [
            {
                "text": "Look through the telescope",
                "result": [
                    "A blue star flickers exactly where the old notes predicted."
                ],
            },
        ],
    },
}

EXTRA_CHOICES = {
    "crossroads": [
        {"text": "Climb the hill to the old observatory", "go": "old_observatory"},
    ],
}
```

The engine supplies empty defaults for omitted items, NPCs, and features.
Simple choices can optionally use `go`, `give_items`, `set_flags`,
`requires_flags`, `blocked_flags`, and `once_flag` before a student needs to add
a new mechanic.

## What is preserved

The port preserves the original authored room graph and records, including:

- room names/descriptions and every exit;
- duplicated direction labels where the original world intentionally had them;
- items and equipment statistics;
- NPC statistics, inventories, dialogue topics, trades, riddles, and surrender
  data;
- features and scripted outcomes;
- gate requirements and blocked-path behavior;
- encounter definitions and conditions;
- the Dust Vault ending branches.

Tests lock this data with canonical fingerprints and play representative full
paths through both games.

### Three reachability repairs

The port makes three narrow fixes where original narrative text described a path
that the old interaction code did not make reachable:

1. A correct Tower Guardian riddle answer grants the Star Crystal without
   requiring the player to kill the guardian.
2. A correct Custodian Echo riddle answer grants the Grave Core without
   requiring the player to kill the custodian.
3. Rafe's post-vault offer records that the offer was heard, so the authored
   landing-beacon corporate ending can actually be selected.

The preserved source world records are otherwise unchanged; these are engine
reachability repairs.

## Run

```bash
python capstone/version1.py
python capstone/version2.py
```

The game rules expose `describe()`, `choices()`, and `apply()`. Terminal I/O is
confined to `engine/console.py`, so another frontend can drive the same full
game later without rewriting it.
