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

print("Welcome to the Tiny Adventure Game!")
print("Tip: type 'quit' at any prompt to leave the game.")

# Store simple player information
player_name = "Tav"
# player_name = input("Enter your name: ")
player_location = "village"
inventory = []

# Track simple game state
key_taken = False
treasure_found = False
game_won = False

# Store information about the world
locations = {
    "village": "You are in a small village. A path leads north into the forest.",
    "forest": "You are in a quiet forest. There is a cave nearby and an old stump by the path.",
    "cave": "You are inside a dark cave. A small treasure chest sits in the corner.",
}

# Main game loop
while True:
    if game_won:
        print("\nThanks for playing!")
        break

    # Show the current location
    print("\nYou look around.")
    print(locations.get(player_location, "This place seems unfamiliar."))

    # Show a very small status display
    print(f"\nPlayer: {player_name}")
    if inventory:
        print("Inventory:", ", ".join(inventory))
    else:
        print("Inventory: empty")

    # Build choices for the current room
    choices = []

    if player_location == "village":
        choices.append(("Go north to the forest", "go_forest"))
        choices.append(("Talk to the villager", "talk_villager"))

    elif player_location == "forest":
        choices.append(("Go south to the village", "go_village"))
        choices.append(("Go east to the cave", "go_cave"))

        if not key_taken:
            choices.append(("Look inside the old stump", "look_stump"))

    elif player_location == "cave":
        choices.append(("Go west to the forest", "go_forest"))

        if not treasure_found:
            choices.append(("Open the treasure chest", "open_chest"))

    # If there are no choices, end the game
    if not choices:
        print("There is nothing more to do here.")
        break

    # Show choices
    print("\nWhat do you want to do?")
    for index, (choice_text, _) in enumerate(choices, start=1):
        print(f"{index}. {choice_text}")

    # Get player input
    user_input = input("\nEnter the number of your choice: ").strip().lower()

    if user_input == "quit":
        print("Thanks for playing!")
        break

    try:
        choice_index = int(user_input) - 1
        action_text, action_value = choices[choice_index]
    except (ValueError, IndexError):
        print("Invalid choice, try again.")
        input("\nPress Enter to continue...")
        continue

    print(f"\nYou chose to: {action_text}")

    # Handle actions
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
        if "key" in inventory:
            print("Villager: Maybe that key opens something in the cave.")
        else:
            print("Villager: I heard there is something useful hidden in the forest.")
        input("\nPress Enter to continue...")

    elif action_value == "look_stump":
        if not key_taken:
            key_taken = True
            inventory.append("key")
            print("You find a small brass key inside the old stump.")
        else:
            print("The stump is empty.")
        input("\nPress Enter to continue...")

    elif action_value == "open_chest":
        if "key" in inventory:
            treasure_found = True
            game_won = True
            print("You unlock the chest with the key.")
            print("Inside is a glittering treasure.")
            print("You found the treasure and won the game!")
        else:
            print("The chest is locked. You need a key.")
        input("\nPress Enter to continue...")

    else:
        print("Nothing happens.")
        input("\nPress Enter to continue...")
