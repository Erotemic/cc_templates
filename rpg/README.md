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
python -m pip install pygame numpy loguru rich
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

## What students can change quickly
- colors and shapes
- character stats and move lists
- wave spell parameters
- team lineups
- battle names and flavor text


## Audio customization
- The default battle song is `soft_dungeon_crawl` in `src/rpg_battle/content/audio.py`.
- Generated music is now built through reusable `TrackBuilder` subclasses in `src/rpg_battle/audio/tracks.py`.
- Shared synthesis helpers live in `src/rpg_battle/audio/builder.py`.
- Add a new track by registering a new `GeneratedTrackSpec` in `content/audio.py` and a matching builder class in `audio/tracks.py`.
- Edit `SOUND_EFFECTS` to change menu blips and move sounds.
- Each move in `src/rpg_battle/content/moves.py` can point at a different `sound_id`.
- The engine caches rendered generated tracks under `~/.cache/rpg_battle/audio/` so later startups can reuse them.



## Development render tools
The project now keeps its CLI tools in `src/rpg_battle/cli/`, with friendly top-level wrappers for convenience.

- Render one character quickly: `./render_character.py knight`
- Render the initial battle layout: `./render_battle_state.py`
- Render the scene with the first player menu open: `./render_battle_state.py --open-menu`
- Render a built-in music track or sound effect: `./render_audio.py --kind music soft_dungeon_crawl`

If you run these without the main id argument, a small `rich` prompt lets students browse the registered options and choose what to render.

By default, outputs land in the current working directory:
- `./knight_preview.png`
- `./battle_preview.png`
- `./soft_dungeon_crawl.wav`

These helpers are useful when students are changing `content/sprites.py`, `content/characters.py`, encounter layouts, or audio assets and want fast feedback without playing a whole battle.

## Debugging and formatting
- Terminal logging now uses `loguru` so students can watch the higher-level architecture: battle setup, round queues, turn starts, menu flow, action resolution, and audio lookup.
- Set `RPG_BATTLE_LOG_LEVEL=DEBUG` before launch to get more detailed logs without flooding the terminal with per-frame game-loop noise.
- Run `ruff format .` after edits to keep the code layout consistent.


## Preview tools

The preview tools now **show or play their result by default**. Use `--no-show` when you only want to save the artifact.

Examples:

```bash
./render_character.py knight
./render_battle_state.py --encounter blues_night
./render_audio.py bluesy_overhaul --kind music

./render_character.py knight --no-show
./render_battle_state.py --encounter boss_ai_slop --no-show
./render_audio.py boss_battle_frenzy --kind music --no-show
```

## Game launcher

The main game is configurable from the command line:

```bash
python run_game.py --encounter boss_ai_slop
python run_game.py --encounter default --music-track bluesy_overhaul
python run_game.py --player-team extra --enemy-team duel_enemy --player-limit 2 --enemy-limit 1
```
