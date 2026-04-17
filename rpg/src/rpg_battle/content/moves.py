from __future__ import annotations

"""Student-friendly move catalog.

Each move uses keyword arguments so students can more easily see what each field
means without memorizing dataclass argument order.
"""

from rpg_battle.core.models import MoveEffect, MoveSpec

MOVES = {
    "strike": MoveSpec(
        move_id="strike",
        name="Strike",
        kind="physical",
        power=10,
        target_mode="single_enemy",
        animation="impact",
        sound_id="attack_basic",
        flavor="A reliable close-range hit.",
    ),
    "shield_bash": MoveSpec(
        move_id="shield_bash",
        name="Shield Bash",
        kind="physical",
        power=11,
        target_mode="single_enemy",
        animation="impact",
        sound_id="shield_bash",
        effects=(
            MoveEffect(
                status="stun",
                chance=0.25,
                duration=1,
            ),
        ),
    ),
    "healing_light": MoveSpec(
        move_id="healing_light",
        name="Healing Light",
        kind="heal",
        power=10,
        target_mode="single_ally",
        animation="heal_pulse",
        sound_id="heal_chime",
    ),
    "thorn_bind": MoveSpec(
        move_id="thorn_bind",
        name="Thorn Bind",
        kind="magical",
        power=9,
        target_mode="single_enemy",
        animation="vine",
        sound_id="thorn_bind",
        effects=(
            MoveEffect(
                status="slow",
                chance=0.65,
                duration=2,
            ),
        ),
    ),
    "arc_bolt": MoveSpec(
        move_id="arc_bolt",
        name="Arc Bolt",
        kind="magical",
        power=12,
        target_mode="single_enemy",
        animation="bolt",
        sound_id="arc_bolt",
    ),
    "ember": MoveSpec(
        move_id="ember",
        name="Ember",
        kind="magical",
        power=10,
        target_mode="single_enemy",
        animation="ember",
        sound_id="ember",
        effects=(
            MoveEffect(
                status="burn",
                chance=0.35,
                duration=3,
            ),
        ),
    ),
    "wind_step": MoveSpec(
        move_id="wind_step",
        name="Wind Step",
        kind="buff",
        target_mode="self",
        animation="wind",
        sound_id="wind_step",
        effects=(
            MoveEffect(
                stat="speed",
                stages=2,
            ),
        ),
    ),
    "stone_ward": MoveSpec(
        move_id="stone_ward",
        name="Stone Ward",
        kind="buff",
        target_mode="single_ally",
        animation="shield",
        sound_id="stone_ward",
        effects=(
            MoveEffect(
                status="guarded",
                duration=2,
            ),
            MoveEffect(
                stat="defense",
                stages=2,
            ),
        ),
    ),
    "mist_veil": MoveSpec(
        move_id="mist_veil",
        name="Mist Veil",
        kind="debuff",
        target_mode="single_enemy",
        animation="mist",
        sound_id="mist_veil",
        effects=(
            MoveEffect(
                status="slow",
                chance=1.0,
                duration=2,
            ),
        ),
    ),
    "sine_wave": MoveSpec(
        move_id="sine_wave",
        name="Sine Wave",
        kind="magical",
        power=12,
        target_mode="single_enemy",
        animation="sine_wave",
        sound_id="sine_wave",
    ),
    "square_pulse": MoveSpec(
        move_id="square_pulse",
        name="Square Pulse",
        kind="magical",
        power=10,
        target_mode="all_enemies",
        animation="square_pulse",
        sound_id="square_pulse",
    ),
    "fractal_veil": MoveSpec(
        move_id="fractal_veil",
        name="Fractal Veil",
        kind="status",
        target_mode="all_allies",
        animation="fractal",
        sound_id="fractal_veil",
        effects=(
            MoveEffect(
                status="focus",
                duration=3,
            ),
        ),
    ),
    "gradient_descent": MoveSpec(
        move_id="gradient_descent",
        name="Gradient Descent",
        kind="magical",
        power=11,
        target_mode="single_enemy",
        animation="gradient_descent",
        sound_id="gradient_descent",
        effects=(
            MoveEffect(
                status="slow",
                chance=0.35,
                duration=2,
            ),
        ),
    ),
    "regularization": MoveSpec(
        move_id="regularization",
        name="Regularization",
        kind="buff",
        target_mode="self",
        animation="regularization",
        sound_id="regularization",
        effects=(
            MoveEffect(
                status="guarded",
                duration=2,
            ),
            MoveEffect(
                stat="defense",
                stages=1,
            ),
        ),
    ),
    "artifact_burst": MoveSpec(
        move_id="artifact_burst",
        name="Artifact Burst",
        kind="magical",
        power=8,
        target_mode="all_enemies",
        animation="artifact_burst",
        sound_id="artifact_burst",
        effects=(
            MoveEffect(
                status="burn",
                chance=0.2,
                duration=2,
            ),
        ),
    ),
}
