from __future__ import annotations

import math

from rpg_battle.render.sprite_animation import select_frame, state_visual, visual_duration
from rpg_battle.render.sprite_motion import evaluate_character_motion, motion_duration


FRAME_A = {"kind": "procedural", "palette": "p", "scale": 1.0, "shapes": [{"kind": "circle"}]}
FRAME_B = {"kind": "procedural", "palette": "p", "scale": 1.0, "shapes": [{"kind": "rect"}]}


def test_frame_animation_uses_time_times_fps() -> None:
    animation = {
        "kind": "frame_animation",
        "fps": 4.0,
        "loop": False,
        "frames": [FRAME_A, FRAME_B],
    }
    assert select_frame(animation, 0.0) is FRAME_A
    assert select_frame(animation, 0.24) is FRAME_A
    assert select_frame(animation, 0.25) is FRAME_B
    assert select_frame(animation, 99.0) is FRAME_B
    assert visual_duration(animation) == 0.5


def test_looping_frame_animation_wraps() -> None:
    animation = {
        "kind": "frame_animation",
        "fps": 2.0,
        "loop": True,
        "frames": [FRAME_A, FRAME_B],
    }
    assert select_frame(animation, 1.0) is FRAME_A
    assert select_frame(animation, 1.5) is FRAME_B


def test_character_art_falls_back_to_idle_visual() -> None:
    recipe = {
        "kind": "character_art",
        "scale": 1.0,
        "states": {"idle": FRAME_A},
    }
    assert state_visual(recipe, "idle") is FRAME_A
    assert state_visual(recipe, "attack") is FRAME_A
    assert state_visual(recipe, "hurt") is FRAME_A


def test_default_motion_composes_idle_bob_and_attack_lunge() -> None:
    motions = {
        "idle": {"kind": "bob", "height": 3.0, "period": 2.0},
        "attack": {"kind": "lunge", "distance": 18.0, "duration": 0.25},
        "hurt": {"kind": "shake", "distance": 6.0, "duration": 0.3, "cycles": 2.0},
        "faint": {
            "kind": "fall",
            "distance": 110.0,
            "duration": 0.9,
            "rotation": 180.0,
            "rotation_duration": 0.24,
            "show_x_eyes": True,
        },
    }
    transform = evaluate_character_motion(
        motions,
        state="attack",
        idle_elapsed=0.5,
        state_elapsed=0.125,
        side="left",
    )
    assert math.isclose(transform.x, 18.0, rel_tol=1e-6)
    assert math.isclose(transform.y, 3.0, rel_tol=1e-6)
    assert motion_duration(motions["attack"]) == 0.25


def test_faint_motion_replaces_idle_bob() -> None:
    motions = {
        "idle": {"kind": "bob", "height": 3.0, "period": 2.0},
        "attack": {"kind": "lunge", "distance": 18.0, "duration": 0.25},
        "hurt": {"kind": "shake", "distance": 6.0, "duration": 0.3, "cycles": 2.0},
        "faint": {
            "kind": "fall",
            "distance": 90.0,
            "duration": 0.9,
            "rotation": 180.0,
            "rotation_duration": 0.3,
            "show_x_eyes": True,
        },
    }
    transform = evaluate_character_motion(
        motions,
        state="faint",
        idle_elapsed=0.5,
        state_elapsed=0.45,
        side="left",
    )
    assert math.isclose(transform.y, 45.0, rel_tol=1e-6)
    assert transform.rotation == 180.0
    assert transform.show_x_eyes
