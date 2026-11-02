"""Ready-to-play encounters and patterns. This module never loads rooms."""

from .model import Act, Opponent, Weapon
from .attacks import TimingStrike, RhythmStrike
from .patterns import FallingPages, ClockworkHops, ShieldWaltz, SafeLanes
from ..art import folio, ferris, prism
from ..student_encounters import EXTRA_OPPONENTS, EXTRA_PATTERNS


def folio_pattern(*, context):
    """Return fresh falling pages, slowed when context.calm shows understanding."""
    return FallingPages(gentle=context.calm > 0)


def ferris_pattern(*, context):
    """Return a fresh jump pattern on even defense turns, or beam lanes on odd turns."""
    return ClockworkHops() if context.turn % 2 == 0 else SafeLanes()


def prism_pattern(*, context):
    """Return a fresh shield pattern on even defense turns, or beam lanes on odd turns."""
    return ShieldWaltz() if context.turn % 2 == 0 else SafeLanes()


OPPONENTS = (
    Opponent(
        key="folio",
        name="Folio",
        description="The courtyard librarian, carrying too many stories.",
        color=(172, 220, 255),
        portrait=folio,
        acts=(
            Act(name="Listen", reply="You let Folio finish the story. The pages settle.", calm=2),
            Act(name="Compliment the cover", reply="Folio pretends not to be pleased.", calm=1),
            Act(name="Tell a pun", reply="A page turns. A very long silence follows.", calm=0),
        ),
        choose_pattern=folio_pattern,
        greeting="Folio opens a new chapter. Every reply has a rhythm.",
        goodbye="Folio writes you into the acknowledgments. You pass as friends.",
    ),
    Opponent(
        key="ferris",
        name="Ferris",
        description="A clockwork beetle who counts the quiet seconds.",
        color=(255, 194, 115),
        portrait=ferris,
        acts=(
            Act(name="Count the rhythm", reply="You count together. Ferris stops rushing.", calm=2),
            Act(name="Inspect the gears", reply="You notice the care in every tiny tooth.", calm=1),
            Act(
                name="Ask the time",
                reply="Ferris gives you the time. To six decimal places.",
                calm=0,
            ),
        ),
        choose_pattern=ferris_pattern,
        max_hp=25,
        greeting='Ferris winds up. "Leave room for a little jump!"',
        goodbye="Ferris gives you an extra minute. You spend it together.",
    ),
    Opponent(
        key="prism",
        name="Prism",
        description="A visitor who paints with reflected light.",
        color=(187, 164, 247),
        portrait=prism,
        acts=(
            Act(
                name="Mirror a gesture",
                reply="You reflect the gesture. Prism feels understood.",
                calm=2,
            ),
            Act(
                name="Ask about colors",
                reply="Prism shows you a shade you had never noticed.",
                calm=1,
            ),
            Act(name="Interrupt", reply="The reflection breaks for a moment.", calm=0),
        ),
        choose_pattern=prism_pattern,
        max_hp=24,
        greeting="Prism splits the light into four directions.",
        goodbye="Prism makes room in the picture for you.",
    ),
) + EXTRA_OPPONENTS

WEAPONS = (
    Weapon(name="Focus strike", factory=TimingStrike, power=13),
    Weapon(name="Three beat strike", factory=RhythmStrike, power=16),
)
PATTERNS = {
    "pages": FallingPages,
    "hops": ClockworkHops,
    "shield": ShieldWaltz,
    "lanes": SafeLanes,
}

# Extend the editable registry with ordinary dictionary update.
PATTERNS.update(EXTRA_PATTERNS)
