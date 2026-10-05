# Project Directions After the Common Lessons

Students do not need to follow one feature ladder after the common sequence.
Choose a direction that gives the programming concepts a purpose.

## Game mechanics / boss design

Build conditional attacks, support moves, statuses, target-selection rules, or
a multi-phase boss. Use named scenarios and fixed seeds to demonstrate each
phase deliberately.

## Character art

There are two intentionally different still-frame art paths.

**Python code art:** use `CodeSpriteFrame` with repeated shapes, symmetry,
coordinates, helper functions, and loops. Refactor repeated drawing ideas into
functions only after the repetition is visible.

**SVG vector art:** use `SvgSpriteFrame` with files in
`student_game/assets/sprites/`. `space_pirate.svg` and `moon_mage.svg` are
examples. The primary classroom workflow is path-based SVG, so students can
mostly work with `<path d="...">`, fill/stroke styling, groups, and transforms.
SVGs load through pygame/SDL_image rather than an extra Cairo dependency.

A frame is only one picture. Preview a still frame with:

```bash
python render_character.py moon_mage
```

## Character animation

The presentation path is deliberately incremental. You can stop at any stage.

1. Draw one still `CodeSpriteFrame` or `SvgSpriteFrame`.
2. Run it with the default battle motions. The picture itself has not changed;
   the renderer moves the whole picture.
3. Tune the explicit `BobMotion`, `LungeMotion`, `ShakeMotion`, and `FallMotion`
   values in `student_game/catalog.py`.
4. Combine several still frames with `FrameAnimation`.
5. Use `CharacterArt` to associate visuals with semantic states such as
   `idle`, `attack`, `hurt`, and `faint`. Missing states reuse `idle`.
6. For an engine-reading project, trace gameplay state through `BattleScene`
   into `SpriteActor`, frame selection, and whole-character motion.

`Knight of Dawn` is the runnable frame-animation reference in
`student_game/art.py`. Its attack has three `CodeSpriteFrame` objects while its
hurt/faint states deliberately fall back to the idle frame. The same
`FrameAnimation` class can contain `SvgSpriteFrame` objects instead.

Use live preview to see the distinction between static artwork, frame animation,
and whole-character motion:

```bash
python render_character.py knight --state idle --animate
python render_character.py knight --state attack --animate
```

For an exact deterministic instant instead of a live loop:

```bash
python render_character.py knight --state attack --time 0.125
```

The public motion objects currently expose a small **battle motion policy**,
not an arbitrary motion framework. Students tune their parameters. Stronger
students who want the actual arithmetic can inspect:

- `src/rpg_battle/render/sprite_motion.py` for bob/lunge/shake/fall math;
- `src/rpg_battle/render/sprite_animation.py` for `int(time * fps)`, modulo,
  and clamping.

Gameplay remains authoritative. A move or damage event decides what happened;
presentation decides what that state looks like. Do not make gameplay outcomes
depend on animation frame numbers.

## Effects and mathematics

Start with piecewise paths and coordinate functions. Extend into sine waves,
triangle/square waves, damping, harmonics, or other functions when appropriate.
`cycles=1` consistently means one full period for periodic built-in paths.

## Sound

Investigate frequency, duration, envelopes, waveforms, and repetition through
audible changes. Students can treat sound generation as another expression- and
function-based system.

## Experiments and balance

Use `python simulate.py --scenario balance --runs 50`. Make one change, predict
its effect, reuse the seed range, and compare wins, rounds, remaining HP, damage,
and scripted damage/healing command counts. These counts include commands whose
attacks miss; they describe commands returned, not automatic code coverage.

## Software engineering / engine exploration

Follow a question into the engine. Examples:

- Where does `damage(10)` become an HP change?
- How does guarding alter the calculation?
- Where is a target declared legal?
- Why are behavior functions given read-only views?
- Why does `attack` presentation only run for physical/magical moves?
- How does a semantic battle event become a visual animation without letting
  animation frames control game rules?

Change one engine rule, write or update a test, and explain the path from
student API to engine implementation.
