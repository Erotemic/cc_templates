"""Optional Textual frontend for the SAME AdventureGame used by console.py.

There are no worker threads, redirected stdout, monkey-patched input(), or
queues. A button press simply calls ``game.apply(action)`` and redraws from
``game.describe()`` / ``game.choices()``.
"""

from __future__ import annotations

from adventure.core import AdventureGame


def run_textual(game: AdventureGame) -> None:
    """Run a Textual UI. Textual is imported only when this function is used."""
    try:
        from textual.app import App, ComposeResult
        from textual.containers import Vertical, VerticalScroll
        from textual.widgets import Button, Footer, Header, Static
    except ImportError as ex:
        raise RuntimeError(
            "Textual is optional. Install it with: python -m pip install textual"
        ) from ex

    class AdventureApp(App):
        CSS = """
        #body {
            padding: 1 2;
        }
        #story {
            height: auto;
            min-height: 8;
            margin-bottom: 1;
        }
        #results {
            height: auto;
            min-height: 4;
            margin-bottom: 1;
        }
        #choices Button {
            width: 100%;
            margin-bottom: 1;
        }
        """

        def __init__(self, current_game: AdventureGame) -> None:
            super().__init__()
            self.game = current_game
            self.last_result: list[str] = []

        def compose(self) -> ComposeResult:
            yield Header()
            with VerticalScroll(id="body"):
                yield Static(id="story")
                yield Static(id="results")
                yield Vertical(id="choices")
            yield Footer()

        def on_mount(self) -> None:
            self.title = self.game.world.title
            self.refresh_game_view()

        def refresh_game_view(self) -> None:
            story = self.query_one("#story", Static)
            results = self.query_one("#results", Static)
            choices_box = self.query_one("#choices", Vertical)

            story.update("\n".join(self.game.describe()))
            results.update("\n".join(self.last_result))
            choices_box.remove_children()

            if self.game.over:
                ending = self.game.ending or ("You win!" if self.game.won else "Game over.")
                results.update(ending)
                choices_box.mount(Button("Quit", id="quit"))
                return

            for number, choice in enumerate(self.game.choices()):
                choices_box.mount(
                    Button(choice.text, id=f"choice-{number}", name=choice.action)
                )
            choices_box.mount(Button("Quit", id="quit", variant="error"))

        def on_button_pressed(self, event: Button.Pressed) -> None:
            button = event.button
            if button.id == "quit":
                self.exit()
                return

            action = button.name
            self.last_result = self.game.apply(action)
            self.refresh_game_view()

    AdventureApp(game).run()
