"""Regression fixtures show what completing the mouse task adds to actual encounters."""

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
from undercode import student_encounters
from undercode.app import Game
from undercode.controls import Controls
from undercode.encounters.encounter import Phase
from undercode.encounters.menu import main_buttons, option_buttons
from undercode.encounters.model import Act
from undercode.exercises import check_mouse


class MouseMissionTests(unittest.TestCase):
    def setUp(self):
        """Inject the instructor implementation only for wiring tests, never for gameplay."""
        patcher = patch.object(student_encounters, "clicked_button", solutions.clicked_button)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_all_four_actions_use_the_same_keyboard_action_path(self):
        for button, expected in zip(
            main_buttons(), (Phase.ATTACK, Phase.ACT, Phase.ITEM, Phase.MERCY)
        ):
            with self.subTest(button=button.label):
                game = Game(encounter="folio")
                game.encounter.set_phase(phase=Phase.MENU)
                game.update(seconds=0, controls=Controls(mouse_click=button.rect.center))
                self.assertEqual(game.encounter.phase, expected)
                # The same click did not also select the submenu or stop the strike.
                if expected == Phase.ATTACK:
                    self.assertFalse(game.encounter.strike.done)
                self.assertEqual(game.encounter.calm, 0)
                self.assertEqual(game.session.player.snacks, 2)
                game.update(seconds=0)
                self.assertEqual(game.encounter.phase, expected)

    def test_submenu_click_applies_once_and_back_returns_to_menu(self):
        game = Game(encounter="folio")
        encounter = game.encounter
        encounter.set_phase(phase=Phase.ACT)
        button = option_buttons(labels=encounter.options(), selection=0)[0]
        game.update(
            seconds=0, controls=Controls(mouse_click=button.rect.center, confirm_pressed=True)
        )
        self.assertEqual(encounter.phase, Phase.MESSAGE)
        self.assertEqual(encounter.calm, encounter.opponent.acts[0].calm)
        encounter.set_phase(phase=Phase.ITEM)
        rows = option_buttons(labels=encounter.options(), selection=0)
        game.update(seconds=0, controls=Controls(mouse_click=rows[-1].rect.center))
        self.assertEqual(encounter.phase, Phase.MENU)
        self.assertEqual(game.session.player.snacks, 2)
        encounter.set_phase(phase=Phase.ITEM)
        game.session.player.hp = 5
        game.update(seconds=0, controls=Controls(mouse_click=rows[0].rect.center))
        game.update(seconds=0)
        self.assertEqual(game.session.player.snacks, 1)
        self.assertEqual(game.session.player.hp, 12)

    def test_scrolled_menu_uses_original_index_and_outside_click_does_nothing(self):
        game = Game(encounter="folio")
        encounter = game.encounter
        encounter.opponent = replace(
            encounter.opponent,
            acts=tuple(Act(name=f"Choice {i}", reply=f"Reply {i}", calm=i) for i in range(10)),
        )
        encounter.set_phase(phase=Phase.ACT)
        encounter.selection = 9
        rows = option_buttons(labels=encounter.options(), selection=encounter.selection)
        wanted = next(button for button in rows if button.index == 9)
        game.update(seconds=0, controls=Controls(mouse_click=(0, 0)))
        self.assertEqual(encounter.selection, 9)
        self.assertEqual(encounter.phase, Phase.ACT)
        game.update(seconds=0, controls=Controls(mouse_click=wanted.rect.center))
        self.assertIn("Reply 9", encounter.current_message)

    def test_clicks_do_not_advance_dialogue_jump_or_bypass_help_pause(self):
        game = Game(encounter="folio")
        button = main_buttons()[0]
        game.update(seconds=0, controls=Controls(mouse_click=button.rect.center))
        self.assertEqual(game.encounter.age, 0)
        self.assertEqual(game.encounter.phase, Phase.MESSAGE)
        game.encounter.set_phase(phase=Phase.MENU)
        game.help_open = True
        game.update(seconds=0, controls=Controls(mouse_click=button.rect.center))
        self.assertEqual(game.encounter.phase, Phase.MENU)
        game = Game(practice="hops")
        game.update(seconds=0, controls=Controls(mouse_click=button.rect.center))
        self.assertTrue(game.encounter.arena.soul.grounded)

    def test_checker_uses_actual_student_code_and_catches_returning_none(self):
        self.assertTrue(all(ok for ok, _ in check_mouse()))

        def unfinished(*, mouse_position, buttons):
            """Represent unfinished work without depending on the shipped student's answer."""
            return None

        with patch.object(student_encounters, "clicked_button", unfinished):
            results = check_mouse()
            self.assertTrue(any(not ok for ok, _ in results))
            self.assertTrue(any("index 0" in message and not ok for ok, message in results))


if __name__ == "__main__":
    unittest.main()
