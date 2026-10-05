from __future__ import annotations

import pytest

from engine import launcher
from engine.console import run_console
from engine.game import AdventureGame
from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL


def test_console_frontend_runs_without_textual_or_a_real_terminal():
    game = AdventureGame(STAR_CRYSTAL)
    answers = iter(["not a number", "quit"])
    output: list[str] = []

    run_console(
        game,
        show_art=False,
        input_func=lambda prompt: next(answers),
        output_func=output.append,
    )

    joined = "\n".join(output)
    assert "The Star Crystal" in joined
    assert "Please enter one of the menu numbers." in joined
    assert "Goodbye!" in joined


def test_auto_ui_falls_back_to_console_when_textual_is_absent(monkeypatch):
    game = AdventureGame(STAR_CRYSTAL)
    called = []
    monkeypatch.setattr(launcher, "textual_available", lambda: False)
    monkeypatch.setattr(launcher, "run_console", lambda game: called.append(game))

    launcher.run_game(game, ["--ui", "auto"])

    assert called == [game]


def test_explicit_textual_request_has_a_helpful_error_when_missing(monkeypatch, capsys):
    game = AdventureGame(STAR_CRYSTAL)
    monkeypatch.setattr(launcher, "textual_available", lambda: False)

    with pytest.raises(SystemExit) as exc:
        launcher.run_game(game, ["--ui", "textual"])
    assert exc.value.code == 2
    assert "Textual is not installed" in capsys.readouterr().err


def test_console_can_drive_real_npc_state_without_textual():
    game = AdventureGame(STAR_CRYSTAL)
    answers = iter(["2", "quit"])  # Approach Elder Mira, then stop.
    output: list[str] = []
    run_console(
        game,
        show_art=False,
        input_func=lambda prompt: next(answers),
        output_func=output.append,
    )
    assert game.mode == "npc"
    assert game.current_npc_name == "Elder Mira"
    assert "Elder Mira" in "\n".join(output)


def test_console_can_submit_free_text_riddle_without_textual():
    game = AdventureGame(STAR_CRYSTAL)
    game.player_location = game.npc_rooms["Tower Guardian"]
    game.current_npc_name = "Tower Guardian"
    game.mode = "npc"

    def answer(prompt: str) -> str:
        if game.mode == "npc":
            choices = game.choices()
            for i, choice in enumerate(choices, 1):
                if choice.action == "riddle":
                    return str(i)
            return "quit"
        if game.mode == "riddle":
            return "river"
        return "quit"

    output: list[str] = []
    run_console(game, show_art=False, input_func=answer, output_func=output.append)
    assert game.npcs["Tower Guardian"]["riddle_solved"]
    assert game.player.has_item("star_crystal")
    assert "Wisdom and patience" in "\n".join(output)
