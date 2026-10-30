"""Independent RPG challenges: goals and concepts, NOT prewritten solutions.

Read these after ``student.py``. The game does not call functions from this
file automatically. Finding the relevant code and wiring new behavior into
real battles is part of each challenge.

Run ``python student_game/challenge.py`` from the RPG folder to print them.
"""

CHALLENGES = [
    (
        "An enemy with a memory",
        "Teach a monster to respond differently after a hero attacks it twice.",
        "Consider: events, remembering previous turns, and persistent state.",
    ),
    (
        "Healing priorities",
        "Make the healer choose between two injured teammates intelligently.",
        "Consider: priorities, sorting or scanning, and limited resources.",
    ),
    (
        "Charge and release",
        "A creature waits one turn before using a powerful attack.",
        "Consider: a state machine and actions on later turns.",
    ),
    (
        "A clever boss",
        "Create a boss with a recognizable pattern players can learn.",
        "Consider: rounds, state, feedback, and fairness.",
    ),
    (
        "A status specialist",
        "Make a fighter change tactics when an enemy is burning or stunned.",
        "Consider: status collections, conditionals, and choosing targets.",
    ),
    (
        "Risk and reward",
        "Invent a move that becomes stronger but has a meaningful trade-off.",
        "Consider: balance, limits, HP, and resources.",
    ),
    (
        "The potion problem",
        "Invent a usable consumable item and make it visible in battle.",
        "Consider: inventory, UI, validating actions, and reducing a count.",
    ),
    (
        "Make a new hero",
        "Design a character with a distinctive appearance and fighting style.",
        "Consider: reusable art, moves, teams, and playtesting.",
    ),
    (
        "A tournament opponent",
        "Create a team strategy that beats several different opponents.",
        "Consider: heuristics, uncertainty, experimentation, and statistics.",
    ),
    (
        "Make the battle tell a story",
        "Change the way the encounter unfolds without adding a cutscene.",
        "Consider: cause and effect, phases, and meaningful choices.",
    ),
]

DETECTIVE_QUESTIONS = [
    "How can a fighter have art and music without opening a file of pixels or audio?",
    "Which part of the engine checks whether a skill costs too much mana?",
    "Why does a move return a command instead of directly reducing HP?",
    "How does a saved battle scenario guarantee the same starting HP?",
    "Find something available in the code that the classroom guide doesn't explain.",
]


def show_board():
    print("INDEPENDENT RPG CHALLENGES")
    print("Goals first; you'll figure out the implementation yourself.\n")
    for number, (name, goal, concepts) in enumerate(CHALLENGES, 1):
        print(f"{number}. {name}\n   Goal: {goal}\n   {concepts}\n")
    print("CODE DETECTIVE")
    for question in DETECTIVE_QUESTIONS:
        print(" -", question)
    print("\nShow a working change, explain one design choice, and show how you tested it.")


if __name__ == "__main__":
    show_board()
