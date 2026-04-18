"""Reusable color palettes for procedural battlers.

Palettes are built incrementally so students can define a new color family one
swatch at a time.
"""

PALETTES: dict[str, dict[str, tuple[int, int, int]]] = {}

dawn: dict[str, tuple[int, int, int]] = {}
dawn["body"] = (92, 118, 196)
dawn["accent"] = (247, 210, 126)
dawn["eye"] = (245, 244, 255)
dawn["detail"] = (55, 61, 97)
PALETTES["dawn"] = dawn

verdant: dict[str, tuple[int, int, int]] = {}
verdant["body"] = (77, 152, 101)
verdant["accent"] = (182, 222, 124)
verdant["eye"] = (244, 255, 241)
verdant["detail"] = (44, 87, 53)
PALETTES["verdant"] = verdant

storm: dict[str, tuple[int, int, int]] = {}
storm["body"] = (87, 133, 176)
storm["accent"] = (184, 230, 245)
storm["eye"] = (243, 250, 255)
storm["detail"] = (42, 72, 112)
PALETTES["storm"] = storm

moon: dict[str, tuple[int, int, int]] = {}
moon["body"] = (133, 110, 197)
moon["accent"] = (225, 215, 255)
moon["eye"] = (255, 248, 255)
moon["detail"] = (74, 52, 126)
PALETTES["moon"] = moon

crystal: dict[str, tuple[int, int, int]] = {}
crystal["body"] = (115, 190, 205)
crystal["accent"] = (215, 246, 255)
crystal["eye"] = (240, 255, 255)
crystal["detail"] = (50, 100, 110)
PALETTES["crystal"] = crystal

mist: dict[str, tuple[int, int, int]] = {}
mist["body"] = (159, 152, 198)
mist["accent"] = (226, 226, 248)
mist["eye"] = (250, 249, 255)
mist["detail"] = (90, 86, 125)
PALETTES["mist"] = mist

rune: dict[str, tuple[int, int, int]] = {}
rune["body"] = (102, 124, 156)
rune["accent"] = (245, 198, 120)
rune["eye"] = (247, 248, 255)
rune["detail"] = (51, 60, 81)
PALETTES["rune"] = rune

slop: dict[str, tuple[int, int, int]] = {}
slop["body"] = (148, 150, 126)
slop["accent"] = (228, 133, 186)
slop["eye"] = (245, 255, 214)
slop["detail"] = (76, 62, 95)
PALETTES["slop"] = slop


corsair: dict[str, tuple[int, int, int]] = {}
corsair["body"] = (94, 92, 165)
corsair["accent"] = (246, 204, 118)
corsair["eye"] = (250, 246, 255)
corsair["detail"] = (49, 42, 91)
PALETTES["corsair"] = corsair

velvet: dict[str, tuple[int, int, int]] = {}
velvet["body"] = (98, 66, 112)
velvet["accent"] = (205, 179, 232)
velvet["eye"] = (252, 245, 255)
velvet["detail"] = (55, 32, 68)
PALETTES["velvet"] = velvet

siren: dict[str, tuple[int, int, int]] = {}
siren["body"] = (123, 164, 184)
siren["accent"] = (220, 236, 244)
siren["eye"] = (246, 252, 255)
siren["detail"] = (62, 88, 104)
PALETTES["siren"] = siren

raider: dict[str, tuple[int, int, int]] = {}
raider["body"] = (123, 92, 82)
raider["accent"] = (236, 162, 107)
raider["eye"] = (250, 243, 236)
raider["detail"] = (63, 44, 40)
PALETTES["raider"] = raider

menace: dict[str, tuple[int, int, int]] = {}
menace["body"] = (123, 111, 79)
menace["accent"] = (241, 202, 98)
menace["eye"] = (250, 243, 220)
menace["detail"] = (69, 58, 33)
PALETTES["menace"] = menace

cryptid: dict[str, tuple[int, int, int]] = {}
cryptid["body"] = (115, 154, 137)
cryptid["accent"] = (203, 234, 216)
cryptid["eye"] = (246, 255, 248)
cryptid["detail"] = (54, 84, 70)
PALETTES["cryptid"] = cryptid
