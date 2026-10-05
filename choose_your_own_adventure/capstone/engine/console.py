"""Terminal UI for any capstone AdventureGame."""

from __future__ import annotations

from .game import AdventureGame


def choose(game: AdventureGame):
    choices = game.choices()
    for number, choice in enumerate(choices, 1):
        print(f"  {number}. {choice.text}")
    while True:
        answer = input("> ").strip()
        if answer.lower() == "quit":
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1].action
        print("Please enter one of the menu numbers.")


def run_console(game: AdventureGame) -> None:
    print(game.world["name"])
    print("Type 'quit' at any menu to stop.")
    while not game.over:
        print("\n" + "=" * 72)
        for line in game.describe():
            if line:
                print(line)
        print("\nWhat do you want to do?")
        action = choose(game)
        if action is None:
            print("Goodbye!")
            return
        lines = game.apply(action)
        for line in lines:
            print(line)
        if game.mode == "riddle":
            answer = input("Your answer: ")
            for line in game.submit_riddle_answer(answer):
                print(line)
    print("\n" + ("YOU WIN" if game.won else "GAME OVER"))
    if game.ending:
        print(game.ending)
