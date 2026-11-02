"""Content definitions and session memory. No window or mixer is opened here."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .arena import DefensePattern
    from .attacks import Strike

Color = tuple[int, int, int]


class Outcome(Enum):
    """Distinguish making peace, combat victory, leaving, and losing an encounter."""

    SPARED = auto()
    DEFEATED = auto()
    LEFT = auto()
    LOST = auto()


@dataclass(frozen=True)
class Act:
    """Define an ACT menu label, its reply, and its nonnegative understanding gain."""

    name: str
    reply: str
    calm: int = 1


@dataclass(frozen=True)
class TurnContext:
    """Give a pattern selector a read-only snapshot at the start of a defense.

    turn starts at 0. enemy_hp/enemy_max_hp describe the opponent; calm is the
    understanding earned through ACT. Return a new pattern using these values.
    """

    turn: int
    enemy_hp: int
    enemy_max_hp: int
    calm: int


@dataclass(frozen=True)
class Character:
    """Define a reusable battle character and its behavior hooks.

    key identifies this definition; separate Placement keys identify neighbors
    on maps. portrait(surface, center, scale, time) draws its art, while
    choose_pattern(TurnContext) returns a fresh DefensePattern for each turn.
    acts and calm_needed determine how the player can reach SPARE.
    """

    key: str
    name: str
    description: str
    invitation: str
    color: Color
    portrait: Callable
    acts: tuple[Act, ...]
    choose_pattern: Callable[[TurnContext], "DefensePattern"]
    max_hp: int = 22
    calm_needed: int = 3
    greeting: str = "A friendly challenger steps forward."
    goodbye: str = "There is more than one way to finish a conversation."


@dataclass(frozen=True)
class Weapon:
    """Pair a menu name and damage power with a factory for a fresh Strike.

    The strike supplies timing accuracy; Battle combines it with power to apply
    damage. A factory is a callable such as TimingStrike, not an existing instance.
    """

    name: str
    factory: Callable[[], "Strike"]
    power: int = 12


@dataclass
class Player:
    """Keep health, cocoa count, and the selected weapon index across rooms and battles."""

    name: str = "Courier"
    max_hp: int = 20
    hp: int = 20
    snacks: int = 2
    weapon: int = 0

    def heal(self, amount):
        """Add nonnegative amount HP, cap at max_hp, and return the actual HP gained."""
        before = self.hp
        self.hp = min(self.max_hp, self.hp + max(0, amount))
        return self.hp - before

    def rest(self):
        """Restore full HP and two cocoa snacks without changing the selected weapon."""
        self.hp = self.max_hp
        self.snacks = 2


@dataclass
class Session:
    """Keep progress for the current run; restart creates a fresh instance.

    resolved maps character placement IDs to battle outcomes. flags stores story
    facts such as collected items and completed choices. Nothing is saved to disk.
    """

    player: Player = field(default_factory=Player)
    resolved: dict[str, Outcome] = field(default_factory=dict)
    flags: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Placement:
    """Locate one character instance in a compiled level.

    character selects a Character definition; key remembers this instance's
    outcome. tile is an internal (column, row); data holds its Python story options.
    """

    key: str
    character: str
    tile: tuple[int, int]
    data: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Exit:
    """Link an internal door tile to another room and a named landing marker.

    destination is the level key; landing names a spawn in that level, not a
    coordinate pair. data holds requirements and locked-door text from the legend.
    """

    tile: tuple[int, int]
    destination: str
    landing: str
    data: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Room:
    """Hold one compiled letter map and the things placed in it.

    tiles is rectangular terrain; people/exits/objects hold internal positions.
    spawns maps arrival names to (column, row) pairs. rest_tile identifies the
    first fountain, if any. Authors edit Python level definitions; story.build_story compiles them.
    """

    key: str
    name: str
    tiles: tuple[str, ...]
    people: tuple[Placement, ...] = ()
    exits: tuple[Exit, ...] = ()
    rest_tile: tuple[int, int] | None = None
    spawns: dict[str, tuple[int, int]] = field(default_factory=dict)
    objects: tuple["StoryObject", ...] = ()


@dataclass(frozen=True)
class StoryObject:
    """Locate a sign, collectible, rest spot, or trigger compiled from a map letter.

    tile is an internal (column, row). kind decides the interaction, while data
    holds the legend's text, conditions, flags and optional mechanic names.
    """

    key: str
    kind: str
    tile: tuple[int, int]
    data: dict = field(default_factory=dict)
