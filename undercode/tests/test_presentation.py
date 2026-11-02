"""Actual pygame rendering/audio and classroom-friendly launch checks."""

from dataclasses import asdict, replace
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame
from undercode.overworld.maps import compile_rooms
from undercode.student_world import LEVELS

ROOMS = compile_rooms(definitions=LEVELS)

from undercode.app import Game
from undercode.audio import Audio
from undercode.encounters.engine import Phase
from undercode.encounters.content import OPPONENTS, PATTERNS
from undercode.encounters.model import Act
from undercode.view import View


class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_mode((960, 720))
        cls.view = View()
        cls.surface = pygame.Surface((960, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_every_portrait_room_menu_and_pattern_renders_without_changing_state(self):
        game = Game()
        for room in ROOMS:
            game.world.change_room(destination=room, landing=next(iter(ROOMS[room].spawns)))
            self.view.draw(surface=self.surface, game=game)
        for character in OPPONENTS:
            game = Game(encounter=character.key)
            for phase in (
                Phase.MESSAGE,
                Phase.MENU,
                Phase.ACT,
                Phase.ITEM,
                Phase.MERCY,
                Phase.ATTACK,
            ):
                game.encounter.set_phase(phase=phase)
                game.encounter.age = 10 if phase == Phase.MESSAGE else 0.3
                before = (
                    asdict(game.session),
                    game.encounter.phase,
                    game.encounter.age,
                    game.encounter.opponent_hp,
                )
                self.view.draw(surface=self.surface, game=game)
                self.assertEqual(
                    before,
                    (
                        asdict(game.session),
                        game.encounter.phase,
                        game.encounter.age,
                        game.encounter.opponent_hp,
                    ),
                )
        for pattern in PATTERNS:
            game = Game(practice=pattern)
            for _ in range(90):
                game.update(seconds=1 / 60)
            random_before = game.encounter.arena.rng.getstate()
            state = (
                game.encounter.arena.elapsed,
                game.session.player.hp,
                [tuple(b.position) for b in game.encounter.arena.bullets],
            )
            self.view.draw(surface=self.surface, game=game)
            self.assertEqual(game.encounter.arena.rng.getstate(), random_before)
            self.assertEqual(
                state,
                (
                    game.encounter.arena.elapsed,
                    game.session.player.hp,
                    [tuple(b.position) for b in game.encounter.arena.bullets],
                ),
            )
        game.help_open = True
        self.view.draw(surface=self.surface, game=game)
        self.view.draw(surface=self.surface, game=game, focused=False)

    def test_long_words_fit_the_panel_and_battle_dialogue_is_paged(self):
        word = "W" * 300
        for line in self.view.lines(text=word, width=300, size=24):
            self.assertLessEqual(self.view.fonts[24].size(line)[0], 300)
        game = Game(encounter="echo")
        game.encounter.say(message=word * 2, then=Phase.MENU)
        self.assertGreater(len(game.encounter.pages), 1)
        self.view.draw(surface=self.surface, game=game)

    def test_student_characters_can_have_more_act_choices_than_fit_on_one_page(self):
        game = Game(encounter="folio")
        game.encounter.opponent = replace(
            game.encounter.opponent,
            acts=tuple(Act(name=f"Choice {i}", reply="A reply.") for i in range(10)),
        )
        game.encounter.set_phase(phase=Phase.ACT)
        game.encounter.selection = 9
        labels = []
        self.view.draw(surface=self.surface, game=game)
        renderer = self.view.encounter_view
        original = renderer.text

        def record(surface, text, *args, **kwargs):
            rect = original(surface=surface, text=text, *args, **kwargs)
            if str(text).startswith("Choice "):
                labels.append((text, rect))
            return rect

        renderer.text = record
        try:
            self.view.draw(surface=self.surface, game=game)
        finally:
            renderer.text = original
        self.assertTrue(any(text == "Choice 9" for text, _ in labels))
        self.assertLessEqual(len(labels), 4)
        self.assertTrue(all(rect.top >= 378 and rect.bottom < 507 for _, rect in labels))

    def test_story_pages_and_choices_fit_their_panels_without_changing_state(self):
        from unittest.mock import patch
        from undercode.dialogue import Conversation, Dialogue, Choice

        game = Game(level="studio")
        game.world.dialogue = Conversation(
            name="Keeper",
            dialogue=Dialogue(
                text="W" * 300, choices=[Choice(label="W" * 60, text="Reply") for _ in range(10)]
            ),
            session=game.session,
        )
        dialogue = game.world.dialogue
        dialogue.page = len(dialogue.pages) - 1
        dialogue.selection = 9
        self.view.draw(surface=self.surface, game=game)
        renderer = self.view.world_view
        original = renderer.text
        rendered, rendered_text = [], []

        def record(surface, text, *args, **kwargs):
            rect = original(surface=surface, text=text, *args, **kwargs)
            if set(str(text)) == {"W"}:
                rendered.append(rect)
                rendered_text.append(str(text))
            return rect

        with patch.object(renderer, "text", record):
            before = asdict(game.session)
            self.view.draw(surface=self.surface, game=game)
            self.assertEqual(asdict(game.session), before)
        self.assertTrue(rendered)
        self.assertEqual(
            sum(t.count("W") for t in rendered_text),
            dialogue.pages[dialogue.page].count("W") + 3 * 60,
        )
        self.assertTrue(all(pygame.Rect(112, 420, 732, 246).contains(r) for r in rendered))
        self.assertEqual(dialogue.selection, 9)

    def test_completed_direction_mission_changes_normal_walking_and_idle_views(self):
        from unittest.mock import patch
        from teacher.solutions import choose_player_view
        from undercode.controls import Controls

        game = Game()
        with (
            patch("undercode.student_overworld.choose_player_view", choose_player_view),
            patch("undercode.view.art.courier") as draw,
        ):
            for (x, y), expected in (
                ((-1, 0), "left"),
                ((1, 0), "right"),
                ((0, -1), "up"),
                ((0, 1), "down"),
            ):
                with self.subTest(view=expected):
                    game.update(seconds=0.01, controls=Controls(move_x=x, move_y=y))
                    self.view.draw(surface=self.surface, game=game)
                    self.assertEqual(draw.call_args.kwargs["view"], expected)
                    game.update(seconds=0.01)  # Releasing keys preserves that view.
                    self.view.draw(surface=self.surface, game=game)
                    self.assertEqual(draw.call_args.kwargs["view"], expected)
            game.restart()
            game.update(seconds=0)
            self.view.draw(surface=self.surface, game=game)
            self.assertEqual(draw.call_args.kwargs["view"], "down")

    def test_four_walking_views_are_distinct_and_animate(self):
        from undercode.art import courier

        images = []
        for direction in ("up", "down", "left", "right"):
            surface = pygame.Surface((80, 80))
            courier(surface=surface, center=(40, 45), time=0, walking=False, view=direction)
            images.append(pygame.image.tobytes(surface, "RGB"))
        self.assertEqual(len(set(images)), 4)
        surface = pygame.Surface((80, 80))
        courier(surface=surface, center=(40, 45), time=0.12, walking=True, view="down")
        self.assertNotEqual(pygame.image.tobytes(surface, "RGB"), images[1])

    def test_synthesized_audio_has_samples_and_mute_controls_the_channel(self):
        audio = Audio()
        try:
            self.assertTrue(audio.enabled)
            self.assertTrue(any(audio.effects["select"].get_raw()))
            self.assertGreater(audio.music["WORLD"].get_length(), 3)
            audio.scene("WORLD")
            channel = pygame.mixer.Channel(0)
            self.assertTrue(channel.get_busy())
            audio.toggle()
            self.assertEqual(channel.get_volume(), 0)
            audio.toggle()
            self.assertGreater(channel.get_volume(), 0)
            audio.scene("ENCOUNTER")
            self.assertTrue(channel.get_busy())
        finally:
            pygame.mixer.quit()


class LaunchTests(unittest.TestCase):
    def run_main(self, *args, **kwargs):
        return subprocess.run(
            [sys.executable, str(ROOT / "main.py"), *args],
            capture_output=True,
            text=True,
            timeout=30,
            **kwargs,
        )

    def test_runs_from_outside_the_folder_and_saves_a_headless_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame.png"
            result = self.run_main(
                "--headless",
                "--mute",
                "--practice",
                "shield",
                "--frames",
                "60",
                "--screenshot",
                str(path),
                cwd=directory,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(path.is_file())
            image = pygame.image.load(str(path))
            self.assertEqual(image.get_size(), (960, 720))

    def test_copied_game_adds_a_room_in_student_world_and_reports_map_mistakes(self):
        """Adding a room needs one edit in the same file as all existing rooms."""
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "student_game"
            project.mkdir()
            shutil.copy2(ROOT / "main.py", project / "main.py")
            shutil.copytree(
                ROOT / "undercode",
                project / "undercode",
                ignore=shutil.ignore_patterns("__pycache__"),
            )
            world_file = project / "undercode" / "student_world.py"
            world_file.write_text(
                world_file.read_text() + "\n# A student adds a room in this same file.\n"
                'MESSAGE = "I wrote this in Python."\n'
                'LEVELS["my_room"] = Room(name="My room", tiles=["######", "#@.?.D", "######"], legend={\n'
                '    "@": Spawn(name="entrance"),\n'
                '    "?": Sign(name="My note", dialogue=Dialogue(text=MESSAGE)),\n'
                '    "D": Door(destination_room="courtyard", destination_spawn="camp"),\n'
                "})\n"
            )
            command = [sys.executable, str(project / "main.py")]
            checked = subprocess.run(
                command + ["--check"], cwd=directory, capture_output=True, text=True, timeout=30
            )
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertIn("5 rooms", checked.stdout)
            played = subprocess.run(
                command
                + [
                    "--headless",
                    "--mute",
                    "--level",
                    "my_room",
                    "--entry",
                    "entrance",
                    "--frames",
                    "2",
                ],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(played.returncode, 0, played.stderr)
            # A changed size avoids stale bytecode for same-second test edits.
            world_file.write_text(
                world_file.read_text().replace('"#@.?.D"', '"#@.!.D"') + "\n# Map edited.\n"
            )
            bad = subprocess.run(
                command + ["--check"], cwd=directory, capture_output=True, text=True, timeout=30
            )
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("row 2, column 4", bad.stderr)
            self.assertNotIn("Traceback", bad.stderr)

    def test_list_check_bad_key_and_invisible_desktop(self):
        listed = self.run_main("--list")
        self.assertEqual(listed.returncode, 0)
        self.assertIn("echo", listed.stdout)
        self.assertIn("ripples", listed.stdout)
        checked = self.run_main("--check")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        bad = self.run_main("--practice", "not-a-pattern")
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("Unknown pattern", bad.stderr)
        invisible = self.run_main("--mute", "--frames", "1")
        self.assertNotEqual(invisible.returncode, 0)
        self.assertIn("No visible desktop", invisible.stderr)


if __name__ == "__main__":
    unittest.main()
