# `student_game`

This directory is the game students author. The engine lives under
`src/rpg_battle/`.

Start with `workshop.py`. It is deliberately limited to the first programming
ideas: move functions, a character, and a simple enemy strategy.

When you want to see more of the same game:

- `workshop_assets.py` contains its palette, procedural sprite, effect, sound,
  and music;
- `workshop_battles.py` contains its teams and battle setup;
- `scenarios.py` contains deliberate lesson starting conditions;
- the larger `art.py`, `moves.py`, `characters.py`, and other modules are a
  reusable reference library.

`catalog.py` registers all of those pieces together, so the small workshop still
runs through the complete RPG engine.

Useful commands from the `rpg` directory:

```bash
python main.py --check
python lab.py scenario threshold_25
python lab.py scenario threshold_25 --engine-details
python main.py --scenario threshold_25 --teach
python simulate.py --scenario balance --runs 50
```

See `docs/student_guide.md`, `docs/CHEATSHEET.md`, and `docs/lessons/`.
