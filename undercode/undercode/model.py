"""Persistent state shared by the two systems. No content or pygame imports.

Player is the ONLY owner of HP and snacks. The overworld and encounter borrow
this same object; an arena never keeps a second copy of health to synchronize.
Session lasts for one run. R creates a new Session rather than saving to disk.
"""

from dataclasses import dataclass, field
from .contracts import Outcome


@dataclass(kw_only=True)
class Player:
    """A dataclass is a record: named fields plus useful operations on those fields."""

    name: str = "Courier"
    max_hp: int = 20
    hp: int = 20
    snacks: int = 2
    weapon: int = 0

    def heal(self, *, amount):
        """Add HP up to max_hp and return the actual gain (possibly zero)."""
        before = self.hp
        self.hp = min(self.max_hp, self.hp + max(0, amount))
        return self.hp - before

    def rest(self):
        """Restore full HP and two cocoa snacks; keep the chosen technique."""
        self.hp = self.max_hp
        self.snacks = 2


@dataclass(kw_only=True)
class Session:
    """Remember this run's player, story flags, and outcomes by overworld person ID."""

    player: Player = field(default_factory=Player)
    flags: set[str] = field(default_factory=set)
    resolved: dict[str, Outcome] = field(default_factory=dict)
