from __future__ import annotations

"""Generated music track definitions.

Each track subclasses :class:`TrackBuilder` so new songs can focus on the
musical arrangement rather than the low-level synthesis details.
"""

import math

import numpy as np

from rpg_battle.audio.builder import (
    DrumEvent,
    NoteEvent,
    TrackArrangement,
    TrackBuilder,
    adsr,
    midi_to_freq,
    note_to_midi,
    one_pole_lowpass,
    pulse_wave,
    stereoize,
    transpose_note,
    triangle_wave,
)


class TrainingBattleTrack(TrackBuilder):
    """Original prototype battle loop kept as a simpler alternate track."""

    track_id = "battle_loop_prototype"
    bpm = 132 * 1.5  # dotted-quarter feel from the prototype, approximated to 16ths.
    total_bars = 16
    master_gain = 0.42

    def build(self) -> TrackArrangement:
        melody: list[NoteEvent] = []
        rhythm: list[DrumEvent] = []
        motif_a = [
            self.note(0, "B4", 2, 0.26),
            self.note(2, "B4", 1, 0.22),
            self.note(3, "G4", 1, 0.18),
            self.note(4, "B4", 2, 0.24),
            self.note(6, "D5", 3, 0.28),
            self.note(9, "B4", 3, 0.20),
            self.note(12, "D5", 1, 0.22),
            self.note(13, "B4", 1, 0.16),
            self.note(14, "D5", 2, 0.22),
            self.note(16, "F#5", 6, 0.30),
            self.note(22, "D5", 5, 0.24),
        ]
        motif_b = [
            self.note(0, "D5", 2, 0.22),
            self.note(2, "D5", 1, 0.18),
            self.note(3, "B4", 1, 0.16),
            self.note(4, "D5", 2, 0.22),
            self.note(6, "F#5", 3, 0.26),
            self.note(9, "D5", 3, 0.20),
            self.note(12, "F#5", 1, 0.22),
            self.note(13, "D5", 1, 0.16),
            self.note(14, "F#5", 2, 0.22),
            self.note(16, "A5", 4, 0.28),
            self.note(20, "F#5", 2, 0.22),
            self.note(22, "D5", 2, 0.18),
        ]
        motif_c = [
            self.note(0, "E5", 2, 0.22),
            self.note(2, "E5", 1, 0.18),
            self.note(3, "C#5", 1, 0.16),
            self.note(4, "E5", 2, 0.22),
            self.note(6, "G5", 3, 0.24),
            self.note(9, "E5", 3, 0.20),
            self.note(12, "G5", 1, 0.22),
            self.note(13, "E5", 1, 0.16),
            self.note(14, "F#5", 2, 0.22),
            self.note(16, "A5", 2, 0.24),
            self.note(18, "B5", 2, 0.26),
            self.note(20, "A5", 2, 0.22),
            self.note(22, "F#5", 2, 0.18),
        ]
        turnaround = [
            self.note(0, "F#5", 2, 0.20),
            self.note(2, "E5", 2, 0.18),
            self.note(4, "D5", 2, 0.16),
            self.note(6, "B4", 3, 0.14),
            self.note(10, "D5", 2, 0.16),
            self.note(12, "F#5", 2, 0.18),
            self.note(14, "A5", 2, 0.16),
        ]
        phrases = [motif_a, motif_a, motif_b, motif_c, motif_a, motif_a, motif_b, turnaround]
        roots = ["B2", "B2", "G2", "D2", "E2", "F#2", "B2", "F#2"]
        for phrase_index, phrase in enumerate(phrases):
            self.add_phrase(melody, phrase, bar_offset=phrase_index * 2)
            root = roots[phrase_index]
            fifth = transpose_note(root, 7)
            octave = transpose_note(root, 12)
            for local in (0, self.bar_steps):
                start = phrase_index * 2 * self.bar_steps + local
                melody.extend(
                    [
                        self.note(start + 0, root, 6, 0.14, "bass"),
                        self.note(start + 0, fifth, 6, 0.06, "bass"),
                        self.note(start + 6, octave, 6, 0.08, "bass"),
                        self.note(start + 12, fifth, 4, 0.05, "bass"),
                    ]
                )
        for bar_index in range(self.total_bars):
            start = bar_index * self.bar_steps
            rhythm.extend(
                [
                    self.drum(start + 0, "kick", 1, 0.06),
                    self.drum(start + 4, "hat", 1, 0.03, 0.10),
                    self.drum(start + 8, "kick", 1, 0.05),
                    self.drum(start + 12, "hat", 1, 0.03, -0.10),
                ]
            )
        return TrackArrangement(tuple(melody), tuple(rhythm))


class SoftDungeonCrawlTrack(TrackBuilder):
    """Softer loop used as the classroom default battle theme."""

    track_id = "soft_dungeon_crawl"
    bpm = 96
    total_bars = 16
    master_gain = 0.20

    def build(self) -> TrackArrangement:
        melody: list[NoteEvent] = []
        pad: list[NoteEvent] = []
        bass: list[NoteEvent] = []
        drums: list[DrumEvent] = []

        phrase_a = [
            self.note(0, "E4", 2, 0.15, pan=0.02),
            self.note(2, "G4", 2, 0.16, pan=0.03),
            self.note(4, "A4", 2, 0.17, pan=0.04),
            self.note(6, "G4", 2, 0.15, pan=0.02),
            self.note(8, "E4", 2, 0.14, pan=0.00),
            self.note(10, "D4", 2, 0.13, pan=-0.01),
            self.note(12, "E4", 2, 0.14, pan=0.00),
            self.note(14, "B3", 2, 0.12, pan=-0.02),
            self.note(16, "E4", 2, 0.15, pan=0.02),
            self.note(18, "G4", 2, 0.16, pan=0.03),
            self.note(20, "A4", 2, 0.17, pan=0.04),
            self.note(22, "B4", 2, 0.18, pan=0.04),
            self.note(24, "A4", 2, 0.15, pan=0.03),
            self.note(26, "G4", 2, 0.14, pan=0.01),
            self.note(28, "E4", 2, 0.13, pan=0.00),
            self.note(30, "D4", 2, 0.12, pan=-0.02),
        ]
        phrase_a2 = [
            self.note(0, "E4", 2, 0.15, pan=0.02),
            self.note(2, "G4", 2, 0.16, pan=0.03),
            self.note(4, "A4", 2, 0.17, pan=0.04),
            self.note(6, "G4", 2, 0.15, pan=0.02),
            self.note(8, "E4", 2, 0.14, pan=0.00),
            self.note(10, "D4", 2, 0.13, pan=-0.01),
            self.note(12, "B3", 2, 0.12, pan=-0.02),
            self.note(14, "D4", 2, 0.12, pan=-0.01),
            self.note(16, "G4", 2, 0.15, pan=0.02),
            self.note(18, "A4", 2, 0.16, pan=0.03),
            self.note(20, "B4", 2, 0.17, pan=0.04),
            self.note(22, "A4", 2, 0.15, pan=0.03),
            self.note(24, "G4", 2, 0.14, pan=0.01),
            self.note(26, "E4", 2, 0.13, pan=0.00),
            self.note(28, "D4", 2, 0.12, pan=-0.01),
            self.note(30, "E4", 2, 0.12, pan=0.00),
        ]
        phrase_b = [
            self.note(0, "C4", 2, 0.13, pan=-0.02),
            self.note(2, "E4", 2, 0.14, pan=-0.01),
            self.note(4, "G4", 2, 0.15, pan=0.01),
            self.note(6, "E4", 2, 0.14, pan=-0.01),
            self.note(8, "D4", 2, 0.13, pan=-0.01),
            self.note(10, "F#4", 2, 0.14, pan=0.00),
            self.note(12, "A4", 2, 0.15, pan=0.02),
            self.note(14, "F#4", 2, 0.14, pan=0.00),
            self.note(16, "B3", 2, 0.12, pan=-0.03),
            self.note(18, "D4", 2, 0.13, pan=-0.01),
            self.note(20, "G4", 2, 0.15, pan=0.01),
            self.note(22, "A4", 2, 0.16, pan=0.03),
            self.note(24, "G4", 2, 0.14, pan=0.01),
            self.note(26, "E4", 2, 0.13, pan=-0.01),
            self.note(28, "D4", 2, 0.12, pan=-0.02),
            self.note(30, "B3", 2, 0.11, pan=-0.03),
        ]
        phrase_c = [
            self.note(0, "E4", 2, 0.14, pan=0.00),
            self.note(2, "G4", 2, 0.15, pan=0.01),
            self.note(4, "B4", 2, 0.17, pan=0.03),
            self.note(6, "A4", 2, 0.15, pan=0.02),
            self.note(8, "G4", 2, 0.14, pan=0.01),
            self.note(10, "E4", 2, 0.13, pan=0.00),
            self.note(12, "D4", 2, 0.12, pan=-0.01),
            self.note(14, "E4", 2, 0.12, pan=0.00),
            self.note(16, "A4", 2, 0.15, pan=0.02),
            self.note(18, "B4", 2, 0.16, pan=0.03),
            self.note(20, "D5", 2, 0.18, pan=0.04),
            self.note(22, "B4", 2, 0.16, pan=0.03),
            self.note(24, "A4", 2, 0.14, pan=0.02),
            self.note(26, "G4", 2, 0.13, pan=0.01),
            self.note(28, "E4", 2, 0.12, pan=0.00),
            self.note(30, "R", 2, 0.00),
        ]
        phrase_d = [
            self.note(0, "G4", 2, 0.14, pan=0.00),
            self.note(2, "A4", 2, 0.15, pan=0.01),
            self.note(4, "B4", 2, 0.16, pan=0.02),
            self.note(6, "D5", 2, 0.17, pan=0.03),
            self.note(8, "B4", 2, 0.15, pan=0.02),
            self.note(10, "A4", 2, 0.14, pan=0.01),
            self.note(12, "G4", 2, 0.13, pan=0.00),
            self.note(14, "E4", 2, 0.12, pan=-0.01),
            self.note(16, "D4", 2, 0.12, pan=-0.01),
            self.note(18, "E4", 2, 0.13, pan=0.00),
            self.note(20, "G4", 2, 0.14, pan=0.01),
            self.note(22, "A4", 2, 0.15, pan=0.02),
            self.note(24, "G4", 2, 0.13, pan=0.00),
            self.note(26, "E4", 2, 0.12, pan=-0.01),
            self.note(28, "D4", 2, 0.11, pan=-0.02),
            self.note(30, "R", 2, 0.00),
        ]
        for bars, phrase in [
            (0, phrase_a),
            (2, phrase_a2),
            (4, phrase_b),
            (6, phrase_c),
            (8, phrase_a),
            (10, phrase_d),
            (12, phrase_c),
            (14, phrase_a2),
        ]:
            self.add_phrase(melody, phrase, bar_offset=bars)

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
        for bar_index, (root, third, fifth) in enumerate(chord_plan):
            s = bar_index * self.bar_steps
            pad.extend(
                [
                    self.note(s + 0, root, 8, 0.055, "pad", -0.28),
                    self.note(s + 0, fifth, 8, 0.045, "pad", 0.22),
                    self.note(s + 8, third, 8, 0.050, "pad", -0.14),
                    self.note(s + 8, fifth, 8, 0.040, "pad", 0.16),
                ]
            )
            bass_root = bass_roots[bar_index]
            bass.extend(
                [
                    self.note(s + 0, bass_root, 3, 0.11, "bass", -0.03),
                    self.note(s + 4, bass_root, 2, 0.10, "bass", -0.03),
                    self.note(s + 8, transpose_note(bass_root, 7), 2, 0.09, "bass", 0.00),
                    self.note(s + 12, transpose_note(bass_root, 12), 2, 0.08, "bass", 0.02),
                ]
            )
        for bar_index in range(self.total_bars):
            s = bar_index * self.bar_steps
            drums.append(self.drum(s + 0, "kick", 1, 0.075 if bar_index % 4 == 0 else 0.06))
            if bar_index % 2 == 1:
                drums.append(self.drum(s + 8, "kick", 1, 0.045, -0.02))
            drums.append(self.drum(s + 12, "hat", 1, 0.025, 0.12))
        return TrackArrangement(tuple(pad + bass + melody), tuple(drums))


class BossBattleFrenzyTrack(TrackBuilder):
    """Fast boss-battle loop based on the user-provided prototype."""

    track_id = "boss_battle_frenzy"
    bpm = 144
    total_bars = 8
    master_gain = 0.34

    def build(self) -> TrackArrangement:
        melody: list[NoteEvent] = []
        harmony: list[NoteEvent] = []
        pad: list[NoteEvent] = []
        bass: list[NoteEvent] = []
        drums: list[DrumEvent] = []

        phrase_a = [
            self.note(0, "E5", 2, 0.18, pan=0.10),
            self.note(2, "G5", 2, 0.19, pan=0.12),
            self.note(4, "B5", 2, 0.22, pan=0.14),
            self.note(6, "A5", 2, 0.19, pan=0.10),
            self.note(8, "G5", 2, 0.18, pan=0.06),
            self.note(10, "F#5", 2, 0.17, pan=0.02),
            self.note(12, "E5", 2, 0.18, pan=-0.02),
            self.note(14, "D#5", 2, 0.16, pan=-0.06),
            self.note(16, "E5", 1, 0.18, pan=0.04),
            self.note(17, "G5", 1, 0.18, pan=0.06),
            self.note(18, "A5", 2, 0.19, pan=0.08),
            self.note(20, "B5", 2, 0.22, pan=0.12),
            self.note(22, "A5", 2, 0.19, pan=0.08),
            self.note(24, "G5", 2, 0.18, pan=0.04),
            self.note(26, "F#5", 2, 0.17, pan=0.00),
            self.note(28, "E5", 4, 0.20, pan=-0.04),
        ]
        phrase_b = [
            self.note(0, "B4", 2, 0.17, pan=-0.02),
            self.note(2, "D#5", 2, 0.18, pan=0.00),
            self.note(4, "F#5", 2, 0.19, pan=0.04),
            self.note(6, "G5", 2, 0.20, pan=0.08),
            self.note(8, "A5", 2, 0.21, pan=0.10),
            self.note(10, "B5", 2, 0.23, pan=0.14),
            self.note(12, "D6", 2, 0.24, pan=0.18),
            self.note(14, "B5", 2, 0.21, pan=0.12),
            self.note(16, "A5", 2, 0.20, pan=0.08),
            self.note(18, "G5", 2, 0.19, pan=0.04),
            self.note(20, "F#5", 2, 0.18, pan=0.00),
            self.note(22, "E5", 2, 0.18, pan=-0.02),
            self.note(24, "D#5", 2, 0.17, pan=-0.04),
            self.note(26, "F#5", 2, 0.18, pan=0.00),
            self.note(28, "B5", 4, 0.22, pan=0.10),
        ]
        phrase_c = [
            self.note(0, "E5", 2, 0.18, pan=0.02),
            self.note(2, "G5", 2, 0.19, pan=0.04),
            self.note(4, "B5", 2, 0.22, pan=0.08),
            self.note(6, "D6", 2, 0.24, pan=0.14),
            self.note(8, "C6", 2, 0.22, pan=0.10),
            self.note(10, "B5", 2, 0.20, pan=0.08),
            self.note(12, "A5", 2, 0.19, pan=0.04),
            self.note(14, "G5", 2, 0.18, pan=0.00),
            self.note(16, "F#5", 2, 0.18, pan=-0.02),
            self.note(18, "G5", 2, 0.19, pan=0.00),
            self.note(20, "A5", 2, 0.20, pan=0.04),
            self.note(22, "B5", 2, 0.22, pan=0.08),
            self.note(24, "A5", 2, 0.19, pan=0.04),
            self.note(26, "G5", 2, 0.18, pan=0.00),
            self.note(28, "F#5", 2, 0.17, pan=-0.02),
            self.note(30, "E5", 2, 0.19, pan=-0.06),
        ]
        phrase_d = [
            self.note(0, "B4", 1, 0.16, pan=0.02),
            self.note(1, "D#5", 1, 0.17, pan=0.04),
            self.note(2, "F#5", 2, 0.19, pan=0.08),
            self.note(4, "A5", 2, 0.20, pan=0.10),
            self.note(6, "B5", 2, 0.22, pan=0.12),
            self.note(8, "A5", 2, 0.20, pan=0.10),
            self.note(10, "G5", 2, 0.19, pan=0.06),
            self.note(12, "F#5", 2, 0.18, pan=0.02),
            self.note(14, "E5", 2, 0.17, pan=-0.02),
            self.note(16, "D#5", 2, 0.17, pan=-0.04),
            self.note(18, "E5", 2, 0.18, pan=-0.02),
            self.note(20, "F#5", 2, 0.19, pan=0.02),
            self.note(22, "G5", 2, 0.20, pan=0.06),
            self.note(24, "A5", 2, 0.21, pan=0.10),
            self.note(26, "B5", 2, 0.22, pan=0.14),
            self.note(28, "E6", 4, 0.24, pan=0.18),
        ]
        for bars, phrase in [
            (0, phrase_a),
            (2, phrase_b),
            (4, phrase_a),
            (6, phrase_c),
            (6, phrase_d),
        ]:
            self.add_phrase(melody, phrase, bar_offset=bars)
        for event in melody:
            if event.note == "R" or event.start_step % 4 != 2:
                continue
            harmony.append(
                self.note(
                    event.start_step,
                    transpose_note(event.note, -12),
                    event.duration_steps,
                    event.gain * 0.55,
                    "lead",
                    -event.pan * 0.6,
                )
            )
        chord_plan = [
            ("E4", "G4", "B4"),
            ("C4", "E4", "G4"),
            ("A3", "C4", "E4"),
            ("B3", "D#4", "F#4"),
            ("E4", "G4", "B4"),
            ("C4", "E4", "G4"),
            ("D4", "F#4", "A4"),
            ("B3", "D#4", "F#4"),
        ]
        bass_roots = ["E2", "C2", "A2", "B2", "E2", "C2", "D2", "B2"]
        for bar_index, chord in enumerate(chord_plan):
            s = bar_index * self.bar_steps
            root, third, fifth = chord
            pad.extend(
                [
                    self.note(s + 0, root, 4, 0.050, "pad", -0.24),
                    self.note(s + 0, fifth, 4, 0.040, "pad", 0.20),
                    self.note(s + 4, root, 4, 0.045, "pad", -0.18),
                    self.note(s + 4, third, 4, 0.040, "pad", 0.10),
                    self.note(s + 8, third, 4, 0.048, "pad", -0.12),
                    self.note(s + 8, fifth, 4, 0.042, "pad", 0.16),
                    self.note(s + 12, root, 4, 0.044, "pad", -0.08),
                    self.note(s + 12, fifth, 4, 0.038, "pad", 0.18),
                ]
            )
            bass_root = bass_roots[bar_index]
            bass.extend(
                [
                    self.note(s + 0, bass_root, 2, 0.12, "bass", -0.04),
                    self.note(s + 2, transpose_note(bass_root, 7), 2, 0.10, "bass", -0.02),
                    self.note(s + 4, bass_root, 2, 0.12, "bass", -0.03),
                    self.note(s + 6, transpose_note(bass_root, 12), 2, 0.11, "bass", 0.00),
                    self.note(s + 8, bass_root, 2, 0.12, "bass", 0.00),
                    self.note(s + 10, transpose_note(bass_root, 7), 2, 0.10, "bass", 0.02),
                    self.note(s + 12, transpose_note(bass_root, 12), 2, 0.11, "bass", 0.03),
                    self.note(s + 14, transpose_note(bass_root, 7), 2, 0.10, "bass", 0.02),
                ]
            )
        for bar_index in range(self.total_bars):
            s = bar_index * self.bar_steps
            drums.extend(
                [
                    self.drum(s + 0, "kick", 1, 0.085),
                    self.drum(s + 4, "snare", 1, 0.050, -0.04),
                    self.drum(s + 8, "kick", 1, 0.075),
                    self.drum(s + 12, "snare", 1, 0.055, 0.05),
                ]
            )
            if bar_index % 2 == 1:
                drums.append(self.drum(s + 10, "kick", 1, 0.060, -0.02))
            for step in range(0, self.bar_steps, 2):
                drums.append(self.drum(s + step, "hat", 1, 0.020 if step % 4 else 0.026, 0.16))
            for step in (3, 7, 11, 15):
                drums.append(self.drum(s + step, "hat", 1, 0.014, -0.14))
        return TrackArrangement(tuple(pad + bass + harmony + melody), tuple(drums))


class BluesyOverhaulTrack(TrackBuilder):
    """Shuffle / 12-8 inspired battle loop based on the user prototype."""

    track_id = "bluesy_overhaul"
    bpm = 116
    bar_steps = 12
    total_bars = 12
    master_gain = 0.22

    def _lead_voice(self, freq: float, times: np.ndarray) -> np.ndarray:
        wobble = 0.10 * np.sin(2 * math.pi * 5.2 * times)
        signal = (
            0.40 * pulse_wave(freq, times, duty=0.45)
            + 0.30 * np.sin(2 * math.pi * freq * times + wobble)
            + 0.18 * np.sin(2 * math.pi * 2 * freq * times)
            + 0.10 * pulse_wave(freq * 0.5, times, duty=0.5)
        )
        signal = np.tanh(1.4 * signal)
        signal = one_pole_lowpass(signal, amount=0.08)
        return signal / 0.92

    def _organ_voice(self, freq: float, times: np.ndarray) -> np.ndarray:
        signal = (
            0.30 * np.sin(2 * math.pi * freq * times)
            + 0.24 * np.sin(2 * math.pi * 2 * freq * times)
            + 0.14 * np.sin(2 * math.pi * 3 * freq * times)
            + 0.10 * pulse_wave(freq, times, duty=0.5)
        )
        signal = one_pole_lowpass(signal, amount=0.05)
        return signal / 0.78

    def _bass_voice(self, freq: float, times: np.ndarray) -> np.ndarray:
        signal = (
            0.65 * triangle_wave(freq, times)
            + 0.22 * np.sin(2 * math.pi * freq * times)
            + 0.12 * pulse_wave(freq * 0.5, times, duty=0.5)
        )
        signal = one_pole_lowpass(signal, amount=0.10)
        return signal / 0.84

    def synth_note(
        self,
        note: str,
        dur_steps: int,
        *,
        voice: str = "lead",
        gain: float = 0.14,
        pan: float = 0.0,
    ) -> np.ndarray:
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        if note == "R":
            return np.zeros((sample_count, 2), dtype=np.float32)
        frequency = midi_to_freq(note_to_midi(note))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        if voice == "bass":
            signal = self._bass_voice(frequency, times)
            env = adsr(
                sample_count, self.sample_rate, attack=0.001, decay=0.02, sustain=0.78, release=0.04
            )
        elif voice == "organ":
            signal = self._organ_voice(frequency, times)
            env = adsr(
                sample_count, self.sample_rate, attack=0.010, decay=0.03, sustain=0.80, release=0.08
            )
        else:
            signal = self._lead_voice(frequency, times)
            env = adsr(
                sample_count,
                self.sample_rate,
                attack=0.002,
                decay=0.026,
                sustain=0.66,
                release=0.05,
            )
        signal = signal * env * gain
        return stereoize(signal, pan=pan)

    def synth_drum(
        self, kind: str, *, dur_steps: int = 1, gain: float = 0.05, pan: float = 0.0
    ) -> np.ndarray:
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        noise = np.random.default_rng(1337).uniform(-1.0, 1.0, sample_count).astype(np.float32)
        if kind == "kick":
            f0, f1 = 100.0, 40.0
            sweep = f0 * ((f1 / f0) ** (times / max(float(times[-1]), 1e-6)))
            phase = 2 * math.pi * np.cumsum(sweep) / self.sample_rate
            signal = np.sin(phase)
            env = np.exp(-times / 0.07)
            signal = signal * env
        elif kind == "snare":
            tone = np.sin(2 * math.pi * 190.0 * times)
            env = np.exp(-times / 0.04)
            signal = (0.20 * tone + 0.80 * noise) * env
        else:
            env = np.exp(-times / 0.012)
            signal = noise * env * 0.45
        signal = signal.astype(np.float32) * gain
        return stereoize(signal, pan=pan)

    def _add_comp_bar(
        self,
        dest: list[NoteEvent],
        bar_idx: int,
        notes: tuple[str, str, str, str],
        *,
        gain: float = 0.020,
    ) -> None:
        start = bar_idx * self.bar_steps
        for offset in (1, 4, 7, 10):
            dest.extend(
                [
                    self.note(start + offset, notes[0], 2, gain, "organ", -0.10),
                    self.note(start + offset, notes[1], 2, gain * 0.92, "organ", 0.02),
                    self.note(start + offset, notes[2], 2, gain * 0.88, "organ", 0.12),
                    self.note(start + offset, notes[3], 2, gain * 0.82, "organ", 0.18),
                ]
            )

    def _add_shuffle_bass(self, dest: list[NoteEvent], bar_idx: int, root: str) -> None:
        start = bar_idx * self.bar_steps
        fifth = transpose_note(root, 7)
        sixth = transpose_note(root, 9)
        flat7 = transpose_note(root, 10)
        octave = transpose_note(root, 12)
        pattern = [
            (0, root),
            (2, fifth),
            (3, sixth),
            (5, flat7),
            (6, octave),
            (8, sixth),
            (9, fifth),
            (11, flat7),
        ]
        for offset, note in pattern:
            dest.append(self.note(start + offset, note, 1, 0.095, "bass", -0.02))

    def build(self) -> TrackArrangement:
        melody: list[NoteEvent] = []
        comp: list[NoteEvent] = []
        bass: list[NoteEvent] = []
        drums: list[DrumEvent] = []

        riff_e1 = [
            self.note(0, "E4", 1, 0.12, pan=0.02),
            self.note(1, "G4", 1, 0.13, pan=0.03),
            self.note(2, "A4", 2, 0.14, pan=0.04),
            self.note(5, "A#4", 1, 0.12, pan=0.03),
            self.note(6, "B4", 2, 0.15, pan=0.05),
            self.note(9, "D5", 1, 0.14, pan=0.05),
            self.note(10, "B4", 1, 0.13, pan=0.04),
            self.note(11, "G4", 1, 0.12, pan=0.03),
        ]
        riff_e2 = [
            self.note(0, "B4", 1, 0.14, pan=0.04),
            self.note(1, "D5", 1, 0.15, pan=0.05),
            self.note(2, "E5", 2, 0.16, pan=0.06),
            self.note(5, "D5", 1, 0.14, pan=0.05),
            self.note(6, "B4", 1, 0.13, pan=0.04),
            self.note(7, "A#4", 1, 0.12, pan=0.03),
            self.note(8, "A4", 1, 0.12, pan=0.03),
            self.note(9, "G4", 1, 0.12, pan=0.03),
            self.note(10, "E4", 2, 0.11, pan=0.01),
        ]
        riff_a = [
            self.note(0, "A4", 1, 0.13, pan=0.03),
            self.note(1, "C5", 1, 0.14, pan=0.04),
            self.note(2, "D5", 2, 0.15, pan=0.05),
            self.note(5, "D#5", 1, 0.13, pan=0.04),
            self.note(6, "E5", 2, 0.16, pan=0.06),
            self.note(9, "G5", 1, 0.15, pan=0.06),
            self.note(10, "E5", 1, 0.14, pan=0.05),
            self.note(11, "D5", 1, 0.13, pan=0.04),
        ]
        riff_b = [
            self.note(0, "B4", 1, 0.14, pan=0.04),
            self.note(1, "D5", 1, 0.15, pan=0.05),
            self.note(2, "F#5", 2, 0.16, pan=0.06),
            self.note(5, "A5", 1, 0.16, pan=0.07),
            self.note(6, "F#5", 1, 0.15, pan=0.06),
            self.note(7, "D5", 1, 0.14, pan=0.05),
            self.note(8, "C5", 1, 0.13, pan=0.04),
            self.note(9, "B4", 1, 0.13, pan=0.04),
            self.note(10, "A4", 2, 0.12, pan=0.03),
        ]
        turnaround = [
            self.note(0, "G4", 1, 0.12, pan=0.03),
            self.note(1, "G#4", 1, 0.12, pan=0.03),
            self.note(2, "A4", 1, 0.13, pan=0.04),
            self.note(3, "A#4", 1, 0.13, pan=0.04),
            self.note(4, "B4", 1, 0.14, pan=0.05),
            self.note(5, "C5", 1, 0.14, pan=0.05),
            self.note(6, "C#5", 1, 0.14, pan=0.05),
            self.note(7, "D5", 1, 0.15, pan=0.06),
            self.note(8, "D#5", 1, 0.15, pan=0.06),
            self.note(9, "E5", 1, 0.16, pan=0.06),
            self.note(10, "B4", 1, 0.13, pan=0.04),
            self.note(11, "R", 1, 0.00),
        ]

        for bar_idx, phrase in enumerate(
            [
                riff_e1,
                riff_e2,
                riff_e1,
                riff_e2,
                riff_a,
                riff_a,
                riff_e1,
                riff_e2,
                riff_b,
                riff_a,
                riff_e1,
                turnaround,
            ]
        ):
            self.add_phrase(melody, phrase, bar_offset=bar_idx)

        comp_chords = [
            ("D4", "G#4", "B4", "D5"),
            ("D4", "G#4", "B4", "D5"),
            ("D4", "G#4", "B4", "D5"),
            ("D4", "G#4", "B4", "D5"),
            ("G4", "C#5", "E5", "G5"),
            ("G4", "C#5", "E5", "G5"),
            ("D4", "G#4", "B4", "D5"),
            ("D4", "G#4", "B4", "D5"),
            ("A4", "D#5", "F#5", "A5"),
            ("G4", "C#5", "E5", "G5"),
            ("D4", "G#4", "B4", "D5"),
            ("A4", "D#5", "F#5", "A5"),
        ]
        bass_roots = ["E2", "E2", "E2", "E2", "A2", "A2", "E2", "E2", "B2", "A2", "E2", "B2"]
        for bar_idx in range(self.total_bars):
            self._add_comp_bar(
                comp, bar_idx, comp_chords[bar_idx], gain=0.021 if bar_idx < 8 else 0.023
            )
            self._add_shuffle_bass(bass, bar_idx, bass_roots[bar_idx])
            start = bar_idx * self.bar_steps
            drums.extend(
                [
                    self.drum(start + 0, "kick", 1, 0.060),
                    self.drum(start + 3, "hat", 1, 0.020, -0.10),
                    self.drum(start + 6, "snare", 1, 0.036, 0.03),
                    self.drum(start + 9, "hat", 1, 0.020, 0.10),
                ]
            )
            if bar_idx % 2 == 1:
                drums.append(self.drum(start + 11, "kick", 1, 0.028, -0.02))

        return TrackArrangement(tuple(comp + bass + melody), tuple(drums))


TRACK_BUILDERS = {
    TrainingBattleTrack.track_id: TrainingBattleTrack,
    SoftDungeonCrawlTrack.track_id: SoftDungeonCrawlTrack,
    BossBattleFrenzyTrack.track_id: BossBattleFrenzyTrack,
    BluesyOverhaulTrack.track_id: BluesyOverhaulTrack,
}
