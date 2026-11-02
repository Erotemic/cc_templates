"""A few sanity checks for the starter, not rules for future student games."""

import importlib.util
import os
import sys
import types
import unittest
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch


MAIN = Path(__file__).resolve().parents[1] / "main.py"


def load_without_pygame():
    """Test simple movement/state logic even where pygame isn't installed."""
    fake = types.ModuleType("pygame")
    for number, name in enumerate((
        "K_1", "K_2", "K_3", "K_r", "K_ESCAPE",
        "K_RIGHT", "K_LEFT", "K_DOWN", "K_UP", "K_d", "K_a", "K_s", "K_w",
    )):
        setattr(fake, name, number + 1)
    spec = importlib.util.spec_from_file_location("classroom_blank_starter", MAIN)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"pygame": fake}):
        spec.loader.exec_module(module)
    return module


class ScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game_code = load_without_pygame()

    def test_menu_selects_all_three_modes_and_escape_returns(self):
        code = self.game_code
        for key, expected in ((code.pygame.K_1, "real_time"),
                              (code.pygame.K_2, "turns"),
                              (code.pygame.K_3, "choices")):
            state = code.on_key_down(code.new_game("menu", (800, 520)),
                                     key, (800, 520))
            self.assertEqual(state["mode"], expected)
            self.assertEqual(code.on_key_down(state, code.pygame.K_ESCAPE,
                                              (800, 520))["mode"], "menu")

    def test_real_time_uses_elapsed_seconds(self):
        code = self.game_code
        state = code.new_game("real_time", (800, 520))
        keys = defaultdict(bool)
        keys[code.pygame.K_RIGHT] = True
        x = state["x"]
        code.update(state, keys, 0.025, (800, 520))
        self.assertAlmostEqual(state["x"] - x, code.SPEED * 0.025)
        self.assertEqual(state["y"], 260)

    def test_turns_advance_once_per_key_press(self):
        code = self.game_code
        state = code.new_game("turns", (800, 520))
        code.on_key_down(state, code.pygame.K_RIGHT, (800, 520))
        self.assertEqual(state["column"], code.COLUMNS // 2 + 1)
        self.assertEqual(state["turns"], 1)
        code.update(state, defaultdict(bool), 1.0, (800, 520))
        self.assertEqual(state["turns"], 1)

    def test_choice_state_can_change_and_restart(self):
        code = self.game_code
        state = code.new_game("choices", (800, 520))
        code.on_key_down(state, code.pygame.K_2, (800, 520))
        self.assertEqual(state["scene"], "right")
        state = code.on_key_down(state, code.pygame.K_r, (800, 520))
        self.assertEqual(state["scene"], "start")

    def test_real_pygame_can_draw_each_example(self):
        if importlib.util.find_spec("pygame") is None:
            self.skipTest("pygame / pygame-ce not installed")
        with patch.dict(os.environ, {"SDL_VIDEODRIVER": "dummy",
                                     "SDL_AUDIODRIVER": "dummy"}):
            import pygame
            # Load the game with actual pygame, not the fake module used above.
            spec = importlib.util.spec_from_file_location("blank_real_pygame", MAIN)
            code = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(code)
            pygame.init()
            try:
                screen = pygame.display.set_mode((800, 520), pygame.RESIZABLE)
                font = pygame.font.Font(None, 28)
                title_font = pygame.font.Font(None, 42)
                for mode in ("menu", "real_time", "turns", "choices"):
                    code.draw(code.new_game(mode, screen.get_size()),
                              screen, font, title_font)
            finally:
                pygame.quit()


if __name__ == "__main__":
    unittest.main()
