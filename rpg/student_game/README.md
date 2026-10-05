# `student_game`

This directory is the game students author. The engine lives under
`src/rpg_battle/`.

Start with `workshop.py`. It is deliberately limited to the first programming
ideas: move functions, a character, and a simple enemy strategy.

When you want to see more of the same game:

- `workshop_assets.py` contains its palette, procedural sprite frame, effect, sound,
  and music;
- `workshop_battles.py` contains its teams and battle setup;
- `scenarios.py` contains deliberate lesson starting conditions;
- the larger `art.py`, `moves.py`, `characters.py`, and other modules are a
  reusable reference library.

`catalog.py` registers all of those pieces together, so the small workshop still
runs through the complete RPG engine.

For students who are more interested in visual design, `assets/sprites/` also
contains SVG character art. `space_pirate.svg` and `moon_mage.svg` are loaded
directly by pygame, so students can modify them in Inkscape or as readable XML.
The intended classroom workflow is path-first SVG editing: students can mostly
work with `<path>` elements without needing an extra Cairo-based dependency on
school machines.

A still `CodeSpriteFrame` or `SvgSpriteFrame` already gets the default battle
motion defined explicitly as `DEFAULT_CHARACTER_MOTION` in `catalog.py`: idle
bob, attack lunge, hurt shake, and knockout fall. Students who want to go
farther can combine several still frames with `FrameAnimation` and
`CharacterArt`. `Knight of Dawn` in `art.py` is the small runnable example: its
attack uses three code-drawn frames while missing states fall back to idle.

The student-facing vocabulary is `frame` / `art` / `animation` / `motion`.
Characters therefore use `art=...`, and the game registers `ART_ASSETS`. Small
read-only compatibility names such as `character.sprite`, `GAME.sprites`,
`workshop_sprite`, and `SPRITE_ASSETS` remain for older code, but new object
construction uses the canonical `art=` / `art_assets=` names.

Useful commands from the `rpg` directory:

```bash
python main.py --check
python lab.py scenario threshold_25
python lab.py scenario threshold_25 --engine-details
python main.py --scenario threshold_25 --teach
python simulate.py --scenario balance --runs 50
python render_character.py knight --state attack --animate
```

See `docs/student_guide.md`, `docs/CHEATSHEET.md`, and `docs/lessons/`.
