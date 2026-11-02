"""Content definitions and session memory. No window or mixer is opened here."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .arena import DefensePattern
    from .attacks import Strike

Color = tuple[int, int, int]


class Outcome(Enum):
    SPARED = auto()
    DEFEATED = auto()
    LEFT = auto()
    LOST = auto()


@dataclass(frozen=True)
class Act:
    name: str
    reply: str
    calm: int = 1


@dataclass(frozen=True)
class TurnContext:
    """Read-only information an enemy uses to choose its next pattern."""

    turn: int
    enemy_hp: int
    enemy_max_hp: int
    calm: int


@dataclass(frozen=True)
class Character:
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
    name: str
    factory: Callable[[], "Strike"]
    power: int = 12


@dataclass
class Player:
    name: str = "Courier"
    max_hp: int = 20
    hp: int = 20
    snacks: int = 2
    weapon: int = 0

    def heal(self, amount):
        before = self.hp
        self.hp = min(self.max_hp, self.hp + max(0, amount))
        return self.hp - before

    def rest(self):
        self.hp = self.max_hp
        self.snacks = 2


@dataclass
class Session:
    player: Player = field(default_factory=Player)
    resolved: dict[str, Outcome] = field(default_factory=dict)
    flags: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Placement:
    key: str
    character: str
    tile: tuple[int, int]
    data: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Exit:
    tile: tuple[int, int]
    destination: str
    landing: str
    data: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Room:
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
    """A map symbol compiled to a position; authors edit its JSON, not this class."""

    key: str
    kind: str
    tile: tuple[int, int]
    data: dict = field(default_factory=dict)
