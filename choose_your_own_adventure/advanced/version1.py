"""
Advanced version 1: split the richer game into reusable modules.

Intermediate version 3 proved the architecture in one file. This version keeps
the same public shape but moves responsibilities into small modules:

    adventure/core.py                 reusable game mechanics
    adventure/worlds/star_crystal.py  rooms, quest logic, story
    adventure/ui/console.py           terminal input/output

The point is not "more files are better". The point is that each file now has
one reason to change, and advanced/version4.py can build a different world without
copying the engine.
"""

from adventure.ui.console import run_console
from adventure.worlds.star_crystal import make_star_crystal_game


def main():
    game = make_star_crystal_game()
    run_console(game)


if __name__ == "__main__":
    main()
