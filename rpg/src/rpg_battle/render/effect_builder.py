from __future__ import annotations

"""Reusable helpers for building attack and spell visuals.

This module keeps the effect math teachable by separating two jobs:
- content files say *what* an effect should look like
- this module explains *how* the graph/path math is sampled

For path-style effects, we treat the path as a graph on the unit interval. The
renderer later stretches that normalized graph between battlefield points.
"""

from dataclasses import dataclass, replace
import math
from typing import Literal

EffectStyle = Literal["ring", "projectile", "path", "burst_rect", "wind_arcs"]
PathMode = Literal["sine", "square", "stairs", "zigzag", "triangle"]


@dataclass(frozen=True)
class PathProfile:
    """Describe a graph-like path for a moving visual effect.

    ``x`` runs from 0 to 1, and the sampled ``y`` value becomes a vertical pixel
    offset. The runtime stretches the normalized ``x`` positions across the
    distance from the source to the target.
    """

    mode: PathMode
    amplitude: float = 24.0
    cycles: float = 4.0
    steps: int = 40
    width: int = 4
    stair_steps: int = 6


@dataclass(frozen=True)
class EffectSpec:
    """Declarative specification for one visual effect animation."""

    effect_id: str
    style: EffectStyle
    color: tuple[int, int, int] = (255, 255, 255)
    duration: float = 0.5
    path: PathProfile | None = None
    radius_start: int = 18
    radius_end: int = 60
    projectile_radius: int = 12
    size_start: int = 10
    size_end: int = 18
    arc_count: int = 3


class EffectBuilder:
    """Build a visual-effect specification with short, readable calls."""

    def __init__(self, effect_id: str) -> None:
        self._spec = EffectSpec(effect_id=effect_id, style="ring")

    def ring(
        self,
        *,
        color: tuple[int, int, int],
        duration: float = 0.5,
        radius_start: int = 18,
        radius_end: int = 60,
    ) -> "EffectBuilder":
        self._spec = replace(
            self._spec,
            style="ring",
            color=color,
            duration=duration,
            radius_start=radius_start,
            radius_end=radius_end,
        )
        return self

    def projectile(
        self, *, color: tuple[int, int, int], duration: float = 0.5, radius: int = 12
    ) -> "EffectBuilder":
        self._spec = replace(
            self._spec, style="projectile", color=color, duration=duration, projectile_radius=radius
        )
        return self

    def path(
        self,
        *,
        color: tuple[int, int, int],
        mode: PathMode,
        duration: float = 0.7,
        amplitude: float = 24.0,
        cycles: float = 4.0,
        steps: int = 40,
        width: int = 4,
        stair_steps: int = 6,
    ) -> "EffectBuilder":
        self._spec = replace(
            self._spec,
            style="path",
            color=color,
            duration=duration,
            path=PathProfile(
                mode=mode,
                amplitude=amplitude,
                cycles=cycles,
                steps=steps,
                width=width,
                stair_steps=stair_steps,
            ),
        )
        return self

    def burst_rect(
        self,
        *,
        color: tuple[int, int, int],
        duration: float = 0.5,
        size_start: int = 10,
        size_end: int = 18,
    ) -> "EffectBuilder":
        self._spec = replace(
            self._spec,
            style="burst_rect",
            color=color,
            duration=duration,
            size_start=size_start,
            size_end=size_end,
        )
        return self

    def wind_arcs(
        self, *, color: tuple[int, int, int], duration: float = 0.55, arc_count: int = 3
    ) -> "EffectBuilder":
        self._spec = replace(
            self._spec, style="wind_arcs", color=color, duration=duration, arc_count=arc_count
        )
        return self

    def build(self) -> EffectSpec:
        return self._spec


def evaluate_path_y(profile: PathProfile, x: float) -> float:
    """Return the vertical offset for a normalized x position.

    The formulas intentionally line up with common graph ideas:
    - sine: smooth sine wave
    - square: two-level square wave
    - stairs: descending step function
    - zigzag/triangle: triangle wave
    """

    if profile.mode == "sine":
        return math.sin(x * math.pi * profile.cycles) * profile.amplitude
    if profile.mode == "square":
        sign = 1.0 if math.sin(x * math.pi * profile.cycles) >= 0 else -1.0
        return sign * profile.amplitude
    if profile.mode == "stairs":
        step_index = int(x * profile.stair_steps)
        step_size = (profile.amplitude * 2.0) / max(1, profile.stair_steps)
        return profile.amplitude - step_index * step_size
    phase = (x * profile.cycles) % 1.0
    return (4.0 * abs(phase - 0.5) - 1.0) * profile.amplitude


def sample_path_points(profile: PathProfile) -> list[tuple[float, float]]:
    """Sample a profile into normalized ``(x, y)`` points."""

    denominator = max(1, profile.steps - 1)
    return [
        (index / denominator, evaluate_path_y(profile, index / denominator))
        for index in range(profile.steps)
    ]
