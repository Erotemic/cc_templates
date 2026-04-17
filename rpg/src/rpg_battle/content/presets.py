from __future__ import annotations

"""Helper constructors for declarative procedural sprite recipes."""


def circle(center, radius, fill="body", outline="detail", width=2):
    """Return a circle shape definition."""
    return {
        "kind": "circle",
        "center": center,
        "radius": radius,
        "fill": fill,
        "outline": outline,
        "width": width,
    }


def ellipse(center, size, fill="body", outline="detail", width=2):
    """Return an ellipse shape definition."""
    return {
        "kind": "ellipse",
        "center": center,
        "size": size,
        "fill": fill,
        "outline": outline,
        "width": width,
    }


def rect(center, size, fill="accent", outline="detail", width=2, border_radius=10):
    """Return a rounded rectangle shape definition."""
    return {
        "kind": "rect",
        "center": center,
        "size": size,
        "fill": fill,
        "outline": outline,
        "width": width,
        "border_radius": border_radius,
    }


def polygon(points, fill="accent", outline="detail", width=2):
    """Return a filled polygon shape definition."""
    return {
        "kind": "polygon",
        "points": points,
        "fill": fill,
        "outline": outline,
        "width": width,
    }


def line(points, color="detail", width=3):
    """Return a line shape definition."""
    return {"kind": "line", "points": points, "color": color, "width": width}


def polyline(points, color="accent", width=3):
    """Return a polyline shape definition."""
    return {"kind": "polyline", "points": points, "color": color, "width": width}


def simple_face(y=-6):
    """Return a friendly default face offset by ``y`` pixels."""
    return [
        circle(center=(-12, y), radius=6, fill="eye", outline="detail", width=1),
        circle(center=(12, y), radius=6, fill="eye", outline="detail", width=1),
        line(points=[(-12, y), (-12, y + 2)], color="detail", width=2),
        line(points=[(12, y), (12, y + 2)], color="detail", width=2),
        polyline(
            points=[(-12, y + 16), (0, y + 22), (12, y + 16)],
            color="detail",
            width=2,
        ),
    ]
