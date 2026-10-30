"""Guided lesson 4: compute the area represented by Manim rectangles.

Run from this folder:
    manim -pql lesson_04_area.py AreaLesson

Edit student.left_sum(...). The rectangles work; the estimate starts at 0.
"""

from manim import (
    Axes, BLUE, Create, DecimalNumber, DOWN, FadeIn, LEFT, RIGHT,
    Scene, TEAL, Text, Transform, UP, VGroup,
)

import student


def f(x):
    # Positive curve, so areas of rectangles are nonnegative.
    return 0.5 + 0.2 * x * x


class AreaLesson(Scene):
    def construct(self):
        title = Text("4. Areas from many rectangles", font_size=32).to_edge(UP)
        axes = Axes(
            x_range=[-2.5, 2.5, 1], y_range=[0, 2.2, 0.5],
            x_length=9, y_length=4.8, tips=False,
        ).shift(DOWN * 0.4)
        graph = axes.plot(f, x_range=[-2, 2, 0.04], color=TEAL)
        a, b = -2.0, 2.0

        # Manim draws rectangles, but it is the STUDENT'S responsibility
        # to calculate their total area in student.left_sum().
        def make_rectangles(n):
            return axes.get_riemann_rectangles(
                graph, x_range=[a, b], dx=(b - a) / n,
                input_sample_type="left", color=(BLUE, TEAL),
                fill_opacity=0.55, stroke_width=1,
            )

        n_label = Text("4 rectangles", font_size=23)
        value = DecimalNumber(student.left_sum(f, a, b, 4),
                              num_decimal_places=3, color=BLUE)
        readout = VGroup(Text("Your area:", font_size=23), value, n_label)
        readout.arrange(RIGHT, buff=0.25).to_edge(UP).shift(DOWN * 0.65)

        rectangles = make_rectangles(4)
        self.play(FadeIn(title), Create(axes), Create(graph))
        self.play(FadeIn(rectangles), FadeIn(readout))
        for n in (8, 16):
            next_rectangles = make_rectangles(n)
            next_value = DecimalNumber(student.left_sum(f, a, b, n),
                                       num_decimal_places=3, color=BLUE)
            next_value.move_to(value)
            next_label = Text(f"{n} rectangles", font_size=23).move_to(n_label)
            self.play(Transform(rectangles, next_rectangles),
                      Transform(value, next_value),
                      Transform(n_label, next_label), run_time=1.5)
            self.wait(0.5)
        self.wait(0.5)

        # TODO(student, Manim): try changing input_sample_type to "right".
        # Would your Python summation also need to change to match it?
        # Bonus: experiment with a much larger n (e.g., 32).
