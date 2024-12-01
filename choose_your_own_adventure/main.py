"""
A simple template for a choose your own adventure game.

Written with the help of ChatGPT:
    https://chatgpt.com/share/674bbe31-d100-8002-b7bc-b9e687ca5ca2
"""


class GameEnvironment:
    """
    Store information about the environment players are in
    """
    def __init__(self):
        self.locations = {}
        self.choices = {}
        self.npcs = {}

    def add_location(self, name, description):
        self.locations[name] = description

    def set_choices(self, location, choices):
        self.choices[location] = choices

    def add_npc(self, location, npc):
        self.npcs[location] = npc

    def observe_suroundings(self, location):
        print('You observe your surroundings')
        print(self.locations.get(location, "This place seems unfamiliar."))

    def get_choices(self, location):
        return self.choices.get(location, {})

    def get_npc(self, location):
        return self.npcs.get(location)


class Player:
    """
    Store information about a player
    """
    def __init__(self, name):
        self.name = name
        self.inventory = []
        self.location = None
        self.health = 100

    def add_item(self, item):
        self.inventory.append(item)
        print(f"{item} added to inventory.")

    def move_to(self, location):
        self.location = location
        print(f"You are now at {location}.")


class MysteriousNPC:
    def __init__(self):
        self.name = "Mysterious Figure"
        self.inventory = ['key']
        self.memory = []

    def speak(self, text):
        typewriter_print(f"{self.name}: ", text)

    def interact(self, player):
        """
        """
        import time
        if len(self.inventory) > 0:
            # The NPC has something left to give
            reward = self.inventory[-1]
            self.speak("Hello traveler! If you can make me laugh, I might just give you something valuable.")
            if reward in self.inventory:
                joke = input("\nTell a joke to the NPC: ").strip()
                if joke:
                    if joke not in self.memory:
                        self.speak(f"Ha ha, that's a good one! Here's a {reward}.")
                        self.inventory.remove(reward)
                        self.memory.append(joke)
                        player.add_item(reward)
                    else:
                        self.speak("Hmm, I've heard that one before. Try again next time!")
                else:
                    self.speak("Hmm, that's not very funny. Try again next time!")
        else:
            assert self.memory, 'Something should be in the NPC memory'
            self.speak(f"Haha, haha: `{self.memory[-1]}`, I can't stop laughing")
        time.sleep(0.5)


def typewriter_print(prefix, text, word_delay=0.1):
    """
    Simulates a typewriter effect with a delay between each character.

    Example:
        >>> typewriter_print("Welcome to the Adventure Game! Your journey begins now.")
    """
    import sys
    import time
    sys.stdout.write(prefix)
    words = text.split(' ')  # Split the text into words
    for word in words:
        char_delay = word_delay / (len(word) + 1)
        for char in word:  # Print each character of the word with a delay
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(char_delay)
        sys.stdout.write(' ')  # Print space after the word
        sys.stdout.flush()
        time.sleep(char_delay)  # Delay between words
    sys.stdout.write('\n')  # Newline after the dialog


def start_game():
    print("Welcome to the Adventure Game Template!")

    player_name = 'Tav'
    # player_name = input("Enter your name: ")  # can get input here

    player = Player(player_name)
    environment = GameEnvironment()

    # Set up locations and choices
    environment.add_location("forest", "You are standing in a forest clearing. Paths lead north and east.")
    environment.add_location("cave", "A dark, damp cave. You hear faint noises in the distance.")
    environment.add_location("lake", "A serene lake surrounded by tall trees. The water is crystal clear.")

    environment.set_choices("forest", {
        "Go north": "cave",
        "Go east": "lake",
    })
    environment.set_choices("cave", {
        "Go back": "forest",
        "Explore deeper": None,  # Example: deeper exploration could be added
    })
    environment.set_choices("lake", {
        "Go back": "forest",
        "Swim": None,  # Swimming interaction
    })

    # Add NPC to the lake
    npc = MysteriousNPC()
    environment.add_npc("lake", npc)

    player.move_to('forest')

    DEBUGGING = 0
    if DEBUGGING:
        player.move_to('lake')

    # Main game loop
    while True:
        environment.observe_suroundings(player.location)

        # Check for NPCs
        npc = environment.get_npc(player.location)

        # Prepare choices
        choices = environment.get_choices(player.location)
        if npc:
            choices["Talk to the mysterious figure"] = "npc_interaction"

        if not choices:
            print("There's nothing more to do here.")
            break

        # Display choices
        print("\nWhat do you want to do?")
        for idx, (choice, _) in enumerate(choices.items(), 1):
            print(f"{idx}. {choice}")

        # Get and handle player choice
        try:
            choice_idx = int(input("\nEnter the number of your choice: ")) - 1
            selected_choice = list(choices.items())[choice_idx]
            action, next_location = selected_choice
            print(f"\nYou chose to: {action}")

            if next_location == "npc_interaction":
                npc.interact(player)
            elif action == "Swim":
                print("You take a refreshing swim in the lake. The water is cold but invigorating!")
            elif next_location:
                player.move_to(next_location)
            else:
                print("Nothing happens...")
        except (IndexError, ValueError):
            print("Invalid choice, try again.")

if __name__ == "__main__":
    start_game()
