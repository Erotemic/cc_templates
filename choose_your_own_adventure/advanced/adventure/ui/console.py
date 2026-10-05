"""Console frontend for AdventureGame.

Notice what is absent: this file does not know how quests, combat, or rooms
work. It only asks the Game what to display and which choices are legal.
"""

from __future__ import annotations

from collections.abc import Callable

from adventure.core import AdventureGame, Choice


InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]
ArtProvider = Callable[[AdventureGame], str | None]


def choose_choice(
    choices: list[Choice],
    *,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
) -> str | None:
    """Return a selected action, or None when the user types ``quit``."""
    while True:
        for number, choice in enumerate(choices, start=1):
            output_fn(f"  {number}. {choice.text}")

        answer = input_fn("> ").strip()
        if answer.lower() == "quit":
            return None
        if answer.isdigit():
            number = int(answer)
            if 1 <= number <= len(choices):
                return choices[number - 1].action
        output_fn("Please enter one of the menu numbers.")


def run_console(
    game: AdventureGame,
    *,
    art_provider: ArtProvider | None = None,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
) -> AdventureGame:
    """Play a game in the terminal and return its final state."""
    output_fn(game.world.title)
    output_fn("Type 'quit' at any prompt to stop.")

    while not game.over:
        output_fn("\n" + "=" * 64)

        if art_provider is not None:
            art = art_provider(game)
            if art:
                output_fn(art)

        for line in game.describe():
            output_fn(line)

        output_fn("\nWhat do you want to do?")
        action = choose_choice(game.choices(), input_fn=input_fn, output_fn=output_fn)
        if action is None:
            output_fn("Goodbye!")
            return game

        for line in game.apply(action):
            output_fn(line)

    output_fn("\n" + ("YOU WIN" if game.won else "GAME OVER"))
    if game.ending:
        output_fn(game.ending)
    return game
