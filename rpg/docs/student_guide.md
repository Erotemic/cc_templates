# Student Guide

## Where to start
Open the `content` folder first. Most of the fun customization lives there.

## Easy first edits
1. Change a color in `colors.py`.
2. Change a face shape in `sprites.py`.
3. Give a character a different move in `characters.py`.
4. Put a different hero on the player's team in `teams.py`.

## Make a new character
Copy one character block in `characters.py`, rename it, then change:
- `name`
- stats
- `sprite_id`
- move ids

## Make a new move
Copy a move in `moves.py`. Change:
- `name`
- `kind`
- `power`
- `animation`
- status or stat effects

## Math challenge path
Look for `sine_wave` and `square_pulse` in `moves.py`.
Then inspect `effect_factory.py` to see how points are sampled.

Try these upgrades:
- change amplitude
- change wavelength
- make a triangle wave
- make a noisy wave
- build a Weierstrass-like spell


## Add or swap music
Open `content/audio.py`.

- Change `DEFAULT_BATTLE_TRACK` to pick a different song. The current default is `soft_dungeon_crawl`.
- Put new songs in `assets/audio/` later and add them to `MUSIC_TRACKS`.
- Generated music works without any extra files, and numpy is available if students want to experiment with richer synthesis.

## Change menu and move sounds
Still in `content/audio.py`:

- `SOUND_EFFECTS` controls menu move, confirm, back, and move sounds.
- Try changing `frequency`, `duration`, `waveform`, or `noise`.

In `content/moves.py`:

- set `sound_id` on a move to choose which sound it plays.
- You can make two moves share one sound, or give every move its own sound.


## Debugging tips
- Run the game from a terminal to see `loguru` debug output.
- Set `RPG_BATTLE_LOG_LEVEL=DEBUG` if you want to watch the turn controller more closely.
- After making changes, run `ruff format .` so the code stays tidy and easier to compare.
