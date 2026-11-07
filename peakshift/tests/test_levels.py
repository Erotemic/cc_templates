"""Maps fail with clear row/column diagnostics, not mystery KeyErrors."""

import unittest
from dataclasses import replace

from peakshift import levels
from peakshift.physics import Game


class LevelTests(unittest.TestCase):
    def test_every_authored_room_valid(self):
        levels.validate_rooms()
        self.assertEqual(len(levels.ROOMS), 4)
        self.assertTrue(all(len(room.tiles) == 15 for room in levels.ROOMS.values()))
        self.assertEqual([room.name for room in levels.ROOMS.values()],
                         ["Trailhead", "Switchbacks", "Skybridge", "Lantern Ridge"])

    def test_graph_connects_to_a_terminal_room(self):
        key = levels.START_ROOM
        visited = set()
        while key is not None:
            self.assertNotIn(key, visited)
            visited.add(key)
            key = levels.ROOMS[key].next_room
        self.assertEqual(visited, set(levels.ROOMS))

    def test_student_map_error_points_to_row(self):
        bad = replace(levels.WELCOME, tiles=levels.WELCOME.tiles[:-1] + ("###",))
        with self.assertRaisesRegex(levels.MapError, "row 15: expected 24 columns"):
            levels.validate_rooms({"bad": bad}, "bad")

    def test_missing_spawn_is_explained(self):
        bad = replace(levels.WELCOME, tiles=tuple(row.replace("P", ".")
                                                     for row in levels.WELCOME.tiles))
        with self.assertRaisesRegex(levels.MapError, "one P"):
            levels.validate_rooms({"bad": bad}, "bad")

    def test_unknown_char_is_located(self):
        rows = list(levels.WELCOME.tiles)
        rows[2] = "?" + rows[2][1:]
        with self.assertRaisesRegex(levels.MapError, "row 3, column 1"):
            levels.validate_rooms({"bad": replace(levels.WELCOME, tiles=tuple(rows))}, "bad")

    def test_student_can_add_room_without_engine_changes(self):
        rows = list(levels.WELCOME.tiles)
        rooms = {"test": replace(levels.WELCOME, name="Student Room",
                                 tiles=tuple(rows), next_room=None)}
        game = Game(rooms, "test")
        self.assertEqual(game.room.name, "Student Room")

    def test_adjacent_platform_characters_form_one_bridge(self):
        self.assertEqual(list(levels.moving_platform_runs(levels.DIVIDE.tiles)),
                         [(16 * 32, 10 * 32, 4 * 32)])


if __name__ == "__main__":
    unittest.main()
