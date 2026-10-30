"""INDEPENDENT CHALLENGES -- choose a goal, then find HOW to achieve it.

Unlike the guided missions in student.py, there are no prepared callbacks
or step-by-step solutions here. You must decide what code to change and
how to connect your new logic to the game.

View the board without opening a 3D window: python -m fpx3d.challenge
"""

CHALLENGES = [
    ("Starter", "A locked side door",
     "Add a door that opens only when the player does something you choose.",
     "Concepts: conditions, remembered state, collisions, visual feedback."),
    ("Starter", "A new security guard",
     "Create an enemy whose behavior is different from both the prism "
     "sentries and the clockwork robot.",
     "Concepts: positions, decisions over time, fairness."),
    ("Starter", "A real healing station",
     "Give the player somewhere to recover health, but not infinitely.",
     "Concepts: counters, cooldowns, state, feedback."),
    ("Starter", "A talking statue",
     "Let a statue respond to something the player has done.",
     "Concepts: interaction distance, events, conditional dialogue."),
    ("Starter", "A better treasure hunt",
     "Create a collectible that asks the player to explore differently.",
     "Concepts: discoverability, a reward, readable rules."),
    ("Intermediate", "Save your best run",
     "Remember a personal record even after closing the game.",
     "Concepts: files, data representation, missing/corrupt saves."),
    ("Intermediate", "Laser puzzle",
     "Build a hazard the player has to understand and time correctly.",
     "Concepts: periodic behavior, visual warning, collision."),
    ("Intermediate", "An actual stealth mechanic",
     "Give the player a way to avoid detection other than running away.",
     "Concepts: geometry, detection rules, states."),
    ("Intermediate", "An inventory",
     "Let the player carry something useful and decide when to use it.",
     "Concepts: lists, ownership, consuming an item."),
    ("Intermediate", "A moving maze",
     "Make the vault change its layout while the player explores.",
     "Concepts: updates, collisions, safety, test cases."),
    ("Intermediate", "A race against the Curator",
     "Add a rival character with a goal of its own.",
     "Concepts: artificial decisions, progress tracking, pacing."),
    ("Intermediate", "Optional puzzle rooms",
     "Make a hidden area with a reward that isn't needed to win.",
     "Concepts: choice, exploration, spatial design."),
    ("Advanced", "A generated vault",
     "Create new rooms each run without trapping the player.",
     "Concepts: procedural generation, graph connectivity, seeds."),
    ("Advanced", "A boss who changes tactics",
     "Create an encounter with several behaviors and clear warnings.",
     "Concepts: state machines, transitions, balancing."),
    ("Advanced", "Accessibility options",
     "Offer options for someone who cannot use fast mouse movement.",
     "Concepts: alternate controls, UI, player testing."),
    ("Design", "Make the vault tell a story",
     "Tell a story through places and objects rather than a long cutscene.",
     "Concepts: visual narrative, consistency, pacing."),
    ("Design", "Invent an ability nobody assigned",
     "Add one mechanic that genuinely changes how the game is played.",
     "Concepts: player experience, rules, tradeoffs."),
]

CODE_DETECTIVE = [
    "Where does pressing W turn into movement in 3D?",
    "How do both the graphics and the physics agree where a wall is?",
    "Why do we multiply speeds by elapsed seconds?",
    "How does the game recognize a prism without a Panda3D collision mesh?",
    "Find code that changes what happens on screen without changing the world geometry.",
]


def show_board() -> None:
    print("PRISM VAULT -- INDEPENDENT CHALLENGES")
    print("Choose a problem. Finding where to write the code is part of the task.\n")
    previous = None
    for number, (difficulty, title, goal, concepts) in enumerate(CHALLENGES, 1):
        if previous != difficulty:
            print(f"\n{difficulty.upper()} CHALLENGES")
            previous = difficulty
        print(f"{number}. {title}\n   Goal: {goal}\n   {concepts}")
    print("\nCODE DETECTIVE -- read the code, no new feature needed")
    for question in CODE_DETECTIVE:
        print(" -", question)


if __name__ == "__main__":
    show_board()
