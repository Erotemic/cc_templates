# Lesson 6 — Make and Explain

**Prerequisites:** the earlier common lessons.

`student_game/workshop.py` is intentionally small: it contains the first move
functions, a character, and a simple enemy strategy. The neighboring
`workshop_assets.py` and `workshop_battles.py` show how the same project adds
art/audio and battle setup when students are ready for them.

## Supported creation

Copy one small object at a time and make it visibly yours. Use the preview tools
for art/effects and the lab for move behavior.

## Independent task

Create or substantially modify **one meaningful playable behavior**, integrate
it into the game, test it, and be able to explain how it works.

Good choices include:

- write a new move with a conditional or loop;
- change targeting or enemy decision-making;
- create a new `CodeSpriteFrame` or `SvgSpriteFrame`;
- turn several frames into a `FrameAnimation`;
- tune the game's default whole-character motion;
- design a new battle or boss phase;
- intentionally redesign an effect or sound.

You do **not** have to do every discipline at once. Art, audio, animation, game
mechanics, and AI are different project tracks after the common programming
lessons.

Your work should pass:

```bash
python main.py --check
```

If you edited SVG art, also preview at least one SVG character so the actual
pygame/SDL_image renderer is exercised:

```bash
python render_character.py moon_mage --no-show
```

## Explain

Demonstrate one behavior to another student. Explain:

1. the important input facts;
2. the control flow or data that you changed;
3. what your code asks the game to do;
4. what the engine then calculated, animated, or changed.

## Choose a project direction

Continue with mechanics/boss design, procedural or SVG art, frame-by-frame
animation, mathematical effects, sound/music, experiments and balance, or
engine/software-engineering work. See `docs/projects.md` for concrete paths.
