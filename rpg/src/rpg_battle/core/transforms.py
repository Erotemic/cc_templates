from __future__ import annotations

"""Signal-transform metadata shared by rules and rendering.

This keeps transform state declarative so future classroom extensions can add
Laplace, z-transform, or wavelet ideas without hard-coding every rule branch in
multiple places.
"""

from dataclasses import dataclass


TRANSFORM_PREFIX = "transform:"


@dataclass(frozen=True)
class TransformVisualStatus:
    """Describe one sticky badge/status created by a transform state."""

    name: str
    label: str
    color: tuple[int, int, int]


@dataclass(frozen=True)
class SignalTransformSpec:
    """Describe one transform and how repeated applications cycle its state."""

    effect_token: str
    transform_id: str
    cycle_length: int
    state_statuses: dict[int, tuple[str, ...]]
    state_text: dict[int, str]


TRANSFORM_STATUS_INFO: dict[str, TransformVisualStatus] = {
    "fourier_domain": TransformVisualStatus(
        name="fourier_domain",
        label="FFT",
        color=(248, 214, 120),
    ),
    "fourier_reflection": TransformVisualStatus(
        name="fourier_reflection",
        label="Flip",
        color=(170, 220, 255),
    ),
}


SIGNAL_TRANSFORMS: dict[str, SignalTransformSpec] = {
    "transform:fourier": SignalTransformSpec(
        effect_token="transform:fourier",
        transform_id="fourier",
        cycle_length=4,
        state_statuses={
            0: (),
            1: ("fourier_domain",),
            2: ("fourier_reflection",),
            3: ("fourier_domain", "fourier_reflection"),
        },
        state_text={
            0: "returns to ordinary space.",
            1: "shifts into the Fourier domain!",
            2: "returns as a spatial reflection!",
            3: "moves into the reflected Fourier domain!",
        },
    ),
}


def get_transform_spec(effect_token: str) -> SignalTransformSpec | None:
    return SIGNAL_TRANSFORMS.get(effect_token)


def transform_status_names(spec: SignalTransformSpec) -> tuple[str, ...]:
    seen: list[str] = []
    for names in spec.state_statuses.values():
        for name in names:
            if name not in seen:
                seen.append(name)
    return tuple(seen)


def is_transform_status(status_name: str) -> bool:
    return status_name in TRANSFORM_STATUS_INFO
