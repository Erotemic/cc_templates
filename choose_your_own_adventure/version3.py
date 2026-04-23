from __future__ import annotations

"""
Version 3: the small story inside a reusable engine.

This version keeps the teaching-sized adventure, but rebuilds it on top of a
larger game architecture. The story is still simple, but the code now uses:
- a world model with locations, exits, items, NPCs, and features
- effect objects for scripted outcomes
- engine modes for exploration, dialogue, combat, and menus
- reusable combat and inventory systems

Use this version to teach:
- separation of concerns
- extensible game architecture
- how a simple story can sit on top of reusable systems
- the tradeoff between flexibility and complexity

This file is useful when students are ready to see how small game logic can
be moved into a more general framework.
"""

from dataclasses import dataclass, field
from collections import Counter
import random
import time


# ============================================================
# Presentation helpers
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
class DialogueTopic:
    key: str
    title: str
    lines: list[str]
    required_flags: set[str] = field(default_factory=set)
    blocked_flags: set[str] = field(default_factory=set)
    required_items: list[str] = field(default_factory=list)
    once: bool = False
    outcome_effect: "Effect | None" = None


@dataclass
class Exit:
    direction: str
    destination: str
    requires_item: str | None = None
    requires_flag: str | None = None
    blocked: bool = False
    blocked_text: str = "That path is blocked."
    warning_text: str | None = None
    on_attempt_effect: "Effect | None" = None
    on_blocked_effect: "Effect | None" = None
    on_success_effect: "Effect | None" = None


@dataclass
class Location:
    key: str
    name: str
    description: str
    exits: list[Exit] = field(default_factory=list)
    items: list[str] = field(default_factory=list)
    npcs: list["NPC"] = field(default_factory=list)
    features: list["Feature"] = field(default_factory=list)


# ============================================================
# Effects
# ============================================================


class Effect:
    def apply(self, game: "Game") -> None:
        raise NotImplementedError


class PrintEffect(Effect):
    def __init__(self, lines: str | list[str]):
        self.lines = [lines] if isinstance(lines, str) else lines

    def apply(self, game: "Game") -> None:
        for line in self.lines:
            print(line)


class SetFlagEffect(Effect):
    def __init__(self, *flags: str):
        self.flags = list(flags)

    def apply(self, game: "Game") -> None:
        for flag in self.flags:
            game.flags.add(flag)


class GivePlayerItemEffect(Effect):
    def __init__(self, *item_ids: str):
        self.item_ids = list(item_ids)

    def apply(self, game: "Game") -> None:
        for item_id in self.item_ids:
            game.give_player_item(item_id)


class MovePlayerEffect(Effect):
    def __init__(self, destination: str, text: str | None = None):
        self.destination = destination
        self.text = text

    def apply(self, game: "Game") -> None:
        if self.text:
            print(self.text)
        game.player.location = self.destination
        game.flags.add(f"visited:{self.destination}")
        game.world.on_location_enter(game, game.current_location())


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

    def apply(self, game: "Game") -> None:
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


class CompositeEffect(Effect):
    def __init__(self, *effects: Effect):
        self.effects = list(effects)

    def apply(self, game: "Game") -> None:
        for effect in self.effects:
            effect.apply(game)


# ============================================================
# Controllers and characters
# ============================================================


class Controller:
    def choose_combat_action(
        self, game: "Game", actor: "Character", opponent: "Character"
    ) -> tuple[str, str | None]:
        raise NotImplementedError


class PlayerController(Controller):
    def choose_combat_action(
        self, game: "Game", actor: "Character", opponent: "Character"
    ) -> tuple[str, str | None]:
        options = [
            {"kind": "attack", "text": "Attack", "value": None},
            {"kind": "defend", "text": "Defend", "value": None},
            {"kind": "item", "text": "Use consumable", "value": None},
            {"kind": "run", "text": "Run", "value": None},
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
        self, game: "Game", actor: "Character", opponent: "Character"
    ) -> tuple[str, str | None]:
        consumables = actor.consumable_items(game.world.item_db)
        hp_ratio = actor.health / max(1, actor.total_max_hp(game.world.item_db))
        if consumables and hp_ratio <= 0.35:
            return "item", consumables[0]
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
    ):
        self.name = name
        self.base_stats = base_stats
        self.controller = controller
        self.location = location
        self.health = base_stats.max_hp
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

    def remove_item(self, item_id: str) -> bool:
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            for slot, equipped in self.equipment.items():
                if equipped == item_id:
                    self.equipment[slot] = None
            return True
        return False

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
            return True, f"Equipped {item.name}."
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

    def show_status(self, item_db: dict[str, Item]) -> None:
        low, high = self.attack_range(item_db)
        divider("STATUS")
        print(f"Name: {self.name}")
        print(f"Health: {self.health}/{self.total_max_hp(item_db)}")
        print(f"Attack: {low}-{high}")
        print(f"Defense: {self.total_defense(item_db)}")

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
        hostile: bool = False,
        dialogue_topics: list[DialogueTopic] | None = None,
        reward_items: list[str] | None = None,
        reward_flags: set[str] | None = None,
        persistent: bool = True,
        inventory: list[str] | None = None,
        equipment: dict[str, str | None] | None = None,
        post_victory_lines: list[str] | None = None,
    ):
        super().__init__(
            name=name,
            base_stats=base_stats,
            controller=AIController(),
        )
        self.description = description
        self.hostile = hostile
        self.dialogue_topics = dialogue_topics or []
        self.reward_items = reward_items or []
        self.reward_flags = reward_flags or set()
        self.persistent = persistent
        self.post_victory_lines = post_victory_lines or []
        self.used_topics: set[str] = set()
        self.defeated = False

        for item_id in inventory or []:
            self.add_item(item_id)
        if equipment:
            for slot, item_id in equipment.items():
                self.equipment[slot] = item_id

    def mood_label(self) -> str:
        if self.defeated:
            return "defeated"
        if self.hostile:
            return "hostile"
        return "neutral"

    def menu_text(self) -> str:
        return f"Approach {self.name}"

    def available_topics(self, game: "Game") -> list[DialogueTopic]:
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

    def can_talk(self, game: "Game") -> bool:
        return self.is_alive() and bool(self.available_topics(game))

    def can_attack(self) -> bool:
        return self.is_alive() and not self.defeated and self.hostile

    def on_player_attack(self, game: "Game") -> None:
        self.hostile = True

    def on_defeat(self, game: "Game") -> None:
        if self.defeated:
            return
        self.defeated = True
        self.hostile = False
        self.health = 0
        for item_id in self.reward_items:
            game.give_player_item(item_id)
        for flag in self.reward_flags:
            game.flags.add(flag)
        game.world.on_npc_defeated(game, self)


# ============================================================
# Features / world objects
# ============================================================


class Feature:
    def __init__(self, name: str, verb: str = "Inspect"):
        self.name = name
        self.verb = verb

    def menu_text(self) -> str:
        return f"{self.verb} {self.name}"

    def interact(self, game: "Game") -> None:
        print(f"Nothing happens when you interact with {self.name}.")


class TextFeature(Feature):
    def __init__(self, name: str, text: str, verb: str = "Inspect"):
        super().__init__(name=name, verb=verb)
        self.text = text

    def interact(self, game: "Game") -> None:
        print("\n" + self.text)


class ScriptedFeature(Feature):
    def __init__(
        self,
        name: str,
        *,
        verb: str = "Use",
        required_flags: set[str] | None = None,
        blocked_flags: set[str] | None = None,
        required_items: list[str] | None = None,
        blocked_text: str = "Nothing happens.",
        once_flag: str | None = None,
        first_effect: Effect | None = None,
        repeat_effect: Effect | None = None,
    ):
        super().__init__(name=name, verb=verb)
        self.required_flags = required_flags or set()
        self.blocked_flags = blocked_flags or set()
        self.required_items = required_items or []
        self.blocked_text = blocked_text
        self.once_flag = once_flag
        self.first_effect = first_effect
        self.repeat_effect = repeat_effect

    def interact(self, game: "Game") -> None:
        if not self.required_flags.issubset(game.flags):
            print(self.blocked_text)
            return
        if self.blocked_flags.intersection(game.flags):
            print(self.blocked_text)
            return
        if not game.player.has_items(self.required_items):
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
# World base class
# ============================================================


class World:
    def __init__(self, name: str):
        self.name = name
        self.locations: dict[str, Location] = {}
        self.item_db: dict[str, Item] = {}

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
        self,
        a: str,
        dir_a_to_b: str,
        b: str,
        dir_b_to_a: str,
        **kwargs,
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

    def on_location_enter(self, game: "Game", location: Location) -> None:
        pass

    def on_item_picked_up(self, game: "Game", item_id: str) -> None:
        pass

    def on_npc_defeated(self, game: "Game", npc: NPC) -> None:
        pass


# ============================================================
# Concrete world
# ============================================================


class ValleyQuestWorld(World):
    def __init__(self):
        super().__init__(name="The Crystal Valley")
        self._flag = lambda _name: False
        self.build_items()
        self.build_locations()
        self.build_paths()
        self.build_features()
        self.build_npcs()
        self.scatter_items()
        self.refresh_descriptions()

    def build_items(self) -> None:
        self.define_item(Item("herb", "Useful Herb", "A fresh herb from the forest."))
        self.define_item(
            Item(
                "sword",
                "Old Sword",
                "An old sword found near a fallen log.",
                slot="weapon",
                power_bonus=6,
            )
        )
        self.define_item(
            Item("lantern", "Lantern", "A lantern bright enough for the cave.")
        )
        self.define_item(
            Item(
                "silver_key",
                "Silver Key",
                "A silver key found near the spider's nest.",
            )
        )
        self.define_item(
            Item(
                "crystal",
                "Glowing Crystal",
                "A warm crystal pulsing with light.",
                set_flags_on_pickup={"crystal_taken"},
            )
        )
        self.define_item(
            Item(
                "health_tonic",
                "Health Tonic",
                "A basic restorative tonic.",
                healing=10,
                tags={"consumable"},
            )
        )

    def build_locations(self) -> None:
        self.add_location("village", "Village Square", "")
        self.add_location("crossroads", "Crossroads", "")
        self.add_location("forest", "Forest", "")
        self.add_location("lake", "Lake Shore", "")
        self.add_location("cave_entrance", "Cave Entrance", "")
        self.add_location("cave", "Dark Cave", "")
        self.add_location("ruins", "Old Ruins", "")
        self.add_location("tower_gate", "Tower Gate", "")
        self.add_location("tower_top", "Tower Top", "")

    def build_paths(self) -> None:
        self.connect_two_way("village", "north", "crossroads", "south")
        self.connect_two_way("crossroads", "west", "forest", "east")
        self.connect_two_way("crossroads", "east", "lake", "west")
        self.connect_two_way("crossroads", "north", "ruins", "south")
        self.connect_two_way("forest", "north", "cave_entrance", "south")
        self.connect(
            "cave_entrance",
            "in",
            "cave",
            requires_item="lantern",
            blocked_text="It is too dark to enter safely. You need a Lantern.",
        )
        self.connect("cave", "out", "cave_entrance")
        self.connect_two_way("ruins", "north", "tower_gate", "south")
        self.connect(
            "tower_gate",
            "up",
            "tower_top",
            requires_flag="tower_unlocked",
            blocked_text="The tower gate is still locked.",
        )
        self.connect("tower_top", "down", "tower_gate")

    def build_features(self) -> None:
        self.place_feature(
            "tower_gate",
            ScriptedFeature(
                name="tower gate",
                verb="Try to open",
                blocked_text="The tower gate is locked. You need a key.",
                once_flag="tower_unlocked",
                required_items=["silver_key"],
                first_effect=CompositeEffect(
                    PrintEffect(
                        [
                            "You unlock the tower gate with the silver key.",
                            "You climb the stairs to the top of the tower.",
                        ]
                    ),
                    SetFlagEffect("tower_unlocked"),
                    MovePlayerEffect("tower_top"),
                ),
                repeat_effect=PrintEffect(
                    "The tower gate is already open, and the stairs still lead upward."
                ),
            ),
        )
        self.place_feature(
            "tower_top",
            ScriptedFeature(
                name="glowing crystal",
                verb="Take",
                blocked_text="The pedestal is already empty.",
                blocked_flags={"crystal_taken"},
                once_flag="crystal_taken_feature",
                first_effect=CompositeEffect(
                    PrintEffect(
                        [
                            "You take the glowing crystal from the pedestal.",
                            "The crystal feels warm in your hands.",
                        ]
                    ),
                    GivePlayerItemEffect("crystal"),
                ),
            ),
        )
        self.place_feature(
            "crossroads",
            TextFeature(
                name="signpost",
                verb="Read",
                text=(
                    "NORTH -> Ruins\nEAST  -> Lake\nWEST  -> Forest\nSOUTH -> Village"
                ),
            ),
        )

    def build_npcs(self) -> None:
        elder_topics = [
            DialogueTopic(
                key="elder_quest",
                title="Talk to the elder",
                lines=[
                    "The village fountain is dry.",
                    "Bring back the crystal from the old tower and restore the village.",
                ],
                blocked_flags={"quest_started", "game_won", "crystal_taken"},
                once=True,
                outcome_effect=SetFlagEffect("quest_started"),
            ),
            DialogueTopic(
                key="elder_reminder",
                title="Ask what to do next",
                lines=[
                    "Search the valley. The forest, lake, cave, and ruins all hide clues."
                ],
                required_flags={"quest_started"},
                blocked_flags={"game_won", "crystal_taken"},
            ),
            DialogueTopic(
                key="elder_win",
                title="Return the crystal",
                lines=[
                    "You found the crystal!",
                    "The elder raises it over the fountain.",
                    "Water bursts upward. The village is saved!",
                ],
                required_items=["crystal"],
                blocked_flags={"game_won"},
                once=True,
                outcome_effect=SetFlagEffect("game_won"),
            ),
        ]
        self.place_npc(
            "village",
            NPC(
                name="Elder",
                base_stats=Stats(20, 1, 2, 0),
                description="An old elder stands near the dry fountain.",
                dialogue_topics=elder_topics,
            ),
        )

        fisherman_topics = [
            DialogueTopic(
                key="fisherman_talk",
                title="Talk to the fisherman",
                lines=[],
                outcome_effect=ConditionalEffect(
                    required_items=["herb"],
                    success_effect=CompositeEffect(
                        PrintEffect(
                            [
                                "Fisherman: Ah, a fresh herb. I will trade you my lantern for it.",
                                "You give the herb to the fisherman.",
                                "You receive a lantern.",
                            ]
                        ),
                        GivePlayerItemEffect("lantern"),
                    ),
                    failure_effect=ConditionalEffect(
                        required_flags={"has_lantern"},
                        success_effect=PrintEffect("Fisherman: Use that lantern well."),
                        failure_effect=PrintEffect(
                            [
                                "Fisherman: The cave is too dark without a lantern.",
                                "Fisherman: Bring me a useful herb from the forest and we can trade.",
                            ]
                        ),
                    ),
                ),
            ),
        ]
        self.place_npc(
            "lake",
            NPC(
                name="Fisherman",
                base_stats=Stats(20, 1, 2, 0),
                description="A fisherman waits quietly by the shore.",
                dialogue_topics=fisherman_topics,
            ),
        )

        self.place_npc(
            "cave",
            NPC(
                name="Giant Spider",
                base_stats=Stats(6, 5, 5, 3),
                description="A giant spider guards something shiny in the darkness.",
                hostile=True,
                reward_items=["silver_key"],
                reward_flags={"spider_defeated"},
                post_victory_lines=[
                    "The defeated spider lies still, and the cave is quiet now."
                ],
            ),
        )

    def scatter_items(self) -> None:
        self.place_item("forest", "herb")
        self.place_item("forest", "sword")

    def refresh_descriptions(self) -> None:
        self.get("village").description = (
            "You are in the village square. The fountain is flowing again, and the villagers are smiling."
            if self._flag("game_won")
            else "You are in a quiet village square. An old elder stands near a dry fountain."
        )
        self.get(
            "crossroads"
        ).description = (
            "You stand at a crossroads. Paths lead north, east, south, and west."
        )

        herb_taken = self._flag("herb_taken")
        sword_taken = self._flag("sword_taken")
        if herb_taken and sword_taken:
            forest_desc = "You are in a shady forest. The herb patch has been picked clean, and the fallen log has already been searched."
        elif herb_taken:
            forest_desc = "You are in a shady forest. Near a fallen log, you think you might still find something useful."
        elif sword_taken:
            forest_desc = "You are in a shady forest. You notice a patch of useful herbs growing nearby."
        else:
            forest_desc = (
                "You are in a shady forest. You notice herbs growing near a fallen log."
            )
        self.get("forest").description = forest_desc

        self.get(
            "lake"
        ).description = "You arrive at a peaceful lake. A fisherman waits by the shore."
        self.get(
            "cave_entrance"
        ).description = "A dark cave entrance opens in the hillside."
        self.get("cave").description = (
            "Inside the cave, the air is cold. The defeated spider lies still, and the cave is quiet now."
            if self._flag("spider_defeated")
            else "Inside the cave, the air is cold. A giant spider guards something shiny."
        )
        self.get(
            "ruins"
        ).description = "You stand among old ruins. A narrow path leads toward a tower."
        self.get("tower_gate").description = (
            "You stand before the tower gate. The lock hangs open."
            if self._flag("tower_unlocked")
            else "You stand before a locked tower gate."
        )
        self.get("tower_top").description = (
            "At the top of the tower, the pedestal is empty."
            if self._flag("crystal_taken")
            else "At the top of the tower, a glowing crystal rests on a pedestal."
        )

    def bind_game(self, game: "Game") -> None:
        self._flag = lambda name: name in game.flags
        self.refresh_descriptions()

    def on_location_enter(self, game: "Game", location: Location) -> None:
        self.bind_game(game)

    def on_item_picked_up(self, game: "Game", item_id: str) -> None:
        if item_id == "herb":
            game.flags.add("herb_taken")
        elif item_id == "sword":
            game.flags.add("sword_taken")
            auto_equip = input("Equip the Old Sword now? [Y/n] ").strip().lower()
            if auto_equip in {"", "y", "yes"}:
                ok, message = game.player.equip("sword", self.item_db)
                print(message)
        elif item_id == "lantern":
            game.flags.add("has_lantern")
            if game.player.has_item("herb"):
                game.player.remove_item("herb")
        self.bind_game(game)

    def on_npc_defeated(self, game: "Game", npc: NPC) -> None:
        if npc.name == "Giant Spider":
            print("You find a silver key near its nest.")
        self.bind_game(game)


# ============================================================
# Engines
# ============================================================


class Engine:
    def run(self, game: "Game") -> None:
        raise NotImplementedError


class ExplorationEngine(Engine):
    def run(self, game: "Game") -> None:
        location = game.current_location()
        divider(f"{game.world.name} - {location.name}")
        print(location.description)
        print(
            f"\n[HP {game.player.health}/{game.player.total_max_hp(game.world.item_db)}]"
        )

        if location.items:
            print("\nItems here:")
            for item_id in location.items:
                print(f"- {game.item_name(item_id)}")

        live_npcs = [
            npc for npc in location.npcs if npc.is_alive() and not npc.defeated
        ]
        if live_npcs:
            print("\nPeople / creatures here:")
            for npc in live_npcs:
                print(f"- {npc.name} ({npc.mood_label()})")

        if location.features:
            print("\nNotable features:")
            for feature in location.features:
                print(f"- {feature.name}")

        game.show_goal()

        choices = []
        for exit_obj in location.exits:
            destination = game.world.get(exit_obj.destination)
            text = f"Go {exit_obj.direction} to {destination.name}"
            if game.exit_is_blocked(exit_obj):
                text += " [blocked]"
            choices.append({"kind": "move", "text": text, "value": exit_obj})

        for item_id in location.items:
            choices.append(
                {
                    "kind": "take_item",
                    "text": f"Take {game.item_name(item_id)}",
                    "value": item_id,
                }
            )

        for npc in live_npcs:
            choices.append({"kind": "npc", "text": npc.menu_text(), "value": npc})

        for feature in location.features:
            choices.append(
                {"kind": "feature", "text": feature.menu_text(), "value": feature}
            )

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
    def run(self, game: "Game") -> None:
        npc: NPC = game.context["npc"]

        divider(f"Interacting with {npc.name}")
        print(npc.description)
        print(f"Mood: {npc.mood_label()}")
        print(f"Health: {npc.health}/{npc.total_max_hp(game.world.item_db)}")

        options = []
        if npc.can_talk(game):
            options.append(
                {"kind": "talk", "text": f"Talk to {npc.name}", "value": npc}
            )
        if npc.can_attack():
            options.append(
                {"kind": "attack", "text": f"Fight {npc.name}", "value": npc}
            )
        options.append({"kind": "back", "text": "Step away", "value": None})

        choice = game.choose(options, prompt="\nChoose an interaction: ")
        kind = choice["kind"]
        if kind == "talk":
            game.enter_mode("dialogue", npc=npc)
        elif kind == "attack":
            npc.on_player_attack(game)
            game.enter_mode("combat", npc=npc)
        elif kind == "back":
            game.enter_mode("exploration")


class DialogueEngine(Engine):
    def run(self, game: "Game") -> None:
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
        game.world.on_location_enter(game, game.current_location())
        game.enter_mode("npc", npc=npc)


class CombatEngine(Engine):
    def run(self, game: "Game") -> None:
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
                if not enemy.is_alive():
                    print(f"The {enemy.name.lower()} is defeated.")
                    enemy.on_defeat(game)
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
                print("You run back to safety.")
                enemy.hostile = True
                game.player.location = "cave_entrance"
                game.world.on_location_enter(game, game.current_location())
                game.enter_mode("exploration")
                return

            if enemy.is_alive() and enemy.hostile:
                enemy_action, enemy_payload = enemy.controller.choose_combat_action(
                    game, enemy, game.player
                )
                if enemy_action == "item" and enemy_payload is not None:
                    ok, _msg, healed = enemy.use_consumable(
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

        game.enter_mode("exploration")


class MenuEngine(Engine):
    def run(self, game: "Game") -> None:
        divider("MENU")
        options = [
            {"kind": "status", "text": "View status", "value": None},
            {"kind": "loadout", "text": "Manage loadout", "value": None},
            {"kind": "journal", "text": "View journal / flags", "value": None},
            {"kind": "back", "text": "Return to exploration", "value": None},
            {"kind": "quit", "text": "Quit game", "value": None},
        ]
        choice = game.choose(options, prompt="Choose a menu option: ")
        if choice["kind"] == "status":
            game.player.show_status(game.world.item_db)
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
    def run(self, game: "Game") -> None:
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
            _ok, message = player.equip(choice["value"], item_db)
            print(message)
            game.enter_mode("loadout")
        elif choice["kind"] == "unequip":
            _ok, message = player.unequip(choice["value"], item_db)
            print(message)
            game.enter_mode("loadout")
        elif choice["kind"] == "back":
            game.enter_mode("menu")


# ============================================================
# Game director / router
# ============================================================


class Game:
    def __init__(self, player_name: str = "Tav", world: World | None = None):
        self.world = world or ValleyQuestWorld()
        self.player = Character(
            name=player_name,
            base_stats=Stats(max_hp=20, attack_min=2, attack_max=4, defense=0),
            controller=PlayerController(),
            location="village",
        )
        self.flags: set[str] = {"game_started"}
        self.running = True
        self.mode = "exploration"
        self.context: dict[str, object] = {}
        self.engines: dict[str, Engine] = {
            "exploration": ExplorationEngine(),
            "npc": NPCInteractionEngine(),
            "dialogue": DialogueEngine(),
            "combat": CombatEngine(),
            "menu": MenuEngine(),
            "loadout": LoadoutEngine(),
        }
        self.world.on_location_enter(self, self.current_location())

    def item_name(self, item_id: str | None) -> str:
        if item_id is None:
            return "empty"
        return self.world.item(item_id).name

    def current_location(self) -> Location:
        return self.world.get(self.player.location)

    def enter_mode(self, mode: str, **context: object) -> None:
        self.mode = mode
        self.context = context

    def show_goal(self) -> None:
        if "game_won" in self.flags:
            print("\nGoal: The village has been saved.")
        elif "crystal_taken" in self.flags:
            print("\nGoal: Return the crystal to the elder.")
        elif "quest_started" in self.flags:
            print("\nGoal: Explore the valley and recover the crystal.")
        else:
            print("\nGoal: Talk to the elder.")

    def show_journal(self) -> None:
        divider("JOURNAL / FLAGS")
        for flag in sorted(self.flags):
            print(f"- {flag}")
        if not self.flags:
            print("No flags set.")

    def choose(self, options: list[dict], prompt: str = "Choose: ") -> dict:
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option['text']}")
        while True:
            answer = input(prompt).strip().lower()
            if answer == "quit":
                print("Thanks for playing!")
                self.running = False
                return {"kind": "quit", "text": "Quit", "value": None}
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

    def run(self) -> None:
        divider(f"Welcome to {self.world.name}")
        print(
            "This version uses the larger mode-driven engine, but the smaller valley story."
        )
        print("Tip: type 'quit' at any menu prompt to leave the game.")
        while self.running:
            if not self.player.is_alive():
                divider("Defeat")
                print("Game over.")
                break
            engine = self.engines[self.mode]
            engine.run(self)
            if self.running and self.player.is_alive():
                prompt_continue()


def main() -> None:
    game = Game(player_name="Tav", world=ValleyQuestWorld())
    game.run()


if __name__ == "__main__":
    main()
