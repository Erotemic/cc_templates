from __future__ import annotations

"""Minimal scene protocol used by the pygame front end."""


class SceneBase:
    """Base protocol for scenes that can request the game to quit."""

    should_quit: bool = False
