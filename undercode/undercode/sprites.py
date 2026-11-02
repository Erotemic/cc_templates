"""Acceptance examples for the walking-view mission (not an implementation)."""

VIEW_CASES = (
    ((0, 1), "down"),
    ((0, -1), "up"),
    ((-1, 0), "left"),
    ((1, 0), "right"),
    ((-0.8, 0.2), "left"),
    ((0.2, -0.8), "up"),
    ((1, 1), "down"),
    ((0, 0), "down"),
)
