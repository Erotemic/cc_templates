from __future__ import annotations

"""Starter character catalog for the classroom battle project.

Each character is added to the catalog one at a time so students can copy an
existing entry, tweak it, and register a new battler without editing a giant
dictionary literal.
"""

from rpg_battle.core.models import CharacterSpec

CHARACTERS: dict[str, CharacterSpec] = {}

CHARACTERS["knight"] = CharacterSpec(
    char_id="knight",
    name="Knight of Dawn",
    role="defender",
    max_hp=58,
    attack=10,
    defense=9,
    magic=4,
    speed=4,
    sprite_id="knight_dawn",
    move_ids=("shield_bash", "stone_ward", "strike"),
    description="A steadfast defender.",
)

CHARACTERS["druid"] = CharacterSpec(
    char_id="druid",
    name="Verdant Druid",
    role="support",
    max_hp=50,
    attack=6,
    defense=6,
    magic=9,
    speed=6,
    sprite_id="verdant_druid",
    move_ids=("healing_light", "thorn_bind", "strike"),
    description="A healer who slows foes with nature magic.",
)

CHARACTERS["ranger"] = CharacterSpec(
    char_id="ranger",
    name="Storm Ranger",
    role="striker",
    max_hp=46,
    attack=9,
    defense=5,
    magic=5,
    speed=10,
    sprite_id="storm_ranger",
    move_ids=("arc_bolt", "wind_step", "strike"),
    description="Fast and accurate.",
)

CHARACTERS["mage"] = CharacterSpec(
    char_id="mage",
    name="Moon Mage",
    role="mage",
    max_hp=44,
    attack=5,
    defense=4,
    magic=11,
    speed=7,
    sprite_id="moon_mage",
    move_ids=("arc_bolt", "ember", "strike"),
    description="A focused spellcaster.",
)

CHARACTERS["guardian"] = CharacterSpec(
    char_id="guardian",
    name="Crystal Guardian",
    role="tank",
    max_hp=62,
    attack=8,
    defense=10,
    magic=6,
    speed=4,
    sprite_id="crystal_guardian",
    move_ids=("stone_ward", "shield_bash", "strike"),
    description="A magical construct of crystal and light.",
)

CHARACTERS["spirit"] = CharacterSpec(
    char_id="spirit",
    name="Mist Spirit",
    role="controller",
    max_hp=42,
    attack=5,
    defense=5,
    magic=10,
    speed=5,
    sprite_id="mist_spirit",
    move_ids=("mist_veil", "arc_bolt", "strike"),
    description="Elusive and patient.",
)

CHARACTERS["runesage"] = CharacterSpec(
    char_id="runesage",
    name="Runesage",
    role="arcane",
    max_hp=45,
    attack=4,
    defense=5,
    magic=12,
    speed=8,
    sprite_id="runesage",
    move_ids=("sine_wave", "square_pulse", "fractal_veil"),
    description="A pattern mage whose spells are built from geometry.",
)

CHARACTERS["ai_slop"] = CharacterSpec(
    char_id="ai_slop",
    name="AI Slop",
    role="aberration",
    max_hp=52,
    attack=7,
    defense=6,
    magic=10,
    speed=3,
    sprite_id="ai_slop",
    move_ids=("gradient_descent", "regularization", "artifact_burst"),
    description="A strange synthetic ooze with mismatched hands and unstable artifacts.",
)
