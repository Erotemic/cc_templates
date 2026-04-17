from __future__ import annotations

import pygame

from rpg_battle.settings import PANEL_ALT, PANEL_COLOR


def panel(surface: pygame.Surface, rect: pygame.Rect, alt: bool = False) -> None:
    pygame.draw.rect(surface, PANEL_ALT if alt else PANEL_COLOR, rect, border_radius=16)
    pygame.draw.rect(surface, (215, 220, 240), rect, 2, border_radius=16)
