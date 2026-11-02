"""Editable portraits. Drawing never changes the game rules."""

import math
import pygame


def draw_echo(surface, center, scale, time):
    """An original lantern spirit. Replace this with YOUR character's art."""
    x, y = center
    y += math.sin(time * 2) * 5 * scale
    rect = pygame.Rect(x - 29 * scale, y - 34 * scale, 58 * scale, 65 * scale)
    pygame.draw.rect(surface, (115, 227, 193), rect, border_radius=max(1, round(17 * scale)))
    inside = rect.inflate(-13 * scale, -13 * scale)
    pygame.draw.rect(surface, (26, 52, 59), inside, border_radius=max(1, round(12 * scale)))
    for side in (-1, 1):
        pygame.draw.circle(
            surface,
            (255, 205, 126),
            (round(x + side * 11 * scale), round(y - 3 * scale)),
            max(2, round(4 * scale)),
        )
    pygame.draw.arc(
        surface,
        (237, 235, 220),
        (x - 15 * scale, y - 51 * scale, 30 * scale, 26 * scale),
        0,
        math.pi,
        max(1, round(4 * scale)),
    )
    pygame.draw.line(
        surface,
        (237, 235, 220),
        (x - 9 * scale, y + 13 * scale),
        (x + 9 * scale, y + 13 * scale),
        max(1, round(2 * scale)),
    )
