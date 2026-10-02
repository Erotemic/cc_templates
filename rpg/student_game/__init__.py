"""The student-authored RPG. Start in ``workshop.py`` when changing the game."""

from rpg_battle.catalog import set_default_content
from student_game.catalog import CONTENT, GAME
from student_game.scenarios import SCENARIOS

set_default_content(CONTENT)

__all__ = ["CONTENT", "GAME", "SCENARIOS"]
