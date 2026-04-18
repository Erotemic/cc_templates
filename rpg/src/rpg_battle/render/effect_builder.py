from __future__ import annotations

"""Reusable helpers for building attack and spell visuals.

Students should be able to define a new effect in a few readable lines instead of
manually writing point math inside the renderer. The :class:`EffectBuilder`
produces declarative :class:`EffectSpec` objects that the renderer can animate.
"""

from dataclasses import dataclass, replace
from typing import Literal

EffectStyle = Literal["ring", "projectile", "path", "burst_rect", "wind_arcs"]
PathMode = Literal["sine", "square", "stairs", "zigzag", "triangle"]


@dataclass(frozen=True)
class PathProfile:
    """Describe a reusable path shape for a moving visual effect."""

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
        self,
        *,
        color: tuple[int, int, int],
        duration: float = 0.5,
        radius: int = 12,
    ) -> "EffectBuilder":
        self._spec = replace(
            self._spec,
            style="projectile",
            color=color,
            duration=duration,
            projectile_radius=radius,
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
        self,
        *,
        color: tuple[int, int, int],
        duration: float = 0.5,
        arc_count: int = 3,
    ) -> "EffectBuilder":
        self._spec = replace(
            self._spec,
            style="wind_arcs",
            color=color,
            duration=duration,
            arc_count=arc_count,
        )
        return self

    def build(self) -> EffectSpec:
        """Return the final immutable effect specification."""

        return self._spec
