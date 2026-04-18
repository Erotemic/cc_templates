from __future__ import annotations

"""High-level audio engine for music and sound effects.

The debug logs in this module are intentionally "architectural" rather than
per-frame so students can trace the flow from content ids -> caches -> rendered
PCM -> pygame playback.
"""

from pathlib import Path
import time

import pygame
from loguru import logger

from rpg_battle.audio.library import (
    FileTrackSpec,
    GeneratedTrackSpec,
    get_track_cache_key,
    render_generated_track,
    render_synth_sound,
    write_pcm_to_wav,
)
from rpg_battle.content.audio import DEFAULT_BATTLE_TRACK, MUSIC_TRACKS, SOUND_EFFECTS


class AudioEngine:
    """Small wrapper around ``pygame.mixer`` used by the classroom project."""

    def __init__(self) -> None:
        self.available = False
        self.initialized = False
        self._sound_cache: dict[str, pygame.mixer.Sound] = {}
        self._music_cache: dict[str, pygame.mixer.Sound] = {}
        self.current_music: str | None = None
        self.cache_dir = Path.home() / ".cache" / "rpg_battle" / "audio"

    def initialize(self) -> None:
        """Initialize the mixer once and remember whether audio is usable."""

        if self.initialized:
            logger.debug("Audio initialize() called again; mixer already initialized")
            return
        self.initialized = True
        logger.info("Initializing audio engine")
        start_time = time.perf_counter()
        try:
            if pygame.mixer.get_init() is None:
                logger.debug("pygame.mixer not ready; calling pre_init() and init()")
                pygame.mixer.pre_init(44100, -16, 2, 512)
                pygame.mixer.init(44100, -16, 2, 512)
            self.available = pygame.mixer.get_init() is not None
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(
                "Audio engine initialized: available={} elapsed={:.3f}s cache_dir={}",
                self.available,
                time.perf_counter() - start_time,
                self.cache_dir,
            )
        except pygame.error as exc:
            self.available = False
            logger.warning(
                "Audio initialization failed after {:.3f}s: {}",
                time.perf_counter() - start_time,
                exc,
            )

    def play_default_music(self) -> None:
        """Play the default battle track from the content catalog."""

        logger.debug("Request to play default music track '{}'", DEFAULT_BATTLE_TRACK)
        self.play_music(DEFAULT_BATTLE_TRACK)

    def play_music(self, track_id: str, loops: int = -1) -> None:
        """Start background music by catalog id."""

        self.initialize()
        if not self.available:
            logger.debug("Skipping play_music('{}') because audio is unavailable", track_id)
            return
        if self.current_music == track_id:
            logger.debug("Music '{}' is already playing", track_id)
            return
        logger.info("Preparing music track '{}'", track_id)
        start_time = time.perf_counter()
        sound = self._load_music(track_id)
        if sound is None:
            logger.warning("Could not load music track '{}'", track_id)
            return
        pygame.mixer.stop()
        sound.play(loops=loops)
        self.current_music = track_id
        logger.info(
            "Playing music track '{}' with loops={} (ready in {:.3f}s)",
            track_id,
            loops,
            time.perf_counter() - start_time,
        )

    def stop_music(self) -> None:
        """Stop background music playback."""

        if self.available:
            logger.debug("Stopping current music '{}'", self.current_music)
            pygame.mixer.stop()
        self.current_music = None

    def play_sfx(self, sound_id: str) -> None:
        """Play a synthesized sound effect by id."""

        self.initialize()
        if not self.available:
            logger.debug("Skipping play_sfx('{}') because audio is unavailable", sound_id)
            return
        sound = self._load_sfx(sound_id)
        if sound is None:
            logger.debug("Missing sound effect '{}'", sound_id)
            return
        sound.play()
        logger.debug("Played sound effect '{}'", sound_id)

    def _generated_cache_path(self, track_id: str, spec: GeneratedTrackSpec) -> Path:
        cache_key = get_track_cache_key(spec)
        return self.cache_dir / f"{track_id}_{cache_key}.wav"

    def _load_music(self, track_id: str) -> pygame.mixer.Sound | None:
        if track_id in self._music_cache:
            logger.debug("Music cache hit (memory) for '{}'", track_id)
            return self._music_cache[track_id]
        spec = MUSIC_TRACKS.get(track_id)
        if spec is None:
            logger.warning("Unknown music track id '{}'", track_id)
            return None
        sound: pygame.mixer.Sound | None = None
        if isinstance(spec, GeneratedTrackSpec):
            cache_path = self._generated_cache_path(track_id, spec)
            if cache_path.exists():
                logger.debug("Music cache hit (disk) for '{}' at {}", track_id, cache_path)
                sound = pygame.mixer.Sound(str(cache_path))
            else:
                logger.info(
                    "Music cache miss for '{}'; rendering builder='{}' volume={}",
                    track_id,
                    spec.builder,
                    spec.volume,
                )
                render_start = time.perf_counter()
                pcm = render_generated_track(spec)
                logger.debug(
                    "Generated PCM for '{}' in {:.3f}s; writing cache file",
                    track_id,
                    time.perf_counter() - render_start,
                )
                write_pcm_to_wav(cache_path, pcm)
                sound = pygame.mixer.Sound(str(cache_path))
        elif isinstance(spec, FileTrackSpec):
            path = Path(spec.path)
            logger.debug("Loading file-backed music '{}' from {}", track_id, path)
            if path.exists():
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(spec.volume)
            else:
                logger.warning("Music file for '{}' does not exist: {}", track_id, path)
        if sound is not None:
            self._music_cache[track_id] = sound
            logger.debug("Cached music '{}' in memory", track_id)
        return sound

    def _load_sfx(self, sound_id: str) -> pygame.mixer.Sound | None:
        if sound_id in self._sound_cache:
            logger.debug("SFX cache hit for '{}'", sound_id)
            return self._sound_cache[sound_id]
        spec = SOUND_EFFECTS.get(sound_id)
        if spec is None:
            logger.warning("Unknown sound effect id '{}'", sound_id)
            return None
        logger.debug("Synthesizing sound effect '{}': {}", sound_id, spec)
        start_time = time.perf_counter()
        buffer = render_synth_sound(spec)
        sound = pygame.mixer.Sound(buffer=buffer.tobytes())
        self._sound_cache[sound_id] = sound
        logger.debug(
            "Cached sound effect '{}' after {:.3f}s", sound_id, time.perf_counter() - start_time
        )
        return sound
