"""Check synthetic audio without installing pygame or needing speakers."""

import types
import unittest
from array import array
from unittest.mock import patch

from platformer import sound


class SynthTests(unittest.TestCase):
    def test_music_has_melody_and_loop_duration(self):
        samples = sound.make_music()
        self.assertAlmostEqual(len(samples) / sound.SAMPLE_RATE,
                               len(sound.MELODY) * sound.NOTE_LENGTH,
                               delta=0.001)
        self.assertGreater(max(samples), 0.04)
        self.assertLess(max(abs(value) for value in samples), 1.0)
        self.assertAlmostEqual(sound.pitch(69), 440)

    def test_custom_melody_can_have_a_different_length(self):
        custom = (60, 64, 67, 72, 71, 67, 64, 60)
        music = sound.make_music(sample_rate=4000, melody=custom)
        self.assertAlmostEqual(len(music) / 4000,
                               len(custom) * sound.NOTE_LENGTH,
                               delta=0.001)
        with self.assertRaises(ValueError):
            sound.make_music(sample_rate=4000, melody=())

    def test_each_effect_is_a_nonempty_pcm_buffer(self):
        self.assertGreaterEqual(len(sound.EFFECTS), 5)
        for name in sound.EFFECTS:
            samples = sound.make_effect(name)
            self.assertGreater(len(samples), 1000)
            self.assertGreater(max(abs(value) for value in samples), 0.01)
            self.assertEqual(len(sound.pcm16(samples)), len(samples) * 4)
        with self.assertRaises(KeyError):
            sound.make_effect("unknown")

    def test_pcm_is_signed_and_stereo(self):
        stereo = array("h")
        stereo.frombytes(sound.pcm16([0.0, 0.5, -0.5], 2))
        self.assertEqual(stereo[0], 0)
        self.assertEqual(stereo[0::2], stereo[1::2])
        self.assertGreater(stereo[2], 0)
        self.assertLess(stereo[4], 0)
        with self.assertRaises(ValueError):
            sound.pcm16([1.0], 3)

    def test_mixer_plays_music_effects_and_mutes(self):
        class FakeSound:
            def __init__(self, *, buffer):
                self.buffer = buffer
                self.count = 0

            def play(self):
                self.count += 1

        class FakeChannel:
            def __init__(self):
                self.played = None
                self.volume = None
                self.paused = False
                self.stopped = False

            def set_volume(self, value):
                self.volume = value

            def play(self, value, loops=0):
                self.played = (value, loops)

            def pause(self):
                self.paused = True

            def unpause(self):
                self.paused = False

            def stop(self):
                self.stopped = True

        channel = FakeChannel()
        fake = types.SimpleNamespace(
            error=RuntimeError,
            mixer=types.SimpleNamespace(
                get_init=lambda: (22050, -16, 2),
                Sound=FakeSound,
                Channel=lambda index: channel,
                set_reserved=lambda count: self.assertEqual(count, 1),
            ),
        )
        with patch.object(sound, "make_music", return_value=[0.2, 0.0]), \
             patch.object(sound, "make_effect", return_value=[0.3, 0.0]):
            audio = sound.SoundBoard(fake)
        self.assertTrue(audio.available)
        self.assertEqual(channel.played[1], -1)
        self.assertIs(channel.played[0], audio._music)
        audio.play(["jump", "star"])
        self.assertEqual(audio.effects["jump"].count, 1)
        original_music = audio._music
        # Mission 7: a student can add a new track for level 2.
        with patch.object(sound.student, "level_melody",
                          side_effect=lambda index: (69, 72, 76, 74) if index == 1 else None):
            audio.set_level(1)
            self.assertIsNot(audio._music, original_music)
            playing = audio._music
            audio.set_level(1)  # Should not restart or re-generate every frame.
            self.assertIs(audio._music, playing)
            audio.set_level(0)
            self.assertIs(audio._music, original_music)
        audio.toggle_mute()
        self.assertTrue(channel.paused)
        audio.play(["star"])
        self.assertEqual(audio.effects["star"].count, 1)
        audio.toggle_mute()
        self.assertFalse(channel.paused)
        audio.play(["star"])
        self.assertEqual(audio.effects["star"].count, 2)
        audio.close()
        self.assertTrue(channel.stopped)

    def test_no_audio_device_is_safe(self):
        fake = types.SimpleNamespace(
            error=RuntimeError,
            mixer=types.SimpleNamespace(get_init=lambda: None),
        )
        audio = sound.SoundBoard(fake)
        self.assertFalse(audio.available)
        audio.play(["jump"])
        audio.toggle_mute()
        audio.close()


if __name__ == "__main__":
    unittest.main()
