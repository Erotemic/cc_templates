"""
Intermediate version 3: a richer adventure in one file.

The earlier beginner/intermediate versions kept the story tiny while the code
organization changed. Now we use those ideas to build a larger game with:
- more rooms
- items and quest flags
- an NPC interaction
- simple combat
- a locked destination
- a win condition

The important architecture is still small:

    Game.describe() -> text about current state
    Game.choices()  -> legal Choice objects
    Game.apply()    -> change state and return result text

The Game never calls input() or print(). The console loop at the bottom is a
separate user interface. Advanced version 1 will move these pieces into a reusable
package without changing that public shape.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Choice:
    action: str
    text: str


@dataclass(frozen=True)
class Room:
    key: str
    name: str
    description: str
    exits: dict[str, str]


@dataclass(frozen=True)
class EnemySpec:
    key: str
    name: str
    hp: int
    attack: int


@dataclass
class Player:
    name: str = "Tav"
    location: str = "village"
    hp: int = 18
    max_hp: int = 18
    attack: int = 5
    gold: int = 4
    inventory: list[str] = field(default_factory=list)
    flags: set[str] = field(default_factory=set)

    def has(self, item):
        return item in self.inventory


ROOMS = {
    "village": Room(
        "village",
        "Willow Village",
        "Lanterns glow around a quiet village square.",
        {"north to the crossroads": "crossroads"},
    ),
    "crossroads": Room(
        "crossroads",
        "Crossroads",
        "Three old paths meet beneath a weathered stone marker.",
        {
            "south to the village": "village",
            "west to the forest": "forest",
            "east to the lake": "lake",
            "north to the ruins": "ruins",
        },
    ),
    "forest": Room(
        "forest",
        "Moonwood Forest",
        "Silver leaves whisper around a moss-covered shrine.",
        {"east to the crossroads": "crossroads"},
    ),
    "lake": Room(
        "lake",
        "Mirror Lake",
        "A patient fisherman sits beside a perfectly still lake.",
        {"west to the crossroads": "crossroads"},
    ),
    "ruins": Room(
        "ruins",
        "Old Ruins",
        "Broken pillars surround a tower gate. Something skitters in the dust.",
        {
            "south to the crossroads": "crossroads",
            "through the tower gate": "tower",
        },
    ),
    "tower": Room(
        "tower",
        "Star Tower",
        "At the top of the tower, blue starlight pools around a crystal pedestal.",
        {"back to the ruins": "ruins"},
    ),
}

ENEMIES = {
    "ruin_spider": EnemySpec("ruin_spider", "ruin spider", hp=10, attack=2),
}


class Game:
    """State and rules for the Star Crystal adventure."""

    def __init__(self, player_name="Tav"):
        self.player = Player(name=player_name)
        self.won = False
        self.lost = False
        self.combat_enemy = None
        self.combat_hp = 0

    @property
    def over(self):
        return self.won or self.lost

    def describe(self):
        if self.combat_enemy is not None:
            enemy = ENEMIES[self.combat_enemy]
            return [
                f"Combat: {enemy.name}",
                f"Your HP: {self.player.hp}/{self.player.max_hp}",
                f"Enemy HP: {self.combat_hp}/{enemy.hp}",
            ]

        room = ROOMS[self.player.location]
        lines = [
            f"{room.name}",
            room.description,
            f"HP: {self.player.hp}/{self.player.max_hp}    Gold: {self.player.gold}",
            "Inventory: " + (", ".join(self.player.inventory) or "empty"),
        ]

        if self.player.location == "village" and "quest_started" not in self.player.flags:
            lines.append("The village elder watches the northern road with concern.")
        if self.player.location == "forest" and not self.player.has("moon herb"):
            lines.append("A pale green plant grows beside the shrine.")
        if self.player.location == "lake" and not self.player.has("tower key"):
            lines.append("The fisherman turns a tiny brass key between his fingers.")
        if self.player.location == "ruins" and "spider_defeated" not in self.player.flags:
            lines.append("A ruin spider guards the tower approach.")
        if self.player.location == "tower" and not self.won:
            lines.append("The Star Crystal is close enough to touch.")

        return lines

    def choices(self):
        if self.over:
            return []

        if self.combat_enemy is not None:
            return [
                Choice("combat:attack", "Attack"),
                Choice("combat:run", "Run back to the crossroads"),
            ]

        room = ROOMS[self.player.location]
        choices = []

        for label, destination in room.exits.items():
            # The tower gate is ordinary game logic, not a special Exit class.
            if destination == "tower":
                gate_open = (
                    self.player.has("tower key")
                    and "spider_defeated" in self.player.flags
                )
                if not gate_open:
                    continue
            choices.append(Choice(f"go:{destination}", f"Go {label}"))

        if self.player.location == "village":
            choices.append(Choice("talk_elder", "Talk to the village elder"))
            if self.player.hp < self.player.max_hp:
                choices.append(Choice("rest", "Rest at the inn"))

        elif self.player.location == "forest" and not self.player.has("moon herb"):
            choices.append(Choice("take_herb", "Pick the moon herb"))

        elif self.player.location == "lake" and not self.player.has("tower key"):
            choices.append(Choice("talk_fisher", "Talk to the fisherman"))

        elif self.player.location == "ruins":
            if "spider_defeated" not in self.player.flags:
                choices.append(Choice("fight_spider", "Face the ruin spider"))
            if not self.player.has("tower key"):
                choices.append(Choice("inspect_gate", "Inspect the locked tower gate"))

        elif self.player.location == "tower":
            choices.append(Choice("take_crystal", "Take the Star Crystal"))

        return choices

    def apply(self, action):
        legal = {choice.action for choice in self.choices()}
        if action not in legal:
            raise ValueError(f"Action is not legal right now: {action!r}")

        if action.startswith("go:"):
            self.player.location = action.removeprefix("go:")
            return []

        if action == "combat:attack":
            return self.attack_enemy()
        if action == "combat:run":
            self.combat_enemy = None
            self.combat_hp = 0
            self.player.location = "crossroads"
            return ["You retreat to the crossroads."]

        return self.apply_world_action(action)

    def apply_world_action(self, action):
        if action == "talk_elder":
            self.player.flags.add("quest_started")
            return [
                "Elder: 'The Star Crystal once protected our valley.'",
                "Elder: 'The old tower is sealed. Ask around; someone may still have its key.'",
            ]

        if action == "rest":
            self.player.hp = self.player.max_hp
            return ["A warm meal and a quiet bed restore your health."]

        if action == "take_herb":
            self.player.inventory.append("moon herb")
            return ["You carefully pick the moon herb."]

        if action == "talk_fisher":
            if self.player.has("moon herb"):
                self.player.inventory.remove("moon herb")
                self.player.inventory.append("tower key")
                return [
                    "Fisherman: 'That herb is exactly what I needed for my tea.'",
                    "He trades you an old tower key.",
                ]
            return [
                "Fisherman: 'I can part with this old key for a moon herb from the western forest.'"
            ]

        if action == "fight_spider":
            self.start_combat("ruin_spider")
            return ["The ruin spider lowers its fangs and rushes toward you!"]

        if action == "inspect_gate":
            return ["The tower gate is locked. Its small keyhole is still intact."]

        if action == "take_crystal":
            self.won = True
            return [
                "The Star Crystal lifts from its pedestal and fills the tower with blue light.",
                "You recovered the Star Crystal. The valley is safe!",
            ]

        raise AssertionError(f"Unhandled legal action: {action}")

    def start_combat(self, enemy_key):
        enemy = ENEMIES[enemy_key]
        self.combat_enemy = enemy_key
        self.combat_hp = enemy.hp

    def attack_enemy(self):
        enemy = ENEMIES[self.combat_enemy]
        lines = []

        self.combat_hp = max(0, self.combat_hp - self.player.attack)
        lines.append(f"You hit the {enemy.name} for {self.player.attack} damage.")

        if self.combat_hp == 0:
            lines.append(f"You defeated the {enemy.name}!")
            defeated_key = self.combat_enemy
            self.combat_enemy = None
            self.player.flags.add("spider_defeated")
            if defeated_key == "ruin_spider":
                lines.append("The path to the tower gate is clear.")
            return lines

        self.player.hp = max(0, self.player.hp - enemy.attack)
        lines.append(f"The {enemy.name} hits you for {enemy.attack} damage.")
        if self.player.hp == 0:
            self.lost = True
            self.combat_enemy = None
            lines.append("You collapse. The adventure ends here.")
        return lines


def choose(choices):
    while True:
        for number, choice in enumerate(choices, start=1):
            print(f"  {number}. {choice.text}")
        answer = input("> ").strip()
        if answer.lower() == "quit":
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1].action
        print("Please enter one of the menu numbers.")


def run_console(game):
    """Terminal presentation. It knows nothing about the game's rules."""
    print("Star Crystal Adventure")
    print("Type 'quit' at any prompt to stop.")

    while not game.over:
        print("\n" + "=" * 64)
        for line in game.describe():
            print(line)
        print("\nWhat do you want to do?")
        action = choose(game.choices())
        if action is None:
            print("Goodbye!")
            return
        for line in game.apply(action):
            print(line)

    print("\n" + ("YOU WIN" if game.won else "GAME OVER"))


if __name__ == "__main__":
    run_console(Game())
