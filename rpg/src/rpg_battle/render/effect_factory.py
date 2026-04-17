from __future__ import annotations

import math
from dataclasses import dataclass

import pygame


@dataclass
class VisualEffect:
    kind: str
    start: tuple[float, float]
    end: tuple[float, float]
    color: tuple[int, int, int]
    duration: float
    timer: float
    points: list[tuple[float, float]] | None = None

    def update(self, dt: float) -> None:
        self.timer -= dt

    def alive(self) -> bool:
        return self.timer > 0

    def draw(self, surface: pygame.Surface) -> None:
        progress = 1.0 - max(0.0, self.timer) / self.duration
        if self.kind in {"impact", "shield", "heal_pulse", "mist", "fractal", "regularization"}:
            cx = self.end[0]
            cy = self.end[1]
            radius = 18 + int(42 * progress)
            pygame.draw.circle(surface, self.color, (int(cx), int(cy)), radius, 3)
        elif self.kind in {"bolt", "ember", "vine"}:
            x = self.start[0] + (self.end[0] - self.start[0]) * progress
            y = self.start[1] + (self.end[1] - self.start[1]) * progress
            pygame.draw.circle(surface, self.color, (int(x), int(y)), 12)
        elif self.kind in {"sine_wave", "square_pulse", "gradient_descent"} and self.points:
            interp = []
            for px, py in self.points:
                x = self.start[0] + (self.end[0] - self.start[0]) * px
                y = self.start[1] + (self.end[1] - self.start[1]) * px + py
                interp.append((int(x), int(y)))
            pygame.draw.lines(surface, self.color, False, interp, 4)
        elif self.kind == "artifact_burst":
            x = self.start[0] + (self.end[0] - self.start[0]) * progress
            y = self.start[1] + (self.end[1] - self.start[1]) * progress
            size = 10 + int(8 * progress)
            pygame.draw.rect(
                surface,
                self.color,
                pygame.Rect(int(x) - size, int(y) - size, size * 2, size * 2),
                3,
                border_radius=4,
            )
        elif self.kind == "wind":
            for i in range(3):
                y = self.start[1] - 24 + i * 22
                pygame.draw.arc(
                    surface,
                    self.color,
                    pygame.Rect(self.start[0] - 30, y - 20, 80, 40),
                    0.3,
                    2.8,
                    3,
                )


def _wave_points(mode: str) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for i in range(40):
        x = i / 39
        if mode == "sine_wave":
            y = math.sin(x * math.pi * 4) * 28
        elif mode == "gradient_descent":
            step = int(x * 6)
            y = 34 - step * 11
        else:
            y = (1 if math.sin(x * math.pi * 4) >= 0 else -1) * 24
        pts.append((x, y))
    return pts


def make_effect(
    animation: str, start: tuple[float, float], end: tuple[float, float]
) -> VisualEffect:
    color_map = {
        "impact": (255, 224, 145),
        "shield": (160, 230, 255),
        "heal_pulse": (120, 245, 170),
        "mist": (214, 220, 255),
        "fractal": (250, 210, 150),
        "bolt": (175, 235, 255),
        "ember": (255, 145, 90),
        "vine": (135, 210, 120),
        "wind": (215, 240, 255),
        "sine_wave": (245, 210, 120),
        "square_pulse": (245, 190, 120),
        "gradient_descent": (194, 255, 138),
        "regularization": (198, 210, 255),
        "artifact_burst": (255, 148, 218),
    }
    duration = 0.5 if animation not in {"sine_wave", "square_pulse", "gradient_descent"} else 0.7
    points = (
        _wave_points(animation)
        if animation in {"sine_wave", "square_pulse", "gradient_descent"}
        else None
    )
    return VisualEffect(
        animation, start, end, color_map.get(animation, (255, 255, 255)), duration, duration, points
    )
