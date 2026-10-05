"""Optional presentation-only ASCII art used by advanced/version3.py."""

from adventure.core import AdventureGame


STAR_CRYSTAL_ART = {
    "village": r"""
       /\        /\
      /  \  /\  /  \
     /____\/__\/____\
       ||  []  ||
    """.strip("\n"),
    "forest": r"""
       &&&   &&&
     &&&&&&&&&&&&
       || /\ ||
       ||/  \||
    """.strip("\n"),
    "lake": r"""
        .-~~~~-.
     .-'        '-.
    ~~~~~~~~~~~~~~~~
    """.strip("\n"),
    "ruins": r"""
      |\        /|
      | \______/ |
      |  _    _  |
      |_| |__| |_|
    """.strip("\n"),
    "tower": r"""
          /\
         /  \
        / /\ \
       /_/  \_\
         ||
        <**>
    """.strip("\n"),
    "ruin_spider": r"""
       \\  |  //
        \\ | //
      ---\|/---
         /o\
      ---/|\---
    """.strip("\n"),
}


def star_crystal_art(game: AdventureGame) -> str | None:
    if game.combat_enemy_key:
        return STAR_CRYSTAL_ART.get(game.combat_enemy_key)
    return STAR_CRYSTAL_ART.get(game.player.location)
