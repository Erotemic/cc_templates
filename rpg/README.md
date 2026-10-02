# RPG Battle Classroom Project

A real pygame fantasy battle game designed to be **changed by students**.

The project deliberately has two layers:

```text
student_game/                 <- start here: your characters, moves, art, battles, audio
src/rpg_battle/                <- engine: turn rules, AI, rendering, menus, audio playback
```

The engine is still normal Python and is meant to be explored later. The important
change is that students can now build a substantial game without first editing the
engine's internal registries.

## What the game already supports

- active + reserve party battles, including 1v1, 2v2, and 3v3 setups
- switching, defending, knockouts, and replacement characters
- physical, magical, healing, buff, debuff, and status moves
- temporary stat stages and statuses such as burn, slow, stun, guard, and focus
- simple AI opponents and boss encounters
- procedural characters drawn from circles, rectangles, polygons, and lines
- graph-based spell effects, including sine, square, staircase, and transform effects
- custom mathematical path functions written in ordinary Python
- synthesized sound effects and generated music
- fast character, battle, effect, and audio preview tools
- custom move functions that use ordinary Python control flow

## Quick start

From this folder:

```bash
python main.py --check
python main.py
```

`--check` validates the student's game without opening pygame. It catches content
problems such as a missing move, unknown sprite, impossible battle lineup, or missing
music track and reports them together.

If a Python dependency is missing, `main.py` prints the packages to install.

## Where students should start

The top-level `student_game/` directory is the authored game:

```text
student_game/
├── art.py          palettes and procedural character drawings
├── audio.py        songs and synthesized sound effects
├── effects.py      attack animations and graph-shaped spell paths
├── moves.py        move definitions and programmable move functions
├── characters.py   stats + art + moves
├── battles.py      teams and launchable battles
└── catalog.py      assembles everything into one Game
```

A character now uses direct Python references:

```python
knight = Character(
    "Knight of Dawn",
    role="defender",
    hp=58,
    attack=10,
    defense=9,
    magic=4,
    speed=4,
    sprite=art.knight_dawn,
    moves=[moves.shield_bash, moves.stone_ward, moves.strike],
)
```

There is no string like `"shield_bash"` that must secretly match a registry elsewhere.
The variable `moves.shield_bash` refers to the move itself.

## From changing values to programming mechanics

Most moves are intentionally simple data:

```python
shield_bash = Move(
    "Shield Bash",
    kind="physical",
    power=11,
    animation=effects.impact,
    sound=audio.shield_bash,
    effects=[status("stun", turns=1, chance=0.20)],
)
```

Students can then graduate to writing behavior:

```python
def desperate_strike_logic(ctx):
    if ctx.user.hp_ratio < 0.5:
        return damage(18)
    return damage(8)


desperate_strike = Move(
    "Desperate Strike",
    kind="physical",
    animation=effects.impact,
    sound=audio.attack_basic,
    action=desperate_strike_logic,
)
```

The function decides *what the move means*. The engine still handles HP mutation,
combat events, knockouts, animation, and battle flow. This keeps the extension point
small enough to learn while allowing real programming.

## Preview tools

Students do not need to play an entire battle after every edit:

```bash
python render_character.py knight
python render_battle_state.py --encounter boss_ai_slop
python render_effect.py sine_wave
python render_audio.py bluesy_overhaul --kind music
```

Most render tools show/play the result by default and also save the generated artifact.
Use `--no-show` where supported when only the file is wanted.

## Launch different battles

```bash
python main.py --encounter training_duel
python main.py --encounter frontline_brawl
python main.py --encounter boss_ai_slop
python main.py --encounter boss_null_hydra
```

The CLI can also override teams, active limits, and music:

```bash
python main.py --encounter default --music-track soft_dungeon_crawl
python main.py --player-team extra --enemy-team duel_enemy --player-limit 2 --enemy-limit 1
```

## Installed-project mode

Direct execution is the beginner path. Later, students can learn packaging:

```bash
python -m pip install -e .
rpg-battle --check
rpg-battle
```

The top-level `student_game` package is installed alongside the reusable `rpg_battle` engine,
so the same authored game is used in both modes.

## Going deeper

The engine consumes one explicit normalized `GameContent` object. Core battle rules,
AI, audio, rendering, and scene code do not import this particular game's content.
`student_game/catalog.py` also wires the basic attack, menu/combat sounds, and standard
heal effect through a `GamePresentation` object, so those choices are not hidden engine
string conventions either. That separation gives advanced students several natural next
steps:

1. inspect how their `Character` becomes a `CharacterSpec`;
2. trace a `Move` through the action/event pipeline;
3. modify AI or battle rules in `src/rpg_battle/core/`;
4. add a new authoring primitive to `rpg_battle.api`;
5. build an entirely different `student_game/` on the same engine.

See `docs/student_guide.md` for a progression of classroom projects and
`docs/teacher_notes.md` for suggested lesson sequencing.
