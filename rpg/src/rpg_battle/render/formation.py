from __future__ import annotations

"""Slot-based formation layout for N-vs-M battles."""

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class FormationSlot:
    x: float
    y: float
    scale: float


def formation_slots(region: pygame.Rect, side: str, count: int) -> list[FormationSlot]:
    if count <= 0:
        return []

    depth_values = [0.52] if count == 1 else [index / (count - 1) for index in range(count)]
    slots: list[FormationSlot] = []
    for depth in depth_values:
        y = region.y + region.height * (0.18 + 0.30 * depth)
        if side == "left":
            x = region.x + region.width * (0.28 + 0.24 * depth)
        else:
            x = region.x + region.width * (0.72 - 0.24 * depth)
        scale = 0.82 + depth * 0.16
        if count >= 3:
            scale *= 0.96
        if count >= 4:
            scale *= 0.93
        if count >= 5:
            scale *= 0.90
        slots.append(FormationSlot(x=x, y=y, scale=scale))
    return slots
