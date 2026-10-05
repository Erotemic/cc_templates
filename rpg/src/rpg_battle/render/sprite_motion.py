from __future__ import annotations

"""Whole-character motion used by battle presentation.

These motions are intentionally independent of the artwork. A student can draw
one completely still frame and still get a bob, lunge, shake, and knockout
motion because the engine moves the whole picture around.
"""

from collections.abc import Mapping
from dataclasses import dataclass
import math

MotionRecipe = Mapping[str, object]
MotionSet = Mapping[str, MotionRecipe]


@dataclass(frozen=True)
class MotionTransform:
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    show_x_eyes: bool = False


def motion_duration(motion: MotionRecipe) -> float:
    """Return the finite duration of a motion, or 0 for looping idle motion."""

    if motion.get("kind") == "bob":
        return 0.0
    return max(0.0, float(motion.get("duration", 0.0)))


def evaluate_motion(motion: MotionRecipe, elapsed: float, side: str) -> MotionTransform:
    kind = motion.get("kind")

    if kind == "bob":
        period = float(motion["period"])
        height = float(motion["height"])
        phase = elapsed * math.tau / period
        return MotionTransform(y=math.sin(phase) * height)

    duration = max(1e-9, float(motion.get("duration", 1.0)))
    progress = min(1.0, max(0.0, elapsed / duration))

    if kind == "lunge":
        direction = 1.0 if side == "left" else -1.0
        distance = float(motion["distance"])
        return MotionTransform(x=direction * distance * math.sin(progress * math.pi))

    if kind == "shake":
        distance = float(motion["distance"])
        cycles = float(motion["cycles"])
        return MotionTransform(x=distance * math.sin(progress * math.tau * cycles))

    if kind == "fall":
        distance = float(motion["distance"])
        rotation = float(motion["rotation"])
        rotation_duration = max(1e-9, float(motion["rotation_duration"]))
        rotation_progress = min(1.0, max(0.0, elapsed / rotation_duration))
        return MotionTransform(
            y=distance * progress,
            rotation=rotation * rotation_progress,
            show_x_eyes=bool(motion.get("show_x_eyes", True)),
        )

    raise ValueError(f"Unknown sprite motion kind {kind!r}")


def evaluate_character_motion(
    motions: MotionSet,
    *,
    state: str,
    idle_elapsed: float,
    state_elapsed: float,
    side: str,
) -> MotionTransform:
    """Evaluate default idle motion plus the current action motion.

    Attack and hurt keep the normal idle bob and layer their horizontal motion
    on top. Faint replaces the idle motion so the character can fall away.
    """

    if state == "faint":
        return evaluate_motion(motions["faint"], state_elapsed, side)

    idle = evaluate_motion(motions["idle"], idle_elapsed, side)
    if state == "idle":
        return idle

    action = evaluate_motion(motions[state], state_elapsed, side)
    return MotionTransform(
        x=idle.x + action.x,
        y=idle.y + action.y,
        rotation=idle.rotation + action.rotation,
        show_x_eyes=idle.show_x_eyes or action.show_x_eyes,
    )
