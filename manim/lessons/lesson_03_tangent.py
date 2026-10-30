"""Guided lesson 3: make a secant-slope estimate match a moving secant.

Run from this folder:
    manim -pql lesson_03_tangent.py TangentLesson

Edit student.secant_slope(function, x, dx). The blue line starts flat.
"""

from manim import (
    Axes, BLUE, Create, DecimalNumber, Dot, DOWN, FadeIn, LEFT, Line,
    RIGHT, Scene, Text, UP, ValueTracker, VGroup, YELLOW,
    always_redraw, linear,
)

import student


def f(x):
    # A parabola: at x=0.5, the tangent slope is 2*x = 1.
    return x * x + 0.5


class TangentLesson(Scene):
    def construct(self):
        title = Text("3. Slope from two nearby points", font_size=32).to_edge(UP)
        axes = Axes(
            x_range=[-2, 2.5, 1], y_range=[0, 5, 1],
            x_length=8, y_length=4.8, tips=False,
        ).shift(DOWN * 0.3)
        graph = axes.plot(f, x_range=[-2, 2.0, 0.05], color=BLUE)
        x = 0.5
        dx = ValueTracker(1.2)

        fixed_dot = Dot(axes.c2p(x, f(x)), color=YELLOW)
        moving_dot = always_redraw(lambda: Dot(
            axes.c2p(x + dx.get_value(), f(x + dx.get_value())),
            color=YELLOW,
        ))
        # Yellow line joins the actual two points on the parabola.
        secant = always_redraw(lambda: Line(
            axes.c2p(x, f(x)),
            axes.c2p(x + dx.get_value(), f(x + dx.get_value())),
            color=YELLOW,
        ))

        # Blue line uses the STUDENT'S slope calculation. Initially flat.
        def estimate_line():
            slope = student.secant_slope(f, x, dx.get_value())
            return Line(
                axes.c2p(x - 0.8, f(x) - 0.8 * slope),
                axes.c2p(x + 0.8, f(x) + 0.8 * slope),
                color=BLUE, stroke_width=6,
            )

        estimate = always_redraw(estimate_line)
        value = DecimalNumber(0, num_decimal_places=2, color=BLUE)
        value.add_updater(
            lambda number: number.set_value(
                student.secant_slope(f, x, dx.get_value())
            )
        )
        label = Text("Your slope:", font_size=24)
        readout = VGroup(label, value).arrange(RIGHT, buff=0.18)
        readout.to_edge(UP).shift(DOWN * 0.65 + LEFT * 0.4)

        self.play(FadeIn(title), Create(axes), Create(graph))
        self.add(fixed_dot, moving_dot, secant, estimate, readout)
        self.play(dx.animate.set_value(0.10), run_time=4, rate_func=linear)
        self.wait(0.8)

        # TODO(student, Manim): change the color of your estimate line
        # and test which objects need always_redraw (and which do not).
        # Optional: add a Text label showing the value of dx.
