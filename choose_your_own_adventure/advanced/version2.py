"""
Advanced version 2: a second frontend, with NO second game engine.

This launches the Star Crystal game through Textual. Compare this tiny file to version1.py: only the frontend changes.

The Textual code in adventure/ui/textual_app.py calls the exact same:

    game.describe()
    game.choices()
    game.apply(action)

There are no worker threads, redirected stdout, monkey-patched input(), or
message queues because the game core was designed not to perform terminal I/O.
"""

from adventure.ui.textual_app import run_textual
from adventure.worlds.star_crystal import make_star_crystal_game


def main():
    game = make_star_crystal_game()
    run_textual(game)


if __name__ == "__main__":
    main()
