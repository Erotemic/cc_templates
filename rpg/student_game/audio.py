from __future__ import annotations

"""Music and sound effects. Simple edits here are immediately audible."""

from rpg_battle.api import Music, Sound

# --- Music ---------------------------------------------------------------

soft_dungeon_crawl = Music.generated(
    "Soft Dungeon Crawl",
    builder="soft_dungeon_crawl",
    volume=0.2,
    id="soft_dungeon_crawl",
)

training_battle = Music.generated(
    "Training Battle",
    builder="battle_loop_prototype",
    volume=0.42,
    id="training_battle",
)

boss_battle_frenzy = Music.generated(
    "Boss Battle Frenzy",
    builder="boss_battle_frenzy",
    volume=0.34,
    id="boss_battle_frenzy",
)

bluesy_overhaul = Music.generated(
    "Bluesy Overhaul",
    builder="bluesy_overhaul",
    volume=0.22,
    id="bluesy_overhaul",
)

chill_exploration = Music.generated(
    "Chill Exploration",
    builder="chill_exploration",
    volume=0.21,
    id="chill_exploration",
)

d_minor_jam = Music.generated(
    "D Minor Jam",
    builder="d_minor_jam",
    volume=0.19,
    id="d_minor_jam",
)

victory_fanfare = Music.generated(
    "Victory Fanfare",
    builder="victory_fanfare",
    volume=0.24,
    id="victory_fanfare",
)

defeat_lament = Music.generated(
    "Defeat Lament",
    builder="defeat_lament",
    volume=0.22,
    id="defeat_lament",
)

MUSIC = [
    soft_dungeon_crawl,
    training_battle,
    boss_battle_frenzy,
    bluesy_overhaul,
    chill_exploration,
    d_minor_jam,
    victory_fanfare,
    defeat_lament,
]

# --- Sound effects -------------------------------------------------------

# Change waveform, frequency, duration, or noise and listen again.

menu_move = Sound(
    "Menu Move",
    waveform="square",
    frequency=740.0,
    duration=0.055,
    volume=0.16,
    release=0.03,
    frequency_end=810.0,
    id="menu_move",
)

menu_confirm = Sound(
    "Menu Confirm",
    waveform="square",
    frequency=510.0,
    duration=0.09,
    volume=0.2,
    release=0.045,
    frequency_end=680.0,
    id="menu_confirm",
)

menu_back = Sound(
    "Menu Back",
    waveform="triangle",
    duration=0.08,
    volume=0.18,
    release=0.04,
    frequency_end=330.0,
    id="menu_back",
)

attack_basic = Sound(
    "Attack Basic",
    waveform="square",
    frequency=170.0,
    duration=0.11,
    volume=0.26,
    release=0.045,
    frequency_end=110.0,
    noise=0.16,
    id="attack_basic",
)

attack_magic = Sound(
    "Attack Magic",
    frequency=330.0,
    duration=0.17,
    volume=0.22,
    release=0.06,
    frequency_end=520.0,
    vibrato_hz=8.0,
    vibrato_depth=0.02,
    id="attack_magic",
)

heal_chime = Sound(
    "Heal Chime",
    frequency=523.25,
    duration=0.22,
    volume=0.22,
    release=0.08,
    frequency_end=783.99,
    vibrato_hz=5.0,
    vibrato_depth=0.015,
    id="heal_chime",
)

shield_bash = Sound(
    "Shield Bash",
    waveform="square",
    frequency=140.0,
    duration=0.14,
    volume=0.28,
    release=0.06,
    frequency_end=90.0,
    noise=0.18,
    id="shield_bash",
)

thorn_bind = Sound(
    "Thorn Bind",
    waveform="saw",
    frequency=290.0,
    duration=0.16,
    volume=0.2,
    release=0.07,
    frequency_end=180.0,
    noise=0.1,
    id="thorn_bind",
)

arc_bolt = Sound(
    "Arc Bolt",
    waveform="triangle",
    frequency=370.0,
    duration=0.18,
    volume=0.2,
    release=0.06,
    frequency_end=610.0,
    vibrato_hz=11.0,
    vibrato_depth=0.025,
    id="arc_bolt",
)

ember = Sound(
    "Ember",
    waveform="square",
    frequency=230.0,
    duration=0.16,
    volume=0.23,
    release=0.06,
    frequency_end=120.0,
    noise=0.24,
    id="ember",
)

wind_step = Sound(
    "Wind Step",
    frequency=420.0,
    duration=0.15,
    volume=0.17,
    frequency_end=700.0,
    vibrato_hz=10.0,
    vibrato_depth=0.03,
    id="wind_step",
)

stone_ward = Sound(
    "Stone Ward",
    waveform="triangle",
    frequency=150.0,
    duration=0.18,
    volume=0.2,
    release=0.08,
    frequency_end=190.0,
    id="stone_ward",
)

mist_veil = Sound(
    "Mist Veil",
    frequency=300.0,
    duration=0.18,
    volume=0.16,
    release=0.08,
    frequency_end=250.0,
    noise=0.12,
    id="mist_veil",
)

sine_wave = Sound(
    "Sine Wave",
    frequency=260.0,
    duration=0.22,
    volume=0.2,
    release=0.08,
    frequency_end=480.0,
    vibrato_hz=7.0,
    vibrato_depth=0.05,
    id="sine_wave",
)

square_pulse = Sound(
    "Square Pulse",
    waveform="square",
    frequency=280.0,
    duration=0.18,
    volume=0.2,
    release=0.07,
    frequency_end=430.0,
    duty_cycle=0.35,
    id="square_pulse",
)

fractal_veil = Sound(
    "Fractal Veil",
    waveform="triangle",
    frequency=360.0,
    duration=0.24,
    volume=0.18,
    release=0.1,
    frequency_end=540.0,
    vibrato_hz=13.0,
    vibrato_depth=0.04,
    id="fractal_veil",
)

gradient_descent = Sound(
    "Gradient Descent",
    waveform="saw",
    duration=0.2,
    volume=0.22,
    release=0.08,
    frequency_end=170.0,
    id="gradient_descent",
)

regularization = Sound(
    "Regularization",
    waveform="triangle",
    frequency=190.0,
    duration=0.18,
    volume=0.2,
    release=0.08,
    frequency_end=240.0,
    id="regularization",
)

artifact_burst = Sound(
    "Artifact Burst",
    waveform="square",
    frequency=520.0,
    duration=0.18,
    volume=0.2,
    release=0.07,
    frequency_end=210.0,
    noise=0.28,
    id="artifact_burst",
)

switch = Sound(
    "Switch",
    waveform="triangle",
    frequency=300.0,
    volume=0.16,
    frequency_end=420.0,
    id="switch",
)

defend = Sound(
    "Defend",
    waveform="triangle",
    frequency=180.0,
    volume=0.15,
    frequency_end=220.0,
    id="defend",
)

ko = Sound(
    "Ko",
    waveform="square",
    frequency=170.0,
    duration=0.22,
    volume=0.2,
    release=0.12,
    frequency_end=70.0,
    noise=0.1,
    id="ko",
)

damage_tick = Sound(
    "Damage Tick",
    waveform="square",
    frequency=200.0,
    duration=0.09,
    volume=0.16,
    release=0.04,
    frequency_end=140.0,
    noise=0.12,
    id="damage_tick",
)

SOUNDS = [
    menu_move,
    menu_confirm,
    menu_back,
    attack_basic,
    attack_magic,
    heal_chime,
    shield_bash,
    thorn_bind,
    arc_bolt,
    ember,
    wind_step,
    stone_ward,
    mist_veil,
    sine_wave,
    square_pulse,
    fractal_veil,
    gradient_descent,
    regularization,
    artifact_burst,
    switch,
    defend,
    ko,
    damage_tick,
]
