"""Terminal UI for any capstone AdventureGame.

The console path intentionally uses the same presentation art as Textual so
school machines without the optional Textual dependency still get the complete
capstone content and illustrations.

``input_func`` and ``output_func`` are injectable on purpose: the frontend can
be tested without a real terminal, which is a small example of dependency
injection in an otherwise straightforward Python program.
"""

from __future__ import annotations

from collections.abc import Callable

from .game import AdventureGame


InputFunc = Callable[[str], str]
OutputFunc = Callable[[str], None]


def choose(
    game: AdventureGame,
    *,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
):
    choices = game.choices()
    for number, choice in enumerate(choices, 1):
        output_func(f"  {number}. {choice.text}")
    while True:
        answer = input_func("> ").strip()
        if answer.lower() == "quit":
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1].action
        output_func("Please enter one of the menu numbers.")


def run_console(
    game: AdventureGame,
    *,
    show_art: bool = True,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
) -> None:
    from art.catalog import choose_art

    output_func(game.world["name"])
    output_func("Type 'quit' at any menu to stop.")
    latest_event = ""
    while not game.over:
        output_func("\n" + "=" * 72)
        if show_art:
            _, title, drawing = choose_art(game.snapshot(), latest_event)
            output_func(title)
            output_func(drawing)
            output_func("")
        output_func(f"Goal: {game.goal_text()}")
        for line in game.describe():
            if line:
                output_func(line)
        output_func("\nWhat do you want to do?")
        action = choose(game, input_func=input_func, output_func=output_func)
        if action is None:
            output_func("Goodbye!")
            return
        lines = game.apply(action)
        if game.mode == "riddle":
            for line in lines:
                output_func(line)
            answer = input_func(game.text_prompt() or "Your answer: ")
            riddle_lines = game.submit_riddle_answer(answer)
            lines = [*lines, *riddle_lines]
        for line in lines:
            output_func(line)
        latest_event = "\n".join(lines)
    output_func("\n" + ("YOU WIN" if game.won else "GAME OVER"))
    if game.ending:
        output_func(game.ending)
    if show_art:
        _, title, drawing = choose_art(game.snapshot(), latest_event)
        output_func("\n" + title)
        output_func(drawing)
