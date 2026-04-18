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
