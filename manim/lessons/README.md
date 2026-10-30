# Five guided Manim lessons for mathematically minded students

These are **not completed examples to copy**. Each scene renders before you
implement it, but part of the picture is deliberately wrong. Your job is to
write the mathematical rule that makes the picture match the idea.

Manim is a Python library that produces videos. The Python code in these
lessons builds the shapes and tells Manim how they change over time. You
should be able to recognize the `Scene`, `self.play(...)`, and `Text(...)`
code without needing to learn a separate game engine.

## Setup

Use **Manim Community Edition** (`manim`), not ManimGL (`manimgl`). If your
computer does not already have Manim installed, follow the official
[Manim installation guide](https://docs.manim.community/en/stable/installation.html).
The lessons do **not** use LaTeX, SVG tools, SymPy, or image assets, although
Manim itself needs its normal system rendering dependencies.

Run from this directory (`manim/lessons`):

```bash
# View a fast, low-resolution preview of lesson 1.
manim -pql lesson_01_graph.py GraphLesson

# Check your math even on a computer without Manim installed.
python check.py 1

# Run the starter's unittest suite (does NOT require completed missions).
python -m unittest discover -s tests -v
```

If there is no video player on your machine, omit `-p`:
`manim -ql lesson_01_graph.py GraphLesson`. Manim saves an MP4 under
`media/videos/...`. It does not overwrite lesson files.

## The learning loop

1. **Render** the incomplete starter and describe what's wrong with it.
2. Open `student.py` and read the numbered steps for that lesson.
3. **Predict** two values before writing the code. Use the `if False` print
   as a temporary diagnostic if you need one.
4. Replace only the `# TODO(student)` function body. Then render again.
5. Run `python check.py <number>`. The checker will say `NOT YET` until
   the math works. It is fine for the OTHER lessons to remain unfinished.
6. Find the `# TODO(student, Manim)` in that lesson's scene file and try its
   small drawing or animation extension.

## Lessons (in order)

| # | Render command | What to implement | Manim concepts |
| --- | --- | --- | --- |
| 1 | `manim -pql lesson_01_graph.py GraphLesson` | Return `sin(x)` instead of a constant | Axes, graph, Dot, `self.play` |
| 2 | `manim -pql lesson_02_circle.py CircleLesson` | Use cos/sin to find a rotating point | radians, `ValueTracker`, `always_redraw` |
| 3 | `manim -pql lesson_03_tangent.py TangentLesson` | Compute rise/run for a secant line | dynamic lines, changing values, limits |
| 4 | `manim -pql lesson_04_area.py AreaLesson` | Add the areas of many rectangles | loops, `VGroup`, `Transform` |
| 5 | `manim -pql lesson_05_matrix.py MatrixLesson` | Apply a 2x2 matrix to each vertex | coordinates, `Polygon`, `Transform` |

These are intentionally small. The visual starter is provided so you can
spend your first session on a *mathematical idea* rather than debugging
video rendering. In each lesson, the last TODO also encourages you to edit
some Manim code directly. You can edit the whole project; these are not
restricted assignments.

## How to tell you are done

- **1:** a yellow dot travels along a sinusoidal blue curve, not a flat line.
- **2:** a yellow point makes a complete revolution around a circle.
- **3:** the student's blue slope line follows the yellow secant as `dx`
  shrinks, and the value approaches 1 at `x=0.5`.
- **4:** the approximate area changes as 4, 8, then 16 rectangles appear.
- **5:** a triangle rotates counterclockwise by a quarter turn.

Run `python check.py all` after finishing the five mathematical tasks.

For ideas **without step-by-step instructions**, see [CHALLENGES.md](CHALLENGES.md).
For lesson pacing and teaching notes, see [TEACHER_GUIDE.md](TEACHER_GUIDE.md).
