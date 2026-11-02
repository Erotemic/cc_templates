# Blank pygame starter

Want to make a game from almost nothing? This is the smallest starting point in
`cc_templates`. It's deliberately **not a complete game**.

```bash
cd blank_game
python main.py
```

Requires Python and an existing `pygame` / `pygame-ce` installation. If pygame
is missing and installing packages is allowed, use `python -m pip install pygame-ce`.
No other packages, assets, sound files, or build steps are needed.

The menu offers **three optional starting styles**:

- **1 — Real time:** a circle moves while an arrow or WASD key is held down.
- **2 — Turn based:** a square takes one grid step per key press.
- **3 — Choices / state:** pressing 1 or 2 changes a remembered state.

Press **Esc** to return to the menu, **R** to restart an example, or **Esc**
from the menu to quit. The window can be resized.

None of the examples has a score, objective, health, enemies, or levels. Add
whatever makes sense for *your* game—or delete the examples and build something
entirely different. You are not expected to finish or even use every mode.

## Where to begin

Everything is in **`main.py`**. Read it from top to bottom:

- `new_game()`: your game's memory (position, turns, current scene, etc.).
- `on_key_down()`: things that happen once, when a key is pressed.
- `update()`: things that happen every frame, using elapsed seconds.
- `draw()`: what appears on the screen.
- `main()`: the pygame window and `events -> update -> draw` loop.

The `# IDEA:` comments give optional directions without prescribing a project.
You can start by changing the window title, background color, shapes, or text.
If you know what you want to build already, delete the parts you don't need.

To check that the basic scaffold still runs:

```bash
python -m unittest discover -s tests -v
```

The tests are for the *starting examples*, not requirements for your final game.
When you replace an example, you can replace its test too.
