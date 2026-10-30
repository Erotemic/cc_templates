"""Starter tests that do not require Manim or finished student missions.

Students can run these while lessons are incomplete. The separate
``python check.py N`` command checks whether a specific mission is solved.
"""

from __future__ import annotations

import ast
import importlib.util
import math
from pathlib import Path
import contextlib
import io
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCENES = (
    ("lesson_01_graph.py", "GraphLesson", "wave_height"),
    ("lesson_02_circle.py", "CircleLesson", "circle_xy"),
    ("lesson_03_tangent.py", "TangentLesson", "secant_slope"),
    ("lesson_04_area.py", "AreaLesson", "left_sum"),
    ("lesson_05_matrix.py", "MatrixLesson", "transform_xy"),
)

# Import the student code directly from this folder. No Manim dependency.
sys.path.insert(0, str(ROOT))
import student  # noqa: E402
import check  # noqa: E402


class LessonScaffoldingTests(unittest.TestCase):
    def test_scenes_are_valid_python_with_a_scene_and_hook(self):
        for filename, scene_name, hook_name in SCENES:
            with self.subTest(filename=filename):
                source = (ROOT / filename).read_text(encoding="utf8")
                tree = ast.parse(source, filename=filename)
                names = {node.name for node in tree.body
                         if isinstance(node, ast.ClassDef)}
                self.assertIn(scene_name, names)
                self.assertIn("student." + hook_name, source)

    def test_student_functions_are_present_and_callable(self):
        values = (
            student.wave_height(0.5),
            *student.circle_xy(0.5),
            student.secant_slope(lambda x: x * x, 1.0, 0.25),
            student.left_sum(lambda x: 1.0, -1.0, 1.0, 3),
            *student.transform_xy(1.0, 2.0, ((0, -1), (1, 0))),
        )
        self.assertEqual(len(values), 7)
        self.assertTrue(all(isinstance(value, (int, float)) and math.isfinite(value)
                            for value in values))

    def test_checker_can_report_success_or_failure_for_any_lesson(self):
        for number in range(1, 6):
            with self.subTest(number=number):
                with contextlib.redirect_stdout(io.StringIO()):
                    with patch.dict(check.CHECKS, {number: lambda: True}, clear=True):
                        self.assertEqual(check.main([str(number)]), 0)
                    with patch.dict(check.CHECKS, {number: lambda: False}, clear=True):
                        self.assertEqual(check.main([str(number)]), 1)

    def test_all_scenes_compile_without_importing_manim(self):
        for filename, _scene_name, _hook_name in SCENES:
            with self.subTest(filename=filename):
                compile((ROOT / filename).read_text(encoding="utf8"),
                        str(ROOT / filename), "exec")

    def test_checker_runs_from_command_line(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "check.py"), "1"],
            cwd=ROOT, capture_output=True, text=True,
        )
        # The student may or may not have finished mission 1.
        self.assertIn(result.returncode, (0, 1))
        self.assertIn("1. function graph:", result.stdout)


def has_real_manim():
    # The repository itself contains a folder named "manim". Python may
    # recognize that as a namespace package even WITHOUT Manim installed.
    # A real Manim installation exports Scene; a namespace folder does not.
    try:
        from manim import Scene  # noqa: F401
    except ImportError:
        return False
    return True


class OptionalManimTests(unittest.TestCase):
    """Import Manim only when it is installed; do not render in every test."""

    @unittest.skipUnless(has_real_manim(), "Manim Community not installed")
    def test_scene_modules_import_with_real_manim(self):
        # A real-import smoke test; render with CLI as documented in README.
        import importlib.util
        import sys

        for filename, scene_name, _ in SCENES:
            with self.subTest(filename=filename):
                spec = importlib.util.spec_from_file_location(
                    f"mathlesson_{filename[:-3]}", ROOT / filename)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.assertTrue(hasattr(module, scene_name))


if __name__ == "__main__":
    unittest.main()
