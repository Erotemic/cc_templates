from __future__ import annotations

"""Starter character catalog for the classroom battle project.

Each character is built up from an empty dictionary so students can add or tweak
one field at a time before registering it in ``CHARACTERS``.
"""

from rpg_battle.core.models import CharacterSpec

CHARACTERS: dict[str, CharacterSpec] = {}

knight: dict[str, object] = {}
knight["char_id"] = "knight"
knight["name"] = "Knight of Dawn"
knight["role"] = "defender"
knight["max_hp"] = 58
knight["attack"] = 10
knight["defense"] = 9
knight["magic"] = 4
knight["speed"] = 4
knight["sprite_id"] = "knight_dawn"
knight["move_ids"] = ("shield_bash", "stone_ward", "strike")
knight["description"] = "A steadfast defender."
CHARACTERS["knight"] = CharacterSpec(**knight)

druid: dict[str, object] = {}
druid["char_id"] = "druid"
druid["name"] = "Verdant Druid"
druid["role"] = "support"
druid["max_hp"] = 50
druid["attack"] = 6
druid["defense"] = 6
druid["magic"] = 9
druid["speed"] = 6
druid["sprite_id"] = "verdant_druid"
druid["move_ids"] = ("healing_light", "thorn_bind", "strike")
druid["description"] = "A healer who slows foes with nature magic."
CHARACTERS["druid"] = CharacterSpec(**druid)

ranger: dict[str, object] = {}
ranger["char_id"] = "ranger"
ranger["name"] = "Storm Ranger"
ranger["role"] = "striker"
ranger["max_hp"] = 46
ranger["attack"] = 9
ranger["defense"] = 5
ranger["magic"] = 5
ranger["speed"] = 10
ranger["sprite_id"] = "storm_ranger"
ranger["move_ids"] = ("arc_bolt", "wind_step", "strike")
ranger["description"] = "Fast and accurate."
CHARACTERS["ranger"] = CharacterSpec(**ranger)

mage: dict[str, object] = {}
mage["char_id"] = "mage"
mage["name"] = "Moon Mage"
mage["role"] = "mage"
mage["max_hp"] = 44
mage["attack"] = 5
mage["defense"] = 4
mage["magic"] = 11
mage["speed"] = 7
mage["sprite_id"] = "moon_mage"
mage["move_ids"] = ("arc_bolt", "ember", "strike")
mage["description"] = "A focused spellcaster."
CHARACTERS["mage"] = CharacterSpec(**mage)

guardian: dict[str, object] = {}
guardian["char_id"] = "guardian"
guardian["name"] = "Crystal Guardian"
guardian["role"] = "tank"
guardian["max_hp"] = 62
guardian["attack"] = 8
guardian["defense"] = 10
guardian["magic"] = 6
guardian["speed"] = 4
guardian["sprite_id"] = "crystal_guardian"
guardian["move_ids"] = ("stone_ward", "shield_bash", "strike")
guardian["description"] = "A magical construct of crystal and light."
CHARACTERS["guardian"] = CharacterSpec(**guardian)

spirit: dict[str, object] = {}
spirit["char_id"] = "spirit"
spirit["name"] = "Mist Spirit"
spirit["role"] = "controller"
spirit["max_hp"] = 42
spirit["attack"] = 5
spirit["defense"] = 5
spirit["magic"] = 10
spirit["speed"] = 5
spirit["sprite_id"] = "mist_spirit"
spirit["move_ids"] = ("mist_veil", "arc_bolt", "strike")
spirit["description"] = "Elusive and patient."
CHARACTERS["spirit"] = CharacterSpec(**spirit)

runesage: dict[str, object] = {}
runesage["char_id"] = "runesage"
runesage["name"] = "Runesage"
runesage["role"] = "arcane"
runesage["max_hp"] = 45
runesage["attack"] = 4
runesage["defense"] = 5
runesage["magic"] = 12
runesage["speed"] = 8
runesage["sprite_id"] = "runesage"
runesage["move_ids"] = ("sine_wave", "square_pulse", "fractal_veil")
runesage["description"] = "A pattern mage whose spells are built from geometry."
CHARACTERS["runesage"] = CharacterSpec(**runesage)

ai_slop: dict[str, object] = {}
ai_slop["char_id"] = "ai_slop"
ai_slop["name"] = "AI Slop"
ai_slop["role"] = "aberration"
ai_slop["max_hp"] = 52
ai_slop["attack"] = 7
ai_slop["defense"] = 6
ai_slop["magic"] = 10
ai_slop["speed"] = 3
ai_slop["sprite_id"] = "ai_slop"
ai_slop["move_ids"] = ("gradient_descent", "regularization", "artifact_burst")
ai_slop["description"] = "A strange synthetic ooze with mismatched hands and unstable artifacts."
CHARACTERS["ai_slop"] = CharacterSpec(**ai_slop)

ai_slop_prime: dict[str, object] = {}
ai_slop_prime["char_id"] = "ai_slop_prime"
ai_slop_prime["name"] = "AI Slop Prime"
ai_slop_prime["role"] = "boss"
ai_slop_prime["max_hp"] = 96
ai_slop_prime["attack"] = 9
ai_slop_prime["defense"] = 8
ai_slop_prime["magic"] = 13
ai_slop_prime["speed"] = 3
ai_slop_prime["sprite_id"] = "ai_slop_prime"
ai_slop_prime["move_ids"] = ("gradient_descent", "regularization", "artifact_burst")
ai_slop_prime["description"] = (
    "A swollen, overtrained version of AI Slop that floods the screen with artifacts."
)
CHARACTERS["ai_slop_prime"] = CharacterSpec(**ai_slop_prime)

null_hydra: dict[str, object] = {}
null_hydra["char_id"] = "null_hydra"
null_hydra["name"] = "Null Hydra"
null_hydra["role"] = "boss"
null_hydra["max_hp"] = 104
null_hydra["attack"] = 8
null_hydra["defense"] = 9
null_hydra["magic"] = 14
null_hydra["speed"] = 4
null_hydra["sprite_id"] = "null_hydra"
null_hydra["move_ids"] = ("singularity_coil", "pixel_storm", "entropy_shield")
null_hydra["description"] = "A many-eyed glitch serpent that spits zigzags and pixel storms."
CHARACTERS["null_hydra"] = CharacterSpec(**null_hydra)


star_corsair: dict[str, object] = {}
star_corsair["char_id"] = "star_corsair"
star_corsair["name"] = "Star Corsair"
star_corsair["role"] = "striker"
star_corsair["max_hp"] = 48
star_corsair["attack"] = 10
star_corsair["defense"] = 5
star_corsair["magic"] = 6
star_corsair["speed"] = 9
star_corsair["sprite_id"] = "star_corsair"
star_corsair["move_ids"] = ("strike", "wind_step", "shield_bash")
star_corsair["description"] = "A swaggering duelist who looks dangerous on purpose."
CHARACTERS["star_corsair"] = CharacterSpec(**star_corsair)

velvet_hexer: dict[str, object] = {}
velvet_hexer["char_id"] = "velvet_hexer"
velvet_hexer["name"] = "Velvet Hexer"
velvet_hexer["role"] = "controller"
velvet_hexer["max_hp"] = 46
velvet_hexer["attack"] = 4
velvet_hexer["defense"] = 5
velvet_hexer["magic"] = 12
velvet_hexer["speed"] = 7
velvet_hexer["sprite_id"] = "velvet_hexer"
velvet_hexer["move_ids"] = ("arc_bolt", "thorn_bind", "mist_veil")
velvet_hexer["description"] = "An elegant moon-and-thorn caster with a perfectly composed stare."
CHARACTERS["velvet_hexer"] = CharacterSpec(**velvet_hexer)

siren_engine: dict[str, object] = {}
siren_engine["char_id"] = "siren_engine"
siren_engine["name"] = "Siren Engine"
siren_engine["role"] = "support"
siren_engine["max_hp"] = 50
siren_engine["attack"] = 5
siren_engine["defense"] = 6
siren_engine["magic"] = 10
siren_engine["speed"] = 6
siren_engine["sprite_id"] = "siren_engine"
siren_engine["move_ids"] = ("arc_bolt", "healing_light", "mist_veil")
siren_engine["description"] = "A machine singer that feels graceful and uncanny at the same time."
CHARACTERS["siren_engine"] = CharacterSpec(**siren_engine)

space_pirate: dict[str, object] = {}
space_pirate["char_id"] = "space_pirate"
space_pirate["name"] = "Space Pirate"
space_pirate["role"] = "raider"
space_pirate["max_hp"] = 52
space_pirate["attack"] = 9
space_pirate["defense"] = 6
space_pirate["magic"] = 5
space_pirate["speed"] = 8
space_pirate["sprite_id"] = "space_pirate"
space_pirate["move_ids"] = ("strike", "shield_bash", "artifact_burst")
space_pirate["description"] = "A rough outlaw draped in scavenged star-tech and trophies."
CHARACTERS["space_pirate"] = CharacterSpec(**space_pirate)

tiny_ancient_menace: dict[str, object] = {}
tiny_ancient_menace["char_id"] = "tiny_ancient_menace"
tiny_ancient_menace["name"] = "Tiny Ancient Menace"
tiny_ancient_menace["role"] = "trickster"
tiny_ancient_menace["max_hp"] = 40
tiny_ancient_menace["attack"] = 5
tiny_ancient_menace["defense"] = 6
tiny_ancient_menace["magic"] = 11
tiny_ancient_menace["speed"] = 8
tiny_ancient_menace["sprite_id"] = "tiny_ancient_menace"
tiny_ancient_menace["move_ids"] = ("square_pulse", "entropy_shield", "gradient_descent")
tiny_ancient_menace["description"] = (
    "A pocket ruin-lord with an ancient glare and a terrible attitude."
)
CHARACTERS["tiny_ancient_menace"] = CharacterSpec(**tiny_ancient_menace)

cryptid_friend: dict[str, object] = {}
cryptid_friend["char_id"] = "cryptid_friend"
cryptid_friend["name"] = "Cryptid Friend"
cryptid_friend["role"] = "support"
cryptid_friend["max_hp"] = 47
cryptid_friend["attack"] = 5
cryptid_friend["defense"] = 6
cryptid_friend["magic"] = 9
cryptid_friend["speed"] = 7
cryptid_friend["sprite_id"] = "cryptid_friend"
cryptid_friend["move_ids"] = ("healing_light", "thorn_bind", "mist_veil")
cryptid_friend["description"] = "A warm, watchful companion that nobody can quite classify."
CHARACTERS["cryptid_friend"] = CharacterSpec(**cryptid_friend)
