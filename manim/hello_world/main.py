import manim
from manim import (
    BLUE, WHITE, TAU,
    Circle, Create, FadeOut, Scene, Text, Transform,
    ParametricFunction, TracedPath, MoveAlongPath,
    MoveToTarget, NumberPlane,
)
import math


class TheHelloWorldScene(Scene):
    def construct(self):

        if False:
            # Create a coordinate grid, which is useful for debugging
            # Can disable this if wanted.
            grid = NumberPlane(
                x_range=[-7, 7, 1],
                y_range=[-4, 4, 1],
                background_line_style={
                    "stroke_color": "#0000FF",
                    "stroke_width": 2,
                    "stroke_opacity": 0.2
                },
                axis_config={
                    "color": 'white',
                    "stroke_width": 3,
                    "stroke_opacity": 0.4
                }
            )
            # Add the grid to the scene
            self.add(grid)

        # --- Circle ---
        circle = Circle(radius=0.3)
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(WHITE, width=4)

        # Show the circle
        self.play(Create(circle))
        self.wait(0.1)

        # --- Sine path & tracer ---
        x_min = -2
        x_max = 2

        def our_position_function(t):
            """
            Given the argument time, return the coordinate the center of the circle
            should be at.
            """
            # Our "t" variable runs from 0 to 6.283ish
            # But the screen coordinates range roughly from -2 to +2, so
            # this will translate our "t" coordinates into nice "x" coordinates
            # for the screen
            x = (t / TAU) * (x_max - x_min) + x_min

            # We compute the sin result directly. These are already in decent
            # display coordinates, but we could modify them if needed.
            y = math.sin(t)

            # We are doing a 2D visualization, so keep z=0
            z = 0
            position = [x, y, z]

            return position

        sine_path = ParametricFunction(
            function=our_position_function,
            t_range=[0, TAU],
            stroke_color=WHITE,
            stroke_width=3,
        )

        # Place circle at start of the path and create a dynamic tracer
        circle.generate_target()
        circle.target.move_to(sine_path.point_from_proportion(0))  # set target position
        self.play(MoveToTarget(circle), run_time=1)

        tracer = TracedPath(circle.get_center, stroke_color=WHITE, stroke_width=4)

        self.add(tracer)  # tracer must be in the scene before movement
        # Animate the circle tracing along the sine
        self.play(MoveAlongPath(circle, sine_path), run_time=3, rate_func=manim.linear)
        self.wait(0.5)

        # (Optional) Clean up the path & tracer before transforming
        self.play(FadeOut(sine_path), FadeOut(tracer))
        self.wait(0.25)

        # --- Transform into text ---
        text = Text("Hello World")
        self.play(Transform(circle, text))
        self.wait(1)

        # Fade out
        self.play(FadeOut(circle))
        self.wait(0.5)


def main():
    # Configure render settings (preview, low quality)
    config = {
        "quality": "low_quality",
        "preview": True
    }
    with manim.tempconfig(config):
        scene = TheHelloWorldScene()
        scene.render()

if __name__ == "__main__":
    # To run this demo, either run:
    # python main.py
    # or use the manim CLI:
    # manim -pql main.py TheHelloWorldScene
    main()
