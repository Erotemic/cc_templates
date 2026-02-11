# desmos_spec.py
"""
manim -pqh desmos_scene.py DesmosTemplate
"""
WINDOW = dict(
    x_range=(-8, 8, 1),
    y_range=(-5, 5, 1),
)

LINES = [
    "y = 2x + 1",
    "y = sin(x)",
    "x^2 + y^2 = 9",
    "y = (x-2)^2 - 2",
]
