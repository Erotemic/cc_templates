"""Guided lesson 1: turn a flat graph into a sine wave.

Run from this folder:
    manim -pql lesson_01_graph.py GraphLesson

Edit the first function in student.py, then render again.
No LaTeX, SymPy, or external images are required.
"""

from manim import (
    Axes, BLUE, Create, Dot, DOWN, FadeIn, Scene, Text,
    UP, ValueTracker, YELLOW, always_redraw, linear,
)

import student


class GraphLesson(Scene):
    def construct(self):
        # A Manim Scene contains objects (mobjects) and animations.
        title = Text("1. Points make a graph", font_size=34).to_edge(UP)
        axes = Axes(
            x_range=[-4, 4, 1], y_range=[-2, 2, 1],
            x_length=9, y_length=4.5, tips=False,
            axis_config={"include_numbers": True},
        ).shift(DOWN * 0.4)

        # Axes.plot calls student.wave_height(x) at many x values.
        # The starter returns 0, so this is a straight line for now.
        graph = axes.plot(student.wave_height, x_range=[-4, 4, 0.06],
                          color=BLUE)
        x_position = ValueTracker(-3.8)
        # The dot is recreated as x_position changes. That is why it stays
        # attached to the graph even AFTER the student edits the function.
        moving_dot = always_redraw(lambda: Dot(
            axes.c2p(x_position.get_value(),
                     student.wave_height(x_position.get_value())),
            color=YELLOW, radius=0.10,
        ))

        self.play(FadeIn(title), Create(axes))
        self.play(Create(graph))
        self.add(moving_dot)
        self.play(x_position.animate.set_value(3.8),
                  run_time=4, rate_func=linear)
        self.wait(0.6)

        # TODO(student, Manim): add a second Text label that says "y=sin(x)".
        # Try creating Text(..., font_size=24), positioning it with
        # .to_edge(UP) or .next_to(...), then self.play(FadeIn(label)).
        # The title above is an example you can adapt.
