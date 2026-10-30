"""Real pygame tests, run in CI with SDL dummy video/audio drivers."""

from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from platformer import level, student


@unittest.skipUnless(importlib.util.find_spec("pygame"), "Install pygame-ce")
class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        import pygame
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        import pygame
        pygame.quit()

    def test_jump_land_and_key_mapping(self):
        import pygame
        from platformer.game import Game, JUMP_KEYS
        self.assertIn(pygame.K_x, JUMP_KEYS)
        self.assertIn(pygame.K_SPACE, JUMP_KEYS)
        game = Game()
        for _ in range(10):
            game.step(0, False, 1 / 60)
        self.assertTrue(game.player.on_ground)
        before = game.player.y
        game.step(0, True, 1 / 60)
        self.assertIn("jump", game.events)
        self.assertLess(game.player.y, before)
        for _ in range(90):
            game.step(0, False, 1 / 60)
        self.assertTrue(game.player.on_ground)

    @staticmethod
    def touch(game, rect):
        game.player.x = float(rect.x)
        game.player.y = float(rect.y)
        game.player.rect.topleft = rect.topleft
        game.step(0, False, 0.0)

    def test_levels_and_final_victory(self):
        from platformer.game import Game
        game = Game()
        # Mission 3 may add a fourth level. Mission 5 may delay transitions.
        # Test the underlying exit behavior with instant changes.
        with patch.object(student, "TRANSITION_SECONDS", 0.0), \
             patch.object(student, "update_boss", lambda *args: None):
            for index in range(len(level.LEVELS)):
                self.assertEqual(game.level_index, index)
                self.assertEqual(game.total_stars, len(level.locations("*", level.LEVELS[index])))
                for star in tuple(game.stars):
                    self.touch(game, star)
                    self.assertIn("star", game.events)
                self.assertEqual(game.collected, game.total_stars)
                if game.boss is not None:
                    game.boss.health = 0  # A completed boss mission can gate the door.
                self.touch(game, game.door)
                expected = "win" if index == len(level.LEVELS) - 1 else "level"
                self.assertIn(expected, game.events)
        self.assertTrue(game.won)
        game.restart()
        self.assertEqual(game.level_index, 0)
        self.assertFalse(game.won)

    def test_locked_door_does_not_advance(self):
        from platformer.game import Game
        game = Game()
        self.touch(game, game.door)
        self.assertEqual(game.level_index, 0)
        self.assertFalse(game.won)
        self.assertGreater(len(game.stars), 0)

    def test_restart_repeats_current_level(self):
        from platformer.game import Game
        game = Game()
        game.load_level(1)
        self.touch(game, game.stars[0])
        self.assertEqual(game.collected, 1)
        game.restart()
        self.assertEqual(game.level_index, 1)
        self.assertEqual(game.collected, 0)

    def test_student_hooks_receive_contact_and_frames(self):
        from platformer.game import Game
        game = Game()
        pad_calls = []
        enemy_calls = []

        def test_pad(player):
            pad_calls.append(player)
            player.vy = -850
            player.on_ground = False

        def test_enemy(enemy, seconds):
            enemy_calls.append(seconds)
            enemy.x += 1

        pad = game.pad
        game.player.x = float(pad.x + 3)
        game.player.y = float(pad.bottom - game.player.rect.height)
        game.player.rect.topleft = (round(game.player.x), round(game.player.y))
        game.player.on_ground = True
        with patch.object(student, "bounce_from_pad", test_pad), \
             patch.object(student, "move_enemy", test_enemy):
            game.step(0, False, 1 / 60)
        self.assertEqual(len(pad_calls), 1)
        self.assertIn("bounce", game.events)
        self.assertLess(game.player.vy, 0)
        self.assertEqual(len(enemy_calls), 1)

    def test_hero_reaction_and_expiring_speech(self):
        from platformer.game import Game
        game = Game()
        with patch.object(student, "hero_speech",
                          side_effect=lambda name, state: f"I got a {name}!"):
            self.touch(game, game.stars[0])
            self.assertEqual(game.speech_text, "I got a star!")
            self.assertGreater(game.speech_seconds, 0)
            game.player.x = 20
            game.player.y = 100
            game.player.rect.topleft = (20, 100)
            for _ in range(35):
                game.step(0, False, 0.05)
            self.assertEqual(game.speech_seconds, 0)
            self.touch(game, game.enemy.rect)
            self.assertEqual(game.speech_text, "I got a hurt!")

    def test_transition_hook_can_animate_before_loading(self):
        import pygame
        from platformer.game import Game
        game = Game()
        with patch.object(student, "TRANSITION_SECONDS", 0.12), \
             patch.object(student, "draw_transition") as draw_hook:
            for star in tuple(game.stars):
                self.touch(game, star)
            self.touch(game, game.door)
            self.assertEqual(game.level_index, 0)
            self.assertEqual(game.transition_to, 1)
            game.step(0, False, 0.05)
            game.draw(pygame.Surface((960, 600)))
            self.assertTrue(draw_hook.called)
            _, progress, name = draw_hook.call_args.args
            self.assertGreater(progress, 0)
            self.assertLess(progress, 1)
            self.assertEqual(name, level.LEVEL_NAMES[1])
            for _ in range(3):
                game.step(0, False, 0.05)
            self.assertEqual(game.level_index, 1)
            self.assertIsNone(game.transition_to)

    def test_boss_hook_and_exit_gate(self):
        from platformer.game import Game
        game = Game()
        game.load_level(2)
        self.assertIsNotNone(game.boss)
        game.boss.active = True
        for star in tuple(game.stars):
            self.touch(game, star)
        with patch.object(student, "update_boss", lambda *args: None):
            self.touch(game, game.door)
            self.assertFalse(game.won)
            self.assertEqual(game.level_index, 2)
            game.boss.health = 0
            self.touch(game, game.door)
            # If the student added a fourth level, the boss exits to it.
            self.assertTrue(game.won or game.level_index == 3)

    def test_zooms_and_keeps_hud_outside_camera(self):
        import pygame
        from platformer.game import Game
        game = Game()
        window = pygame.Surface((960, 600))
        with patch.object(student, "camera_view", return_value=(810, 420, 1.8)) as camera:
            game.draw(window)
        camera.assert_called_once_with(game.player)
        self.assertEqual(window.get_size(), (960, 600))

    def test_moving_platform_hook_carries_player(self):
        from platformer.game import Game
        game = Game()
        game.load_level(1)
        self.assertEqual(len(game.ledges), 1)
        ledge = game.ledges[0]
        game.player.x = ledge.x + 25
        game.player.y = ledge.y - game.player.rect.height
        game.player.rect.topleft = (round(game.player.x), round(game.player.y))
        game.player.on_ground = True
        old_x = game.player.x
        def move(ledge, seconds):
            ledge.x += 30 * seconds
        with patch.object(student, "move_platform", move):
            game.step(0, False, 0.02)
        self.assertGreater(game.player.x, old_x)
        self.assertTrue(game.player.on_ground)

    def test_switch_hook_can_reveal_one_star(self):
        from platformer.game import Game
        game = Game()
        game.load_level(1)
        self.assertIsNotNone(game.switch)
        original = game.total_stars
        def toggle(game):
            if not game.switch_pressed:
                game.switch_pressed = True
                game.stars.append(game.bonus_star)
                game.total_stars += 1
        with patch.object(student, "activate_switch", toggle):
            self.touch(game, game.switch)
            self.touch(game, game.switch)
        self.assertTrue(game.switch_pressed)
        self.assertEqual(game.total_stars, original + 1)

    def test_second_jump_hook_can_launch_in_air(self):
        from platformer.game import Game
        game = Game()
        game.player.on_ground = False
        game.player.vy = 25
        def extra_jump(player, pressed):
            if pressed:
                player.vy = -400
                return True
            return False
        with patch.object(student, "try_double_jump", extra_jump):
            game.step(0, True, 1 / 60)
        self.assertLess(game.player.vy, 0)
        self.assertIn("jump", game.events)

    def test_graphical_smoke_and_screenshot(self):
        from platformer.game import main
        with tempfile.TemporaryDirectory() as tempdir:
            image = Path(tempdir) / "frame.png"
            self.assertEqual(main(["--frames", "3", "--screenshot", str(image)]), 0)
            self.assertTrue(image.exists())
            self.assertGreater(image.stat().st_size, 2500)


if __name__ == "__main__":
    unittest.main()
