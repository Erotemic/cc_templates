from __future__ import annotations

"""Supporting art and audio for the small classroom workshop.

Students can ignore this module while learning control flow. When they want to
customize presentation, this is the next place to explore.
"""

from rpg_battle.api import CodeSpriteFrame, Music, Palette, Sound, VisualEffect

workshop_palette = Palette(
    "Workshop Colors",
    id="workshop_colors",
    body=(90, 165, 245),
    accent=(255, 215, 95),
    detail=(28, 40, 70),
)

workshop_frame = CodeSpriteFrame(
    "Workshop Hero Sprite",
    id="workshop_hero_frame",
    palette=workshop_palette,
)
workshop_frame.circle((0, 5), 38, fill="body")
workshop_frame.polygon([(-28, -18), (0, -55), (28, -18)], fill="accent")
workshop_frame.face(-3)

workshop_impact = VisualEffect.ring(
    "Workshop Impact",
    id="workshop_impact",
    color=(255, 220, 105),
    duration=0.42,
)

workshop_hit = Sound(
    "Workshop Hit",
    id="workshop_hit",
    waveform="triangle",
    frequency=240.0,
    frequency_end=150.0,
    duration=0.11,
    volume=0.24,
)

workshop_theme = Music.generated(
    "Workshop Theme",
    id="workshop_theme",
    builder="battle_loop_prototype",
    volume=0.30,
)

PALETTES = [workshop_palette]
ART_ASSETS = [workshop_frame]

# Compatibility names used by older exercises.
workshop_sprite = workshop_frame
SPRITE_ASSETS = ART_ASSETS
SPRITES = ART_ASSETS
EFFECTS = [workshop_impact]
SOUNDS = [workshop_hit]
MUSIC = [workshop_theme]
