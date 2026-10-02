"""The student-authored RPG. Start here when you want to change the game."""

from rpg_battle.catalog import set_default_content
from student_game.catalog import CONTENT, GAME

set_default_content(CONTENT)

__all__ = ["CONTENT", "GAME"]
