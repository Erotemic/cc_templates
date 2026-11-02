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
from undercode.runtime import read_input, logical_mouse_position


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

    def test_mouse_press_maps_the_event_position_and_does_not_repeat(self):
        """A click uses event.pos and is a one-frame action rather than a held button."""
        viewport = pygame.Rect(100, 50, 480, 360)
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(180, 370)))
        first, _ = read_input(pygame=pygame, held=self.held, viewport=viewport)
        self.assertEqual(first.mouse_click, (160, 640))
        self.assertFalse(first.confirm_pressed)
        second, _ = read_input(pygame=pygame, held=self.held, viewport=viewport)
        self.assertIsNone(second.mouse_click)
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(180, 370)))
        right, _ = read_input(pygame=pygame, held=self.held, viewport=viewport)
        self.assertIsNone(right.mouse_click)

    def test_logical_coordinates_reject_letterbox_and_preserve_fractional_edges(self):
        """Input undoes the exact drawing viewport, including offsets and noninteger scale."""
        for viewport in (
            pygame.Rect(0, 0, 960, 720),
            pygame.Rect(180, 0, 960, 720),
            pygame.Rect(0, 100, 600, 450),
            pygame.Rect(0, 0, 1237, 928),
        ):
            with self.subTest(viewport=viewport):
                self.assertEqual(
                    logical_mouse_position(window_position=viewport.topleft, viewport=viewport),
                    (0, 0),
                )
                self.assertIsNone(
                    logical_mouse_position(
                        window_position=(viewport.right, viewport.centery), viewport=viewport
                    )
                )
                self.assertIsNone(
                    logical_mouse_position(
                        window_position=(viewport.x - 1, viewport.y), viewport=viewport
                    )
                )
                point = (viewport.x + 123, viewport.y + 217)
                logical = logical_mouse_position(window_position=point, viewport=viewport)
                self.assertAlmostEqual(logical[0], 123 * 960 / viewport.width)
                self.assertAlmostEqual(logical[1], 217 * 720 / viewport.height)

    def test_scaled_event_click_reaches_the_same_action_path_as_keyboard(self):
        """Exercise the event → logical coordinate → student function → encounter chain."""
        from unittest.mock import patch
        from teacher import solutions
        from undercode import student_encounters
        from undercode.app import Game
        from undercode.encounters.encounter import Phase
        from undercode.encounters.menu import main_buttons

        game = Game(encounter="folio")
        game.encounter.set_phase(phase=Phase.MENU)
        viewport = pygame.Rect(200, 50, 480, 360)
        act = main_buttons()[1].rect.center
        window_point = (viewport.x + act[0] / 2, viewport.y + act[1] / 2)
        with patch.object(student_encounters, "clicked_button", solutions.clicked_button):
            pygame.event.post(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=window_point)
            )
            controls, _ = read_input(pygame=pygame, held=self.held, viewport=viewport)
            game.update(seconds=0, controls=controls)
            self.assertEqual(game.encounter.phase, Phase.ACT)
            controls, _ = read_input(pygame=pygame, held=self.held, viewport=viewport)
            game.update(seconds=0, controls=controls)
            self.assertEqual(game.encounter.calm, 0)
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 50)))
            controls, _ = read_input(pygame=pygame, held=self.held, viewport=viewport)
            self.assertIsNone(controls.mouse_click)
            game.update(seconds=0, controls=controls)
            self.assertEqual(game.encounter.phase, Phase.ACT)


if __name__ == "__main__":
    unittest.main()
