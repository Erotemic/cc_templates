"""
Beginner version 2: the SAME adventure, now with functions.

Compare this file directly with beginner/version1.py. The story and winning path are
unchanged. Only the organization changes.

New ideas in this version:
- defining and calling functions
- function parameters and return values
- removing repeated menu / display code

The game state is still just ordinary variables, and the action handling is
still one explicit if / elif tree. That is intentional: one new idea at a time.
"""


def show_status(player_name, inventory, description):
    """Display the room and the small amount of player state we care about."""
    print("\n" + "=" * 56)
    print(description)
    print(f"Player: {player_name}")
    if inventory:
        print("Inventory:", ", ".join(inventory))
    else:
        print("Inventory: empty")


def choose(choices):
    """Show numbered choices and return the selected action label.

    Returning None means the player typed ``quit``.
    """
    while True:
        print("\nWhat do you want to do?")
        for number, (text, action) in enumerate(choices, start=1):
            print(f"  {number}. {text}")

        answer = input("> ").strip()
        if answer.lower() == "quit":
            return None
        if answer.isdigit():
            number = int(answer)
            if 1 <= number <= len(choices):
                return choices[number - 1][1]
        print("Please enter one of the menu numbers.")


def main():
    print("Welcome to Tiny Adventure!")
    print("Find the treasure in the cave. Type 'quit' at any prompt to stop.")

    player_name = "Tav"
    player_location = "village"
    inventory = []
    key_taken = False
    game_won = False

    rooms = {
        "village": "You are in a small village. A path leads north into the forest.",
        "forest": "You are in a quiet forest. A cave lies east of an old stump.",
        "cave": "You are inside a dark cave. A locked treasure chest waits here.",
    }

    while not game_won:
        show_status(player_name, inventory, rooms[player_location])

        choices = []
        if player_location == "village":
            choices.append(("Go north to the forest", "go_forest"))
            choices.append(("Talk to the villager", "talk_villager"))
        elif player_location == "forest":
            choices.append(("Go south to the village", "go_village"))
            choices.append(("Go east to the cave", "go_cave"))
            if not key_taken:
                choices.append(("Look inside the old stump", "search_stump"))
        elif player_location == "cave":
            choices.append(("Go west to the forest", "go_forest"))
            choices.append(("Open the treasure chest", "open_chest"))

        action = choose(choices)
        if action is None:
            print("Goodbye!")
            return

        if action == "go_forest":
            player_location = "forest"
        elif action == "go_village":
            player_location = "village"
        elif action == "go_cave":
            player_location = "cave"
        elif action == "talk_villager":
            print("The villager says: 'I lost a little brass key near an old stump.'")
        elif action == "search_stump":
            print("Inside the stump you find a little brass key!")
            inventory.append("brass key")
            key_taken = True
        elif action == "open_chest":
            if "brass key" in inventory:
                print("The key turns. The chest opens. You found the treasure!")
                game_won = True
            else:
                print("The chest is locked. You need a key.")

    print("\nYou win! Thanks for playing.")


if __name__ == "__main__":
    main()
