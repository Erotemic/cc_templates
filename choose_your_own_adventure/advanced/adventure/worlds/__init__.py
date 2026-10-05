"""Example worlds that share the same AdventureGame engine."""

from .dust_vault import make_dust_vault_game
from .star_crystal import make_star_crystal_game

__all__ = ["make_dust_vault_game", "make_star_crystal_game"]
