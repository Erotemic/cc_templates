"""Original music and sound effects generated in memory from Python code.

No sound files, media converters, or NumPy are required. pygame.mixer.Sound
plays the bytes returned by ``to_pcm16()``. Students can change the MIDI
note numbers below to compose their own music; restart the game to hear it.

Audio math: one musical note is a sine wave whose frequency depends on its
pitch. Envelopes make each note start and finish softly instead of clicking.
"""

from __future__ import annotations

from array import array
from math import exp, pi, sin
from random import Random

SAMPLE_RATE = 22050


def frequency(midi: int) -> float:
    """Convert a piano key number to frequency in hertz (A4=440)."""
    return 440 * 2 ** ((midi - 69) / 12)


def add_note(samples, start, length, midi, volume, *,
             sample_rate, shape="bell"):
    """Mix a short generated note into a looping song.

    Modulo wraps the end of a note around to the start of the song, so a
    loop doesn't cut off reverb or produce a click at its boundary.
    """
    sr = sample_rate
    first = round(start * sr)
    count = round(length * sr)
    hz = frequency(midi)
    for index in range(count):
        t = index / sr
        attack = min(1.0, t / 0.013)
        fade_out = min(1.0, (length - t) / 0.09)
        decay = exp(-t * (3.9 if shape == "bell" else 1.0))
        phase = 2 * pi * hz * t
        if shape == "bass":
            wave_value = sin(phase) + 0.18 * sin(phase * 2)
        elif shape == "pad":
            wave_value = sin(phase) + 0.16 * sin(phase * 2)
        else:
            wave_value = (sin(phase) + 0.24 * sin(phase * 2)
                          + 0.10 * sin(phase * 3))
        samples[(first + index) % len(samples)] += (
            volume * attack * fade_out * decay * wave_value
        )


def make_music(sample_rate: int = SAMPLE_RATE):
    """An original four-bar minor-key exploration loop (~8.6 seconds)."""
    beat = 60 / 112
    bars = 4
    samples = [0.0] * round(bars * 4 * beat * sample_rate)
    # MIDI notes: Dm, Bb, Gm, A. Four bars, looping back to Dm.
    chords = [
        ((50, 53, 57), 38, (74, 77, 81, 77)),
        ((46, 50, 53), 34, (77, 74, 70, 74)),
        ((43, 46, 50), 31, (74, 70, 67, 70)),
        ((45, 49, 52), 33, (69, 73, 76, 73)),
    ]
    for bar, (chord, bass, melody) in enumerate(chords):
        start = bar * 4 * beat
        for note in chord:
            add_note(samples, start, 4 * beat, note, 0.024,
                     sample_rate=sample_rate, shape="pad")
        for offset in (0, 2):
            add_note(samples, start + offset * beat, 0.95 * beat,
                     bass, 0.14, sample_rate=sample_rate, shape="bass")
        for step in range(8):
            note = chord[(step + (step // 4)) % 3] + 24
            add_note(samples, start + step * beat / 2,
                     beat * 0.42, note, 0.082,
                     sample_rate=sample_rate, shape="bell")
        for step, note in enumerate(melody):
            add_note(samples, start + (step + 0.18) * beat,
                     0.62 * beat, note, 0.043,
                     sample_rate=sample_rate, shape="bell")
    # Soft, reproducible tick on offbeats; no sampled drum recordings.
    rng = Random(77)
    for beat_index in range(16):
        for offset in (0, 0.5):
            start = round((beat_index + offset) * beat * sample_rate)
            for i in range(round(0.035 * sample_rate)):
                t = i / sample_rate
                volume = (0.012 if offset == 0 else 0.019) * exp(-t * 85)
                samples[(start + i) % len(samples)] += (
                    volume * rng.uniform(-1.0, 1.0)
                )
    return samples


def make_effect(name: str, sample_rate: int = SAMPLE_RATE):
    """Simple synthetic effects: an upward chirp, landing, hit, and reward."""
    durations = {"jump": 0.18, "land": 0.11, "hurt": 0.32,
                 "reset": 0.27, "milestone": 0.55, "pickup": 0.21,
                 "heckler_mumble_1": 0.082,
                 "heckler_mumble_2": 0.082,
                 "heckler_mumble_3": 0.082}
    duration = durations[name]
    samples = [0.0] * round(duration * sample_rate)
    rng = Random(48)
    phase = 0.0
    for i in range(len(samples)):
        t = i / sample_rate
        u = t / duration
        if name == "jump":
            hz = 290 + 510 * (u ** 1.4)
            env = (1 - u) ** 1.6
            amp = 0.28
        elif name == "land":
            hz = 145 - 75 * u
            env = (1 - u) ** 2.8
            amp = 0.24
        elif name == "hurt":
            hz = 360 - 270 * u
            env = (1 - u) ** 1.2
            amp = 0.28
        elif name == "reset":
            hz = 400 - 200 * u
            env = (1 - u) ** 1.8
            amp = 0.21
        elif name == "pickup":
            hz = 520 + 240 * u
            env = (1 - u) ** 1.4
            amp = 0.18
        elif name.startswith("heckler_mumble_"):
            variant = int(name[-1]) - 1
            hz = (185, 220, 202)[variant] + 29 * sin(2 * pi * 11 * t) - 24 * u
            env = (1 - u) ** 2.1
            amp = 0.13
        else:
            # Short major arpeggio signals every ten tiers.
            melody = (74, 78, 81, 86)  # D F# A D
            hz = frequency(melody[min(3, int(u * 4))])
            env = (1 - u) * (0.7 + 0.3 * sin(pi * 4 * u) ** 2)
            amp = 0.20
        phase += 2 * pi * hz / sample_rate
        attack = min(1.0, t / 0.008)
        tone = sin(phase) + 0.15 * sin(2 * phase)
        if name in {"land", "hurt"}:
            tone += (0.1 if name == "land" else 0.18) * rng.uniform(-1, 1)
        elif name.startswith("heckler_mumble_"):
            tone += 0.34 * sin(3 * phase)  # Small nasal, cartoon-mumble timbre.
        samples[i] = amp * attack * env * tone
    return samples


def to_pcm16(samples: list[float], channels: int = 2) -> bytes:
    """Convert floating-point samples to signed 16-bit PCM for SDL's mixer.

    With stereo audio, each mono sample is repeated in both speakers.
    array('h') writes native-endian 16-bit values, as SDL's -16 mixer expects.
    """
    if channels not in (1, 2):
        raise ValueError("Only mono and stereo mixers are supported")
    peak = max((abs(value) for value in samples), default=0.0)
    gain = min(1.0, 0.88 / peak) if peak else 1.0
    pcm = array("h")
    for value in samples:
        amplitude = round(max(-1.0, min(1.0, value * gain)) * 32767)
        for _ in range(channels):
            pcm.append(amplitude)
    return pcm.tobytes()
