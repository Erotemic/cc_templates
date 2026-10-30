"""INDEPENDENT CHALLENGES: goals, not instructions.

Finish one guided mission in student.py first. Then pick a challenge here.
These challenges don't say which file to edit or what code to write.
You are the game designer: there is more than one good solution.

For each challenge, be ready to demonstrate it, explain what you changed,
and describe a bug you solved. You can invent your own challenge too.

Run ``python -m platformer.challenge`` to print this challenge board.
"""

CHALLENGES = (
    (
        "A secret side room",
        "Add an optional room the player can travel to and return from.",
        "Think about: maps, positions, keeping track of where you are.",
    ),
    (
        "Crumbling platforms",
        "Make certain platforms disappear a moment after you land on them.",
        "Think about: timers, temporary states, collisions, rebuilding a level.",
    ),
    (
        "Dangerous ground",
        "Add a new type of tile the player should avoid.",
        "Think about: collision, different tile types, consequences.",
    ),
    (
        "A useful secret",
        "Hide something worth discovering in the level.",
        "Think about: clues, conditions, rewards.",
    ),
    (
        "A timer",
        "Let players compete to finish the room as quickly as possible.",
        "Think about: time, starting and finishing, best scores.",
    ),
    (
        "Speedrun race",
        "Challenge the player to finish every room before a time limit.",
        "Think about: elapsed time, deadlines, scores, feedback.",
    ),
    (
        "A different kind of enemy",
        "Invent an enemy that is not just a purple creature patrolling.",
        "Think about: behavior, decisions, animation, difficulty.",
    ),
    (
        "An original mechanic",
        "Add something nobody asked you to add. Make it fun to play.",
        "Think about: testing an idea, giving feedback, keeping it simple.",
    ),
)

CODE_DETECTIVE = (
    "Where does the game first read a keyboard key?",
    "Why can a player stand on a platform instead of falling through it?",
    "How does the door know when every star has been collected?",
    "Why is jumping upward a negative velocity?",
    "Where does the program load the second and third levels?",
    "Where does the background music come from if there are no WAV files?",
)


def main() -> None:
    print("OPEN CHALLENGES — choose one to invent")
    for number, (name, goal, ideas) in enumerate(CHALLENGES, 1):
        print(f"\n{number}. {name.upper()}\n   {goal}\n   {ideas}")
    print("\nCODE DETECTIVE")
    for number, question in enumerate(CODE_DETECTIVE, 1):
        print(f"{number}. {question}")


if __name__ == "__main__":
    main()
