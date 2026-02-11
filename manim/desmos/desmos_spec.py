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

    # # --- Inverse hyperbolic functions (defined with logs, Desmos-style) ---
    # # arctanh(x) = 1/2 ln((1+x)/(1-x))   domain: |x| < 1
    # "y = (1/2) ln((1+x)/(1-x))",

    # # arccoth(x) = 1/2 ln((x+1)/(x-1))   domain: |x| > 1
    # # (equivalently 1/2 ln((x+1)/(x-1)) for x>1; and 1/2 ln((x+1)/(x-1)) also works with abs handling)
    # "y = (1/2) ln((x+1)/(x-1))",

    # # --- Antiderivatives ---
    # # ∫ arctanh(x) dx = x*arctanh(x) + 1/2 ln(1 - x^2) + C
    # # We'll use the log-definition for arctanh(x) inside:
    # "y = x*((1/2) ln((1+x)/(1-x))) + (1/2) ln(1 - x^2)",

    # # ∫ arccoth(x) dx = x*arccoth(x) + 1/2 ln(x^2 - 1) + C
    # # We'll use the log-definition for arccoth(x) inside:
    # "y = x*((1/2) ln((x+1)/(x-1))) + (1/2) ln(x^2 - 1)",

    # # --- Optional visual cue: show they're the same template ---
    # # Both have:  x * (inverse hyperbolic)  +  (1/2) ln(|1 - x^2|) up to domain/abs.
    # # This "unified" expression uses abs; it will show the shared structure across domains.
    # "y = x*((1/2) ln(abs((1+x)/(1-x)))) + (1/2) ln(abs(1 - x^2))",
]
