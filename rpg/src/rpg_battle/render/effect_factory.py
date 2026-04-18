from __future__ import annotations

"""Runtime visual effects built from declarative effect specifications."""

import math
from dataclasses import dataclass

import pygame

from rpg_battle.content.effects import EFFECTS
from rpg_battle.render.effect_builder import EffectSpec, sample_path_points


@dataclass
class VisualEffect:
    """Animated effect instance traveling between two battlefield points."""

    spec: EffectSpec
    start: tuple[float, float]
    end: tuple[float, float]
    timer: float
    points: list[tuple[float, float]] | None = None

    @property
    def duration(self) -> float:
        return self.spec.duration

    def update(self, dt: float) -> None:
        self.timer -= dt

    def alive(self) -> bool:
        return self.timer > 0

    def draw(self, surface: pygame.Surface) -> None:
        progress = 1.0 - max(0.0, self.timer) / self.duration
        if self.spec.style == "ring":
            cx = self.end[0]
            cy = self.end[1]
            radius = int(
                self.spec.radius_start + (self.spec.radius_end - self.spec.radius_start) * progress
            )
            pygame.draw.circle(surface, self.spec.color, (int(cx), int(cy)), radius, 3)
        elif self.spec.style == "projectile":
            x = self.start[0] + (self.end[0] - self.start[0]) * progress
            y = self.start[1] + (self.end[1] - self.start[1]) * progress
            pygame.draw.circle(
                surface,
                self.spec.color,
                (int(x), int(y)),
                self.spec.projectile_radius,
            )
        elif self.spec.style == "path" and self.points:
            interp = []
            line_width = self.spec.path.width if self.spec.path else 4
            for px, py in self.points:
                x = self.start[0] + (self.end[0] - self.start[0]) * px
                y = self.start[1] + (self.end[1] - self.start[1]) * px + py
                interp.append((int(x), int(y)))
            pygame.draw.lines(surface, self.spec.color, False, interp, line_width)
        elif self.spec.style == "burst_rect":
            x = self.start[0] + (self.end[0] - self.start[0]) * progress
            y = self.start[1] + (self.end[1] - self.start[1]) * progress
            size = int(
                self.spec.size_start + (self.spec.size_end - self.spec.size_start) * progress
            )
            pygame.draw.rect(
                surface,
                self.spec.color,
                pygame.Rect(int(x) - size, int(y) - size, size * 2, size * 2),
                3,
                border_radius=4,
            )
        elif self.spec.style == "wind_arcs":
            for index in range(self.spec.arc_count):
                y = self.start[1] - 24 + index * 22
                pygame.draw.arc(
                    surface,
                    self.spec.color,
                    pygame.Rect(self.start[0] - 30, y - 20, 80, 40),
                    0.3,
                    2.8,
                    3,
                )


def make_effect(
    animation: str,
    start: tuple[float, float],
    end: tuple[float, float],
) -> VisualEffect:
    """Create a runtime effect from the declarative effect catalog."""

    spec = EFFECTS.get(animation)
    if spec is None:
        spec = EffectSpec(effect_id=animation, style="ring")
    points = sample_path_points(spec.path) if spec.path else None
    return VisualEffect(spec=spec, start=start, end=end, timer=spec.duration, points=points)
