"""Guided lesson 5: calculate a 2D matrix transform, then animate it.

Run from this folder:
    manim -pql lesson_05_matrix.py MatrixLesson

Edit student.transform_xy(...). Initially the transformation is identity.
"""

from manim import (
    BLUE, Create, DOWN, FadeIn, GRAY, NumberPlane, Polygon,
    Scene, Text, Transform, UP, YELLOW,
)

import student


# A quarter-turn counterclockwise, encoded as a 2-by-2 matrix.
# The student applies this to EACH corner of the triangle.
MATRIX = ((0.0, -1.0), (1.0, 0.0))
CORNERS = ((-1.0, -0.75), (1.0, -0.75), (0.4, 1.3))


class MatrixLesson(Scene):
    def construct(self):
        title = Text("5. Matrices move every point", font_size=32).to_edge(UP)
        plane = NumberPlane(
            x_range=[-3.5, 3.5, 1], y_range=[-2.5, 2.5, 1],
            x_length=8, y_length=5, tips=False,
        ).shift(DOWN * 0.35)
        original = Polygon(*[plane.c2p(x, y) for x, y in CORNERS],
                           color=BLUE, fill_opacity=0.5)
        transformed = Polygon(*[
            plane.c2p(*student.transform_xy(x, y, MATRIX))
            for x, y in CORNERS
        ], color=YELLOW, fill_opacity=0.5)

        # The faint outline remembers the original position.
        outline = original.copy().set_stroke(color=GRAY, width=2)
        outline.set_fill(opacity=0)
        matrix_label = Text("Matrix: [[0, -1], [1, 0]]", font_size=23)
        matrix_label.to_edge(UP).shift(DOWN * 0.65)
        self.play(FadeIn(title), Create(plane))
        self.play(Create(original), FadeIn(outline), FadeIn(matrix_label))
        self.play(Transform(original, transformed), run_time=3)
        self.wait(0.7)

        # TODO(student, Manim): change MATRIX and update matrix_label.
        # Try ((2, 0), (0, 1)) for horizontal scaling or
        # ((1, 1), (0, 1)) for a shear. Predict the new triangle first.
