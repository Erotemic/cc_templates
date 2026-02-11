from manim import *
import sympy as sp

class DesmosLikeGraph(Scene):
    def construct(self):
        # --- Student-editable section (later move to a separate file) ---
        window = dict(x_range=(-8, 8, 1), y_range=(-5, 5, 1))
        expressions = [
            dict(expr="2*x+1", color=YELLOW, label="y=2x+1"),
            dict(expr="sin(x)", color=BLUE, label="y=sin(x)"),
        ]
        # ---------------------------------------------------------------

        axes = Axes(
            x_range=window["x_range"],
            y_range=window["y_range"],
            axis_config={"include_numbers": True},
            tips=False,
        ).to_edge(RIGHT, buff=0.8)

        self.play(Create(axes))

        # "Desmos list" panel on the left
        panel = RoundedRectangle(corner_radius=0.2, height=4.8, width=4.5)
        panel.set_stroke(WHITE, 2).set_fill(BLACK, opacity=0.3)
        panel.to_edge(LEFT, buff=0.5)

        title = Text("Expressions", font_size=28).next_to(panel.get_top(), DOWN, buff=0.3)
        self.play(FadeIn(panel), FadeIn(title))

        x = sp.Symbol("x")
        rows = VGroup()

        plots = VGroup()
        for i, item in enumerate(expressions):
            expr_str = item["expr"]
            color = item.get("color", WHITE)
            label_str = item.get("label", f"y={expr_str}")

            # SymPy parse -> numeric function
            sym_expr = sp.sympify(expr_str, locals={"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sqrt": sp.sqrt})
            f = sp.lambdify(x, sym_expr, "numpy")

            graph = axes.plot(lambda t: f(t), color=color)
            plots.add(graph)

            row = Text(label_str, font_size=22, color=color)
            rows.add(row)

        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        rows.next_to(title, DOWN, buff=0.3).align_to(panel.get_left(), LEFT).shift(RIGHT*0.3)

        self.play(LaggedStart(*[Write(r) for r in rows], lag_ratio=0.15))
        self.play(LaggedStart(*[Create(g) for g in plots], lag_ratio=0.2))
        self.wait()

        # Bonus: a moving dot (like Desmos cursor)
        dot = Dot(color=WHITE)
        t = ValueTracker(-6)

        first_expr = sp.sympify(expressions[0]["expr"], locals={"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "sqrt": sp.sqrt})
        f0 = sp.lambdify(x, first_expr, "numpy")

        dot.add_updater(lambda m: m.move_to(axes.c2p(t.get_value(), f0(t.get_value()))))
        self.add(dot)

        self.play(t.animate.set_value(6), run_time=3, rate_func=linear)
        dot.clear_updaters()
        self.wait()

