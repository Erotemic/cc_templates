from __future__ import annotations

"""Battle moves. Start with the data moves, then try the function example below."""

from rpg_battle.api import (
    Move,
    MoveContext,
    add_status,
    change_stat,
    damage,
    heal,
    stat_change,
    status,
)

from student_game import audio, effects

# --- Declarative moves ---------------------------------------------------

strike = Move(
    "Strike",
    id="strike",
    kind="physical",
    power=9,
    animation=effects.slash,
    sound=audio.attack_basic,
)

shield_bash = Move(
    "Shield Bash",
    id="shield_bash",
    kind="physical",
    power=11,
    animation=effects.impact,
    sound=audio.shield_bash,
    effects=[
        status("stun", chance=0.2),
    ],
)

healing_light = Move(
    "Healing Light",
    id="healing_light",
    kind="heal",
    power=16,
    target="single_ally",
    animation=effects.heal,
    sound=audio.heal_chime,
)

thorn_bind = Move(
    "Thorn Bind",
    id="thorn_bind",
    kind="magical",
    power=8,
    animation=effects.thorn,
    sound=audio.thorn_bind,
    effects=[
        status("slow", turns=2, chance=0.8),
    ],
)

arc_bolt = Move(
    "Arc Bolt",
    id="arc_bolt",
    kind="magical",
    power=10,
    animation=effects.arc,
    sound=audio.arc_bolt,
)

ember = Move(
    "Ember",
    id="ember",
    kind="magical",
    power=10,
    animation=effects.ember,
    sound=audio.ember,
    effects=[
        status("burn", turns=2, chance=0.35),
    ],
)

wind_step = Move(
    "Wind Step",
    id="wind_step",
    kind="buff",
    target="self",
    animation=effects.wind,
    sound=audio.wind_step,
    effects=[
        stat_change("speed", 2),
    ],
)

stone_ward = Move(
    "Stone Ward",
    id="stone_ward",
    kind="buff",
    target="self",
    animation=effects.shield,
    sound=audio.stone_ward,
    effects=[
        status("guarded", turns=2),
        stat_change("defense", 2),
    ],
)

mist_veil = Move(
    "Mist Veil",
    id="mist_veil",
    kind="debuff",
    animation=effects.mist,
    sound=audio.mist_veil,
    effects=[
        status("slow", turns=2),
    ],
)

sine_wave = Move(
    "Sine Wave",
    id="sine_wave",
    kind="magical",
    power=12,
    animation=effects.sine_wave,
    sound=audio.sine_wave,
)

fourier_transform = Move(
    "Fourier Transform",
    id="fourier_transform",
    kind="magical",
    power=9,
    animation=effects.fourier_transform,
    sound=audio.sine_wave,
    effects=[
        status("transform:fourier", turns=0),
    ],
)

square_pulse = Move(
    "Square Pulse",
    id="square_pulse",
    kind="magical",
    power=10,
    target="all_enemies",
    animation=effects.square_pulse,
    sound=audio.square_pulse,
)

fractal_veil = Move(
    "Fractal Veil",
    id="fractal_veil",
    kind="status",
    target="all_allies",
    animation=effects.fractal,
    sound=audio.fractal_veil,
    effects=[
        status("focus", turns=3),
    ],
)

gradient_descent = Move(
    "Gradient Descent",
    id="gradient_descent",
    kind="magical",
    power=11,
    animation=effects.gradient_descent,
    sound=audio.gradient_descent,
    effects=[
        status("slow", turns=2, chance=0.35),
    ],
)

regularization = Move(
    "Regularization",
    id="regularization",
    kind="buff",
    target="self",
    animation=effects.regularization,
    sound=audio.regularization,
    effects=[
        status("guarded", turns=2),
        stat_change("defense", 1),
    ],
)

artifact_burst = Move(
    "Artifact Burst",
    id="artifact_burst",
    kind="magical",
    power=8,
    target="all_enemies",
    animation=effects.artifact_burst,
    sound=audio.artifact_burst,
    effects=[
        status("burn", turns=2, chance=0.2),
    ],
)

singularity_coil = Move(
    "Singularity Coil",
    id="singularity_coil",
    kind="magical",
    power=15,
    animation=effects.chaos_zigzag,
    sound=audio.arc_bolt,
)

pixel_storm = Move(
    "Pixel Storm",
    id="pixel_storm",
    kind="magical",
    power=10,
    target="all_enemies",
    animation=effects.pixel_storm,
    sound=audio.artifact_burst,
    effects=[
        status("burn", turns=2, chance=0.25),
    ],
)

entropy_shield = Move(
    "Entropy Shield",
    id="entropy_shield",
    kind="buff",
    target="self",
    animation=effects.entropy_shield,
    sound=audio.regularization,
    effects=[
        status("guarded", turns=2),
        status("focus", turns=2),
        stat_change("defense", 1),
    ],
)

# --- Programming extension ---------------------------------------------

# The engine gives this function read-only facts about the battle. The function
# returns commands; the engine still handles HP, events, animation, and knockouts.
def desperate_strike_logic(ctx: MoveContext):
    if ctx.user.hp_ratio < 0.5:
        return damage(18)
    return damage(8)

desperate_strike = Move(
    "Desperate Strike",
    id="desperate_strike",
    kind="physical",
    ai_power=8,  # estimate used only when the computer compares scripted moves
    animation=effects.impact,
    sound=audio.attack_basic,
    action=desperate_strike_logic,
)

MOVES = [
    strike,
    shield_bash,
    healing_light,
    thorn_bind,
    arc_bolt,
    ember,
    wind_step,
    stone_ward,
    mist_veil,
    sine_wave,
    fourier_transform,
    square_pulse,
    fractal_veil,
    gradient_descent,
    regularization,
    artifact_burst,
    singularity_coil,
    pixel_storm,
    entropy_shield,
    desperate_strike,
]
