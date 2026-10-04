from __future__ import annotations

"""Helpers for classroom-friendly native SVG loading.

We intentionally rely on pygame / SDL_image for SVG support so schools do not
need an extra Cairo-based dependency just to preview vector art.  The teaching
workflow is path-first: students can edit ordinary SVG ``<path>`` elements and
preview the result directly in the game.
"""

import io

import pygame


def load_svg_surface(svg_bytes: bytes, resource_name: str) -> pygame.Surface:
    """Load SVG bytes through pygame's native SVG support."""
    try:
        return pygame.image.load(io.BytesIO(svg_bytes), resource_name)
    except pygame.error as ex:
        raise RuntimeError(
            f'Could not load SVG asset {resource_name!r}. '
            'This project intentionally uses pygame/SDL_image native SVG support '
            'so classrooms do not need an extra Cairo dependency. '
            'If this fails, the local pygame build likely lacks SVG support.'
        ) from ex
