"""Small reusable engine for the advanced adventure examples.

This module deliberately avoids input(), print(), Textual, and story-specific
branches. It owns only reusable game mechanics and a tiny interface that a
world module supplies with ordinary Python functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Choice:
    """One action the player can legally choose right now."""

    action: str
    text: str


@dataclass(frozen=True)
class Room:
    key: str
    name: str
    description: str
    exits: dict[str, str]


@dataclass(frozen=True)
class Enemy:
    key: str
    name: str
    hp: int
    attack: int
    reward_gold: int = 0


@dataclass
class Player:
    name: str = "Tav"
    location: str = ""
    hp: int = 18
    max_hp: int = 18
    attack: int = 5
    gold: int = 0
    inventory: list[str] = field(default_factory=list)
    flags: set[str] = field(default_factory=set)

    def has(self, item: str) -> bool:
        return item in self.inventory

    def give(self, item: str) -> None:
        if item not in self.inventory:
            self.inventory.append(item)

    def take(self, item: str) -> bool:
        if item not in self.inventory:
            return False
        self.inventory.remove(item)
        return True


# These aliases make the World dataclass readable without inventing a hierarchy
# of Effect, Controller, Engine, Feature, and Encounter classes.
DescribeExtra = Callable[["AdventureGame"], list[str]]
GetChoices = Callable[["AdventureGame"], list[Choice]]
HandleAction = Callable[["AdventureGame", str], list[str]]
EnemyDefeated = Callable[["AdventureGame", Enemy], list[str]]


@dataclass(frozen=True)
class World:
    """Story data plus a few ordinary functions for world-specific rules."""

    title: str
    start_location: str
    rooms: dict[str, Room]
    enemies: dict[str, Enemy]
    describe_extra: DescribeExtra
    get_choices: GetChoices
    handle_action: HandleAction
    on_enemy_defeated: EnemyDefeated


class AdventureGame:
    """Reusable state machine shared by the console, Textual UI, and tests."""

    def __init__(self, world: World, player_name: str = "Tav") -> None:
        self.world = world
        self.player = Player(name=player_name, location=world.start_location)
        self.won = False
        self.lost = False
        self.ending = ""
        self.combat_enemy_key: str | None = None
        self.combat_enemy_hp = 0
        self.combat_return_location: str | None = None

    @property
    def over(self) -> bool:
        return self.won or self.lost

    @property
    def room(self) -> Room:
        return self.world.rooms[self.player.location]

    def describe(self) -> list[str]:
        """Return presentation-neutral lines describing the current state."""
        if self.combat_enemy_key is not None:
            enemy = self.world.enemies[self.combat_enemy_key]
            return [
                f"Combat: {enemy.name}",
                f"Your HP: {self.player.hp}/{self.player.max_hp}",
                f"Enemy HP: {self.combat_enemy_hp}/{enemy.hp}",
            ]

        lines = [
            self.room.name,
            self.room.description,
            f"HP: {self.player.hp}/{self.player.max_hp}    Gold: {self.player.gold}",
            "Inventory: " + (", ".join(self.player.inventory) or "empty"),
        ]
        lines.extend(self.world.describe_extra(self))
        return lines

    def exit_choices(self) -> list[Choice]:
        """Build normal movement choices from the current Room's exit data."""
        return [
            Choice(action=f"go:{destination}", text=f"Go {label}")
            for label, destination in self.room.exits.items()
        ]

    def choices(self) -> list[Choice]:
        if self.over:
            return []
        if self.combat_enemy_key is not None:
            return [
                Choice("combat:attack", "Attack"),
                Choice("combat:run", "Run away"),
            ]
        return self.world.get_choices(self)

    def apply(self, action: str) -> list[str]:
        """Apply one legal action and return lines describing the result."""
        legal_actions = {choice.action for choice in self.choices()}
        if action not in legal_actions:
            raise ValueError(f"Action is not legal right now: {action!r}")

        if action.startswith("go:"):
            destination = action.removeprefix("go:")
            self.move(destination)
            return []

        if action == "combat:attack":
            return self.attack_enemy()
        if action == "combat:run":
            return self.run_from_combat()

        return self.world.handle_action(self, action)

    def move(self, destination: str) -> None:
        if destination not in self.world.rooms:
            raise KeyError(f"Unknown room: {destination!r}")
        self.player.location = destination

    def give_item(self, item: str) -> bool:
        """Give an item once. Return True only when it was newly added."""
        if self.player.has(item):
            return False
        self.player.give(item)
        return True

    def take_item(self, item: str) -> bool:
        return self.player.take(item)

    def set_flag(self, flag: str) -> None:
        self.player.flags.add(flag)

    def has_flag(self, flag: str) -> bool:
        return flag in self.player.flags

    def heal(self, amount: int | None = None) -> int:
        before = self.player.hp
        if amount is None:
            self.player.hp = self.player.max_hp
        else:
            self.player.hp = min(self.player.max_hp, self.player.hp + amount)
        return self.player.hp - before

    def start_combat(self, enemy_key: str, *, return_location: str | None = None) -> None:
        enemy = self.world.enemies[enemy_key]
        self.combat_enemy_key = enemy_key
        self.combat_enemy_hp = enemy.hp
        self.combat_return_location = return_location or self.player.location

    def attack_enemy(self) -> list[str]:
        enemy = self.world.enemies[self.combat_enemy_key]
        lines: list[str] = []

        self.combat_enemy_hp = max(0, self.combat_enemy_hp - self.player.attack)
        lines.append(f"You hit the {enemy.name} for {self.player.attack} damage.")

        if self.combat_enemy_hp == 0:
            self.player.gold += enemy.reward_gold
            defeated = enemy
            self.combat_enemy_key = None
            self.combat_return_location = None
            lines.append(f"You defeated the {enemy.name}!")
            if enemy.reward_gold:
                lines.append(f"You found {enemy.reward_gold} gold.")
            lines.extend(self.world.on_enemy_defeated(self, defeated))
            return lines

        self.player.hp = max(0, self.player.hp - enemy.attack)
        lines.append(f"The {enemy.name} hits you for {enemy.attack} damage.")
        if self.player.hp == 0:
            self.lose(f"The {enemy.name} defeated you.")
            self.combat_enemy_key = None
            self.combat_return_location = None
            lines.append(self.ending)
        return lines

    def run_from_combat(self) -> list[str]:
        enemy = self.world.enemies[self.combat_enemy_key]
        destination = self.combat_return_location or self.player.location
        self.combat_enemy_key = None
        self.combat_enemy_hp = 0
        self.combat_return_location = None
        self.player.location = destination
        return [f"You escape from the {enemy.name}."]

    def win(self, message: str) -> None:
        self.won = True
        self.ending = message

    def lose(self, message: str) -> None:
        self.lost = True
        self.ending = message
