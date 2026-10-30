"""INDEPENDENT CHALLENGES -- you decide HOW to build them.

Start with ``student.py`` if you want an exercise that teaches you exactly
where to write code. Come back here when you're ready to explore on your own.

These challenges are different:

* The goal is described, but there is NO prepared function to fill in.
* The hints name CONCEPTS to think about, not filenames or exact steps.
* You decide which files and functions to change, and what to invent.
* This file is a challenge board, NOT part of the game loop. Writing code
  here won't change the game unless you connect it to the rest of the game.

Pick just ONE challenge. Make a tiny first version that you can show someone.
Then improve it. Ask yourself: what does the game need to remember? How will
I know whether the behavior works? What should happen in tricky cases?

To print this board in the terminal, run:

    python -m climber.challenge

Add your own challenge to the list or replace any prompt with your idea.
"""

# Each challenge has: difficulty, name, what the PLAYER should experience,
# and concepts worth thinking about. There are no prescribed solutions.
CHALLENGES = [
    (
        "Starter", "Breaking platforms",
        "Some platforms should break after you stand on them. You can fall "
        "through after they break.",
        "Things to consider: time, states that change, collisions.",
    ),
    (
        "Starter", "Checkpoints",
        "Make some locations act as checkpoints so a mistake does not "
        "always send you to the ground.",
        "Things to consider: remembering a location, resets, fair rules.",
    ),
    (
        "Starter", "Treasure with a purpose",
        "Make collected treasure useful in a way you invent.",
        "Things to consider: rewards, counters, choices, feedback.",
    ),
    (
        "Starter", "A second enemy type",
        "Add an enemy whose behavior is different from the pink creatures.",
        "Things to consider: movement rules, state, appearance, testing.",
    ),
    (
        "Starter", "The heckler gets smarter",
        "Make the heckler react to something the player does that he "
        "currently ignores.",
        "Things to consider: events, remembered facts, timing, dialogue.",
    ),
    (
        "Intermediate", "Personal best",
        "Remember the player's highest climb even after the program closes.",
        "Things to consider: reading/writing data, missing files, records.",
    ),
    (
        "Intermediate", "A new power-up",
        "Invent a temporary ability and a way to get it. Make its "
        "effects clear to the player.",
        "Things to consider: duration, activation, ending, visual feedback.",
    ),
    (
        "Intermediate", "Weather",
        "Make weather change how climbing works, not just how it looks.",
        "Things to consider: forces, difficulty, fairness, visibility.",
    ),
    (
        "Intermediate", "Secret rooms",
        "Add hidden places that reward curious players for finding them.",
        "Things to consider: exploration, discovery, camera, transitions.",
    ),
    (
        "Intermediate", "Tower regions",
        "Make the tower change its style and gameplay as the climb continues.",
        "Things to consider: deterministic generation, variety, reachability.",
    ),
    (
        "Intermediate", "The heckler fights back",
        "Give the heckler a way to interfere with the climber.",
        "Things to consider: cause and effect, warning the player, balance.",
    ),
    (
        "Intermediate", "Speedrun mode",
        "Let the player race against their own time. Decide what counts "
        "as finishing a race in a tower without an end.",
        "Things to consider: timers, start/end events, saving results.",
    ),
    (
        "Advanced", "A rival climber",
        "Add a second character who is also trying to climb the tower.",
        "Things to consider: computer decisions, movement, competition.",
    ),
    (
        "Advanced", "A climbing boss",
        "Create a boss encounter that tests climbing skill instead of "
        "only fighting skill.",
        "Things to consider: patterns, multiple phases, readable warnings.",
    ),
    (
        "Advanced", "Invent a better tower generator",
        "Build a more interesting infinite tower without trapping the player "
        "in impossible jumps.",
        "Things to consider: procedural patterns, constraints, consistency.",
    ),
    (
        "Design", "Make the tower tell a story",
        "Let players learn something about this place or its inhabitants "
        "just by climbing. No cutscenes required.",
        "Things to consider: environmental storytelling, repetition, change.",
    ),
    (
        "Design", "Make floor 50 memorable",
        "Something important should happen when the player reaches floor 50. "
        "You decide what and why.",
        "Things to consider: anticipation, a special event, player choice.",
    ),
    (
        "Design", "Invent a mechanic nobody assigned",
        "Change the way the game plays using an idea that is not on this list.",
        "Things to consider: what makes it fun, how to explain it, testing.",
    ),
]


CODE_DETECTIVE = [
    "How can the tower go on forever without storing every platform?",
    "How does the game tell a landing apart from hitting a ledge below?",
    "How can the camera scroll without changing every platform's world Y?",
    "Where does the background music come from if no audio file is loaded?",
    "Find something the code can do that the controls page doesn't explain.",
]


def show_board():
    """Print the challenges; the gameplay does not import this module."""
    print("INFINITY CLIMBER: INDEPENDENT CHALLENGES")
    print("Choose one goal. Work out where to make changes yourself.\n")
    previous = None
    for number, (level, title, goal, concepts) in enumerate(CHALLENGES, 1):
        if level != previous:
            print(f"\n{level.upper()} CHALLENGES")
            previous = level
        print(f"{number}. {title}")
        print(f"   Goal: {goal}")
        print(f"   {concepts}")
    print("\nCODE DETECTIVE (no new feature required)")
    for question in CODE_DETECTIVE:
        print(f" - {question}")
    print("\nShow your result, explain one design decision, and describe a bug you fixed.")


if __name__ == "__main__":
    show_board()


# You can put your own code below. To make it part of the GAME, you will
# need to figure out where and when the game should call it. That's part of
# solving an independent challenge; nothing here runs during gameplay yet.
