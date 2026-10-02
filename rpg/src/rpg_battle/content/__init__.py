"""Compatibility views of the student-authored ``student_game`` package.

New classroom work should happen in the top-level ``student_game/`` directory.  These
names keep older engine tests, examples, and installed entry points working.
"""

from student_game import CONTENT as DEFAULT_CONTENT

__all__ = ["DEFAULT_CONTENT"]
