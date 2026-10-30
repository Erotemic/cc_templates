"""Audio, challenge board and CLI work without a window or Panda3D."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

from fpx3d import audio, challenge

ROOT = Path(__file__).resolve().parents[1]


class Tests(unittest.TestCase):
    def test_headless_run(self):
        result = subprocess.run([sys.executable, 'main.py', '--headless',
                                 '--frames', '240'], cwd=ROOT, check=True,
                                capture_output=True, text=True)
        self.assertIn('frames=240', result.stdout)
        self.assertIn('prisms=', result.stdout)

    def test_missing_graphics_message_is_friendly(self):
        try:
            import panda3d
        except ImportError:
            result = subprocess.run([sys.executable, 'main.py', '--frames', '2'],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('panda3d', result.stderr.lower())

    def test_challenge_catalog(self):
        self.assertGreaterEqual(len(challenge.CHALLENGES), 15)
        self.assertEqual(len(challenge.CODE_DETECTIVE), 5)
        result = subprocess.run([sys.executable, '-m', 'fpx3d.challenge'],
                                cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertIn('INDEPENDENT CHALLENGES', result.stdout)
        self.assertIn('A generated vault', result.stdout)

    def test_original_audio_has_valid_pcm(self):
        song = audio.make_music()
        self.assertGreater(len(song) / audio.SAMPLE_RATE, 7)
        self.assertLess(len(song) / audio.SAMPLE_RATE, 10)
        for event in audio.SOUND_NAMES:
            self.assertGreater(len(audio.make_effect(event)), 1200)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'short.wav'
            audio.write_wav(path, song[:1000])
            with wave.open(str(path), 'rb') as reader:
                self.assertEqual(reader.getnchannels(), 2)
                self.assertEqual(reader.getsampwidth(), 2)
                self.assertEqual(reader.getframerate(), audio.SAMPLE_RATE)
                self.assertEqual(reader.getnframes(), 1000)


if __name__ == '__main__':
    unittest.main()
