"""Tests for two new teaching hooks and optional sound playback."""

from __future__ import annotations

import types
import unittest
from unittest.mock import patch

from climber import settings, student, synth, world
from climber.audio import EFFECTS, SoundBoard
from climber.engine import Controls, Game, Player, update


class PlatformExerciseTests(unittest.TestCase):
    def test_blue_platform_visible_at_beginning(self):
        game = Game()
        blue = game.nearby_moving_platforms()
        self.assertIn(2, [p.tier for p in blue])
        for platform in blue:
            self.assertGreaterEqual(platform.x, platform.left_limit)
            self.assertLessEqual(platform.x, platform.right_limit)
            self.assertGreaterEqual(platform.left_limit, settings.LEFT_WALL)
            self.assertLessEqual(platform.right_limit + platform.width,
                                 settings.RIGHT_WALL)

    def test_moving_platforms_are_bounded_at_high_altitudes(self):
        game = Game()
        for tier in range(1, 2000, 23):
            game.camera_y = world.main_platform(tier).y - 200
            blue = game.nearby_moving_platforms()
            self.assertLessEqual(len(blue), 4)
            self.assertLessEqual(len(game.moving_platforms), 4)
            for platform in blue:
                self.assertGreater(platform.right_limit, platform.left_limit)

    def test_student_platform_movement_hook_is_connected(self):
        game = Game()
        platform = next(p for p in game.nearby_moving_platforms()
                        if p.tier == 2)
        initial_x = platform.x

        def animate_platform(platform, seconds):
            platform.x += platform.direction * platform.speed * seconds

        with patch.object(student, "move_platform", animate_platform):
            update(game, Controls(), 0.02)
        self.assertGreater(platform.x, initial_x)

    def test_player_is_carried_horizontally(self):
        game = Game()
        platform = next(p for p in game.nearby_moving_platforms()
                        if p.tier == 2)
        game.player = Player(x=platform.x + 30,
                             y=platform.y - settings.PLAYER_HEIGHT,
                             on_ground=True)
        start_x, start_y = game.player.x, game.player.y

        def animate_platform(platform, seconds):
            platform.x += 30 * seconds

        with patch.object(student, "move_platform", animate_platform):
            update(game, Controls(), 0.02)
        self.assertAlmostEqual(game.player.x, start_x + 0.6)
        self.assertAlmostEqual(game.player.y, start_y)
        self.assertTrue(game.player.on_ground)

    def test_platform_is_not_required_for_main_route(self):
        game = Game()
        for tier in (2, 8, 14, 20, 26, 32):
            game.camera_y = world.main_platform(tier).y - 250
            main_before = world.main_platform(tier)
            game.nearby_moving_platforms()
            self.assertEqual(main_before, world.main_platform(tier))


class GeneratorExerciseTests(unittest.TestCase):
    def test_zero_offset_keeps_original_even_tier_heights(self):
        # Explicitly test the starter formula. The student is allowed to
        # replace the default hook with a valid noisy offset.
        with patch.object(student, "platform_height_offset",
                          lambda tier, noise: 0.0):
            for tier in range(1, 200):
                self.assertEqual(world.main_platform(tier).y,
                                 settings.GROUND_Y - tier * settings.TIER_HEIGHT)

    def test_height_offset_hook_changes_spacings_and_is_reachable(self):
        def height_offset(tier, noise):
            return 16 * noise

        with patch.object(student, "platform_height_offset", height_offset):
            y_values = [world.main_platform(tier).y
                        for tier in range(1, 2001)]
            gaps = [a - b for a, b in zip(y_values, y_values[1:])]
            self.assertGreater(max(gaps) - min(gaps), 8.0)
            self.assertGreater(min(gaps), 60.0)
            self.assertLess(max(gaps), 150.0)
            # Generating a very distant tier doesn't need to visit all
            # previous tiers or remember any of them.
            high = world.main_platform(1_000_000)
            self.assertEqual(high, world.main_platform(1_000_000))

    def test_height_offset_works_with_ladders_and_streaming(self):
        with patch.object(student, "platform_height_offset",
                          lambda tier, noise: 18 * noise):
            for tier in range(1, 100):
                main = world.main_platform(tier)
                ladder = world.ladder_to(tier)
                self.assertLess(ladder.top, main.y)
                self.assertGreater(ladder.bottom, main.y)
                near = world.platforms_near(main.y - 40, main.y + 40)
                self.assertIn(main, near)


class EventSoundTests(unittest.TestCase):
    def test_jump_and_land_events(self):
        game = Game()
        update(game, Controls(jump_pressed=True), 1 / 60)
        self.assertIn("jump", game.events)
        seen_land = False
        for _ in range(90):
            update(game, Controls(), 1 / 60)
            seen_land |= "land" in game.events
        self.assertTrue(seen_land)
        game.reset()
        self.assertIn("reset", game.events)

    def test_generated_audio_has_expected_duration_and_no_clipping(self):
        # Synthesis happens at startup: it does not need pygame or disk files.
        music = synth.make_music()
        duration = len(music) / synth.SAMPLE_RATE
        self.assertGreater(duration, 8)
        self.assertLess(duration, 12)
        self.assertGreater(max(abs(value) for value in music), 0.08)
        for name in EFFECTS:
            effect = synth.make_effect(name)
            min_duration = 0.05 if name.startswith("heckler_mumble_") else 0.09
            self.assertGreater(len(effect) / synth.SAMPLE_RATE, min_duration)
            self.assertLess(len(effect) / synth.SAMPLE_RATE, 0.8)
            self.assertTrue(any(effect))
        with self.assertRaises(KeyError):
            synth.make_effect("not_an_event")

    def test_pcm16_mono_and_stereo_are_signed_samples(self):
        from array import array

        mono = synth.to_pcm16([0, 0.5, -0.5], channels=1)
        stereo = synth.to_pcm16([0, 0.5, -0.5], channels=2)
        self.assertEqual(len(mono), 3 * 2)  # 16 bits = 2 bytes
        self.assertEqual(len(stereo), 3 * 2 * 2)
        values = array("h")
        values.frombytes(stereo)
        self.assertEqual(values[0::2], values[1::2])
        self.assertEqual(values[0], 0)
        self.assertGreater(values[2], 0)
        self.assertLess(values[4], 0)
        with self.assertRaises(ValueError):
            synth.to_pcm16([0.5], channels=3)

    def test_no_sound_device_does_not_crash(self):
        mixer = types.SimpleNamespace(get_init=lambda: None)
        fake_pygame = types.SimpleNamespace(mixer=mixer, error=RuntimeError)
        audio = SoundBoard(fake_pygame)
        self.assertEqual(audio.label, "N/A")
        audio.play_events(["jump", "hurt"])
        audio.toggle_mute()
        audio.close()

    def test_audio_playback_and_muting_without_real_hardware(self):
        # Fake PCM-aware mixer catches regressions even when pygame is absent.
        class FakeSound:
            def __init__(self, *, buffer):
                self.pcm = buffer
                self.plays = 0
                self.volume = 1.0
                self.assert_buffer()

            def assert_buffer(self):
                if not isinstance(self.pcm, bytes) or not self.pcm:
                    raise ValueError("pygame.Sound needs nonempty PCM bytes")

            def play(self):
                self.plays += 1

            def set_volume(self, volume):
                self.volume = volume

        class FakeChannel:
            def __init__(self):
                self.music = None
                self.loops = None
                self.paused = False
                self.stopped = False
                self.volume = None

            def set_volume(self, volume):
                self.volume = volume

            def play(self, sound, loops=0):
                self.music = sound
                self.loops = loops

            def pause(self):
                self.paused = True

            def unpause(self):
                self.paused = False

            def stop(self):
                self.stopped = True

        channel = FakeChannel()
        sounds = []

        def load(*, buffer):
            sound = FakeSound(buffer=buffer)
            sounds.append(sound)
            return sound

        mixer = types.SimpleNamespace(
            get_init=lambda: (22050, -16, 2),
            Sound=load, set_reserved=lambda count: self.assertEqual(count, 1),
            Channel=lambda index: channel,
        )
        fake_pygame = types.SimpleNamespace(mixer=mixer, error=RuntimeError)
        # Keep this wiring test fast; synthesis itself has an independent
        # full-duration test above.
        with patch.object(synth, "make_music", return_value=[0.0, 0.25, 0.0]), \
             patch.object(synth, "make_effect", return_value=[0.0, 0.5, 0.0]):
            audio = SoundBoard(fake_pygame)
        self.assertTrue(audio.available)
        self.assertEqual(audio.label, "ON")
        self.assertEqual(len(sounds), len(EFFECTS) + 1)
        self.assertEqual(len(sounds[0].pcm), 3 * 2 * 2)
        self.assertEqual(channel.loops, -1)
        self.assertIs(channel.music, sounds[-1])
        self.assertEqual(channel.volume, student.MUSIC_VOLUME)
        audio.play_events(["jump", "land", "nothing"])
        self.assertEqual(audio._effects["jump"].plays, 1)
        self.assertEqual(audio._effects["land"].plays, 1)
        self.assertEqual(audio._effects["heckler_mumble_1"].volume, 0.24)
        audio.play_events(["heckler_mumble_1"])
        self.assertEqual(audio._effects["heckler_mumble_1"].plays, 1)
        audio.toggle_mute()
        self.assertTrue(channel.paused)
        self.assertEqual(audio.label, "OFF")
        audio.play_events(["jump"])
        self.assertEqual(audio._effects["jump"].plays, 1)
        audio.toggle_mute()
        self.assertFalse(channel.paused)
        audio.play_events(["jump"])
        self.assertEqual(audio._effects["jump"].plays, 2)
        audio.close()
        self.assertTrue(channel.stopped)

    def test_unsupported_mixer_does_not_crash(self):
        mixer = types.SimpleNamespace(get_init=lambda: (22050, 8, 2))
        fake_pygame = types.SimpleNamespace(mixer=mixer, error=RuntimeError)
        audio = SoundBoard(fake_pygame)
        self.assertFalse(audio.available)
        self.assertEqual(audio.label, "N/A")
        audio.close()


if __name__ == "__main__":
    unittest.main()
