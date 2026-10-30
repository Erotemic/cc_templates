"""Small original soundtrack and effects, synthesized directly in Python.

No WAV files, NumPy, or extra tools. Pygame's mixer plays the generated
samples. Mission 7 can choose a different melody for each level.
"""

from array import array
from math import pi, sin

from . import student

SAMPLE_RATE = 22050
NOTE_LENGTH = 0.28  # seconds between notes

# Each number is a piano/MIDI note. The music repeats after the last note.
MELODY = (72, 76, 79, 76, 74, 77, 81, 77,
          76, 79, 83, 79, 74, 77, 79, 72)
BASS = (48, 50, 52, 48)


def pitch(number: int) -> float:
    """Convert a MIDI note to its frequency (A4, note 69, is 440 Hz)."""
    return 440 * 2 ** ((number - 69) / 12)


def add_note(samples: list[float], start: float, length: float,
             number: int, volume: float, sample_rate: int) -> None:
    """Add one gently faded tone to a list of audio samples."""
    first = int(start * sample_rate)
    count = min(int(length * sample_rate), len(samples) - first)
    hz = pitch(number)
    for i in range(max(0, count)):
        t = i / sample_rate
        fade = min(1.0, t / 0.01, (length - t) / 0.06)
        wave = sin(2 * pi * hz * t) + 0.18 * sin(4 * pi * hz * t)
        samples[first + i] += volume * fade * wave


def make_music(sample_rate: int = SAMPLE_RATE,
               melody: tuple[int, ...] | None = None) -> list[float]:
    """Synthesize any student's melody, or use the original by default."""
    notes = MELODY if melody is None else melody
    if not notes:
        raise ValueError("The melody needs at least one note")
    samples = [0.0] * int(len(notes) * NOTE_LENGTH * sample_rate)
    for index, note in enumerate(notes):
        start = index * NOTE_LENGTH
        add_note(samples, start, NOTE_LENGTH * 0.85, note,
                 0.14, sample_rate)
        if index % 4 == 0:
            add_note(samples, start, NOTE_LENGTH * 3.8,
                     BASS[(index // 4) % len(BASS)], 0.09, sample_rate)
    return samples


EFFECTS = ("jump", "star", "hurt", "bounce", "level", "win")


def make_effect(name: str, sample_rate: int = SAMPLE_RATE) -> list[float]:
    """Generate a chirp for an event (nothing is read from disk)."""
    durations = {"jump": 0.16, "star": 0.25, "hurt": 0.24,
                 "bounce": 0.25, "level": 0.40, "win": 0.72}
    duration = durations[name]  # A misspelled event raises KeyError.
    samples = []
    phase = 0.0
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        fraction = t / duration
        if name == "jump":
            hz = 320 + 400 * fraction
        elif name == "star":
            hz = (659, 880)[min(1, int(fraction * 2))]
        elif name == "hurt":
            hz = 340 - 210 * fraction
        elif name == "bounce":
            hz = 240 + 750 * fraction
        elif name == "level":
            hz = (523, 659, 784)[min(2, int(fraction * 3))]
        else:  # win
            hz = (523, 659, 784, 1046)[min(3, int(fraction * 4))]
        phase += 2 * pi * hz / sample_rate
        fade = min(1.0, t / 0.008) * (1.0 - fraction) ** 1.4
        samples.append(0.28 * fade * sin(phase))
    return samples


def pcm16(samples: list[float], channels: int = 2) -> bytes:
    """Convert numbers between -1 and +1 into signed 16-bit mixer bytes."""
    if channels not in (1, 2):
        raise ValueError("Only mono or stereo are supported")
    output = array("h")
    for sample in samples:
        value = round(max(-1.0, min(1.0, sample)) * 32767)
        for _ in range(channels):
            output.append(value)
    return output.tobytes()


class SoundBoard:
    """Loop music, play event effects, and degrade gracefully without audio."""

    def __init__(self, pygame_module):
        self._pygame = pygame_module
        self.available = False
        self.muted = False
        self.music_channel = None
        self._music = None
        self._songs = {}
        self._current_melody = None
        self._mixer = None
        self._sample_rate = SAMPLE_RATE
        self._channels = 2
        self.effects = {}
        try:
            mixer = pygame_module.mixer
            config = mixer.get_init()
            if config is None:
                return
            sample_rate, sample_format, channels = config
            if sample_format != -16 or channels not in (1, 2):
                return
            self.effects = {
                name: mixer.Sound(buffer=pcm16(make_effect(name, sample_rate), channels))
                for name in EFFECTS
            }
            self._music = mixer.Sound(buffer=pcm16(make_music(sample_rate), channels))
            self._songs[None] = self._music
            self._mixer = mixer
            self._sample_rate = sample_rate
            self._channels = channels
            mixer.set_reserved(1)
            self.music_channel = mixer.Channel(0)
            self.music_channel.set_volume(0.22)
            self.music_channel.play(self._music, loops=-1)
            self.available = True
        except (pygame_module.error, OSError, ValueError) as error:
            print(f"Sound disabled: {error}")

    def set_level(self, index: int) -> None:
        """Mission 7: change music on a level boundary, not every frame."""
        if not self.available:
            return
        selected = student.level_melody(index)
        notes = tuple(selected) if selected is not None else None
        if notes == self._current_melody:
            return  # Avoid restarting the song 60 times per second.
        try:
            if notes not in self._songs:
                samples = make_music(self._sample_rate, notes)
                self._songs[notes] = self._mixer.Sound(
                    buffer=pcm16(samples, self._channels))
            self._music = self._songs[notes]
            self.music_channel.play(self._music, loops=-1)
            self._current_melody = notes
            if self.muted:
                self.music_channel.pause()
        except (self._pygame.error, OSError, ValueError) as error:
            print(f"New level music disabled: {error}")

    def play(self, events: list[str]) -> None:
        if self.available and not self.muted:
            for name in events:
                if name in self.effects:
                    self.effects[name].play()

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        if self.music_channel is not None:
            if self.muted:
                self.music_channel.pause()
            else:
                self.music_channel.unpause()

    def close(self) -> None:
        if self.music_channel is not None:
            self.music_channel.stop()
