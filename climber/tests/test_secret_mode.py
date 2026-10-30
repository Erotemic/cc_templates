"""Check the optional hidden keyboard input without needing pygame."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from climber import settings
from climber.engine import Controls, Game, Player, update
from climber.game import _advance_sequence, _handle_sequence_key, _secret_keys


# Numeric keycodes are used here so input matching stays testable without SDL.
SEQUENCE = (1, 1, 2, 2, 3, 4, 3, 4, 5, 6, 7, 8)


class KeyboardSequenceTests(unittest.TestCase):
    def test_actual_keyboard_binding_has_requested_order(self):
        fake_pygame = SimpleNamespace(K_UP=1, K_DOWN=2, K_LEFT=3,
                                      K_RIGHT=4, K_b=5, K_a=6,
                                      K_SPACE=7, K_RETURN=8)
        self.assertEqual(_secret_keys(fake_pygame), SEQUENCE)

    def test_full_sequence_toggles_power_and_can_toggle_back(self):
        game = Game()
        progress = 0
        for index, key in enumerate(SEQUENCE):
            progress = _handle_sequence_key(game, SEQUENCE, progress, key)
            if index < len(SEQUENCE) - 1:
                self.assertFalse(game.super_mode)
        self.assertEqual(progress, 0)
        self.assertTrue(game.super_mode)

        for key in SEQUENCE:
            progress = _handle_sequence_key(game, SEQUENCE, progress, key)
        self.assertFalse(game.super_mode)
        self.assertEqual(progress, 0)

    def test_wrong_key_does_not_unlock_and_progress_recovers(self):
        game = Game()
        progress = 0
        for key in SEQUENCE[:5] + (999,) + SEQUENCE[5:]:
            progress = _handle_sequence_key(game, SEQUENCE, progress, key)
        self.assertFalse(game.super_mode)
        for key in SEQUENCE:
            progress = _handle_sequence_key(game, SEQUENCE, progress, key)
        self.assertTrue(game.super_mode)

    def test_overlapping_start_does_not_lose_a_valid_sequence(self):
        # The third '1' should count as a fresh start of the two-key prefix.
        progress = 0
        matches = []
        for key in (1,) + SEQUENCE:
            progress, matched = _advance_sequence(SEQUENCE, progress, key)
            matches.append(matched)
        self.assertEqual(sum(matches), 1)
        self.assertEqual(progress, 0)


class SuperModePhysicsTests(unittest.TestCase):
    def test_super_mode_jumps_repeatedly_in_midair(self):
        game = Game(super_mode=True)
        game.player = Player(x=466, y=250, vy=400, on_ground=False)
        for _ in range(6):
            old_y = game.player.y
            update(game, Controls(jump_pressed=True), 1 / 60)
            self.assertLess(game.player.y, old_y)
            self.assertAlmostEqual(game.player.vy,
                                   -settings.JUMP_SPEED + settings.GRAVITY / 60)
        self.assertIn("jump", game.events)

    def test_normal_airborne_player_cannot_rejump(self):
        game = Game()
        game.player = Player(x=466, y=250, vy=400, on_ground=False)
        update(game, Controls(jump_pressed=True), 1 / 60)
        self.assertGreater(game.player.vy, 0)
        self.assertNotIn("jump", game.events)

    def test_super_mode_ignores_enemy_contact(self):
        game = Game(super_mode=True)
        game.camera_y = -190
        enemy = next(e for e in game.nearby_enemies() if e.tier == 6)
        game.player = Player(x=enemy.x, y=enemy.y, on_ground=False)
        update(game, Controls(), 0.0)
        self.assertEqual(game.hearts, 3)
        self.assertEqual(game.failures, 0)
        self.assertNotIn("hurt", game.events)

    def test_super_mode_survives_the_danger_floor_and_restart(self):
        game = Game(super_mode=True)
        game.hazard_y = game.player.bottom - 5
        update(game, Controls(), 1 / 60)
        self.assertEqual(game.failures, 0)
        game.reset()
        self.assertTrue(game.super_mode)
        self.assertEqual(game.failures, 1)


class SuperModeRenderingTests(unittest.TestCase):
    def test_glow_appears_only_in_super_mode(self):
        import importlib.util
        if importlib.util.find_spec("pygame") is None:
            self.skipTest("Install pygame-ce for visual rendering tests")

        import os
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        import pygame
        from climber.art import Painter

        pygame.init()
        try:
            painter = Painter()
            game = Game()
            cx = round(game.player.x + settings.PLAYER_WIDTH / 2)
            cy = round(game.player.y - game.camera_y
                       + settings.PLAYER_HEIGHT / 2)
            sample = (cx + 40, cy)
            painter.scene.fill((0, 0, 0))
            painter._draw_player(game)
            normal = painter.scene.get_at(sample)
            game.super_mode = True
            painter.scene.fill((0, 0, 0))
            painter._draw_player(game)
            powered = painter.scene.get_at(sample)
            self.assertNotEqual(normal, powered)

            # The effect is attached to world/player coordinates, not the HUD.
            game.player.x += 70
            painter.scene.fill((0, 0, 0))
            painter._draw_player(game)
            self.assertNotEqual(powered, painter.scene.get_at(sample))
        finally:
            pygame.quit()


if __name__ == "__main__":
    unittest.main()
