"""Core moves must work in the unsolved student starter."""

import unittest
from unittest.mock import patch

from peakshift import levels, settings, student
from peakshift.physics import Controls, Game, Player, update
from peakshift.art import camera_top

DT = 1 / 60


def step(game, frames, controls=None):
    for _ in range(frames):
        update(game, controls or Controls(), DT)


class CoreMovementTests(unittest.TestCase):
    def test_spawn_and_gravity_are_grounded(self):
        game = Game()
        step(game, 10)
        self.assertTrue(game.player.on_ground)
        self.assertAlmostEqual(game.player.bottom, 18 * settings.TILE)

    def test_movement_and_friction(self):
        game = Game()
        step(game, 15, Controls(right=True))
        self.assertGreater(game.player.x, 110)
        before = game.player.x
        step(game, 10)
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
        # Test movement separately from authored hazards and chasms.
        tiles = ["." * settings.COLS for _ in range(20)]
        tiles[17] = "..P...................G."
        tiles[18] = "#" * settings.COLS
        flat = levels.Room("Movement Test", tuple(tiles), "", None)
        game = Game({"flat": flat}, "flat")
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
        # A wall is a continuous face: climb and jump away from either side.
        game.load_room("switchbacks")
        game.player = Player(x=364, y=700, vy=370, on_ground=False)
        update(game, Controls(right=True), DT)
        self.assertEqual(game.player.wall_side, 1)
        step(game, 6, Controls(right=True))
        self.assertLessEqual(game.player.vy, settings.WALL_SLIDE + 1)
        update(game, Controls(right=True, jump_pressed=True, jump_held=True), DT)
        self.assertLess(game.player.vy, 0)
        self.assertLess(game.player.vx, 0)

    def test_spikes_respawn_without_ending_campaign(self):
        game = Game()
        col, row = levels.find(game.room.tiles, "^")[0]
        game.player.x = col * 32 + 7
        game.player.y = row * 32 + 2
        step(game, 1)
        self.assertEqual(game.deaths, 1)
        self.assertEqual(game.room_key, "trailhead")
        self.assertEqual((game.player.x, game.player.y), game.checkpoint)

    def test_checkpoint_used_on_death(self):
        game = Game(start="ridge")
        # The first checkpoint is directly above the first tower.
        col, row = levels.find(game.room.tiles, "C")[0]
        game.player.x = col * 32 + 6
        game.player.y = row * 32 + 5
        step(game, 1)
        self.assertNotEqual(game.checkpoint, (2 * 32 + 6, 28 * 32 - 26))
        saved = game.checkpoint
        game.player.y = game.world_height + settings.CAMERA_OVERSCROLL + 100
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
        game.player.y = 18 * settings.TILE - settings.PLAYER_H - 5
        game.player.on_ground = False
        game.player.vy = 260
        update(game, Controls(jump_pressed=True, jump_held=True), DT)
        step(game, 5, Controls(jump_held=True))
        self.assertLess(game.player.vy, 0)
        self.assertFalse(game.player.on_ground)

    def test_cliff_grip_climbs_and_exhausts_stamina(self):
        game = Game(start="switchbacks")
        game.player = Player(x=364, y=715, wall_side=1)
        start_y = game.player.y
        step(game, 50, Controls(right=True, up=True, grab_held=True))
        self.assertLess(game.player.y, start_y - 75)
        self.assertLess(game.player.grip_left, 1.0)
        step(game, 100, Controls(right=True, up=True, grab_held=True))
        self.assertFalse(game.player.grabbing)
        self.assertEqual(game.player.grip_left, 0)

    def test_bottomless_gap_causes_a_real_fall_and_respawn(self):
        game = Game(start="divide")
        # x=7 is suspended above the gorge with no floor under the player.
        game.player = Player(x=7 * 32 + 4, y=20 * 32 - settings.PLAYER_H)
        starting_y = game.player.y
        step(game, 12)
        self.assertGreater(game.player.y, starting_y)
        for _ in range(180):
            if game.deaths:
                break
            update(game, Controls(), DT)
        self.assertEqual(game.deaths, 1)
        self.assertEqual((game.player.x, game.player.y), game.checkpoint)

    def test_camera_tracks_vertical_rooms_and_stops_at_abyss(self):
        game = Game(start="ridge")
        initial = camera_top(game)
        self.assertGreater(initial, 0)
        game.player.y = 150
        self.assertLess(camera_top(game), initial)
        game.player.y = game.world_height + 50
        self.assertLessEqual(camera_top(game), game.world_height - settings.HEIGHT
                             + settings.CAMERA_OVERSCROLL)

    def test_authored_course_is_playable_without_solving_student_missions(self):
        """Recorded, deterministic no-death playthroughs of every authored room.

        R/L = motion, J = held jump (pressed at segment start), X = dash,
        C = grab, U = climb. Every route starts at that room's default P.
        No student TODO is implemented or bypassed.
        """
        routes = {
            "trailhead": [(14, "R"), (50, "RJ"), (11, "R"),
                          (75, "RCU"), (45, "R"), (100, "RCU"), (80, "R")],
            "switchbacks": [(4, ""), (25, "RJ"), (65, "RCU"),
                            (18, "L"), (15, ""), (25, "RJ"),
                            (65, "RCU"), (20, "L"), (20, ""),
                            (25, "RJ"), (60, "RCU"), (85, "R")],
            "divide": [(14, "R"), (50, "RJ"), (11, "R"), (80, "RCU"),
                       (20, "R"), (25, "RJ"), (1, "RX"), (70, "R")],
            "ridge": [(14, "R"), (36, "RJ"), (80, "RCU"), (20, "R"),
                      (25, "RJ"), (25, ""), (25, "RJ"), (75, "RCU"),
                      (12, "R"), (28, "RJ"), (85, "RCU"), (70, "R")],
        }
        for key, segments in routes.items():
            with self.subTest(room=key):
                game = Game(start=key)
                checkpoints = 0
                for frames, keys in segments:
                    for i in range(frames):
                        update(game, Controls(
                            right="R" in keys, left="L" in keys,
                            up="U" in keys, grab_held="C" in keys,
                            jump_pressed="J" in keys and i == 0,
                            jump_held="J" in keys,
                            dash_pressed="X" in keys and i == 0), DT)
                        checkpoints += "checkpoint" in game.events
                        if game.deaths or game.finished or game.room_key != key:
                            break
                    if game.deaths or game.finished or game.room_key != key:
                        break
                self.assertEqual(game.deaths, 0, f"{key}: route died")
                self.assertTrue(game.finished or game.room_key != key,
                                f"{key}: exit not reached")
                if key in ("switchbacks", "divide", "ridge"):
                    self.assertGreater(checkpoints, 0)

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
            col, row = levels.find(game.room.tiles, "*")[0]
            game.player.x = col * 32 + 4
            game.player.y = row * 32 + 2
            step(game, 3)
        self.assertEqual(hook.call_count, 1)
        self.assertEqual(game.berries, 1)

    def test_crystal_hook_is_used(self):
        game = Game(start="divide")
        game.player.dashes = 0
        col, row = levels.find(game.room.tiles, "R")[0]
        game.player.x = col * 32 + 5
        game.player.y = row * 32 + 5
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
        col, row = levels.find(game.room.tiles, "w")[0]
        game.player = Player(x=col * 32 + 5, y=row * 32 + 5)
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
