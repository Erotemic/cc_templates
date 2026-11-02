"""The floor piano is scenery until student collision and tone code is implemented."""

import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ["SDL_AUDIODRIVER"] = "dummy"
from undercode.app import Game
from undercode.audio import Audio
from undercode import student_overworld
from undercode.overworld.engine import tile_center
from undercode.exercises import check_piano
from teacher import solutions


class PianoTests(unittest.TestCase):
    def test_keys_do_not_automatically_detect_collision_or_queue_tones(self):
        """No hidden trigger can complete the task if the student's function does nothing."""

        def unfinished(*, world):
            """Represent unfinished student work even after a student edits the shipped stub."""
            pass

        with patch.object(student_overworld, "update_piano", unfinished):
            game = Game()
            self.assertEqual(len(game.world.piano_keys), 8)
            game.world.position = tile_center(tile=game.world.piano_keys[0].tile)
            for _ in range(3):
                game.update(seconds=1 / 60)
            self.assertFalse(game.tones)
            self.assertIsNone(game.world.piano_key)
            self.assertTrue(any(not ok for ok, _ in check_piano()))

    @patch.object(student_overworld, "update_piano", solutions.update_piano)
    def test_completed_collision_rule_distinguishes_body_overlap_from_nearness(self):
        game = Game()
        world = game.world
        rect = world.tile_rect(tile=world.piano_keys[0].tile)
        world.position.x = rect.left - 9
        world.position.y = rect.centery
        game.update(seconds=0)
        self.assertFalse(game.tones)  # Body only touches the edge: no area overlap.
        world.position.x += 1
        game.update(seconds=0)
        self.assertEqual(len(game.tones), 1)
        self.assertAlmostEqual(game.tones[0].hz, 261.63)
        self.assertFalse(world.tones)  # Coordinator drained the request exactly once.

    @patch.object(student_overworld, "update_piano", solutions.update_piano)
    def test_each_key_plays_once_until_exit_and_reentry_and_restart_clears_memory(self):
        self.assertTrue(all(ok for ok, _ in check_piano()))
        game = Game()
        for key, expected in zip(
            game.world.piano_keys, (261.63, 293.66, 329.63, 349.23, 392, 440, 493.88, 523.25)
        ):
            game.world.position = tile_center(tile=key.tile)
            game.update(seconds=1 / 60)
            self.assertEqual(len(game.tones), 1)
            self.assertAlmostEqual(game.tones[0].hz, expected)
            game.tones.clear()  # What the window adapter does after playing requests.
            for _ in range(10):
                game.update(seconds=1 / 60)
            self.assertFalse(game.tones)
        game.world.position = tile_center(tile=game.world.room.spawns["camp"])
        game.update(seconds=0)
        self.assertIsNone(game.world.piano_key)
        game.world.position = tile_center(tile=game.world.piano_keys[-1].tile)
        game.update(seconds=0)
        self.assertEqual(len(game.tones), 1)
        game.restart()
        self.assertIsNone(game.world.piano_key)
        self.assertFalse(game.tones)

    def test_worked_c4_and_exact_notice_are_in_the_starting_room(self):
        """The supplied head start works in normal play, alongside the requested sign."""
        from undercode.overworld.model import Sign

        game = Game()
        self.assertEqual(game.world.room_key, "courtyard")
        notices = [obj for obj in game.world.room.objects if isinstance(obj.definition, Sign)]
        self.assertTrue(
            any(
                obj.definition.dialogue.text
                == "A piano, but most of the keys seem broken. Maybe we can fix it?"
                for obj in notices
            )
        )
        # Run the actual student file's function, without replacing it with an answer.
        game.world.position = tile_center(tile=game.world.piano_keys[0].tile)
        game.update(seconds=0)
        self.assertEqual(len(game.tones), 1)
        self.assertAlmostEqual(game.tones[0].hz, 261.63)
        game.tones.clear()
        game.update(seconds=0)
        self.assertFalse(game.tones)
        # Remaining keys are intentionally left to students; no assertion freezes
        # those unfinished answers, so completing the task keeps this suite usable.

    def test_audio_adapter_generates_and_reuses_the_requested_pitch_and_respects_mute(self):
        import pygame

        audio = Audio()
        try:
            self.assertTrue(audio.enabled)
            with patch.object(audio, "tone", wraps=audio.tone) as synthesize:
                audio.play_tone(hz=261.63, duration=0.4)
                audio.play_tone(hz=261.63, duration=0.4)
                synthesize.assert_called_once_with(hz=261.63, duration=0.4)
                self.assertTrue(any(audio.note_sounds[(261.63, 0.4)].get_raw()))
                audio.toggle()
                audio.play_tone(hz=440, duration=0.4)
                self.assertEqual(synthesize.call_count, 1)
            silent = Audio(enabled=False)
            silent.play_tone(hz=440)
            self.assertFalse(silent.note_sounds)
        finally:
            pygame.mixer.quit()


if __name__ == "__main__":
    unittest.main()
