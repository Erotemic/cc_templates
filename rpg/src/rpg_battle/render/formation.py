from __future__ import annotations

"""Slot-based formation layout for N-vs-M battles.

The key goal is readability, not geometric purity.  We use a few hand-tuned
formation presets for the common party sizes used in the classroom project, and
fall back to a gentle diagonal spread for larger counts.
"""

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class FormationSlot:
    """Concrete anchor point for a battler sprite and its overlays."""

    x: float
    y: float
    scale: float


# Relative coordinates within a formation region.
_LEFT_PRESETS: dict[int, list[tuple[float, float, float]]] = {
    1: [(0.34, 0.58, 0.92)],
    2: [
        (0.24, 0.44, 0.82),
        (0.43, 0.74, 0.98),
    ],
    3: [
        (0.16, 0.34, 0.76),
        (0.33, 0.57, 0.88),
        (0.52, 0.82, 1.00),
    ],
    4: [
        (0.12, 0.28, 0.72),
        (0.26, 0.48, 0.82),
        (0.40, 0.68, 0.92),
        (0.56, 0.86, 1.00),
    ],
}


def _mirror(preset: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    return [(1.0 - x, y, scale) for x, y, scale in preset]


_RIGHT_PRESETS = {count: _mirror(slots) for count, slots in _LEFT_PRESETS.items()}


def _fallback_slots(side: str, count: int) -> list[tuple[float, float, float]]:
    """Return a readable diagonal spread for larger party sizes."""

    if count <= 0:
        return []
    if count == 1:
        return _LEFT_PRESETS[1] if side == "left" else _RIGHT_PRESETS[1]

    slots: list[tuple[float, float, float]] = []
    for index in range(count):
        depth = index / max(1, count - 1)
        x = 0.10 + 0.48 * depth
        if side == "right":
            x = 1.0 - x
        y = 0.24 + 0.64 * depth
        scale = 0.68 + 0.28 * depth
        if count >= 5:
            scale *= 0.92
        if count >= 6:
            scale *= 0.90
        slots.append((x, y, scale))
    return slots


def formation_slots(region: pygame.Rect, side: str, count: int) -> list[FormationSlot]:
    """Return battler anchors inside ``region`` for one team's active slots."""

    if count <= 0:
        return []

    presets = _LEFT_PRESETS if side == "left" else _RIGHT_PRESETS
    rel_slots = presets.get(count) or _fallback_slots(side, count)
    slots: list[FormationSlot] = []
    for rel_x, rel_y, scale in rel_slots:
        slots.append(
            FormationSlot(
                x=region.x + region.width * rel_x,
                y=region.y + region.height * rel_y,
                scale=scale,
            )
        )
    return slots
