"""
Version 1: the giant if / elif / else version.

This file keeps the small adventure story, but makes the control flow
extremely explicit. Almost everything happens inside one large game loop
with one large action tree.

Use this version to teach:
- state variables
- menu building
- nested conditionals
- how repetition grows in a procedural program
- why "just one more branch" works for a while, but becomes hard to manage

This is not the cleanest version.
It is here so students can see the brute-force approach clearly before moving
to better organization.
"""


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
    """
    if isinstance(lines, str):
        lines = [lines]

    if not lines:
        return

    print("\nResult:")
    for line in lines:
        print(line)


def pause():
    input("\nPress Enter to continue...")


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


def show_dialog_lines(speaker, lines, word_delay=0.1):
    """
    Show spoken dialog with the typewriter effect, while keeping narration
    and other result text handled elsewhere.
    """
    if isinstance(lines, str):
        lines = [lines]

    if not lines:
        return

    print("\nDialog:")
    for line in lines:
        typewriter_print(f"{speaker}: ", line, word_delay=word_delay)


# ============================================================
# Main game
# ============================================================


def start_game():
    print("Welcome to the Adventure Game Template!")
    print("Tip: type 'quit' at any prompt to leave the game.")

    player_name = "Tav"
    # player_name = input("Enter your name: ")  # can get input here

    # Store information about a player
    player_inventory = []
    player_location = "village"
    player_health = 20

    # Track game state
    quest_started = False
    spider_alive = True
    herb_taken = False
    sword_taken = False
    tower_unlocked = False
    crystal_taken = False
    game_won = False
    quit_game = False

    # Main game loop
    while True:
        if quit_game:
            print("\nThanks for playing!")
            break

        if player_health <= 0:
            print("\nGame over.")
            break

        if game_won:
            print("\nThanks for playing!")
            break

        # ============================================================
        # Observe surroundings
        # ============================================================

        print("\nYou observe your surroundings")

        if player_location == "village":
            if game_won:
                print(
                    "You are in the village square. The fountain is flowing again, and the villagers are smiling."
                )
            else:
                print(
                    "You are in a quiet village square. An old elder stands near a dry fountain."
                )

        elif player_location == "crossroads":
            print("You stand at a crossroads. Paths lead north, east, south, and west.")

        elif player_location == "forest":
            if herb_taken and sword_taken:
                print(
                    "You are in a shady forest. The herb patch has been picked clean, and the fallen log has already been searched."
                )
            elif herb_taken and not sword_taken:
                print(
                    "You are in a shady forest. Near a fallen log, you think you might still find something useful."
                )
            elif sword_taken and not herb_taken:
                print(
                    "You are in a shady forest. You notice a patch of useful herbs growing nearby."
                )
            else:
                print(
                    "You are in a shady forest. You notice herbs growing near a fallen log."
                )

        elif player_location == "lake":
            print("You arrive at a peaceful lake. A fisherman waits by the shore.")

        elif player_location == "cave_entrance":
            print("A dark cave entrance opens in the hillside.")

        elif player_location == "cave":
            if spider_alive:
                print(
                    "Inside the cave, the air is cold. A giant spider guards something shiny."
                )
            else:
                print(
                    "Inside the cave, the air is cold. The defeated spider lies still, and the cave is quiet now."
                )

        elif player_location == "ruins":
            print("You stand among old ruins. A narrow path leads toward a tower.")

        elif player_location == "tower_gate":
            if tower_unlocked:
                print("You stand before the tower gate. The lock hangs open.")
            else:
                print("You stand before a locked tower gate.")

        elif player_location == "tower_top":
            if crystal_taken:
                print("At the top of the tower, the pedestal is empty.")
            else:
                print("At the top of the tower, a glowing crystal rests on a pedestal.")

        else:
            print("This place seems unfamiliar.")

        # ============================================================
        # Show player status
        # ============================================================

        print(f"\nPlayer: {player_name}")
        print(f"Health: {player_health}")
        if player_inventory:
            print("Inventory:", ", ".join(player_inventory))
        else:
            print("Inventory: empty")

        # ============================================================
        # Build choices directly with if / elif / else
        # ============================================================

        choices = []

        if player_location == "village":
            choices.append(
                ("Go north to the crossroads", "go_to_crossroads_from_village")
            )
            choices.append(("Talk to the elder", "talk_to_elder"))

        elif player_location == "crossroads":
            choices.append(("Go south to the village", "go_to_village_from_crossroads"))
            choices.append(("Go west to the forest", "go_to_forest_from_crossroads"))
            choices.append(("Go east to the lake", "go_to_lake_from_crossroads"))
            choices.append(("Go north to the ruins", "go_to_ruins_from_crossroads"))

        elif player_location == "forest":
            choices.append(
                ("Go east to the crossroads", "go_to_crossroads_from_forest")
            )
            choices.append(
                ("Go north to the cave entrance", "go_to_cave_entrance_from_forest")
            )

            if herb_taken:
                pass
            else:
                choices.append(("Pick the herb", "pick_herb"))

            if sword_taken:
                pass
            else:
                choices.append(("Look near the fallen log", "find_sword"))

        elif player_location == "lake":
            choices.append(("Go west to the crossroads", "go_to_crossroads_from_lake"))
            choices.append(("Talk to the fisherman", "talk_to_fisherman"))

        elif player_location == "cave_entrance":
            choices.append(
                ("Go south to the forest", "go_to_forest_from_cave_entrance")
            )
            choices.append(("Enter the cave", "enter_cave"))

        elif player_location == "cave":
            choices.append(
                ("Go south to the cave entrance", "go_to_cave_entrance_from_cave")
            )

            if spider_alive:
                choices.append(("Fight the spider", "fight_spider"))
            else:
                pass

        elif player_location == "ruins":
            choices.append(
                ("Go south to the crossroads", "go_to_crossroads_from_ruins")
            )
            choices.append(
                ("Go north to the tower gate", "go_to_tower_gate_from_ruins")
            )

        elif player_location == "tower_gate":
            choices.append(("Go south to the ruins", "go_to_ruins_from_tower_gate"))

            if tower_unlocked:
                choices.append(
                    ("Go up into the tower", "go_to_tower_top_from_tower_gate")
                )
            else:
                choices.append(("Try to open the tower gate", "open_tower_gate"))

        elif player_location == "tower_top":
            choices.append(
                ("Go down to the tower gate", "go_to_tower_gate_from_tower_top")
            )

            if crystal_taken:
                pass
            else:
                choices.append(("Take the crystal", "take_crystal"))

        else:
            pass

        if not choices:
            print("There's nothing more to do here.")
            break

        # ============================================================
        # Show choices
        # ============================================================

        print("\nWhat do you want to do?")
        for idx, (choice_text, choice_value) in enumerate(choices, 1):
            print(f"{idx}. {choice_text}")

        user_input = input("\nEnter the number of your choice: ").strip().lower()

        if user_input == "quit":
            print("Thanks for playing!")
            break

        try:
            choice_index = int(user_input) - 1
            action_text, action_value = choices[choice_index]
        except (ValueError, IndexError):
            show_result(["Invalid choice, try again."])
            pause()
            continue

        show_action(action_text)

        # ============================================================
        # Giant action tree
        # ============================================================

        if action_value == "go_to_crossroads_from_village":
            player_location = "crossroads"
            show_result(["You travel to the crossroads."])
            pause()

        elif action_value == "go_to_village_from_crossroads":
            player_location = "village"
            show_result(["You return to the village."])
            pause()

        elif action_value == "go_to_forest_from_crossroads":
            player_location = "forest"
            show_result(["You head into the forest."])
            pause()

        elif action_value == "go_to_lake_from_crossroads":
            player_location = "lake"
            show_result(["You walk to the lake."])
            pause()

        elif action_value == "go_to_ruins_from_crossroads":
            player_location = "ruins"
            show_result(["You travel to the ruins."])
            pause()

        elif action_value == "go_to_crossroads_from_forest":
            player_location = "crossroads"
            show_result(["You travel back to the crossroads."])
            pause()

        elif action_value == "go_to_cave_entrance_from_forest":
            player_location = "cave_entrance"
            show_result(["You make your way to the cave entrance."])
            pause()

        elif action_value == "go_to_crossroads_from_lake":
            player_location = "crossroads"
            show_result(["You travel back to the crossroads."])
            pause()

        elif action_value == "go_to_forest_from_cave_entrance":
            player_location = "forest"
            show_result(["You head back into the forest."])
            pause()

        elif action_value == "go_to_cave_entrance_from_cave":
            player_location = "cave_entrance"
            show_result(["You leave the cave and return to the entrance."])
            pause()

        elif action_value == "go_to_crossroads_from_ruins":
            player_location = "crossroads"
            show_result(["You travel back to the crossroads."])
            pause()

        elif action_value == "go_to_tower_gate_from_ruins":
            player_location = "tower_gate"
            show_result(["You walk up to the tower gate."])
            pause()

        elif action_value == "go_to_ruins_from_tower_gate":
            player_location = "ruins"
            show_result(["You leave the tower gate and return to the ruins."])
            pause()

        elif action_value == "go_to_tower_top_from_tower_gate":
            player_location = "tower_top"
            show_result(["You climb the stairs and enter the top of the tower."])
            pause()

        elif action_value == "go_to_tower_gate_from_tower_top":
            player_location = "tower_gate"
            show_result(["You climb down from the top of the tower."])
            pause()

        elif action_value == "talk_to_elder":
            dialog_lines = []
            result_lines = []

            if "crystal" in player_inventory and not game_won:
                if quest_started:
                    dialog_lines.append("You found the crystal!")
                else:
                    dialog_lines.append(
                        "You found the crystal before I even had time to explain the quest!"
                    )
                    dialog_lines.append("No matter. You have saved us all.")

                result_lines.append("The elder raises it over the fountain.")
                result_lines.append("Water bursts upward. The village is saved!")
                quest_started = True
                game_won = True

            elif not quest_started:
                dialog_lines.append("The village fountain is dry.")
                dialog_lines.append(
                    "Bring back the crystal from the old tower and restore the village."
                )
                quest_started = True

            else:
                dialog_lines.append(
                    "Search the valley. The forest, lake, cave, and ruins all hide clues."
                )

            show_dialog_lines("Elder", dialog_lines)
            if result_lines:
                show_result(result_lines)
            pause()

        elif action_value == "talk_to_fisherman":
            dialog_lines = []
            result_lines = []

            if "herb" in player_inventory and "lantern" not in player_inventory:
                if "herb" in player_inventory:
                    player_inventory.remove("herb")
                if "lantern" not in player_inventory:
                    player_inventory.append("lantern")

                dialog_lines.append(
                    "Ah, a fresh herb. I will trade you my lantern for it."
                )
                result_lines.append("You give the herb to the fisherman.")
                result_lines.append("You receive a lantern.")

            elif "lantern" not in player_inventory:
                dialog_lines.append("The cave is too dark without a lantern.")
                dialog_lines.append(
                    "Bring me a useful herb from the forest and we can trade."
                )

            else:
                dialog_lines.append("Use that lantern well.")

            show_dialog_lines("Fisherman", dialog_lines)
            if result_lines:
                show_result(result_lines)
            pause()

        elif action_value == "pick_herb":
            result_lines = []

            if herb_taken:
                result_lines.append("You already picked the useful herb here.")
            else:
                herb_taken = True

                if "herb" in player_inventory:
                    result_lines.append("You already have the herb.")
                else:
                    player_inventory.append("herb")
                    result_lines.append("You pick a useful herb from the forest.")
                    result_lines.append("You put the herb in your bag.")

            show_result(result_lines)
            pause()

        elif action_value == "find_sword":
            result_lines = []

            if sword_taken:
                result_lines.append("There is nothing else useful near the log.")
            else:
                sword_taken = True

                if "sword" in player_inventory:
                    result_lines.append("You already took the sword.")
                else:
                    player_inventory.append("sword")
                    result_lines.append("You search near the fallen log.")
                    result_lines.append("You find an old sword and take it with you.")

            show_result(result_lines)
            pause()

        elif action_value == "enter_cave":
            result_lines = []

            if "lantern" in player_inventory:
                player_location = "cave"
                result_lines.append("You light your lantern and step into the cave.")
            else:
                result_lines.append("It is too dark to enter safely.")
                result_lines.append("You need a lantern.")

            show_result(result_lines)
            pause()

        elif action_value == "fight_spider":
            while True:
                if not spider_alive:
                    break

                if player_health <= 0:
                    break

                print("\n" + "=" * 40)
                print("The spider attacks!")
                print("=" * 40)
                print(f"Your health: {player_health}")

                print("\nWhat do you do?")
                print("1. Attack")
                print("2. Run away")

                fight_input = input("Enter your choice: ").strip().lower()

                if fight_input == "quit":
                    quit_game = True
                    show_result(["You leave the cave and abandon the adventure."])
                    pause()
                    break

                elif fight_input == "1":
                    if "sword" in player_inventory:
                        spider_alive = False

                        if "silver key" in player_inventory:
                            show_result(
                                [
                                    "You strike the spider with your sword.",
                                    "The spider is defeated.",
                                ]
                            )
                        else:
                            player_inventory.append("silver key")
                            show_result(
                                [
                                    "You strike the spider with your sword.",
                                    "The spider is defeated.",
                                    "You find a silver key near its nest.",
                                ]
                            )

                        pause()
                        break

                    else:
                        player_health = player_health - 5

                        result_lines = []
                        result_lines.append(
                            "You try to fight with your bare hands, but the spider stays out of reach."
                        )
                        result_lines.append("The spider bites you.")
                        result_lines.append("You lose 5 health.")

                        if player_health <= 0:
                            result_lines.append("You were defeated by the spider.")

                        show_result(result_lines)
                        pause()

                    # keep looping

                elif fight_input == "2":
                    player_location = "cave_entrance"
                    show_result(["You run back to the cave entrance."])
                    pause()
                    break

                else:
                    show_result(["Invalid choice."])
                    pause()

        elif action_value == "open_tower_gate":
            result_lines = []

            if "silver key" in player_inventory:
                tower_unlocked = True
                player_location = "tower_top"
                result_lines.append("You unlock the tower gate with the silver key.")
                result_lines.append("You climb the stairs to the top of the tower.")
            else:
                result_lines.append("The tower gate is locked. You need a key.")

            show_result(result_lines)
            pause()

        elif action_value == "take_crystal":
            result_lines = []

            if crystal_taken:
                result_lines.append("The pedestal is already empty.")
            else:
                crystal_taken = True

                if "crystal" in player_inventory:
                    result_lines.append("You already took the crystal.")
                else:
                    player_inventory.append("crystal")
                    result_lines.append(
                        "You take the glowing crystal from the pedestal."
                    )
                    result_lines.append("The crystal feels warm in your hands.")

            show_result(result_lines)
            pause()

        else:
            show_result(["That action is not implemented yet."])
            pause()


if __name__ == "__main__":
    start_game()
