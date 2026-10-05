"""
Advanced version 4: a different world using the same engine.

This is the payoff for the architecture introduced in intermediate/version3.py
and advanced/version1.py. Dust Vault has different rooms, quest logic, items,
and an enemy, but it reuses
``adventure/core.py`` and ``adventure/ui/console.py`` unchanged.

To build your own larger adventure, copy a WORLD module like
``adventure/worlds/dust_vault.py`` rather than copying the engine.
"""

from adventure.ui.console import run_console
from adventure.worlds.dust_vault import make_dust_vault_game


def main():
    game = make_dust_vault_game()
    run_console(game)


if __name__ == "__main__":
    main()
