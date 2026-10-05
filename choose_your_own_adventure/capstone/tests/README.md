# Capstone tests

The capstone is large enough to use the same testing layers as a real software
project:

- `test_world_validation.py` checks authored data before gameplay begins.
- `test_state_machine.py` checks transition invariants, verifies that every
  selected action returns same-turn player feedback, and runs deterministic
  random simulations through both complete worlds.
- `test_river_crossing.py` demonstrates a focused state-machine test: it
  exhaustively explores the wolf/goat/cabbage transitions, then drives the same
  puzzle through the complete Star Crystal game.
- `test_frontends.py` proves the console path works without Textual, checks
  free-text riddle presentation for duplicate/delayed output, and verifies that
  UI selection fails cleanly when an optional dependency is missing.
- The repository-level `tests/test_capstone.py` contains long story-path and
  ending tests that exercise the preserved Star Crystal and Dust Vault content.

Run just the capstone engineering tests:

```bash
python -m pytest capstone/tests -q
```

Run the full project suite:

```bash
python -m pytest -q
```

Stress the state machine outside pytest:

```bash
python capstone/simulate.py --world both --runs 25 --steps 250
```

## Architecture regression tests

`test_architecture_contracts.py` protects the boundaries that make the larger
engine robust. In particular it checks that:

- only `__init__` and `_transition_mode()` assign the game mode;
- terminal flags are synchronized before automatic encounter reactions;
- duplicate loose items still produce one unambiguous menu action;
- malformed world records fail validation instead of crashing when reached;
- the validator itself reports bad collection shapes rather than raising a
  `TypeError`;
- corrupt runtime context fails at the next public action boundary;
- story behavior is not coupled to the old source filename or hard-coded NPC
  names in the core engine.

These are examples of tests for *architecture*, not just individual outputs.
