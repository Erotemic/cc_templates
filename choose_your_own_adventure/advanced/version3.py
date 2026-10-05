"""
Advanced version 3: presentation changes without changing the game rules.

This is still the same Star Crystal world and the same AdventureGame engine.
We pass an optional art function to the console frontend. The art observes
state; it does not decide gameplay outcomes.
"""

from adventure.art import star_crystal_art
from adventure.ui.console import run_console
from adventure.worlds.star_crystal import make_star_crystal_game


def main():
    game = make_star_crystal_game()
    run_console(game, art_provider=star_crystal_art)


if __name__ == "__main__":
    main()
