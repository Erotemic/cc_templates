"""Full Textual frontend for the capstone AdventureGame.

This restores the strongest UI ideas from the original v5-v8 sequence while
keeping the cleaned architecture: the frontend calls ``describe()``,
``choices()``, ``apply()``, ``submit_riddle_answer()``, and ``snapshot()``
directly.  There are no worker threads, redirected terminal streams, or queue bridges.
"""

from __future__ import annotations

from collections.abc import Iterable
import re

from .game import AdventureGame


def _stream_chunks(lines: Iterable[str]) -> list[str]:
    """Break result text into readable typewriter chunks.

    Streaming belongs to presentation.  The game engine still returns complete
    result strings immediately, which keeps tests and alternate frontends
    deterministic.
    """
    text = "\n".join(line for line in lines if line)
    if not text:
        return []
    # Keep whitespace with its neighboring words so a timer tick advances by a
    # visible amount rather than one painfully slow character at a time.
    return [part for part in re.split(r"(\s+)", text) if part]


def run_textual(game: AdventureGame) -> None:
    """Run the full capstone UI.  Textual remains an optional dependency."""
    try:
        from textual.app import App, ComposeResult
        from textual.containers import Horizontal, Vertical, VerticalScroll
        from textual.events import Key
        from textual.widgets import Footer, Header, Input, OptionList, RichLog, Static
    except ImportError as ex:  # pragma: no cover - depends on local setup
        raise RuntimeError(
            "The capstone Textual UI needs the optional 'textual' package. "
            "Install it with: python -m pip install textual"
        ) from ex

    # ``art`` is a sibling package of ``engine`` when the capstone scripts are
    # launched directly (the normal student workflow).
    from art.catalog import choose_art

    class CapstoneAdventureApp(App):
        CSS = """
        Screen {
            layout: vertical;
        }

        #body {
            height: 1fr;
            layout: horizontal;
        }

        #sidebar {
            width: 35;
            min-width: 28;
            border: round $accent;
            padding: 1;
        }

        #main {
            width: 1fr;
            border: round $accent;
            padding: 1;
        }

        #actions {
            width: 40;
            min-width: 34;
            border: round $accent;
            padding: 1;
        }

        #goal, #location, #status {
            height: auto;
            margin-bottom: 1;
            border: round $surface;
            padding: 1;
        }

        #ascii_art {
            height: 18;
            min-height: 12;
            border: round $surface;
            padding: 1;
            margin-bottom: 1;
            content-align: center middle;
            overflow: auto;
        }

        #current_event {
            height: 1fr;
            min-height: 7;
            border: round $surface;
            padding: 1;
            margin-bottom: 1;
            overflow-y: auto;
        }

        #log_status {
            height: auto;
            margin-bottom: 1;
            border: round $surface;
            padding: 0 1;
        }

        #history {
            height: 6;
            min-height: 4;
            max-height: 13;
            border: round $surface;
            padding: 1;
        }

        #prompt {
            margin-bottom: 1;
            min-height: 3;
            border: round $surface;
            padding: 1;
        }

        #options {
            height: 1fr;
            margin-bottom: 1;
        }

        #options:focus {
            border: round $accent;
        }

        #text_input {
            margin-top: 1;
        }

        .hidden {
            display: none;
        }
        """

        BINDINGS = [
            ("q", "quit", "Quit"),
            ("m", "menu", "Inventory"),
            ("c", "clear_history", "Clear history"),
            ("l", "toggle_log", "Toggle log"),
            ("L", "toggle_log", "Toggle log"),
            ("a", "toggle_art", "Toggle art"),
            ("escape", "focus_choices", "Focus choices"),
        ]

        def __init__(self, current_game: AdventureGame) -> None:
            super().__init__()
            self.game = current_game
            self.pending_choices = []
            self.current_event_text = ""
            self.latest_complete_event = ""
            self.history_line_count = 0
            self.log_collapsed = True
            self.art_collapsed = False
            self.stream_queue: list[str] = []
            self.stream_active = False

        def compose(self) -> ComposeResult:
            yield Header(show_clock=False)
            with Horizontal(id="body"):
                with VerticalScroll(id="sidebar"):
                    yield Static("Goal", id="goal", markup=False)
                    yield Static("Location", id="location", markup=False)
                    yield Static("Status", id="status", markup=False)
                with Vertical(id="main"):
                    yield Static("Scene art", id="ascii_art", markup=False)
                    yield Static(
                        "Latest outcome will appear here.",
                        id="current_event",
                        markup=False,
                    )
                    yield Static(
                        "History hidden. Press L to show.",
                        id="log_status",
                        markup=False,
                    )
                    yield RichLog(
                        id="history",
                        wrap=True,
                        markup=False,
                        auto_scroll=True,
                        max_lines=800,
                        classes="hidden",
                    )
                with Vertical(id="actions"):
                    yield Static("Choose an action.", id="prompt", markup=False)
                    yield OptionList(id="options", markup=False)
                    yield Input(
                        placeholder="Type response and press Enter",
                        id="text_input",
                        classes="hidden",
                    )
            yield Footer()

        def on_mount(self) -> None:
            self.title = self.game.world["name"]
            self.sub_title = "Capstone adventure"
            self.set_interval(0.025, self.drain_stream)
            self.refresh_view()

        # ------------------------------------------------------------
        # Keyboard actions
        # ------------------------------------------------------------
        def action_menu(self) -> None:
            if self.stream_active or self.game.mode in {"combat", "riddle"}:
                return
            for choice in self.game.choices():
                if choice.action == "inventory":
                    self.archive_current_event()
                    self.present_result(self.game.apply("inventory"))
                    return

        def action_focus_choices(self) -> None:
            if self.game.mode == "riddle":
                self.query_one("#text_input", Input).focus()
            else:
                self.query_one("#options", OptionList).focus()

        def action_clear_history(self) -> None:
            self.query_one("#history", RichLog).clear()
            self.history_line_count = 0
            self.update_history_size()

        def action_toggle_log(self) -> None:
            self.log_collapsed = not self.log_collapsed
            history = self.query_one("#history", RichLog)
            status = self.query_one("#log_status", Static)
            if self.log_collapsed:
                history.add_class("hidden")
                status.update("History hidden. Press L to show.")
            else:
                history.remove_class("hidden")
                status.update("History visible. Press L to hide.")
                self.update_history_size()

        def action_toggle_art(self) -> None:
            self.art_collapsed = not self.art_collapsed
            art = self.query_one("#ascii_art", Static)
            if self.art_collapsed:
                art.add_class("hidden")
            else:
                art.remove_class("hidden")
                self.update_art()

        # ------------------------------------------------------------
        # Rendering
        # ------------------------------------------------------------
        def normalize_event_text(self) -> str:
            text = self.current_event_text.strip("\n")
            if not text:
                return "Latest outcome will appear here."
            lines = text.splitlines()
            normalized: list[str] = []
            previous_blank = False
            for line in lines:
                blank = not line.strip()
                if blank and previous_blank:
                    continue
                normalized.append(line)
                previous_blank = blank
            return "\n".join(normalized)

        def render_current_event(self) -> None:
            self.query_one("#current_event", Static).update(self.normalize_event_text())

        def archive_current_event(self) -> None:
            text = self.normalize_event_text()
            if not text or text == "Latest outcome will appear here.":
                return
            history = self.query_one("#history", RichLog)
            history.write("-" * 56)
            self.history_line_count += 1
            for line in text.splitlines():
                history.write(line)
                self.history_line_count += 1
            self.current_event_text = ""
            self.render_current_event()
            self.update_history_size()

        def update_history_size(self) -> None:
            if self.log_collapsed:
                return
            history = self.query_one("#history", RichLog)
            history.styles.height = max(4, min(13, self.history_line_count + 2))

        def update_art(self) -> None:
            if self.art_collapsed:
                return
            snapshot = self.game.snapshot()
            _, title, drawing = choose_art(snapshot, self.latest_complete_event)
            self.query_one("#ascii_art", Static).update(f"{title}\n\n{drawing}")

        def update_state_panels(self) -> None:
            snapshot = self.game.snapshot()
            self.query_one("#goal", Static).update(f"GOAL\n{snapshot['goal']}")

            location_lines = [snapshot["location"], "", snapshot["description"]]
            if snapshot["items"]:
                location_lines += ["", "Items here:"] + [f"- {x}" for x in snapshot["items"]]
            if snapshot["npcs"]:
                location_lines += ["", "People / creatures:"] + [f"- {x}" for x in snapshot["npcs"]]
            if snapshot["features"]:
                location_lines += ["", "Features:"] + [f"- {x}" for x in snapshot["features"]]
            self.query_one("#location", Static).update("\n".join(location_lines))

            low, high = snapshot["attack"]
            status_lines = [
                "PLAYER",
                f"HP: {snapshot['health']}/{snapshot['max_health']}",
                f"Attack: {low}-{high}",
                f"Defense: {snapshot['defense']}",
                f"Gold: {snapshot['gold']}",
                f"Bounty: {snapshot['bounty']}",
                "",
                "Equipment:",
            ]
            for slot, item in snapshot["equipment"].items():
                status_lines.append(f"- {slot}: {item}")
            status_lines += ["", "Inventory:"]
            if snapshot["inventory"]:
                for name, count in snapshot["inventory"]:
                    suffix = f" x{count}" if count > 1 else ""
                    status_lines.append(f"- {name}{suffix}")
            else:
                status_lines.append("- empty")
            self.query_one("#status", Static).update("\n".join(status_lines))
            self.update_art()

        def clear_options(self) -> None:
            options = self.query_one("#options", OptionList)
            options.clear_options()
            self.pending_choices = []

        def show_choices(self) -> None:
            self.hide_text_input()
            self.pending_choices = list(self.game.choices())
            options = self.query_one("#options", OptionList)
            options.clear_options()
            labels = [f"{i}. {choice.text}" for i, choice in enumerate(self.pending_choices, 1)]
            if labels:
                options.add_options(labels)
                options.highlighted = 0
                options.focus()
            prompt = "Use Up/Down + Enter, number keys 1-9, or click."
            if self.game.over:
                prompt = self.game.ending or ("You win." if self.game.won else "Game over.")
            self.query_one("#prompt", Static).update(prompt)

        def show_text_input(self) -> None:
            self.clear_options()
            prompt = self.game.text_prompt() or "Type your answer and press Enter."
            self.query_one("#prompt", Static).update(prompt)
            widget = self.query_one("#text_input", Input)
            widget.remove_class("hidden")
            widget.value = ""
            widget.placeholder = "Type your answer and press Enter"
            widget.focus()

        def hide_text_input(self) -> None:
            widget = self.query_one("#text_input", Input)
            widget.add_class("hidden")
            widget.value = ""

        def refresh_view(self) -> None:
            self.update_state_panels()
            if self.stream_active:
                return
            if self.game.over:
                self.clear_options()
                self.hide_text_input()
                self.query_one("#prompt", Static).update(
                    self.game.ending or ("You win." if self.game.won else "Game over.")
                )
                return
            if self.game.mode == "riddle":
                self.show_text_input()
            else:
                self.show_choices()

        # ------------------------------------------------------------
        # Result streaming / current event focus
        # ------------------------------------------------------------
        def present_result(self, lines: list[str]) -> None:
            self.clear_options()
            self.hide_text_input()
            self.latest_complete_event = "\n".join(line for line in lines if line)
            self.update_state_panels()
            chunks = _stream_chunks(lines)
            if not chunks:
                self.current_event_text = ""
                self.render_current_event()
                self.refresh_view()
                return
            # Paint the first chunk synchronously in the selection handler so
            # feedback is visible immediately, even before the first timer tick.
            self.current_event_text = chunks.pop(0)
            self.stream_queue = chunks
            self.stream_active = bool(chunks)
            self.render_current_event()
            if self.stream_active:
                self.query_one("#prompt", Static).update("Resolving action...")
            else:
                self.refresh_view()

        def drain_stream(self) -> None:
            if not self.stream_active:
                return
            if self.stream_queue:
                # Two tokens per tick keeps the animation visible without
                # making longer dialogue frustrating.
                for _ in range(min(2, len(self.stream_queue))):
                    self.current_event_text += self.stream_queue.pop(0)
                self.render_current_event()
                return
            self.stream_active = False
            self.refresh_view()

        # ------------------------------------------------------------
        # Input handlers
        # ------------------------------------------------------------
        def perform_choice(self, index: int) -> None:
            if self.stream_active or not (0 <= index < len(self.pending_choices)):
                return
            choice = self.pending_choices[index]
            self.archive_current_event()
            self.present_result(self.game.apply(choice.action))

        def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
            self.perform_choice(event.option_index)

        def on_key(self, event: Key) -> None:
            if self.stream_active or self.game.mode == "riddle":
                return
            count = len(self.pending_choices)
            if count == 0:
                return
            options = self.query_one("#options", OptionList)
            if self.focused is options and event.key in {"up", "down", "enter"}:
                return
            if event.key == "up":
                current = options.highlighted if options.highlighted is not None else 0
                options.highlighted = max(0, current - 1)
                event.stop()
            elif event.key == "down":
                current = options.highlighted if options.highlighted is not None else 0
                options.highlighted = min(count - 1, current + 1)
                event.stop()
            elif event.key == "enter":
                self.perform_choice(options.highlighted or 0)
                event.stop()
            elif len(event.key) == 1 and event.key.isdigit():
                index = int(event.key) - 1
                if 0 <= index < count:
                    options.highlighted = index
                    self.perform_choice(index)
                    event.stop()

        def on_input_submitted(self, event: Input.Submitted) -> None:
            if event.input.id != "text_input" or self.game.mode != "riddle":
                return
            self.archive_current_event()
            self.present_result(self.game.submit_riddle_answer(event.value))

    CapstoneAdventureApp(game).run()
