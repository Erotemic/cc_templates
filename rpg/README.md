# RPG Battle Classroom Project

A pygame fantasy battle engine designed so high-school students can learn real
Python by modifying and extending a rich game.

## Start here

From the `rpg` directory:

```bash
python main.py --check
python lab.py scenario threshold_25
python main.py --scenario threshold_25 --teach
```

Then open:

```text
student_game/workshop.py
```

The workshop is a small starting surface inside the full game. It contains a
complete example of original art, effects, sound, music, moves, a character,
teams, and battles.

## Trustworthy feedback

The teaching tools are intended to agree with the actual engine:

- command targets are validated both before play and at runtime;
- custom-move smoke tests respect the move's real target mode;
- AI strategy targets are checked for legality;
- scripting views expose effective stats used by the rules, plus `base_*` stats;
- importing the game performs structural validation without executing student
  behavior functions;
- `python main.py --check` explicitly tests those behaviors;
- the move lab's damage/healing explanation is recorded by the real rules
  engine while the move resolves.

## Deliberate teaching scenarios

```bash
python lab.py scenario threshold_25
python lab.py scenario threshold_26
python lab.py scenario threshold_27
python lab.py scenario chain_lightning
python lab.py scenario target_selection
python lab.py scenario healing
```

Play the same setup by replacing `lab.py scenario` with:

```bash
python main.py --scenario <scenario> --teach
```

For a balance experiment:

```bash
python simulate.py --scenario balance --runs 50
```

The simulator reports wins, average rounds, remaining HP, damage, move usage,
and scripted command powers so students can see changes hidden by win rate.

## Curriculum and references

- `docs/student_guide.md` — student workflow and scenarios
- `docs/CHEATSHEET.md` — scripting patterns and commands
- `docs/lessons/` — six common lessons from prediction to independent creation
- `docs/projects.md` — parallel creative project directions
- `docs/teacher_notes.md` — teaching contracts and classroom guidance
- `docs/setup.md` — classroom setup

## Full game features

The reference game remains deliberately rich:

- active/reserve party battles and switching;
- status effects and temporary stat changes;
- student-programmable move behavior and enemy strategies;
- procedural character art;
- mathematical path effects;
- generated sound effects and music;
- deterministic labs, named scenarios, and headless simulation;
- render/preview tools;
- a reusable engine that advanced students can inspect.

Students are not expected to understand all of this before starting. The engine
is a destination for deeper investigation, not a prerequisite for changing the
game.

## Setup

See `docs/setup.md`. The shortest editable install is:

```bash
python -m pip install -e ".[classroom]"
python main.py --check
```

## Development / previews

```bash
python render_character.py workshop_hero
python render_effect.py classroom_wave
python render_battle_state.py --encounter workshop
python render_audio.py --kind music workshop_theme
python -m pytest -q
```

Installed equivalents include `rpg-battle`, `rpg-battle-lab`, and
`rpg-battle-simulate`.
