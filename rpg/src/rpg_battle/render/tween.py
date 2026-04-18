from __future__ import annotations

"""Small interpolation helpers shared by battle presentation code."""


def approach(current: float, target: float, speed: float) -> float:
    """Move ``current`` toward ``target`` by at most ``speed`` this step."""

    if current < target:
        return min(target, current + speed)
    return max(target, current - speed)
