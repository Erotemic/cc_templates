"""
Beginner version 1: one loop, one tiny adventure.

Start here if Python is still new.

New ideas in this version:
- variables
- lists and dictionaries
- while loops
- if / elif / else
- input and output

There are deliberately NO custom functions or classes yet.
The whole game fits in one place so you can see the basic recipe for a
text adventure before learning how to organize a larger program.
"""

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
    print("\n" + "=" * 56)
    print(rooms[player_location])
    print(f"Player: {player_name}")
    if inventory:
        print("Inventory:", ", ".join(inventory))
    else:
        print("Inventory: empty")

    # Each choice is (what the player sees, what the program should do).
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

    print("\nWhat do you want to do?")
    for number, (text, action) in enumerate(choices, start=1):
        print(f"  {number}. {text}")

    answer = input("> ").strip()
    if answer.lower() == "quit":
        print("Goodbye!")
        break

    # int("3") gives the number 3. We check BOTH ends of the range.
    # Without the `1 <= ...` check, entering 0 would accidentally select
    # Python list index -1, which means "the last item".
    if not answer.isdigit():
        print("Please enter one of the menu numbers.")
        continue

    number = int(answer)
    if not 1 <= number <= len(choices):
        print("That number is not one of the choices.")
        continue

    action = choices[number - 1][1]

    # This is the "big action tree". It is perfectly reasonable for a tiny
    # program. In later versions we will learn how to organize it as the game
    # grows.
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

if game_won:
    print("\nYou win! Thanks for playing.")
