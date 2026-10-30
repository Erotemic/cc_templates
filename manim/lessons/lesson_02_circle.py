"""Guided lesson 2: animate a point with sine and cosine.

Run from this folder:
    manim -pql lesson_02_circle.py CircleLesson

Edit student.circle_xy(angle); then try adding a projection line here.
"""

import math

from manim import (
    Axes, BLUE, Create, Dot, DOWN, FadeIn, LEFT, Line, RIGHT, Scene, Text,
    UP, ValueTracker, YELLOW, always_redraw, linear,
)

import student


class CircleLesson(Scene):
    def construct(self):
        title = Text("2. Sine and cosine go in circles", font_size=32).to_edge(UP)
        axes = Axes(
            x_range=[-1.5, 1.5, 0.5], y_range=[-1.5, 1.5, 0.5],
            x_length=5, y_length=5, tips=False,
        ).shift(LEFT * 1.0 + DOWN * 0.35)

        # The circle is already correct; the student's point is not.
        # Every angle t produces the reference point (cos(t), sin(t)).
        circle = axes.plot_parametric_curve(
            lambda t: (math.cos(t), math.sin(t), 0),
            t_range=[0, 2 * math.pi], color=BLUE,
        )
        angle = ValueTracker(0)

        # Both objects use the same student math function. They will move
        # together after circle_xy is implemented correctly.
        point = always_redraw(lambda: Dot(
            axes.c2p(*student.circle_xy(angle.get_value())),
            color=YELLOW, radius=0.10,
        ))
        radius = always_redraw(lambda: Line(
            axes.c2p(0, 0),
            axes.c2p(*student.circle_xy(angle.get_value())),
            color=YELLOW,
        ))
        hint = Text("A full turn is 2*pi radians", font_size=24)
        hint.next_to(axes, RIGHT, buff=0.25)

        self.play(FadeIn(title), Create(axes), Create(circle))
        self.add(radius, point)
        self.play(FadeIn(hint))
        self.play(angle.animate.set_value(2 * math.pi),
                  run_time=5, rate_func=linear)
        self.wait(0.6)

        # TODO(student, Manim): draw the vertical projection from the point
        # to the x-axis. Hint: use another always_redraw(lambda: Line(...)).
        # Its endpoints should be axes.c2p(x, y) and axes.c2p(x, 0).
        # x, y come from student.circle_xy(angle.get_value()).
