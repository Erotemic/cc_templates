"""Original, procedurally composed audio. No sound assets in this repository.

Panda3D's loader accepts sound filenames, so we create small WAVs at runtime
in the user's cache, never in the project. The game works without audio.
"""

from __future__ import annotations

from array import array
from math import exp, pi, sin
import hashlib
from pathlib import Path
import wave

from . import settings

SAMPLE_RATE = 22_050
BEAT = 60 / 112
SOUND_NAMES = ("core", "bonus", "jump", "spring", "hurt", "portal",
               "checkpoint", "respawn", "win", "lose")
# Changing notes/rhythms in this Python file creates a fresh cache name,
# so students HEAR their edits without needing to find/delete old audio.
SYNTH_VERSION = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:10]


def _frequency(midi: int) -> float:
    return 440 * 2 ** ((midi - 69) / 12)


def _note(samples: list[float], start: float, duration: float,
          midi: int, volume: float) -> None:
    length = len(samples)
    first = round(start * SAMPLE_RATE)
    for i in range(round(duration * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        attack = min(1.0, t / .012)
        release = max(0.0, min(1.0, (duration - t) / .1))
        env = attack * release * exp(-t * 2.3)
        phase = 2 * pi * _frequency(midi) * t
        samples[(first + i) % length] += volume * env * (sin(phase) + .18 * sin(2*phase))


def make_music() -> list[float]:
    """Four-bar D minor loop; its chords and melody are original to this game."""
    samples = [0.0] * round(16 * BEAT * SAMPLE_RATE)
    bars = (
        ((50, 53, 57), 38, (74, 77, 81, 77)),
        ((46, 50, 53), 34, (77, 74, 70, 74)),
        ((43, 46, 50), 31, (74, 70, 67, 70)),
        ((45, 49, 52), 33, (69, 73, 76, 73)),
    )
    for bar, (chord, bass, melody) in enumerate(bars):
        start = bar * 4 * BEAT
        for pitch in chord:
            _note(samples, start, 4 * BEAT, pitch, .02)
        for beat in (0, 2):
            _note(samples, start + beat * BEAT, BEAT, bass, .11)
        for i in range(8):
            _note(samples, start + i * BEAT / 2, .42 * BEAT,
                  chord[i % 3] + 24, .075)
        for i, pitch in enumerate(melody):
            _note(samples, start + (i + .15) * BEAT, .68 * BEAT, pitch, .04)
    return samples


def make_effect(kind: str) -> list[float]:
    durations = {"core": .26, "bonus": .20, "jump": .15, "spring": .24,
                 "hurt": .28, "portal": .55, "checkpoint": .33,
                 "respawn": .30, "win": .8, "lose": .5}
    duration = durations[kind]
    samples = []
    phase = 0.0
    for i in range(round(duration * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        u = t / duration
        if kind == "jump":
            hz = 280 + u * 320
        elif kind == "spring":
            hz = 240 + u * 780
        elif kind in {"hurt", "lose", "respawn"}:
            hz = 360 - u * 240
        elif kind in {"core", "bonus"}:
            hz = 560 + 370 * u
        else:
            seq = (62, 65, 69, 74)
            hz = _frequency(seq[min(3, int(u * 4))])
        phase += 2 * pi * hz / SAMPLE_RATE
        envelope = min(1.0, t / .012) * (1-u)**1.6
        samples.append(.24 * envelope * (sin(phase) + .18 * sin(2 * phase)))
    return samples


def write_wav(path: Path, samples: list[float]) -> None:
    """Stereo 16-bit PCM. Output is cached outside the source tree."""
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = max((abs(s) for s in samples), default=0)
    gain = min(1.0, .88 / peak) if peak else 1.0
    pcm = array("h")
    for sample in samples:
        value = round(max(-1, min(1, sample * gain)) * 32767)
        pcm.append(value)
        pcm.append(value)
    # WAV is little endian regardless of CPU architecture.
    import sys
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(path), "wb") as file:
        file.setnchannels(2)
        file.setsampwidth(2)
        file.setframerate(SAMPLE_RATE)
        file.writeframes(pcm.tobytes())


class GameAudio:
    """Play original tunes through Panda3D; never block gameplay on audio."""

    def __init__(self, game) -> None:
        self.game = game
        self.cache = Path.home() / ".cache" / "fpx3d" / "audio"
        self.music = None
        self.effects = {}
        self.muted = False
        self.available = bool(settings.AUDIO_ENABLED)
        if not self.available:
            return
        try:
            path = self.cache / f"prism-vault-music-{SYNTH_VERSION}.wav"
            if not path.is_file():
                write_wav(path, make_music())
            self.music = game.loader.loadMusic(str(path))
            self.music.setLoop(True)
            self.music.setVolume(settings.MUSIC_VOLUME)
            self.music.play()
        except (OSError, ValueError, AttributeError, RuntimeError) as error:
            print(f"Audio unavailable ({error}); continuing silently.")
            self.available = False

    def play(self, event: str) -> None:
        if not self.available or self.muted or event not in SOUND_NAMES:
            return
        try:
            sound = self.effects.get(event)
            if sound is None:
                path = self.cache / f"prism-vault-{event}-{SYNTH_VERSION}.wav"
                if not path.is_file():
                    write_wav(path, make_effect(event))
                sound = self.game.loader.loadSfx(str(path))
                sound.setVolume(settings.SFX_VOLUME)
                self.effects[event] = sound
            sound.play()
        except (OSError, ValueError, AttributeError, RuntimeError) as error:
            print(f"Sound effect unavailable ({error}).")
            self.available = False

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        if self.music is not None:
            if self.muted:
                self.music.stop()
            else:
                self.music.play()

    def close(self) -> None:
        if self.music is not None:
            self.music.stop()
