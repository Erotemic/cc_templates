"""Five guided math tasks. The Manim scenes are in lesson_0*.py.

RECOMMENDED WORKFLOW
    1. Render a starter scene. It should already work, but look incomplete.
    2. Read ONE mission below and predict what needs to change.
    3. Try the diagnostic: change ``if False`` to ``if True`` briefly.
    4. Implement the missing math with ordinary Python.
    5. Render again, then run ``python check.py <lesson-number>``.

You are expected to change these functions! Their starting answers are
placeholders, not solutions. Nothing in this file requires Manim to import.
"""

import math


def wave_height(x):
    """MISSION 1: make a moving dot trace a sine wave instead of a flat line.

    INPUT:  x is a horizontal coordinate, measured in radians for sin(x).
    OUTPUT: the height y of the graph at that x.

    HOW TO DO IT:
    1. Render GraphLesson first. See the flat blue graph and moving dot.
    2. Turn on the diagnostic below to observe some x values.
    3. ``math.sin(x)`` gives the correct height at x.
    4. Replace ``return 0.0`` with a return statement that uses sin(x).
    5. Render again. The blue line should now rise and fall; the dot must
       stay on the curve. In lesson_01_graph.py, add a new Text label.

    CHECK: python check.py 1
    WHY: a graph of y=f(x) is all points (x, f(x)).
    """
    if False:
        print("WAVE DEBUG:", "x=", round(x, 2),
              "sin(x)=", round(math.sin(x), 2))

    # TODO(student): return the sine of x, rather than a constant height.
    return 0.0


def circle_xy(angle):
    """MISSION 2: find a point on the unit circle from an angle.

    INPUT: angle is in RADIANS (not degrees); 2*pi is a full revolution.
    OUTPUT: two numbers (x, y), the point on the circle.

    HOW TO DO IT:
    1. Render CircleLesson. The angle changes, but the dot stays still.
    2. At angle 0, the point is (1, 0); at pi/2 it is (0, 1).
    3. Use cosine for the x-coordinate and sine for the y-coordinate.
       ``math.cos(angle)`` and ``math.sin(angle)`` do both calculations.
    4. Return the TWO coordinates separated by a comma, e.g. (x, y).
    5. Render again. The dot and radius should rotate one full turn.
       Then try drawing the vertical projection in lesson_02_circle.py.

    CHECK: python check.py 2
    WHY: cos^2(theta) + sin^2(theta) = 1.
    """
    if False:
        print("CIRCLE DEBUG:", "angle=", round(angle, 2),
              "expected x=", round(math.cos(angle), 2),
              "expected y=", round(math.sin(angle), 2))

    # TODO(student): compute x and y using cosine and sine.
    return (1.0, 0.0)


def secant_slope(function, x, dx):
    """MISSION 3: calculate the slope of a secant line.

    INPUT: function is a callable f(x); x is the starting x; dx > 0.
    OUTPUT: slope of the line from (x, f(x)) to (x+dx, f(x+dx)).

    HOW TO DO IT:
    1. Render TangentLesson. The yellow secant tilts, but your blue
       estimated-slope line is horizontal. Its numeric readout is zero.
    2. The horizontal distance (run) is ``dx``.
    3. The vertical distance (rise) is ``function(x + dx) - function(x)``.
    4. Slope is rise divided by run. Compute and return that number.
    5. Render again. As the yellow points approach each other, the blue
       estimate should approach the actual tangent to the curve.

    CHECK: python check.py 3
    WHY: the derivative is the LIMIT of secant slopes as dx approaches 0.
    The exercise only uses positive dx; you do not need dx=0.
    """
    if False:
        print("SLOPE DEBUG:", "x=", x, "dx=", dx,
              "f(x)=", function(x), "f(x+dx)=", function(x + dx))

    # TODO(student): compute rise/run, taking care to use function(...).
    return 0.0


def left_sum(function, left, right, count):
    """MISSION 4: approximate area with left-endpoint rectangles.

    INPUT: function f(x), interval [left, right], and rectangle count >= 1.
    OUTPUT: the total approximate area under f on the interval.

    HOW TO DO IT:
    1. Render AreaLesson. The rectangles are drawn for you, but the
       'your estimate' number is wrong: it stays at zero.
    2. Each rectangle has width ``dx = (right - left) / count``.
    3. Start ``total = 0.0``.
    4. In ``for i in range(count):`` get the left edge's x-coordinate:
       ``x = left + i * dx``.
    5. Rectangle area is ``function(x) * dx``; add it to total.
    6. Return total. Re-render and compare the estimates for 4, 8, and
       16 rectangles. The sum should change as the rectangles get thinner.

    CHECK: python check.py 4
    WHY: integration can be approximated by adding many small rectangles.
    Stretch: use right or midpoint samples; which is more accurate?
    """
    if False:
        print("AREA DEBUG:", "left=", left, "right=", right,
              "count=", count, "width=", (right - left) / count)

    # TODO(student): compute dx, loop over rectangles, and accumulate area.
    return 0.0


def transform_xy(x, y, matrix):
    """MISSION 5: move a shape using a 2-by-2 matrix.

    INPUT: a point (x, y) and matrix ((a, b), (c, d)).
    OUTPUT: new coordinates (new_x, new_y).

    HOW TO DO IT:
    1. Render MatrixLesson. The yellow triangle does not rotate yet.
    2. Read ``matrix[0]`` and ``matrix[1]`` to find the two rows.
       You can unpack them: ``a, b = matrix[0]`` and ``c, d = matrix[1]``.
    3. Compute ``new_x = a*x + b*y``.
    4. Compute ``new_y = c*x + d*y``.
    5. Return (new_x, new_y). The scene now rotates a triangle by 90 degrees.
    6. Change the matrix in lesson_05_matrix.py and predict what happens:
       try a scale matrix or a shear matrix.

    CHECK: python check.py 5
    WHY: a matrix describes a rule that transforms every point in the plane.
    """
    if False:
        print("MATRIX DEBUG:", "point=", (x, y), "matrix=", matrix)

    # TODO(student): compute the two dot products of the matrix rows.
    return (x, y)
