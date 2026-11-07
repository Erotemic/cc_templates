"""The headless mode must run without pygame installed."""

import subprocess
import sys
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def test_headless_launch(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "main.py", "--headless", "--frames", "12"],
                                cwd=root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("room=trailhead frames=12", result.stdout)


if __name__ == "__main__":
    unittest.main()
