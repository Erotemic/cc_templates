from rpg_battle.debug import configure_logging
from rpg_battle.game import run_game


def main() -> None:
    """Launch the classroom RPG battle demo."""
    configure_logging()
    run_game()


if __name__ == "__main__":
    main()
