# SVG character art

This folder is for character art authored as SVG vector graphics instead of
Python shape calls.

`space_pirate.svg` and `moon_mage.svg` are the current examples. The game
loads them directly through pygame / SDL_image, so there is no generated PNG to
keep in sync and no extra Cairo dependency to install on school machines.

A good editing loop is:

1. Open `space_pirate.svg` or `moon_mage.svg` in a text editor, browser, or
   vector editor such as Inkscape.
2. Change one path, color, or group.
3. Save the SVG.
4. From the `rpg` directory run:

   ```bash
   python render_character.py moon_mage
   ```

The SVG uses a `1024 x 1024` `viewBox` and named groups such as `head`,
`helmet`, `torso`, `jetpack`, `plasma-cutlass`, and `pistol-arm`. Keeping those
names is not required by the engine, but it makes the file easier to teach.

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

Keep the root `viewBox="0 0 1024 1024"` unless you also intend to retune the
sprite's `scale=` value in `student_game/art.py`.

`moon_mage.svg` uses the same `1024 x 1024` viewBox and readable group names such as `staff`, `back-cloak`, `legs`, `front-cloak`, and `hood-and-face`.
