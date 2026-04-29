"""
Version 0: the smallest clean adventure game.

This is the beginner-first starting point in the progression.
It keeps the game as small and readable as possible so students can focus on:
- variables
- dictionaries
- loops
- conditionals
- user input

This version is intentionally tiny.
It does not introduce custom functions yet.
Its job is to help students understand how a text adventure works before
they learn about organizing code into reusable pieces.
"""

# print() shows text in the terminal. \n in a print starts a new line.
print("Welcome to the Tiny Adventure Game!")
print("Tip: type 'quit' at any prompt to leave the game.")

# --- Variables ---------------------------------------------------------------
# A "variable" is a name that holds a value. We can read it and change it
# later. The type of value is inferred from what we put on the right side.

player_name = "Tav"             # a string (text)
# Uncomment the next line to ask the player for their name instead:
# player_name = input("Enter your name: ")
player_location = "village"     # which room the player is in right now
inventory = []                  # a list — starts empty, grows as we pick things up

# --- Game state flags --------------------------------------------------------
# Booleans are True/False values. Great for "has this happened yet?" questions.
key_taken = False
treasure_found = False
game_won = False

# --- World data --------------------------------------------------------------
# A dictionary maps "keys" to "values". Here the key is a location name and
# the value is the description we print when the player is there.
# We can look something up later with locations[key] or locations.get(key).
locations = {
    "village": "You are in a small village. A path leads north into the forest.",
    "forest": "You are in a quiet forest. There is a cave nearby and an old stump by the path.",
    "cave": "You are inside a dark cave. A small treasure chest sits in the corner.",
}

# --- Main game loop ----------------------------------------------------------
# `while True` runs forever — until something inside calls `break` to stop it.
# Each pass through the loop is one "turn": show the room, ask for a choice,
# and react to it.
while True:
    # If the player won last turn, say goodbye and leave the loop.
    if game_won:
        print("\nThanks for playing!")
        break

    # --- Describe the current room ------------------------------------------
    print("\nYou look around.")
    # .get(key, default) returns the value if the key exists, otherwise the
    # default text. This is safer than locations[key] which would crash.
    print(locations.get(player_location, "This place seems unfamiliar."))

    # --- Show a tiny status display -----------------------------------------
    # f-strings let us drop variables right into a string with {curly braces}.
    print(f"\nPlayer: {player_name}")
    # An empty list is "falsy" in Python, so `if inventory` means "if it has
    # at least one item". ", ".join(...) glues the list into one string.
    if inventory:
        print("Inventory:", ", ".join(inventory))
    else:
        print("Inventory: empty")

    # --- Build a list of choices for the current room -----------------------
    # Each choice is a tuple: (text we show the player, an action label
    # we use later to decide what to do).
    choices = []

    # `if` / `elif` lets us branch — only one of these blocks will run.
    if player_location == "village":
        choices.append(("Go north to the forest", "go_forest"))
        choices.append(("Talk to the villager", "talk_villager"))

    elif player_location == "forest":
        choices.append(("Go south to the village", "go_village"))
        choices.append(("Go east to the cave", "go_cave"))

        # Only show this option if we haven't already taken the key.
        if not key_taken:
            choices.append(("Look inside the old stump", "look_stump"))

    elif player_location == "cave":
        choices.append(("Go west to the forest", "go_forest"))

        if not treasure_found:
            choices.append(("Open the treasure chest", "open_chest"))

    # If we somehow built no choices, there's nothing left to do — end the game.
    if not choices:
        print("There is nothing more to do here.")
        break

    # --- Show the choices to the player -------------------------------------
    print("\nWhat do you want to do?")
    # enumerate(..., start=1) numbers the items 1, 2, 3, ... so the player
    # can type a number. The `_` means "we don't care about this value here".
    for index, (choice_text, _) in enumerate(choices, start=1):
        print(f"{index}. {choice_text}")

    # --- Read what the player typed -----------------------------------------
    # input() pauses the program until the user types something and presses
    # Enter. .strip() removes spaces, .lower() makes the text lowercase so
    # "Quit", "QUIT", and "quit" all match.
    user_input = input("\nEnter the number of your choice: ").strip().lower()

    if user_input == "quit":
        print("Thanks for playing!")
        break

    # try/except lets us recover when something goes wrong instead of crashing.
    # int(...) fails if the text isn't a number. choices[index] fails if the
    # number is out of range. Either way, we just say "invalid" and try again.
    try:
        choice_index = int(user_input) - 1   # -1 because lists start at 0
        action_text, action_value = choices[choice_index]
    except (ValueError, IndexError):
        print("Invalid choice, try again.")
        input("\nPress Enter to continue...")
        continue   # `continue` skips the rest of the loop body and starts the next turn

    print(f"\nYou chose to: {action_text}")

    # --- React to the chosen action -----------------------------------------
    # Each branch updates variables (location, inventory, flags) and prints
    # a short message describing what happened.
    if action_value == "go_forest":
        player_location = "forest"
        print("You walk to the forest.")
        input("\nPress Enter to continue...")

    elif action_value == "go_village":
        player_location = "village"
        print("You return to the village.")
        input("\nPress Enter to continue...")

    elif action_value == "go_cave":
        player_location = "cave"
        print("You step carefully into the cave.")
        input("\nPress Enter to continue...")

    elif action_value == "talk_villager":
        # The villager gives a different hint depending on what we have.
        # "key" in inventory checks whether that string is in the list.
        if "key" in inventory:
            print("Villager: Maybe that key opens something in the cave.")
        else:
            print("Villager: I heard there is something useful hidden in the forest.")
        input("\nPress Enter to continue...")

    elif action_value == "look_stump":
        if not key_taken:
            key_taken = True
            inventory.append("key")   # add an item to the list
            print("You find a small brass key inside the old stump.")
        else:
            print("The stump is empty.")
        input("\nPress Enter to continue...")

    elif action_value == "open_chest":
        if "key" in inventory:
            # Win condition: setting game_won = True ends the loop next turn.
            treasure_found = True
            game_won = True
            print("You unlock the chest with the key.")
            print("Inside is a glittering treasure.")
            print("You found the treasure and won the game!")
        else:
            print("The chest is locked. You need a key.")
        input("\nPress Enter to continue...")

    else:
        # Safety net: if we ever forget to handle one of the action values.
        print("Nothing happens.")
        input("\nPress Enter to continue...")
