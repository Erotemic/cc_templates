"""
Version 2: a small, organized game script.

This version keeps the same small adventure, but organizes the code into
clearer pieces:
- plain data for rooms and state
- a Player dataclass
- helper functions for world description and choices
- one function per action
- a small dispatch table for action handling

Use this version to teach:
- separating data from behavior
- writing focused helper functions
- reducing repetition without building a full engine
- how a small program can become easier to read and extend

This is a good "middle ground" version:
more structured than the giant if / else file, but still small enough for
students to hold in their heads.
"""

# `dataclass` is a decorator that auto-generates __init__ (and friends)
# for a class so you can declare a "record" type in a few lines.
# `field(default_factory=list)` says "if no value is passed, start with a
# brand new empty list" — important because using `= []` as a default
# would share one list across every instance (a classic Python gotcha).
from dataclasses import dataclass, field


def typewriter_print(prefix, text, word_delay=0.1):
    """
    Simulates a typewriter effect with a delay between each character.

    Example:
        >>> typewriter_print("Narrator: ", "Welcome to the Adventure Game! Your journey begins now.")
    """
    import sys
    import time

    sys.stdout.write(prefix)
    words = text.split(" ")  # Split the text into words
    for word in words:
        char_delay = word_delay / (len(word) + 1)
        for char in word:  # Print each character of the word with a delay
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(char_delay)
        sys.stdout.write(" ")  # Print space after the word
        sys.stdout.flush()
        time.sleep(char_delay)  # Delay between words
    sys.stdout.write("\n")  # Newline after the dialog


# ============================================================
# Data
# ============================================================
# Big idea: pull the *world* (rooms, exits, default state) out of the
# code and into plain data structures. Adding a new room is now just
# adding a key to a dictionary — you don't have to touch the game loop
# or the action tree the way version 1 made you do.


# Maps each room key -> list of (visible text, destination room key).
# When the player is in a room, we can look up "where can I go from here?"
# in one line: ROOM_CHOICES[player.location].
ROOM_CHOICES = {
    "village": [("Go north to the crossroads", "crossroads")],
    "crossroads": [
        ("Go south to the village", "village"),
        ("Go west to the forest", "forest"),
        ("Go east to the lake", "lake"),
        ("Go north to the ruins", "ruins"),
    ],
    "forest": [
        ("Go east to the crossroads", "crossroads"),
        ("Go north to the cave entrance", "cave_entrance"),
    ],
    "lake": [("Go west to the crossroads", "crossroads")],
    "cave_entrance": [
        ("Go south to the forest", "forest"),
        ("Enter the cave", "enter_cave"),
    ],
    "cave": [("Go south to the cave entrance", "cave_entrance")],
    "ruins": [
        ("Go south to the crossroads", "crossroads"),
        ("Go north to the tower gate", "tower_gate"),
    ],
    "tower_gate": [("Go south to the ruins", "ruins")],
    "tower_top": [("Go down to the tower gate", "tower_gate")],
}

# A `set` of just the room keys — handy for "is this action a room name?"
# checks (sets give us fast `in` lookups).
ROOM_NAMES = set(ROOM_CHOICES)

# All the boolean flags live in one dictionary instead of being eight
# separate variables like in version 1. Now we can copy this dict at the
# start of a new game with `dict(STATE_DEFAULTS)` and pass the whole
# state around as a single argument — far easier to manage.
STATE_DEFAULTS = {
    "quest_started": False,
    "spider_alive": True,
    "herb_taken": False,
    "sword_taken": False,
    "tower_unlocked": False,
    "crystal_taken": False,
    "game_won": False,
    "quit_game": False,
}


# ============================================================
# Player
# ============================================================


# A class is a custom type. With @dataclass, we just declare the fields
# (with optional defaults) and Python writes the boilerplate for us.
# We can now write Player("Tav") and get an object with a name, a default
# location, default health, and a fresh empty inventory.
#
# `name: str`, `health: int`, ... are *type hints*. Python doesn't
# enforce them at runtime, but they document intent and let editors and
# type-checkers catch mistakes.
#
# The methods (has_item, add_item, remove_item) are simple wrappers that
# *attach behavior to the data*. From now on, anywhere we have a Player
# we can just say `player.add_item("herb")` instead of poking at the
# list directly. This is the start of object-oriented thinking.
@dataclass
class Player:
    """
    Store information about a player
    """

    name: str
    location: str = "village"
    health: int = 20
    inventory: list[str] = field(default_factory=list)

    def has_item(self, item):
        return item in self.inventory

    def add_item(self, item):
        # Avoid duplicates — having two "lanterns" wouldn't help anything.
        if item not in self.inventory:
            self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)


# ============================================================
# Small user-interface helpers
# ============================================================


def show_action(action_text):
    print("\n" + "=" * 40)
    print(f"You chose to: {action_text}")
    print("=" * 40)


def show_result(lines):
    """
    Show the result of an action in one clear block.

    Dialogue lines use the typewriter effect.
    Other lines print normally so the game keeps a readable pace.
    """
    if isinstance(lines, str):
        lines = [lines]

    if not lines:
        return

    print("\nResult:")
    for line in lines:
        if ": " in line:
            speaker, text = line.split(": ", 1)
            typewriter_print(f"{speaker}: ", text, word_delay=0.06)
        else:
            print(line)


def pause():
    input("\nPress Enter to continue...")


# ============================================================
# World helpers
# ============================================================


def describe_location(location, state):
    """
    Return a description of the current location.

    Some descriptions change based on game state so the world feels
    more consistent to the player.
    """
    # Notice the structure: this function *returns* a string instead of
    # printing it. That's a deliberate choice — separating "decide what
    # to say" from "say it" makes the function easier to reuse and test.
    if location == "village":
        if state["game_won"]:
            return "You are in the village square. The fountain is flowing again, and the villagers are smiling."
        return "You are in a quiet village square. An old elder stands near a dry fountain."

    if location == "crossroads":
        return "You stand at a crossroads. Paths lead north, east, south, and west."

    if location == "forest":
        if state["herb_taken"] and state["sword_taken"]:
            return "You are in a shady forest. The herb patch has been picked clean, and the fallen log has already been searched."
        if state["herb_taken"]:
            return "You are in a shady forest. Near a fallen log, you think you might still find something useful."
        if state["sword_taken"]:
            return "You are in a shady forest. You notice a patch of useful herbs growing nearby."
        return "You are in a shady forest. You notice herbs growing near a fallen log."

    if location == "lake":
        return "You arrive at a peaceful lake. A fisherman waits by the shore."

    if location == "cave_entrance":
        return "A dark cave entrance opens in the hillside."

    if location == "cave":
        if state["spider_alive"]:
            return "Inside the cave, the air is cold. A giant spider guards something shiny."
        return "Inside the cave, the air is cold. The defeated spider lies still, and the cave is quiet now."

    if location == "ruins":
        return "You stand among old ruins. A narrow path leads toward a tower."

    if location == "tower_gate":
        if state["tower_unlocked"]:
            return "You stand before the tower gate. The lock hangs open."
        return "You stand before a locked tower gate."

    if location == "tower_top":
        if state["crystal_taken"]:
            return "At the top of the tower, the pedestal is empty."
        return "At the top of the tower, a glowing crystal rests on a pedestal."

    return "This place seems unfamiliar."


def observe_surroundings(player, state):
    print("\nYou observe your surroundings")
    print(describe_location(player.location, state))


def show_status(player):
    print(f"\nPlayer: {player.name}")
    print(f"Health: {player.health}")
    if player.inventory:
        print("Inventory:", ", ".join(player.inventory))
    else:
        print("Inventory: empty")


def get_choices(player, state):
    """
    Add extra choices based on location and game state.
    Remove choices that no longer make sense.
    """
    # Start with the basic exits looked up from data, then layer extra
    # actions on top depending on context. This is much smaller than
    # version 1's giant if/elif tree because the *common* cases (room
    # exits) come straight from ROOM_CHOICES.
    # `list(...)` makes a copy so we don't mutate the original.
    choices = list(ROOM_CHOICES[player.location])

    if player.location == "village":
        choices.append(("Talk to the elder", "talk_elder"))

    if player.location == "lake":
        choices.append(("Talk to the fisherman", "talk_fisherman"))

    if player.location == "forest":
        if not state["herb_taken"]:
            choices.append(("Pick the herb", "pick_herb"))
        if not state["sword_taken"]:
            choices.append(("Look near the fallen log", "find_sword"))

    if player.location == "cave" and state["spider_alive"]:
        choices.append(("Fight the spider", "fight_spider"))

    if player.location == "tower_gate":
        if state["tower_unlocked"]:
            choices.append(("Go up into the tower", "tower_top"))
        else:
            choices.append(("Try to open the tower gate", "open_tower"))

    if player.location == "tower_top" and not state["crystal_taken"]:
        choices.append(("Take the crystal", "take_crystal"))

    return choices


# ============================================================
# Actions
# ============================================================
# One function per action. Each one takes (player, state) and returns a
# list of strings to print. Returning data instead of printing means the
# caller can decide *how* to present it — and we can later log it, show
# it in a different style, etc., without changing this code.
#
# Compare this to the giant elif-tree in version 1: there, picking the
# herb and reading the elder's lines were two more branches in one huge
# function. Here they're independent functions, each easy to read in isolation.


def talk_to_elder(player, state):
    """
    Handle elder dialogue.
    """
    lines = []

    if player.has_item("crystal") and not state["game_won"]:
        if not state["quest_started"]:
            lines.append(
                "Elder: You found the crystal before I even had time to explain the quest!"
            )
            lines.append("Elder: No matter. You have saved us all.")
        else:
            lines.append("Elder: You found the crystal!")

        lines.append("The elder raises it over the fountain.")
        lines.append("Water bursts upward. The village is saved!")
        state["quest_started"] = True
        state["game_won"] = True

    elif not state["quest_started"]:
        lines.append("Elder: The village fountain is dry.")
        lines.append(
            "Elder: Bring back the crystal from the old tower and restore the village."
        )
        state["quest_started"] = True

    else:
        lines.append(
            "Elder: Search the valley. The forest, lake, cave, and ruins all hide clues."
        )

    return lines


def talk_to_fisherman(player, state):
    """
    Handle fisherman dialogue and trade.
    """
    lines = []

    if player.has_item("herb") and not player.has_item("lantern"):
        player.remove_item("herb")
        player.add_item("lantern")
        lines.append("Fisherman: Ah, a fresh herb. I will trade you my lantern for it.")
        lines.append("You give the herb to the fisherman.")
        lines.append("You receive a lantern.")
    elif not player.has_item("lantern"):
        lines.append("Fisherman: The cave is too dark without a lantern.")
        lines.append(
            "Fisherman: Bring me a useful herb from the forest and we can trade."
        )
    else:
        lines.append("Fisherman: Use that lantern well.")

    return lines


def pick_herb(player, state):
    if not state["herb_taken"]:
        state["herb_taken"] = True
        player.add_item("herb")
        return [
            "You pick a useful herb from the forest.",
            "You put the herb in your bag.",
        ]
    return ["You already picked the useful herb here."]


def find_sword(player, state):
    if not state["sword_taken"]:
        state["sword_taken"] = True
        player.add_item("sword")
        return [
            "You search near the fallen log.",
            "You find an old sword and take it with you.",
        ]
    return ["There is nothing else useful near the log."]


def enter_cave(player, state):
    if player.has_item("lantern"):
        player.location = "cave"
        return ["You light your lantern and step into the cave."]
    return [
        "It is too dark to enter safely.",
        "You need a lantern.",
    ]


def fight_spider(player, state):
    """
    A very simple combat example.
    """
    while state["spider_alive"] and player.health > 0:
        print("\n" + "=" * 40)
        print("The spider attacks!")
        print("=" * 40)

        print(f"Your health: {player.health}")
        print("\nWhat do you do?")
        print("1. Attack")
        print("2. Run away")

        choice = input("Enter your choice: ").strip().lower()

        if choice == "quit":
            state["quit_game"] = True
            return ["You leave the cave and abandon the adventure."]

        if choice == "1":
            if player.has_item("sword"):
                state["spider_alive"] = False
                player.add_item("silver key")
                show_result(
                    [
                        "You strike the spider with your sword.",
                        "The spider is defeated.",
                        "You find a silver key near its nest.",
                    ]
                )
                pause()
                return []
            player.health -= 5
            lines = [
                "You try to fight with your bare hands, but the spider stays out of reach.",
                "The spider bites you.",
                "You lose 5 health.",
            ]
            if player.health <= 0:
                lines.append("You were defeated by the spider.")
            show_result(lines)
            pause()
            continue

        if choice == "2":
            player.location = "cave_entrance"
            show_result(["You run back to the cave entrance."])
            pause()
            return []

        show_result(["Invalid choice."])
        pause()

    return []


def open_tower(player, state):
    if player.has_item("silver key"):
        state["tower_unlocked"] = True
        player.location = "tower_top"
        return [
            "You unlock the tower gate with the silver key.",
            "You climb the stairs to the top of the tower.",
        ]
    return ["The tower gate is locked. You need a key."]


def take_crystal(player, state):
    if not state["crystal_taken"]:
        state["crystal_taken"] = True
        player.add_item("crystal")
        return [
            "You take the glowing crystal from the pedestal.",
            "The crystal feels warm in your hands.",
        ]
    return ["The pedestal is already empty."]


def move_player(player, destination):
    player.location = destination
    move_text = {
        "tower_top": "You climb the stairs and enter the top of the tower.",
        "tower_gate": "You walk to the tower gate.",
        "cave_entrance": "You make your way to the cave entrance.",
        "crossroads": "You travel back to the crossroads.",
        "forest": "You head into the forest.",
        "lake": "You walk to the lake.",
        "village": "You return to the village.",
        "ruins": "You travel to the ruins.",
    }
    return [move_text.get(destination, f"You travel to the {destination}.")]


# ----- Dispatch table -----------------------------------------------------
# This is the key idea of version 2. Instead of one giant if/elif chain
# saying "if action == 'pick_herb': ... elif action == 'find_sword': ...",
# we keep a *dictionary* that maps each action name to the function that
# handles it. Looking up the right function becomes a single lookup.
#
# Functions are objects in Python — we can store them in a dict, pass
# them around, and call them later. `ACTIONS["pick_herb"]` returns the
# pick_herb function itself; adding `(...)` then calls it.
#
# Adding a new action is now: write a function, add one entry here.
ACTIONS = {
    "talk_elder": talk_to_elder,
    "talk_fisherman": talk_to_fisherman,
    "pick_herb": pick_herb,
    "find_sword": find_sword,
    "enter_cave": enter_cave,
    "fight_spider": fight_spider,
    "open_tower": open_tower,
    "take_crystal": take_crystal,
}


def handle_action(action, player, state):
    """
    Handle actions with a small dispatch table.
    """
    # Two kinds of action: moving to another room (the action value *is*
    # a room name), or one of the named ACTIONS above. We check each in
    # turn and fall through to a generic "not implemented" message.
    if action in ROOM_NAMES:
        return move_player(player, action)

    handler = ACTIONS.get(action)  # .get returns None if the key is missing
    if handler is not None:
        return handler(player, state)  # call the function we just looked up

    return ["That action is not implemented yet."]


# ============================================================
# Main game loop
# ============================================================


def start_game():
    # Compare this function with version 1's start_game! It is dramatically
    # shorter because all the room descriptions, choice-building, and
    # action-handling has moved into focused helpers above. The loop here
    # is now just: describe -> menu -> dispatch -> repeat.
    print("Welcome to the Adventure Game Template!")
    print("Tip: type 'quit' at any prompt to leave the game.")

    player_name = "Tav"
    # player_name = input("Enter your name: ")  # can get input here

    # One Player object holds all the player data.
    player = Player(player_name)
    # `dict(STATE_DEFAULTS)` makes a fresh copy of the defaults so editing
    # `state` doesn't change the template for future games.
    state = dict(STATE_DEFAULTS)

    # Main game loop
    while True:
        if state["quit_game"] or state["game_won"]:
            print("\nThanks for playing!")
            break

        if player.health <= 0:
            print("\nGame over.")
            break

        observe_surroundings(player, state)
        show_status(player)

        choices = get_choices(player, state)

        if not choices:
            print("There's nothing more to do here.")
            break

        print("\nWhat do you want to do?")
        for idx, (choice_text, _) in enumerate(choices, 1):
            print(f"{idx}. {choice_text}")

        user_input = input("\nEnter the number of your choice: ").strip().lower()

        if user_input == "quit":
            print("Thanks for playing!")
            break

        try:
            choice_idx = int(user_input) - 1
            action_text, action_value = choices[choice_idx]
        except (IndexError, ValueError):
            show_result(["Invalid choice, try again."])
            pause()
            continue

        show_action(action_text)
        result_lines = handle_action(action_value, player, state)

        if result_lines:
            show_result(result_lines)
            pause()


if __name__ == "__main__":
    start_game()
