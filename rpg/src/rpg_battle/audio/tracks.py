from __future__ import annotations

"""Generated music track definitions.

Each track subclasses :class:`TrackBuilder` so new songs can focus on the
musical arrangement rather than the low-level synthesis details.
"""

import math

import numpy as np

from rpg_battle.audio.builder import (
    ChordEvent,
    DrumEvent,
    NoteEvent,
    TrackArrangement,
    TrackBuilder,
    adsr,
    bass_voice,
    midi_to_freq,
    note_to_midi,
    one_pole_lowpass,
    pad_voice,
    pulse_wave,
    saw_wave,
    scale_path,
    sine_wave,
    soft_clip,
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
    steps_per_beat = 3
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
        bend_from: str | None = None,
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


class ChillExplorationTrack(TrackBuilder):
    """Seamless chill exploration loop based on the uploaded prototype.

    This track demonstrates a richer arrangement style with sustained pad
    chords, plucked melodic notes, and a loop-aware stereo delay.
    """

    track_id = "chill_exploration"
    bpm = 104
    total_bars = 8
    master_gain = 0.21
    cache_version = 2

    def _sine_wave(self, freq: float, times: np.ndarray) -> np.ndarray:
        return np.sin(2 * math.pi * freq * times).astype(np.float32)

    def _saw_wave(self, freq: float, times: np.ndarray) -> np.ndarray:
        phase = (freq * times) % 1.0
        return (2.0 * phase - 1.0).astype(np.float32)

    def _soft_clip(self, signal: np.ndarray, *, drive: float = 1.4) -> np.ndarray:
        return np.tanh(drive * signal).astype(np.float32)

    def _soft_pad(self, freq: float, times: np.ndarray) -> np.ndarray:
        slow = 0.15 * np.sin(2 * math.pi * 0.18 * times)
        signal = (
            0.36 * self._saw_wave(freq * (1.000 + 0.002 * slow), times)
            + 0.32 * self._saw_wave(freq * 0.997, times)
            + 0.20 * self._sine_wave(freq * 0.5, times)
            + 0.18 * self._sine_wave(freq * 2.0, times)
        )
        signal = one_pole_lowpass(signal, amount=0.018)
        return self._soft_clip(signal, drive=1.2) / 0.88

    def _glass_pluck(self, freq: float, times: np.ndarray) -> np.ndarray:
        signal = (
            0.55 * triangle_wave(freq, times)
            + 0.25 * self._sine_wave(freq * 2.0, times)
            + 0.12 * pulse_wave(freq * 4.0, times, duty=0.18)
        )
        bright_env = np.exp(-times / 0.06).astype(np.float32)
        rng = np.random.default_rng(7)
        signal += 0.06 * rng.uniform(-1.0, 1.0, len(times)).astype(np.float32) * bright_env
        signal = one_pole_lowpass(signal, amount=0.08)
        return self._soft_clip(signal, drive=1.1) / 0.82

    def _sub_bass(self, freq: float, times: np.ndarray) -> np.ndarray:
        signal = (
            0.72 * self._sine_wave(freq, times)
            + 0.22 * triangle_wave(freq, times)
            + 0.12 * self._sine_wave(freq * 0.5, times)
        )
        signal = one_pole_lowpass(signal, amount=0.03)
        return self._soft_clip(signal, drive=1.05) / 0.92

    def _airy_lead(self, freq: float, times: np.ndarray) -> np.ndarray:
        vibrato = 1.0 + 0.0035 * np.sin(2 * math.pi * 5.3 * times)
        signal = (
            0.40 * self._sine_wave(freq * vibrato, times)
            + 0.24 * triangle_wave(freq * (1.0 + 0.002), times)
            + 0.18 * self._sine_wave(freq * 2.0, times)
        )
        signal = one_pole_lowpass(signal, amount=0.05)
        return self._soft_clip(signal, drive=1.15) / 0.86

    def synth_note(
        self,
        note: str,
        dur_steps: int,
        *,
        voice: str = "pluck",
        gain: float = 0.12,
        pan: float = 0.0,
        bend_from: str | None = None,
    ) -> np.ndarray:
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        if note == "R":
            return np.zeros((sample_count, 2), dtype=np.float32)
        frequency = midi_to_freq(note_to_midi(note))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        if voice == "bass":
            signal = self._sub_bass(frequency, times)
            env = adsr(
                sample_count, self.sample_rate, attack=0.002, decay=0.05, sustain=0.82, release=0.08
            )
        elif voice == "pad":
            signal = self._soft_pad(frequency, times)
            env = adsr(
                sample_count, self.sample_rate, attack=0.05, decay=0.22, sustain=0.76, release=0.22
            )
        elif voice == "lead":
            signal = self._airy_lead(frequency, times)
            env = adsr(
                sample_count, self.sample_rate, attack=0.008, decay=0.08, sustain=0.72, release=0.12
            )
        else:
            signal = self._glass_pluck(frequency, times)
            env = adsr(
                sample_count, self.sample_rate, attack=0.001, decay=0.14, sustain=0.22, release=0.12
            )
        signal = signal * env * gain
        return stereoize(signal, pan=pan)

    def _synth_chord(
        self,
        notes: list[str],
        dur_steps: int,
        *,
        voice: str = "pad",
        gain: float = 0.10,
        pan: float = 0.0,
    ) -> np.ndarray:
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        signal = np.zeros(sample_count, dtype=np.float32)
        for idx, note in enumerate(notes):
            frequency = midi_to_freq(note_to_midi(note))
            detune = 1.0 + (idx - (len(notes) - 1) / 2.0) * 0.0025
            part = (
                self._soft_pad(frequency * detune, times)
                if voice == "pad"
                else self._glass_pluck(frequency * detune, times)
            )
            signal += part / max(1, len(notes))
        if voice == "pad":
            env = adsr(
                sample_count, self.sample_rate, attack=0.08, decay=0.30, sustain=0.78, release=0.28
            )
            signal = one_pole_lowpass(signal, amount=0.025)
        else:
            env = adsr(
                sample_count, self.sample_rate, attack=0.002, decay=0.18, sustain=0.20, release=0.12
            )
            signal = one_pole_lowpass(signal, amount=0.07)
        signal = signal * env * gain
        return stereoize(signal, pan=pan)

    def synth_drum(
        self,
        kind: str,
        *,
        dur_steps: int = 1,
        gain: float = 0.06,
        pan: float = 0.0,
    ) -> np.ndarray:
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        noise = np.random.default_rng(7).uniform(-1.0, 1.0, sample_count).astype(np.float32)
        if kind == "kick":
            f0, f1 = 95.0, 38.0
            sweep = f0 * ((f1 / f0) ** (times / max(float(times[-1]), 1e-6)))
            phase = 2 * math.pi * np.cumsum(sweep) / self.sample_rate
            body = np.sin(phase).astype(np.float32)
            click = 0.10 * noise * np.exp(-times / 0.008)
            env = np.exp(-times / 0.11).astype(np.float32)
            signal = (body + click) * env
        elif kind == "clap":
            burst1 = noise * np.exp(-times / 0.015)
            burst2 = np.pad((0.8 * noise[: max(1, sample_count - 450)]), (450, 0))[
                :sample_count
            ] * np.exp(-times / 0.020)
            burst3 = np.pad((0.6 * noise[: max(1, sample_count - 900)]), (900, 0))[
                :sample_count
            ] * np.exp(-times / 0.030)
            signal = 0.55 * burst1 + 0.30 * burst2 + 0.20 * burst3
        elif kind == "hat":
            hp = noise - one_pole_lowpass(noise, amount=0.22)
            env = np.exp(-times / 0.020).astype(np.float32)
            signal = hp * env * 0.55
        else:
            hp = noise - one_pole_lowpass(noise, amount=0.30)
            env = np.exp(-times / 0.045).astype(np.float32)
            signal = hp * env * 0.30
        signal *= gain
        return stereoize(signal, pan=pan)

    def _stereo_delay_loop(
        self, signal: np.ndarray, *, delay_sec: float = 0.25, wet: float = 0.12
    ) -> np.ndarray:
        delay = max(1, int(delay_sec * self.sample_rate))
        out = signal.copy()
        out += wet * np.roll(signal[:, ::-1], delay, axis=0)
        out += wet * 0.40 * np.roll(signal, 2 * delay, axis=0)
        return out

    def _place_loop(self, buf: np.ndarray, clip: np.ndarray, start_step: int) -> None:
        total = len(buf)
        start = int(round(start_step * self.step_seconds * self.sample_rate)) % total
        end = start + len(clip)
        if end <= total:
            buf[start:end] += clip
        else:
            split = total - start
            buf[start:] += clip[:split]
            buf[: end - total] += clip[split:]

    def build(self) -> TrackArrangement:
        note_events: list[NoteEvent] = []
        drum_events: list[DrumEvent] = []

        bar_1 = [
            self.note(1, "D5", 2, 0.10, "pluck", 0.10),
            self.note(4, "F5", 2, 0.10, "pluck", 0.12),
            self.note(7, "A5", 1, 0.10, "pluck", 0.14),
            self.note(9, "C6", 2, 0.11, "pluck", 0.15),
            self.note(12, "A5", 2, 0.10, "pluck", 0.14),
            self.note(14, "F5", 1, 0.09, "pluck", 0.12),
        ]
        bar_2 = [
            self.note(1, "Bb4", 2, 0.10, "pluck", 0.08),
            self.note(4, "D5", 2, 0.10, "pluck", 0.10),
            self.note(7, "F5", 1, 0.10, "pluck", 0.12),
            self.note(9, "A5", 2, 0.11, "pluck", 0.14),
            self.note(12, "F5", 2, 0.10, "pluck", 0.12),
            self.note(14, "D5", 1, 0.09, "pluck", 0.10),
        ]
        bar_3 = [
            self.note(1, "C5", 2, 0.10, "pluck", 0.08),
            self.note(4, "D5", 2, 0.10, "pluck", 0.10),
            self.note(7, "F5", 1, 0.10, "pluck", 0.12),
            self.note(9, "A5", 2, 0.11, "pluck", 0.14),
            self.note(12, "G5", 2, 0.10, "pluck", 0.12),
            self.note(14, "F5", 1, 0.09, "pluck", 0.10),
        ]
        bar_4 = [
            self.note(1, "G4", 2, 0.09, "pluck", 0.06),
            self.note(4, "C5", 2, 0.10, "pluck", 0.08),
            self.note(7, "D5", 2, 0.10, "pluck", 0.10),
            self.note(10, "E5", 2, 0.11, "pluck", 0.12),
            self.note(13, "D5", 1, 0.10, "pluck", 0.10),
            self.note(14, "G4", 1, 0.08, "pluck", 0.08),
        ]
        bar_8 = [
            self.note(1, "D5", 2, 0.10, "pluck", 0.10),
            self.note(4, "F5", 2, 0.10, "pluck", 0.12),
            self.note(7, "A5", 1, 0.10, "pluck", 0.14),
            self.note(9, "C6", 2, 0.11, "pluck", 0.15),
            self.note(12, "A5", 1, 0.10, "pluck", 0.14),
            self.note(13, "C6", 1, 0.10, "pluck", 0.15),
            self.note(14, "D6", 1, 0.11, "pluck", 0.16),
            self.note(15, "E6", 1, 0.11, "pluck", 0.18),
        ]
        lead_hook = [
            self.note(0, "A4", 4, 0.09, "lead", -0.10),
            self.note(4, "C5", 2, 0.10, "lead", -0.08),
            self.note(6, "D5", 4, 0.11, "lead", -0.06),
            self.note(10, "F5", 2, 0.10, "lead", -0.04),
            self.note(12, "E5", 4, 0.10, "lead", -0.02),
        ]
        lead_answer = [
            self.note(0, "G4", 4, 0.09, "lead", -0.10),
            self.note(4, "A4", 2, 0.10, "lead", -0.08),
            self.note(6, "C5", 4, 0.11, "lead", -0.06),
            self.note(10, "D5", 2, 0.10, "lead", -0.04),
            self.note(12, "C5", 4, 0.10, "lead", -0.02),
        ]
        pluck_plan = [bar_1, bar_2, bar_3, bar_4, bar_1, bar_2, bar_4, bar_8]
        bass_roots = ["D2", "Bb1", "F2", "C2", "G1", "Bb1", "C2", "D2"]
        for bar_index in range(self.total_bars):
            self.add_phrase(note_events, pluck_plan[bar_index], bar_offset=bar_index)
            base = bar_index * self.bar_steps
            root = bass_roots[bar_index]
            fifth = transpose_note(root, 7)
            octave = transpose_note(root, 12)
            for start, note, dur in [
                (0, root, 2),
                (3, fifth, 1),
                (4, root, 2),
                (8, octave, 2),
                (11, fifth, 1),
                (12, root, 2),
                (14, fifth, 2),
            ]:
                note_events.append(self.note(base + start, note, dur, 0.096, "bass", 0.00))
        self.add_phrase(note_events, lead_hook, bar_offset=2)
        self.add_phrase(note_events, lead_answer, bar_offset=6)
        for bar_index in range(self.total_bars):
            s = bar_index * self.bar_steps
            drum_events.extend(
                [
                    self.drum(s + 0, "kick", 1, 0.064, 0.00),
                    self.drum(s + 2, "hat", 1, 0.014, -0.10),
                    self.drum(s + 4, "clap", 1, 0.028, 0.02),
                    self.drum(s + 6, "hat", 1, 0.014, 0.10),
                    self.drum(s + 8, "kick", 1, 0.058, 0.00),
                    self.drum(s + 10, "hat", 1, 0.015, -0.10),
                    self.drum(s + 12, "clap", 1, 0.026, 0.02),
                    self.drum(s + 14, "hat", 1, 0.014, 0.10),
                    self.drum(s + 15, "shaker", 1, 0.011, 0.08),
                ]
            )
        return TrackArrangement(tuple(note_events), tuple(drum_events))

    def render(self) -> np.ndarray:
        arrangement = self.build()
        chord_plan = [
            ["D4", "F4", "A4", "C5", "E5"],
            ["Bb3", "D4", "F4", "A4"],
            ["F4", "A4", "C5", "G5"],
            ["C4", "G4", "D5", "E5"],
            ["G3", "Bb3", "D4", "F4", "A4"],
            ["Bb3", "D4", "F4", "A4"],
            ["C4", "G4", "D5", "E5"],
            ["D4", "F4", "A4", "C5", "E5"],
        ]
        total_samples = int(round(self.total_steps * self.step_seconds * self.sample_rate))
        mix = np.zeros((total_samples, 2), dtype=np.float32)
        for bar_index, chord in enumerate(chord_plan):
            clip = self._synth_chord(chord, 16, voice="pad", gain=0.105, pan=-0.03)
            self._place_loop(mix, clip, bar_index * self.bar_steps)
        for event in arrangement.note_events:
            clip = self.synth_note(
                event.note, event.duration_steps, voice=event.voice, gain=event.gain, pan=event.pan
            )
            self._place_loop(mix, clip, event.start_step)
        for event in arrangement.drum_events:
            clip = self.synth_drum(
                event.kind, dur_steps=event.duration_steps, gain=event.gain, pan=event.pan
            )
            self._place_loop(mix, clip, event.start_step)
        mix = self._stereo_delay_loop(mix, delay_sec=0.25, wet=0.12)
        peak = float(np.max(np.abs(mix)))
        if peak > 0:
            mix /= peak
        mix *= self.master_gain
        return np.clip(mix * 32767, -32768, 32767).astype(np.int16, copy=False)


class DMinorJamTrack(TrackBuilder):
    """Sixteen-bar D-minor jam loop with a long expressive solo.

    This port keeps the original track structure intact:
    - 16 distinct pluck/support bars so the back half opens up for the solo
    - a continuous guitarist-style jam with bends preserved via ``bend_from``
    - loop-wrapping event placement so long notes can cross the seam cleanly
    """

    track_id = "d_minor_jam"
    bpm = 126
    total_bars = 16
    master_gain = 0.19
    cache_version = 2
    wrap_loop_events = True

    SOLO_SCALE_PCS = {2, 5, 7, 9, 0}

    def _soft_pad(self, freq: float, times: np.ndarray) -> np.ndarray:
        signal = (
            0.34 * saw_wave(freq * 1.000, times)
            + 0.28 * saw_wave(freq * 0.997, times)
            + 0.18 * sine_wave(freq * 0.5, times)
            + 0.14 * triangle_wave(freq, times)
        )
        signal = one_pole_lowpass(signal, amount=0.020)
        return soft_clip(signal, drive=1.12) / 0.88

    def _glass_pluck(self, freq: float, times: np.ndarray) -> np.ndarray:
        signal = (
            0.46 * triangle_wave(freq, times)
            + 0.22 * pulse_wave(freq * 2.0, times, duty=0.18)
            + 0.14 * sine_wave(freq * 2.0, times)
        )
        pick = np.exp(-times / 0.040).astype(np.float32)
        rng = np.random.default_rng(7)
        signal += 0.035 * rng.uniform(-1.0, 1.0, len(times)).astype(np.float32) * pick
        signal = one_pole_lowpass(signal, amount=0.085)
        return soft_clip(signal, drive=1.06) / 0.84

    def _electric_lead(
        self, note: str, times: np.ndarray, *, bend_from: str | None = None
    ) -> np.ndarray:
        target_midi = note_to_midi(note)
        target_freq = midi_to_freq(target_midi)
        if not bend_from:
            freq_curve = np.full(len(times), target_freq, dtype=np.float32)
        else:
            start_midi = note_to_midi(bend_from)
            path = scale_path(start_midi, target_midi, self.SOLO_SCALE_PCS)
            freq_curve = np.full(len(times), target_freq, dtype=np.float32)
            bend_time = min(0.22, 0.08 + 0.03 * max(0, len(path) - 1))
            bend_count = min(len(times), max(4, int(round(bend_time * self.sample_rate))))
            cursor = 0
            pairs = max(1, len(path) - 1)
            for pair_index in range(pairs):
                remaining = bend_count - cursor
                if remaining <= 0:
                    break
                seg_count = (
                    remaining
                    if pair_index == pairs - 1
                    else max(4, remaining // (pairs - pair_index))
                )
                hold_count = max(1, int(seg_count * 0.65))
                f0 = midi_to_freq(path[pair_index])
                f1 = midi_to_freq(path[pair_index + 1])
                hold_end = min(len(times), cursor + hold_count)
                seg_end = min(len(times), cursor + seg_count)
                freq_curve[cursor:hold_end] = f0
                if seg_end > hold_end:
                    ramp = np.linspace(
                        0.0, 1.0, seg_end - hold_end, endpoint=False, dtype=np.float32
                    )
                    freq_curve[hold_end:seg_end] = f0 * ((f1 / f0) ** ramp)
                cursor = seg_end

        vib_env = (1.0 - np.exp(-times / 0.16)).astype(np.float32)
        vib_semitones = (
            0.045 * vib_env * np.sin(2 * math.pi * 5.4 * times)
            + 0.014 * vib_env * np.sin(2 * math.pi * 7.1 * times + 0.3)
        ).astype(np.float32)
        freq_curve = freq_curve * (2.0 ** (vib_semitones / 12.0))
        phase1 = (2 * math.pi * np.cumsum(freq_curve) / self.sample_rate).astype(np.float32)
        phase2 = (2 * math.pi * np.cumsum(freq_curve * 1.0032) / self.sample_rate).astype(
            np.float32
        )
        saw1 = (2.0 * ((phase1 / (2 * math.pi)) % 1.0) - 1.0).astype(np.float32)
        saw2 = (2.0 * ((phase2 / (2 * math.pi)) % 1.0) - 1.0).astype(np.float32)
        square = np.sign(np.sin(phase1)).astype(np.float32)
        signal = (
            0.30 * saw1
            + 0.22 * saw2
            + 0.18 * square
            + 0.18 * np.sin(phase1)
            + 0.10 * np.sin(2.0 * phase1 + 0.12)
        )
        pick_noise = np.random.default_rng(7).uniform(-1.0, 1.0, len(times)).astype(np.float32)
        pick_noise *= np.exp(-times / 0.014)
        signal += 0.018 * pick_noise
        signal = one_pole_lowpass(signal, amount=0.078)
        signal = soft_clip(signal, drive=1.85)
        return signal / 0.94

    def synth_note(
        self,
        note: str,
        dur_steps: int,
        *,
        voice: str = "pluck",
        gain: float = 0.12,
        pan: float = 0.0,
        bend_from: str | None = None,
    ) -> np.ndarray:
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        if note == "R":
            return np.zeros((sample_count, 2), dtype=np.float32)
        frequency = midi_to_freq(note_to_midi(note))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        if voice == "bass":
            signal = bass_voice(frequency, times)
            env = adsr(
                sample_count,
                self.sample_rate,
                attack=0.002,
                decay=0.05,
                sustain=0.84,
                release=0.07,
            )
        elif voice == "solo":
            signal = self._electric_lead(note, times, bend_from=bend_from)
            env = adsr(
                sample_count,
                self.sample_rate,
                attack=0.0015,
                decay=0.06,
                sustain=0.86,
                release=0.10,
            )
        else:
            signal = self._glass_pluck(frequency, times)
            env = adsr(
                sample_count,
                self.sample_rate,
                attack=0.001,
                decay=0.10,
                sustain=0.18,
                release=0.09,
            )
        signal = signal * env * gain
        return stereoize(signal, pan=pan)

    def synth_chord(
        self,
        notes: list[str],
        dur_steps: int,
        *,
        voice: str = "pad",
        gain: float = 0.10,
        pan: float = 0.0,
    ) -> np.ndarray:
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        signal = np.zeros(sample_count, dtype=np.float32)
        for idx, note in enumerate(notes):
            frequency = midi_to_freq(note_to_midi(note))
            detune = 1.0 + (idx - (len(notes) - 1) / 2.0) * 0.0020
            signal += self._soft_pad(frequency * detune, times) / max(1, len(notes))
        env = adsr(
            sample_count,
            self.sample_rate,
            attack=0.07,
            decay=0.26,
            sustain=0.78,
            release=0.22,
        )
        signal = one_pole_lowpass(signal, amount=0.026)
        signal = signal * env * gain
        return stereoize(signal, pan=pan)

    def synth_drum(
        self, kind: str, *, dur_steps: int = 1, gain: float = 0.06, pan: float = 0.0
    ) -> np.ndarray:
        sample_count = max(1, int(round(dur_steps * self.step_seconds * self.sample_rate)))
        times = np.arange(sample_count, dtype=np.float32) / self.sample_rate
        noise = np.random.default_rng(7).uniform(-1.0, 1.0, sample_count).astype(np.float32)
        if kind == "kick":
            f0, f1 = 96.0, 40.0
            sweep = f0 * ((f1 / f0) ** (times / max(float(times[-1]), 1e-6)))
            phase = 2 * math.pi * np.cumsum(sweep) / self.sample_rate
            body = np.sin(phase).astype(np.float32)
            click = 0.07 * noise * np.exp(-times / 0.008)
            env = np.exp(-times / 0.10).astype(np.float32)
            signal = (body + click) * env
        elif kind == "clap":
            burst1 = noise * np.exp(-times / 0.014)
            burst2 = np.pad((0.7 * noise[: max(1, sample_count - 380)]), (380, 0))[:sample_count]
            burst2 *= np.exp(-times / 0.018)
            burst3 = np.pad((0.5 * noise[: max(1, sample_count - 760)]), (760, 0))[:sample_count]
            burst3 *= np.exp(-times / 0.024)
            signal = 0.54 * burst1 + 0.28 * burst2 + 0.18 * burst3
        elif kind == "hat":
            hp = noise - one_pole_lowpass(noise, amount=0.24)
            env = np.exp(-times / 0.016).astype(np.float32)
            signal = hp * env * 0.46
        else:
            hp = noise - one_pole_lowpass(noise, amount=0.32)
            env = np.exp(-times / 0.035).astype(np.float32)
            signal = hp * env * 0.22
        signal *= gain
        return stereoize(signal, pan=pan)

    def process_mix(self, mix: np.ndarray) -> np.ndarray:
        delay = max(1, int(0.19 * self.sample_rate))
        out = mix.copy()
        out += 0.07 * np.roll(mix[:, ::-1], delay, axis=0)
        out += 0.07 * 0.25 * np.roll(mix, 2 * delay, axis=0)
        return out

    def build(self) -> TrackArrangement:
        chords: list[ChordEvent] = []
        notes: list[NoteEvent] = []
        drums: list[DrumEvent] = []

        chord_plan = [
            ["D4", "F4", "A4"],
            ["Bb3", "D4", "F4"],
            ["F4", "A4", "C5"],
            ["C4", "G4", "D5"],
            ["D4", "F4", "A4"],
            ["Bb3", "D4", "F4"],
            ["F4", "A4", "C5"],
            ["C4", "G4", "D5"],
            ["D4", "F4", "A4"],
            ["Bb3", "D4", "F4"],
            ["F4", "A4", "C5"],
            ["C4", "G4", "D5"],
            ["D4", "F4", "A4"],
            ["Bb3", "D4", "F4"],
            ["F4", "A4", "C5"],
            ["C4", "G4", "D5"],
        ]
        bass_roots = [
            "D2",
            "Bb1",
            "F2",
            "C2",
            "D2",
            "Bb1",
            "F2",
            "C2",
            "D2",
            "Bb1",
            "F2",
            "C2",
            "D2",
            "Bb1",
            "F2",
            "C2",
        ]
        bar_1 = [
            self.note(0, "D5", 2, 0.074, "pluck", 0.10),
            self.note(4, "A4", 2, 0.070, "pluck", 0.12),
            self.note(8, "F5", 2, 0.072, "pluck", 0.14),
            self.note(12, "A4", 2, 0.068, "pluck", 0.12),
        ]
        bar_2 = [
            self.note(0, "Bb4", 2, 0.072, "pluck", 0.08),
            self.note(4, "F5", 2, 0.070, "pluck", 0.10),
            self.note(8, "D5", 2, 0.070, "pluck", 0.12),
            self.note(12, "F5", 2, 0.068, "pluck", 0.10),
        ]
        bar_3 = [
            self.note(0, "F5", 2, 0.072, "pluck", 0.08),
            self.note(4, "C5", 2, 0.070, "pluck", 0.10),
            self.note(8, "A4", 2, 0.070, "pluck", 0.12),
            self.note(12, "C5", 2, 0.068, "pluck", 0.10),
        ]
        bar_4 = [
            self.note(0, "C5", 2, 0.070, "pluck", 0.06),
            self.note(4, "G4", 2, 0.068, "pluck", 0.08),
            self.note(8, "D5", 2, 0.070, "pluck", 0.10),
            self.note(12, "G4", 2, 0.066, "pluck", 0.08),
        ]
        support_5 = [
            self.note(0, "D5", 1, 0.040, "pluck", 0.08),
            self.note(8, "F5", 1, 0.038, "pluck", 0.10),
        ]
        support_6 = [
            self.note(0, "Bb4", 1, 0.040, "pluck", 0.08),
            self.note(8, "D5", 1, 0.038, "pluck", 0.10),
        ]
        support_7 = [
            self.note(0, "F5", 1, 0.040, "pluck", 0.08),
            self.note(8, "C5", 1, 0.038, "pluck", 0.10),
        ]
        support_8 = [
            self.note(0, "C5", 1, 0.040, "pluck", 0.06),
            self.note(8, "D5", 1, 0.040, "pluck", 0.10),
            self.note(14, "C5", 1, 0.042, "pluck", 0.12),
            self.note(15, "D5", 1, 0.044, "pluck", 0.14),
        ]
        support_9 = [
            self.note(0, "D5", 1, 0.034, "pluck", 0.08),
            self.note(8, "A4", 1, 0.032, "pluck", 0.10),
        ]
        support_10 = [
            self.note(0, "Bb4", 1, 0.034, "pluck", 0.08),
            self.note(8, "F5", 1, 0.032, "pluck", 0.10),
        ]
        support_11 = [
            self.note(0, "F5", 1, 0.034, "pluck", 0.08),
            self.note(8, "C5", 1, 0.032, "pluck", 0.10),
        ]
        support_12 = [
            self.note(0, "C5", 1, 0.034, "pluck", 0.06),
            self.note(8, "G4", 1, 0.032, "pluck", 0.08),
        ]
        support_13 = [self.note(0, "D5", 1, 0.032, "pluck", 0.08)]
        support_14 = [self.note(0, "Bb4", 1, 0.032, "pluck", 0.08)]
        support_15 = [
            self.note(0, "F5", 1, 0.034, "pluck", 0.08),
            self.note(12, "D5", 1, 0.030, "pluck", 0.10),
        ]
        support_16 = [
            self.note(0, "C5", 1, 0.032, "pluck", 0.06),
            self.note(12, "A4", 1, 0.030, "pluck", 0.08),
            self.note(14, "C5", 1, 0.036, "pluck", 0.12),
            self.note(15, "D5", 1, 0.040, "pluck", 0.14),
        ]
        phrase_plan = [
            bar_1,
            bar_2,
            bar_3,
            bar_4,
            support_5,
            support_6,
            support_7,
            support_8,
            support_9,
            support_10,
            support_11,
            support_12,
            support_13,
            support_14,
            support_15,
            support_16,
        ]

        for bar_idx in range(self.total_bars):
            if bar_idx < 4:
                pad_gain = 0.082
            elif bar_idx < 8:
                pad_gain = 0.072
            elif bar_idx < 14:
                pad_gain = 0.064
            else:
                pad_gain = 0.070
            chords.append(
                self.chord(
                    bar_idx * self.bar_steps, chord_plan[bar_idx], 16, pad_gain, "pad", -0.04
                )
            )
            self.add_phrase(notes, phrase_plan[bar_idx], bar_offset=bar_idx)
            base = bar_idx * self.bar_steps
            root = bass_roots[bar_idx]
            fifth = transpose_note(root, 7)
            octave = transpose_note(root, 12)
            for offset, note, dur in [
                (0, root, 2),
                (4, root, 2),
                (8, octave, 2),
                (12, fifth, 2),
                (14, root, 2),
            ]:
                notes.append(self.note(base + offset, note, dur, 0.086, "bass"))
            fill = bar_idx in {7, 11, 15}
            jam = 8 <= bar_idx <= 13
            drums.extend(
                [
                    self.drum(base + 0, "kick", 1, 0.058),
                    self.drum(base + 2, "hat", 1, 0.011, -0.10),
                    self.drum(base + 4, "clap", 1, 0.022, 0.02),
                    self.drum(base + 6, "hat", 1, 0.011, 0.10),
                    self.drum(base + 8, "kick", 1, 0.054),
                    self.drum(base + 10, "hat", 1, 0.012, -0.10),
                    self.drum(base + 12, "clap", 1, 0.021, 0.02),
                    self.drum(base + 14, "hat", 1, 0.011, 0.10),
                    self.drum(base + 15, "shaker", 1, 0.009, 0.08),
                ]
            )
            if jam:
                drums.extend(
                    [
                        self.drum(base + 1, "hat", 1, 0.008, -0.06),
                        self.drum(base + 9, "hat", 1, 0.008, 0.06),
                    ]
                )
            if fill:
                drums.extend(
                    [
                        self.drum(base + 13, "hat", 1, 0.010, -0.08),
                        self.drum(base + 14, "kick", 1, 0.034, -0.02),
                        self.drum(base + 15, "hat", 1, 0.010, 0.08),
                    ]
                )

        solo_events = [
            self.note(64, "D5", 4, 0.108, "solo", -0.06, "C5"),
            self.note(68, "F5", 4, 0.112, "solo", -0.04, "D5"),
            self.note(72, "A5", 4, 0.118, "solo", -0.02, "G5"),
            self.note(76, "G5", 4, 0.110, "solo", -0.02, "F5"),
            self.note(80, "A5", 1, 0.102, "solo", 0.00),
            self.note(81, "G5", 1, 0.100, "solo", 0.00),
            self.note(82, "F5", 1, 0.100, "solo", 0.00),
            self.note(83, "D5", 1, 0.098, "solo", 0.00),
            self.note(84, "A5", 1, 0.102, "solo", 0.00),
            self.note(85, "G5", 1, 0.100, "solo", 0.00),
            self.note(86, "F5", 1, 0.100, "solo", 0.00),
            self.note(87, "D5", 1, 0.098, "solo", 0.00),
            self.note(88, "C6", 1, 0.104, "solo", 0.02),
            self.note(89, "A5", 1, 0.102, "solo", 0.02),
            self.note(90, "G5", 1, 0.100, "solo", 0.02),
            self.note(91, "F5", 1, 0.100, "solo", 0.02),
            self.note(92, "A5", 1, 0.102, "solo", 0.02),
            self.note(93, "G5", 1, 0.100, "solo", 0.02),
            self.note(94, "F5", 1, 0.100, "solo", 0.02),
            self.note(95, "D5", 1, 0.098, "solo", 0.02),
            self.note(96, "G5", 4, 0.112, "solo", -0.02, "F5"),
            self.note(100, "A5", 4, 0.118, "solo", 0.00, "G5"),
            self.note(104, "F5", 4, 0.112, "solo", 0.02, "D5"),
            self.note(108, "D5", 4, 0.108, "solo", 0.02, "C5"),
            self.note(112, "C6", 1, 0.104, "solo", 0.02),
            self.note(113, "A5", 1, 0.102, "solo", 0.02),
            self.note(114, "G5", 1, 0.100, "solo", 0.02),
            self.note(115, "F5", 1, 0.100, "solo", 0.02),
            self.note(116, "A5", 1, 0.104, "solo", 0.04),
            self.note(117, "G5", 1, 0.102, "solo", 0.04),
            self.note(118, "F5", 1, 0.100, "solo", 0.04),
            self.note(119, "D5", 1, 0.098, "solo", 0.04),
            self.note(120, "G5", 2, 0.108, "solo", 0.04, "F5"),
            self.note(122, "F5", 2, 0.104, "solo", 0.06, "D5"),
            self.note(124, "D5", 2, 0.104, "solo", 0.08, "C5"),
            self.note(126, "C5", 1, 0.102, "solo", 0.10),
            self.note(127, "D5", 1, 0.106, "solo", 0.12),
            self.note(128, "D5", 4, 0.108, "solo", -0.06, "C5"),
            self.note(132, "F5", 2, 0.110, "solo", -0.04, "D5"),
            self.note(134, "G5", 2, 0.108, "solo", -0.02),
            self.note(136, "A5", 2, 0.116, "solo", 0.00, "G5"),
            self.note(138, "G5", 1, 0.102, "solo", 0.00),
            self.note(139, "F5", 1, 0.100, "solo", 0.00),
            self.note(140, "D5", 1, 0.098, "solo", 0.00),
            self.note(141, "C5", 1, 0.096, "solo", 0.00),
            self.note(142, "D5", 2, 0.104, "solo", 0.02),
            self.note(144, "A5", 1, 0.104, "solo", 0.00),
            self.note(145, "G5", 1, 0.102, "solo", 0.00),
            self.note(146, "F5", 1, 0.100, "solo", 0.00),
            self.note(147, "D5", 1, 0.098, "solo", 0.00),
            self.note(148, "D5", 1, 0.100, "solo", 0.02),
            self.note(149, "F5", 1, 0.102, "solo", 0.02),
            self.note(150, "G5", 1, 0.104, "solo", 0.02),
            self.note(151, "A5", 1, 0.106, "solo", 0.02),
            self.note(152, "C6", 4, 0.112, "solo", 0.04, "A5"),
            self.note(156, "A5", 4, 0.108, "solo", 0.04),
            self.note(160, "A5", 1, 0.104, "solo", 0.00),
            self.note(161, "G5", 1, 0.102, "solo", 0.00),
            self.note(162, "F5", 1, 0.100, "solo", 0.00),
            self.note(163, "D5", 1, 0.098, "solo", 0.00),
            self.note(164, "A5", 1, 0.104, "solo", 0.00),
            self.note(165, "G5", 1, 0.102, "solo", 0.00),
            self.note(166, "F5", 1, 0.100, "solo", 0.00),
            self.note(167, "D5", 1, 0.098, "solo", 0.00),
            self.note(168, "C6", 1, 0.106, "solo", 0.02),
            self.note(169, "A5", 1, 0.104, "solo", 0.02),
            self.note(170, "G5", 1, 0.102, "solo", 0.02),
            self.note(171, "F5", 1, 0.100, "solo", 0.02),
            self.note(172, "A5", 1, 0.104, "solo", 0.02),
            self.note(173, "G5", 1, 0.102, "solo", 0.02),
            self.note(174, "F5", 1, 0.100, "solo", 0.02),
            self.note(175, "D5", 1, 0.098, "solo", 0.02),
            self.note(176, "G5", 4, 0.110, "solo", 0.04, "F5"),
            self.note(180, "A5", 4, 0.116, "solo", 0.06, "G5"),
            self.note(184, "C6", 2, 0.112, "solo", 0.06, "A5"),
            self.note(186, "A5", 1, 0.104, "solo", 0.04),
            self.note(187, "G5", 1, 0.102, "solo", 0.04),
            self.note(188, "F5", 1, 0.100, "solo", 0.04),
            self.note(189, "D5", 1, 0.098, "solo", 0.04),
            self.note(190, "C5", 1, 0.096, "solo", 0.04),
            self.note(191, "D5", 1, 0.100, "solo", 0.04),
            self.note(192, "F5", 4, 0.110, "solo", 0.04, "D5"),
            self.note(196, "G5", 4, 0.112, "solo", 0.04, "F5"),
            self.note(200, "A5", 4, 0.116, "solo", 0.06, "G5"),
            self.note(204, "C6", 4, 0.112, "solo", 0.06, "A5"),
            self.note(208, "A5", 1, 0.104, "solo", 0.02),
            self.note(209, "G5", 1, 0.102, "solo", 0.02),
            self.note(210, "F5", 1, 0.100, "solo", 0.02),
            self.note(211, "D5", 1, 0.098, "solo", 0.02),
            self.note(212, "C6", 1, 0.106, "solo", 0.02),
            self.note(213, "A5", 1, 0.104, "solo", 0.02),
            self.note(214, "G5", 1, 0.102, "solo", 0.02),
            self.note(215, "F5", 1, 0.100, "solo", 0.02),
            self.note(216, "A5", 2, 0.112, "solo", 0.04, "G5"),
            self.note(218, "C6", 2, 0.114, "solo", 0.04, "A5"),
            self.note(220, "A5", 1, 0.104, "solo", 0.04),
            self.note(221, "G5", 1, 0.102, "solo", 0.04),
            self.note(222, "F5", 1, 0.100, "solo", 0.04),
            self.note(223, "D5", 1, 0.098, "solo", 0.04),
            self.note(224, "F5", 4, 0.108, "solo", -0.02, "D5"),
            self.note(228, "D5", 4, 0.102, "solo", 0.00),
            self.note(232, "C5", 4, 0.098, "solo", 0.02),
            self.note(236, "A4", 4, 0.094, "solo", 0.02),
            self.note(240, "D5", 4, 0.104, "solo", 0.04, "C5"),
            self.note(244, "F5", 2, 0.106, "solo", 0.04, "D5"),
            self.note(246, "D5", 2, 0.100, "solo", 0.02),
            self.note(248, "C5", 2, 0.096, "solo", 0.02),
            self.note(250, "A4", 2, 0.092, "solo", 0.02),
            self.note(252, "C5", 2, 0.096, "solo", 0.04),
            self.note(254, "C5", 1, 0.094, "solo", 0.04),
            self.note(255, "D5", 1, 0.098, "solo", 0.06),
        ]
        notes.extend(solo_events)
        return TrackArrangement(tuple(notes), tuple(drums), tuple(chords))


TRACK_BUILDERS = {
    TrainingBattleTrack.track_id: TrainingBattleTrack,
    SoftDungeonCrawlTrack.track_id: SoftDungeonCrawlTrack,
    BossBattleFrenzyTrack.track_id: BossBattleFrenzyTrack,
    BluesyOverhaulTrack.track_id: BluesyOverhaulTrack,
    ChillExplorationTrack.track_id: ChillExplorationTrack,
    DMinorJamTrack.track_id: DMinorJamTrack,
}
