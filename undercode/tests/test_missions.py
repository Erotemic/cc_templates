"""Exercise the real extension points with completed instructor implementations.

The starter is intentionally unfinished. These tests check that implementing a
mission affects real play, without requiring students to finish every mission
before running the rest of the suite.
"""

from dataclasses import replace
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from teacher import solutions
from undercode.overworld.maps import compile_rooms
from undercode.student_world import LEVELS
from undercode.overworld.model import Trigger

ROOMS = compile_rooms(definitions=LEVELS)

from undercode.model import Player
from undercode.app import Game
from undercode.encounters.arena import Arena
from undercode.encounters.encounter import Phase
from undercode.controls import Controls

from undercode.encounters.model import TurnContext
from undercode.student_encounters import LanternPulse, RippleLanes
from undercode.overworld.world import tile_center


class CompletedMissionTests(unittest.TestCase):
    @patch.object(
        next(o.definition for o in ROOMS["studio"].objects if isinstance(o.definition, Trigger)),
        "on_enter",
        solutions.warm_light,
    )
    def test_healing_reports_actual_gain_and_clamps_health(self):
        world = Game(level="studio").world
        trigger = next(o for o in world.room.objects if isinstance(o.definition, Trigger))
        for hp, result, message in ((5, 8, "3 HP"), (19, 20, "1 HP"), (20, 20, "0 HP")):
            with self.subTest(hp=hp):
                world.session.player.hp = hp
                world.trigger_tiles.clear()
                world.position = tile_center(tile=trigger.tile)
                world.update(seconds=0, controls=Controls())
                self.assertEqual(world.session.player.hp, result)
                self.assertIn(message, world.toast)

    @patch.object(LanternPulse, "update", solutions.update_lantern_pulse)
    def test_completed_pulse_warns_moves_repeats_and_finishes(self):
        arena = Arena(pattern=LanternPulse(), player=Player(hp=1000, max_hp=1000))
        for _ in range(20):
            arena.update(seconds=1 / 60, controls=Controls())
        self.assertEqual(len(arena.bullets), 1)
        first = arena.bullets[0]
        self.assertGreater(first.warmup, 0)
        self.assertEqual(first.position.x, 8)
        for _ in range(60):
            arena.update(seconds=1 / 60, controls=Controls())
        self.assertGreater(first.position.x, 8)
        self.assertEqual(len(arena.bullets), 2)
        while not arena.done:
            arena.update(seconds=1 / 60, controls=Controls())
        self.assertFalse(arena.bullets)  # Final spark leaves before the turn ends.
        # The registered CLI practice uses the same class that students implement.
        game = Game(practice="pulse")
        game.update(seconds=0.4)
        self.assertEqual(len(game.encounter.arena.bullets), 1)
        game.restart()
        self.assertFalse(game.encounter.arena.bullets)

    @patch.object(LanternPulse, "update", solutions.update_lantern_pulse)
    def test_completed_selector_changes_a_real_echo_battle(self):
        game = Game(encounter="echo")
        # The immutable Character stores its callable when content is loaded;
        # substitute the completed selector as loading a student's edited file would.
        game.encounter.opponent = replace(
            game.encounter.opponent, choose_pattern=solutions.choose_echo_pattern
        )
        game.encounter.turn = 0
        game.encounter.set_phase(phase=Phase.DEFEND)
        self.assertIsInstance(game.encounter.arena.pattern, RippleLanes)
        game.encounter.turn = 1
        game.encounter.set_phase(phase=Phase.DEFEND)
        self.assertIsInstance(game.encounter.arena.pattern, LanternPulse)
        game.update(seconds=0.4)
        self.assertTrue(game.encounter.arena.bullets)
        a = solutions.choose_echo_pattern(
            context=TurnContext(turn=1, opponent_hp=20, opponent_max_hp=20, calm=0)
        )
        b = solutions.choose_echo_pattern(
            context=TurnContext(turn=1, opponent_hp=20, opponent_max_hp=20, calm=0)
        )
        self.assertIsNot(a, b)
        a.cooldown = -5
        self.assertEqual(b.cooldown, 0.3)


if __name__ == "__main__":
    unittest.main()
