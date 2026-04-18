from __future__ import annotations

"""Visual effect catalog for spell and attack animations.

Students can create a new attack effect by choosing a builder style and tweaking
just a few descriptive numbers such as color, amplitude, or duration.
"""

from rpg_battle.render.effect_builder import EffectBuilder, EffectSpec

EFFECTS: dict[str, EffectSpec] = {}


def add_effect(effect_id: str, spec: EffectSpec) -> None:
    """Register one visual effect spec in a readable incremental style."""

    EFFECTS[effect_id] = spec


add_effect(
    "impact",
    EffectBuilder("impact").ring(color=(255, 224, 145), duration=0.45).build(),
)
add_effect(
    "shield",
    EffectBuilder("shield").ring(color=(160, 230, 255), duration=0.50).build(),
)
add_effect(
    "heal",
    EffectBuilder("heal").ring(color=(120, 245, 170), duration=0.55).build(),
)
add_effect(
    "mist",
    EffectBuilder("mist").ring(color=(214, 220, 255), duration=0.50).build(),
)
add_effect(
    "fractal",
    EffectBuilder("fractal").ring(color=(250, 210, 150), duration=0.60).build(),
)
add_effect(
    "regularization",
    EffectBuilder("regularization").ring(color=(198, 210, 255), duration=0.55).build(),
)
add_effect(
    "entropy_shield",
    EffectBuilder("entropy_shield").ring(color=(255, 120, 210), duration=0.60).build(),
)

add_effect(
    "arc",
    EffectBuilder("arc").projectile(color=(175, 235, 255), duration=0.45, radius=12).build(),
)
add_effect(
    "ember",
    EffectBuilder("ember").projectile(color=(255, 145, 90), duration=0.45, radius=12).build(),
)
add_effect(
    "thorn",
    EffectBuilder("thorn").projectile(color=(135, 210, 120), duration=0.50, radius=11).build(),
)

add_effect(
    "wind",
    EffectBuilder("wind").wind_arcs(color=(215, 240, 255), duration=0.55, arc_count=3).build(),
)

add_effect(
    "sine_wave",
    EffectBuilder("sine_wave")
    .path(color=(245, 210, 120), mode="sine", duration=0.70, amplitude=28, cycles=4)
    .build(),
)
add_effect(
    "square_pulse",
    EffectBuilder("square_pulse")
    .path(color=(245, 190, 120), mode="square", duration=0.70, amplitude=24, cycles=4)
    .build(),
)
add_effect(
    "gradient_descent",
    EffectBuilder("gradient_descent")
    .path(
        color=(194, 255, 138),
        mode="stairs",
        duration=0.70,
        amplitude=34,
        steps=40,
        stair_steps=6,
    )
    .build(),
)
add_effect(
    "artifact_burst",
    EffectBuilder("artifact_burst")
    .burst_rect(color=(255, 148, 218), duration=0.50, size_start=10, size_end=18)
    .build(),
)
add_effect(
    "chaos_zigzag",
    EffectBuilder("chaos_zigzag")
    .path(color=(255, 120, 210), mode="zigzag", duration=0.75, amplitude=30, cycles=5)
    .build(),
)
add_effect(
    "pixel_storm",
    EffectBuilder("pixel_storm")
    .burst_rect(color=(160, 255, 210), duration=0.60, size_start=12, size_end=22)
    .build(),
)
