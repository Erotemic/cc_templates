from __future__ import annotations

"""Textual front end for rich_single_file_rpg.py.

This app wraps the existing single-file RPG logic in a Textual TUI without
rewriting the game's core systems. The backend game runs in a worker thread,
and this UI turns blocking prompts into widgets.
"""

from collections import Counter
from contextlib import redirect_stdout, redirect_stderr
import builtins
import importlib.util
from pathlib import Path
import queue
import sys
import threading
import traceback
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, RichLog, Static


CORE_PATH = Path(__file__).with_name("version4.py")


def load_core_module() -> Any:
    spec = importlib.util.spec_from_file_location("rpg_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load game core from {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class QueueWriter:
    """Capture stdout/stderr and emit complete lines to the UI queue."""

    def __init__(self, bridge: "BackendBridge"):
        self.bridge = bridge
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self.bridge.emit("log", text=line)
        return len(text)

    def flush(self) -> None:
        if self._buffer:
            self.bridge.emit("log", text=self._buffer)
            self._buffer = ""


class BackendBridge:
    def __init__(self, core: Any):
        self.core = core
        self.events: queue.Queue[dict[str, Any]] = queue.Queue()
        self.responses: queue.Queue[Any] = queue.Queue()
        self.thread: threading.Thread | None = None
        self.game: Any | None = None

    def start(self) -> None:
        self.thread = threading.Thread(target=self._run_backend, daemon=True)
        self.thread.start()

    def emit(self, event_type: str, **payload: Any) -> None:
        self.events.put({"type": event_type, **payload})

    def snapshot(self) -> dict[str, Any]:
        game = self.game
        if game is None:
            return {
                "mode": "boot",
                "goal": "",
                "location": "Starting...",
                "description": "",
                "items": [],
                "npcs": [],
                "features": [],
                "health": 0,
                "max_health": 0,
                "gold": 0,
                "bounty": 0,
                "attack": (0, 0),
                "defense": 0,
                "equipment": {},
                "inventory": [],
                "flags": [],
            }
        location = game.current_location()
        item_db = game.world.item_db
        low, high = game.player.attack_range(item_db)
        counts = Counter(game.player.inventory)
        inventory = []
        seen = set()
        for item_id in game.player.inventory:
            if item_id in seen:
                continue
            seen.add(item_id)
            item = item_db[item_id]
            count = counts[item_id]
            inventory.append((item.name, count))
        equipment = {}
        for slot in game.player.EQUIPMENT_SLOTS:
            item_id = game.player.equipment[slot]
            equipment[slot] = item_db[item_id].name if item_id is not None else "empty"
        return {
            "mode": game.mode,
            "goal": self.goal_text(game),
            "location": location.name,
            "description": location.description,
            "items": [game.item_name(item_id) for item_id in location.items],
            "npcs": [f"{npc.name} ({npc.mood_label()})" for npc in location.npcs],
            "features": [feature.name for feature in location.features],
            "health": game.player.health,
            "max_health": game.player.total_max_hp(item_db),
            "gold": game.player.gold,
            "bounty": game.bounty,
            "attack": (low, high),
            "defense": game.player.total_defense(item_db),
            "equipment": equipment,
            "inventory": inventory,
            "flags": sorted(game.flags),
        }

    def goal_text(self, game: Any) -> str:
        if "jailed" in game.flags:
            return "Serve your time."
        if "quest_started" not in game.flags:
            return "Talk to Elder Mira."
        if "has_star_crystal" in game.flags and "game_won" not in game.flags:
            return "Return the Star Crystal to Elder Mira."
        if "game_won" in game.flags:
            return "The valley has been saved."
        return "Explore the valley and recover the Star Crystal."

    def request_choice(self, options: list[dict[str, Any]], prompt: str) -> int:
        self.emit("state", snapshot=self.snapshot())
        self.emit(
            "choices", prompt=prompt, options=[option["text"] for option in options]
        )
        return int(self.responses.get())

    def request_text(self, prompt: str) -> str:
        self.emit("state", snapshot=self.snapshot())
        self.emit("text_input", prompt=prompt)
        response = self.responses.get()
        return "" if response is None else str(response)

    def request_continue(self, prompt: str) -> None:
        self.emit("state", snapshot=self.snapshot())
        self.emit("continue", prompt=prompt)
        self.responses.get()

    def _run_backend(self) -> None:
        core = self.core
        bridge = self

        class TuiGame(core.Game):
            def __init__(self, bridge: BackendBridge):
                self._bridge = bridge
                super().__init__(player_name="Tav", world=core.StarCrystalWorld())

            def choose(self, options: list[dict], prompt: str = "Choose: ") -> dict:
                index = self._bridge.request_choice(options, prompt)
                selected = options[index]
                core.action_separator(selected.get("text"))
                return selected

        old_input = builtins.input
        old_typewriter = core.typewriter_print
        old_continue = core.prompt_continue

        def fast_typewriter(prefix: str, text: str, word_delay: float = 0.0) -> None:
            print(f"{prefix}{text}")

        def queued_input(prompt: str = "") -> str:
            return bridge.request_text(prompt)

        def queued_continue(prompt: str = "Press Enter to continue...") -> None:
            bridge.request_continue(prompt)

        writer = QueueWriter(bridge)

        try:
            builtins.input = queued_input
            core.typewriter_print = fast_typewriter
            core.prompt_continue = queued_continue
            with redirect_stdout(writer), redirect_stderr(writer):
                bridge.game = TuiGame(bridge)
                bridge.emit("state", snapshot=bridge.snapshot())
                bridge.game.run()
            writer.flush()
            bridge.emit("state", snapshot=bridge.snapshot())
            bridge.emit("game_over", message="Game over.")
        except Exception:
            writer.flush()
            bridge.emit("log", text=traceback.format_exc())
            bridge.emit("game_over", message="The backend crashed.")
        finally:
            builtins.input = old_input
            core.typewriter_print = old_typewriter
            core.prompt_continue = old_continue


class RPGTextualApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }

    #body {
        height: 1fr;
        layout: horizontal;
    }

    #sidebar {
        width: 34;
        min-width: 28;
        border: round $accent;
        padding: 1;
    }

    #main {
        width: 1fr;
        border: round $accent;
    }

    #actions {
        width: 38;
        min-width: 34;
        border: round $accent;
        padding: 1;
    }

    #goal, #location, #status {
        margin-bottom: 1;
        border: round $surface;
        padding: 1;
    }

    #log {
        height: 1fr;
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
    }

    #options Button {
        width: 1fr;
        margin-bottom: 1;
    }

    #text_input {
        margin-top: 1;
    }

    #continue_button {
        margin-top: 1;
        width: 1fr;
    }

    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("m", "menu", "Menu"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.core = load_core_module()
        self.bridge = BackendBridge(self.core)
        self.interaction_mode = "boot"
        self.pending_options: list[str] = []
        self.game_over = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                yield Static("Goal", id="goal")
                yield Static("Location", id="location")
                yield Static("Status", id="status")
            with Vertical(id="main"):
                yield RichLog(id="log", wrap=True, markup=False, auto_scroll=True)
            with Vertical(id="actions"):
                yield Static("Starting up...", id="prompt")
                yield VerticalScroll(id="options")
                yield Input(
                    placeholder="Type response and press Enter",
                    id="text_input",
                    classes="hidden",
                )
                yield Button(
                    "Continue",
                    id="continue_button",
                    variant="primary",
                    classes="hidden",
                )
        yield Footer()

    def on_mount(self) -> None:
        self.bridge.start()
        self.set_interval(0.05, self.poll_backend)

    def action_menu(self) -> None:
        if self.interaction_mode == "choice":
            for i, label in enumerate(self.pending_options):
                if label.lower().startswith("open menu"):
                    self.bridge.responses.put(i)
                    return

    def poll_backend(self) -> None:
        while True:
            try:
                event = self.bridge.events.get_nowait()
            except queue.Empty:
                break
            self.handle_backend_event(event)

    def handle_backend_event(self, event: dict[str, Any]) -> None:
        event_type = event["type"]
        if event_type == "log":
            text = event.get("text", "")
            if text.strip() or text == "":
                self.query_one("#log", RichLog).write(text)
        elif event_type == "state":
            self.update_state(event["snapshot"])
        elif event_type == "choices":
            self.show_choices(event["prompt"], event["options"])
        elif event_type == "text_input":
            self.show_text_input(event["prompt"])
        elif event_type == "continue":
            self.show_continue(event["prompt"])
        elif event_type == "game_over":
            self.game_over = True
            self.query_one("#prompt", Static).update(event.get("message", "Game over."))
            self.clear_options()
            self.hide_text_input()
            self.hide_continue_button()

    def update_state(self, snapshot: dict[str, Any]) -> None:
        goal = self.query_one("#goal", Static)
        location = self.query_one("#location", Static)
        status = self.query_one("#status", Static)

        goal.update(f"[b]Goal[/b]\n{snapshot['goal']}")

        parts = [f"[b]{snapshot['location']}[/b]", "", snapshot["description"]]
        if snapshot["items"]:
            parts.extend(
                ["", "[b]Items here[/b]"] + [f"- {item}" for item in snapshot["items"]]
            )
        if snapshot["npcs"]:
            parts.extend(
                ["", "[b]People / creatures[/b]"]
                + [f"- {npc}" for npc in snapshot["npcs"]]
            )
        if snapshot["features"]:
            parts.extend(
                ["", "[b]Features[/b]"]
                + [f"- {feature}" for feature in snapshot["features"]]
            )
        location.update("\n".join(parts))

        attack_low, attack_high = snapshot["attack"]
        status_lines = [
            "[b]Player[/b]",
            f"HP: {snapshot['health']}/{snapshot['max_health']}",
            f"Attack: {attack_low}-{attack_high}",
            f"Defense: {snapshot['defense']}",
            f"Gold: {snapshot['gold']}",
            f"Bounty: {snapshot['bounty']}",
            "",
            "[b]Equipment[/b]",
        ]
        for slot, item_name in snapshot["equipment"].items():
            status_lines.append(f"- {slot}: {item_name}")
        status_lines.extend(["", "[b]Inventory[/b]"])
        if snapshot["inventory"]:
            for item_name, count in snapshot["inventory"]:
                suffix = f" x{count}" if count > 1 else ""
                status_lines.append(f"- {item_name}{suffix}")
        else:
            status_lines.append("- empty")
        status.update("\n".join(status_lines))

    def clear_options(self) -> None:
        container = self.query_one("#options", VerticalScroll)
        container.remove_children()
        self.pending_options = []

    def show_choices(self, prompt: str, options: list[str]) -> None:
        self.interaction_mode = "choice"
        self.pending_options = list(options)
        self.query_one("#prompt", Static).update(prompt)
        self.hide_text_input()
        self.hide_continue_button()
        container = self.query_one("#options", VerticalScroll)
        container.remove_children()
        for index, label in enumerate(options):
            button = Button(f"{index + 1}. {label}", id=f"opt-{index}")
            container.mount(button)
        first = container.query("Button").first()
        if first is not None:
            first.focus()

    def show_text_input(self, prompt: str) -> None:
        self.interaction_mode = "text"
        self.clear_options()
        self.query_one("#prompt", Static).update(prompt)
        self.hide_continue_button()
        input_widget = self.query_one("#text_input", Input)
        input_widget.remove_class("hidden")
        input_widget.value = ""
        input_widget.placeholder = prompt or "Type response and press Enter"
        input_widget.focus()

    def hide_text_input(self) -> None:
        input_widget = self.query_one("#text_input", Input)
        input_widget.add_class("hidden")
        input_widget.value = ""

    def show_continue(self, prompt: str) -> None:
        self.interaction_mode = "continue"
        self.clear_options()
        self.hide_text_input()
        self.query_one("#prompt", Static).update(prompt)
        button = self.query_one("#continue_button", Button)
        button.remove_class("hidden")
        button.focus()

    def hide_continue_button(self) -> None:
        self.query_one("#continue_button", Button).add_class("hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("opt-") and self.interaction_mode == "choice":
            index = int(button_id.split("-", 1)[1])
            self.bridge.responses.put(index)
            self.clear_options()
            self.query_one("#prompt", Static).update("Resolving action...")
        elif button_id == "continue_button" and self.interaction_mode == "continue":
            self.bridge.responses.put("")
            self.hide_continue_button()
            self.query_one("#prompt", Static).update("Continuing...")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "text_input" or self.interaction_mode != "text":
            return
        self.bridge.responses.put(event.value)
        self.hide_text_input()
        self.query_one("#prompt", Static).update("Resolving input...")


if __name__ == "__main__":
    RPGTextualApp().run()
