"""Small original synthesized soundtrack/cues; pygame + standard library only."""

from array import array
import math
import os
from pathlib import Path
import sys
import pygame


class Audio:
    """Generate and play optional music/effects independently of the game rules.

    Channel 0 is reserved for looping music; other channels play cues. Disabled
    or unavailable audio leaves play/scene/toggle safe to call during the loop.
    """

    def __init__(self, enabled=True):
        """Try to open the mixer and synthesize sounds, unless enabled is False.

        Missing Linux audio endpoints skip initialization; pygame audio errors
        print a diagnostic and leave enabled False so gameplay can continue.
        """
        self.enabled = False
        self.muted = not enabled
        self.current_scene = None
        self.effects = {}
        self.music = {}
        self.note_sounds = {}
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
            self.music = {"WORLD": self.theme(False), "ENCOUNTER": self.theme(True)}
        except pygame.error as error:
            print(f"Audio unavailable; continuing silently: {error}")
            self.enabled = False

    @property
    def label(self):
        """Return a short HUD message describing audio availability and mute state."""
        if not self.enabled:
            return "Sound unavailable / off"
        return "M: sound off" if self.muted else "M: sound on"

    def tone(self, hz, duration):
        """Return a pygame Sound synthesized at hz for duration seconds.

        Build a fading 22,050 Hz mono signed-16-bit buffer in memory. The mixer
        must already be initialized; no sound file is read or written.
        """
        rate = 22050
        data = array("h")
        for i in range(int(rate * duration)):
            t = i / rate
            envelope = min(1, t / 0.008) * (1 - t / duration) ** 2
            sample = math.sin(2 * math.pi * hz * t) + 0.2 * math.sin(4 * math.pi * hz * t)
            data.append(round(6500 * envelope * sample))
        return pygame.mixer.Sound(buffer=data.tobytes())

    def theme(self, battle):
        """Return an original looping melody; battle chooses its faster tempo.

        Generate samples in memory using MIDI note numbers converted to Hz.
        This creates the sound but does not start playback.
        """
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
        """Loop the music named WORLD or BATTLE when the scene name changes.

        Leave the current track running on repeated calls. Respect mute and
        do nothing if audio is unavailable; name must be a registered music key.
        """
        if not self.enabled or name == self.current_scene:
            return
        self.current_scene = name
        channel = pygame.mixer.Channel(0)
        channel.play(self.music[name], loops=-1, fade_ms=250)
        channel.set_volume(0 if self.muted else 0.26)

    def play(self, cue):
        """Play a known cue on an effect channel when audio is available and unmuted."""
        if self.enabled and not self.muted and cue in self.effects:
            self.effects[cue].play()

    def play_tone(self, *, hz, duration=0.4):
        """Play a requested pitch with the same optional/muted behavior as sound cues.

        Synthesize on first use and reuse the buffer. Bound the cache for students
        experimenting with many frequencies. Channel 0 remains reserved for music.
        """
        if not self.enabled or self.muted:
            return
        key = (hz, duration)
        if key not in self.note_sounds:
            if len(self.note_sounds) >= 64:
                self.note_sounds.clear()
            self.note_sounds[key] = self.tone(hz=hz, duration=duration)
        self.note_sounds[key].play()

    def toggle(self):
        """Switch mute state, update music volume, and stop effects when muting."""
        self.muted = not self.muted
        if self.enabled:
            pygame.mixer.Channel(0).set_volume(0 if self.muted else 0.26)
            if self.muted:
                for i in range(1, pygame.mixer.get_num_channels()):
                    pygame.mixer.Channel(i).stop()
