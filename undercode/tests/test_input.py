"""Keyboard behavior is separate from rules; use real pygame events to check it."""

import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pygame
from undercode.runtime import read_input


class InputTests(unittest.TestCase):
    def setUp(self):
        """Use a tiny dummy display so pygame's event queue behaves like the classroom window."""
        pygame.display.init()
        pygame.display.set_mode((2, 2))
        pygame.event.clear()
        self.held = set()

    def tearDown(self):
        """Release the display; the render tests open their own separately."""
        pygame.display.quit()

    def test_holding_movement_does_not_repeat_menu_or_confirm_presses(self):
        for key in (pygame.K_RIGHT, pygame.K_z, pygame.K_LSHIFT):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
        first, _ = read_input(pygame=pygame, held=self.held)
        self.assertEqual(first.move_x, 1)
        self.assertEqual(first.menu_x, 1)
        self.assertTrue(first.confirm_pressed)
        self.assertTrue(first.sprint_held)
        next_frame, _ = read_input(pygame=pygame, held=self.held)
        self.assertEqual(next_frame.move_x, 1)
        self.assertEqual(next_frame.menu_x, 0)
        self.assertFalse(next_frame.confirm_pressed)
        self.assertTrue(next_frame.sprint_held)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z, repeat=True))
        repeated, _ = read_input(pygame=pygame, held=self.held)
        self.assertFalse(repeated.confirm_pressed)
        pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_RIGHT))
        released, _ = read_input(pygame=pygame, held=self.held)
        self.assertEqual(released.move_x, 0)

    def test_focus_loss_clears_held_keys_and_debug_is_a_window_command(self):
        self.held.add(pygame.K_RIGHT)
        pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F2))
        controls, commands = read_input(pygame=pygame, held=self.held)
        self.assertEqual(controls.move_x, 0)
        self.assertIn("unfocused", commands)
        self.assertIn("debug", commands)


if __name__ == "__main__":
    unittest.main()
