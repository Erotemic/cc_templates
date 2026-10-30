# Instructor guide: guided Manim math lessons

## Design decision

The pre-existing `manim/hello_world/` and `manim/desmos/` illustrate what
Manim can do, but they don't guide a student through making a meaningful
change. These five exercises keep a working visual baseline and one
math function deliberately unfinished for each lesson. The student gets
feedback from **both** a rendered animation and a plain-Python checker.

Avoid showing the student the finished expressions before they have guessed
what should happen. The instructions are explicit so students can work
independently if the instructor is helping someone else.

## Suggested sequence

| Lesson | Mathematical questions | Python / Manim questions |
| --- | --- | --- |
| 1. Graph | What is y at x=0 and x=pi/2? | What does `Axes.c2p` do? What does the tracker change? |
| 2. Circle | Why do sin/cos trace a circle? Why radians? | Why is `always_redraw` useful? |
| 3. Slope | How does rise/run change as points get closer? | Why is the number updated every frame? |
| 4. Area | Why does changing the rectangle count change the error? | Where is the `for` loop? What does `Transform` animate? |
| 5. Matrix | Where does (1,0) go under a 90-degree rotation? | How are every vertex's new coordinates computed? |

The first two can each fit into a 30-45 minute meeting. The other three
are natural follow-ups for students already comfortable with loops and
functions. Let students change parameters and try their own mathematical
examples after a lesson passes.

## Where to guide vs. leave room

- `student.py` has step-by-step instructions and optional diagnostics.
  Every function has an intentionally incomplete return value.
- Each scene file contains a `TODO(student, Manim)` for extending the
  *animation code*, not just the mathematics.
- `check.py` imports only `student.py` and Python's standard library.
  It intentionally reports `NOT YET` for unfinished missions; this is not
  a test-suite failure.
- `tests/` checks that the starter scenes parse and their extension points
  are usable, without requiring the student to adopt one particular answer.
- Scene files use only Manim's `Text`, not `MathTex`, so LaTeX is optional.

## Important teaching distinctions

- **Math coordinates vs. screen coordinates**: `axes.c2p(x, y)` maps a
  mathematical point to a position in Manim's scene.
- **An update vs. an animation**: `ValueTracker` stores a number;
  `always_redraw` recomputes shapes while `self.play(...)` changes it.
- **Numerical vs. exact mathematics**: `secant_slope` uses a nonzero `dx`
  rather than directly calculating a derivative at `dx=0`.
- **Area approximation**: the sum should use the *same sampling choice*
  as the Manim rectangles (`input_sample_type="left"`).
- **Matrices**: the output components are row dot-products with `(x, y)`.

## Check commands

```bash
cd manim/lessons
python -m unittest discover -s tests -v
python check.py 1  # expected NOT YET before the student's implementation
manim -ql lesson_01_graph.py GraphLesson
```

Rendering uses Manim's own renderer. The standard library tests run even
on school computers where Manim has not been set up, but the actual videos
must be checked with a functioning Manim install.

## Extensions once a student finishes

The open challenge board includes Newton's method, Monte Carlo pi,
random walks, and graphs/algorithms. These work well for mathematically
motivated students who want to research a method and choose their own
visualization rather than follow another recipe.
