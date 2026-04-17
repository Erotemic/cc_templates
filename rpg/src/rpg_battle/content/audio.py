from __future__ import annotations

"""Student-facing audio catalog.

Swap the default battle music by changing ``DEFAULT_BATTLE_TRACK`` to another key
from ``MUSIC_TRACKS``. Each move in ``content.moves`` also points at a sound id
from ``SOUND_EFFECTS``. The incremental style here mirrors the rest of
``content/`` so students can add one sound or one track at a time.
"""

from pathlib import Path

from rpg_battle.audio.library import GeneratedTrackSpec, SynthSoundSpec

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
AUDIO_ASSET_DIR = PACKAGE_ROOT / "assets" / "audio"

DEFAULT_BATTLE_TRACK = "soft_dungeon_crawl"

MUSIC_TRACKS: dict[str, GeneratedTrackSpec] = {}
MUSIC_TRACKS["soft_dungeon_crawl"] = GeneratedTrackSpec(builder="soft_dungeon_crawl", volume=0.20)
MUSIC_TRACKS["training_battle"] = GeneratedTrackSpec(builder="battle_loop_prototype", volume=0.42)

SOUND_EFFECTS: dict[str, SynthSoundSpec] = {}
SOUND_EFFECTS["menu_move"] = SynthSoundSpec(
    waveform="square",
    frequency=740.0,
    frequency_end=810.0,
    duration=0.055,
    volume=0.16,
    release=0.03,
)
SOUND_EFFECTS["menu_confirm"] = SynthSoundSpec(
    waveform="square",
    frequency=510.0,
    frequency_end=680.0,
    duration=0.09,
    volume=0.2,
    release=0.045,
)
SOUND_EFFECTS["menu_back"] = SynthSoundSpec(
    waveform="triangle",
    frequency=440.0,
    frequency_end=330.0,
    duration=0.08,
    volume=0.18,
    release=0.04,
)
SOUND_EFFECTS["attack_basic"] = SynthSoundSpec(
    waveform="square",
    frequency=170.0,
    frequency_end=110.0,
    duration=0.11,
    volume=0.26,
    noise=0.16,
    release=0.045,
)
SOUND_EFFECTS["attack_magic"] = SynthSoundSpec(
    waveform="sine",
    frequency=330.0,
    frequency_end=520.0,
    duration=0.17,
    volume=0.22,
    vibrato_hz=8.0,
    vibrato_depth=0.02,
    release=0.06,
)
SOUND_EFFECTS["heal_chime"] = SynthSoundSpec(
    waveform="sine",
    frequency=523.25,
    frequency_end=783.99,
    duration=0.22,
    volume=0.22,
    vibrato_hz=5.0,
    vibrato_depth=0.015,
    release=0.08,
)
SOUND_EFFECTS["shield_bash"] = SynthSoundSpec(
    waveform="square",
    frequency=140.0,
    frequency_end=90.0,
    duration=0.14,
    volume=0.28,
    noise=0.18,
    release=0.06,
)
SOUND_EFFECTS["thorn_bind"] = SynthSoundSpec(
    waveform="saw",
    frequency=290.0,
    frequency_end=180.0,
    duration=0.16,
    volume=0.2,
    noise=0.1,
    release=0.07,
)
SOUND_EFFECTS["arc_bolt"] = SynthSoundSpec(
    waveform="triangle",
    frequency=370.0,
    frequency_end=610.0,
    duration=0.18,
    volume=0.2,
    vibrato_hz=11.0,
    vibrato_depth=0.025,
    release=0.06,
)
SOUND_EFFECTS["ember"] = SynthSoundSpec(
    waveform="square",
    frequency=230.0,
    frequency_end=120.0,
    duration=0.16,
    volume=0.23,
    noise=0.24,
    release=0.06,
)
SOUND_EFFECTS["wind_step"] = SynthSoundSpec(
    waveform="sine",
    frequency=420.0,
    frequency_end=700.0,
    duration=0.15,
    volume=0.17,
    vibrato_hz=10.0,
    vibrato_depth=0.03,
    release=0.05,
)
SOUND_EFFECTS["stone_ward"] = SynthSoundSpec(
    waveform="triangle",
    frequency=150.0,
    frequency_end=190.0,
    duration=0.18,
    volume=0.2,
    release=0.08,
)
SOUND_EFFECTS["mist_veil"] = SynthSoundSpec(
    waveform="sine",
    frequency=300.0,
    frequency_end=250.0,
    duration=0.18,
    volume=0.16,
    noise=0.12,
    release=0.08,
)
SOUND_EFFECTS["sine_wave"] = SynthSoundSpec(
    waveform="sine",
    frequency=260.0,
    frequency_end=480.0,
    duration=0.22,
    volume=0.2,
    vibrato_hz=7.0,
    vibrato_depth=0.05,
    release=0.08,
)
SOUND_EFFECTS["square_pulse"] = SynthSoundSpec(
    waveform="square",
    frequency=280.0,
    frequency_end=430.0,
    duration=0.18,
    volume=0.2,
    duty_cycle=0.35,
    release=0.07,
)
SOUND_EFFECTS["fractal_veil"] = SynthSoundSpec(
    waveform="triangle",
    frequency=360.0,
    frequency_end=540.0,
    duration=0.24,
    volume=0.18,
    vibrato_hz=13.0,
    vibrato_depth=0.04,
    release=0.1,
)
SOUND_EFFECTS["gradient_descent"] = SynthSoundSpec(
    waveform="saw", frequency=440.0, frequency_end=170.0, duration=0.2, volume=0.22, release=0.08
)
SOUND_EFFECTS["regularization"] = SynthSoundSpec(
    waveform="triangle",
    frequency=190.0,
    frequency_end=240.0,
    duration=0.18,
    volume=0.2,
    release=0.08,
)
SOUND_EFFECTS["artifact_burst"] = SynthSoundSpec(
    waveform="square",
    frequency=520.0,
    frequency_end=210.0,
    duration=0.18,
    volume=0.2,
    noise=0.28,
    release=0.07,
)
SOUND_EFFECTS["switch"] = SynthSoundSpec(
    waveform="triangle",
    frequency=300.0,
    frequency_end=420.0,
    duration=0.12,
    volume=0.16,
    release=0.05,
)
SOUND_EFFECTS["defend"] = SynthSoundSpec(
    waveform="triangle",
    frequency=180.0,
    frequency_end=220.0,
    duration=0.12,
    volume=0.15,
    release=0.05,
)
SOUND_EFFECTS["ko"] = SynthSoundSpec(
    waveform="square",
    frequency=170.0,
    frequency_end=70.0,
    duration=0.22,
    volume=0.2,
    noise=0.1,
    release=0.12,
)
SOUND_EFFECTS["damage_tick"] = SynthSoundSpec(
    waveform="square",
    frequency=200.0,
    frequency_end=140.0,
    duration=0.09,
    volume=0.16,
    noise=0.12,
    release=0.04,
)
