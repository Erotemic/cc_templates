# SVG character art

This folder is for character art authored as SVG vector graphics instead of
Python shape calls.

`space_pirate.svg` is the first example. The game loads it directly with
pygame, so there is no generated PNG to keep in sync.

A good editing loop is:

1. Open `space_pirate.svg` in a text editor, browser, or vector editor such as
   Inkscape.
2. Change one shape, color, or group.
3. Save the SVG.
4. From the `rpg` directory run:

   ```bash
   python render_character.py space_pirate
   ```

The SVG uses a `1024 x 1024` `viewBox` and named groups such as `head`,
`helmet`, `torso`, `jetpack`, `plasma-cutlass`, and `pistol-arm`. Keeping those
groups intact is not required by the engine, but it makes the file easier to
understand and edit.

## Useful SVG ideas to experiment with

- `<polygon>` and `<polyline>` for silhouettes and armor
- `<circle>` / `<ellipse>` for faces, eyes, lights, and emblems
- `<rect rx="...">` for rounded equipment panels
- `fill` and `stroke` for color and outlines
- `stroke-width`, `stroke-linecap`, and `stroke-linejoin`
- `<g id="...">` for organizing related pieces
- `transform` for moving or reusing a small design

Keep the root `viewBox="0 0 1024 1024"` unless you also intend to retune the
sprite's `scale=` value in `student_game/art.py`.
