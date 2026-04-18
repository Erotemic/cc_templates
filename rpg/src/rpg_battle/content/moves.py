from __future__ import annotations

"""Move catalog for the classroom battle project.

Moves are built from empty dictionaries so students can add one field at a time,
then register the completed move into ``MOVES``.
"""

from rpg_battle.core.models import MoveEffect, MoveSpec

MOVES: dict[str, MoveSpec] = {}

strike: dict[str, object] = {}
strike["move_id"] = "strike"
strike["name"] = "Strike"
strike["kind"] = "physical"
strike["power"] = 9
strike["target_mode"] = "single_enemy"
strike["animation"] = "slash"
strike["sound_id"] = "attack_basic"
MOVES["strike"] = MoveSpec(**strike)

shield_bash: dict[str, object] = {}
shield_bash["move_id"] = "shield_bash"
shield_bash["name"] = "Shield Bash"
shield_bash["kind"] = "physical"
shield_bash["power"] = 11
shield_bash["target_mode"] = "single_enemy"
shield_bash["animation"] = "impact"
shield_bash["sound_id"] = "shield_bash"
shield_bash["effects"] = (MoveEffect(status="stun", chance=0.20, duration=1),)
MOVES["shield_bash"] = MoveSpec(**shield_bash)

healing_light: dict[str, object] = {}
healing_light["move_id"] = "healing_light"
healing_light["name"] = "Healing Light"
healing_light["kind"] = "heal"
healing_light["power"] = 16
healing_light["target_mode"] = "single_ally"
healing_light["animation"] = "heal"
healing_light["sound_id"] = "heal_chime"
MOVES["healing_light"] = MoveSpec(**healing_light)

thorn_bind: dict[str, object] = {}
thorn_bind["move_id"] = "thorn_bind"
thorn_bind["name"] = "Thorn Bind"
thorn_bind["kind"] = "magical"
thorn_bind["power"] = 8
thorn_bind["target_mode"] = "single_enemy"
thorn_bind["animation"] = "thorn"
thorn_bind["sound_id"] = "thorn_bind"
thorn_bind["effects"] = (MoveEffect(status="slow", chance=0.80, duration=2),)
MOVES["thorn_bind"] = MoveSpec(**thorn_bind)

arc_bolt: dict[str, object] = {}
arc_bolt["move_id"] = "arc_bolt"
arc_bolt["name"] = "Arc Bolt"
arc_bolt["kind"] = "magical"
arc_bolt["power"] = 10
arc_bolt["target_mode"] = "single_enemy"
arc_bolt["animation"] = "arc"
arc_bolt["sound_id"] = "arc_bolt"
MOVES["arc_bolt"] = MoveSpec(**arc_bolt)

ember: dict[str, object] = {}
ember["move_id"] = "ember"
ember["name"] = "Ember"
ember["kind"] = "magical"
ember["power"] = 10
ember["target_mode"] = "single_enemy"
ember["animation"] = "ember"
ember["sound_id"] = "ember"
ember["effects"] = (MoveEffect(status="burn", chance=0.35, duration=2),)
MOVES["ember"] = MoveSpec(**ember)

wind_step: dict[str, object] = {}
wind_step["move_id"] = "wind_step"
wind_step["name"] = "Wind Step"
wind_step["kind"] = "buff"
wind_step["target_mode"] = "self"
wind_step["animation"] = "wind"
wind_step["sound_id"] = "wind_step"
wind_step["effects"] = (MoveEffect(stat="speed", stages=2),)
MOVES["wind_step"] = MoveSpec(**wind_step)

stone_ward: dict[str, object] = {}
stone_ward["move_id"] = "stone_ward"
stone_ward["name"] = "Stone Ward"
stone_ward["kind"] = "buff"
stone_ward["target_mode"] = "self"
stone_ward["animation"] = "shield"
stone_ward["sound_id"] = "stone_ward"
stone_ward["effects"] = (
    MoveEffect(status="guarded", duration=2),
    MoveEffect(stat="defense", stages=2),
)
MOVES["stone_ward"] = MoveSpec(**stone_ward)

mist_veil: dict[str, object] = {}
mist_veil["move_id"] = "mist_veil"
mist_veil["name"] = "Mist Veil"
mist_veil["kind"] = "debuff"
mist_veil["target_mode"] = "single_enemy"
mist_veil["animation"] = "mist"
mist_veil["sound_id"] = "mist_veil"
mist_veil["effects"] = (MoveEffect(status="slow", chance=1.0, duration=2),)
MOVES["mist_veil"] = MoveSpec(**mist_veil)

sine_wave: dict[str, object] = {}
sine_wave["move_id"] = "sine_wave"
sine_wave["name"] = "Sine Wave"
sine_wave["kind"] = "magical"
sine_wave["power"] = 12
sine_wave["target_mode"] = "single_enemy"
sine_wave["animation"] = "sine_wave"
sine_wave["sound_id"] = "sine_wave"
MOVES["sine_wave"] = MoveSpec(**sine_wave)

fourier_transform: dict[str, object] = {}
fourier_transform["move_id"] = "fourier_transform"
fourier_transform["name"] = "Fourier Transform"
fourier_transform["kind"] = "magical"
fourier_transform["power"] = 9
fourier_transform["target_mode"] = "single_enemy"
fourier_transform["animation"] = "fourier_transform"
fourier_transform["sound_id"] = "sine_wave"
fourier_transform["effects"] = (MoveEffect(status="transform:fourier"),)
MOVES["fourier_transform"] = MoveSpec(**fourier_transform)

square_pulse: dict[str, object] = {}
square_pulse["move_id"] = "square_pulse"
square_pulse["name"] = "Square Pulse"
square_pulse["kind"] = "magical"
square_pulse["power"] = 10
square_pulse["target_mode"] = "all_enemies"
square_pulse["animation"] = "square_pulse"
square_pulse["sound_id"] = "square_pulse"
MOVES["square_pulse"] = MoveSpec(**square_pulse)

fractal_veil: dict[str, object] = {}
fractal_veil["move_id"] = "fractal_veil"
fractal_veil["name"] = "Fractal Veil"
fractal_veil["kind"] = "status"
fractal_veil["target_mode"] = "all_allies"
fractal_veil["animation"] = "fractal"
fractal_veil["sound_id"] = "fractal_veil"
fractal_veil["effects"] = (MoveEffect(status="focus", duration=3),)
MOVES["fractal_veil"] = MoveSpec(**fractal_veil)

gradient_descent: dict[str, object] = {}
gradient_descent["move_id"] = "gradient_descent"
gradient_descent["name"] = "Gradient Descent"
gradient_descent["kind"] = "magical"
gradient_descent["power"] = 11
gradient_descent["target_mode"] = "single_enemy"
gradient_descent["animation"] = "gradient_descent"
gradient_descent["sound_id"] = "gradient_descent"
gradient_descent["effects"] = (MoveEffect(status="slow", chance=0.35, duration=2),)
MOVES["gradient_descent"] = MoveSpec(**gradient_descent)

regularization: dict[str, object] = {}
regularization["move_id"] = "regularization"
regularization["name"] = "Regularization"
regularization["kind"] = "buff"
regularization["target_mode"] = "self"
regularization["animation"] = "regularization"
regularization["sound_id"] = "regularization"
regularization["effects"] = (
    MoveEffect(status="guarded", duration=2),
    MoveEffect(stat="defense", stages=1),
)
MOVES["regularization"] = MoveSpec(**regularization)

artifact_burst: dict[str, object] = {}
artifact_burst["move_id"] = "artifact_burst"
artifact_burst["name"] = "Artifact Burst"
artifact_burst["kind"] = "magical"
artifact_burst["power"] = 8
artifact_burst["target_mode"] = "all_enemies"
artifact_burst["animation"] = "artifact_burst"
artifact_burst["sound_id"] = "artifact_burst"
artifact_burst["effects"] = (MoveEffect(status="burn", chance=0.2, duration=2),)
MOVES["artifact_burst"] = MoveSpec(**artifact_burst)

singularity_coil: dict[str, object] = {}
singularity_coil["move_id"] = "singularity_coil"
singularity_coil["name"] = "Singularity Coil"
singularity_coil["kind"] = "magical"
singularity_coil["power"] = 15
singularity_coil["target_mode"] = "single_enemy"
singularity_coil["animation"] = "chaos_zigzag"
singularity_coil["sound_id"] = "arc_bolt"
MOVES["singularity_coil"] = MoveSpec(**singularity_coil)

pixel_storm: dict[str, object] = {}
pixel_storm["move_id"] = "pixel_storm"
pixel_storm["name"] = "Pixel Storm"
pixel_storm["kind"] = "magical"
pixel_storm["power"] = 10
pixel_storm["target_mode"] = "all_enemies"
pixel_storm["animation"] = "pixel_storm"
pixel_storm["sound_id"] = "artifact_burst"
pixel_storm["effects"] = (MoveEffect(status="burn", chance=0.25, duration=2),)
MOVES["pixel_storm"] = MoveSpec(**pixel_storm)

entropy_shield: dict[str, object] = {}
entropy_shield["move_id"] = "entropy_shield"
entropy_shield["name"] = "Entropy Shield"
entropy_shield["kind"] = "buff"
entropy_shield["target_mode"] = "self"
entropy_shield["animation"] = "entropy_shield"
entropy_shield["sound_id"] = "regularization"
entropy_shield["effects"] = (
    MoveEffect(status="guarded", duration=2),
    MoveEffect(status="focus", duration=2),
    MoveEffect(stat="defense", stages=1),
)
MOVES["entropy_shield"] = MoveSpec(**entropy_shield)
