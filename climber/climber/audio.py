"""Optional pygame mixer playback of in-memory original sounds.

The simulation writes event names like "jump" into ``game.events``.
This module plays pre-synthesized pygame sounds for those events without
adding pygame as a dependency of the physics code or requiring audio files.
"""

from __future__ import annotations

from . import student, synth

EFFECTS = ("jump", "land", "hurt", "reset", "milestone", "pickup",
           "heckler_mumble_1", "heckler_mumble_2", "heckler_mumble_3")


class SoundBoard:
    """Loop background music, play effects, and remain usable without audio."""

    def __init__(self, pygame_module):
        self._pygame = pygame_module
        self.available = False
        self.muted = False
        self._music_channel = None
        self._effects = {}
        self._music = None

        try:
            mixer = pygame_module.mixer
            config = mixer.get_init()
            if config is None:
                return  # No working sound device; keep the game playable.
            sample_rate, sample_format, channels = config
            if sample_format != -16 or channels not in (1, 2):
                # The game asks for -16 / stereo via pre_init(). A different
                # format is not safe to feed 16-bit audio bytes into.
                print("Sound disabled (unsupported mixer format).")
                return

            # Sound(buffer=...) accepts raw PCM. Nothing is written to disk.
            self._effects = {
                name: mixer.Sound(buffer=synth.to_pcm16(
                    synth.make_effect(name, sample_rate), channels))
                for name in EFFECTS
            }
            # Quiet, short synth blips accompany every few typed letters.
            # No voice recordings or sound assets are needed.
            for name in EFFECTS:
                if name.startswith("heckler_mumble_"):
                    self._effects[name].set_volume(0.24)
            self._music = mixer.Sound(buffer=synth.to_pcm16(
                synth.make_music(sample_rate), channels))
            mixer.set_reserved(1)  # Leave channel 0 exclusively for music.
            channel = mixer.Channel(0)
            channel.set_volume(student.MUSIC_VOLUME)
            channel.play(self._music, loops=-1)
            self._music_channel = channel
            self.available = True
        except (OSError, ValueError, pygame_module.error) as error:
            print(f"Sound disabled ({error}).")

    @property
    def label(self) -> str:
        if not self.available:
            return "N/A"
        return "OFF" if self.muted else "ON"

    def toggle_mute(self) -> None:
        """M pauses the music and suppresses effects until pressed again."""
        self.muted = not self.muted
        if self._music_channel is not None:
            if self.muted:
                self._music_channel.pause()
            else:
                self._music_channel.unpause()

    def play_events(self, events) -> None:
        """Play events emitted by the pygame-independent simulation."""
        if self.muted or not self.available:
            return
        for event in events:
            sound = self._effects.get(event)
            if sound is not None:
                sound.play()

    def close(self) -> None:
        if self._music_channel is not None:
            self._music_channel.stop()
