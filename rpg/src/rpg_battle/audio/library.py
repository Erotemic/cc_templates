from __future__ import annotations

"""Audio specs and reusable rendering helpers.

This module is intentionally the small public surface for the rest of the game:
- content modules import the spec dataclasses from here
- the engine asks this module to render or cache generated tracks
- CLIs use the same helpers, so exported files and in-game audio match
"""

from array import array
from dataclasses import dataclass
from hashlib import sha256
import inspect
from pathlib import Path
import json
import math
import time
import wave

import numpy as np
from loguru import logger

from rpg_battle.audio.builder import MAX_I16, SAMPLE_RATE
from rpg_battle.audio.tracks import TRACK_BUILDERS


@dataclass(frozen=True)
class GeneratedTrackSpec:
    """A track synthesized from a registered :class:`TrackBuilder`."""

    builder: str
    volume: float = 0.4


@dataclass(frozen=True)
class FileTrackSpec:
    """A track backed by an audio file on disk."""

    path: str | Path
    volume: float = 0.5


@dataclass(frozen=True)
class SynthSoundSpec:
    """Small synthesized sound-effect recipe used by the battle engine."""

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
    """Render one synthesized sound effect to stereo int16 PCM."""

    start_time = time.perf_counter()
    sample_count = max(1, int(spec.duration * sample_rate))
    attack = int(spec.attack * sample_rate)
    release = int(spec.release * sample_rate)
    phase = 0.0
    data = array("h")
    rng = np.random.default_rng(1337)
    end_frequency = spec.frequency_end if spec.frequency_end is not None else spec.frequency
    logger.debug(
        "Rendering synth sound waveform={} duration={}s freq={}->{} samples={}",
        spec.waveform,
        spec.duration,
        spec.frequency,
        end_frequency,
        sample_count,
    )
    noise_values = None
    if spec.noise:
        noise_values = rng.uniform(-1.0, 1.0, sample_count)
    for index in range(sample_count):
        t = index / max(1, sample_count - 1)
        frequency = spec.frequency + (end_frequency - spec.frequency) * t
        if spec.vibrato_hz and spec.vibrato_depth:
            frequency *= (
                1.0
                + math.sin(math.tau * spec.vibrato_hz * (index / sample_rate)) * spec.vibrato_depth
            )
        phase += frequency / sample_rate
        sample = _sample_wave(phase, spec.waveform, spec.duty_cycle)
        if noise_values is not None:
            sample = sample * (1.0 - spec.noise) + float(noise_values[index]) * spec.noise
        sample *= _adsr(spec.volume, index, sample_count, attack, release)
        value = int(max(-1.0, min(1.0, sample)) * MAX_I16)
        data.append(value)
        data.append(value)
    logger.debug("Finished synth sound render in {:.3f}s", time.perf_counter() - start_time)
    return data


def render_generated_track(spec: GeneratedTrackSpec, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Render a generated music track through its registered builder."""

    builder_cls = TRACK_BUILDERS.get(spec.builder)
    if builder_cls is None:
        raise KeyError(f"Unknown generated track builder: {spec.builder}")
    start_time = time.perf_counter()
    logger.info(
        "Rendering generated track builder='{}' volume={} sample_rate={}",
        spec.builder,
        spec.volume,
        sample_rate,
    )
    builder = builder_cls(sample_rate=sample_rate, volume=spec.volume)
    pcm = builder.render()
    logger.info(
        "Rendered generated track '{}' in {:.3f}s ({} samples)",
        spec.builder,
        time.perf_counter() - start_time,
        len(pcm),
    )
    return pcm


def _safe_source_hash(obj: object) -> str:
    """Return a short hash of source text for cache invalidation.

    This makes generated-track caches robust when students tweak the builder
    implementation but forget to manually bump a cache version.
    """

    try:
        source = inspect.getsource(obj)
    except (OSError, TypeError):
        source = repr(obj)
    return sha256(source.encode("utf8")).hexdigest()[:16]


def get_track_cache_key(spec: GeneratedTrackSpec, sample_rate: int = SAMPLE_RATE) -> str:
    """Return a stable cache key for a generated track spec.

    The key intentionally includes builder source hashes so stale cached WAVs do
    not survive after students change track code.
    """

    builder_cls = TRACK_BUILDERS[spec.builder]
    payload = {
        "builder": spec.builder,
        "volume": spec.volume,
        "sample_rate": sample_rate,
        "builder_version": builder_cls.cache_version,
        "builder_source": _safe_source_hash(builder_cls),
        "builder_base_source": _safe_source_hash(builder_cls.__mro__[1]),
    }
    return sha256(json.dumps(payload, sort_keys=True).encode("utf8")).hexdigest()[:16]


def write_pcm_to_wav(
    output: Path,
    pcm: array | np.ndarray,
    *,
    channels: int = 2,
    sample_rate: int = SAMPLE_RATE,
) -> Path:
    """Write PCM data to a WAV file."""

    output.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(pcm, np.ndarray):
        data = pcm.astype(np.int16, copy=False).tobytes(order="C")
    else:
        data = pcm.tobytes()
    with wave.open(str(output), "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data)
    logger.debug("Wrote wav file to {}", output)
    return output
