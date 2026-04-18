from __future__ import annotations

"""Apply mathematically motivated signal transforms to sprite surfaces."""

import numpy as np
import pygame


def _normalize_field(field: np.ndarray) -> np.ndarray:
    scale = float(np.percentile(field, 99.5))
    if scale <= 1e-6:
        scale = float(field.max(initial=1.0))
    if scale <= 1e-6:
        return np.zeros_like(field)
    return np.clip(field / scale, 0.0, 1.0)


def _phase_to_rgb(phase: np.ndarray, value: np.ndarray) -> np.ndarray:
    twopi_over_three = 2.0 * np.pi / 3.0
    red = value * (0.5 + 0.5 * np.cos(phase))
    green = value * (0.5 + 0.5 * np.cos(phase - twopi_over_three))
    blue = value * (0.5 + 0.5 * np.cos(phase - 2.0 * twopi_over_three))
    return np.stack((red, green, blue), axis=2)


def _make_surface_from_arrays(rgb: np.ndarray, alpha: np.ndarray) -> pygame.Surface:
    surface = pygame.Surface((rgb.shape[0], rgb.shape[1]), pygame.SRCALPHA)
    rgb_view = pygame.surfarray.pixels3d(surface)
    alpha_view = pygame.surfarray.pixels_alpha(surface)
    rgb_view[:, :, :] = np.clip(rgb * 255.0, 0.0, 255.0).astype(np.uint8)
    alpha_view[:, :] = np.clip(alpha * 255.0, 0.0, 255.0).astype(np.uint8)
    del rgb_view
    del alpha_view
    return surface


def _fourier_visual_surface(signal_rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    frequency = np.fft.fftshift(np.fft.fft2(signal_rgb, axes=(0, 1)), axes=(0, 1))
    magnitude = np.linalg.norm(frequency, axis=2)
    value = _normalize_field(np.log1p(magnitude))
    phase = np.angle(frequency.mean(axis=2))
    visible = np.clip((value - 0.18) / 0.82, 0.0, 1.0)
    alpha = np.clip(visible**0.7, 0.0, 1.0)
    rgb = _phase_to_rgb(phase, np.clip(visible**0.9 * 1.2, 0.0, 1.0))
    return rgb, alpha


def apply_signal_transforms(
    surface: pygame.Surface,
    render_transforms: dict[str, int] | None = None,
) -> pygame.Surface:
    """Return a new surface showing the sprite under its current signal state.

    ``render_transforms`` stores integer phases for transform families. For the
    Fourier transform, phase ``n`` means ``F^n`` applied to the original sprite.
    Since ``F^2`` is a spatial reflection (up to normalization), we can render
    the cycle using one reflection bit and one Fourier-domain bit.
    """

    if not render_transforms:
        return surface

    fourier_phase = int(render_transforms.get("fourier", 0)) % 4
    if fourier_phase == 0:
        return surface

    rgb = pygame.surfarray.array3d(surface).astype(np.float32)
    alpha = pygame.surfarray.array_alpha(surface).astype(np.float32) / 255.0
    signal_rgb = rgb * alpha[:, :, None]

    if fourier_phase & 0b10:
        signal_rgb = signal_rgb[::-1, ::-1, :]
        alpha = alpha[::-1, ::-1]

    if fourier_phase & 0b01:
        transformed_rgb, transformed_alpha = _fourier_visual_surface(signal_rgb)
        return _make_surface_from_arrays(transformed_rgb, transformed_alpha)

    reflected_rgb = np.clip(signal_rgb / 255.0, 0.0, 1.0)
    return _make_surface_from_arrays(reflected_rgb, alpha)
