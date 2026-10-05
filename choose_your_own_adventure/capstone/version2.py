"""Capstone version 2: the complete Dust Vault adventure."""

from engine.console import run_console
from engine.game import AdventureGame
from worlds.dust_vault import WORLD_DATA


def make_game(player_name="Tav", *, seed=0):
    return AdventureGame(WORLD_DATA, player_name=player_name, seed=seed)


if __name__ == "__main__":
    run_console(make_game())
