from __future__ import annotations

"""Move animations, including graph-shaped math effects."""

import math

from rpg_battle.api import VisualEffect

# Preset effects are short descriptions. The renderer does the animation work.

slash = VisualEffect.path_effect(
    "Slash",
    color=(255, 224, 145),
    mode="zigzag",
    duration=0.3,
    amplitude=8,
    cycles=1,
    steps=8,
    id="slash",
)

impact = VisualEffect.ring(
    "Impact",
    color=(255, 224, 145),
    duration=0.45,
    id="impact",
)

shield = VisualEffect.ring(
    "Shield",
    color=(160, 230, 255),
    duration=0.5,
    id="shield",
)

heal = VisualEffect.ring(
    "Heal",
    color=(120, 245, 170),
    duration=0.55,
    id="heal",
)

# The scene uses a second pulse after HP is restored. It is explicit here so
# presentation behavior is visible rather than relying on a hidden fallback.
heal_pulse = VisualEffect.ring(
    "Heal Pulse",
    color=(255, 255, 255),
    duration=0.5,
    id="heal_pulse",
)

mist = VisualEffect.ring(
    "Mist",
    color=(214, 220, 255),
    duration=0.5,
    id="mist",
)

fractal = VisualEffect.ring(
    "Fractal",
    color=(250, 210, 150),
    duration=0.6,
    id="fractal",
)

regularization = VisualEffect.ring(
    "Regularization",
    color=(198, 210, 255),
    duration=0.55,
    id="regularization",
)

entropy_shield = VisualEffect.ring(
    "Entropy Shield",
    color=(255, 120, 210),
    duration=0.6,
    id="entropy_shield",
)

arc = VisualEffect.projectile(
    "Arc",
    color=(175, 235, 255),
    duration=0.45,
    radius=12,
    id="arc",
)

ember = VisualEffect.projectile(
    "Ember",
    color=(255, 145, 90),
    duration=0.45,
    radius=12,
    id="ember",
)

thorn = VisualEffect.projectile(
    "Thorn",
    color=(135, 210, 120),
    duration=0.5,
    radius=11,
    id="thorn",
)

wind = VisualEffect.wind(
    "Wind",
    color=(215, 240, 255),
    duration=0.55,
    arcs=3,
    id="wind",
)

sine_wave = VisualEffect.path_effect(
    "Sine Wave",
    color=(245, 210, 120),
    mode="sine",
    duration=0.7,
    amplitude=28,
    cycles=4,
    id="sine_wave",
)

fourier_transform = VisualEffect.path_effect(
    "Fourier Transform",
    color=(150, 225, 255),
    mode="sine",
    duration=0.78,
    amplitude=36,
    cycles=6,
    id="fourier_transform",
)

square_pulse = VisualEffect.path_effect(
    "Square Pulse",
    color=(245, 190, 120),
    mode="square",
    duration=0.7,
    amplitude=24,
    cycles=4,
    id="square_pulse",
)

gradient_descent = VisualEffect.path_effect(
    "Gradient Descent",
    color=(194, 255, 138),
    mode="stairs",
    duration=0.7,
    amplitude=34,
    cycles=4.0,
    id="gradient_descent",
)

artifact_burst = VisualEffect.burst_rect(
    "Artifact Burst",
    color=(255, 148, 218),
    duration=0.5,
    size_start=10,
    size_end=18,
    id="artifact_burst",
)

chaos_zigzag = VisualEffect.path_effect(
    "Chaos Zigzag",
    color=(255, 120, 210),
    mode="zigzag",
    duration=0.75,
    amplitude=30,
    cycles=5,
    id="chaos_zigzag",
)

pixel_storm = VisualEffect.burst_rect(
    "Pixel Storm",
    color=(160, 255, 210),
    duration=0.6,
    size_start=12,
    size_end=22,
    id="pixel_storm",
)

# A function can define a path too. x moves from 0.0 at the attacker to 1.0
# at the target, and the return value becomes the vertical offset in pixels.
def classroom_wave(x: float) -> float:
    envelope = 1.0 - 0.45 * x
    return math.sin(x * math.tau * 3) * 30 * envelope

classroom_wave_effect = VisualEffect.path_effect(
    "Classroom Wave",
    color=(255, 230, 120),
    function=classroom_wave,
    steps=60,
    id="classroom_wave",
)

EFFECTS = [
    slash,
    impact,
    shield,
    heal,
    heal_pulse,
    mist,
    fractal,
    regularization,
    entropy_shield,
    arc,
    ember,
    thorn,
    wind,
    sine_wave,
    fourier_transform,
    square_pulse,
    gradient_descent,
    artifact_burst,
    chaos_zigzag,
    pixel_storm,
    classroom_wave_effect,
]
