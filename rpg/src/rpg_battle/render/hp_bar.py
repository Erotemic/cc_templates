from __future__ import annotations

import pygame

from rpg_battle.render.tween import approach


class HPBar:
    def __init__(self, start_ratio: float = 1.0) -> None:
        self.display_ratio = start_ratio
        self.target_ratio = start_ratio

    def set_target(self, target_ratio: float) -> None:
        self.target_ratio = max(0.0, min(1.0, target_ratio))

    def snap(self, target_ratio: float) -> None:
        self.set_target(target_ratio)
        self.display_ratio = self.target_ratio

    def update(self, dt: float) -> None:
        self.display_ratio = approach(self.display_ratio, self.target_ratio, dt * 0.9)

    def draw(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, (28, 30, 40), rect, border_radius=8)
        inner = rect.inflate(-4, -4)
        fill = inner.copy()
        fill.width = max(0, int(inner.width * self.display_ratio))
        color = (
            (110, 220, 120)
            if self.display_ratio > 0.45
            else (240, 180, 80)
            if self.display_ratio > 0.2
            else (230, 90, 90)
        )
        pygame.draw.rect(surface, color, fill, border_radius=6)
        pygame.draw.rect(surface, (215, 220, 240), rect, 2, border_radius=8)
