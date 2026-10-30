"""Starter regression tests: should remain valid after students add features."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from climber import settings, student, world
from climber.engine import Controls, Game, Heckler, Pickup, Player, update


class TowerTests(unittest.TestCase):
    def test_tower_is_deterministic(self):
        self.assertEqual(world.main_platform(420), world.main_platform(420))
        with patch.object(student, "TOWER_SEED", student.TOWER_SEED + 1):
            other = world.main_platform(420)
        self.assertNotEqual(world.main_platform(420).x, other.x)

    def test_every_tier_reachable_by_normal_jump(self):
        jump_height = settings.JUMP_SPEED ** 2 / (2 * settings.GRAVITY)
        self.assertGreater(jump_height, settings.TIER_HEIGHT + 35)
        for tier in range(1, 2001):
            first = world.main_platform(tier)
            second = world.main_platform(tier + 1)
            # Mission 6 changes the 100px baseline. Require a reachable
            # vertical gap rather than insisting the student keep the stub.
            self.assertGreater(first.y - second.y, 45)
            self.assertLess(first.y - second.y, jump_height - 8)
            self.assertLess(abs(world.platform_center(tier + 1)
                                - world.platform_center(tier)), 110)
            self.assertGreater(first.x, settings.LEFT_WALL)
            self.assertLess(first.right, settings.RIGHT_WALL)

    def test_window_does_not_make_more_tiers(self):
        near_bottom = world.platforms_near(100, 700)
        very_high = world.platforms_near(-10_000_000, -10_000_000 + 600)
        self.assertLess(len(near_bottom), 20)
        self.assertLess(len(very_high), 20)
        self.assertTrue(all(p.y < -9_999_000 for p in very_high))

    def test_streaming_enemies_stay_bounded(self):
        game = Game()
        for tier in range(1, 1000, 7):
            game.camera_y = settings.GROUND_Y - tier * settings.TIER_HEIGHT
            game.nearby_enemies()
            self.assertLessEqual(len(game.enemies), 4)

    def test_streaming_pickups_stay_bounded(self):
        game = Game()
        for tier in range(1, 1000, 9):
            game.camera_y = settings.GROUND_Y - tier * settings.TIER_HEIGHT
            game.nearby_pickups()
            self.assertLessEqual(len(game.pickups), 4)

    def test_hud_is_below_gameplay_not_over_ground(self):
        width, height = settings.START_WINDOW_SIZE
        self.assertEqual(width, settings.VIEW_WIDTH)
        self.assertEqual(height,
                         settings.VIEW_HEIGHT + settings.HUD_HEIGHT)

    def test_ladder_joins_main_platforms(self):
        for tier in range(1, 100):
            ladder = world.ladder_to(tier)
            lower = (world.main_platform(tier - 1) if tier > 1 else None)
            lower_y = lower.y if lower else settings.GROUND_Y
            self.assertLess(ladder.top, ladder.bottom)
            self.assertGreater(ladder.bottom, lower_y)
            self.assertLess(ladder.top, world.main_platform(tier).y)

    def test_pickups_are_placed_on_some_tiers(self):
        seen = [world.pickup_for_tier(tier) for tier in range(1, 40)]
        seen = [pickup for pickup in seen if pickup is not None]
        self.assertGreaterEqual(len(seen), 6)
        self.assertTrue(all(settings.LEFT_WALL < pickup.x < settings.RIGHT_WALL
                            for pickup in seen))


class PhysicsTests(unittest.TestCase):
    def test_player_can_jump_and_land_one_tier_higher(self):
        game = Game()
        first = world.main_platform(1)
        game.player.x = first.x + 30
        initial_y = game.player.y
        update(game, Controls(jump_pressed=True), 1 / 60)
        self.assertLess(game.player.y, initial_y)
        for _ in range(90):
            update(game, Controls(), 1 / 60)
        self.assertTrue(game.player.on_ground)
        self.assertAlmostEqual(game.player.bottom, first.y)

    def test_player_cannot_leave_tower(self):
        game = Game()
        game.player.x = settings.LEFT_WALL
        update(game, Controls(left=True), 1 / 60)
        self.assertEqual(game.player.x, settings.LEFT_WALL)
        self.assertEqual(game.player.wall_side, -1)
        game.player.x = settings.RIGHT_WALL - settings.PLAYER_WIDTH
        update(game, Controls(right=True), 1 / 60)
        self.assertEqual(game.player.right, settings.RIGHT_WALL)
        self.assertEqual(game.player.wall_side, +1)

    def test_camera_tracks_ascent_and_falling(self):
        game = Game()
        game.player.y = -1200
        update(game, Controls(), 0.0)
        self.assertAlmostEqual(game.player.y - game.camera_y, 210)
        self.assertGreater(game.highest_tier, 10)
        game.player.y += 500
        update(game, Controls(), 0.0)
        self.assertAlmostEqual(game.player.y - game.camera_y,
                               settings.VIEW_HEIGHT - 105)

    def test_ladder_student_hook_is_connected(self):
        game = Game()
        ladder = world.ladder_to(1)
        game.player.x = ladder.x
        previous_y = game.player.y

        def learn_ladder(player, controls, touching):
            player.climbing = touching and controls.up

        with patch.object(student, "update_ladder_state", learn_ladder):
            update(game, Controls(up=True), 1 / 60)
        self.assertTrue(game.player.climbing)
        self.assertLess(game.player.y, previous_y)

    def test_wall_jump_student_hook_is_connected(self):
        game = Game()
        game.player.on_ground = False
        game.player.wall_side = -1
        game.player.x = settings.LEFT_WALL

        def learn_wall_jump(player, pressed):
            if pressed and player.wall_side:
                player.vy = -settings.JUMP_SPEED
                return True
            return False

        with patch.object(student, "try_wall_jump", learn_wall_jump):
            update(game, Controls(jump_pressed=True), 1 / 60)
        self.assertLess(game.player.vy, 0)
        self.assertGreater(game.player.wall_push_time, 0)

    def test_enemy_student_hook_is_connected(self):
        game = Game()
        game.player = Player(x=466, y=125, on_ground=False)
        game.camera_y = -190
        enemy = next(e for e in game.nearby_enemies() if e.tier == 6)
        before = enemy.x

        def learn_patrol(enemy, seconds):
            enemy.x += enemy.direction * enemy.speed * seconds

        with patch.object(student, "move_enemy", learn_patrol):
            update(game, Controls(), 1 / 60)
        self.assertGreater(enemy.x, before)

    def test_rising_floor_student_hook_is_connected(self):
        game = Game()

        def learn_rising_floor(game, seconds):
            game.hazard_y -= 20 * seconds

        initial = game.hazard_y
        with patch.object(student, "move_rising_floor", learn_rising_floor):
            update(game, Controls(), 1 / 60)
        self.assertLess(game.hazard_y, initial)

    def test_pickup_student_hook_is_connected(self):
        game = Game()
        game.player = Player(x=485, y=410, on_ground=False)
        game.camera_y = 120
        pickup = next(p for p in game.nearby_pickups() if p.tier == 3)
        game.player.x = pickup.x
        game.player.y = pickup.y - 10

        def learn_pickup(game, pickup):
            pickup.collected = True
            game.pickups_collected += 1

        with patch.object(student, "collect_pickup", learn_pickup):
            update(game, Controls(), 1 / 60)
        self.assertTrue(pickup.collected)
        self.assertEqual(game.pickups_collected, 1)
        self.assertIn("pickup", game.events)

    def test_heckler_tracks_upward_but_not_falls(self):
        game = Game(heckler=Heckler())
        start_y = game.heckler.y
        game.player.y = start_y - 50
        update(game, Controls(), 1 / 60)
        climbed_y = game.heckler.y
        self.assertLess(climbed_y, start_y)
        game.player.y = min(settings.GROUND_Y - settings.PLAYER_HEIGHT - 5, climbed_y + 120)
        update(game, Controls(), 0.0)
        self.assertEqual(game.heckler.y, climbed_y)

    def test_danger_resets_player(self):
        game = Game()
        game.hazard_y = settings.GROUND_Y - 1
        update(game, Controls(), 1 / 60)
        self.assertEqual(game.failures, 1)
        self.assertEqual(game.player.y,
                         settings.GROUND_Y - settings.PLAYER_HEIGHT)

    def test_headless_starts_without_pygame(self):
        project = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(project / "main.py"),
             "--headless", "--frames", "240"],
            capture_output=True, text=True, cwd=project, check=True,
        )
        self.assertIn("frames=240", result.stdout)


class HecklerDialogueTests(unittest.TestCase):
    def test_typewriter_mumbles_then_vanishes_and_does_not_repeat(self):
        game = Game()
        update(game, Controls(), 1 / 60)
        self.assertEqual(game.heckler.text, "I ride. You climb.")
        self.assertEqual(game.heckler.revealed, 1)
        self.assertIn("heckler_mumble_1", game.events)

        saw_later_blip = False
        for _ in range(90):
            update(game, Controls(), 1 / 60)
            saw_later_blip |= any(event.startswith("heckler_mumble_")
                                  for event in game.events)
        self.assertTrue(saw_later_blip)
        self.assertEqual(game.heckler.revealed, len(game.heckler.text))
        self.assertNotEqual(game.heckler.text, "")

        for _ in range(150):
            update(game, Controls(), 1 / 60)
        self.assertEqual(game.heckler.text, "")
        self.assertEqual(game.heckler.revealed, 0)
        for _ in range(240):
            update(game, Controls(), 1 / 60)
            self.assertEqual(game.heckler.text, "")
            self.assertFalse(any(event.startswith("heckler_mumble_")
                                 for event in game.events))

    def test_new_milestone_starts_different_line(self):
        game = Game()
        update(game, Controls(), 1 / 60)
        for _ in range(245):
            update(game, Controls(), 1 / 60)
        self.assertEqual(game.heckler.text, "")
        game.highest_tier = 10
        update(game, Controls(), 1 / 60)
        self.assertIn("Only ALL of them", game.heckler.text)
        self.assertEqual(game.heckler.revealed, 1)

    def test_unimplemented_hook_does_not_arm_a_fall_or_speak(self):
        """Mission 8 must really be left for the student."""
        game = Game()
        with patch.object(student, "heckler_line", lambda *_: ""):
            game.player.y = 100
            update(game, Controls(), 0.0)
            game.heckler.y = game.player.y - settings.HECKLER_OFFSET
            game.player.y += 190
            update(game, Controls(), 0.0)
            self.assertFalse(game.comeback_pending)
            self.assertEqual(game.fall_count, 0)
            self.assertEqual(game.heckler.text, "")
            game.player.y = 120
            update(game, Controls(), 0.0)
            self.assertFalse(game.comeback_pending)
            self.assertEqual(game.heckler.text, "")

    def test_hook_receives_fall_and_later_return_frames(self):
        """The student must see each frame, not just when speech is idle."""
        game = Game()
        frames_seen = []

        def observe(game, heckler):
            frames_seen.append(game.player.y)
            return None

        with patch.object(student, "update_heckler_comeback", observe), \
             patch.object(student, "heckler_line", lambda *_: ""):
            game.player.y = 100
            update(game, Controls(), 0.0)
            game.player.y = 290
            update(game, Controls(), 0.0)
            game.player.y = 120
            update(game, Controls(), 0.0)

        self.assertEqual(frames_seen, [100, 290, 120])

    def test_student_event_can_trigger_the_speech_system(self):
        game = Game()
        with patch.object(student, "heckler_line", lambda *_: ""), \
             patch.object(student, "update_heckler_comeback",
                          side_effect=[None, None, "You came back!", None]):
            game.player.y = 100
            update(game, Controls(), 0.0)
            game.player.y = 290
            update(game, Controls(), 0.0)
            self.assertEqual(game.heckler.text, "")
            game.player.y = 120
            update(game, Controls(), 0.0)
            self.assertEqual(game.heckler.text, "You came back!")
            self.assertEqual(game.heckler.revealed, 1)
            update(game, Controls(), 0.0)
            self.assertEqual(game.heckler.text, "You came back!")

    def test_student_event_waits_for_current_speech(self):
        game = Game()
        update(game, Controls(), 1 / 60)
        self.assertEqual(game.heckler.text, "I ride. You climb.")

        sent = False
        def student_event(game, heckler):
            nonlocal sent
            if not sent:
                sent = True
                return "Look who made it back."
            return None

        with patch.object(student, "update_heckler_comeback", student_event):
            update(game, Controls(), 1 / 60)
            self.assertEqual(game.heckler.text, "I ride. You climb.")
            self.assertEqual(game.heckler.queued_comeback,
                             "Look who made it back.")
            for _ in range(450):
                update(game, Controls(), 1 / 60)
                if game.heckler.text == "Look who made it back.":
                    break
            else:
                self.fail("Queued comeback never started after existing line")

            self.assertEqual(game.heckler.queued_comeback, "")
            self.assertEqual(game.heckler.revealed, 1)

    def test_restart_clears_student_memory(self):
        game = Game()
        game.peak_player_y = 100
        game.comeback_peak_y = 100
        game.comeback_pending = True
        game.fall_count = 2
        game.heckler.queued_comeback = "Old comeback"
        game.reset()
        self.assertEqual(game.peak_player_y, game.player.y)
        self.assertEqual(game.comeback_peak_y, game.player.y)
        self.assertFalse(game.comeback_pending)
        self.assertEqual(game.fall_count, 0)
        self.assertEqual(game.heckler.queued_comeback, "")


class GraphicSmokeTests(unittest.TestCase):
    def test_graphical_startup_and_resize(self):
        import importlib.util
        if importlib.util.find_spec("pygame") is None:
            self.skipTest("Install pygame-ce to test graphical rendering")
        import os
        import tempfile
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
        import pygame
        from climber.art import Painter
        from climber.game import run_graphical

        with tempfile.TemporaryDirectory() as directory:
            screenshot = Path(directory) / "frame.png"
            self.assertEqual(run_graphical(frames=3, screenshot=str(screenshot)), 0)
            self.assertTrue(screenshot.is_file())
            self.assertGreater(screenshot.stat().st_size, 2000)

        pygame.init()
        try:
            window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
            painter = Painter()
            game = Game()
            painter.draw(game, window, 1 / 60)
            self.assertEqual(window.get_size(), (1280, 720))

            # A bubble stays anchored to the heckler's world position.
            game.heckler.text = "Short taunt."
            game.heckler.revealed = 5
            first, _ = painter._heckler_bubble_layout(game)
            game.heckler.y -= 40
            second, _ = painter._heckler_bubble_layout(game)
            self.assertEqual(second.centery, first.centery - 40)
            game.camera_y -= 20
            third, _ = painter._heckler_bubble_layout(game)
            self.assertEqual(third.centery, second.centery + 20)
            game.heckler.text = ""
            self.assertIsNone(painter._heckler_bubble_layout(game))
        finally:
            pygame.quit()


if __name__ == "__main__":
    unittest.main()
