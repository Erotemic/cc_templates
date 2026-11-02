"""Actual pygame rendering/audio and classroom-friendly launch checks."""

from dataclasses import asdict, replace
import os
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
from undercode.app import Game
from undercode.audio import Audio
from undercode.battle import Phase
from undercode.content import CHARACTERS, PATTERNS, ROOMS
from undercode.model import Act
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
            game.world.change_room(room, next(iter(ROOMS[room].spawns)))
            self.view.draw(self.surface, game)
        for character in CHARACTERS:
            game = Game(encounter=character.key)
            for phase in (
                Phase.MESSAGE,
                Phase.MENU,
                Phase.ACT,
                Phase.ITEM,
                Phase.MERCY,
                Phase.ATTACK,
            ):
                game.battle.set_phase(phase)
                game.battle.age = 10 if phase == Phase.MESSAGE else 0.3
                before = (
                    asdict(game.session),
                    game.battle.phase,
                    game.battle.age,
                    game.battle.enemy_hp,
                )
                self.view.draw(self.surface, game)
                self.assertEqual(
                    before,
                    (
                        asdict(game.session),
                        game.battle.phase,
                        game.battle.age,
                        game.battle.enemy_hp,
                    ),
                )
        for pattern in PATTERNS:
            game = Game(practice=pattern)
            for _ in range(90):
                game.update(1 / 60)
            random_before = game.battle.arena.rng.getstate()
            state = (
                game.battle.arena.elapsed,
                game.session.player.hp,
                [tuple(b.position) for b in game.battle.arena.bullets],
            )
            self.view.draw(self.surface, game)
            self.assertEqual(game.battle.arena.rng.getstate(), random_before)
            self.assertEqual(
                state,
                (
                    game.battle.arena.elapsed,
                    game.session.player.hp,
                    [tuple(b.position) for b in game.battle.arena.bullets],
                ),
            )
        game.help_open = True
        self.view.draw(self.surface, game)
        self.view.draw(self.surface, game, focused=False)

    def test_long_words_fit_the_panel_and_battle_dialogue_is_paged(self):
        word = "W" * 300
        for line in self.view.lines(word, 300, 24):
            self.assertLessEqual(self.view.fonts[24].size(line)[0], 300)
        game = Game(encounter="echo")
        game.battle.say(word * 2, Phase.MENU)
        self.assertGreater(len(game.battle.pages), 1)
        self.view.draw(self.surface, game)

    def test_student_characters_can_have_more_act_choices_than_fit_on_one_page(self):
        game = Game(encounter="folio")
        game.battle.character = replace(
            game.battle.character,
            acts=tuple(Act(f"Choice {i}", "A reply.") for i in range(10)),
        )
        game.battle.set_phase(Phase.ACT)
        game.battle.selection = 9
        labels = []
        original = self.view.text

        def record(surface, text, *args, **kwargs):
            rect = original(surface, text, *args, **kwargs)
            if str(text).startswith("Choice "):
                labels.append((text, rect))
            return rect

        self.view.text = record
        try:
            self.view.draw(self.surface, game)
        finally:
            self.view.text = original
        self.assertTrue(any(text == "Choice 9" for text, _ in labels))
        self.assertLessEqual(len(labels), 4)
        self.assertTrue(all(rect.top >= 378 and rect.bottom < 507 for _, rect in labels))

    def test_story_pages_choices_and_sprite_task_stay_inside_their_panels(self):
        from unittest.mock import patch
        from undercode.story import Dialogue

        game = Game(level="studio", sprite_task=True)
        game.world.dialogue = Dialogue(
            "Keeper",
            {
                "text": "W" * 300,
                "choices": [{"label": "W" * 60} for _ in range(10)],
            },
            game.session,
        )
        dialogue = game.world.dialogue
        dialogue.page = len(dialogue.pages) - 1
        dialogue.selection = 9
        rendered = []
        rendered_text = []
        original = self.view.text

        def record(surface, text, *args, **kwargs):
            rect = original(surface, text, *args, **kwargs)
            if set(str(text)) == {"W"}:
                rendered.append(rect)
                rendered_text.append(str(text))
            return rect

        with (
            patch.object(self.view, "text", record),
            patch("undercode.view.choose_player_view", return_value="left") as student,
            patch("undercode.view.art.courier") as draw,
        ):
            before = asdict(game.session)
            self.view.draw(self.surface, game)
            student.assert_called_once_with(game.world.facing)
            self.assertEqual(draw.call_args.args[-1], "left")
            self.assertEqual(asdict(game.session), before)
        self.assertTrue(rendered)
        self.assertEqual(
            sum(t.count("W") for t in rendered_text),
            dialogue.pages[dialogue.page].count("W") + 3 * 60,
        )
        self.assertTrue(all(pygame.Rect(112, 420, 732, 246).contains(r) for r in rendered))
        self.assertEqual(dialogue.selection, 9)

    def test_four_walking_views_are_distinct_and_animate(self):
        from undercode.art import courier

        images = []
        for direction in ("up", "down", "left", "right"):
            surface = pygame.Surface((80, 80))
            courier(surface, (40, 45), 0, False, direction)
            images.append(pygame.image.tobytes(surface, "RGB"))
        self.assertEqual(len(set(images)), 4)
        surface = pygame.Surface((80, 80))
        courier(surface, (40, 45), 0.12, True, "down")
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
            audio.scene("BATTLE")
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
