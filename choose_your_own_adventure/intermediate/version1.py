"""
Intermediate version 1: the SAME adventure, now data-driven.

Compare this file with beginner/version2.py. The player still visits the same three
rooms and solves the same key-and-chest puzzle.

New ideas in this version:
- a dataclass for related player state
- room data separated from game logic
- one small function per action
- a dictionary that maps action names to functions

This is a useful middle ground for student projects: organized, but still
small enough to understand without an engine framework.
"""

from dataclasses import dataclass, field


@dataclass
class Player:
    name: str = "Tav"
    location: str = "village"
    inventory: list[str] = field(default_factory=list)


ROOMS = {
    "village": {
        "description": "You are in a small village. A path leads north into the forest.",
        "exits": [("Go north to the forest", "forest")],
        "choices": [{"text": "Talk to the villager", "action": "talk_villager"}],
    },
    "forest": {
        "description": "You are in a quiet forest. A cave lies east of an old stump.",
        "exits": [
            ("Go south to the village", "village"),
            ("Go east to the cave", "cave"),
        ],
        "choices": [{"text": "Look inside the old stump", "action": "search_stump"}],
    },
    "cave": {
        "description": "You are inside a dark cave. A locked treasure chest waits here.",
        "exits": [("Go west to the forest", "forest")],
        "choices": [{"text": "Open the treasure chest", "action": "open_chest"}],
    },
}


def show_status(player):
    room = ROOMS[player.location]
    print("\n" + "=" * 56)
    print(room["description"])
    print(f"Player: {player.name}")
    print("Inventory:", ", ".join(player.inventory) if player.inventory else "empty")


def choose(choices):
    """Return an action string, or None when the player quits."""
    while True:
        print("\nWhat do you want to do?")
        for number, (text, action) in enumerate(choices, start=1):
            print(f"  {number}. {text}")
        answer = input("> ").strip()
        if answer.lower() == "quit":
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1][1]
        print("Please enter one of the menu numbers.")


def build_choices(player, state):
    """Build the menu from room data plus choices that depend on state."""
    choices = []

    for text, destination in ROOMS[player.location]["exits"]:
        choices.append((text, f"go:{destination}"))

    # A normal story choice lives with the room that owns it.  Students can
    # add rooms and choices by copying data blocks before learning dispatch.
    for index, spec in enumerate(ROOMS[player.location].get("choices", [])):
        action = spec.get("action", f"room:{index}")
        choices.append((spec["text"], action))

    return choices


def talk_villager(player, state):
    return ["The villager says: 'I lost a little brass key near an old stump.'"]


def search_stump(player, state):
    if state["key_taken"]:
        return ["You already searched the stump."]
    player.inventory.append("brass key")
    state["key_taken"] = True
    return ["Inside the stump you find a little brass key!"]


def open_chest(player, state):
    if "brass key" not in player.inventory:
        return ["The chest is locked. You need a key."]
    state["game_won"] = True
    return ["The key turns. The chest opens. You found the treasure!"]


# Functions are values in Python, so they can live in a dictionary.
# This replaces a growing `elif action == ...` chain with a lookup.
ACTION_HANDLERS = {
    "talk_villager": talk_villager,
    "search_stump": search_stump,
    "open_chest": open_chest,
}


def handle_action(action, player, state):
    if action.startswith("room:"):
        index = int(action.removeprefix("room:"))
        spec = ROOMS[player.location]["choices"][index]
        return list(spec.get("result", []))

    if action.startswith("go:"):
        destination = action.removeprefix("go:")
        player.location = destination
        return []

    handler = ACTION_HANDLERS[action]
    return handler(player, state)


def main():
    print("Welcome to Tiny Adventure!")
    print("Find the treasure in the cave. Type 'quit' at any prompt to stop.")

    player = Player()
    state = {
        "key_taken": False,
        "game_won": False,
    }

    while not state["game_won"]:
        show_status(player)
        action = choose(build_choices(player, state))
        if action is None:
            print("Goodbye!")
            return

        for line in handle_action(action, player, state):
            print(line)

    print("\nYou win! Thanks for playing.")


if __name__ == "__main__":
    main()
