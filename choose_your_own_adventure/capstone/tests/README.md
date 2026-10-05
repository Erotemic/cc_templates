# Capstone tests

The capstone is large enough to use the same testing layers as a real software
project:

- `test_world_validation.py` checks authored data before gameplay begins.
- `test_state_machine.py` checks transition invariants and runs deterministic
  random simulations through both complete worlds.
- `test_frontends.py` proves the console path works without Textual and that UI
  selection fails cleanly when an optional dependency is missing.
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
