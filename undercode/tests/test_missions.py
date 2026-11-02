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
from undercode.app import Game
from undercode.arena import Arena
from undercode.battle import Phase
from undercode.controls import Controls
from undercode.content import ROOMS
from undercode.model import TurnContext
from undercode.student import LanternPulse, RippleLanes
from undercode.world import tile_center


class CompletedMissionTests(unittest.TestCase):
    @patch.dict(
        next(o for o in ROOMS["studio"].objects if o.kind == "trigger").data,
        {"on_enter": solutions.warm_light},
    )
    def test_healing_reports_actual_gain_and_clamps_health(self):
        world = Game(level="studio").world
        trigger = next(o for o in world.room.objects if o.kind == "trigger")
        for hp, result, message in ((5, 8, "3 HP"), (19, 20, "1 HP"), (20, 20, "0 HP")):
            with self.subTest(hp=hp):
                world.session.player.hp = hp
                world.trigger_tiles.clear()
                world.position = tile_center(trigger.tile)
                world.update(0, Controls())
                self.assertEqual(world.session.player.hp, result)
                self.assertIn(message, world.toast)

    @patch.object(LanternPulse, "update", solutions.update_lantern_pulse)
    def test_completed_pulse_warns_moves_repeats_and_finishes(self):
        arena = Arena(LanternPulse(), hp=1000)
        for _ in range(20):
            arena.update(1 / 60, Controls())
        self.assertEqual(len(arena.bullets), 1)
        first = arena.bullets[0]
        self.assertGreater(first.warmup, 0)
        self.assertEqual(first.position.x, 8)
        for _ in range(60):
            arena.update(1 / 60, Controls())
        self.assertGreater(first.position.x, 8)
        self.assertEqual(len(arena.bullets), 2)
        while not arena.done:
            arena.update(1 / 60, Controls())
        self.assertFalse(arena.bullets)  # Final spark leaves before the turn ends.
        # The registered CLI practice uses the same class that students implement.
        game = Game(practice="pulse")
        game.update(0.4)
        self.assertEqual(len(game.battle.arena.bullets), 1)
        game.restart()
        self.assertFalse(game.battle.arena.bullets)

    @patch.object(LanternPulse, "update", solutions.update_lantern_pulse)
    def test_completed_selector_changes_a_real_echo_battle(self):
        game = Game(encounter="echo")
        # The immutable Character stores its callable when content is loaded;
        # substitute the completed selector as loading a student's edited file would.
        game.battle.character = replace(
            game.battle.character, choose_pattern=solutions.choose_echo_pattern
        )
        game.battle.turn = 0
        game.battle.set_phase(Phase.DEFEND)
        self.assertIsInstance(game.battle.arena.pattern, RippleLanes)
        game.battle.turn = 1
        game.battle.set_phase(Phase.DEFEND)
        self.assertIsInstance(game.battle.arena.pattern, LanternPulse)
        game.update(0.4)
        self.assertTrue(game.battle.arena.bullets)
        a = solutions.choose_echo_pattern(TurnContext(1, 20, 20, 0))
        b = solutions.choose_echo_pattern(TurnContext(1, 20, 20, 0))
        self.assertIsNot(a, b)
        a.cooldown = -5
        self.assertEqual(b.cooldown, 0.3)


if __name__ == "__main__":
    unittest.main()
