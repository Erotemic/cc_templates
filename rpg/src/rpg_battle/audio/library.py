from __future__ import annotations

from array import array
from dataclasses import dataclass
from pathlib import Path
import math
import random

import numpy as np

SAMPLE_RATE = 44100
MAX_I16 = 32767


@dataclass(frozen=True)
class GeneratedTrackSpec:
    builder: str
    volume: float = 0.4


@dataclass(frozen=True)
class FileTrackSpec:
    path: str | Path
    volume: float = 0.5


@dataclass(frozen=True)
class SynthSoundSpec:
    waveform: str = "sine"
    frequency: float = 440.0
    duration: float = 0.12
    volume: float = 0.35
    attack: float = 0.004
    release: float = 0.05
    frequency_end: float | None = None
    duty_cycle: float = 0.5
    vibrato_hz: float = 0.0
    vibrato_depth: float = 0.0
    noise: float = 0.0


def note_to_frequency(note: str) -> float:
    names = {
        "C": 0,
        "C#": 1,
        "Db": 1,
        "D": 2,
        "D#": 3,
        "Eb": 3,
        "E": 4,
        "F": 5,
        "F#": 6,
        "Gb": 6,
        "G": 7,
        "G#": 8,
        "Ab": 8,
        "A": 9,
        "A#": 10,
        "Bb": 10,
        "B": 11,
    }
    if note == "R":
        return 0.0
    name = note[0]
    octave_str = note[1:]
    if len(note) >= 3 and note[1] in {"#", "b"}:
        name = note[:2]
        octave_str = note[2:]
    octave = int(octave_str)
    midi = 12 * (octave + 1) + names[name]
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def _adsr(level: float, pos: int, length: int, attack: int, release: int) -> float:
    if length <= 0:
        return 0.0
    if attack > 0 and pos < attack:
        return level * (pos / max(1, attack))
    if release > 0 and pos >= length - release:
        return level * max(0.0, (length - pos) / max(1, release))
    return level


def _sample_wave(phase: float, waveform: str, duty_cycle: float) -> float:
    phase = phase % 1.0
    if waveform == "square":
        return 1.0 if phase < duty_cycle else -1.0
    if waveform == "triangle":
        return 1.0 - 4.0 * abs(phase - 0.5)
    if waveform == "saw":
        return 2.0 * phase - 1.0
    return math.sin(phase * math.tau)


def render_synth_sound(spec: SynthSoundSpec, sample_rate: int = SAMPLE_RATE) -> array:
    sample_count = max(1, int(spec.duration * sample_rate))
    attack = int(spec.attack * sample_rate)
    release = int(spec.release * sample_rate)
    phase = 0.0
    data = array("h")
    rng = random.Random(1337)
    end_frequency = spec.frequency_end if spec.frequency_end is not None else spec.frequency
    for i in range(sample_count):
        t = i / max(1, sample_count - 1)
        frequency = spec.frequency + (end_frequency - spec.frequency) * t
        if spec.vibrato_hz and spec.vibrato_depth:
            frequency *= (
                1.0 + math.sin(math.tau * spec.vibrato_hz * (i / sample_rate)) * spec.vibrato_depth
            )
        phase += frequency / sample_rate
        sample = _sample_wave(phase, spec.waveform, spec.duty_cycle)
        if spec.noise:
            sample = sample * (1.0 - spec.noise) + rng.uniform(-1.0, 1.0) * spec.noise
        sample *= _adsr(spec.volume, i, sample_count, attack, release)
        value = int(max(-1.0, min(1.0, sample)) * MAX_I16)
        data.append(value)
        data.append(value)
    return data


def _mix_note(
    buffer: list[float],
    start_seconds: float,
    duration_seconds: float,
    frequency: float,
    volume: float,
    waveform: str,
) -> None:
    if frequency <= 0 or duration_seconds <= 0:
        return
    start = int(start_seconds * SAMPLE_RATE)
    count = int(duration_seconds * SAMPLE_RATE)
    if count <= 0:
        return
    attack = max(1, int(0.008 * SAMPLE_RATE))
    release = max(1, int(0.05 * SAMPLE_RATE))
    phase = 0.0
    for i in range(count):
        idx = start + i
        if idx >= len(buffer):
            break
        phase += frequency / SAMPLE_RATE
        sample = _sample_wave(phase, waveform, 0.5)
        if waveform == "sine":
            sample = (
                0.78 * sample
                + 0.18 * math.sin((phase * 2.0) % 1.0 * math.tau)
                + 0.08 * math.sin((phase * 3.0) % 1.0 * math.tau)
            )
        env = _adsr(volume, i, count, attack, release)
        buffer[idx] += sample * env


def render_battle_loop_prototype(sample_rate: int = SAMPLE_RATE, volume: float = 0.4) -> array:
    sixteenth = 60.0 / (132.0 * 6.0)
    bar_units = 18
    total_units = bar_units * 16
    total_samples = int(total_units * sixteenth * sample_rate)
    buffer = [0.0] * total_samples

    motif_a = [
        (0, "B4", 2, 0.26),
        (2, "B4", 1, 0.22),
        (3, "G4", 1, 0.18),
        (4, "B4", 2, 0.24),
        (6, "D5", 3, 0.28),
        (9, "B4", 3, 0.2),
        (12, "D5", 1, 0.22),
        (13, "B4", 1, 0.16),
        (14, "D5", 2, 0.22),
        (16, "F#5", 6, 0.3),
        (22, "D5", 5, 0.24),
    ]
    motif_b = [
        (0, "D5", 2, 0.22),
        (2, "D5", 1, 0.18),
        (3, "B4", 1, 0.16),
        (4, "D5", 2, 0.22),
        (6, "F#5", 3, 0.26),
        (9, "D5", 3, 0.2),
        (12, "F#5", 1, 0.22),
        (13, "D5", 1, 0.16),
        (14, "F#5", 2, 0.22),
        (16, "A5", 4, 0.28),
        (20, "F#5", 2, 0.22),
        (22, "D5", 2, 0.18),
    ]
    motif_c = [
        (0, "E5", 2, 0.22),
        (2, "E5", 1, 0.18),
        (3, "C#5", 1, 0.16),
        (4, "E5", 2, 0.22),
        (6, "G5", 3, 0.24),
        (9, "E5", 3, 0.2),
        (12, "G5", 1, 0.22),
        (13, "E5", 1, 0.16),
        (14, "F#5", 2, 0.22),
        (16, "A5", 2, 0.24),
        (18, "B5", 2, 0.26),
        (20, "A5", 2, 0.22),
        (22, "F#5", 2, 0.18),
    ]
    turnaround = [
        (0, "F#5", 2, 0.2),
        (2, "E5", 2, 0.18),
        (4, "D5", 2, 0.16),
        (6, "B4", 3, 0.14),
        (10, "D5", 2, 0.16),
        (12, "F#5", 2, 0.18),
        (14, "A5", 2, 0.16),
    ]
    phrases = [motif_a, motif_a, motif_b, motif_c, motif_a, motif_a, motif_b, turnaround]
    roots = ["B2", "B2", "G2", "D2", "E2", "F#2", "B2", "F#2"]

    for phrase_index, phrase in enumerate(phrases):
        phrase_offset = phrase_index * 2 * bar_units
        for start_unit, note, dur_units, note_volume in phrase:
            _mix_note(
                buffer,
                (phrase_offset + start_unit) * sixteenth,
                dur_units * sixteenth,
                note_to_frequency(note),
                note_volume,
                "sine",
            )
        root = roots[phrase_index]
        fifth_freq = note_to_frequency(root) * (2.0 ** (7.0 / 12.0))
        octave_freq = note_to_frequency(root) * 2.0
        for local in (0, bar_units):
            _mix_note(
                buffer,
                (phrase_offset + local + 0) * sixteenth,
                6 * sixteenth,
                note_to_frequency(root),
                0.14,
                "triangle",
            )
            _mix_note(
                buffer,
                (phrase_offset + local + 0) * sixteenth,
                6 * sixteenth,
                fifth_freq,
                0.06,
                "triangle",
            )
            _mix_note(
                buffer,
                (phrase_offset + local + 6) * sixteenth,
                6 * sixteenth,
                octave_freq,
                0.08,
                "triangle",
            )
            _mix_note(
                buffer,
                (phrase_offset + local + 12) * sixteenth,
                4 * sixteenth,
                fifth_freq,
                0.05,
                "triangle",
            )

    pcm = array("h")
    for sample in buffer:
        clamped = max(-1.0, min(1.0, sample * volume))
        value = int(clamped * MAX_I16)
        pcm.append(value)
        pcm.append(value)
    return pcm


# New track based on the user's softer dungeon-crawl proof of concept.
NOTE_INDEX = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _note_to_midi(note: str) -> int | None:
    if note == "R":
        return None
    if len(note) == 2:
        name = note[0]
        octave = int(note[1])
    else:
        name = note[:2]
        octave = int(note[2])
    return 12 * (octave + 1) + NOTE_INDEX[name]


def _midi_to_note(midi: int) -> str:
    return NAMES[midi % 12] + str(midi // 12 - 1)


def _transpose_note(note: str, semitones: int) -> str:
    if note == "R":
        return "R"
    midi = _note_to_midi(note)
    assert midi is not None
    return _midi_to_note(midi + semitones)


def _midi_to_freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def _stereoize(y: np.ndarray, pan: float = 0.0) -> np.ndarray:
    left = math.sqrt((1.0 - pan) / 2.0)
    right = math.sqrt((1.0 + pan) / 2.0)
    return np.column_stack([y * left, y * right]).astype(np.float32)


def _adsr_np(
    n: int, attack: float = 0.004, decay: float = 0.04, sustain: float = 0.72, release: float = 0.06
) -> np.ndarray:
    a = max(1, int(attack * SAMPLE_RATE))
    d = max(1, int(decay * SAMPLE_RATE))
    r = max(1, int(release * SAMPLE_RATE))
    s = max(0, n - a - d - r)
    env = np.concatenate(
        [
            np.linspace(0.0, 1.0, a, endpoint=False),
            np.linspace(1.0, sustain, d, endpoint=False),
            np.full(s, sustain, dtype=np.float32),
            np.linspace(sustain, 0.0, r, endpoint=True),
        ]
    ).astype(np.float32)
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    return env[:n]


def _pulse_wave(freq: float, t: np.ndarray, duty: float = 0.25) -> np.ndarray:
    phase = (freq * t) % 1.0
    return np.where(phase < duty, 1.0, -1.0).astype(np.float32)


def _triangle_wave(freq: float, t: np.ndarray) -> np.ndarray:
    phase = (freq * t) % 1.0
    return (4.0 * np.abs(phase - 0.5) - 1.0).astype(np.float32)


def _one_pole_lowpass(y: np.ndarray, amount: float = 0.10) -> np.ndarray:
    out = np.empty_like(y)
    out[0] = y[0]
    for i in range(1, len(y)):
        out[i] = out[i - 1] + amount * (y[i] - out[i - 1])
    return out


def _soft_lead(freq: float, t: np.ndarray) -> np.ndarray:
    y = (
        0.75 * _pulse_wave(freq, t, duty=0.25)
        + 0.20 * _pulse_wave(freq * 2, t, duty=0.125)
        + 0.08 * np.sin(2 * math.pi * freq * t)
    )
    y = _one_pole_lowpass(y, amount=0.08)
    return y / 1.03


def _soft_pad(freq: float, t: np.ndarray) -> np.ndarray:
    y = (
        0.45 * _pulse_wave(freq * 0.997, t, duty=0.25)
        + 0.45 * _pulse_wave(freq * 1.003, t, duty=0.25)
        + 0.12 * np.sin(2 * math.pi * 2 * freq * t)
    )
    y = _one_pole_lowpass(y, amount=0.05)
    return y / 0.96


def _soft_bass(freq: float, t: np.ndarray) -> np.ndarray:
    y = 0.90 * _triangle_wave(freq, t) + 0.10 * np.sin(2 * math.pi * freq * t)
    y = _one_pole_lowpass(y, amount=0.10)
    return y / 0.95


def _synth_note_np(
    note: str,
    dur_steps: int,
    voice: str = "lead",
    gain: float = 0.15,
    pan: float = 0.0,
    step_sec: float = 60.0 / 96.0 / 4.0,
) -> np.ndarray:
    n = max(1, int(round(dur_steps * step_sec * SAMPLE_RATE)))
    if note == "R":
        return np.zeros((n, 2), dtype=np.float32)
    midi = _note_to_midi(note)
    assert midi is not None
    freq = _midi_to_freq(midi)
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    if voice == "pad":
        y = _soft_pad(freq, t)
        env = _adsr_np(n, attack=0.03, decay=0.03, sustain=0.80, release=0.10)
    elif voice == "bass":
        y = _soft_bass(freq, t)
        env = _adsr_np(n, attack=0.002, decay=0.02, sustain=0.82, release=0.04)
    else:
        y = _soft_lead(freq, t)
        env = _adsr_np(n, attack=0.004, decay=0.035, sustain=0.68, release=0.06)
    y = y * env * gain
    return _stereoize(y, pan=pan)


def _synth_drum_np(
    kind: str,
    dur_steps: int = 1,
    gain: float = 0.08,
    pan: float = 0.0,
    step_sec: float = 60.0 / 96.0 / 4.0,
) -> np.ndarray:
    n = max(1, int(round(dur_steps * step_sec * SAMPLE_RATE)))
    t = np.arange(n, dtype=np.float32) / SAMPLE_RATE
    noise = np.random.default_rng(1337).uniform(-1.0, 1.0, n).astype(np.float32)
    if kind == "kick":
        f0, f1 = 90.0, 40.0
        sweep = f0 * ((f1 / f0) ** (t / max(float(t[-1]), 1e-6)))
        phase = 2 * math.pi * np.cumsum(sweep) / SAMPLE_RATE
        y = np.sin(phase).astype(np.float32)
        env = np.exp(-t / 0.08).astype(np.float32)
        y = y * env
    else:
        env = np.exp(-t / 0.02).astype(np.float32)
        y = noise * env * 0.5
    y *= gain
    return _stereoize(y, pan=pan)


def _place_np(buf: np.ndarray, clip: np.ndarray, start_step: int, step_sec: float) -> None:
    start = int(round(start_step * step_sec * SAMPLE_RATE))
    end = min(len(buf), start + len(clip))
    if end > start:
        buf[start:end] += clip[: end - start]


def render_soft_dungeon_crawl(sample_rate: int = SAMPLE_RATE, volume: float = 0.20) -> np.ndarray:
    bpm = 96
    beat_sec = 60.0 / bpm
    step_sec = beat_sec / 4.0
    bar = 16
    total_bars = 16
    total_steps = bar * total_bars

    phrase_a = [
        (0, "E4", 2, 0.15, "lead", 0.02),
        (2, "G4", 2, 0.16, "lead", 0.03),
        (4, "A4", 2, 0.17, "lead", 0.04),
        (6, "G4", 2, 0.15, "lead", 0.02),
        (8, "E4", 2, 0.14, "lead", 0.00),
        (10, "D4", 2, 0.13, "lead", -0.01),
        (12, "E4", 2, 0.14, "lead", 0.00),
        (14, "B3", 2, 0.12, "lead", -0.02),
        (16, "E4", 2, 0.15, "lead", 0.02),
        (18, "G4", 2, 0.16, "lead", 0.03),
        (20, "A4", 2, 0.17, "lead", 0.04),
        (22, "B4", 2, 0.18, "lead", 0.04),
        (24, "A4", 2, 0.15, "lead", 0.03),
        (26, "G4", 2, 0.14, "lead", 0.01),
        (28, "E4", 2, 0.13, "lead", 0.00),
        (30, "D4", 2, 0.12, "lead", -0.02),
    ]
    phrase_a2 = [
        (0, "E4", 2, 0.15, "lead", 0.02),
        (2, "G4", 2, 0.16, "lead", 0.03),
        (4, "A4", 2, 0.17, "lead", 0.04),
        (6, "G4", 2, 0.15, "lead", 0.02),
        (8, "E4", 2, 0.14, "lead", 0.00),
        (10, "D4", 2, 0.13, "lead", -0.01),
        (12, "B3", 2, 0.12, "lead", -0.02),
        (14, "D4", 2, 0.12, "lead", -0.01),
        (16, "G4", 2, 0.15, "lead", 0.02),
        (18, "A4", 2, 0.16, "lead", 0.03),
        (20, "B4", 2, 0.17, "lead", 0.04),
        (22, "A4", 2, 0.15, "lead", 0.03),
        (24, "G4", 2, 0.14, "lead", 0.01),
        (26, "E4", 2, 0.13, "lead", 0.00),
        (28, "D4", 2, 0.12, "lead", -0.01),
        (30, "E4", 2, 0.12, "lead", 0.00),
    ]
    phrase_b = [
        (0, "C4", 2, 0.13, "lead", -0.02),
        (2, "E4", 2, 0.14, "lead", -0.01),
        (4, "G4", 2, 0.15, "lead", 0.01),
        (6, "E4", 2, 0.14, "lead", -0.01),
        (8, "D4", 2, 0.13, "lead", -0.01),
        (10, "F#4", 2, 0.14, "lead", 0.00),
        (12, "A4", 2, 0.15, "lead", 0.02),
        (14, "F#4", 2, 0.14, "lead", 0.00),
        (16, "B3", 2, 0.12, "lead", -0.03),
        (18, "D4", 2, 0.13, "lead", -0.01),
        (20, "G4", 2, 0.15, "lead", 0.01),
        (22, "A4", 2, 0.16, "lead", 0.03),
        (24, "G4", 2, 0.14, "lead", 0.01),
        (26, "E4", 2, 0.13, "lead", -0.01),
        (28, "D4", 2, 0.12, "lead", -0.02),
        (30, "B3", 2, 0.11, "lead", -0.03),
    ]
    phrase_c = [
        (0, "E4", 2, 0.14, "lead", 0.00),
        (2, "G4", 2, 0.15, "lead", 0.01),
        (4, "B4", 2, 0.17, "lead", 0.03),
        (6, "A4", 2, 0.15, "lead", 0.02),
        (8, "G4", 2, 0.14, "lead", 0.01),
        (10, "E4", 2, 0.13, "lead", 0.00),
        (12, "D4", 2, 0.12, "lead", -0.01),
        (14, "E4", 2, 0.12, "lead", 0.00),
        (16, "A4", 2, 0.15, "lead", 0.02),
        (18, "B4", 2, 0.16, "lead", 0.03),
        (20, "D5", 2, 0.18, "lead", 0.04),
        (22, "B4", 2, 0.16, "lead", 0.03),
        (24, "A4", 2, 0.14, "lead", 0.02),
        (26, "G4", 2, 0.13, "lead", 0.01),
        (28, "E4", 2, 0.12, "lead", 0.00),
        (30, "R", 2, 0.00, "lead", 0.00),
    ]
    phrase_d = [
        (0, "G4", 2, 0.14, "lead", 0.00),
        (2, "A4", 2, 0.15, "lead", 0.01),
        (4, "B4", 2, 0.16, "lead", 0.02),
        (6, "D5", 2, 0.17, "lead", 0.03),
        (8, "B4", 2, 0.15, "lead", 0.02),
        (10, "A4", 2, 0.14, "lead", 0.01),
        (12, "G4", 2, 0.13, "lead", 0.00),
        (14, "E4", 2, 0.12, "lead", -0.01),
        (16, "D4", 2, 0.12, "lead", -0.01),
        (18, "E4", 2, 0.13, "lead", 0.00),
        (20, "G4", 2, 0.14, "lead", 0.01),
        (22, "A4", 2, 0.15, "lead", 0.02),
        (24, "G4", 2, 0.13, "lead", 0.00),
        (26, "E4", 2, 0.12, "lead", -0.01),
        (28, "D4", 2, 0.11, "lead", -0.02),
        (30, "R", 2, 0.00, "lead", 0.00),
    ]

    def add_phrase(
        dest: list[tuple[int, str, int, float, str, float]],
        phrase: list[tuple[int, str, int, float, str, float]],
        bar_offset: int,
    ) -> None:
        step_offset = bar_offset * bar
        for event in phrase:
            start, note, dur, gain, voice, pan = event
            dest.append((step_offset + start, note, dur, gain, voice, pan))

    def add_pad_bar(
        dest: list[tuple[int, str, int, float, str, float]],
        bar_idx: int,
        root: str,
        third: str,
        fifth: str,
    ) -> None:
        s = bar_idx * bar
        dest += [
            (s + 0, root, 8, 0.055, "pad", -0.28),
            (s + 0, fifth, 8, 0.045, "pad", 0.22),
            (s + 8, third, 8, 0.050, "pad", -0.14),
            (s + 8, fifth, 8, 0.040, "pad", 0.16),
        ]

    def add_bass_bar(
        dest: list[tuple[int, str, int, float, str, float]], bar_idx: int, root: str
    ) -> None:
        s = bar_idx * bar
        fifth = _transpose_note(root, 7)
        octave = _transpose_note(root, 12)
        dest += [
            (s + 0, root, 3, 0.11, "bass", -0.03),
            (s + 4, root, 2, 0.10, "bass", -0.03),
            (s + 8, fifth, 2, 0.09, "bass", 0.00),
            (s + 12, octave, 2, 0.08, "bass", 0.02),
        ]

    melody: list[tuple[int, str, int, float, str, float]] = []
    add_phrase(melody, phrase_a, 0)
    add_phrase(melody, phrase_a2, 2)
    add_phrase(melody, phrase_b, 4)
    add_phrase(melody, phrase_c, 6)
    add_phrase(melody, phrase_a, 8)
    add_phrase(melody, phrase_d, 10)
    add_phrase(melody, phrase_c, 12)
    add_phrase(melody, phrase_a2, 14)

    pad: list[tuple[int, str, int, float, str, float]] = []
    bass: list[tuple[int, str, int, float, str, float]] = []

    chord_plan = [
        ("E4", "G4", "B4"),
        ("C4", "E4", "G4"),
        ("A3", "C4", "E4"),
        ("B3", "D4", "F#4"),
        ("C4", "E4", "G4"),
        ("D4", "F#4", "A4"),
        ("E4", "G4", "B4"),
        ("B3", "D4", "F#4"),
        ("G3", "B3", "D4"),
        ("D4", "F#4", "A4"),
        ("E4", "G4", "B4"),
        ("C4", "E4", "G4"),
        ("A3", "C4", "E4"),
        ("G3", "B3", "D4"),
        ("B3", "D4", "F#4"),
        ("B3", "D4", "F#4"),
    ]
    bass_roots = [
        "E2",
        "C2",
        "A2",
        "B2",
        "C2",
        "D2",
        "E2",
        "B2",
        "G2",
        "D2",
        "E2",
        "C2",
        "A2",
        "G2",
        "B2",
        "B2",
    ]

    for i, chord in enumerate(chord_plan):
        add_pad_bar(pad, i, *chord)
        add_bass_bar(bass, i, bass_roots[i])

    drums: list[tuple[int, str, int, float, float]] = []
    for bar_index in range(total_bars):
        s = bar_index * bar
        drums.append((s + 0, "kick", 1, 0.06 if bar_index % 4 else 0.075, 0.00))
        if bar_index % 2 == 1:
            drums.append((s + 8, "kick", 1, 0.045, -0.02))
        drums.append((s + 12, "hat", 1, 0.025, 0.12))

    total_samples = int(round(total_steps * step_sec * sample_rate))
    out = np.zeros((total_samples, 2), dtype=np.float32)

    for start, note, dur, gain, voice, pan in pad + bass + melody:
        clip = _synth_note_np(note, dur, voice=voice, gain=gain, pan=pan, step_sec=step_sec)
        _place_np(out, clip, start, step_sec)

    for start, kind, dur, gain, pan in drums:
        clip = _synth_drum_np(kind, dur_steps=dur, gain=gain, pan=pan, step_sec=step_sec)
        _place_np(out, clip, start, step_sec)

    peak = float(np.max(np.abs(out)))
    if peak > 0:
        out /= peak
    out *= volume
    return np.clip(out * MAX_I16, -32768, 32767).astype(np.int16, copy=False)
