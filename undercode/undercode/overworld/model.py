"""Named records for authoring rooms. All arguments are written as keywords.

These classes contain data, not a hidden scripting language. Room's legend maps
letters to records. maps.py walks the letters to place them. Add behavior in
world.py or an ordinary Python callback; drawing.py reads the resulting state.
"""

from dataclasses import dataclass, field
from typing import Callable
from ..dialogue import Dialogue


@dataclass(kw_only=True)
class Spawn:
    """An invisible arrival marker; doors name it instead of using coordinates."""

    name: str
    ground: str = "."


@dataclass(kw_only=True)
class Door:
    """An arrival link with an optional flag/condition explaining why it stays locked."""

    destination_room: str
    destination_spawn: str
    required_flag: str | None = None
    when: Callable | None = None
    locked_text: str = "This door is locked."
    ground: str = "."


@dataclass(kw_only=True)
class Person:
    """An overworld neighbor. Peaceful people need no encounter definition.

    portrait is a drawing function, dialogue is writing, and encounter_id is an
    optional link. id remembers this instance's outcome; omit it for an automatic
    map-local ID. invitation is shown after dialogue when an encounter is offered.
    """

    name: str
    portrait: Callable
    dialogue: Dialogue | None = None
    encounter_id: str | None = None
    id: str | None = None
    invitation: str = "Want to practice? Z: yes. X: later."
    required_flag: str | None = None
    when: Callable | None = None
    locked_text: str = "There is more to do first."
    on_interact: Callable | None = None
    ground: str = "."


@dataclass(kw_only=True)
class Sign:
    """Writing read with Z. Optional on_interact runs before the conversation opens."""

    name: str
    dialogue: Dialogue
    required_flag: str | None = None
    when: Callable | None = None
    locked_text: str = "There is more to do first."
    on_interact: Callable | None = None
    ground: str = "."


@dataclass(kw_only=True)
class Item:
    """A collectible: set flag immediately, disappear, then show text."""

    name: str
    flag: str
    text: str | list[str]
    required_flag: str | None = None
    when: Callable | None = None
    locked_text: str = "There is more to do first."
    on_interact: Callable | None = None
    ground: str = "."


@dataclass(kw_only=True)
class Rest:
    """A fountain; Z restores HP/cocoa while walking near it."""

    name: str = "Lantern fountain"
    required_flag: str | None = None
    when: Callable | None = None
    locked_text: str = "There is more to do first."
    on_interact: Callable | None = None
    ground: str = "."


@dataclass(kw_only=True)
class Trigger:
    """A place calling on_enter(world=..., obj=...) once each time you enter it."""

    name: str
    on_enter: Callable
    required_flag: str | None = None
    when: Callable | None = None
    ground: str = "."


@dataclass(kw_only=True)
class PianoKey:
    """A visible floor key. Mission 7 must detect overlap and choose its note's frequency.

    This record does not contain an automatic trigger or a frequency lookup.
    note is a musical label such as 'C4'; ground is the walkable tile beneath it.
    """

    note: str
    ground: str = "."


@dataclass(kw_only=True)
class Tile:
    """Alias a map letter to terrain, such as 'T': Tile(ground='#')."""

    ground: str


@dataclass(kw_only=True)
class Room:
    """A single-screen map: equally wide strings and a letter-to-object legend."""

    name: str
    tiles: list[str]
    legend: dict = field(default_factory=dict)


@dataclass(kw_only=True)
class PlacedObject:
    """A definition plus an internal (column, row); maps.py creates these from letters."""

    key: str
    tile: tuple[int, int]
    definition: Person | Sign | Item | Rest | Trigger | Door | PianoKey


@dataclass(kw_only=True)
class RoomMap:
    """Compiled terrain and placed records, ready for engine movement and drawing."""

    key: str
    name: str
    tiles: tuple[str, ...]
    objects: list[PlacedObject]
    spawns: dict[str, tuple[int, int]]

    @property
    def people(self):
        """Find people by record type, without a second mutable list to synchronize."""
        return [obj for obj in self.objects if isinstance(obj.definition, Person)]

    @property
    def exits(self):
        """Find doors among the room's placed records."""
        return [obj for obj in self.objects if isinstance(obj.definition, Door)]

    @property
    def rest_tile(self):
        """Return the first fountain tile, or None when this room has no fountain."""
        for obj in self.objects:
            if isinstance(obj.definition, Rest):
                return obj.tile
        return None
