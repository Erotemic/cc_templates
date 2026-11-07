"""Tiny original synthesized soundtrack; silent fallback for school machines.

No downloaded samples, NumPy, SVG libraries, or asset build step required.
"""

from __future__ import annotations

from array import array
from math import pi, sin

SAMPLE_RATE = 16000


def _pcm(samples):
    out = array("h")
    peak = max((abs(s) for s in samples), default=1) or 1
    scale = min(1.0, 0.85 / peak)
    for sample in samples:
        q = int(max(-1, min(1, sample * scale)) * 32767)
        out.extend((q, q))
    return out.tobytes()


def _note(samples, start, duration, midi, volume, *, softness=2):
    frequency = 440 * 2 ** ((midi - 69) / 12)
    count = round(duration * SAMPLE_RATE)
    offset = round(start * SAMPLE_RATE)
    for index in range(count):
        elapsed = index / SAMPLE_RATE
        env = min(1, elapsed * 70) * max(0, (duration - elapsed) / duration) ** softness
        phase = 2 * pi * frequency * elapsed
        samples[(offset + index) % len(samples)] += volume * env * (
            sin(phase) + 0.12 * sin(2 * phase))


def music():
    """Original 8-bar looping melody in D minor; notes are easy to edit."""
    beat = 0.45
    samples = [0.0] * int(8 * 4 * beat * SAMPLE_RATE)
    chords = ((50, 53, 57), (46, 50, 53), (48, 52, 55), (45, 49, 52))
    melody = ((74, 77, 81, 77), (72, 74, 77, 74),
              (76, 79, 81, 79), (73, 76, 81, 76))
    for bar in range(8):
        start = bar * 4 * beat
        chord = chords[bar % 4]
        for note in chord:
            _note(samples, start, 1.7, note, 0.017, softness=1)
        for step, note in enumerate(melody[bar % 4]):
            _note(samples, start + step * beat, 0.39, note, 0.064)
        for step in (0, 2):
            _note(samples, start + step * beat, 0.75, chord[0] - 12, 0.08)
    return _pcm(samples)


def effect(name):
    lengths = {"jump": .13, "dash": .21, "land": .08,
               "hurt": .26, "room": .28, "win": .52,
               "berry": .18, "crystal": .24, "checkpoint": .30}
    duration = lengths[name]
    samples = []
    phase = 0.0
    for i in range(round(duration * SAMPLE_RATE)):
        u = i / (duration * SAMPLE_RATE)
        pitch = {"jump": (310, 720), "dash": (520, 150),
                 "land": (230, 90), "hurt": (570, 100),
                 "room": (400, 780), "win": (420, 1040),
                 "berry": (610, 930), "crystal": (480, 1160),
                 "checkpoint": (410, 820)}[name]
        hz = pitch[0] + (pitch[1] - pitch[0]) * u
        phase += 2 * pi * hz / SAMPLE_RATE
        env = (1 - u) ** 1.5 * min(1, u * 60)
        samples.append(.18 * env * (sin(phase) + 0.13 * sin(3 * phase)))
    return _pcm(samples)


class SoundBoard:
    def __init__(self, pg):
        self.pg = pg
        self.muted = False
        self.sounds = {}
        self.song = None
        try:
            if not pg.mixer.get_init():
                pg.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)
            self.sounds = {name: pg.mixer.Sound(buffer=effect(name))
                           for name in ("jump", "dash", "land", "hurt", "room",
                                        "win", "berry", "crystal", "checkpoint")}
            self.song = pg.mixer.Sound(buffer=music())
            self.song.set_volume(.2)
            self.song.play(loops=-1)
        except pg.error:
            self.sounds = {}
            self.song = None

    def play(self, events):
        if self.muted:
            return
        for event in events:
            if event in self.sounds:
                self.sounds[event].play()

    def toggle(self):
        self.muted = not self.muted
        if self.song:
            self.song.set_volume(0 if self.muted else .2)

    def close(self):
        if self.song:
            self.song.stop()
