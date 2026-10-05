"""Frontends for AdventureGame."""

from .console import choose_choice, run_console
from .textual_app import run_textual

__all__ = ["choose_choice", "run_console", "run_textual"]
