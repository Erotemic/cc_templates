from __future__ import annotations

from pathlib import Path

import pygame
from loguru import logger

from rpg_battle.audio.library import (
    FileTrackSpec,
    GeneratedTrackSpec,
    render_battle_loop_prototype,
    render_soft_dungeon_crawl,
    render_synth_sound,
)
from rpg_battle.content.audio import DEFAULT_BATTLE_TRACK, MUSIC_TRACKS, SOUND_EFFECTS


class AudioEngine:
    """Small wrapper around pygame.mixer used by the classroom project."""

    def __init__(self) -> None:
        self.available = False
        self.initialized = False
        self._sound_cache: dict[str, pygame.mixer.Sound] = {}
        self._music_cache: dict[str, pygame.mixer.Sound] = {}
        self.current_music: str | None = None

    def initialize(self) -> None:
        """Initialize pygame's mixer once and remember whether audio is usable."""
        if self.initialized:
            return
        self.initialized = True
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.pre_init(44100, -16, 2, 512)
                pygame.mixer.init(44100, -16, 2, 512)
            self.available = pygame.mixer.get_init() is not None
            logger.info("Audio engine initialized: available={}", self.available)
        except pygame.error as exc:
            self.available = False
            logger.warning("Audio initialization failed: {}", exc)

    def play_default_music(self) -> None:
        """Play the default battle track from the content catalog."""
        self.play_music(DEFAULT_BATTLE_TRACK)

    def play_music(self, track_id: str, loops: int = -1) -> None:
        """Start background music by catalog id."""
        self.initialize()
        if not self.available:
            logger.debug("Skipping play_music because audio is unavailable")
            return
        if self.current_music == track_id:
            return
        sound = self._load_music(track_id)
        if sound is None:
            logger.warning("Could not load music track '{}'", track_id)
            return
        pygame.mixer.stop()
        sound.play(loops=loops)
        self.current_music = track_id
        logger.info("Playing music track '{}'", track_id)

    def stop_music(self) -> None:
        """Stop background music playback."""
        if self.available:
            pygame.mixer.stop()
        self.current_music = None

    def play_sfx(self, sound_id: str) -> None:
        """Play a synthesized sound effect by id."""
        self.initialize()
        if not self.available:
            return
        sound = self._load_sfx(sound_id)
        if sound is None:
            logger.debug("Missing sound effect '{}'", sound_id)
            return
        sound.play()

    def _load_music(self, track_id: str) -> pygame.mixer.Sound | None:
        if track_id in self._music_cache:
            return self._music_cache[track_id]
        spec = MUSIC_TRACKS.get(track_id)
        if spec is None:
            return None
        sound: pygame.mixer.Sound | None = None
        if isinstance(spec, GeneratedTrackSpec):
            if spec.builder == "battle_loop_prototype":
                buffer = render_battle_loop_prototype(volume=spec.volume)
                sound = pygame.mixer.Sound(buffer=buffer.tobytes())
            elif spec.builder == "soft_dungeon_crawl":
                buffer = render_soft_dungeon_crawl(volume=spec.volume)
                sound = pygame.mixer.Sound(buffer=buffer.tobytes())
        elif isinstance(spec, FileTrackSpec):
            path = Path(spec.path)
            if path.exists():
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(spec.volume)
        if sound is not None:
            self._music_cache[track_id] = sound
        return sound

    def _load_sfx(self, sound_id: str) -> pygame.mixer.Sound | None:
        if sound_id in self._sound_cache:
            return self._sound_cache[sound_id]
        spec = SOUND_EFFECTS.get(sound_id)
        if spec is None:
            return None
        buffer = render_synth_sound(spec)
        sound = pygame.mixer.Sound(buffer=buffer.tobytes())
        self._sound_cache[sound_id] = sound
        return sound
