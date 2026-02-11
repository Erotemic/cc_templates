# desmos_scene.py
"""
manim -pqh desmos_scene.py DesmosTemplate
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Tuple, List

from manim import *
import numpy as np

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

# ---- Parsing helpers (Desmos-ish) ----

TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,  # "2x" -> 2*x
    convert_xor,                          # "x^2" -> x**2
)

SAFE_LOCALS = {
    # symbols (we'll override with actual sympy Symbols too)
    "pi": sp.pi,
    "e": sp.E,

    # functions
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
    "ln": sp.log,
    "log": sp.log,
    "exp": sp.exp,
}

x_sym = sp.Symbol("x")
y_sym = sp.Symbol("y")

SAFE_LOCALS.update({"x": x_sym, "y": y_sym})


def desmos_parse(s: str) -> sp.Expr:
    """
    Parse a Desmos-like expression string into a SymPy expression.
    Supports:
      - implicit multiplication: 2x
      - xor exponent: x^2
    """
    s = s.strip()
    # Common Desmos-ish cosmetic:
    s = s.replace("−", "-")  # minus variants
    return parse_expr(s, local_dict=SAFE_LOCALS, transformations=TRANSFORMS)


@dataclass
class ParsedLine:
    raw: str
    label: str
    kind: str  # "explicit_y" or "implicit"
    f_y: Optional[Callable[[float], float]] = None               # for y=f(x)
    F_xy: Optional[Callable[[float, float], float]] = None       # for F(x,y)=0


def parse_line(line: str) -> ParsedLine:
    """
    Decide whether this is explicit y=... or an implicit equation.
    Rules:
      - If it is exactly "y = <expr>", treat as explicit y=f(x)
      - Otherwise, if it contains "=", treat as implicit: left - right = 0
      - Otherwise, treat as implicit expression = 0
    """
    raw = line.strip()

    # Remove trailing semicolons etc.
    raw = raw.rstrip(";")

    if "=" in raw:
        left, right = [p.strip() for p in raw.split("=", 1)]

        # explicit y=...
        if left == "y":
            expr = desmos_parse(right)
            f = sp.lambdify(x_sym, expr, "numpy")
            return ParsedLine(raw=raw, label=raw, kind="explicit_y", f_y=f)

        # implicit equation: left - right = 0
        L = desmos_parse(left)
        R = desmos_parse(right)
        Fexpr = sp.simplify(L - R)
        F = sp.lambdify((x_sym, y_sym), Fexpr, "numpy")
        return ParsedLine(raw=raw, label=raw, kind="implicit", F_xy=F)

    # No equals: treat as implicit "expr = 0"
    expr = desmos_parse(raw)
    F = sp.lambdify((x_sym, y_sym), expr, "numpy")
    return ParsedLine(raw=raw, label=raw, kind="implicit", F_xy=F)


# ---- Scene ----

class DesmosTemplate(Scene):
    """
    A reusable scene that reads desmos_spec.py and draws:
      - axes
      - a Desmos-like expression list panel
      - explicit plots and implicit curves
    """

    def construct(self):
        # import student spec
        import desmos_spec as spec

        x_range = spec.WINDOW["x_range"]
        y_range = spec.WINDOW["y_range"]

        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            axis_config={"include_numbers": True},
            tips=False,
            x_length=9,
            y_length=6,
        ).to_edge(RIGHT, buff=0.6)

        self.play(Create(axes))

        panel, title = self._make_panel()
        self.play(FadeIn(panel), FadeIn(title))

        parsed = [parse_line(s) for s in spec.LINES]

        rows = self._make_expression_rows(parsed, panel, title)
        self.play(LaggedStart(*[Write(r) for r in rows], lag_ratio=0.12))

        # Draw graphs
        graphs = VGroup()
        for i, p in enumerate(parsed):
            color = self._pick_color(i)

            if p.kind == "explicit_y" and p.f_y is not None:
                g = axes.plot(lambda t: float(p.f_y(t)), color=color)
                graphs.add(g)

            elif p.kind == "implicit" and p.F_xy is not None:
                g = self._implicit_graph(axes, p.F_xy, x_range, y_range, color=color)
                graphs.add(g)

        self.play(LaggedStart(*[Create(g) for g in graphs], lag_ratio=0.15))
        self.wait()

        # Optional: a "cursor dot" moving along the first explicit graph, if present
        first_explicit = next((p for p in parsed if p.kind == "explicit_y" and p.f_y is not None), None)
        if first_explicit:
            t = ValueTracker(x_range[0])
            dot = Dot(radius=0.06)
            dot.set_z_index(10)

            def dot_updater(m: Mobject):
                xv = t.get_value()
                yv = float(first_explicit.f_y(xv))
                m.move_to(axes.c2p(xv, yv))

            dot.add_updater(dot_updater)
            self.add(dot)
            self.play(t.animate.set_value(x_range[1]), run_time=3, rate_func=linear)
            dot.clear_updaters()
            self.wait()

    # ---- UI helpers ----

    def _make_panel(self):
        panel = RoundedRectangle(corner_radius=0.2, height=5.8, width=3.3)
        panel.set_stroke(WHITE, 2).set_fill(BLACK, opacity=0.25)
        panel.to_edge(LEFT, buff=0.5)

        title = Text("Expressions", font_size=28).next_to(panel.get_top(), DOWN, buff=0.25)
        title.align_to(panel, LEFT).shift(RIGHT * 0.25)
        return panel, title

    def _make_expression_rows(self, parsed: List[ParsedLine], panel: Mobject, title: Mobject):
        rows = VGroup()
        for i, p in enumerate(parsed):
            color = self._pick_color(i)
            row = Text(p.label, font_size=22, color=color)
            rows.add(row)

        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        rows.next_to(title, DOWN, buff=0.3)
        rows.align_to(panel, LEFT).shift(RIGHT * 0.25)
        return rows

    def _pick_color(self, i: int):
        palette = [YELLOW, BLUE, GREEN, RED, PURPLE, ORANGE, TEAL]
        return palette[i % len(palette)]

    # ---- Implicit plotting ----

    def _implicit_graph(
        self,
        axes: Axes,
        F_xy: Callable[[float, float], float],
        x_range: Tuple[float, float, float],
        y_range: Tuple[float, float, float],
        color=WHITE,
    ) -> VMobject:
        """
        Render F(x,y)=0 using Manim's ImplicitFunction, but evaluated in AXES coordinates.
        ImplicitFunction parameterizes in scene coordinates, so we convert (X,Y)->(x,y) using axes.p2c.
        """
        x_min, x_max, _ = x_range
        y_min, y_max, _ = y_range

        # Convert scene point -> axes coords -> evaluate F
        def F_scene(X, Y):
            x_val, y_val, *_ = axes.p2c(np.array([X, Y, 0.0]))
            return float(F_xy(x_val, y_val))

        # We must define the scene-coordinate bounding box that corresponds to the axes window
        bl = axes.c2p(x_min, y_min)
        tr = axes.c2p(x_max, y_max)

        # In scene coords:
        X_min, Y_min, _ = bl
        X_max, Y_max, _ = tr

        # ImplicitFunction exists in Manim Community; if you get an import error,
        # you can replace this with a custom contour sampler later.
        curve = ImplicitFunction(
            F_scene,
            x_range=[X_min, X_max],
            y_range=[Y_min, Y_max],
            color=color,
        )
        return curve
