# RPG Battle Classroom Project

A small but real pygame fantasy battle engine built for students to modify.

## Features
- 3v3 party battles
- Procedural battlers drawn from shapes
- Skill, defend, and switch actions
- Floating combat text and simple animations
- Built-in music and sound effects with easy track swapping
- Path-based spell effects including sine and square waves
- Content-first editing workflow in `src/rpg_battle/content/`

## Quick start

From the project root, the simplest launch command is:

```bash
python run_game.py
```

If you want the package installed in editable mode:

```bash
python -m pip install -e .
python -m rpg_battle
```

Or without an editable install:

```bash
python -m pip install pygame numpy loguru
PYTHONPATH=src python -m rpg_battle
```

## Best student entry points
Start in these files:
- `src/rpg_battle/content/characters.py`
- `src/rpg_battle/content/moves.py`
- `src/rpg_battle/content/sprites.py`
- `src/rpg_battle/content/teams.py`
- `src/rpg_battle/content/audio.py`

## Controls
- Arrow keys: move through menus
- Enter / Space: confirm
- Escape / Backspace: cancel
- R: restart battle
- Q: quit

## What students can change quickly
- colors and shapes
- character stats and move lists
- wave spell parameters
- team lineups
- battle names and flavor text


## Audio customization
- The default battle song is now `soft_dungeon_crawl` in `src/rpg_battle/content/audio.py`.
- Edit `MUSIC_TRACKS` to swap between `soft_dungeon_crawl`, `training_battle`, or a future `.wav` / `.ogg` file.
- Edit `SOUND_EFFECTS` to change menu blips and move sounds.
- Each move in `src/rpg_battle/content/moves.py` can point at a different `sound_id`.


## Debugging and formatting
- Terminal logging now uses `loguru` so students can watch turn order, menu choices, and action resolution while the game runs.
- Set `RPG_BATTLE_LOG_LEVEL=DEBUG` before launch to get more detailed logs.
- Run `ruff format .` after edits to keep the code layout consistent.
