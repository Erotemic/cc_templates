"""Architecture promises: independently runnable systems and understandable state ownership."""

import contextlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
from undercode.app import Game
from undercode.controls import Controls
from undercode.contracts import EncounterRequest, EncounterResult, Outcome
from undercode.encounters.engine import Phase
from undercode.exercises import check_exercises
from undercode import student_overworld, student_encounters
from teacher import solutions


class BoundaryTests(unittest.TestCase):
    def test_each_learning_mode_runs_with_the_other_authors_file_broken(self):
        """A student's syntax error in one activity must not block the other activity."""
        for broken, args in (
            ("student_world.py", ["--encounter", "echo"]),
            ("student_world.py", ["--practice", "shield"]),
            ("student_encounters.py", ["--overworld"]),
        ):
            with self.subTest(broken=broken, args=args), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                shutil.copy2(ROOT / "main.py", project / "main.py")
                shutil.copytree(
                    ROOT / "undercode",
                    project / "undercode",
                    ignore=shutil.ignore_patterns("__pycache__"),
                )
                (project / "undercode" / broken).write_text("def unfinished( !!!\n")
                result = subprocess.run(
                    [
                        sys.executable,
                        str(project / "main.py"),
                        *args,
                        "--headless",
                        "--mute",
                        "--frames",
                        "2",
                    ],
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_standalone_encounter_finishes_without_loading_an_overworld(self):
        """A completed isolated encounter stays on its result screen until R or quit."""
        game = Game(encounter="folio")
        game.encounter.finish(outcome=Outcome.LEFT, message="See you later.")
        for _ in range(10):
            if game.encounter.phase == Phase.FINISHED:
                break
            game.update(seconds=1 / 60, controls=Controls(confirm_pressed=True))
        self.assertEqual(game.encounter.phase, Phase.FINISHED)
        game.update(seconds=0)
        self.assertIsNone(game.world)
        self.assertEqual(game.finished_result.outcome, Outcome.LEFT)
        game.restart()
        self.assertIsNone(game.world)
        self.assertIsNone(game.finished_result)

    def test_one_player_owns_health_including_during_defense(self):
        """Damage is visible immediately without a copy-back step in Encounter.update."""
        game = Game(encounter="folio")
        game.encounter.set_phase(phase=Phase.DEFEND)
        self.assertIs(game.encounter.player, game.session.player)
        self.assertIs(game.encounter.arena.player, game.session.player)
        game.encounter.arena.hurt(damage=3)
        self.assertEqual(game.session.player.hp, 17)
        game.session.player.heal(amount=2)
        self.assertEqual(game.encounter.arena.hp, 19)

    def test_typed_messages_delay_scene_change_until_covered_midpoint(self):
        """The coordinator accepts concrete data, not anonymous closures or tuple tags."""
        game = Game()
        request = EncounterRequest(encounter_id="folio", person_id="folio")
        game.begin_transition(request=request)
        self.assertIs(game.transition.request, request)
        game.update(seconds=0.2)
        self.assertIsNone(game.encounter)
        game.update(seconds=0.2)
        self.assertIsNotNone(game.encounter)
        result = EncounterResult(outcome=Outcome.SPARED, opponent_name="Folio")
        game.apply_request(request=result)
        self.assertEqual(game.session.resolved["folio"], Outcome.SPARED)

    def test_completed_sprint_is_used_in_real_movement_not_just_the_checker(self):
        """A completed function changes distance in normal play; release restores speed."""
        with patch.object(student_overworld, "movement_speed", solutions.movement_speed):
            walking, sprinting = Game(), Game()
            before = walking.world.position.copy()
            walking.update(seconds=0.1, controls=Controls(move_x=1))
            sprinting.update(seconds=0.1, controls=Controls(move_x=1, sprint_held=True))
            self.assertAlmostEqual(walking.world.position.x - before.x, 15.5)
            self.assertAlmostEqual(sprinting.world.position.x - before.x, 23)
            before = sprinting.world.position.copy()
            sprinting.update(seconds=0.1, controls=Controls(move_x=1))
            self.assertAlmostEqual(sprinting.world.position.x - before.x, 15.5)


class ExerciseChecksTests(unittest.TestCase):
    def test_checkers_accept_completed_implementations_without_engine_solution_switch(self):
        """Teacher examples are injected only by tests; checkers themselves use student code."""
        with (
            patch.object(student_overworld, "choose_player_view", solutions.choose_player_view),
            patch.object(student_overworld, "movement_speed", solutions.movement_speed),
            patch.object(student_overworld, "warm_light", solutions.warm_light),
            patch.object(student_encounters.LanternPulse, "update", solutions.update_lantern_pulse),
            patch.object(student_encounters, "choose_echo_pattern", solutions.choose_echo_pattern),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(check_exercises(exercise="all"), 0)

    def test_progress_reports_actual_unfinished_behavior_not_teacher_examples(self):
        """A deliberately wrong function fails even while engine regression checks pass."""

        def unfinished(*, facing):
            """Represent incomplete student work independently of the shipped starter."""
            return "down"

        with (
            patch.object(student_overworld, "choose_player_view", unfinished),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(check_exercises(exercise="facing"), 1)
        self.assertIn("3/8", output.getvalue())


if __name__ == "__main__":
    unittest.main()
