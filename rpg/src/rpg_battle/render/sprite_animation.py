from __future__ import annotations

"""Small helpers for frame-by-frame character animation.

The student-facing API intentionally keeps frame selection simple. A frame
animation is just a list of still frames plus an FPS value.
"""

from collections.abc import Mapping

SpriteRecipe = Mapping[str, object]


def visual_duration(visual: SpriteRecipe) -> float:
    """Return how long a non-looping visual needs to show every frame once."""

    if visual.get("kind") != "frame_animation":
        return 0.0
    frames = visual.get("frames", ())
    fps = float(visual.get("fps", 1.0))
    if not frames or fps <= 0:
        return 0.0
    return len(frames) / fps


def select_frame(visual: SpriteRecipe, elapsed: float) -> SpriteRecipe:
    """Choose the still frame that should be visible at ``elapsed`` seconds."""

    if visual.get("kind") != "frame_animation":
        return visual

    frames = visual["frames"]
    fps = float(visual["fps"])
    frame_index = max(0, int(elapsed * fps))
    if visual.get("loop", False):
        frame_index %= len(frames)
    else:
        frame_index = min(frame_index, len(frames) - 1)
    return frames[frame_index]


def state_visual(sprite_recipe: SpriteRecipe, state: str) -> SpriteRecipe:
    """Return the visual for a state, falling back to idle when needed."""

    if sprite_recipe.get("kind") != "character_art":
        return sprite_recipe
    states = sprite_recipe["states"]
    return states.get(state, states["idle"])


def state_visual_duration(sprite_recipe: SpriteRecipe, state: str) -> float:
    return visual_duration(state_visual(sprite_recipe, state))
