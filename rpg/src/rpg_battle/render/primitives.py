from __future__ import annotations

import pygame


def _resolve_color(recipe, palette, key, fallback=(255, 255, 255)):
    if key is None:
        return None
    if isinstance(key, tuple):
        return key
    return palette.get(key, fallback)


def _transform_point(point, center, scale, facing=1, offset=(0, 0)):
    x = center[0] + (point[0] * scale * facing) + offset[0]
    y = center[1] + (point[1] * scale) + offset[1]
    return int(x), int(y)


def draw_shape(
    surface: pygame.Surface,
    shape: dict,
    center: tuple[float, float],
    scale: float,
    palette: dict,
    facing: int = 1,
    offset: tuple[float, float] = (0, 0),
) -> None:
    kind = shape["kind"]
    fill = _resolve_color(shape, palette, shape.get("fill"))
    outline = _resolve_color(shape, palette, shape.get("outline"), (0, 0, 0))
    width = shape.get("width", 0)
    if kind == "circle":
        c = _transform_point(shape["center"], center, scale, facing, offset)
        radius = max(1, int(shape["radius"] * scale))
        pygame.draw.circle(surface, fill, c, radius)
        if outline and width:
            pygame.draw.circle(surface, outline, c, radius, width)
    elif kind == "ellipse":
        c = _transform_point(shape["center"], center, scale, facing, offset)
        w, h = shape["size"]
        rect = pygame.Rect(0, 0, int(w * scale), int(h * scale))
        rect.center = c
        pygame.draw.ellipse(surface, fill, rect)
        if outline and width:
            pygame.draw.ellipse(surface, outline, rect, width)
    elif kind == "rect":
        c = _transform_point(shape["center"], center, scale, facing, offset)
        w, h = shape["size"]
        rect = pygame.Rect(0, 0, int(w * scale), int(h * scale))
        rect.center = c
        border_radius = int(shape.get("border_radius", 0) * scale)
        pygame.draw.rect(surface, fill, rect, border_radius=border_radius)
        if outline and width:
            pygame.draw.rect(surface, outline, rect, width, border_radius=border_radius)
    elif kind in {"polygon", "polyline", "line"}:
        points = [_transform_point(p, center, scale, facing, offset) for p in shape["points"]]
        color = _resolve_color(
            shape, palette, shape.get("color", shape.get("fill", "detail")), (255, 255, 255)
        )
        if kind == "polygon":
            pygame.draw.polygon(surface, fill, points)
            if outline and width:
                pygame.draw.polygon(surface, outline, points, width)
        elif kind == "polyline":
            pygame.draw.lines(surface, color, False, points, width)
        else:
            pygame.draw.lines(surface, color, False, points, width)
