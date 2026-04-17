from __future__ import annotations


def approach(current: float, target: float, speed: float) -> float:
    if current < target:
        return min(target, current + speed)
    return max(target, current - speed)
