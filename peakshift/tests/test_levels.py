"""Maps fail with clear row/column diagnostics, not mystery KeyErrors."""

import unittest
from dataclasses import replace

from peakshift import levels
from peakshift.physics import Game


class LevelTests(unittest.TestCase):
    def test_every_authored_room_valid(self):
        levels.validate_rooms()
        self.assertEqual(len(levels.ROOMS), 4)
        self.assertEqual([len(room.tiles) for room in levels.ROOMS.values()],
                         [20, 29, 23, 31])
        self.assertTrue(all(len(line) == 24 for room in levels.ROOMS.values()
                            for line in room.tiles))
        self.assertEqual([room.name for room in levels.ROOMS.values()],
                         ["Trailhead", "Switchbacks", "Skybridge", "Lantern Ridge"])

    def test_authored_course_contains_real_cliff_walls_and_floorless_gaps(self):
        """Tall faces and an absent collision floor, not painted scenery."""
        for name, room in levels.ROOMS.items():
            with self.subTest(room=name):
                # At least one face has >=4 tiles of vertical rock.
                wall_height = max(
                    max((len(run) for run in ''.join(
                        'X' if row[col] == '#' else '.' for row in room.tiles
                    ).split('.')), default=0)
                    for col in range(24))
                self.assertGreaterEqual(wall_height, 4)
                # Below spawn height, a 4-column hole has no collision floor.
                spawn_row = levels.find(room.tiles, 'P')[0][1]
                gaps = [all(row[col] not in '#=bm'
                            for row in room.tiles[spawn_row + 1:])
                        for col in range(24)]
                self.assertIn('XXXX', ''.join('X' if gap else '.' for gap in gaps))

    def test_validator_accepts_tall_maps_but_rejects_too_short(self):
        from peakshift import settings
        from dataclasses import replace
        short = replace(levels.WELCOME, tiles=levels.WELCOME.tiles[:settings.ROWS - 1])
        with self.assertRaisesRegex(levels.MapError, 'expected at least 15 rows'):
            levels.validate_rooms({'short': short}, 'short')

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
        with self.assertRaisesRegex(levels.MapError, "row 20: expected 24 columns"):
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
                         [(18 * 32, 17 * 32, 2 * 32)])


if __name__ == "__main__":
    unittest.main()
