"""
A simple template for a choose your own adventure game.

This version is designed to be easy to teach:
- one player
- one world
- one main game loop
- small action functions
- one action dispatch table

It also tries to make the gameplay feel clear:
- choose an action
- see the result in one place
- press Enter when you are ready for the next decision
"""

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

ROOM_NAMES = set(ROOM_CHOICES)

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
    if action in ROOM_NAMES:
        return move_player(player, action)

    handler = ACTIONS.get(action)
    if handler is not None:
        return handler(player, state)

    return ["That action is not implemented yet."]


# ============================================================
# Main game loop
# ============================================================


def start_game():
    print("Welcome to the Adventure Game Template!")
    print("Tip: type 'quit' at any prompt to leave the game.")

    player_name = "Tav"
    # player_name = input("Enter your name: ")  # can get input here

    player = Player(player_name)
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
