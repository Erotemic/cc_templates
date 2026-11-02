"""Working reference for choosing a walking view; drawing lives in art.py."""


def player_view(facing):
    """Use the dominant axis; ties face vertically. World remembers idle facing."""
    x, y = facing
    if abs(x) > abs(y):
        return "right" if x > 0 else "left"
    return "up" if y < 0 else "down"


# Shared exercise cases, independent of the reference function's implementation.
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
