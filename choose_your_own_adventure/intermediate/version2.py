"""
Intermediate version 2: the SAME adventure, now organized as game objects.

Compare this with intermediate/version1.py. We are not adding a bigger story yet. We are
learning how a program can own its state and expose a small public API.

New ideas in this version:
- Room and Choice dataclasses
- one Game object that owns runtime state
- methods such as describe(), choices(), and apply()
- separating the game rules from the console input/output loop

That last point matters later: a terminal UI, a graphical UI, tests, or an AI
player can all drive the same Game object without changing the game rules.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Choice:
    action: str
    text: str


@dataclass(frozen=True)
class Room:
    key: str
    description: str
    exits: dict[str, str]


@dataclass
class Player:
    name: str = "Tav"
    location: str = "village"
    inventory: list[str] = field(default_factory=list)


ROOMS = {
    "village": Room(
        key="village",
        description="You are in a small village. A path leads north into the forest.",
        exits={"north to the forest": "forest"},
    ),
    "forest": Room(
        key="forest",
        description="You are in a quiet forest. A cave lies east of an old stump.",
        exits={"south to the village": "village", "east to the cave": "cave"},
    ),
    "cave": Room(
        key="cave",
        description="You are inside a dark cave. A locked treasure chest waits here.",
        exits={"west to the forest": "forest"},
    ),
}


class Game:
    """Own the game state and rules, but do not read input or print output."""

    def __init__(self, player_name="Tav"):
        self.player = Player(name=player_name)
        self.key_taken = False
        self.won = False

    def describe(self):
        """Return lines describing the current state."""
        room = ROOMS[self.player.location]
        inventory = ", ".join(self.player.inventory) if self.player.inventory else "empty"
        return [
            room.description,
            f"Player: {self.player.name}",
            f"Inventory: {inventory}",
        ]

    def choices(self):
        """Return the actions that are legal right now."""
        room = ROOMS[self.player.location]
        choices = [
            Choice(action=f"go:{destination}", text=f"Go {label}")
            for label, destination in room.exits.items()
        ]

        if self.player.location == "village":
            choices.append(Choice("talk_villager", "Talk to the villager"))
        elif self.player.location == "forest" and not self.key_taken:
            choices.append(Choice("search_stump", "Look inside the old stump"))
        elif self.player.location == "cave":
            choices.append(Choice("open_chest", "Open the treasure chest"))

        return choices

    def apply(self, action):
        """Apply one currently legal action and return result text."""
        legal_actions = {choice.action for choice in self.choices()}
        if action not in legal_actions:
            raise ValueError(f"Action is not legal right now: {action!r}")

        if action.startswith("go:"):
            self.player.location = action.removeprefix("go:")
            return []

        if action == "talk_villager":
            return ["The villager says: 'I lost a little brass key near an old stump.'"]

        if action == "search_stump":
            self.player.inventory.append("brass key")
            self.key_taken = True
            return ["Inside the stump you find a little brass key!"]

        if action == "open_chest":
            if "brass key" not in self.player.inventory:
                return ["The chest is locked. You need a key."]
            self.won = True
            return ["The key turns. The chest opens. You found the treasure!"]

        raise AssertionError(f"Unhandled legal action: {action}")


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
    """A tiny user interface around the Game API."""
    print("Welcome to Tiny Adventure!")
    print("Find the treasure in the cave. Type 'quit' at any prompt to stop.")

    while not game.won:
        print("\n" + "=" * 56)
        for line in game.describe():
            print(line)
        print("\nWhat do you want to do?")
        action = choose(game.choices())
        if action is None:
            print("Goodbye!")
            return
        for line in game.apply(action):
            print(line)

    print("\nYou win! Thanks for playing.")


if __name__ == "__main__":
    run_console(Game())
