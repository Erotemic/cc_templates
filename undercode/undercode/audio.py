"""Small original synthesized soundtrack/cues; pygame + standard library only."""

from array import array
import math
import os
from pathlib import Path
import sys
import pygame


class Audio:
    def __init__(self, enabled=True):
        self.enabled = False
        self.muted = not enabled
        self.current_scene = None
        self.effects = {}
        self.music = {}
        if not enabled:
            return
        if sys.platform.startswith("linux") and not os.environ.get("SDL_AUDIODRIVER"):
            runtime = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
            endpoint = (
                any(Path("/dev/snd").glob("pcm*p"))
                or os.environ.get("PULSE_SERVER")
                or os.environ.get("PIPEWIRE_REMOTE")
                or (runtime / "pulse/native").exists()
                or (runtime / "pipewire-0").exists()
            )
            if not endpoint:
                return
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            pygame.mixer.set_num_channels(12)
            pygame.mixer.set_reserved(1)
            self.enabled = True
            notes = {
                "move": (500, 0.035),
                "select": (700, 0.09),
                "hit": (140, 0.12),
                "hurt": (95, 0.16),
                "block": (950, 0.08),
                "jump": (420, 0.07),
                "heal": (780, 0.2),
                "win": (1040, 0.3),
                "soft": (330, 0.12),
                "transition": (260, 0.18),
            }
            self.effects = {name: self.tone(hz, seconds) for name, (hz, seconds) in notes.items()}
            self.music = {"WORLD": self.theme(False), "BATTLE": self.theme(True)}
        except pygame.error as error:
            print(f"Audio unavailable; continuing silently: {error}")
            self.enabled = False

    @property
    def label(self):
        if not self.enabled:
            return "Sound unavailable / off"
        return "M: sound off" if self.muted else "M: sound on"

    def tone(self, hz, duration):
        rate = 22050
        data = array("h")
        for i in range(int(rate * duration)):
            t = i / rate
            envelope = min(1, t / 0.008) * (1 - t / duration) ** 2
            sample = math.sin(2 * math.pi * hz * t) + 0.2 * math.sin(4 * math.pi * hz * t)
            data.append(round(6500 * envelope * sample))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def theme(self, battle):
        rate, beat = 22050, 0.32 if battle else 0.48
        melody = (64, 67, 71, 74, 71, 67, 62, 67, 64, 69, 72, 76, 72, 69, 67, 62)
        data = array("h")
        for i in range(int(rate * beat * len(melody))):
            t = i / rate
            note = melody[min(len(melody) - 1, int(t / beat))]
            frequency = 440 * 2 ** ((note - 69) / 12)
            phase = (t % beat) / beat
            envelope = min(1, phase * 15) * (1 - phase) ** 2
            bass = 110 if int(t / (beat * 4)) % 2 == 0 else 130.8128
            sample = math.sin(math.tau * frequency * t) * envelope + 0.32 * math.sin(
                math.tau * bass * t
            )
            data.append(round(sample * 4200))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def scene(self, name):
        if not self.enabled or name == self.current_scene:
            return
        self.current_scene = name
        channel = pygame.mixer.Channel(0)
        channel.play(self.music[name], loops=-1, fade_ms=250)
        channel.set_volume(0 if self.muted else 0.26)

    def play(self, cue):
        if self.enabled and not self.muted and cue in self.effects:
            self.effects[cue].play()

    def toggle(self):
        self.muted = not self.muted
        if self.enabled:
            pygame.mixer.Channel(0).set_volume(0 if self.muted else 0.26)
            if self.muted:
                for i in range(1, pygame.mixer.get_num_channels()):
                    pygame.mixer.Channel(i).stop()
