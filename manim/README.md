# Manim: make mathematical ideas move

Manim makes animations by writing ordinary Python. Start with the **guided
lessons**, not the larger examples, if you are new to it.

| Folder | What it is for |
| --- | --- |
| [`lessons/`](lessons/README.md) | Five guided math/Manim exercises, with runnable starter scenes and checks |
| `hello_world/` | One complete first animation to read and modify |
| `desmos/` | A more advanced graphing example using Manim and SymPy |

The `lessons/` folder requires Manim Community Edition and its normal rendering
tools. It does **not** require SymPy, SciPy, an extra noise package, or LaTeX.
Use the school's existing Manim installation if one is available.

From `manim/lessons/`:

```bash
manim -ql lesson_01_graph.py GraphLesson
python check.py 1
```

`-ql` renders a low-quality, fast preview. Drop `-p` into the command to open
it automatically if your computer has a video player (`manim -pql ...`).
The checker intentionally reports that a lesson is incomplete until you
write its missing function in `student.py`.
