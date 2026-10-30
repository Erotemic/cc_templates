"""A small pygame game you can learn by reading and changing."""


def main() -> int:
    """Entry point for ``python -m platformer`` and installed commands."""
    from .game import main as run
    return run()
