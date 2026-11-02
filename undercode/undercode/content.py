"""The cast, equipment and overworld. Extend these ordinary data structures."""

from .story import build_story
from .student_world import LEVELS, START_LEVEL, START_ENTRY

from .model import Act, Character, Weapon
from .attacks import TimingStrike, RhythmStrike
from .patterns import FallingPages, ClockworkHops, ShieldWaltz, SafeLanes
from .art import folio, ferris, prism
from .student import EXTRA_CHARACTERS, EXTRA_PATTERNS


def folio_pattern(context):
    """Return fresh falling pages, slowed when context.calm shows understanding."""
    return FallingPages(gentle=context.calm > 0)


def ferris_pattern(context):
    """Return a fresh jump pattern on even defense turns, or beam lanes on odd turns."""
    return ClockworkHops() if context.turn % 2 == 0 else SafeLanes()


def prism_pattern(context):
    """Return a fresh shield pattern on even defense turns, or beam lanes on odd turns."""
    return ShieldWaltz() if context.turn % 2 == 0 else SafeLanes()


CHARACTERS = (
    Character(
        "folio",
        "Folio",
        "The courtyard librarian, carrying too many stories.",
        "Can you read the spaces between my pages? Z: practice. X: later.",
        (172, 220, 255),
        folio,
        (
            Act("Listen", "You let Folio finish the story. The pages settle.", 2),
            Act("Compliment the cover", "Folio pretends not to be pleased.", 1),
            Act("Tell a pun", "A page turns. A very long silence follows.", 0),
        ),
        folio_pattern,
        greeting="Folio opens a new chapter. Every reply has a rhythm.",
        goodbye="Folio writes you into the acknowledgments. You pass as friends.",
    ),
    Character(
        "ferris",
        "Ferris",
        "A clockwork beetle who counts the quiet seconds.",
        "A little footwork? Watch for low gears. Z: practice. X: later.",
        (255, 194, 115),
        ferris,
        (
            Act("Count the rhythm", "You count together. Ferris stops rushing.", 2),
            Act("Inspect the gears", "You notice the care in every tiny tooth.", 1),
            Act("Ask the time", "Ferris gives you the time. To six decimal places.", 0),
        ),
        ferris_pattern,
        max_hp=25,
        greeting='Ferris winds up. "Leave room for a little jump!"',
        goodbye="Ferris gives you an extra minute. You spend it together.",
    ),
    Character(
        "prism",
        "Prism",
        "A visitor who paints with reflected light.",
        "Face the sparks with your shield. Z: practice. X: later.",
        (187, 164, 247),
        prism,
        (
            Act("Mirror a gesture", "You reflect the gesture. Prism feels understood.", 2),
            Act("Ask about colors", "Prism shows you a shade you had never noticed.", 1),
            Act("Interrupt", "The reflection breaks for a moment.", 0),
        ),
        prism_pattern,
        max_hp=24,
        greeting="Prism splits the light into four directions.",
        goodbye="Prism makes room in the picture for you.",
    ),
) + EXTRA_CHARACTERS

WEAPONS = (Weapon("Focus strike", TimingStrike, 13), Weapon("Three beat strike", RhythmStrike, 16))
PATTERNS = {
    "pages": FallingPages,
    "hops": ClockworkHops,
    "shield": ShieldWaltz,
    "lanes": SafeLanes,
    **EXTRA_PATTERNS,
}

# Compile the student's Python story after registering the battle cast.
ROOMS, START_LEVEL, START_ENTRY = build_story(
    LEVELS, START_LEVEL, START_ENTRY, {c.key for c in CHARACTERS}
)
