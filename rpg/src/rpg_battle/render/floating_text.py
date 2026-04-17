from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass
class FloatingText:
    text: str
    pos: list[float]
    color: tuple[int, int, int]
    timer: float = 0.9

    def update(self, dt: float) -> None:
        self.timer -= dt
        self.pos[1] -= 32 * dt

    def alive(self) -> bool:
        return self.timer > 0

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        alpha = max(0, min(255, int(255 * min(1.0, self.timer / 0.9))))
        text = font.render(self.text, True, self.color)
        text.set_alpha(alpha)
        rect = text.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        surface.blit(text, rect)
