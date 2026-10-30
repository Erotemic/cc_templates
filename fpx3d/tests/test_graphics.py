"""Optional real Panda3D smoke test; run with a display or Xvfb.

The unit suite remains useful on school machines with no Panda3D installed.
Set FPX3D_GRAPHICS_TEST=1 to request actual scene creation and rendering.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec('panda3d') is not None,
                     'Panda3D is not installed')
class WindowPropertiesTests(unittest.TestCase):
    def test_window_configuration_uses_supported_panda3d_api(self):
        """Catch WindowProperties typos even without opening a 3D window.

        Panda3D exposes setFixedSize(False), not setResizable(True).
        Unlike the screenshot test, this runs whenever Panda3D is installed.
        """
        from fpx3d.game import PrismVault
        from fpx3d import student

        hidden = PrismVault._window_properties(hidden=True)
        self.assertTrue(hidden.getCursorHidden())
        self.assertFalse(hidden.getFixedSize())
        self.assertEqual(hidden.getTitle(), student.YOUR_VAULT_NAME)

        visible = PrismVault._window_properties(hidden=False)
        self.assertFalse(visible.getCursorHidden())
        self.assertFalse(visible.getFixedSize())


@unittest.skipUnless(os.environ.get('FPX3D_GRAPHICS_TEST') == '1',
                     'Opt-in graphical test: set FPX3D_GRAPHICS_TEST=1')
@unittest.skipUnless(importlib.util.find_spec('panda3d') is not None,
                     'Panda3D is not installed')
class RenderSmokeTests(unittest.TestCase):
    def test_real_window_and_screenshot(self):
        with tempfile.TemporaryDirectory() as dirname:
            screenshot = Path(dirname) / 'vault.png'
            result = subprocess.run(
                [sys.executable, 'main.py', '--frames', '8',
                 '--screenshot', str(screenshot)],
                cwd=ROOT, capture_output=True, text=True, timeout=75,
            )
            self.assertEqual(result.returncode, 0,
                             result.stdout + '\n' + result.stderr)
            self.assertTrue(screenshot.is_file(), result.stdout + result.stderr)
            self.assertGreater(screenshot.stat().st_size, 1600)
            self.assertEqual(screenshot.read_bytes()[:8], b'\x89PNG\r\n\x1a\n')


if __name__ == '__main__':
    unittest.main()
