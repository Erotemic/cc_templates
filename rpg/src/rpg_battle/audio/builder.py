from __future__ import annotations

"""Reusable audio composition helpers for generated music tracks.

The goal of this module is to keep new tracks concise and teachable:
- common synthesis primitives live in one place
- tracks describe *events* instead of re-implementing playback math
- generated songs can share phrase helpers and voice definitions
- more advanced tracks can opt into bends, chords, and post-processing
"""

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

import numpy as np
from loguru import logger

SAMPLE_RATE = 44100
MAX_I16 = 32767
BAR_STEPS = 16
STEPS_PER_BEAT = 4

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


@dataclass(frozen=True)
class NoteEvent:
    """One note placed on a track grid.

    ``bend_from`` lets more advanced solo voices start from another note and
    slide into the target pitch.
    """

    start_step: int
    note: str
    duration_steps: int
    gain: float
    voice: str = "lead"
    pan: float = 0.0
    bend_from: str | None = None


@dataclass(frozen=True)
class ChordEvent:
    """A chord placed on a track grid."""

    start_step: int
    notes: tuple[str, ...]
    duration_steps: int
    gain: float
    voice: str = "pad"
    pan: float = 0.0


@dataclass(frozen=True)
class DrumEvent:
    """One drum/percussion event placed on a track grid."""

    start_step: int
    kind: str
    duration_steps: int
    gain: float
    pan: float = 0.0


@dataclass(frozen=True)
class TrackArrangement:
    """The event lists that define a full generated track."""

    note_events: tuple[NoteEvent, ...] = ()
    drum_events: tuple[DrumEvent, ...] = ()
    chord_events: tuple[ChordEvent, ...] = ()


class TrackBuilder:
    """Base class for concise, reusable generated music tracks.

    Subclasses configure tempo and arrangement by emitting event objects. The
    heavy synthesis and mixing logic lives here so new tracks only need to
    describe *what* to play.
    """

    track_id = "base_track"
    cache_version = 1
    bpm = 120
    steps_per_beat = STEPS_PER_BEAT
    bar_steps = BAR_STEPS
    total_bars = 8
    master_gain = 0.25
    wrap_loop_events = False

    def __init__(self, *, sample_rate: int = SAMPLE_RATE, volume: float | None = None) -> None:
        self.sample_rate = sample_rate
        self.master_gain = self.master_gain if volume is None else volume
        self.steps_per_beat = getattr(type(self), "steps_per_beat", STEPS_PER_BEAT)
        self.bar_steps = getattr(type(self), "bar_steps", BAR_STEPS)
        self.total_steps = self.bar_steps * self.total_bars
        self.step_seconds = 60.0 / self.bpm / self.steps_per_beat

    def build(self) -> TrackArrangement:
        """Return the note/drum/chord events that define this track."""
        raise NotImplementedError

    def render(self) -> np.ndarray:
        """Render the full arrangement to stereo int16 PCM."""

        arrangement = self.build()
        total_samples = int(round(self.total_steps * self.step_seconds * self.sample_rate))
        logger.debug(
            "Rendering generated track '{}' (bars={}, bpm={}, notes={}, chords={}, drums={})",
            self.track_id,
            self.total_bars,
            self.bpm,
            len(arrangement.note_events),
            len(arrangement.chord_events),
            len(arrangement.drum_events),
        )
        mix = np.zeros((total_samples, 2), dtype=np.float32)
        for event in arrangement.chord_events:
            clip = self.synth_chord(
                list(event.notes),
                event.duration_steps,
                voice=event.voice,
                gain=event.gain,
                pan=event.pan,
            )
            self.place_event(mix, clip, event.start_step)
        for event in arrangement.note_events:
            clip = self.synth_note(
                event.note,
                event.duration_steps,
                voice=event.voice,
                gain=event.gain,
                pan=event.pan,
                bend_from=event.bend_from,
            )
            self.place_event(mix, clip, event.start_step)
        for event in arrangement.drum_events:
            clip = self.synth_drum(
                event.kind,
                dur_steps=event.duration_steps,
                gain=event.gain,
                pan=event.pan,
            )
            self.place_event(mix, clip, event.start_step)
        mix = self.process_mix(mix)
        peak = float(np.max(np.abs(mix)))
        if peak > 0:
            mix /= peak
        mix *= self.master_gain
        return np.clip(mix * MAX_I16, -32768, 32767).astype(np.int16, copy=False)

    def process_mix(self, mix: np.ndarray) -> np.ndarray:
        """Hook for optional post-processing like loop-safe delay."""
        return mix

    def add_phrase(
        self, dest: list[NoteEvent], phrase: Iterable[NoteEvent], *, bar_offset: int
    ) -> None:
        """Append a phrase shifted by a whole-number bar offset."""

        offset = bar_offset * self.bar_steps
        for event in phrase:
            dest.append(
                NoteEvent(
                    start_step=offset + event.start_step,
                    note=event.note,
                    duration_steps=event.duration_steps,
                    gain=event.gain,
                    voice=event.voice,
                    pan=event.pan,
                    bend_from=event.bend_from,
                )
            )

    def note(self, *args: object, **kwargs: object) -> NoteEvent:
        return NoteEvent(*args, **kwargs)

    def chord(
        self,
        start_step: int,
        notes: Sequence[str],
        duration_steps: int,
        gain: float,
        voice: str = "pad",
        pan: float = 0.0,
    ) -> ChordEvent:
        return ChordEvent(start_step, tuple(notes), duration_steps, gain, voice, pan)

    def drum(self, *args: object, **kwargs: object) -> DrumEvent:
        return DrumEvent(*args, **kwargs)

    def place(self, buf: np.ndarray, clip: np.ndarray, start_step: int) -> None:
        start = int(round(start_step * self.step_seconds * self.sample_rate))
        end = min(len(buf), start + len(clip))
        if end > start:
            buf[start:end] += clip[: end - start]

    def place_loop(self, buf: np.ndarray, clip: np.ndarray, start_step: int) -> None:
        """Place a clip into a looping buffer with wraparound at the seam."""

        total = len(buf)
        start = int(round(start_step * self.step_seconds * self.sample_rate)) % total
        end = start + len(clip)
        if end <= total:
            buf[start:end] += clip
        else:
            split = total - start
            buf[start:] += clip[:split]
            buf[: end - total] += clip[split:]

    def place_event(self, buf: np.ndarray, clip: np.ndarray, start_step: int) -> None:
        """Place an event clip using either truncating or loop-wrapping semantics."""

        if self.wrap_loop_events:
            self.place_loop(buf, clip, start_step)
        else:
            self.place(buf, clip, start_step)

    def synth_note(
        self,
        note: str,
        dur_steps: int,
        *,
        voice: str = "lead",
        gain: float = 0.15,
        pan: float = 0.0,
        bend_from: str | None = None,
    ) -> np.ndarray:
        """Synthesize one pitched note clip.

        The base implementation ignores ``bend_from``. More advanced tracks can
        override this and use the extra metadata for solo slides.
        """
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        if note == "R":
            return np.zeros((sample_count, 2), dtype=np.float32)
        frequency = midi_to_freq(note_to_midi(note))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        if voice == "pad":
            signal = pad_voice(frequency, times)
            env = adsr(
                sample_count, self.sample_rate, attack=0.03, decay=0.03, sustain=0.80, release=0.10
            )
        elif voice == "bass":
            signal = bass_voice(frequency, times)
            env = adsr(
                sample_count, self.sample_rate, attack=0.002, decay=0.02, sustain=0.82, release=0.04
            )
        else:
            signal = lead_voice(frequency, times)
            env = adsr(
                sample_count,
                self.sample_rate,
                attack=0.004,
                decay=0.035,
                sustain=0.68,
                release=0.06,
            )
        signal = signal * env * gain
        return stereoize(signal, pan=pan)

    def synth_chord(
        self,
        notes: Sequence[str],
        dur_steps: int,
        *,
        voice: str = "pad",
        gain: float = 0.10,
        pan: float = 0.0,
    ) -> np.ndarray:
        """Synthesize a simple chord clip.

        This gives tracks a concise way to add sustained harmony without having
        to schedule every note manually.
        """
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        signal = np.zeros(sample_count, dtype=np.float32)
        for idx, note in enumerate(notes):
            frequency = midi_to_freq(note_to_midi(note))
            detune = 1.0 + (idx - (len(notes) - 1) / 2.0) * 0.002
            if voice == "pad":
                part = pad_voice(frequency * detune, times)
            else:
                part = lead_voice(frequency * detune, times)
            signal += part / max(1, len(notes))
        env = adsr(
            sample_count, self.sample_rate, attack=0.05, decay=0.15, sustain=0.76, release=0.18
        )
        signal = one_pole_lowpass(signal, amount=0.03) * env * gain
        return stereoize(signal, pan=pan)

    def synth_drum(
        self, kind: str, *, dur_steps: int = 1, gain: float = 0.08, pan: float = 0.0
    ) -> np.ndarray:
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        noise = np.random.default_rng(1337).uniform(-1.0, 1.0, sample_count).astype(np.float32)
        if kind == "kick":
            f0, f1 = 90.0, 40.0
            sweep = f0 * ((f1 / f0) ** (times / max(float(times[-1]), 1e-6)))
            phase = 2 * math.pi * np.cumsum(sweep) / self.sample_rate
            signal = np.sin(phase).astype(np.float32)
            env = np.exp(-times / 0.08).astype(np.float32)
            signal = signal * env
        elif kind == "snare":
            tone = np.sin(2 * math.pi * 180.0 * times).astype(np.float32)
            tone *= np.exp(-times / 0.055).astype(np.float32)
            body = noise * np.exp(-times / 0.045).astype(np.float32) * 0.65
            signal = tone * 0.35 + body
        else:
            high_noise = noise - one_pole_lowpass(noise, amount=0.18)
            env = np.exp(-times / 0.012).astype(np.float32)
            signal = high_noise * env * 0.45
        signal *= gain
        return stereoize(signal, pan=pan)


def note_to_midi(note: str) -> int:
    if note == "R":
        raise ValueError("Rest notes do not have MIDI values")
    name = note[0]
    octave_str = note[1:]
    if len(note) >= 3 and note[1] in {"#", "b"}:
        name = note[:2]
        octave_str = note[2:]
    octave = int(octave_str)
    return 12 * (octave + 1) + NOTE_INDEX[name]


def midi_to_note(midi: int) -> str:
    return NAMES[midi % 12] + str(midi // 12 - 1)


def transpose_note(note: str, semitones: int) -> str:
    if note == "R":
        return "R"
    return midi_to_note(note_to_midi(note) + semitones)


def midi_to_freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def scale_path(start_midi: int, target_midi: int, scale_pitch_classes: set[int]) -> list[int]:
    """Walk from start to target, keeping intermediate notes inside a scale.

    This is useful for simple slide/bend effects where a solo line should move
    through scale tones rather than a raw chromatic sweep.
    """
    if start_midi == target_midi:
        return [start_midi]
    step = 1 if target_midi > start_midi else -1
    out = [start_midi]
    midi = start_midi + step
    while (midi <= target_midi) if step > 0 else (midi >= target_midi):
        if (midi % 12) in scale_pitch_classes:
            out.append(midi)
        midi += step
    if out[-1] != target_midi:
        out.append(target_midi)
    return out


def stereoize(signal: np.ndarray, *, pan: float = 0.0) -> np.ndarray:
    left = math.sqrt((1.0 - pan) / 2.0)
    right = math.sqrt((1.0 + pan) / 2.0)
    return np.column_stack([signal * left, signal * right]).astype(np.float32)


def adsr(
    sample_count: int,
    sample_rate: int,
    *,
    attack: float = 0.004,
    decay: float = 0.04,
    sustain: float = 0.72,
    release: float = 0.06,
) -> np.ndarray:
    attack_count = max(1, int(attack * sample_rate))
    decay_count = max(1, int(decay * sample_rate))
    release_count = max(1, int(release * sample_rate))
    sustain_count = max(0, sample_count - attack_count - decay_count - release_count)
    env = np.concatenate(
        [
            np.linspace(0.0, 1.0, attack_count, endpoint=False),
            np.linspace(1.0, sustain, decay_count, endpoint=False),
            np.full(sustain_count, sustain, dtype=np.float32),
            np.linspace(sustain, 0.0, release_count, endpoint=True),
        ]
    ).astype(np.float32)
    if len(env) < sample_count:
        env = np.pad(env, (0, sample_count - len(env)))
    return env[:sample_count]


def sine_wave(freq: float, times: np.ndarray) -> np.ndarray:
    return np.sin(2 * math.pi * freq * times).astype(np.float32)


def saw_wave(freq: float, times: np.ndarray) -> np.ndarray:
    phase = (freq * times) % 1.0
    return (2.0 * phase - 1.0).astype(np.float32)


def pulse_wave(freq: float, times: np.ndarray, *, duty: float = 0.25) -> np.ndarray:
    phase = (freq * times) % 1.0
    return np.where(phase < duty, 1.0, -1.0).astype(np.float32)


def triangle_wave(freq: float, times: np.ndarray) -> np.ndarray:
    phase = (freq * times) % 1.0
    return (4.0 * np.abs(phase - 0.5) - 1.0).astype(np.float32)


def one_pole_lowpass(signal: np.ndarray, *, amount: float = 0.10) -> np.ndarray:
    out = np.empty_like(signal)
    out[0] = signal[0]
    for index in range(1, len(signal)):
        out[index] = out[index - 1] + amount * (signal[index] - out[index - 1])
    return out


def soft_clip(signal: np.ndarray, *, drive: float = 1.4) -> np.ndarray:
    return np.tanh(drive * signal).astype(np.float32)


def lead_voice(freq: float, times: np.ndarray) -> np.ndarray:
    signal = (
        0.75 * pulse_wave(freq, times, duty=0.25)
        + 0.20 * pulse_wave(freq * 2, times, duty=0.125)
        + 0.08 * np.sin(2 * math.pi * freq * times)
    )
    signal = one_pole_lowpass(signal, amount=0.08)
    return signal / 1.03


def pad_voice(freq: float, times: np.ndarray) -> np.ndarray:
    signal = (
        0.45 * pulse_wave(freq * 0.997, times, duty=0.25)
        + 0.45 * pulse_wave(freq * 1.003, times, duty=0.25)
        + 0.12 * np.sin(2 * math.pi * 2 * freq * times)
    )
    signal = one_pole_lowpass(signal, amount=0.05)
    return signal / 0.96


def bass_voice(freq: float, times: np.ndarray) -> np.ndarray:
    signal = 0.90 * triangle_wave(freq, times) + 0.10 * np.sin(2 * math.pi * freq * times)
    signal = one_pole_lowpass(signal, amount=0.10)
    return signal / 0.95
