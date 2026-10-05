# Capstone adventures

Capstone contains the complete, content-heavy games. It is not a signal that a
student must understand every engine subsystem before contributing.

- `version1.py` runs the complete **Star Crystal** world from the original deep
  game line.
- `version2.py` runs the complete **Dust Vault** world from the original final
  game.
- `engine/` contains reusable mechanics plus console and Textual frontends.
- `art/` contains presentation-only ASCII art for locations, characters, and
  story moments.
- `worlds/` contains the faithfully ported authored worlds.
- `tests/` contains capstone-local software-engineering tests.
- `simulate.py` drives the full games headlessly and checks state invariants.

There is deliberately no `rich.py`: module names describe responsibilities
(`game.py`, `models.py`, `actions.py`, `console.py`, `textual_app.py`) rather
than how large a game happens to be.


## Full presentation layer

The capstone restores the best presentation work from the original v5-v8 line
without restoring its I/O bridge complexity. `AdventureGame` remains independent
of terminal/UI code; both frontends drive the same `snapshot()`, `choices()`,
`apply()`, and free-text riddle APIs.

The Textual frontend includes:

- goal, location, status, equipment, and inventory panels;
- a dedicated scene-art panel;
- `OptionList` keyboard/click navigation and number-key shortcuts;
- free-text riddle input;
- a focused latest-event panel plus collapsible history;
- lightweight typewriter-style result streaming;
- `M` for inventory, `L` for history, `C` to clear history, `A` to hide/show
  artwork, `Esc` to return focus, and `Q` to quit.

Star Crystal retains all **50** original v7 scene keys, including Elder Mira and
every other named character in alive/defeated states, and adds new art for the
Hearthfield Farm / Willow River side quest. Only the current polished drawings
are kept; the old duplicate legacy-art table has been removed. Dust Vault has art
for all 18 locations, every named NPC, Patrol Drone, Glass Maw, and major story
beats/endings. Student-added rooms/NPCs receive presentation fallbacks even if
they do not add art yet.

Presentation never decides gameplay. Art selection reads state and the latest
outcome only.

## Wolf, goat, and cabbage side quest

Star Crystal now includes an optional delivery quest at **Hearthfield Farm**,
reached from the Old Crossroads. Farmer Elowen asks the player to deliver a
wolf, goat, and cabbage to the far side of Willow River.

Without the quest, Willow River is ordinary travel: take the boat east or west.
With all three passengers in your care, the same boat becomes a small explicit
state machine. The boat can carry the player plus one passenger, and a proposed
transition is rejected if it would leave either unsafe pair unattended:

- wolf + goat;
- goat + cabbage.

The pure transition rules live in `engine/river_crossing.py`; world/story data
still lives in `worlds/star_crystal.py`. This makes the puzzle useful as a
capstone programming example: students can inspect a compact state machine,
its invariant, and its tests without having to understand the rest of combat or
dialogue machinery.

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
paths through both games. The runtime also preserves consequential interaction
behavior from the originals: exploration encounters are reevaluated between
turns, dead NPCs cannot talk/trade/challenge/fight, surrendered enemies still
produce the explicit Spare/Kill decision, and corpse inventories are looted
item-by-item rather than automatically.

### Three reachability repairs

The port makes three narrow fixes where original narrative text described a path
that the old interaction code did not make reachable:

1. A correct Tower Guardian riddle answer grants the Star Crystal without
   requiring the player to kill the guardian.
2. A correct Custodian Echo riddle answer grants the Grave Core without
   requiring the player to kill the custodian.
3. Rafe's post-vault offer records that the offer was heard, so the authored
   landing-beacon corporate ending can actually be selected.

The preserved source world fields are otherwise unchanged; these are engine
reachability repairs.

### One intentional gameplay polish

Resting at Sunmeadow Village's fountain now restores the player to full health.
The original serialized `HealPlayerEffect.amount` is retained for provenance,
and the port adds an explicit `full_heal` flag so the behavior is readable in
the world data rather than hidden in engine special cases.

## Run

```bash
# Best capstone experience (Textual is used automatically when installed)
python -m pip install textual
python capstone/version1.py
python capstone/version2.py

# Frontends are intentionally interchangeable
python capstone/version1.py --ui textual
python capstone/version1.py --ui console
```

The game rules expose `snapshot()`, `describe()`, `choices()`, and `apply()`.
Neither frontend owns gameplay state. The console path also shows the same ASCII
art, so the complete presentation remains usable on a machine without Textual.


### Same-turn feedback contract

`AdventureGame.apply()` treats a player selection as a transaction: every legal
menu action returns at least one nonblank result line in the same call. Movement,
inventory transitions, NPC approach/leave, combat initiation, looting, and
data-only room choices therefore cannot silently mutate state and rely on the
next click to reveal what happened. The simulator asserts this contract after
every generated action.

The Textual frontend also paints the first result chunk synchronously before its
optional typewriter stream continues, while the console frontend prints riddle
intro/question/answer feedback exactly once.

## Testing is part of the capstone

The capstone deliberately shows more than unit tests for individual helper
functions. It uses several layers that students will encounter in real software
projects:

1. **World-data validation** checks room/item/NPC/effect references when a game
   is constructed. A misspelled destination or unknown item fails near the
   authored data instead of much later during play.
2. **State-transition tests** encode invariants such as `0 <= HP <= max HP`,
   combat context existing only during combat, pending exits existing only
   during move confirmation, and every committed wolf/goat/cabbage river state
   satisfying the puzzle's safety rule.
3. **Regression tests** lock bugs that have actually occurred: false tonic
   shatter art, stale combat context after death, equipment/HP drift, dead-NPC
   interactions, bounty/jail reactions, surrender choices, selective loot, and
   same-turn feedback so a menu action cannot appear to resolve one click late.
4. **Story tests** drive full Star Crystal and Dust Vault paths, including all
   three Dust Vault endings.
5. **Frontend tests** exercise the console without a terminal and verify that
   the game falls back cleanly when optional Textual is absent.
6. **Deterministic simulation** performs many legal random transitions while
   checking invariants after every action.

Run the capstone-specific tests:

```bash
python -m pip install -r capstone/requirements-dev.txt
python -m pytest capstone/tests -q
```

Run the whole curriculum suite:

```bash
python -m pytest -q
```

Stress both complete worlds without either UI:

```bash
python capstone/simulate.py --world both --runs 25 --steps 250
```

To inspect one simulated run transition-by-transition:

```bash
python capstone/simulate.py --world star --runs 1 --steps 100 --trace
```

Optional branch coverage is also straightforward:

```bash
coverage run --branch -m pytest -q
coverage report -m
```

The simulator and tests call the same `choices()` / `apply()` API as the
frontends. This is why the game remains fully testable when Textual is not
installed.
