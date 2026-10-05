# SVG character art

This folder is for character art authored as SVG vector graphics instead of
Python shape calls.

`space_pirate.svg` and `moon_mage.svg` are the current examples. The game
loads them directly through pygame / SDL_image, so there is no generated PNG to
keep in sync and no extra Cairo dependency to install on school machines.

`moon_mage.svg` is a direct vector port of the earlier `moon_mage_pil.py`
design rather than a new character design. Its groups follow the same visible
parts: staff, cape, legs and boots, face, hair, hood, front cloak, and spell.

A good editing loop is:

1. Open `space_pirate.svg` or `moon_mage.svg` in a text editor, browser, or
   vector editor such as Inkscape.
2. Change one path, color, or group.
3. Save the SVG.
4. From the `rpg` directory run:

   ```bash
   python render_character.py moon_mage
   ```

`space_pirate.svg` uses a `1024 x 1024` `viewBox` and named groups such as
`head`, `helmet`, `torso`, `jetpack`, `plasma-cutlass`, and `pistol-arm`.
`moon_mage.svg` keeps the `512 x 768` coordinate system of its original Python
art. Group names are not required by the engine, but they make the files easier
to teach.

## Path-first SVG workflow

If `path` is the main SVG concept you want to teach, that is enough.
Students can draw almost everything with paths, and vector editors can convert
most other shapes into paths.

Useful ideas to experiment with:

- `<path>` for silhouettes, hair, coats, weapons, and expressive outlines
- `M`, `L`, `C`, `Q`, and `Z` commands inside `d="..."`
- relative commands such as `m`, `l`, and `c`
- `fill` and `stroke` for color and outlines
- `stroke-width`, `stroke-linecap`, and `stroke-linejoin`
- `<g id="...">` for organizing related pieces
- `transform` for moving or reusing a small design

Keep each SVG's root `viewBox` stable while editing unless you also intend to
retune that frame's `scale=` value in `student_game/art.py`.

`moon_mage.svg` uses readable group names such as `staff`, `cape`, `legs`,
`face`, `hair`, `hood`, `front-cloak`, and `spell`.

## Still frames and animation

The game treats one drawing as one **sprite frame**:

```python
from rpg_battle.api import SvgSpriteFrame

hero = SvgSpriteFrame(
    "My Hero",
    "assets/sprites/my_hero.svg",
)
```

That frame does not need to contain animation. The default battle presentation
in `student_game/catalog.py` moves the whole frame for you: characters bob while
idle, lunge when they attack, shake when hurt, and fall when knocked out.

If you later want true frame-by-frame animation, draw several SVG files and put
them in a `FrameAnimation`:

```python
from rpg_battle.api import CharacterArt, FrameAnimation, SvgSpriteFrame

idle = SvgSpriteFrame("Hero Idle", "assets/sprites/hero_idle.svg")
attack_1 = SvgSpriteFrame("Hero Attack 1", "assets/sprites/hero_attack_1.svg")
attack_2 = SvgSpriteFrame("Hero Attack 2", "assets/sprites/hero_attack_2.svg")
attack_3 = SvgSpriteFrame("Hero Attack 3", "assets/sprites/hero_attack_3.svg")

hero = CharacterArt(
    "Hero",
    idle=idle,
    attack=FrameAnimation(
        [attack_1, attack_2, attack_3],
        fps=8,
        loop=False,
    ),
)
```

You do not have to draw special `hurt` or `faint` frames. Any missing state
reuses the idle frame. The whole-character shake/fall motion still applies.

You can play a presentation state live without starting a battle:

```bash
python render_character.py moon_mage --state idle --animate
python render_character.py knight --state attack --animate
```

For a deterministic snapshot at one exact animation time:

```bash
python render_character.py knight --state attack --time 0.125
```

The important separation is:

- a **frame** is one picture;
- a **frame animation** chooses pictures over time;
- a **motion** moves the whole picture;
- battle code chooses semantic states such as `attack` or `hurt`.
