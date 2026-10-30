"""Pygame-free checks for the editable classroom levels and student hooks."""

import unittest
from unittest.mock import patch

from platformer import challenge, level, student


class LevelTests(unittest.TestCase):
    def test_starting_maps_and_any_extra_levels_are_valid(self):
        self.assertGreaterEqual(len(level.LEVELS), 3)
        self.assertEqual(len(level.LEVELS), len(level.LEVEL_NAMES))
        level.check_all_maps()
        for tiles in level.LEVELS:
            self.assertEqual(len(tiles), 15)
            self.assertTrue(all(len(row) == 24 for row in tiles))
            for symbol in ("P", "D", "E", "^"):
                self.assertEqual(len(level.locations(symbol, tiles)), 1)
            self.assertGreaterEqual(len(level.locations("*", tiles)), 1)

    def test_invalid_map_gives_readable_feedback(self):
        with patch.object(level, "TILES", ("P..", "##", "D*E")):
            with self.assertRaisesRegex(ValueError, "same length"):
                level.check_map()
        broken = list(level.LEVEL_2)
        broken[0] = "?" + broken[0][1:]
        with self.assertRaisesRegex(ValueError, "Unknown map symbol"):
            level.check_map(tuple(broken))
        with self.assertRaisesRegex(ValueError, "Level 2"):
            with patch.object(level, "LEVELS", (level.LEVEL_1, tuple(broken), level.LEVEL_3)):
                level.check_all_maps()

    def test_add_fourth_level_is_supported(self):
        # Completing mission 3 must not make a baseline test fail.
        with patch.object(level, "LEVELS", level.LEVELS + (level.LEVEL_3,)), \
             patch.object(level, "LEVEL_NAMES", level.LEVEL_NAMES + ("My Level",)):
            level.check_all_maps()
            self.assertEqual(len(level.LEVELS), 4)

    def test_optional_mission_tiles_are_present(self):
        self.assertTrue(level.locations("M", level.LEVEL_2))
        self.assertTrue(level.locations("S", level.LEVEL_2))
        self.assertTrue(level.locations("B", level.LEVEL_3))

    def test_guided_hooks_can_be_called(self):
        # Students may implement these functions, so do not require no-ops!
        class Player:
            vy = 0
            on_ground = True

        class Enemy:
            x = 100
            speed = 60
            direction = 1
            left_limit = 80
            right_limit = 180

        p = Player()
        e = Enemy()
        student.bounce_from_pad(p)
        student.move_enemy(e, 1 / 60)
        self.assertIsInstance(p.vy, (float, int))
        self.assertIsInstance(e.x, (float, int))

    def test_open_challenges_are_distinct(self):
        self.assertGreaterEqual(len(challenge.CHALLENGES), 6)
        names = [name for name, _goal, _concept in challenge.CHALLENGES]
        self.assertEqual(len(names), len(set(names)))
        for _name, goal, concept in challenge.CHALLENGES:
            self.assertTrue(goal)
            self.assertIn("Think about:", concept)


if __name__ == "__main__":
    unittest.main()
