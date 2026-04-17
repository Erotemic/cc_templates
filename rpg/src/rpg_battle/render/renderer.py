from __future__ import annotations

import pygame

from rpg_battle.render.ui_panels import panel
from rpg_battle.settings import BG_COLOR


def draw_background(surface: pygame.Surface) -> None:
    surface.fill(BG_COLOR)
    ground = pygame.Rect(0, surface.get_height() - 180, surface.get_width(), 180)
    pygame.draw.rect(surface, (26, 44, 36), ground)
    pygame.draw.circle(surface, (34, 48, 64), (180, 120), 90)
    pygame.draw.circle(surface, (42, 58, 80), (surface.get_width() - 180, 100), 110)


def draw_frame(surface: pygame.Surface, menu_rect: pygame.Rect, log_rect: pygame.Rect) -> None:
    panel(surface, menu_rect)
    panel(surface, log_rect, alt=True)
