from __future__ import annotations

"""Student-facing audio catalog.

Tracks and sound effects are built from empty dictionaries so students can add a
new field, listen, then keep iterating.
"""

from pathlib import Path

from rpg_battle.audio.library import GeneratedTrackSpec, SynthSoundSpec

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
AUDIO_ASSET_DIR = PACKAGE_ROOT / "assets" / "audio"

DEFAULT_BATTLE_TRACK = "bluesy_overhaul"
DEFAULT_VICTORY_TRACK = "victory_fanfare"
DEFAULT_DEFEAT_TRACK = "defeat_lament"

MUSIC_TRACKS: dict[str, GeneratedTrackSpec] = {}

soft_dungeon_crawl: dict[str, object] = {}
soft_dungeon_crawl["builder"] = "soft_dungeon_crawl"
soft_dungeon_crawl["volume"] = 0.20
MUSIC_TRACKS["soft_dungeon_crawl"] = GeneratedTrackSpec(**soft_dungeon_crawl)

training_battle: dict[str, object] = {}
training_battle["builder"] = "battle_loop_prototype"
training_battle["volume"] = 0.42
MUSIC_TRACKS["training_battle"] = GeneratedTrackSpec(**training_battle)

boss_battle_frenzy: dict[str, object] = {}
boss_battle_frenzy["builder"] = "boss_battle_frenzy"
boss_battle_frenzy["volume"] = 0.34
MUSIC_TRACKS["boss_battle_frenzy"] = GeneratedTrackSpec(**boss_battle_frenzy)

bluesy_overhaul: dict[str, object] = {}
bluesy_overhaul["builder"] = "bluesy_overhaul"
bluesy_overhaul["volume"] = 0.22
MUSIC_TRACKS["bluesy_overhaul"] = GeneratedTrackSpec(**bluesy_overhaul)

chill_exploration: dict[str, object] = {}
chill_exploration["builder"] = "chill_exploration"
chill_exploration["volume"] = 0.21
MUSIC_TRACKS["chill_exploration"] = GeneratedTrackSpec(**chill_exploration)


d_minor_jam: dict[str, object] = {}
d_minor_jam["builder"] = "d_minor_jam"
d_minor_jam["volume"] = 0.19
MUSIC_TRACKS["d_minor_jam"] = GeneratedTrackSpec(**d_minor_jam)


victory_fanfare: dict[str, object] = {}
victory_fanfare["builder"] = "victory_fanfare"
victory_fanfare["volume"] = 0.24
MUSIC_TRACKS["victory_fanfare"] = GeneratedTrackSpec(**victory_fanfare)

defeat_lament: dict[str, object] = {}
defeat_lament["builder"] = "defeat_lament"
defeat_lament["volume"] = 0.22
MUSIC_TRACKS["defeat_lament"] = GeneratedTrackSpec(**defeat_lament)


SOUND_EFFECTS: dict[str, SynthSoundSpec] = {}


def add_sound(sound_id: str, **kwargs: object) -> None:
    """Register one synthesized sound effect in a readable incremental style."""

    SOUND_EFFECTS[sound_id] = SynthSoundSpec(**kwargs)


add_sound(
    "menu_move",
    waveform="square",
    frequency=740.0,
    frequency_end=810.0,
    duration=0.055,
    volume=0.16,
    release=0.03,
)
add_sound(
    "menu_confirm",
    waveform="square",
    frequency=510.0,
    frequency_end=680.0,
    duration=0.09,
    volume=0.2,
    release=0.045,
)
add_sound(
    "menu_back",
    waveform="triangle",
    frequency=440.0,
    frequency_end=330.0,
    duration=0.08,
    volume=0.18,
    release=0.04,
)
add_sound(
    "attack_basic",
    waveform="square",
    frequency=170.0,
    frequency_end=110.0,
    duration=0.11,
    volume=0.26,
    noise=0.16,
    release=0.045,
)
add_sound(
    "attack_magic",
    waveform="sine",
    frequency=330.0,
    frequency_end=520.0,
    duration=0.17,
    volume=0.22,
    vibrato_hz=8.0,
    vibrato_depth=0.02,
    release=0.06,
)
add_sound(
    "heal_chime",
    waveform="sine",
    frequency=523.25,
    frequency_end=783.99,
    duration=0.22,
    volume=0.22,
    vibrato_hz=5.0,
    vibrato_depth=0.015,
    release=0.08,
)
add_sound(
    "shield_bash",
    waveform="square",
    frequency=140.0,
    frequency_end=90.0,
    duration=0.14,
    volume=0.28,
    noise=0.18,
    release=0.06,
)
add_sound(
    "thorn_bind",
    waveform="saw",
    frequency=290.0,
    frequency_end=180.0,
    duration=0.16,
    volume=0.2,
    noise=0.1,
    release=0.07,
)
add_sound(
    "arc_bolt",
    waveform="triangle",
    frequency=370.0,
    frequency_end=610.0,
    duration=0.18,
    volume=0.2,
    vibrato_hz=11.0,
    vibrato_depth=0.025,
    release=0.06,
)
add_sound(
    "ember",
    waveform="square",
    frequency=230.0,
    frequency_end=120.0,
    duration=0.16,
    volume=0.23,
    noise=0.24,
    release=0.06,
)
add_sound(
    "wind_step",
    waveform="sine",
    frequency=420.0,
    frequency_end=700.0,
    duration=0.15,
    volume=0.17,
    vibrato_hz=10.0,
    vibrato_depth=0.03,
    release=0.05,
)
add_sound(
    "stone_ward",
    waveform="triangle",
    frequency=150.0,
    frequency_end=190.0,
    duration=0.18,
    volume=0.2,
    release=0.08,
)
add_sound(
    "mist_veil",
    waveform="sine",
    frequency=300.0,
    frequency_end=250.0,
    duration=0.18,
    volume=0.16,
    noise=0.12,
    release=0.08,
)
add_sound(
    "sine_wave",
    waveform="sine",
    frequency=260.0,
    frequency_end=480.0,
    duration=0.22,
    volume=0.2,
    vibrato_hz=7.0,
    vibrato_depth=0.05,
    release=0.08,
)
add_sound(
    "square_pulse",
    waveform="square",
    frequency=280.0,
    frequency_end=430.0,
    duration=0.18,
    volume=0.2,
    duty_cycle=0.35,
    release=0.07,
)
add_sound(
    "fractal_veil",
    waveform="triangle",
    frequency=360.0,
    frequency_end=540.0,
    duration=0.24,
    volume=0.18,
    vibrato_hz=13.0,
    vibrato_depth=0.04,
    release=0.1,
)
add_sound(
    "gradient_descent",
    waveform="saw",
    frequency=440.0,
    frequency_end=170.0,
    duration=0.2,
    volume=0.22,
    release=0.08,
)
add_sound(
    "regularization",
    waveform="triangle",
    frequency=190.0,
    frequency_end=240.0,
    duration=0.18,
    volume=0.2,
    release=0.08,
)
add_sound(
    "artifact_burst",
    waveform="square",
    frequency=520.0,
    frequency_end=210.0,
    duration=0.18,
    volume=0.2,
    noise=0.28,
    release=0.07,
)
add_sound(
    "switch",
    waveform="triangle",
    frequency=300.0,
    frequency_end=420.0,
    duration=0.12,
    volume=0.16,
    release=0.05,
)
add_sound(
    "defend",
    waveform="triangle",
    frequency=180.0,
    frequency_end=220.0,
    duration=0.12,
    volume=0.15,
    release=0.05,
)
add_sound(
    "ko",
    waveform="square",
    frequency=170.0,
    frequency_end=70.0,
    duration=0.22,
    volume=0.2,
    noise=0.1,
    release=0.12,
)
add_sound(
    "damage_tick",
    waveform="square",
    frequency=200.0,
    frequency_end=140.0,
    duration=0.09,
    volume=0.16,
    noise=0.12,
    release=0.04,
)
