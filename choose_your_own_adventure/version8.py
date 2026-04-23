from __future__ import annotations

"""
Single-file RPG architecture prototype.

This version integrates the TUI with the game a little bit better.
"""

from collections import Counter
from dataclasses import dataclass, field
import random
import time
from typing import Callable


# ============================================================
# Small helpers / presentation
# ============================================================


def typewriter_print(prefix: str, text: str, word_delay: float = 0.018) -> None:
    print(prefix, end="")
    for word in text.split():
        print(word, end=" ", flush=True)
        time.sleep(word_delay)
    print()


def say(name: str, text: str) -> None:
    typewriter_print(f"{name}: ", text)


def divider(title: str | None = None) -> None:
    print("\n" + "=" * 72)
    if title:
        print(title)
        print("-" * 72)


def action_separator(label: str | None = None) -> None:
    print("\n" + "-" * 72)
    if label:
        print(f"> {label}")
        print("-" * 72)


def prompt_continue(prompt: str = "Press Enter to continue...") -> None:
    input(f"\n{prompt}")


# ============================================================
# Core data models
# ============================================================


@dataclass
class Stats:
    max_hp: int
    attack_min: int
    attack_max: int
    defense: int = 0


@dataclass
class Item:
    item_id: str
    name: str
    description: str = ""
    slot: str | None = None
    power_bonus: int = 0
    defense_bonus: int = 0
    hp_bonus: int = 0
    healing: int = 0
    set_flags_on_pickup: set[str] = field(default_factory=set)
    tags: set[str] = field(default_factory=set)


@dataclass
class TradeOffer:
    title: str
    wants_items: list[str] = field(default_factory=list)
    gives_items: list[str] = field(default_factory=list)
    wants_gold: int = 0
    gives_gold: int = 0
    repeatable: bool = False
    required_flags: set[str] = field(default_factory=set)
    blocked_flags: set[str] = field(default_factory=set)


@dataclass
class DialogueTopic:
    key: str
    title: str
    lines: list[str]
    required_flags: set[str] = field(default_factory=set)
    blocked_flags: set[str] = field(default_factory=set)
    required_items: list[str] = field(default_factory=list)
    once: bool = False
    outcome_effect: Effect | None = None


@dataclass
class Riddle:
    question: str
    answers: list[str]
    intro_lines: list[str] = field(default_factory=list)
    success_lines: list[str] = field(default_factory=list)
    failure_lines: list[str] = field(default_factory=list)
    repeat_lines: list[str] = field(default_factory=list)
    damage_on_failure: int = 0
    set_flags_on_success: set[str] = field(default_factory=set)


@dataclass
class Exit:
    direction: str
    destination: str
    requires_item: str | None = None
    requires_flag: str | None = None
    blocked: bool = False
    blocked_text: str = "That path is blocked."
    warning_text: str | None = None
    on_attempt_effect: Effect | None = None
    on_blocked_effect: Effect | None = None
    on_success_effect: Effect | None = None


@dataclass
class Location:
    key: str
    name: str
    description: str
    exits: list[Exit] = field(default_factory=list)
    items: list[str] = field(default_factory=list)
    npcs: list[NPC] = field(default_factory=list)
    features: list[Feature] = field(default_factory=list)


# ============================================================
# Effects
# ============================================================


class Effect:
    def apply(self, game: Game) -> None:
        raise NotImplementedError


class PrintEffect(Effect):
    def __init__(self, lines: str | list[str]):
        self.lines = [lines] if isinstance(lines, str) else lines

    def apply(self, game: Game) -> None:
        for line in self.lines:
            print(line)


class SetFlagEffect(Effect):
    def __init__(self, *flags: str):
        self.flags = list(flags)

    def apply(self, game: Game) -> None:
        for flag in self.flags:
            game.flags.add(flag)


class ClearFlagEffect(Effect):
    def __init__(self, *flags: str):
        self.flags = list(flags)

    def apply(self, game: Game) -> None:
        for flag in self.flags:
            game.flags.discard(flag)


class SetBountyEffect(Effect):
    def __init__(self, amount: int):
        self.amount = amount

    def apply(self, game: Game) -> None:
        game.bounty = max(0, self.amount)
        print(f"[Bounty] Set to {game.bounty}")


class ChangeBountyEffect(Effect):
    def __init__(self, amount: int, reason: str | None = None):
        self.amount = amount
        self.reason = reason

    def apply(self, game: Game) -> None:
        game.change_bounty(self.amount, self.reason)


class HealPlayerEffect(Effect):
    def __init__(
        self, amount: int, heal_text: str | None = None, full_text: str | None = None
    ):
        self.amount = amount
        self.heal_text = heal_text or "You recover some health."
        self.full_text = full_text or "You already feel fully rested."

    def apply(self, game: Game) -> None:
        if game.player.health >= game.player.total_max_hp(game.world.item_db):
            print(self.full_text)
            return
        print(self.heal_text)
        healed = game.player.heal(self.amount, game.world.item_db)
        print(f"Recovered {healed} health.")


class GivePlayerItemEffect(Effect):
    def __init__(self, *item_ids: str):
        self.item_ids = list(item_ids)

    def apply(self, game: Game) -> None:
        for item_id in self.item_ids:
            game.give_player_item(item_id)


class ChangeGoldEffect(Effect):
    def __init__(
        self, amount: int, *, target: str = "player", reason: str | None = None
    ):
        self.amount = amount
        self.target = target
        self.reason = reason

    def apply(self, game: Game) -> None:
        actor = game.player if self.target == "player" else game.find_npc(self.target)
        if actor is None:
            return
        actor.gold = max(0, actor.gold + self.amount)
        label = f"[Gold] {actor.name} now has {actor.gold} gold"
        if self.reason:
            print(f"{self.reason}")
            print(label)
        elif self.target == "player":
            if self.amount > 0:
                print(f"You gain {self.amount} gold.")
            elif self.amount < 0:
                print(f"You lose {-self.amount} gold.")
            print(label)


class RemoveItemEffect(Effect):
    def __init__(
        self, item_id: str, *, target: str = "player", text: str | None = None
    ):
        self.item_id = item_id
        self.target = target
        self.text = text

    def apply(self, game: Game) -> None:
        actor = game.player if self.target == "player" else game.find_npc(self.target)
        if actor is None:
            return
        if actor.remove_item(self.item_id) and self.text:
            print(self.text)


class RemoveRandomItemEffect(Effect):
    def __init__(self, *, target: str = "player", text_prefix: str = "You lose"):
        self.target = target
        self.text_prefix = text_prefix

    def apply(self, game: Game) -> None:
        actor = game.player if self.target == "player" else game.find_npc(self.target)
        if actor is None or not actor.inventory:
            return
        item_id = random.choice(actor.inventory)
        actor.remove_item(item_id)
        print(f"{self.text_prefix}: {game.item_name(item_id)}")


class DamageCharacterEffect(Effect):
    def __init__(self, target: str, amount: int, text: str | None = None):
        self.target = target
        self.amount = amount
        self.text = text

    def apply(self, game: Game) -> None:
        actor: Character | None
        if self.target == "player":
            actor = game.player
        else:
            actor = game.find_npc(self.target)
        if actor is None:
            return
        if self.text:
            print(self.text)
        actual = actor.take_damage(self.amount, game.world.item_db)
        print(f"{actor.name} takes {actual} damage.")
        if isinstance(actor, NPC) and not actor.is_alive() and not actor.defeated:
            actor.on_defeat(game)


class MovePlayerEffect(Effect):
    def __init__(self, destination: str, text: str | None = None):
        self.destination = destination
        self.text = text

    def apply(self, game: Game) -> None:
        if self.text:
            print(self.text)
        game.player.location = self.destination
        game.flags.add(f"visited:{self.destination}")
        game.world.on_location_enter(game, game.current_location())


class BlockPathEffect(Effect):
    def __init__(self, location_key: str, direction: str, reason: str):
        self.location_key = location_key
        self.direction = direction
        self.reason = reason

    def apply(self, game: Game) -> None:
        game.world.block_path(self.location_key, self.direction, self.reason)


class UnblockPathEffect(Effect):
    def __init__(self, location_key: str, direction: str):
        self.location_key = location_key
        self.direction = direction

    def apply(self, game: Game) -> None:
        game.world.unblock_path(self.location_key, self.direction)


class ConditionalEffect(Effect):
    def __init__(
        self,
        *,
        required_flags: set[str] | None = None,
        blocked_flags: set[str] | None = None,
        required_items: list[str] | None = None,
        success_effect: Effect,
        failure_effect: Effect | None = None,
    ):
        self.required_flags = required_flags or set()
        self.blocked_flags = blocked_flags or set()
        self.required_items = required_items or []
        self.success_effect = success_effect
        self.failure_effect = failure_effect

    def apply(self, game: Game) -> None:
        ok = True
        if not self.required_flags.issubset(game.flags):
            ok = False
        if self.blocked_flags.intersection(game.flags):
            ok = False
        if not game.player.has_items(self.required_items):
            ok = False
        if ok:
            self.success_effect.apply(game)
        elif self.failure_effect is not None:
            self.failure_effect.apply(game)


class ChanceEffect(Effect):
    def __init__(
        self,
        chance: float,
        success_effect: Effect,
        failure_effect: Effect | None = None,
    ):
        self.chance = chance
        self.success_effect = success_effect
        self.failure_effect = failure_effect

    def apply(self, game: Game) -> None:
        if random.random() < self.chance:
            self.success_effect.apply(game)
        elif self.failure_effect is not None:
            self.failure_effect.apply(game)


class CompositeEffect(Effect):
    def __init__(self, *effects: Effect):
        self.effects = list(effects)

    def apply(self, game: Game) -> None:
        for effect in self.effects:
            effect.apply(game)


class EndGameEffect(Effect):
    def __init__(self, lines: str | list[str], *flags: str):
        self.lines = [lines] if isinstance(lines, str) else list(lines)
        self.flags = list(flags)

    def apply(self, game: Game) -> None:
        for line in self.lines:
            print(line)
        for flag in self.flags:
            game.flags.add(flag)
        game.running = False


class BranchOnBountyEffect(Effect):
    def __init__(
        self,
        clean_effect: Effect,
        hot_effect: Effect,
        *,
        threshold: int = 0,
    ):
        self.clean_effect = clean_effect
        self.hot_effect = hot_effect
        self.threshold = threshold

    def apply(self, game: Game) -> None:
        if game.bounty <= self.threshold:
            self.clean_effect.apply(game)
        else:
            self.hot_effect.apply(game)


# ============================================================
# Controllers and characters
# ============================================================


class Controller:
    def choose_combat_action(
        self, game: Game, actor: Character, opponent: Character
    ) -> tuple[str, str | None]:
        raise NotImplementedError


class PlayerController(Controller):
    def choose_combat_action(
        self, game: Game, actor: Character, opponent: Character
    ) -> tuple[str, str | None]:
        options = [
            {"kind": "attack", "text": "Attack", "value": None},
            {"kind": "defend", "text": "Defend", "value": None},
            {"kind": "item", "text": "Use consumable", "value": None},
            {"kind": "run", "text": "Run", "value": None},
            {"kind": "surrender", "text": "Surrender", "value": None},
        ]
        choice = game.choose(options, prompt="Choose a combat action: ")
        if choice["kind"] == "item":
            consumables = actor.consumable_items(game.world.item_db)
            if not consumables:
                print("You have no consumables to use.")
                return "none", None
            item_options = []
            for item_id in consumables:
                item = game.world.item(item_id)
                item_options.append(
                    {
                        "kind": "use",
                        "text": f"Use {item.name} (+{item.healing} HP)",
                        "value": item_id,
                    }
                )
            item_options.append({"kind": "back", "text": "Back", "value": None})
            item_choice = game.choose(item_options, prompt="Choose an item: ")
            if item_choice["kind"] == "back":
                return "none", None
            return "item", item_choice["value"]
        return choice["kind"], choice["value"]


class AIController(Controller):
    def choose_combat_action(
        self, game: Game, actor: Character, opponent: Character
    ) -> tuple[str, str | None]:
        consumables = actor.consumable_items(game.world.item_db)
        hp_ratio = actor.health / max(1, actor.total_max_hp(game.world.item_db))
        if consumables and hp_ratio <= 0.35 and random.random() < 0.60:
            return "item", consumables[0]
        if isinstance(actor, NPC) and actor.aggression < 35 and random.random() < 0.25:
            return "defend", None
        return "attack", None


class Character:
    EQUIPMENT_SLOTS = ("weapon", "armor", "charm")

    def __init__(
        self,
        name: str,
        base_stats: Stats,
        controller: Controller,
        *,
        location: str | None = None,
        gold: int = 0,
    ):
        self.name = name
        self.base_stats = base_stats
        self.controller = controller
        self.location = location
        self.health = base_stats.max_hp
        self.gold = gold
        self.inventory: list[str] = []
        self.equipment: dict[str, str | None] = {
            slot: None for slot in self.EQUIPMENT_SLOTS
        }

    def is_alive(self) -> bool:
        return self.health > 0

    def item_counts(self) -> Counter:
        return Counter(self.inventory)

    def has_item(self, item_id: str) -> bool:
        return item_id in self.inventory

    def has_items(self, item_ids: list[str]) -> bool:
        owned = self.item_counts()
        need = Counter(item_ids)
        return all(owned[item_id] >= count for item_id, count in need.items())

    def add_item(self, item_id: str) -> None:
        self.inventory.append(item_id)

    def add_items(self, item_ids: list[str]) -> None:
        for item_id in item_ids:
            self.add_item(item_id)

    def remove_item(self, item_id: str) -> bool:
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            for slot, equipped in self.equipment.items():
                if equipped == item_id:
                    self.equipment[slot] = None
            return True
        return False

    def remove_items(self, item_ids: list[str]) -> bool:
        if not self.has_items(item_ids):
            return False
        for item_id in item_ids:
            self.remove_item(item_id)
        return True

    def equipped_items(self, item_db: dict[str, Item]) -> list[Item]:
        return [
            item_db[item_id]
            for item_id in self.equipment.values()
            if item_id is not None
        ]

    def total_max_hp(self, item_db: dict[str, Item]) -> int:
        return self.base_stats.max_hp + sum(
            item.hp_bonus for item in self.equipped_items(item_db)
        )

    def total_defense(self, item_db: dict[str, Item]) -> int:
        return self.base_stats.defense + sum(
            item.defense_bonus for item in self.equipped_items(item_db)
        )

    def attack_range(self, item_db: dict[str, Item]) -> tuple[int, int]:
        bonus = sum(item.power_bonus for item in self.equipped_items(item_db))
        return self.base_stats.attack_min + bonus, self.base_stats.attack_max + bonus

    def roll_attack_damage(self, item_db: dict[str, Item]) -> int:
        low, high = self.attack_range(item_db)
        return random.randint(low, high)

    def take_damage(self, raw_damage: int, item_db: dict[str, Item]) -> int:
        actual = max(1, raw_damage - self.total_defense(item_db))
        self.health = max(0, self.health - actual)
        return actual

    def heal(self, amount: int, item_db: dict[str, Item]) -> int:
        before = self.health
        self.health = min(self.total_max_hp(item_db), self.health + amount)
        return self.health - before

    def clamp_health(self, item_db: dict[str, Item]) -> None:
        self.health = min(self.health, self.total_max_hp(item_db))

    def equippable_items(self, item_db: dict[str, Item]) -> list[str]:
        result = []
        seen = set()
        for item_id in self.inventory:
            if item_id in seen:
                continue
            seen.add(item_id)
            if item_db[item_id].slot in self.EQUIPMENT_SLOTS:
                result.append(item_id)
        return result

    def consumable_items(self, item_db: dict[str, Item]) -> list[str]:
        result = []
        seen = set()
        for item_id in self.inventory:
            if item_id in seen:
                continue
            seen.add(item_id)
            if item_db[item_id].healing > 0:
                result.append(item_id)
        return result

    def equip(self, item_id: str, item_db: dict[str, Item]) -> tuple[bool, str]:
        if item_id not in self.inventory:
            return False, f"{self.name} does not have that item."
        item = item_db[item_id]
        if item.slot not in self.EQUIPMENT_SLOTS:
            return False, f"{item.name} cannot be equipped."
        previous = self.equipment[item.slot]
        self.equipment[item.slot] = item_id
        self.clamp_health(item_db)
        if previous is None:
            return True, f"Equipped {item.name} in {item.slot} slot."
        return True, f"Equipped {item.name}, replacing {item_db[previous].name}."

    def unequip(self, slot: str, item_db: dict[str, Item]) -> tuple[bool, str]:
        if slot not in self.EQUIPMENT_SLOTS:
            return False, "Invalid equipment slot."
        current = self.equipment[slot]
        if current is None:
            return False, f"Nothing is equipped in {slot}."
        item_name = item_db[current].name
        self.equipment[slot] = None
        self.clamp_health(item_db)
        return True, f"Unequipped {item_name}."

    def use_consumable(
        self, item_id: str, item_db: dict[str, Item]
    ) -> tuple[bool, str, int]:
        if item_id not in self.inventory:
            return False, "Item not in inventory.", 0
        item = item_db[item_id]
        if item.healing <= 0:
            return False, f"{item.name} is not a consumable healing item.", 0
        self.remove_item(item_id)
        healed = self.heal(item.healing, item_db)
        return True, f"Used {item.name}.", healed

    def show_status(self, item_db: dict[str, Item], *, bounty: int = 0) -> None:
        low, high = self.attack_range(item_db)
        divider("STATUS")
        print(f"Name: {self.name}")
        print(f"Health: {self.health}/{self.total_max_hp(item_db)}")
        print(f"Attack: {low}-{high}")
        print(f"Defense: {self.total_defense(item_db)}")
        print(f"Gold: {self.gold}")
        print(f"Bounty: {bounty}")
        print("\nEquipment:")
        for slot in self.EQUIPMENT_SLOTS:
            item_id = self.equipment[slot]
            label = item_db[item_id].name if item_id is not None else "empty"
            print(f"- {slot}: {label}")
        print("\nInventory:")
        if not self.inventory:
            print("- empty")
        else:
            counts = Counter(self.inventory)
            seen = set()
            for item_id in self.inventory:
                if item_id in seen:
                    continue
                seen.add(item_id)
                suffix = f" x{counts[item_id]}" if counts[item_id] > 1 else ""
                print(f"- {item_db[item_id].name}{suffix}")


# ============================================================
# Shared NPC model
# ============================================================


class NPC(Character):
    def __init__(
        self,
        name: str,
        base_stats: Stats,
        *,
        description: str = "",
        tags: set[str] | None = None,
        aggression: int = 0,
        courage: int = 50,
        willingness_to_trade: int = 0,
        hostile: bool = False,
        dialogue_topics: list[DialogueTopic] | None = None,
        trade_offers: list[TradeOffer] | None = None,
        riddle: Riddle | None = None,
        surrender_at_ratio: float | None = None,
        surrender_lines: list[str] | None = None,
        surrender_trade_offers: list[TradeOffer] | None = None,
        peaceful_after_surrender: bool = True,
        surrender_accept_lines: list[str] | None = None,
        surrender_reject_lines: list[str] | None = None,
        surrender_accept_effect: Effect | None = None,
        defeat_lines: list[str] | None = None,
        reward_items: list[str] | None = None,
        reward_flags: set[str] | None = None,
        reward_gold: int = 0,
        persistent: bool = True,
        inventory: list[str] | None = None,
        equipment: dict[str, str | None] | None = None,
        gold: int = 0,
    ):
        super().__init__(
            name=name, base_stats=base_stats, controller=AIController(), gold=gold
        )
        self.description = description
        self.tags = tags or set()
        self.aggression = aggression
        self.courage = courage
        self.willingness_to_trade = willingness_to_trade
        self.hostile = hostile
        self.dialogue_topics = dialogue_topics or []
        self.trade_offers = trade_offers or []
        self.riddle = riddle
        self.surrender_at_ratio = surrender_at_ratio
        self.surrender_lines = surrender_lines or []
        self.surrender_trade_offers = surrender_trade_offers or []
        self.peaceful_after_surrender = peaceful_after_surrender
        self.surrender_accept_lines = surrender_accept_lines or []
        self.surrender_reject_lines = surrender_reject_lines or []
        self.surrender_accept_effect = surrender_accept_effect
        self.defeat_lines = defeat_lines or []
        self.reward_items = reward_items or []
        self.reward_flags = reward_flags or set()
        self.reward_gold = reward_gold
        self.persistent = persistent
        self.used_topics: set[str] = set()
        self.completed_trades: set[int] = set()
        self.surrendered = False
        self.riddle_solved = False
        self.defeated = False

        for item_id in inventory or []:
            self.add_item(item_id)
        if equipment:
            for slot, item_id in equipment.items():
                self.equipment[slot] = item_id

    def is_guard(self) -> bool:
        return "guard" in self.tags or "law" in self.tags

    def mood_label(self) -> str:
        if self.defeated:
            return "defeated"
        if self.surrendered:
            return "surrendered"
        if self.hostile:
            return "hostile"
        if self.willingness_to_trade >= 70:
            return "open to trade"
        if self.aggression >= 60:
            return "dangerous"
        return "neutral"

    def menu_text(self) -> str:
        return f"Approach {self.name}"

    def available_topics(self, game: Game) -> list[DialogueTopic]:
        results = []
        for topic in self.dialogue_topics:
            if topic.once and topic.key in self.used_topics:
                continue
            if not topic.required_flags.issubset(game.flags):
                continue
            if topic.blocked_flags.intersection(game.flags):
                continue
            if not game.player.has_items(topic.required_items):
                continue
            results.append(topic)
        return results

    def available_trade_offers(self, game: Game) -> list[tuple[int, TradeOffer]]:
        results = []
        for index, offer in enumerate(self.trade_offers):
            if not offer.repeatable and index in self.completed_trades:
                continue
            if not offer.required_flags.issubset(game.flags):
                continue
            if offer.blocked_flags.intersection(game.flags):
                continue
            if self.gold < offer.gives_gold:
                continue
            if not self.has_items(offer.gives_items):
                continue
            results.append((index, offer))
        return results

    def can_talk(self, game: Game) -> bool:
        return self.is_alive() and bool(self.available_topics(game))

    def can_trade(self, game: Game) -> bool:
        if not self.is_alive():
            return False
        if not self.available_trade_offers(game):
            return False
        if self.surrendered:
            return True
        return self.willingness_to_trade >= 30 and not self.hostile

    def can_riddle(self) -> bool:
        return self.is_alive() and self.riddle is not None and not self.riddle_solved

    def can_attack(self) -> bool:
        return self.is_alive()

    def can_loot(self) -> bool:
        return self.defeated and (bool(self.inventory) or self.gold > 0)

    def on_player_attack(self, game: Game) -> None:
        if not self.hostile and not self.defeated:
            if self.is_guard():
                ChangeBountyEffect(75, f"Assaulting guard {self.name}").apply(game)
            elif self.aggression < 50:
                ChangeBountyEffect(25, f"Assaulting {self.name}").apply(game)
        self.hostile = True
        self.aggression = max(self.aggression, 70)

    def maybe_surrender(self, game: Game) -> bool:
        if self.surrendered or self.surrender_at_ratio is None or not self.is_alive():
            return False
        ratio = self.health / max(1, self.total_max_hp(game.world.item_db))
        if ratio > self.surrender_at_ratio:
            return False
        self.surrendered = True
        if self.peaceful_after_surrender:
            self.hostile = False
        self.willingness_to_trade = max(self.willingness_to_trade, 80)
        self.trade_offers.extend(self.surrender_trade_offers)
        for line in self.surrender_lines:
            say(self.name, line)
        return True

    def will_accept_player_surrender(self, game: Game) -> bool:
        if self.defeated or not self.is_alive():
            return False
        if self.is_guard():
            return True
        if self.surrendered:
            return True
        return self.aggression < 90 or self.willingness_to_trade > 40

    def handle_player_surrender(self, game: Game) -> bool:
        if not self.will_accept_player_surrender(game):
            lines = self.surrender_reject_lines or ["No. This ends here."]
            for line in lines:
                say(self.name, line)
            self.hostile = True
            return False

        lines = self.surrender_accept_lines or ["Drop your guard and back away slowly."]
        for line in lines:
            say(self.name, line)

        self.hostile = False
        if self.surrender_accept_effect is not None:
            self.surrender_accept_effect.apply(game)
        else:
            if self.aggression >= 70:
                if game.player.gold > 0:
                    stolen = min(game.player.gold, max(5, game.player.gold // 2))
                    game.player.gold -= stolen
                    self.gold += stolen
                    print(f"{self.name} takes {stolen} gold from you.")
                elif game.player.inventory:
                    RemoveRandomItemEffect(text_prefix=f"{self.name} takes").apply(game)
            game.enter_mode("exploration")
        if game.mode == "combat":
            game.enter_mode("exploration")
        return True

    def on_defeat(self, game: Game) -> None:
        if self.defeated:
            return
        self.defeated = True
        self.hostile = False
        self.health = 0

        if self.surrendered:
            ChangeBountyEffect(100, f"Killing surrendering {self.name}").apply(game)
        elif self.is_guard():
            ChangeBountyEffect(150, f"Killing guard {self.name}").apply(game)
        elif self.aggression < 50:
            ChangeBountyEffect(40, f"Killing non-hostile {self.name}").apply(game)

        for line in self.defeat_lines:
            print(line)
        for item_id in self.reward_items:
            game.give_player_item(item_id)
        if self.reward_gold:
            game.player.gold += self.reward_gold
            print(f"You gain {self.reward_gold} gold.")
        for flag in self.reward_flags:
            game.flags.add(flag)
        game.world.on_npc_defeated(game, self)


class MerchantNPC(NPC):
    def __init__(self, name: str, base_stats: Stats | None = None, **kwargs):
        kwargs.setdefault("aggression", 10)
        kwargs.setdefault("courage", 40)
        kwargs.setdefault("willingness_to_trade", 90)
        kwargs.setdefault("hostile", False)
        super().__init__(
            name=name, base_stats=base_stats or Stats(35, 4, 6, 1), **kwargs
        )


class BanditNPC(NPC):
    def __init__(self, name: str, base_stats: Stats | None = None, **kwargs):
        kwargs.setdefault("aggression", 70)
        kwargs.setdefault("courage", 35)
        kwargs.setdefault("willingness_to_trade", 10)
        kwargs.setdefault("hostile", False)
        kwargs.setdefault("surrender_at_ratio", 0.25)
        super().__init__(
            name=name, base_stats=base_stats or Stats(28, 5, 9, 1), **kwargs
        )


class GuardianNPC(NPC):
    def __init__(self, name: str, base_stats: Stats | None = None, **kwargs):
        kwargs.setdefault("aggression", 50)
        kwargs.setdefault("courage", 90)
        kwargs.setdefault("willingness_to_trade", 0)
        kwargs.setdefault("hostile", False)
        super().__init__(
            name=name, base_stats=base_stats or Stats(38, 7, 11, 2), **kwargs
        )


class ElderNPC(NPC):
    def __init__(self, name: str, base_stats: Stats | None = None, **kwargs):
        kwargs.setdefault("aggression", 5)
        kwargs.setdefault("courage", 20)
        kwargs.setdefault("willingness_to_trade", 15)
        kwargs.setdefault("hostile", False)
        super().__init__(
            name=name, base_stats=base_stats or Stats(40, 4, 7, 0), **kwargs
        )


class GuardNPC(NPC):
    def __init__(self, name: str, base_stats: Stats | None = None, **kwargs):
        kwargs.setdefault("tags", {"guard", "law"})
        kwargs.setdefault("aggression", 40)
        kwargs.setdefault("courage", 85)
        kwargs.setdefault("willingness_to_trade", 0)
        kwargs.setdefault("hostile", False)
        super().__init__(
            name=name, base_stats=base_stats or Stats(45, 6, 9, 2), **kwargs
        )


# ============================================================
# Features / world objects
# ============================================================


class Feature:
    def __init__(self, name: str, verb: str = "Inspect"):
        self.name = name
        self.verb = verb

    def menu_text(self) -> str:
        return f"{self.verb} {self.name}"

    def interact(self, game: Game) -> None:
        print(f"Nothing happens when you interact with {self.name}.")


class TextFeature(Feature):
    def __init__(self, name: str, text: str, verb: str = "Inspect"):
        super().__init__(name=name, verb=verb)
        self.text = text

    def interact(self, game: Game) -> None:
        print("\n" + self.text)


class ScriptedFeature(Feature):
    def __init__(
        self,
        name: str,
        *,
        verb: str = "Use",
        required_flags: set[str] | None = None,
        blocked_text: str = "Nothing happens.",
        once_flag: str | None = None,
        first_effect: Effect | None = None,
        repeat_effect: Effect | None = None,
    ):
        super().__init__(name=name, verb=verb)
        self.required_flags = required_flags or set()
        self.blocked_text = blocked_text
        self.once_flag = once_flag
        self.first_effect = first_effect
        self.repeat_effect = repeat_effect

    def interact(self, game: Game) -> None:
        if not self.required_flags.issubset(game.flags):
            print(self.blocked_text)
            return
        if self.once_flag and self.once_flag in game.flags:
            if self.repeat_effect is not None:
                self.repeat_effect.apply(game)
            else:
                print("Nothing more happens.")
            return
        if self.first_effect is not None:
            self.first_effect.apply(game)
        if self.once_flag:
            game.flags.add(self.once_flag)
        if self.once_flag is None and self.repeat_effect is not None:
            self.repeat_effect.apply(game)


# ============================================================
# Encounters
# ============================================================


class EncounterRule:
    def __init__(
        self,
        name: str,
        *,
        locations: set[str],
        chance: float,
        handler: Callable[[Game], bool],
        required_flags: set[str] | None = None,
        blocked_flags: set[str] | None = None,
        once_flag: str | None = None,
        predicate: Callable[[Game], bool] | None = None,
    ):
        self.name = name
        self.locations = locations
        self.chance = chance
        self.handler = handler
        self.required_flags = required_flags or set()
        self.blocked_flags = blocked_flags or set()
        self.once_flag = once_flag
        self.predicate = predicate

    def try_trigger(self, game: Game) -> bool:
        location = game.current_location()
        if location.key not in self.locations:
            return False
        if self.once_flag and self.once_flag in game.flags:
            return False
        if not self.required_flags.issubset(game.flags):
            return False
        if self.blocked_flags.intersection(game.flags):
            return False
        if self.predicate is not None and not self.predicate(game):
            return False
        if random.random() > self.chance:
            return False
        triggered = self.handler(game)
        if triggered and self.once_flag:
            game.flags.add(self.once_flag)
        return triggered


# ============================================================
# World base class
# ============================================================


class World:
    def __init__(self, name: str):
        self.name = name
        self.locations: dict[str, Location] = {}
        self.item_db: dict[str, Item] = {}
        self.encounter_rules: list[EncounterRule] = []

    def define_item(self, item: Item) -> None:
        self.item_db[item.item_id] = item

    def item(self, item_id: str) -> Item:
        return self.item_db[item_id]

    def add_location(self, key: str, name: str, description: str) -> None:
        self.locations[key] = Location(key=key, name=name, description=description)

    def get(self, key: str) -> Location:
        return self.locations[key]

    def connect(
        self,
        source: str,
        direction: str,
        destination: str,
        *,
        requires_item: str | None = None,
        requires_flag: str | None = None,
        blocked: bool = False,
        blocked_text: str = "That path is blocked.",
        warning_text: str | None = None,
        on_attempt_effect: Effect | None = None,
        on_blocked_effect: Effect | None = None,
        on_success_effect: Effect | None = None,
    ) -> None:
        self.locations[source].exits.append(
            Exit(
                direction=direction,
                destination=destination,
                requires_item=requires_item,
                requires_flag=requires_flag,
                blocked=blocked,
                blocked_text=blocked_text,
                warning_text=warning_text,
                on_attempt_effect=on_attempt_effect,
                on_blocked_effect=on_blocked_effect,
                on_success_effect=on_success_effect,
            )
        )

    def connect_two_way(
        self, a: str, dir_a_to_b: str, b: str, dir_b_to_a: str, **kwargs
    ) -> None:
        self.connect(a, dir_a_to_b, b, **kwargs)
        self.connect(b, dir_b_to_a, a)

    def place_item(self, location_key: str, item_id: str) -> None:
        self.locations[location_key].items.append(item_id)

    def place_feature(self, location_key: str, feature: Feature) -> None:
        self.locations[location_key].features.append(feature)

    def place_npc(self, location_key: str, npc: NPC) -> None:
        npc.location = location_key
        self.locations[location_key].npcs.append(npc)

    def add_encounter_rule(self, rule: EncounterRule) -> None:
        self.encounter_rules.append(rule)

    def find_exit(self, location_key: str, direction: str) -> Exit | None:
        for exit_obj in self.locations[location_key].exits:
            if exit_obj.direction == direction:
                return exit_obj
        return None

    def block_path(self, location_key: str, direction: str, reason: str) -> None:
        exit_obj = self.find_exit(location_key, direction)
        if exit_obj is not None:
            exit_obj.blocked = True
            exit_obj.blocked_text = reason

    def unblock_path(self, location_key: str, direction: str) -> None:
        exit_obj = self.find_exit(location_key, direction)
        if exit_obj is not None:
            exit_obj.blocked = False

    def on_location_enter(self, game: Game, location: Location) -> None:
        pass

    def on_item_picked_up(self, game: Game, item_id: str) -> None:
        pass

    def on_npc_defeated(self, game: Game, npc: NPC) -> None:
        pass

    def try_start_of_exploration_encounter(self, game: Game) -> bool:
        for rule in self.encounter_rules:
            if rule.try_trigger(game):
                return True
        return False


# ============================================================
# Concrete world
# ============================================================


class DustVaultWorld(World):
    def __init__(self):
        super().__init__(name="Dust Vault")
        self.build_items()
        self.build_locations()
        self.build_paths()
        self.build_features()
        self.build_npcs()
        self.scatter_items()
        self.build_encounters()

    def build_items(self) -> None:
        self.define_item(
            Item(
                "utility_knife",
                "Utility Knife",
                "A serviceable field blade issued to disposable crew.",
                slot="weapon",
                power_bonus=1,
            )
        )
        self.define_item(
            Item(
                "spoofer",
                "Port Spoofer",
                "A handshake spoofer for old security panels.",
            )
        )
        self.define_item(
            Item(
                "payroll_shard",
                "Payroll Shard",
                "The encrypted payroll archive your crew was hired to steal.",
                set_flags_on_pickup={"has_payroll_shard"},
            )
        )
        self.define_item(
            Item(
                "survey_canister",
                "Survey Canister",
                "A sealed field canister tagged with a dead world survey code.",
            )
        )
        self.define_item(
            Item(
                "cutter_rifle",
                "Cutter Rifle",
                "A compact industrial carbine cut down for boarding work.",
                slot="weapon",
                power_bonus=5,
            )
        )
        self.define_item(
            Item(
                "pressure_weave",
                "Pressure Weave",
                "Layered expedition armor rated for thin air and stone spray.",
                slot="armor",
                defense_bonus=2,
                hp_bonus=12,
            )
        )
        self.define_item(
            Item(
                "claim_marker",
                "Claim Marker",
                "A brass marker used to stamp discovered ground as owned.",
                slot="charm",
                defense_bonus=1,
            )
        )
        self.define_item(
            Item(
                "line_spool",
                "Line Spool",
                "A powered anchor line for crossing broken industrial gaps.",
            )
        )
        self.define_item(
            Item(
                "coldlamp",
                "Cold Lamp",
                "A harsh white lamp that cuts through dust and dead tunnels.",
            )
        )
        self.define_item(
            Item(
                "locator_chart",
                "Locator Chart",
                "A triangulation chart recovered from an old survey mast.",
                set_flags_on_pickup={"found_locator"},
            )
        )
        self.define_item(
            Item(
                "vault_cipher",
                "Vault Cipher",
                "A drill-yard cipher rod keyed to the buried access seals.",
            )
        )
        self.define_item(
            Item(
                "grave_core",
                "Grave Core",
                "A dense, warm machine core that hums with buried authority.",
                set_flags_on_pickup={"has_grave_core"},
            )
        )
        self.define_item(
            Item(
                "med_patch",
                "Med Patch",
                "A quick seal patch full of painkillers and clotting foam.",
                healing=20,
                tags={"consumable"},
            )
        )
        self.define_item(
            Item(
                "stim_dose",
                "Stim Dose",
                "A stronger injector used when your hands start to shake.",
                healing=34,
                tags={"consumable"},
            )
        )

    def build_locations(self) -> None:
        self.add_location(
            "berth",
            "Ring Berth Three",
            "A freight berth on a tired transfer ring. Cargo nets sway over scarred deck plating while your crew pretends this is just another routine lift.",
        )
        self.add_location(
            "lounge",
            "Crew Cubicle",
            "A rented crew room with cracked lockers, stale coffee, and a table full of disposable mission tablets.",
        )
        self.add_location(
            "service",
            "Service Spine",
            "A narrow maintenance artery running behind customs walls and freight lifts.",
        )
        self.add_location(
            "annex",
            "Archive Access",
            "A pressure door, a dead camera cluster, and a security panel older than the station itself.",
        )
        self.add_location(
            "archive",
            "Black Archive",
            "A temperature-controlled records vault full of payroll wafers, claim ledgers, and sealed survey debris no one was meant to notice.",
        )
        self.add_location(
            "shuttle",
            "Extraction Pad",
            "A utility skiff waits on mag clamps beside a yawning lock and a view of black space.",
        )
        self.add_location(
            "brig",
            "Transit Brig",
            "A narrow holding box bolted beside the docking arms. It smells of coolant, bruises, and bad judgment.",
        )
        self.add_location(
            "survey_pad",
            "Survey Pad",
            "A prefab landing pad baked hard by years of dust. The horizon is all rock, wind, and abandoned equipment.",
        )
        self.add_location(
            "crash_gully",
            "Crash Gully",
            "A twisted escape coffin lies cracked open between stone ribs and drifting dust.",
        )
        self.add_location(
            "windbreak",
            "Windbreak Camp",
            "A lean-to camp built from survey panels and rover doors. Someone here survived by becoming harder than the planet.",
        )
        self.add_location(
            "relay",
            "Relay Ridge",
            "A ridge line crowned by a dead survey mast and snapped antenna spars.",
        )
        self.add_location(
            "habitat",
            "Habitat Shell",
            "An abandoned habitat ring slumps into the dust, half buried but still full of airless rooms and old voices.",
        )
        self.add_location(
            "pump",
            "Pump House",
            "A concrete utility bunker feeding ancient lines into the plateau. Its machinery knocks like a failing heart.",
        )
        self.add_location(
            "ravine",
            "Glass Ravine",
            "A cut of fused stone and brittle mineral sheets. Every step sounds like something ready to break.",
        )
        self.add_location(
            "drill",
            "Drill Site Theta",
            "A stripped drill yard surrounds a collapsed bore and a crane frozen mid-lift.",
        )
        self.add_location(
            "crater",
            "Burial Crater",
            "An excavation bowl ringed with abandoned charges and survey flags. Something was opened here and then hurriedly covered again.",
        )
        self.add_location(
            "gallery",
            "Lower Gallery",
            "Dust hangs unmoving in a buried machine corridor cut with geometric precision far older than the survey camp above.",
        )
        self.add_location(
            "vault",
            "Vault Heart",
            "A colossal chamber surrounds a suspended core cradle. The air is still, warm, and charged with old intent.",
        )

    def build_paths(self) -> None:
        self.connect_two_way("berth", "east", "lounge", "west")
        self.connect_two_way("lounge", "north", "service", "south")
        self.connect_two_way("service", "north", "annex", "south")
        self.connect_two_way("service", "east", "shuttle", "west")
        self.connect(
            "annex",
            "north",
            "archive",
            requires_flag="archive_opened",
            blocked_text="The archive door is deadlocked. You need to spoof the panel first.",
        )
        self.connect("archive", "south", "annex")

        self.connect_two_way("survey_pad", "south", "windbreak", "north")
        self.connect_two_way("crash_gully", "east", "windbreak", "west")
        self.connect_two_way("windbreak", "east", "habitat", "west")
        self.connect_two_way("windbreak", "west", "pump", "east")
        self.connect_two_way("windbreak", "north", "relay", "south")
        self.connect(
            "pump",
            "north",
            "ravine",
            requires_flag="bridge_powered",
            blocked_text="The access bridge has no power. The ravine is too wide to cross by foot.",
        )
        self.connect("ravine", "south", "pump")
        self.connect(
            "ravine",
            "east",
            "drill",
            requires_item="line_spool",
            blocked_text="The far side is reachable only with an anchor line.",
            warning_text="The glass shelves crack under every step. Cross anyway?",
            on_success_effect=ChanceEffect(
                0.35,
                CompositeEffect(
                    PrintEffect(
                        "The shelf snaps under you for half a breath before the line catches. Stone and glass rake your arms as you swing across."
                    ),
                    DamageCharacterEffect("player", 7),
                ),
                PrintEffect("You clip the line and cross the ravine without incident."),
            ),
        )
        self.connect("drill", "west", "ravine")
        self.connect(
            "habitat",
            "north",
            "crater",
            requires_flag="found_locator",
            requires_item="vault_cipher",
            blocked_text="Without the locator chart and a matching cipher, the crater is just another dead hole in the ground.",
        )
        self.connect("crater", "south", "habitat")
        self.connect(
            "crater",
            "down",
            "gallery",
            requires_item="coldlamp",
            blocked_text="The shaft below is lightless and deep. You need a proper lamp.",
        )
        self.connect("gallery", "up", "crater")
        self.connect_two_way("gallery", "north", "vault", "south")

    def build_features(self) -> None:
        self.place_feature(
            "lounge",
            ScriptedFeature(
                name="crew locker",
                verb="Search",
                once_flag="locker_searched",
                first_effect=CompositeEffect(
                    PrintEffect(
                        [
                            "You crack your own locker and take what should already have been issued.",
                            "The crew never spends good money on people they can replace.",
                        ]
                    ),
                    GivePlayerItemEffect("med_patch"),
                ),
                repeat_effect=PrintEffect(
                    "The locker is empty except for old meal wrappers."
                ),
            ),
        )
        self.place_feature(
            "annex",
            ScriptedFeature(
                name="security panel",
                verb="Spoof",
                required_flags={"act1_started"},
                blocked_text="You do not even have a job yet.",
                once_flag="archive_opened",
                first_effect=ConditionalEffect(
                    required_items=["spoofer"],
                    success_effect=CompositeEffect(
                        PrintEffect(
                            [
                                "You jack the spoofer into the old panel.",
                                "The archive lock chatters, hesitates, and finally rolls open.",
                            ]
                        ),
                        SetFlagEffect("archive_opened"),
                    ),
                    failure_effect=PrintEffect(
                        "You need the port spoofer Mina promised before this panel will do anything useful."
                    ),
                ),
                repeat_effect=PrintEffect("The archive lock is already hanging open."),
            ),
        )
        self.place_feature(
            "archive",
            ScriptedFeature(
                name="red locker",
                verb="Crack",
                required_flags={"archive_opened"},
                blocked_text="You should get inside the archive properly first.",
                once_flag="red_locker_hit",
                first_effect=CompositeEffect(
                    PrintEffect(
                        [
                            "You force the red locker and sweep the contents into your bag.",
                            "A silent trip wakes somewhere in the wall. You have what you wanted, but the job is no longer clean.",
                        ]
                    ),
                    GivePlayerItemEffect("survey_canister"),
                    ChangeGoldEffect(
                        12, reason="Loose station credit and bonded scrip"
                    ),
                    ChangeBountyEffect(45, "You tripped the archive side locker"),
                ),
                repeat_effect=PrintEffect("You already stripped the red locker."),
            ),
        )
        self.place_feature(
            "archive",
            ScriptedFeature(
                name="sealed terminal",
                verb="Read",
                once_flag="saw_suppressed_log",
                first_effect=PrintEffect(
                    [
                        "A suppressed log flashes up before the terminal wipes itself.",
                        "Survey World MV-241. Deep anomaly. All crew claims frozen. Site sealed by order of claims division.",
                        "Someone buried a find on this world and then buried the record of finding it.",
                    ]
                ),
                repeat_effect=PrintEffect(
                    "The terminal is blank now, but you still remember the world code."
                ),
            ),
        )
        self.place_feature(
            "shuttle",
            ScriptedFeature(
                name="extraction skiff",
                verb="Board",
                required_flags={"has_payroll_shard"},
                blocked_text="There is no point running for extraction before you have the payroll shard.",
                once_flag="left_station",
                first_effect=BranchOnBountyEffect(
                    clean_effect=CompositeEffect(
                        PrintEffect(
                            [
                                "Rafe checks the shard, studies you for a second, and almost smiles.",
                                "Clean lift. No alarms worth caring about. He promotes you on the spot and hands you a proper field assignment.",
                                "The side log from the archive mentioned a dead survey world. Rafe wants first rights to whatever was buried there, and now you are trusted enough to go look.",
                            ]
                        ),
                        GivePlayerItemEffect(
                            "cutter_rifle",
                            "pressure_weave",
                            "claim_marker",
                            "med_patch",
                        ),
                        ChangeGoldEffect(
                            18, reason="Promotion cut and expedition advance"
                        ),
                        SetBountyEffect(0),
                        SetFlagEffect("promoted", "act2_started", "heard_artifact_tip"),
                        MovePlayerEffect(
                            "survey_pad",
                            text="Hours later the skiff sets down on a survey pad under a hard white sky.",
                        ),
                    ),
                    hot_effect=CompositeEffect(
                        PrintEffect(
                            [
                                "Rafe clocks the heat before you even make the ramp.",
                                "He says nothing on the ride down to the surface. When the skiff drops through dust over the survey world, the crew shoves you into an emergency coffin with your knife and not much else.",
                                "You hit the ground alone. The skiff never comes back.",
                            ]
                        ),
                        SetBountyEffect(0),
                        SetFlagEffect("stranded", "act2_started", "heard_artifact_tip"),
                        DamageCharacterEffect("player", 12),
                        MovePlayerEffect(
                            "crash_gully",
                            text="You wake in broken fiberglass and dust on a world you were never meant to see.",
                        ),
                    ),
                ),
                repeat_effect=PrintEffect("The station is behind you now."),
            ),
        )
        self.place_feature(
            "brig",
            ScriptedFeature(
                name="brig bench",
                verb="Wait on",
                required_flags={"jailed"},
                blocked_text="No one is holding you here right now.",
                first_effect=CompositeEffect(
                    PrintEffect(
                        [
                            "You let the station clock grind away your temper.",
                            "Eventually a bored deputy vents you back toward the freight decks.",
                        ]
                    ),
                    SetBountyEffect(0),
                    ClearFlagEffect("jailed"),
                    MovePlayerEffect(
                        "berth", text="You are dumped back at Ring Berth Three."
                    ),
                    HealPlayerEffect(
                        999,
                        heal_text="Time and water do some repair.",
                        full_text="You are already steady enough.",
                    ),
                ),
            ),
        )
        self.place_feature(
            "windbreak",
            ScriptedFeature(
                name="field stove",
                verb="Rest at",
                first_effect=HealPlayerEffect(
                    18,
                    heal_text="You sit by the stove and let your hands stop shaking.",
                    full_text="You already feel as rested as this camp can make you.",
                ),
            ),
        )
        self.place_feature(
            "relay",
            ScriptedFeature(
                name="survey mast",
                verb="Align",
                once_flag="relay_aligned",
                first_effect=CompositeEffect(
                    PrintEffect(
                        [
                            "You wrestle the dead mast into one last sweep.",
                            "A locator chart spills across the cracked screen, along with a lamp cached for emergency descent work.",
                        ]
                    ),
                    GivePlayerItemEffect("locator_chart", "coldlamp"),
                ),
                repeat_effect=PrintEffect(
                    "The mast has already given you everything it had left."
                ),
            ),
        )
        self.place_feature(
            "pump",
            ScriptedFeature(
                name="bridge control",
                verb="Start",
                once_flag="bridge_powered",
                first_effect=CompositeEffect(
                    PrintEffect(
                        [
                            "You kick the old pumps awake and route power into the ravine bridge.",
                            "Somewhere out in the dust, metal begins to move again.",
                        ]
                    ),
                    SetFlagEffect("bridge_powered"),
                ),
                repeat_effect=PrintEffect("The bridge control is already humming."),
            ),
        )
        self.place_feature(
            "habitat",
            ScriptedFeature(
                name="archive uplink",
                verb="Broadcast through",
                required_flags={"has_grave_core", "truth_known"},
                blocked_text="Without the grave core and the truth of what this place is, the uplink is just a dead frame.",
                once_flag="ending_broadcast",
                first_effect=EndGameEffect(
                    [
                        "You wire the grave core into the habitat uplink and flood every claims relay you can reach with the buried archive.",
                        "By dawn the planet is no longer a rumor. It is evidence, territory, scandal, and war all at once.",
                        "The company cannot bury the find again, but the people still living here will now endure the kind of attention that kills more slowly than a bullet.",
                        "Ending: Broadcast the truth.",
                    ],
                    "ending_broadcast",
                    "game_won",
                ),
                repeat_effect=PrintEffect(
                    "The uplink is already screaming the truth into the void."
                ),
            ),
        )
        self.place_feature(
            "crater",
            ScriptedFeature(
                name="collapse charges",
                verb="Arm",
                required_flags={"has_grave_core"},
                blocked_text="You would only do that if you had already taken the core.",
                once_flag="ending_bury",
                first_effect=EndGameEffect(
                    [
                        "You sink the grave core into the old charge well and trigger the crater collapse.",
                        "Stone folds in on the shaft. The vault, the machine records, and the promise of profit vanish under a landslide of dust and bad luck.",
                        "No one gets rich. No one learns enough. The planet goes back to keeping its own counsel.",
                        "Ending: Bury it again.",
                    ],
                    "ending_bury",
                    "game_won",
                ),
                repeat_effect=PrintEffect("The crater is already coming down."),
            ),
        )
        self.place_feature(
            "windbreak",
            ScriptedFeature(
                name="landing beacon",
                verb="Answer",
                required_flags={"has_grave_core", "rafe_offer_heard"},
                blocked_text="No one is waiting for your answer yet.",
                once_flag="ending_corporate",
                first_effect=EndGameEffect(
                    [
                        "You answer Rafe's beacon and hand over the grave core for extraction, pay, and a promised place higher up the chain.",
                        "Within weeks the survey world is fenced, drilled, and stripped. Everyone who helped you is bought off, pushed out, or buried under paperwork and private security.",
                        "You got exactly what a successful heist is supposed to buy: a future. It just was not a future anyone else here got to share.",
                        "Ending: Sell the vault.",
                    ],
                    "ending_corporate",
                    "game_won",
                ),
                repeat_effect=PrintEffect("The beacon has already done its work."),
            ),
        )

    def build_npcs(self) -> None:
        self.place_npc(
            "lounge",
            NPC(
                name="Rafe Mercer",
                base_stats=Stats(34, 5, 8, 1),
                description="Crew lead, well dressed for a thief, and always measuring people by how much noise they make.",
                aggression=25,
                courage=60,
                willingness_to_trade=0,
                hostile=False,
                dialogue_topics=[
                    DialogueTopic(
                        key="job_pitch",
                        title="Ask about the job",
                        lines=[
                            "Simple lift. Payroll shard out of a dead annex, no bodies, no heroics.",
                            "Do it clean and I stop calling you the new hand.",
                        ],
                        blocked_flags={"act1_started"},
                        once=True,
                        outcome_effect=CompositeEffect(
                            GivePlayerItemEffect("spoofer"),
                            SetFlagEffect("act1_started"),
                        ),
                    ),
                    DialogueTopic(
                        key="after_start",
                        title="Ask what comes after the lift",
                        lines=[
                            "If the shard sells, we eat well. If the side archive log is real, we might eat for a year.",
                            "Dead survey worlds hide expensive mistakes.",
                        ],
                        required_flags={"act1_started"},
                        blocked_flags={"act2_started"},
                    ),
                ],
                inventory=["med_patch"],
                gold=10,
            ),
        )
        self.place_npc(
            "lounge",
            NPC(
                name="Mina Voss",
                base_stats=Stats(28, 4, 7, 0),
                description="The slicer on the crew. Her tools are neat, her hands are not.",
                aggression=5,
                courage=35,
                willingness_to_trade=20,
                hostile=False,
                dialogue_topics=[
                    DialogueTopic(
                        key="mina_advice",
                        title="Ask for advice",
                        lines=[
                            "The panel at archive access still speaks antique station. Use the spoofer and do not get curious about the red locker.",
                            "Curiosity is how cheap jobs become hard ones.",
                        ],
                    ),
                    DialogueTopic(
                        key="mina_patch",
                        title="Ask if she has anything useful",
                        lines=["Take this patch and stop leaking on the consoles."],
                        blocked_flags={"mina_helped"},
                        once=True,
                        outcome_effect=CompositeEffect(
                            GivePlayerItemEffect("med_patch"),
                            SetFlagEffect("mina_helped"),
                        ),
                    ),
                ],
            ),
        )
        self.place_npc(
            "annex",
            GuardNPC(
                "Marshal Sorn",
                description="A station marshal posted to a job too quiet to stay honest for long.",
                dialogue_topics=[
                    DialogueTopic(
                        key="marshal_bluff",
                        title="Ask who still uses this annex",
                        lines=[
                            "Claims division, when it wants something forgotten instead of processed.",
                            "That should tell you enough to turn around.",
                        ],
                    )
                ],
                surrender_accept_lines=[
                    "Down. Hands where I can see them.",
                    "You can try again after you cool off in the brig.",
                ],
                surrender_accept_effect=CompositeEffect(
                    SetFlagEffect("jailed"),
                    SetBountyEffect(0),
                    MovePlayerEffect(
                        "brig",
                        text="Marshal Sorn knocks the fight out of you and drops you in the transit brig.",
                    ),
                ),
                inventory=["pressure_weave", "med_patch"],
                equipment={"armor": "pressure_weave"},
                gold=15,
            ),
        )
        self.place_npc(
            "windbreak",
            MerchantNPC(
                "Orla Quist",
                description="A scavenger-mechanic who has made a life out of dead survey hardware and careful distrust.",
                dialogue_topics=[
                    DialogueTopic(
                        key="orla_intro",
                        title="Ask how she survived here",
                        lines=[
                            "By staying useful and never standing where companies last saw me.",
                            "This world eats plans. Learn to travel with spares.",
                        ],
                    ),
                    DialogueTopic(
                        key="orla_tip",
                        title="Ask about the buried site",
                        lines=[
                            "People came here for ore and left whispering about a hollow under the plateau.",
                            "Whatever they found, claims division buried the hole and the workers with the paperwork.",
                        ],
                        required_flags={"act2_started"},
                    ),
                ],
                trade_offers=[
                    TradeOffer(
                        title="Buy Line Spool for 5 gold",
                        wants_gold=5,
                        gives_items=["line_spool"],
                    ),
                    TradeOffer(
                        title="Buy Med Patch for 6 gold",
                        wants_gold=6,
                        gives_items=["med_patch"],
                        repeatable=True,
                    ),
                    TradeOffer(
                        title="Buy Stim Dose for 11 gold",
                        wants_gold=11,
                        gives_items=["stim_dose"],
                        repeatable=True,
                    ),
                ],
                inventory=["line_spool", "med_patch", "med_patch", "stim_dose"],
                gold=40,
            ),
        )
        self.place_npc(
            "habitat",
            ElderNPC(
                "Juno Hale",
                description="A former survey geologist who stayed when the company wrote the planet off. Dust has taken the softness out of her voice, not the memory.",
                dialogue_topics=[
                    DialogueTopic(
                        key="juno_planet",
                        title="Ask what the survey team found",
                        lines=[
                            "Not ore. Not a ruin exactly. A machine complex sealed under the plateau like the world had grown around it.",
                            "Claims division froze the reports, killed the dig, and told us to forget where we had drilled.",
                        ],
                        blocked_flags={"truth_known"},
                        once=True,
                        outcome_effect=SetFlagEffect("truth_known"),
                    ),
                    DialogueTopic(
                        key="juno_canister",
                        title="Show the survey canister",
                        lines=[
                            "I remember this casing. It held the first field core they pulled out before they resealed the shaft.",
                            "The artifact is not the prize. It is the key they used to wake the rest of the place.",
                        ],
                        required_items=["survey_canister"],
                        blocked_flags={"canister_discussed"},
                        once=True,
                        outcome_effect=SetFlagEffect(
                            "truth_known", "canister_discussed"
                        ),
                    ),
                    DialogueTopic(
                        key="juno_end",
                        title="Ask what to do with the grave core",
                        lines=[
                            "If you hand it back to the kind of people who bury worlds, they will own this place before the dust settles.",
                            "If you show everyone what it is, the lies stop, but the scramble begins. Frontier truth is expensive that way.",
                        ],
                        required_flags={"has_grave_core"},
                    ),
                ],
                inventory=["med_patch"],
                gold=5,
            ),
        )
        self.place_npc(
            "drill",
            BanditNPC(
                "Cade Voss",
                description="A rival salvage runner stripping the drill yard for anything portable and profitable.",
                dialogue_topics=[
                    DialogueTopic(
                        key="cade_claim",
                        title="Ask what he found here",
                        lines=[
                            "A cipher rod, a dead crane, and proof that everyone on this rock is late to somebody else's score.",
                            "You want the rod, bring money or bring blood.",
                        ],
                    )
                ],
                trade_offers=[
                    TradeOffer(
                        title="Buy Vault Cipher for 12 gold",
                        wants_gold=12,
                        gives_items=["vault_cipher"],
                    )
                ],
                surrender_lines=[
                    "All right. Enough. I am not dying for a cipher rod.",
                    "Take the rod or trade for it. I am done bleeding over survey junk.",
                ],
                surrender_trade_offers=[
                    TradeOffer(
                        title="Take Vault Cipher for 5 gold",
                        wants_gold=5,
                        gives_items=["vault_cipher"],
                    )
                ],
                inventory=["vault_cipher", "med_patch"],
                equipment={"weapon": "utility_knife"},
                gold=18,
                reward_gold=8,
            ),
        )
        self.place_npc(
            "vault",
            GuardianNPC(
                "Custodian Echo",
                description="A voice distributed through the chamber, speaking from nowhere human-sized.",
                dialogue_topics=[
                    DialogueTopic(
                        key="echo_warning",
                        title="Ask what this place is",
                        lines=[
                            "A registry of deep claims and deeper dead. A vault built to remember extraction long after extractors were gone.",
                            "Your kind returns to every grave with scales and flags.",
                        ],
                        blocked_flags={"custodian_cleared"},
                    ),
                    DialogueTopic(
                        key="echo_after",
                        title="Ask what the grave core does",
                        lines=[
                            "It names ownership, wakes dormant routes, and proves this world was catalogued before your survey ships were born.",
                            "In smaller hands it is a key. In larger hands it becomes a deed.",
                        ],
                        required_flags={"custodian_cleared"},
                    ),
                ],
                riddle=Riddle(
                    intro_lines=[
                        "Answer plainly. What comes before every stolen claim?"
                    ],
                    question="What is the first tool of every claim jumper?",
                    answers=["lie", "a lie", "lies"],
                    success_lines=["Correct. Your species teaches that lesson early."],
                    failure_lines=["No. The blade comes later."],
                    damage_on_failure=10,
                    set_flags_on_success={"custodian_cleared"},
                    repeat_lines=[
                        "The chamber has judged you already. Take what you came for."
                    ],
                ),
                inventory=["grave_core", "stim_dose"],
                defeat_lines=[
                    "The chamber voice fractures into a thousand quiet tones and finally falls still."
                ],
                reward_flags={"custodian_cleared"},
                reward_gold=0,
            ),
        )

    def scatter_items(self) -> None:
        self.place_item("archive", "payroll_shard")
        self.place_item("survey_pad", "med_patch")
        self.place_item("crash_gully", "med_patch")
        self.place_item("pump", "med_patch")
        self.place_item("habitat", "claim_marker")

    def build_encounters(self) -> None:
        self.add_encounter_rule(
            EncounterRule(
                "service_patrol",
                locations={"service", "annex", "shuttle"},
                chance=1.0,
                required_flags={"act1_started"},
                blocked_flags={"act2_started", "patrol_drone_seen"},
                predicate=lambda game: game.bounty > 0,
                handler=self.handle_station_patrol,
                once_flag="patrol_drone_seen",
            )
        )
        self.add_encounter_rule(
            EncounterRule(
                "glass_maw",
                locations={"ravine"},
                chance=0.30,
                blocked_flags={"act3_started"},
                predicate=lambda game: game.player.is_alive(),
                handler=self.handle_glass_maw,
            )
        )
        self.add_encounter_rule(
            EncounterRule(
                "rafe_offer",
                locations={"windbreak", "crater"},
                chance=1.0,
                required_flags={"has_grave_core"},
                blocked_flags={"rafe_offer_heard", "game_won"},
                handler=self.handle_rafe_offer,
                once_flag="rafe_offer_heard",
            )
        )

    def handle_station_patrol(self, game: Game) -> bool:
        drone = NPC(
            name="Patrol Drone",
            base_stats=Stats(max_hp=18, attack_min=4, attack_max=7, defense=1),
            description="A station patrol drone skims out of a wall cradle with your heat profile already painted red.",
            tags={"law", "drone", "encounter"},
            aggression=85,
            courage=100,
            willingness_to_trade=0,
            hostile=True,
            persistent=False,
            surrender_reject_lines=["The drone's warning klaxon only rises in pitch."],
            defeat_lines=[
                "The patrol drone tumbles across the deck, sparks bleeding from its lens."
            ],
            reward_gold=6,
        )
        action_separator("A station patrol wakes")
        print(
            "A patrol drone finds your trail and sweeps the corridor with a stunner arc."
        )
        game.enter_mode("combat", npc=drone)
        return True

    def handle_glass_maw(self, game: Game) -> bool:
        beast = NPC(
            name="Glass Maw",
            base_stats=Stats(max_hp=20, attack_min=5, attack_max=8, defense=1),
            description="A low-slung dust predator lunges out from beneath the fused shelves.",
            tags={"beast", "encounter"},
            aggression=90,
            courage=40,
            willingness_to_trade=0,
            hostile=True,
            persistent=False,
            surrender_reject_lines=[
                "It only scrapes its teeth across the stone and comes on."
            ],
            defeat_lines=[
                "The glass maw shudders once and slides back into stillness."
            ],
            reward_gold=7,
        )
        action_separator("Something moves in the ravine")
        print(
            "A dust predator erupts from the mineral shelves and cuts off your retreat."
        )
        game.enter_mode("combat", npc=beast)
        return True

    def handle_rafe_offer(self, game: Game) -> bool:
        action_separator("An incoming signal")
        print(
            "Rafe's cutter hails you from above the plateau. He knows you made it inside, and now he wants the grave core brought to the landing beacon for payment and extraction."
        )
        game.flags.add("act3_started")
        return False

    def on_item_picked_up(self, game: Game, item_id: str) -> None:
        if item_id == "grave_core":
            game.flags.add("act3_started")
        if item_id == "payroll_shard":
            game.flags.add("has_payroll_shard")

    def on_location_enter(self, game: Game, location: Location) -> None:
        if location.key == "survey_pad" and "survey_pad_intro" not in game.flags:
            game.flags.add("survey_pad_intro")
            print(
                "The survey world is all hard light and harder silence. If there is an artifact here, the company buried it where only desperate people would keep digging."
            )
        if location.key == "crash_gully" and "crash_gully_intro" not in game.flags:
            game.flags.add("crash_gully_intro")
            print(
                "Your crew is gone. The planet is not. Somewhere out under all this dust is the same buried thing they were willing to strand you over."
            )
        if location.key == "vault" and "vault_intro" not in game.flags:
            game.flags.add("vault_intro")
            print(
                "The buried chamber is too large to have been built for one drill team or one claim. Whatever this place was, frontier companies only found its grave, not its beginning."
            )


# ============================================================
# Engines
# ============================================================


class Engine:
    def run(self, game: Game) -> None:
        raise NotImplementedError


class ExplorationEngine(Engine):
    def run(self, game: Game) -> None:
        if game.world.try_start_of_exploration_encounter(game):
            return

        location = game.current_location()
        divider(f"{game.world.name} - {location.name}")
        print(location.description)
        print(
            f"\n[HP {game.player.health}/{game.player.total_max_hp(game.world.item_db)}] [Gold {game.player.gold}] [Bounty {game.bounty}]"
        )

        if location.items:
            print("\nItems here:")
            for item_id in location.items:
                print(f"- {game.item_name(item_id)}")

        if location.npcs:
            print("\nPeople / creatures here:")
            for npc in location.npcs:
                print(f"- {npc.name} ({npc.mood_label()})")

        if location.features:
            print("\nNotable features:")
            for feature in location.features:
                print(f"- {feature.name}")

        game.show_goal()

        choices = []
        jailed = "jailed" in game.flags and location.key == "jail"
        if not jailed:
            for exit_obj in location.exits:
                destination = game.world.get(exit_obj.destination)
                text = f"Go {exit_obj.direction} to {destination.name}"
                if game.exit_is_blocked(exit_obj):
                    text += " [blocked]"
                elif exit_obj.warning_text:
                    text += " [risky]"
                choices.append({"kind": "move", "text": text, "value": exit_obj})

            for item_id in location.items:
                choices.append(
                    {
                        "kind": "take_item",
                        "text": f"Take {game.item_name(item_id)}",
                        "value": item_id,
                    }
                )

            for npc in location.npcs:
                choices.append({"kind": "npc", "text": npc.menu_text(), "value": npc})

        for feature in location.features:
            choices.append(
                {"kind": "feature", "text": feature.menu_text(), "value": feature}
            )

        if not jailed:
            choices.append({"kind": "menu", "text": "Open menu", "value": None})

        choice = game.choose(choices, prompt="\nWhat do you want to do? ")

        if choice["kind"] == "move":
            game.handle_move(choice["value"])
        elif choice["kind"] == "take_item":
            game.handle_take_item(choice["value"])
        elif choice["kind"] == "npc":
            game.enter_mode("npc", npc=choice["value"])
        elif choice["kind"] == "feature":
            choice["value"].interact(game)
        elif choice["kind"] == "menu":
            game.enter_mode("menu")


class NPCInteractionEngine(Engine):
    def run(self, game: Game) -> None:
        npc: NPC = game.context["npc"]

        divider(f"Interacting with {npc.name}")
        print(npc.description)
        print(f"Mood: {npc.mood_label()}")
        print(f"Health: {npc.health}/{npc.total_max_hp(game.world.item_db)}")
        print(f"Gold: {npc.gold}")

        options = []
        if npc.can_talk(game):
            options.append(
                {"kind": "talk", "text": f"Talk to {npc.name}", "value": npc}
            )
        if npc.can_trade(game):
            options.append(
                {"kind": "trade", "text": f"Trade with {npc.name}", "value": npc}
            )
        if npc.can_riddle():
            options.append(
                {"kind": "riddle", "text": f"Challenge {npc.name}", "value": npc}
            )
        if npc.can_attack():
            options.append(
                {"kind": "attack", "text": f"Attack {npc.name}", "value": npc}
            )
        if npc.can_loot():
            options.append({"kind": "loot", "text": f"Loot {npc.name}", "value": npc})
        options.append({"kind": "back", "text": "Step away", "value": None})

        choice = game.choose(options, prompt="\nChoose an interaction: ")
        kind = choice["kind"]
        if kind == "talk":
            game.enter_mode("dialogue", npc=npc)
        elif kind == "trade":
            game.enter_mode("trade", npc=npc)
        elif kind == "riddle":
            game.enter_mode("riddle", npc=npc)
        elif kind == "attack":
            npc.on_player_attack(game)
            game.enter_mode("combat", npc=npc)
        elif kind == "loot":
            game.loot_npc(npc)
            game.enter_mode("npc", npc=npc)
        elif kind == "back":
            game.enter_mode("exploration")


class DialogueEngine(Engine):
    def run(self, game: Game) -> None:
        npc: NPC = game.context["npc"]
        topics = npc.available_topics(game)
        if not topics:
            say(npc.name, "I have nothing more to say right now.")
            game.enter_mode("npc", npc=npc)
            return

        divider(f"Dialogue - {npc.name}")
        options = [
            {"kind": "topic", "text": topic.title, "value": topic} for topic in topics
        ]
        options.append({"kind": "back", "text": "Back", "value": None})
        choice = game.choose(options, prompt="\nChoose a topic: ")
        if choice["kind"] == "back":
            game.enter_mode("npc", npc=npc)
            return

        topic: DialogueTopic = choice["value"]
        for line in topic.lines:
            say(npc.name, line)
        if topic.outcome_effect is not None:
            topic.outcome_effect.apply(game)
        if topic.once:
            npc.used_topics.add(topic.key)
        if "game_won" in game.flags:
            game.running = False
            return
        game.enter_mode("npc", npc=npc)


class TradeEngine(Engine):
    def run(self, game: Game) -> None:
        npc: NPC = game.context["npc"]
        offers = npc.available_trade_offers(game)
        divider(f"Trade - {npc.name}")
        print(f"Your gold: {game.player.gold}")
        if not offers:
            say(npc.name, "I have nothing I can trade right now.")
            game.enter_mode("npc", npc=npc)
            return

        options = []
        for offer_index, offer in offers:
            wants_parts = []
            if offer.wants_gold:
                wants_parts.append(f"{offer.wants_gold} gold")
            if offer.wants_items:
                wants_parts.extend(
                    game.item_name(item_id) for item_id in offer.wants_items
                )
            gives_parts = []
            if offer.gives_gold:
                gives_parts.append(f"{offer.gives_gold} gold")
            if offer.gives_items:
                gives_parts.extend(
                    game.item_name(item_id) for item_id in offer.gives_items
                )
            wants = ", ".join(wants_parts) or "nothing"
            gives = ", ".join(gives_parts) or "nothing"
            options.append(
                {
                    "kind": "offer",
                    "text": f"{offer.title} [{wants} -> {gives}]",
                    "value": (offer_index, offer),
                }
            )
        options.append({"kind": "back", "text": "Back", "value": None})

        choice = game.choose(options, prompt="\nChoose a trade: ")
        if choice["kind"] == "back":
            game.enter_mode("npc", npc=npc)
            return

        offer_index, offer = choice["value"]
        if game.player.gold < offer.wants_gold:
            say(npc.name, f"Come back when you have {offer.wants_gold} gold.")
            game.enter_mode("npc", npc=npc)
            return
        if not game.player.has_items(offer.wants_items):
            say(
                npc.name,
                f"Come back when you have: {', '.join(game.item_name(i) for i in offer.wants_items)}.",
            )
            game.enter_mode("npc", npc=npc)
            return
        if npc.gold < offer.gives_gold or not npc.has_items(offer.gives_items):
            say(npc.name, "I cannot complete that trade right now.")
            game.enter_mode("npc", npc=npc)
            return

        game.player.gold -= offer.wants_gold
        npc.gold += offer.wants_gold
        npc.gold -= offer.gives_gold
        game.player.gold += offer.gives_gold
        game.player.remove_items(offer.wants_items)
        npc.add_items(offer.wants_items)
        npc.remove_items(offer.gives_items)
        for item_id in offer.gives_items:
            game.give_player_item(item_id)
        if not offer.repeatable:
            npc.completed_trades.add(offer_index)
        say(npc.name, "A fair trade.")
        game.enter_mode("npc", npc=npc)


class RiddleEngine(Engine):
    def run(self, game: Game) -> None:
        npc: NPC = game.context["npc"]
        riddle = npc.riddle
        if riddle is None:
            game.enter_mode("npc", npc=npc)
            return

        divider(f"Challenge - {npc.name}")
        if npc.riddle_solved:
            for line in riddle.repeat_lines:
                say(npc.name, line)
            game.enter_mode("npc", npc=npc)
            return

        for line in riddle.intro_lines:
            say(npc.name, line)
        say(npc.name, riddle.question)
        answer = input("Your answer: ").strip().lower()

        if answer in [a.lower() for a in riddle.answers]:
            for line in riddle.success_lines:
                say(npc.name, line)
            npc.riddle_solved = True
            for flag in riddle.set_flags_on_success:
                game.flags.add(flag)
        else:
            for line in riddle.failure_lines:
                say(npc.name, line)
            if riddle.damage_on_failure > 0:
                actual = game.player.take_damage(
                    riddle.damage_on_failure, game.world.item_db
                )
                print(f"You take {actual} damage.")

        game.enter_mode("npc", npc=npc)


class CombatEngine(Engine):
    def run(self, game: Game) -> None:
        enemy: NPC = game.context["npc"]
        player_defending = False
        enemy_defending = False

        divider(f"Combat - {enemy.name}")
        print(f"{enemy.name} squares off against you.")

        while (
            game.running
            and game.player.is_alive()
            and enemy.is_alive()
            and enemy.hostile
        ):
            print("\n--- Combat Round ---")
            print(
                f"Your HP: {game.player.health}/{game.player.total_max_hp(game.world.item_db)}"
            )
            print(
                f"{enemy.name} HP: {enemy.health}/{enemy.total_max_hp(game.world.item_db)}"
            )
            print(f"Your gold: {game.player.gold} | Their gold: {enemy.gold}")

            action, payload = game.player.controller.choose_combat_action(
                game, game.player, enemy
            )
            if action == "none":
                continue

            if action == "attack":
                raw = game.player.roll_attack_damage(game.world.item_db)
                if enemy_defending:
                    raw = max(1, raw // 2)
                    enemy_defending = False
                actual = enemy.take_damage(raw, game.world.item_db)
                print(f"You hit {enemy.name} for {actual} damage.")

                if enemy.maybe_surrender(game):
                    if enemy.name == "Bandit Nox":
                        game.flags.add("bandit_spared")
                    if game.resolve_enemy_surrender(enemy):
                        return

                if not enemy.is_alive():
                    enemy.on_defeat(game)
                    if enemy.persistent:
                        game.enter_mode("npc", npc=enemy)
                    else:
                        game.enter_mode("exploration")
                    return

            elif action == "defend":
                player_defending = True
                print("You brace for the next attack.")

            elif action == "item":
                ok, message, healed = game.player.use_consumable(
                    payload, game.world.item_db
                )
                if ok:
                    print(f"{message} Restored {healed} HP.")
                else:
                    print(message)
                    continue

            elif action == "run":
                if random.random() < 0.5:
                    print("You escape successfully!")
                    enemy.hostile = False if enemy.surrendered else enemy.hostile
                    game.enter_mode("exploration")
                    return
                print("You try to run, but the enemy cuts you off!")

            elif action == "surrender":
                if enemy.handle_player_surrender(game):
                    return
                continue

            if enemy.is_alive() and enemy.hostile:
                enemy_action, enemy_payload = enemy.controller.choose_combat_action(
                    game, enemy, game.player
                )
                if enemy_action == "item" and enemy_payload is not None:
                    ok, msg, healed = enemy.use_consumable(
                        enemy_payload, game.world.item_db
                    )
                    if ok:
                        print(
                            f"{enemy.name} uses {game.item_name(enemy_payload)} and heals {healed} HP."
                        )
                elif enemy_action == "defend":
                    enemy_defending = True
                    print(f"{enemy.name} takes a guarded stance.")
                else:
                    raw = enemy.roll_attack_damage(game.world.item_db)
                    if player_defending:
                        raw = max(1, raw // 2)
                        player_defending = False
                    actual = game.player.take_damage(raw, game.world.item_db)
                    print(f"{enemy.name} hits you for {actual} damage.")
                if not game.player.is_alive():
                    return

        if enemy.persistent:
            game.enter_mode("npc", npc=enemy)
        else:
            game.enter_mode("exploration")


class MenuEngine(Engine):
    def run(self, game: Game) -> None:
        divider("MENU")
        options = [
            {"kind": "status", "text": "View status", "value": None},
            {"kind": "loadout", "text": "Manage loadout", "value": None},
            {"kind": "journal", "text": "View world flags / journal", "value": None},
            {"kind": "back", "text": "Return to exploration", "value": None},
            {"kind": "quit", "text": "Quit game", "value": None},
        ]
        choice = game.choose(options, prompt="Choose a menu option: ")
        if choice["kind"] == "status":
            game.player.show_status(game.world.item_db, bounty=game.bounty)
            game.enter_mode("menu")
        elif choice["kind"] == "loadout":
            game.enter_mode("loadout")
        elif choice["kind"] == "journal":
            game.show_journal()
            game.enter_mode("menu")
        elif choice["kind"] == "back":
            game.enter_mode("exploration")
        elif choice["kind"] == "quit":
            print("Thanks for playing!")
            game.running = False


class LoadoutEngine(Engine):
    def run(self, game: Game) -> None:
        divider("LOADOUT")
        player = game.player
        item_db = game.world.item_db

        print("Current equipment:")
        for slot in player.EQUIPMENT_SLOTS:
            item_id = player.equipment[slot]
            label = game.item_name(item_id) if item_id is not None else "empty"
            print(f"- {slot}: {label}")

        options = []
        for item_id in player.equippable_items(item_db):
            item = item_db[item_id]
            options.append(
                {
                    "kind": "equip",
                    "text": f"Equip {item.name} ({item.slot})",
                    "value": item_id,
                }
            )
        for slot in player.EQUIPMENT_SLOTS:
            if player.equipment[slot] is not None:
                options.append(
                    {"kind": "unequip", "text": f"Unequip {slot}", "value": slot}
                )
        options.append({"kind": "back", "text": "Back", "value": None})

        choice = game.choose(options, prompt="Choose a loadout action: ")
        if choice["kind"] == "equip":
            ok, message = player.equip(choice["value"], item_db)
            print(message)
            game.enter_mode("loadout")
        elif choice["kind"] == "unequip":
            ok, message = player.unequip(choice["value"], item_db)
            print(message)
            game.enter_mode("loadout")
        elif choice["kind"] == "back":
            game.enter_mode("menu")


# ============================================================
# Game director / router
# ============================================================


class Game:
    def __init__(self, player_name: str = "Tav", world: World | None = None):
        self.world = world or DustVaultWorld()
        self.player = Character(
            name=player_name,
            base_stats=Stats(max_hp=100, attack_min=6, attack_max=10, defense=1),
            controller=PlayerController(),
            location="berth",
            gold=5,
        )
        self.flags: set[str] = {"game_started"}
        self.bounty = 0
        self.running = True
        self.mode = "exploration"
        self.context: dict[str, object] = {}
        self.engines: dict[str, Engine] = {
            "exploration": ExplorationEngine(),
            "npc": NPCInteractionEngine(),
            "dialogue": DialogueEngine(),
            "trade": TradeEngine(),
            "riddle": RiddleEngine(),
            "combat": CombatEngine(),
            "menu": MenuEngine(),
            "loadout": LoadoutEngine(),
        }
        self.player.add_item("utility_knife")
        self.player.equip("utility_knife", self.world.item_db)
        self.world.on_location_enter(self, self.current_location())

    def item_name(self, item_id: str | None) -> str:
        if item_id is None:
            return "empty"
        return self.world.item(item_id).name

    def current_location(self) -> Location:
        return self.world.get(self.player.location)

    def find_npc(self, npc_name: str) -> NPC | None:
        for location in self.world.locations.values():
            for npc in location.npcs:
                if npc.name == npc_name:
                    return npc
        return None

    def enter_mode(self, mode: str, **context: object) -> None:
        self.mode = mode
        self.context = context

    def change_bounty(self, amount: int, reason: str | None = None) -> None:
        self.bounty = max(0, self.bounty + amount)
        if reason:
            print(f"[Bounty] {reason}: {self.bounty}")
        else:
            print(f"[Bounty] {self.bounty}")

    def current_goal_text(self) -> str:
        if "jailed" in self.flags:
            return "Serve your time and get back on your feet."
        if "act1_started" not in self.flags:
            return "Talk to Rafe Mercer and get briefed on the lift."
        if "act2_started" not in self.flags and "has_payroll_shard" not in self.flags:
            return "Break into the Black Archive and steal the payroll shard."
        if "act2_started" not in self.flags:
            return "Reach the extraction skiff and see how the job shakes out."
        if "found_locator" not in self.flags:
            return "Search Relay Ridge for a locator chart to the buried site."
        if not self.player.has_item("vault_cipher"):
            return "Reach Drill Site Theta and secure the vault cipher."
        if "has_grave_core" not in self.flags:
            return "Descend through Burial Crater and reach the vault heart."
        if "game_won" in self.flags:
            if "ending_corporate" in self.flags:
                return "You sold the vault and bought yourself a future."
            if "ending_broadcast" in self.flags:
                return "The truth is out, and the scramble has begun."
            if "ending_bury" in self.flags:
                return "The vault is buried again."
        return "Decide what to do with the grave core before the cutters close in."

    def show_goal(self) -> None:
        print(f"\nGoal: {self.current_goal_text()}")

    def show_journal(self) -> None:
        divider("JOURNAL / WORLD FLAGS")
        print(f"Gold: {self.player.gold}")
        print(f"Bounty: {self.bounty}")
        if not self.flags:
            print("No flags set.")
            return
        for flag in sorted(self.flags):
            print(f"- {flag}")

    def choose(self, options: list[dict], prompt: str = "Choose: ") -> dict:
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option['text']}")
        while True:
            answer = input(prompt).strip()
            try:
                idx = int(answer) - 1
                selected = options[idx]
                action_separator(selected.get("text"))
                return selected
            except (ValueError, IndexError):
                print("Please enter a valid menu number.")

    def exit_is_blocked(self, exit_obj: Exit) -> bool:
        if exit_obj.blocked:
            return True
        if exit_obj.requires_item and not self.player.has_item(exit_obj.requires_item):
            return True
        if exit_obj.requires_flag and exit_obj.requires_flag not in self.flags:
            return True
        return False

    def handle_move(self, exit_obj: Exit) -> None:
        if exit_obj.on_attempt_effect is not None:
            exit_obj.on_attempt_effect.apply(self)

        if self.exit_is_blocked(exit_obj):
            print(exit_obj.blocked_text)
            if exit_obj.on_blocked_effect is not None:
                exit_obj.on_blocked_effect.apply(self)
            return

        if exit_obj.warning_text:
            print(exit_obj.warning_text)
            confirm = input("Continue? [y/N] ").strip().lower()
            if confirm not in {"y", "yes"}:
                print("You decide not to risk it.")
                return

        self.player.location = exit_obj.destination
        self.flags.add(f"visited:{exit_obj.destination}")
        if exit_obj.on_success_effect is not None:
            exit_obj.on_success_effect.apply(self)
        self.world.on_location_enter(self, self.current_location())

    def give_player_item(self, item_id: str) -> None:
        self.player.add_item(item_id)
        item = self.world.item(item_id)
        print(f"[Inventory] You got: {item.name}")
        if item.description:
            print(item.description)
        for flag in item.set_flags_on_pickup:
            self.flags.add(flag)
        self.world.on_item_picked_up(self, item_id)

    def handle_take_item(self, item_id: str) -> None:
        location = self.current_location()
        if item_id not in location.items:
            print("That item is no longer here.")
            return
        location.items.remove(item_id)
        self.give_player_item(item_id)

    def loot_npc(self, npc: NPC) -> None:
        if not npc.can_loot():
            print(f"There is nothing to loot from {npc.name}.")
            return
        divider(f"Looting {npc.name}")
        if npc.gold > 0:
            print(f"You take {npc.gold} gold.")
            self.player.gold += npc.gold
            npc.gold = 0
        while npc.inventory:
            seen = set()
            options = []
            for item_id in npc.inventory:
                if item_id in seen:
                    continue
                seen.add(item_id)
                count = npc.inventory.count(item_id)
                suffix = f" x{count}" if count > 1 else ""
                options.append(
                    {
                        "kind": "take",
                        "text": f"Take {self.item_name(item_id)}{suffix}",
                        "value": item_id,
                    }
                )
            options.append({"kind": "done", "text": "Done looting", "value": None})
            choice = self.choose(options, prompt="Choose loot: ")
            if choice["kind"] == "done":
                return
            item_id = choice["value"]
            npc.remove_item(item_id)
            self.give_player_item(item_id)
        print("Nothing remains.")

    def resolve_enemy_surrender(self, enemy: NPC) -> bool:
        divider(f"{enemy.name} Surrenders")
        options = [
            {"kind": "spare", "text": f"Spare {enemy.name}", "value": None},
            {"kind": "kill", "text": f"Kill {enemy.name}", "value": None},
        ]
        choice = self.choose(options, prompt="Choose your response: ")
        if choice["kind"] == "spare":
            if enemy.name == "Bandit Nox":
                self.flags.add("bandit_spared")
            self.enter_mode("npc", npc=enemy)
            return True
        if choice["kind"] == "kill":
            enemy.health = 0
            enemy.on_defeat(self)
            if enemy.persistent:
                self.enter_mode("npc", npc=enemy)
            else:
                self.enter_mode("exploration")
            return True
        return False

    def run(self) -> None:
        divider(f"Welcome to {self.world.name}")
        print(
            "A three-act frontier heist: hit the archive, survive the survey world, and decide who owns the buried vault."
        )
        while self.running:
            if not self.player.is_alive():
                divider("Defeat")
                print("You collapse from your injuries. The adventure ends here.")
                break
            engine = self.engines[self.mode]
            engine.run(self)
            if self.running and self.player.is_alive():
                prompt_continue()


"""Textual front end for rich_single_file_rpg.py.

Development version that imports the core game from a sibling file.
A build script can merge both files into a single-file program by setting
EMBEDDED_CORE=True and prepending the core code.
"""

from collections import Counter
from contextlib import redirect_stdout, redirect_stderr
import builtins
import importlib.util
from pathlib import Path
import queue
import sys
import threading
import traceback
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Footer, Header, Input, OptionList, RichLog, Static


EMBEDDED_CORE = True
CORE_PATH = Path(__file__).with_name("rich_single_file_rpg.py")


def load_core_module() -> Any:
    if EMBEDDED_CORE:
        return sys.modules[__name__]
    spec = importlib.util.spec_from_file_location("rpg_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load game core from {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class QueueWriter:
    """Capture stdout/stderr and emit complete lines to the UI queue."""

    def __init__(self, bridge: "BackendBridge"):
        self.bridge = bridge
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self.bridge.emit("log", text=line)
        return len(text)

    def flush(self) -> None:
        if self._buffer:
            self.bridge.emit("log", text=self._buffer)
            self._buffer = ""


class BackendBridge:
    def __init__(self, core: Any):
        self.core = core
        self.events: queue.Queue[dict[str, Any]] = queue.Queue()
        self.responses: queue.Queue[Any] = queue.Queue()
        self.thread: threading.Thread | None = None
        self.game: Any | None = None

    def start(self) -> None:
        self.thread = threading.Thread(target=self._run_backend, daemon=True)
        self.thread.start()

    def emit(self, event_type: str, **payload: Any) -> None:
        self.events.put({"type": event_type, **payload})

    def snapshot(self) -> dict[str, Any]:
        game = self.game
        if game is None:
            return {
                "mode": "boot",
                "goal": "",
                "location": "Starting...",
                "description": "",
                "items": [],
                "npcs": [],
                "features": [],
                "health": 0,
                "max_health": 0,
                "gold": 0,
                "bounty": 0,
                "attack": (0, 0),
                "defense": 0,
                "equipment": {},
                "inventory": [],
                "flags": [],
            }
        location = game.current_location()
        item_db = game.world.item_db
        low, high = game.player.attack_range(item_db)
        counts = Counter(game.player.inventory)
        inventory = []
        seen = set()
        for item_id in game.player.inventory:
            if item_id in seen:
                continue
            seen.add(item_id)
            item = item_db[item_id]
            count = counts[item_id]
            inventory.append((item.name, count))
        equipment = {}
        for slot in game.player.EQUIPMENT_SLOTS:
            item_id = game.player.equipment[slot]
            equipment[slot] = item_db[item_id].name if item_id is not None else "empty"
        return {
            "mode": game.mode,
            "goal": self.goal_text(game),
            "location": location.name,
            "description": location.description,
            "items": [game.item_name(item_id) for item_id in location.items],
            "npcs": [f"{npc.name} ({npc.mood_label()})" for npc in location.npcs],
            "features": [feature.name for feature in location.features],
            "health": game.player.health,
            "max_health": game.player.total_max_hp(item_db),
            "gold": game.player.gold,
            "bounty": game.bounty,
            "attack": (low, high),
            "defense": game.player.total_defense(item_db),
            "equipment": equipment,
            "inventory": inventory,
            "flags": sorted(game.flags),
        }

    def goal_text(self, game: Any) -> str:
        if hasattr(game, "current_goal_text"):
            return game.current_goal_text()
        return "Keep moving."

    def request_choice(self, options: list[dict[str, Any]], prompt: str) -> int:
        self.emit("state", snapshot=self.snapshot())
        self.emit(
            "choices", prompt=prompt, options=[option["text"] for option in options]
        )
        return int(self.responses.get())

    def request_text(self, prompt: str) -> str:
        self.emit("state", snapshot=self.snapshot())
        self.emit("text_input", prompt=prompt)
        response = self.responses.get()
        return "" if response is None else str(response)

    def request_continue(self, prompt: str) -> None:
        # In the TUI, the current outcome remains visible in its own pane, so
        # an explicit continue step is unnecessary. Treat it as a no-op.
        self.emit("state", snapshot=self.snapshot())
        return

    def _run_backend(self) -> None:
        core = self.core
        bridge = self

        class TuiExplorationEngine(core.Engine):
            def run(self, game: Any) -> None:
                if game.world.try_start_of_exploration_encounter(game):
                    return

                location = game.current_location()
                choices = []
                jailed = "jailed" in game.flags and location.key == "jail"
                if not jailed:
                    for exit_obj in location.exits:
                        destination = game.world.get(exit_obj.destination)
                        text = f"Go {exit_obj.direction} to {destination.name}"
                        if game.exit_is_blocked(exit_obj):
                            text += " [blocked]"
                        elif exit_obj.warning_text:
                            text += " [risky]"
                        choices.append(
                            {"kind": "move", "text": text, "value": exit_obj}
                        )
                    for item_id in location.items:
                        choices.append(
                            {
                                "kind": "take_item",
                                "text": f"Take {game.item_name(item_id)}",
                                "value": item_id,
                            }
                        )
                    for npc in location.npcs:
                        choices.append(
                            {"kind": "npc", "text": npc.menu_text(), "value": npc}
                        )
                for feature in location.features:
                    choices.append(
                        {
                            "kind": "feature",
                            "text": feature.menu_text(),
                            "value": feature,
                        }
                    )
                if not jailed:
                    choices.append({"kind": "menu", "text": "Open menu", "value": None})

                choice = game.choose(choices, prompt="What do you want to do?")
                if choice["kind"] == "move":
                    game.handle_move(choice["value"])
                elif choice["kind"] == "take_item":
                    game.handle_take_item(choice["value"])
                elif choice["kind"] == "npc":
                    game.enter_mode("npc", npc=choice["value"])
                elif choice["kind"] == "feature":
                    choice["value"].interact(game)
                elif choice["kind"] == "menu":
                    game.enter_mode("menu")

        class TuiNPCInteractionEngine(core.Engine):
            def run(self, game: Any) -> None:
                npc = game.context["npc"]
                if (
                    npc.is_guard()
                    and game.bounty > 0
                    and npc.is_alive()
                    and not npc.defeated
                    and not npc.hostile
                ):
                    core.say(
                        npc.name, f"You have a bounty of {game.bounty}. Stand down."
                    )
                    npc.hostile = True
                    game.enter_mode("combat", npc=npc)
                    return

                options = []
                if npc.can_talk(game):
                    options.append(
                        {"kind": "talk", "text": f"Talk to {npc.name}", "value": npc}
                    )
                if npc.can_trade(game):
                    options.append(
                        {
                            "kind": "trade",
                            "text": f"Trade with {npc.name}",
                            "value": npc,
                        }
                    )
                if npc.can_riddle():
                    options.append(
                        {
                            "kind": "riddle",
                            "text": f"Challenge {npc.name}",
                            "value": npc,
                        }
                    )
                if npc.can_attack():
                    options.append(
                        {"kind": "attack", "text": f"Attack {npc.name}", "value": npc}
                    )
                if npc.can_loot():
                    options.append(
                        {"kind": "loot", "text": f"Loot {npc.name}", "value": npc}
                    )
                options.append({"kind": "back", "text": "Step away", "value": None})

                choice = game.choose(
                    options, prompt=f"How do you want to interact with {npc.name}?"
                )
                kind = choice["kind"]
                if kind == "talk":
                    game.enter_mode("dialogue", npc=npc)
                elif kind == "trade":
                    game.enter_mode("trade", npc=npc)
                elif kind == "riddle":
                    game.enter_mode("riddle", npc=npc)
                elif kind == "attack":
                    npc.on_player_attack(game)
                    game.enter_mode("combat", npc=npc)
                elif kind == "loot":
                    game.loot_npc(npc)
                    game.enter_mode("npc", npc=npc)
                elif kind == "back":
                    game.enter_mode("exploration")

        class TuiDialogueEngine(core.Engine):
            def run(self, game: Any) -> None:
                npc = game.context["npc"]
                topics = npc.available_topics(game)
                if not topics:
                    core.say(npc.name, "I have nothing more to say right now.")
                    game.enter_mode("npc", npc=npc)
                    return

                options = [
                    {"kind": "topic", "text": topic.title, "value": topic}
                    for topic in topics
                ]
                options.append({"kind": "back", "text": "Back", "value": None})
                choice = game.choose(
                    options, prompt=f"What do you want to ask {npc.name}?"
                )
                if choice["kind"] == "back":
                    game.enter_mode("npc", npc=npc)
                    return

                topic = choice["value"]
                for line in topic.lines:
                    core.say(npc.name, line)
                if topic.outcome_effect is not None:
                    topic.outcome_effect.apply(game)
                if topic.once:
                    npc.used_topics.add(topic.key)
                if "game_won" in game.flags:
                    game.running = False
                    return
                game.enter_mode("npc", npc=npc)

        class TuiTradeEngine(core.Engine):
            def run(self, game: Any) -> None:
                npc = game.context["npc"]
                offers = npc.available_trade_offers(game)
                if not offers:
                    core.say(npc.name, "I have nothing I can trade right now.")
                    game.enter_mode("npc", npc=npc)
                    return

                options = []
                for offer_index, offer in offers:
                    wants_parts = []
                    if offer.wants_gold:
                        wants_parts.append(f"{offer.wants_gold} gold")
                    if offer.wants_items:
                        wants_parts.extend(
                            game.item_name(item_id) for item_id in offer.wants_items
                        )
                    gives_parts = []
                    if offer.gives_gold:
                        gives_parts.append(f"{offer.gives_gold} gold")
                    if offer.gives_items:
                        gives_parts.extend(
                            game.item_name(item_id) for item_id in offer.gives_items
                        )
                    wants = ", ".join(wants_parts) or "nothing"
                    gives = ", ".join(gives_parts) or "nothing"
                    options.append(
                        {
                            "kind": "offer",
                            "text": f"{offer.title} [{wants} -> {gives}]",
                            "value": (offer_index, offer),
                        }
                    )
                options.append({"kind": "back", "text": "Back", "value": None})

                choice = game.choose(options, prompt=f"Choose a trade with {npc.name}")
                if choice["kind"] == "back":
                    game.enter_mode("npc", npc=npc)
                    return

                offer_index, offer = choice["value"]
                if game.player.gold < offer.wants_gold:
                    core.say(
                        npc.name, f"Come back when you have {offer.wants_gold} gold."
                    )
                    game.enter_mode("npc", npc=npc)
                    return
                if not game.player.has_items(offer.wants_items):
                    core.say(
                        npc.name,
                        f"Come back when you have: {', '.join(game.item_name(i) for i in offer.wants_items)}.",
                    )
                    game.enter_mode("npc", npc=npc)
                    return
                if npc.gold < offer.gives_gold or not npc.has_items(offer.gives_items):
                    core.say(npc.name, "I cannot complete that trade right now.")
                    game.enter_mode("npc", npc=npc)
                    return

                game.player.gold -= offer.wants_gold
                npc.gold += offer.wants_gold
                npc.gold -= offer.gives_gold
                game.player.gold += offer.gives_gold
                game.player.remove_items(offer.wants_items)
                npc.add_items(offer.wants_items)
                npc.remove_items(offer.gives_items)
                for item_id in offer.gives_items:
                    game.give_player_item(item_id)
                if not offer.repeatable:
                    npc.completed_trades.add(offer_index)
                core.say(npc.name, "A fair trade.")
                game.enter_mode("npc", npc=npc)

        class TuiRiddleEngine(core.Engine):
            def run(self, game: Any) -> None:
                npc = game.context["npc"]
                riddle = npc.riddle
                if riddle is None:
                    game.enter_mode("npc", npc=npc)
                    return
                if npc.riddle_solved:
                    for line in riddle.repeat_lines:
                        core.say(npc.name, line)
                    game.enter_mode("npc", npc=npc)
                    return

                for line in riddle.intro_lines:
                    core.say(npc.name, line)
                core.say(npc.name, riddle.question)
                answer = input("Your answer: ").strip().lower()
                if answer in [a.lower() for a in riddle.answers]:
                    for line in riddle.success_lines:
                        core.say(npc.name, line)
                    npc.riddle_solved = True
                    for flag in riddle.set_flags_on_success:
                        game.flags.add(flag)
                else:
                    for line in riddle.failure_lines:
                        core.say(npc.name, line)
                    if riddle.damage_on_failure > 0:
                        actual = game.player.take_damage(
                            riddle.damage_on_failure, game.world.item_db
                        )
                        print(f"You take {actual} damage.")
                game.enter_mode("npc", npc=npc)

        class TuiMenuEngine(core.Engine):
            def run(self, game: Any) -> None:
                options = [
                    {"kind": "status", "text": "View status", "value": None},
                    {"kind": "loadout", "text": "Manage loadout", "value": None},
                    {
                        "kind": "journal",
                        "text": "View world flags / journal",
                        "value": None,
                    },
                    {"kind": "back", "text": "Return to exploration", "value": None},
                    {"kind": "quit", "text": "Quit game", "value": None},
                ]
                choice = game.choose(options, prompt="Choose a menu option")
                if choice["kind"] == "status":
                    game.player.show_status(game.world.item_db, bounty=game.bounty)
                    game.enter_mode("menu")
                elif choice["kind"] == "loadout":
                    game.enter_mode("loadout")
                elif choice["kind"] == "journal":
                    game.show_journal()
                    game.enter_mode("menu")
                elif choice["kind"] == "back":
                    game.enter_mode("exploration")
                elif choice["kind"] == "quit":
                    print("Thanks for playing!")
                    game.running = False

        class TuiLoadoutEngine(core.Engine):
            def run(self, game: Any) -> None:
                player = game.player
                item_db = game.world.item_db
                options = []
                for item_id in player.equippable_items(item_db):
                    item = item_db[item_id]
                    current = player.equipment.get(item.slot)
                    suffix = " [equipped]" if current == item_id else ""
                    options.append(
                        {
                            "kind": "equip",
                            "text": f"Equip {item.name} ({item.slot}){suffix}",
                            "value": item_id,
                        }
                    )
                for slot in player.EQUIPMENT_SLOTS:
                    if player.equipment[slot] is not None:
                        options.append(
                            {
                                "kind": "unequip",
                                "text": f"Unequip {slot}",
                                "value": slot,
                            }
                        )
                options.append({"kind": "back", "text": "Back", "value": None})
                choice = game.choose(options, prompt="Choose a loadout action")
                if choice["kind"] == "equip":
                    ok, message = player.equip(choice["value"], item_db)
                    print(message)
                    game.enter_mode("loadout")
                elif choice["kind"] == "unequip":
                    ok, message = player.unequip(choice["value"], item_db)
                    print(message)
                    game.enter_mode("loadout")
                elif choice["kind"] == "back":
                    game.enter_mode("menu")

        class TuiGame(core.Game):
            def __init__(self, bridge: BackendBridge):
                self._bridge = bridge
                super().__init__(player_name="Tav", world=core.DustVaultWorld())
                self.engines.update(
                    {
                        "exploration": TuiExplorationEngine(),
                        "npc": TuiNPCInteractionEngine(),
                        "dialogue": TuiDialogueEngine(),
                        "trade": TuiTradeEngine(),
                        "riddle": TuiRiddleEngine(),
                        "menu": TuiMenuEngine(),
                        "loadout": TuiLoadoutEngine(),
                    }
                )

            def choose(self, options: list[dict], prompt: str = "Choose: ") -> dict:
                index = self._bridge.request_choice(options, prompt)
                selected = options[index]
                core.action_separator(selected.get("text"))
                return selected

        old_input = builtins.input
        old_typewriter = core.typewriter_print
        old_continue = core.prompt_continue

        def queued_typewriter(prefix: str, text: str, word_delay: float = 0.02) -> None:
            bridge.emit("stream_start", prefix=prefix)
            words = text.split()
            for index, word in enumerate(words):
                suffix = " " if index < len(words) - 1 else ""
                bridge.emit("stream_chunk", text=word + suffix)
                if word_delay > 0:
                    time.sleep(word_delay)
            bridge.emit("stream_end")

        def queued_input(prompt: str = "") -> str:
            return bridge.request_text(prompt)

        def queued_continue(prompt: str = "Press Enter to continue...") -> None:
            bridge.request_continue(prompt)

        writer = QueueWriter(bridge)

        try:
            builtins.input = queued_input
            core.typewriter_print = queued_typewriter
            core.prompt_continue = queued_continue
            with redirect_stdout(writer), redirect_stderr(writer):
                bridge.game = TuiGame(bridge)
                bridge.emit("state", snapshot=bridge.snapshot())
                bridge.game.run()
            writer.flush()
            bridge.emit("state", snapshot=bridge.snapshot())
            bridge.emit("game_over", message="Game over.")
        except Exception:
            writer.flush()
            bridge.emit("log", text=traceback.format_exc())
            bridge.emit("game_over", message="The backend crashed.")
        finally:
            builtins.input = old_input
            core.typewriter_print = old_typewriter
            core.prompt_continue = old_continue


class RPGTextualApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    #body {
        height: 1fr;
        layout: horizontal;
    }

    #sidebar {
        width: 34;
        min-width: 28;
        border: round $accent;
        padding: 1;
    }

    #main {
        width: 1fr;
        border: round $accent;
        padding: 1;
    }

    #actions {
        width: 40;
        min-width: 34;
        border: round $accent;
        padding: 1;
    }

    #goal, #location, #status {
        margin-bottom: 1;
        border: round $surface;
        padding: 1;
    }

    #current_event {
        height: 1fr;
        min-height: 10;
        border: round $surface;
        padding: 1;
        margin-bottom: 1;
        overflow-y: auto;
    }

    #log_status {
        height: auto;
        margin-bottom: 1;
        border: round $surface;
        padding: 0 1;
    }

    #history {
        height: 6;
        min-height: 4;
        max-height: 12;
        border: round $surface;
        padding: 1;
    }

    #prompt {
        margin-bottom: 1;
        min-height: 3;
        border: round $surface;
        padding: 1;
    }

    #options {
        height: 1fr;
        margin-bottom: 1;
    }

    #options:focus {
        border: round $accent;
    }

    #text_input {
        margin-top: 1;
    }


    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("m", "menu", "Menu"),
        ("c", "clear_history", "Clear history"),
        ("l", "toggle_log", "Toggle log"),
        ("L", "toggle_log", "Toggle log"),
        ("escape", "focus_choices", "Focus choices"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.core = load_core_module()
        self.bridge = BackendBridge(self.core)
        self.interaction_mode = "boot"
        self.pending_options: list[str] = []
        self.current_event_text = ""
        self.game_over = False
        self.log_collapsed = True
        self.history_line_count = 0

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                yield Static("Goal", id="goal")
                yield Static("Location", id="location")
                yield Static("Status", id="status")
            with Vertical(id="main"):
                yield Static("Latest outcome will appear here.", id="current_event")
                yield Static("System log hidden. Press L to show.", id="log_status")
                yield RichLog(
                    id="history",
                    wrap=True,
                    markup=False,
                    auto_scroll=True,
                    max_lines=600,
                    classes="hidden",
                )
            with Vertical(id="actions"):
                yield Static("Starting up...", id="prompt")
                yield OptionList(id="options")
                yield Input(
                    placeholder="Type response and press Enter",
                    id="text_input",
                    classes="hidden",
                )
        yield Footer()

    def on_mount(self) -> None:
        self.bridge.start()
        self.set_interval(0.05, self.poll_backend)

    def action_menu(self) -> None:
        if self.interaction_mode == "choice":
            for i, label in enumerate(self.pending_options):
                if label.lower().startswith("open menu"):
                    self.archive_current_event()
                    self.bridge.responses.put(i)
                    return

    def action_focus_choices(self) -> None:
        if self.interaction_mode == "choice":
            self.query_one("#options", OptionList).focus()
        elif self.interaction_mode == "text":
            self.query_one("#text_input", Input).focus()

    def action_clear_history(self) -> None:
        self.query_one("#history", RichLog).clear()
        self.history_line_count = 0
        self.update_history_size()

    def action_toggle_log(self) -> None:
        self.log_collapsed = not self.log_collapsed
        log = self.query_one("#history", RichLog)
        status = self.query_one("#log_status", Static)
        if self.log_collapsed:
            log.add_class("hidden")
            status.update("System log hidden. Press L to show.")
        else:
            log.remove_class("hidden")
            status.update("System log visible. Press L to hide.")
            self.update_history_size()

    def poll_backend(self) -> None:
        while True:
            try:
                event = self.bridge.events.get_nowait()
            except queue.Empty:
                break
            self.handle_backend_event(event)

    def handle_backend_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "log":
            self.append_current_event_line(event.get("text", ""))
        elif event_type == "stream_start":
            self.prepare_for_stream_start()
            self.append_current_event_chunk(event.get("prefix", ""))
        elif event_type == "stream_chunk":
            self.append_current_event_chunk(event.get("text", ""))
        elif event_type == "stream_end":
            self.append_current_event_chunk("\n")
        elif event_type == "state":
            self.update_state(event["snapshot"])
        elif event_type == "choices":
            self.show_choices(event["prompt"], event["options"])
        elif event_type == "text_input":
            self.show_text_input(event["prompt"])
        elif event_type == "game_over":
            self.game_over = True
            self.query_one("#prompt", Static).update(event.get("message", "Game over."))
            self.clear_options()
            self.hide_text_input()
            self.archive_current_event()

    def append_current_event_line(self, text: str) -> None:
        if self.current_event_text and not self.current_event_text.endswith("\n"):
            self.current_event_text += "\n"
        self.current_event_text += text
        self.render_current_event()

    def prepare_for_stream_start(self) -> None:
        if not self.current_event_text:
            return
        if not self.current_event_text.endswith("\n"):
            self.current_event_text += "\n"
        if not self.current_event_text.endswith("\n\n"):
            self.current_event_text += "\n"
        self.render_current_event()

    def append_current_event_chunk(self, text: str) -> None:
        self.current_event_text += text
        self.render_current_event()

    def normalize_event_text(self) -> str:
        if not self.current_event_text:
            return "Latest outcome will appear here."
        lines = self.current_event_text.split("\n")
        while lines and lines[0] == "":
            lines.pop(0)
        while lines and lines[-1] == "":
            lines.pop()
        if not lines:
            return "Latest outcome will appear here."
        normalized = []
        blank_run = 0
        for line in lines:
            if line == "":
                blank_run += 1
                if blank_run <= 1:
                    normalized.append(line)
            else:
                blank_run = 0
                normalized.append(line)
        return "\n".join(normalized)

    def render_current_event(self) -> None:
        self.query_one("#current_event", Static).update(self.normalize_event_text())

    def archive_current_event(self) -> None:
        text = self.normalize_event_text()
        if text and text != "Latest outcome will appear here.":
            history = self.query_one("#history", RichLog)
            history.write("─" * 56)
            self.history_line_count += 1
            for line in text.splitlines():
                history.write(line)
                self.history_line_count += 1
            self.update_history_size()
        self.current_event_text = ""
        self.render_current_event()

    def update_history_size(self) -> None:
        history = self.query_one("#history", RichLog)
        if self.log_collapsed:
            return
        desired = max(4, min(12, self.history_line_count + 2))
        history.styles.height = desired

    def update_state(self, snapshot: dict[str, Any]) -> None:
        goal = self.query_one("#goal", Static)
        location = self.query_one("#location", Static)
        status = self.query_one("#status", Static)

        goal.update(f"[b]Goal[/b]\n{snapshot['goal']}")

        parts = [f"[b]{snapshot['location']}[/b]", "", snapshot["description"]]
        if snapshot["items"]:
            parts.extend(
                ["", "[b]Items here[/b]"] + [f"- {item}" for item in snapshot["items"]]
            )
        if snapshot["npcs"]:
            parts.extend(
                ["", "[b]People / creatures[/b]"]
                + [f"- {npc}" for npc in snapshot["npcs"]]
            )
        if snapshot["features"]:
            parts.extend(
                ["", "[b]Features[/b]"]
                + [f"- {feature}" for feature in snapshot["features"]]
            )
        location.update("\n".join(parts))

        attack_low, attack_high = snapshot["attack"]
        status_lines = [
            "[b]Player[/b]",
            f"HP: {snapshot['health']}/{snapshot['max_health']}",
            f"Attack: {attack_low}-{attack_high}",
            f"Defense: {snapshot['defense']}",
            f"Gold: {snapshot['gold']}",
            f"Bounty: {snapshot['bounty']}",
            "",
            "[b]Equipment[/b]",
        ]
        for slot, item_name in snapshot["equipment"].items():
            status_lines.append(f"- {slot}: {item_name}")
        status_lines.extend(["", "[b]Inventory[/b]"])
        if snapshot["inventory"]:
            for item_name, count in snapshot["inventory"]:
                suffix = f" x{count}" if count > 1 else ""
                status_lines.append(f"- {item_name}{suffix}")
        else:
            status_lines.append("- empty")
        status.update("\n".join(status_lines))

    def clear_options(self) -> None:
        option_list = self.query_one("#options", OptionList)
        option_list.clear_options()
        self.pending_options = []

    def show_choices(self, prompt: str, options: list[str]) -> None:
        self.interaction_mode = "choice"
        self.pending_options = list(options)
        self.query_one("#prompt", Static).update(
            f"{prompt}\n\nUse ↑/↓ and Enter, number keys 1-9, or click."
        )
        self.hide_text_input()
        option_list = self.query_one("#options", OptionList)
        option_list.clear_options()
        display_options = [f"{i}. {label}" for i, label in enumerate(options, start=1)]
        option_list.add_options(display_options)
        option_list.highlighted = 0 if options else None
        option_list.focus()

    def show_text_input(self, prompt: str) -> None:
        self.interaction_mode = "text"
        self.clear_options()
        self.query_one("#prompt", Static).update(prompt)
        input_widget = self.query_one("#text_input", Input)
        input_widget.remove_class("hidden")
        input_widget.value = ""
        input_widget.placeholder = prompt or "Type response and press Enter"
        input_widget.focus()

    def hide_text_input(self) -> None:
        input_widget = self.query_one("#text_input", Input)
        input_widget.add_class("hidden")
        input_widget.value = ""

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if self.interaction_mode != "choice":
            return
        self.archive_current_event()
        self.bridge.responses.put(event.option_index)
        self.clear_options()
        self.query_one("#prompt", Static).update("Resolving action...")

    def on_key(self, event: Key) -> None:
        if self.interaction_mode != "choice":
            return

        option_list = self.query_one("#options", OptionList)
        count = len(self.pending_options)
        if count == 0:
            return

        key = event.key
        option_list_has_focus = self.focused is option_list

        # When the OptionList itself has focus, let it handle arrow keys and
        # Enter so we do not double-advance the selection.
        if option_list_has_focus and key in {"up", "down", "enter"}:
            return

        if key == "up":
            current = option_list.highlighted
            if current is None:
                option_list.highlighted = 0
            else:
                option_list.highlighted = max(0, current - 1)
            event.stop()
            return

        if key == "down":
            current = option_list.highlighted
            if current is None:
                option_list.highlighted = 0
            else:
                option_list.highlighted = min(count - 1, current + 1)
            event.stop()
            return

        if key == "enter":
            current = option_list.highlighted
            if current is None:
                current = 0
            self.archive_current_event()
            self.bridge.responses.put(current)
            self.clear_options()
            self.query_one("#prompt", Static).update("Resolving action...")
            event.stop()
            return

        if len(key) == 1 and key.isdigit():
            index = int(key) - 1
            if 0 <= index < count:
                option_list.highlighted = index
                self.archive_current_event()
                self.bridge.responses.put(index)
                self.clear_options()
                self.query_one("#prompt", Static).update("Resolving action...")
                event.stop()
                return

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "text_input" or self.interaction_mode != "text":
            return
        self.archive_current_event()
        self.bridge.responses.put(event.value)
        self.hide_text_input()
        self.query_one("#prompt", Static).update("Resolving input...")


if __name__ == "__main__":
    RPGTextualApp().run()
