# `student_game`

This directory is the game students author. The engine lives under
`src/rpg_battle/`.

Start with `workshop.py`, not the larger reference modules.

The workshop demonstrates the complete registration path for palettes, sprites,
effects, sounds, music, moves, characters, teams, and battles. When the
workshop becomes crowded, move your content into a new module and add its lists
to `catalog.py`.

Named lesson setups live in `scenarios.py`. They describe deliberate starting
conditions without putting game-specific ids into the reusable engine.

Useful commands from the `rpg` directory:

```bash
python main.py --check
python lab.py scenario threshold_25
python main.py --scenario threshold_25 --teach
python simulate.py --scenario balance --runs 50
```

See `docs/student_guide.md`, `docs/CHEATSHEET.md`, and `docs/lessons/`.
