"""Small runtime models for the capstone adventure engine.

World authors normally edit dictionaries in ``capstone/worlds`` instead of
these classes.  The runtime types are deliberately small and conventional so
students who inspect the engine see ordinary Python rather than a framework.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Choice:
    action: str
    text: str


@dataclass
class Actor:
    name: str
    max_hp: int
    attack_min: int
    attack_max: int
    defense: int = 0
    health: int | None = None
    gold: int = 0
    inventory: list[str] = field(default_factory=list)
    equipment: dict[str, str | None] = field(
        default_factory=lambda: {"weapon": None, "armor": None, "charm": None}
    )

    def __post_init__(self) -> None:
        if self.health is None:
            self.health = self.max_hp

    def has_item(self, item_id: str) -> bool:
        return item_id in self.inventory

    def has_items(self, item_ids: list[str]) -> bool:
        owned = Counter(self.inventory)
        needed = Counter(item_ids)
        return all(owned[key] >= count for key, count in needed.items())

    def add_item(self, item_id: str) -> None:
        self.inventory.append(item_id)

    def remove_item(self, item_id: str) -> bool:
        if item_id not in self.inventory:
            return False
        self.inventory.remove(item_id)
        for slot, equipped in self.equipment.items():
            if equipped == item_id:
                self.equipment[slot] = None
        return True

    def remove_items(self, item_ids: list[str]) -> bool:
        if not self.has_items(item_ids):
            return False
        for item_id in item_ids:
            self.remove_item(item_id)
        return True
