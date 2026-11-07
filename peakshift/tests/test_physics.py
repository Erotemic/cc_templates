"""Core moves must work in the unsolved student starter."""

import unittest
from unittest.mock import patch

from peakshift import levels, settings, student
from peakshift.physics import Controls, Game, Player, update

DT = 1 / 60


def step(game, frames, controls=None):
    for _ in range(frames):
        update(game, controls or Controls(), DT)


class CoreMovementTests(unittest.TestCase):
    def test_spawn_and_gravity_are_grounded(self):
        game = Game()
        step(game, 10)
        self.assertTrue(game.player.on_ground)
        self.assertAlmostEqual(game.player.bottom, 14 * settings.TILE)

    def test_movement_and_friction(self):
        game = Game()
        step(game, 20, Controls(right=True))
        self.assertGreater(game.player.x, 110)
        before = game.player.x
        step(game, 20)
        self.assertGreater(game.player.x, before)
        self.assertAlmostEqual(game.player.vx, 0)

    def test_jump_cuts_shorter_than_holding(self):
        def height(hold):
            game = Game()
            step(game, 2)
            initial = game.player.y
            for i in range(32):
                update(game, Controls(jump_pressed=i == 0,
                                      jump_held=i < hold), DT)
            return initial - game.player.y
        self.assertGreater(height(32), height(2) + 35)

    def test_one_air_dash_until_landing(self):
        game = Game()
        step(game, 2)
        update(game, Controls(jump_pressed=True, jump_held=True), DT)
        update(game, Controls(right=True, dash_pressed=True, jump_held=True), DT)
        self.assertEqual(game.player.dashes, 0)
        self.assertGreater(game.player.vx, settings.RUN_SPEED)
        step(game, 10, Controls(right=True, jump_held=True))
        self.assertEqual(game.player.dashes, 0)
        step(game, 110)
        self.assertEqual(game.player.dashes, 1)

    def test_dash_diagonal_is_normalized(self):
        game = Game()
        step(game, 1)
        update(game, Controls(right=True, up=True, dash_pressed=True), 1 / 120)
        self.assertAlmostEqual((game.player.vx ** 2 + game.player.vy ** 2) ** .5,
                               settings.DASH_SPEED, delta=1)

    def test_wall_slide_and_wall_jump(self):
        game = Game()
        # A rock wall at column zero in Switchbacks is solid from the side.
        game.load_room("switchbacks")
        game.player = Player(x=32, y=345,
                             vy=370, on_ground=False)
        update(game, Controls(left=True), DT)
        self.assertEqual(game.player.wall_side, -1)
        step(game, 6, Controls(left=True))
        self.assertLessEqual(game.player.vy, settings.WALL_SLIDE + 1)
        update(game, Controls(left=True, jump_pressed=True, jump_held=True), DT)
        self.assertLess(game.player.vy, 0)
        self.assertGreater(game.player.vx, 0)

    def test_spikes_respawn_without_ending_campaign(self):
        game = Game()
        game.player.x = 9 * 32 + 7
        game.player.y = 13 * 32 + 2
        step(game, 1)
        self.assertEqual(game.deaths, 1)
        self.assertEqual(game.room_key, "trailhead")
        self.assertEqual((game.player.x, game.player.y), game.checkpoint)

    def test_checkpoint_used_on_death(self):
        game = Game(start="ridge")
        # Simulate reaching the checkpoint flag on the crumbling ledge.
        game.player.x = 9 * 32 + 6
        game.player.y = 9 * 32 + 5
        step(game, 1)
        self.assertNotEqual(game.checkpoint, (2 * 32 + 6, 14 * 32 - 26))
        saved = game.checkpoint
        game.player.y = settings.HEIGHT + 100
        step(game, 1)
        self.assertEqual((game.player.x, game.player.y), saved)

    def test_coyote_time_allows_late_jump(self):
        game = Game()
        game.player.y = 300
        game.player.on_ground = False
        game.player.coyote = .06
        update(game, Controls(jump_pressed=True, jump_held=True), DT)
        self.assertLess(game.player.vy, -settings.JUMP_SPEED + 50)

    def test_jump_buffer_fires_on_landing(self):
        game = Game()
        game.player.y = 14 * settings.TILE - settings.PLAYER_H - 5
        game.player.on_ground = False
        game.player.vy = 260
        update(game, Controls(jump_pressed=True, jump_held=True), DT)
        step(game, 5, Controls(jump_held=True))
        self.assertLess(game.player.vy, 0)
        self.assertFalse(game.player.on_ground)

    def test_authored_course_is_playable_without_solving_student_missions(self):
        """Recorded, deterministic keyboard routes from all four default spawns.

        Verify room geometry is attainable with only the baseline moves.
        These are smoke routes, not a level-quality substitute for playtesting.
        """
        routes = (
            ("trailhead", {48}, set()),
            ("switchbacks", {17, 60, 112}, set()),
            ("divide", {51}, {69}),
            ("ridge", {10, 46, 82, 124}, set()),
        )
        for key, jump_frames, dash_frames in routes:
            with self.subTest(room=key):
                game = Game(start=key)
                for i in range(290):
                    update(game, Controls(
                        right=True, jump_pressed=i in jump_frames,
                        jump_held=any(frame <= i < frame + 25 for frame in jump_frames),
                        dash_pressed=i in dash_frames), DT)
                    if game.finished or game.room_key != key or game.deaths:
                        break
                self.assertEqual(game.deaths, 0, f"{key}: route hit a hazard")
                self.assertTrue(game.finished or game.room_key != key,
                                f"{key}: could not reach the exit")

    def test_goal_advances_and_last_room_wins(self):
        game = Game()
        for room in ("trailhead", "switchbacks", "divide", "ridge"):
            self.assertEqual(game.room_key, room)
            col, row = levels.find(game.room.tiles, "G")[0]
            game.player.x = col * 32 + 5
            game.player.y = row * 32 + 5
            step(game, 1)
        self.assertTrue(game.finished)
        game.restart()
        self.assertEqual(game.room_key, "trailhead")
        self.assertFalse(game.finished)


class StudentMissionIntegrationTests(unittest.TestCase):
    def test_berry_score_hook_is_used_once(self):
        game = Game()
        with patch.object(student, "collect_berry", side_effect=lambda g: setattr(g, "berries", g.berries + 1)) as hook:
            game.player.x = 5 * 32 + 4
            game.player.y = 12 * 32 + 2
            step(game, 3)
        self.assertEqual(hook.call_count, 1)
        self.assertEqual(game.berries, 1)

    def test_crystal_hook_is_used(self):
        game = Game(start="divide")
        game.player.dashes = 0
        game.player.x = 5 * 32 + 5
        game.player.y = 12 * 32 + 5
        with patch.object(student, "refill_dash_from_crystal", side_effect=lambda p: setattr(p, "dashes", 1) or True):
            step(game, 1)
        self.assertEqual(game.player.dashes, 1)
        self.assertEqual(len(game.used_crystals), 1)

    def test_moving_platform_hook_and_carry(self):
        game = Game(start="divide")
        platform = game.platforms[0]
        game.player = Player(x=platform.x + 16, y=platform.y - settings.PLAYER_H,
                             on_ground=True, ground_platform=platform)
        previous = game.player.x
        def move(platform, seconds):
            platform.x += 72 * seconds
        with patch.object(student, "move_platform", move):
            step(game, 4)
        self.assertGreater(game.player.x, previous + 2)
        self.assertTrue(game.player.on_ground)

    def test_crumble_hook_removes_tile_collision(self):
        game = Game(start="ridge")
        block = next(iter(game.blocks.values()))
        original = block.rect
        game.player = Player(x=original.x + 5, y=original.y - settings.PLAYER_H,
                             on_ground=True)
        def break_tile(block, dt, standing):
            if standing:
                block.timer += dt
                if block.timer > .1:
                    block.broken = True
        with patch.object(student, "update_crumble", break_tile):
            step(game, 15)
        self.assertTrue(block.broken)

    def test_wind_hook_affects_horizontal_motion(self):
        game = Game(start="ridge")
        game.player = Player(x=17 * 32 + 5, y=7 * 32 + 5)
        with patch.object(student, "wind_acceleration", lambda p, inside: 720 if inside else 0):
            step(game, 1)
        self.assertGreater(game.player.vx, 0)

    def test_timer_hook_is_used(self):
        game = Game()
        with patch.object(student, "record_time", lambda g, seconds: setattr(g, "elapsed", g.elapsed + seconds)):
            step(game, 60)
        self.assertAlmostEqual(game.elapsed, 1.0, delta=0.01)


if __name__ == "__main__":
    unittest.main()
