# desmos_scene.py
"""
Run with:

    manim -pqh desmos_scene.py DesmosTemplate

    # low quality faster render
    manim -pql desmos_scene.py DesmosTemplate
    manim -pqk desmos_scene.py DesmosTemplate


This file is a "Desmos-like" graphing template built on Manim + SymPy.

High-level idea:
- Write equations in `desmos_spec.py` (like typing into Desmos).
- We parse those strings into SymPy expressions (math objects).
- We turn SymPy expressions into fast numeric functions (via lambdify).
- We draw the resulting curves with Manim.

Key concepts:
- SymPy is the "math brain" (parsing + symbolic expressions).
- Manim is the "animation engine" (axes, shapes, drawing, and animations).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple, List

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

# Explicit Manim imports
from manim import (
    # Core scene / animation primitives
    Scene,
    Create,
    FadeIn,
    Write,
    LaggedStart,
    linear,
    # Coordinate system and graphing
    Axes,
    ImplicitFunction,
    # Vector graphics "containers"
    VGroup,
    VMobject,
    Mobject,
    # UI and text
    RoundedRectangle,
    Text,
    # Simple objects + animation helpers
    Dot,
    ValueTracker,
    # Direction vectors (used with .to_edge / .shift)
    RIGHT,
    LEFT,
    DOWN,
    # Common colors
    WHITE,
    BLACK,
    YELLOW,
    BLUE,
    GREEN,
    RED,
    PURPLE,
    ORANGE,
    TEAL,
)


# =============================================================================
# Parsing helpers (turn Desmos-ish strings into SymPy expressions)
# =============================================================================

# SymPy's parser can apply "transformations" to change how strings are interpreted.
# We add two transformations that make it feel more like Desmos:
# - implicit_multiplication_application: "2x" becomes "2*x"
# - convert_xor: "x^2" becomes "x**2" (Python uses ** for powers)
TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,  # "2x" -> 2*x
    convert_xor,  # "x^2" -> x**2
)

# Restrict what names/functions are allowed during parsing for safety + clarity.
# Students can type sin(x), ln(x), sqrt(x), etc.
SAFE_LOCALS = {
    # constants
    "pi": sp.pi,
    "e": sp.E,
    # common functions
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
    "Abs": sp.Abs,  # allow either abs(...) or Abs(...)
    "ln": sp.log,
    "log": sp.log,
    "exp": sp.exp,
}

# These are the symbols that can appear in equations.
# We make them explicit so SymPy knows "x" and "y" are variables.
x_sym = sp.Symbol("x")
y_sym = sp.Symbol("y")
SAFE_LOCALS.update({"x": x_sym, "y": y_sym})


def desmos_parse(s: str) -> sp.Expr:
    """
    Parse a Desmos-like expression string into a SymPy expression.

    Example inputs:
        "2x + 1"
        "sin(x)"
        "x^2 + y^2 - 9"

    Returns:
        A SymPy expression object (symbolic math).
    """
    s = s.strip()

    # Sometimes text copied from web uses a unicode minus sign "−".
    # We normalize it to the normal ASCII "-".
    s = s.replace("−", "-")

    # parse_expr turns a string into a SymPy expression, using our safe locals + transforms.
    return parse_expr(s, local_dict=SAFE_LOCALS, transformations=TRANSFORMS)


@dataclass
class ParsedLine:
    """
    A small record that stores what we learned by reading a single line from desmos_spec.py.

    - kind="explicit_y": equation is y = f(x)
      We store f_y: a fast numerical function f(x).

    - kind="implicit": equation is F(x, y) = 0 (like x^2 + y^2 = 9)
      We store F_xy: a fast numerical function F(x, y).
    """
    raw: str
    label: str
    kind: str  # "explicit_y" or "implicit"
    f_y: Optional[Callable[[float], float]] = None  # for y=f(x)
    F_xy: Optional[Callable[[float, float], float]] = None  # for F(x,y)=0


def parse_line(line: str) -> ParsedLine:
    """
    Convert one Desmos-style line into either an explicit function or an implicit equation.

    Rules:
      1) If the line looks like: "y = <expr>" → explicit y=f(x).
      2) Else, if it contains "=" → implicit: left - right = 0.
      3) Else → implicit: expr = 0.
    """
    raw = line.strip().rstrip(";")

    if "=" in raw:
        left, right = [p.strip() for p in raw.split("=", 1)]

        # Explicit function case: y = f(x)
        if left == "y":
            expr = desmos_parse(right)

            # lambdify turns a SymPy expression into a fast numeric function.
            # Using backend="numpy" makes it work on floats efficiently.
            f = sp.lambdify(x_sym, expr, "numpy")
            return ParsedLine(raw=raw, label=raw, kind="explicit_y", f_y=f)

        # Implicit case: (left) = (right)  -->  (left - right) = 0
        L = desmos_parse(left)
        R = desmos_parse(right)
        Fexpr = sp.simplify(L - R)
        F = sp.lambdify((x_sym, y_sym), Fexpr, "numpy")
        return ParsedLine(raw=raw, label=raw, kind="implicit", F_xy=F)

    # No equals sign: interpret as "expr = 0"
    expr = desmos_parse(raw)
    F = sp.lambdify((x_sym, y_sym), expr, "numpy")
    return ParsedLine(raw=raw, label=raw, kind="implicit", F_xy=F)


# =============================================================================
# Manim Scene: build axes, show expressions, draw curves
# =============================================================================

class DesmosTemplate(Scene):
    """
    A reusable scene that reads `desmos_spec.py` and draws:
      - axes
      - a Desmos-like expression list panel (left side)
      - explicit plots y=f(x)
      - implicit curves F(x,y)=0
    """

    def construct(self):
        # This imports the data we want to plot from: desmos_spec.py
        # It should contain WINDOW and LINES.
        import desmos_spec as spec

        x_range = spec.WINDOW["x_range"]
        y_range = spec.WINDOW["y_range"]

        # Axes are like the graphing window in Desmos.
        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            axis_config={"include_numbers": True},
            tips=False,
            x_length=9,
            y_length=6,
        ).to_edge(RIGHT, buff=0.6)

        # Animate drawing the axes.
        self.play(Create(axes))

        # Make the "expression list" UI on the left.
        panel, title = self._make_panel()
        self.play(FadeIn(panel), FadeIn(title))

        # Parse each line of input into a standardized representation.
        parsed = [parse_line(s) for s in spec.LINES]

        # Show the parsed lines as colored text, like a Desmos list.
        rows = self._make_expression_rows(parsed, panel, title)
        self.play(LaggedStart(*[Write(r) for r in rows], lag_ratio=0.12))

        # Draw graphs (curves) for every expression.
        graphs = VGroup()
        for i, p in enumerate(parsed):
            color = self._pick_color(i)

            if p.kind == "explicit_y" and p.f_y is not None:
                # Why not axes.plot(...)?
                #
                # Desmos skips parts of curves that are not real-valued
                # (e.g. ln(1-x^2) outside [-1, 1]). Manim's built-in plot doesn't
                # always handle NaNs/infinities the way we want.
                #
                # So we sample many x values, keep only real/finite y values,
                # and split the curve into segments when it "breaks".
                x_min, x_max, _ = x_range
                g = self._plot_real_segments(axes, p.f_y, x_min, x_max, color=color)
                graphs.add(g)

            elif p.kind == "implicit" and p.F_xy is not None:
                # Implicit curve: draw the set of points where F(x,y)=0
                g = self._implicit_graph(axes, p.F_xy, x_range, y_range, color=color)
                graphs.add(g)

        self.play(LaggedStart(*[Create(g) for g in graphs], lag_ratio=0.15))
        self.wait()

        # A "tracer dot" that moves along every curve we drew
        dot = Dot(radius=0.06, color=WHITE)
        dot.set_z_index(10)
        self.add(dot)

        # graphs is a VGroup that contains either:
        # - implicit curves: VMobject
        # - explicit curves: VGroup of VMobject segments
        for g in graphs:
            if isinstance(g, VGroup):
                # explicit plot made of multiple segments
                for seg in g:
                    # skip tiny/empty segments
                    if hasattr(seg, "get_num_points") and seg.get_num_points() < 2:
                        continue
                    self._trace_dot_along(dot, seg, run_time=1.5)
            else:
                # implicit curve is typically a single VMobject
                if hasattr(g, "get_num_points") and g.get_num_points() >= 2:
                    self._trace_dot_along(dot, g, run_time=2.0)

        self.wait()

    def _trace_dot_along(self, dot: Dot, curve: VMobject, run_time: float = 2.0):
        """
        Animate `dot` sliding along `curve` from start to end.
        Uses curve.point_from_proportion(alpha) where alpha goes 0->1.
        """
        alpha = ValueTracker(0.0)

        def updater(m: Mobject):
            m.move_to(curve.point_from_proportion(alpha.get_value()))

        dot.add_updater(updater)
        self.play(alpha.animate.set_value(1.0), run_time=run_time, rate_func=linear)
        dot.remove_updater(updater)

    # -------------------------------------------------------------------------
    # UI helpers (the "Desmos expression list" panel)
    # -------------------------------------------------------------------------

    def _make_panel(self):
        # This rectangle is just a visual "panel" like Desmos' left sidebar.
        panel = RoundedRectangle(corner_radius=0.2, height=5.8, width=3.3)
        panel.set_stroke(WHITE, 2).set_fill(BLACK, opacity=0.25)
        panel.to_edge(LEFT, buff=0.5)

        title = Text("Expressions", font_size=28).next_to(panel.get_top(), DOWN, buff=0.25)
        title.align_to(panel, LEFT).shift(RIGHT * 0.25)
        return panel, title

    def _make_expression_rows(self, parsed: List[ParsedLine], panel: Mobject, title: Mobject):
        # Build a vertical list of colored equation strings.
        rows = VGroup()
        for i, p in enumerate(parsed):
            color = self._pick_color(i)
            row = Text(p.label, font_size=22, color=color)
            rows.add(row)

        # Stack them top-to-bottom, left aligned.
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        rows.next_to(title, DOWN, buff=0.3)
        rows.align_to(panel, LEFT).shift(RIGHT * 0.25)
        return rows

    def _pick_color(self, i: int):
        # A simple repeating palette, similar to Desmos line colors.
        palette = [YELLOW, BLUE, GREEN, RED, PURPLE, ORANGE, TEAL]
        return palette[i % len(palette)]

    # -------------------------------------------------------------------------
    # Implicit plotting: curves defined by F(x,y) = 0
    # -------------------------------------------------------------------------

    def _implicit_graph(
        self,
        axes: Axes,
        F_xy: Callable[[float, float], float],
        x_range: Tuple[float, float, float],
        y_range: Tuple[float, float, float],
        color=WHITE,
    ) -> VMobject:
        """
        Render an implicit curve F(x,y)=0 using Manim's ImplicitFunction.

        Important subtlety:
        - ImplicitFunction expects a function in *scene coordinates* (pixels-ish),
          but our math function F_xy expects *axes coordinates* (x and y values).
        - So we convert (X_scene, Y_scene) -> (x_axes, y_axes) before evaluating F_xy.
        """
        x_min, x_max, _ = x_range
        y_min, y_max, _ = y_range

        def F_scene(X, Y):
            # axes.p2c converts a point in scene coordinates to coordinates in the axes system.
            coords = axes.p2c(np.array([X, Y, 0.0]))
            x_val, y_val = coords[0], coords[1]
            return float(F_xy(x_val, y_val))

        # Define the scene-coordinate bounding box that corresponds to our axes window.
        bl = axes.c2p(x_min, y_min)  # bottom-left corner (scene coords)
        tr = axes.c2p(x_max, y_max)  # top-right corner (scene coords)
        X_min, Y_min, _ = bl
        X_max, Y_max, _ = tr

        # ImplicitFunction traces where F_scene(X,Y)=0.
        curve = ImplicitFunction(
            F_scene,
            x_range=[X_min, X_max],
            y_range=[Y_min, Y_max],
            color=color,
        )
        return curve

    # -------------------------------------------------------------------------
    # Explicit plotting: curves defined by y = f(x), with Desmos-like domain handling
    # -------------------------------------------------------------------------

    def _plot_real_segments(
        self,
        axes: Axes,
        f: Callable[[float], float],
        x_min: float,
        x_max: float,
        color=WHITE,
        n_samples: int = 2000,
        jump_tol: float = 3.0,
    ) -> VGroup:
        """
        Draw y=f(x) by sampling many x values, then:
        - keep only finite (real) points
        - split into separate curve segments when values become invalid or jump

        This mimics Desmos behavior around:
        - logs with restricted domains
        - vertical asymptotes
        - square roots of negative numbers, etc.
        """
        xs = np.linspace(x_min, x_max, n_samples)
        ys = np.empty_like(xs, dtype=float)

        # Evaluate y values. Any invalid computation becomes NaN.
        for i, xv in enumerate(xs):
            try:
                yv = f(xv)

                # If SymPy/numpy produces complex numbers (not real),
                # we treat that as "not drawable" in a real graph.
                if np.iscomplexobj(yv):
                    yv = np.nan

                ys[i] = float(yv)
            except Exception:
                ys[i] = np.nan

        # Valid means finite (not NaN, not inf).
        valid = np.isfinite(ys)

        segments = VGroup()
        start = None  # index where the current valid segment began

        def flush_segment(a: Optional[int], b: Optional[int]):
            """Create a VMobject from xs[a:b], ys[a:b] if the slice is long enough."""
            if a is None or b is None or b - a < 2:
                return
            pts = [axes.c2p(xs[j], ys[j]) for j in range(a, b)]
            vm = VMobject()
            vm.set_points_as_corners(pts)
            vm.set_stroke(color, width=4)
            segments.add(vm)

        # Walk across samples; break segments on invalid points or large jumps.
        for i in range(len(xs)):
            if not valid[i]:
                flush_segment(start, i)
                start = None
                continue

            if start is None:
                start = i
                continue

            # If consecutive points have a big y jump, that's usually an asymptote.
            if np.isfinite(ys[i - 1]) and abs(ys[i] - ys[i - 1]) > jump_tol:
                flush_segment(start, i)
                start = i

        flush_segment(start, len(xs))
        return segments

    # Manim Studio compatibility hook (older Manim Studio expects this)
    def setup_deepness(self):
        pass
