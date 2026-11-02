"""Original portraits and drawing helpers. No images, SVGs or system fonts."""

import math
import pygame

INK = (19, 23, 42)
PAPER = (237, 235, 220)
MINT = (115, 227, 193)
CORAL = (255, 119, 135)
GOLD = (255, 205, 126)
LILAC = (187, 164, 247)
MUTED = (146, 158, 182)


def star(surface, center, radius, color=GOLD, points=4):
    """Draw an alternating-radius star on surface, using pixel center/radius and RGB color."""
    x, y = center
    vertices = []
    for i in range(points * 2):
        angle = i * math.pi / points - math.pi / 2
        r = radius if i % 2 == 0 else radius * 0.35
        vertices.append((x + math.cos(angle) * r, y + math.sin(angle) * r))
    pygame.draw.polygon(surface, color, vertices)


def folio(surface, center, scale, time):
    """Draw Folio's book portrait at center on surface.

    scale multiplies local drawing sizes; time is elapsed seconds for bobbing.
    This shared portrait signature works for world NPCs and larger battle art.
    """
    x, y = center
    y += math.sin(time * 2.2) * 3 * scale

    def polygon(points, color):
        """Scale local book vertices around the bobbing center and draw a filled polygon."""
        pygame.draw.polygon(surface, color, [(x + a * scale, y + b * scale) for a, b in points])

    polygon(
        [(-49, -26), (-8, -33), (0, -25), (8, -33), (49, -26), (45, 32), (0, 38), (-45, 32)],
        (87, 134, 161),
    )
    polygon([(-44, -29), (-7, -34), (0, -26), (0, 29), (-41, 22)], PAPER)
    polygon([(44, -29), (7, -34), (0, -26), (0, 29), (41, 22)], (218, 223, 215))
    pygame.draw.line(
        surface, INK, (x, y - 25 * scale), (x, y + 30 * scale), max(1, round(2 * scale))
    )
    for side in (-1, 1):
        pygame.draw.circle(
            surface,
            INK,
            (round(x + side * 17 * scale), round(y - 4 * scale)),
            max(2, round(4 * scale)),
        )
        for line in range(3):
            pygame.draw.line(
                surface,
                (162, 176, 177),
                (x + side * 8 * scale, y + (9 + line * 5) * scale),
                (x + side * 32 * scale, y + (7 + line * 5) * scale),
                max(1, round(scale)),
            )
    star(surface, (x + 38 * scale, y - 42 * scale), 10 * scale, MINT)


def ferris(surface, center, scale, time):
    """Draw Ferris at pixel center with scale-sized details animated by time in seconds."""
    x, y = center
    y += math.sin(time * 2.8) * 2 * scale
    for side in (-1, 1):
        for row in range(3):
            a = (x + side * 23 * scale, y + (row * 13 - 6) * scale)
            b = (x + side * (43 + math.sin(time * 3 + row) * 3) * scale, y + (row * 13 - 1) * scale)
            pygame.draw.line(surface, GOLD, a, b, max(2, round(4 * scale)))
    body = pygame.Rect(0, 0, 66 * scale, 64 * scale)
    body.center = (x, y + 4 * scale)
    pygame.draw.ellipse(surface, (171, 112, 77), body)
    pygame.draw.ellipse(
        surface, GOLD, body.inflate(-10 * scale, -6 * scale), max(1, round(2 * scale))
    )
    face = pygame.Rect(0, 0, 53 * scale, 30 * scale)
    face.center = (x, y - 13 * scale)
    pygame.draw.rect(surface, INK, face, border_radius=max(1, round(10 * scale)))
    for side in (-1, 1):
        pygame.draw.circle(
            surface,
            MINT,
            (round(x + side * 13 * scale), round(y - 13 * scale)),
            max(2, round(4 * scale)),
        )
    pygame.draw.line(
        surface,
        GOLD,
        (x, y - 31 * scale),
        (x + 8 * scale, y - 48 * scale),
        max(1, round(3 * scale)),
    )
    star(surface, (x + 9 * scale, y - 49 * scale), 6 * scale, CORAL)
    pygame.draw.circle(surface, INK, (round(x), round(y + 20 * scale)), max(2, round(7 * scale)))
    pygame.draw.line(
        surface,
        GOLD,
        (x, y + 20 * scale),
        (x + math.cos(time) * 5 * scale, y + (20 + math.sin(time) * 5) * scale),
        max(1, round(2 * scale)),
    )


def prism(surface, center, scale, time):
    """Draw Prism at pixel center with scale-sized details animated by time in seconds."""
    x, y = center
    y += math.sin(time * 2) * 4 * scale
    points = [(x, y - 52 * scale), (x + 39 * scale, y), (x, y + 45 * scale), (x - 39 * scale, y)]
    pygame.draw.polygon(surface, LILAC, points)
    pygame.draw.polygon(
        surface, (123, 117, 189), [points[0], points[1], points[2], (x - 6 * scale, y)]
    )
    pygame.draw.polygon(surface, PAPER, points, max(1, round(2 * scale)))
    pygame.draw.line(surface, MINT, points[0], (x - 6 * scale, y), max(1, round(2 * scale)))
    for side in (-1, 1):
        pygame.draw.circle(
            surface,
            INK,
            (round(x + side * 12 * scale), round(y - 2 * scale)),
            max(2, round(3 * scale)),
        )
        star(
            surface,
            (x + side * 56 * scale, y + math.sin(time * 2 + side) * 16 * scale),
            7 * scale,
            GOLD,
        )
    pygame.draw.arc(
        surface,
        INK,
        pygame.Rect(x - 8 * scale, y + 2 * scale, 16 * scale, 12 * scale),
        0.2,
        math.pi - 0.2,
        max(1, round(2 * scale)),
    )


def courier(surface, center, time, walking=False, view="down"):
    """Draw the Courier's supplied walking art on surface at pixel center.

    view is 'up', 'down', 'left', or 'right', chosen by the student function.
    walking enables the stride; time is the world walk clock in seconds.
    Draw only: this function does not choose facing or change movement state.
    """
    x, y = center
    stride = math.sin(time * 13) * 3 if walking else 0
    pygame.draw.ellipse(surface, (25, 33, 49), (x - 11, y + 7, 22, 7))
    pygame.draw.line(surface, INK, (x - 4, y + 4), (x - 5 + stride, y + 12), 5)
    pygame.draw.line(surface, INK, (x + 4, y + 4), (x + 5 - stride, y + 12), 5)
    side = view in ("left", "right")
    width = 12 if side else 16
    pygame.draw.rect(surface, MINT, (x - width / 2, y - 5, width, 15), border_radius=5)
    pygame.draw.circle(surface, (242, 204, 164), (round(x), round(y - 11)), 9)
    pygame.draw.arc(surface, CORAL, (x - 11, y - 23, 22, 20), 0, math.pi, 9)
    if view == "up":
        # Back of cap and backpack; no eyes on the back of a head.
        pygame.draw.rect(surface, CORAL, (x - 8, y - 17, 16, 9), border_radius=3)
        pygame.draw.rect(surface, GOLD, (x - 7, y - 3, 14, 13), border_radius=3)
        pygame.draw.line(surface, (164, 125, 65), (x - 4, y + 3), (x + 4, y + 3), 2)
    elif side:
        direction = -1 if view == "left" else 1
        pygame.draw.rect(surface, CORAL, (x - 8 + direction * 4, y - 16, 17, 5), border_radius=2)
        pygame.draw.circle(surface, INK, (round(x + direction * 5), round(y - 10)), 2)
        pygame.draw.rect(surface, GOLD, (x - direction * 10 - 3, y - 3, 6, 12), border_radius=2)
    else:
        pygame.draw.rect(surface, CORAL, (x - 12, y - 16, 24, 5), border_radius=2)
        for offset in (-3, 3):
            pygame.draw.circle(surface, INK, (round(x + offset), round(y - 10)), 2)
        pygame.draw.rect(surface, GOLD, (x - 12, y - 3, 5, 12), border_radius=2)


def soul(surface, center, color=CORAL, radius=8):
    """Draw the player marker at pixel center with an RGB color and radius in pixels."""
    x, y = center
    pygame.draw.polygon(
        surface, color, [(x, y - radius), (x + radius, y), (x, y + radius), (x - radius, y)]
    )
    pygame.draw.circle(
        surface,
        PAPER,
        (round(x - radius * 0.22), round(y - radius * 0.25)),
        max(1, round(radius * 0.18)),
    )
