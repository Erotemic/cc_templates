"""Capstone version 1: the complete Star Crystal adventure.

Runs the full Textual interface when Textual is installed, with a console
fallback for minimal school machines.  Use ``--ui console`` or ``--ui textual``
to choose explicitly.
"""

from engine.game import AdventureGame
from engine.launcher import run_game
from worlds.star_crystal import WORLD_DATA


def make_game(player_name="Tav", *, seed=0):
    return AdventureGame(WORLD_DATA, player_name=player_name, seed=seed)


if __name__ == "__main__":
    run_game(make_game())
