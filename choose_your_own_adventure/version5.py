from __future__ import annotations

"""
Version 5: a graphical/textual front end for the rich RPG.

This file does not replace the game logic in version4.
Instead, it wraps that game in a Textual user interface.

This version is useful for teaching:
- separating core logic from presentation
- adapting a command-line game to another interface
- threading and event-driven UI ideas
- how to reuse an existing backend instead of rewriting it

The important lesson here is that the game systems live in version4,
while this file focuses on input, output, layout, and interaction.

How this file works
-------------------
The big challenge: v4 is written assuming a terminal — it calls input()
and print() freely. Textual is event-driven and runs on the main thread,
so we can't just call v4.Game().run() inside it (the blocking input()s
would freeze the UI).

The solution this file uses, in three layers:

1. Run v4's game loop on a *background thread* (BackendBridge._run_backend).
2. Replace the game's I/O with thread-safe queues:
     - print() output is captured by QueueWriter and pushed onto an
       "events" queue that the UI polls.
     - input() is monkey-patched to *block on a "responses" queue* until
       the UI puts a value into it.
3. The Textual app polls the events queue every 50ms (set_interval),
   updates the UI, and pushes user clicks back onto the responses queue.

This is a classic *backend / frontend separation* and a classic
*producer/consumer with queues* pattern — both common in real software.
"""

from collections import Counter
# `redirect_stdout` / `redirect_stderr` are context managers that
# temporarily replace sys.stdout / sys.stderr so any print() inside the
# `with` block writes to our fake stream instead.
from contextlib import redirect_stdout, redirect_stderr
import builtins             # we'll replace builtins.input to redirect input()
import importlib.util       # used to load version4.py by file path
from pathlib import Path
import queue                # thread-safe FIFO queues
import sys
import threading            # to run the game on a worker thread
import traceback
from typing import Any

# Textual is a framework for building terminal-based UIs that look like
# graphical apps. App is the root, ComposeResult is the type returned by
# compose() (a generator of widgets), and the rest are widget classes.
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, RichLog, Static


# Path to v4 so we can load it as a module without `import version4`.
# Using a file path (instead of a normal import) keeps these example
# files independent of the package layout — they work no matter where
# the file is run from.
CORE_PATH = Path(__file__).with_name("version4.py")


def load_core_module() -> Any:
    # Dynamic import: read version4.py from disk and execute it as a
    # fresh module called "rpg_core". `module.Game`, `module.StarCrystalWorld`
    # etc. are then available as normal attributes.
    spec = importlib.util.spec_from_file_location("rpg_core", CORE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load game core from {CORE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # register so other imports can find it
    spec.loader.exec_module(module)
    return module


class QueueWriter:
    """Capture stdout/stderr and emit complete lines to the UI queue."""

    # We "duck-type" a file-like object: anything that has .write(str)
    # and .flush() can be used as a stdout replacement. Python doesn't
    # require us to inherit from a particular base class — having the
    # right methods is enough.
    #
    # We buffer partial output and only emit complete lines, so each
    # log message in the UI corresponds to one print() line.

    def __init__(self, bridge: "BackendBridge"):
        self.bridge = bridge
        self._buffer = ""

    def write(self, text: str) -> int:
        self._buffer += text
        # As long as we have a newline, split off the next complete line
        # and push it to the UI as a log event.
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self.bridge.emit("log", text=line)
        return len(text)

    def flush(self) -> None:
        # Emit any leftover partial line. Called on shutdown to make
        # sure we don't lose the last bit of output.
        if self._buffer:
            self.bridge.emit("log", text=self._buffer)
            self._buffer = ""


class BackendBridge:
    # The "bridge" between the worker thread (running the v4 game) and
    # the UI thread (running Textual). Two queues do the actual work:
    #
    #   events    -- backend pushes, UI pops. Anything the player should
    #                see: log lines, snapshots, prompts.
    #   responses -- UI pushes, backend pops. The player's answer to a
    #                prompt (a number, a string, or None to continue).
    #
    # Because queue.Queue is thread-safe, neither side needs explicit
    # locking: each operation is atomic.

    def __init__(self, core: Any):
        self.core = core
        self.events: queue.Queue[dict[str, Any]] = queue.Queue()
        self.responses: queue.Queue[Any] = queue.Queue()
        self.thread: threading.Thread | None = None
        self.game: Any | None = None

    def start(self) -> None:
        # daemon=True means the thread dies automatically when the main
        # program exits — handy for a UI app, since closing the window
        # should not leave a zombie game loop running in the background.
        self.thread = threading.Thread(target=self._run_backend, daemon=True)
        self.thread.start()

    def emit(self, event_type: str, **payload: Any) -> None:
        # Push an event dict onto the events queue. The UI polls this
        # queue regularly (see RPGTextualApp.poll_backend).
        self.events.put({"type": event_type, **payload})

    def snapshot(self) -> dict[str, Any]:
        # Build a plain-dict picture of the current game state. The UI
        # only ever reads from snapshots — it never touches game/player
        # objects directly. This keeps thread boundaries clean: the
        # backend mutates objects on its thread; the UI only sees frozen
        # copies via queues.
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

    # ---- Request/response calls -----------------------------------------
    # These run on the backend thread. Each one:
    #   1. Sends a state snapshot + a prompt event to the UI.
    #   2. Calls .get() on the responses queue, which BLOCKS until the
    #      UI thread answers via .put(...).
    # That blocking get is the secret sauce — it lets the v4 game keep
    # using `input()`-shaped synchronous calls even though the UI is
    # event-driven.

    def request_choice(self, options: list[dict[str, Any]], prompt: str) -> int:
        self.emit("state", snapshot=self.snapshot())
        self.emit(
            "choices", prompt=prompt, options=[option["text"] for option in options]
        )
        return int(self.responses.get())  # blocks until UI sends an int

    def request_text(self, prompt: str) -> str:
        self.emit("state", snapshot=self.snapshot())
        self.emit("text_input", prompt=prompt)
        response = self.responses.get()
        return "" if response is None else str(response)

    def request_continue(self, prompt: str) -> None:
        self.emit("state", snapshot=self.snapshot())
        self.emit("continue", prompt=prompt)
        self.responses.get()  # value doesn't matter — just unblocks us

    def _run_backend(self) -> None:
        # This method runs on the worker thread. Its job is to set up
        # the I/O redirection, instantiate the v4 game, and run it.
        core = self.core
        bridge = self

        # A subclass of v4's Game that overrides .choose() so menu
        # selection goes through our bridge instead of input(). The rest
        # of v4's Game logic is inherited unchanged.
        class TuiGame(core.Game):
            def __init__(self, bridge: BackendBridge):
                self._bridge = bridge
                super().__init__(player_name="Tav", world=core.StarCrystalWorld())

            def choose(self, options: list[dict], prompt: str = "Choose: ") -> dict:
                index = self._bridge.request_choice(options, prompt)
                selected = options[index]
                core.action_separator(selected.get("text"))
                return selected

        # Save the originals so the `finally` block can restore them.
        # *Monkey-patching* like this is something to use sparingly — but
        # here it is the cleanest way to make v4 (which uses input() and
        # custom typewriter prints) play well with our async UI.
        old_input = builtins.input
        old_typewriter = core.typewriter_print
        old_continue = core.prompt_continue

        # Strip the typewriter delay — Textual will animate the log itself.
        def fast_typewriter(prefix: str, text: str, word_delay: float = 0.0) -> None:
            print(f"{prefix}{text}")

        # When v4 calls input(...), it actually blocks here until the UI
        # responds via the responses queue.
        def queued_input(prompt: str = "") -> str:
            return bridge.request_text(prompt)

        def queued_continue(prompt: str = "Press Enter to continue...") -> None:
            bridge.request_continue(prompt)

        writer = QueueWriter(bridge)

        try:
            # Install the patches and the redirected stdout/stderr. From
            # this point on, *every* print() and input() inside v4 flows
            # through our queues to the UI.
            builtins.input = queued_input
            core.typewriter_print = fast_typewriter
            core.prompt_continue = queued_continue
            with redirect_stdout(writer), redirect_stderr(writer):
                bridge.game = TuiGame(bridge)
                bridge.emit("state", snapshot=bridge.snapshot())
                bridge.game.run()  # v4's main game loop runs here
            writer.flush()
            bridge.emit("state", snapshot=bridge.snapshot())
            bridge.emit("game_over", message="Game over.")
        except Exception:
            # Surface backend crashes to the log so the user can see them
            # instead of the worker thread silently dying.
            writer.flush()
            bridge.emit("log", text=traceback.format_exc())
            bridge.emit("game_over", message="The backend crashed.")
        finally:
            # Always restore globals — otherwise the next thing to call
            # input() in this process would still be talking to our queue.
            builtins.input = old_input
            core.typewriter_print = old_typewriter
            core.prompt_continue = old_continue


# ============================================================
# Textual UI (front-end)
# ============================================================
# Textual is a Python framework for building rich UIs that run inside a
# terminal. If you've ever written HTML + CSS + JavaScript, the model
# will feel familiar:
#   - HTML  ->  the widget tree built by `compose()` below.
#   - CSS   ->  the CSS string below (Textual uses its own CSS dialect).
#   - JS    ->  the on_*() event handler methods.
# Widgets are nestable building blocks: Header, Footer, Static (a text
# label), Button, Input (a text field), RichLog (a scrolling log),
# Horizontal/Vertical (layout containers), VerticalScroll (a scrollable
# vertical container).
#
# Textual runs on the main thread and pumps its own event loop. We never
# call blocking input() here — instead we poll the bridge's events queue
# every 50ms (see on_mount + poll_backend below) so the UI stays
# responsive while the game thinks in the background.


class RPGTextualApp(App):
    # ---- CSS (Textual's own CSS dialect) -----------------------------
    # CSS rules are written as: <selector> { <property>: <value>; ... }
    # Selectors:
    #   `Screen`       -- match by class name (any Screen widget)
    #   `#sidebar`     -- match by id (the widget with id="sidebar")
    #   `.hidden`      -- match by class (the widget has classes="hidden")
    #   `#options Button` -- descendant: any Button inside #options
    # Properties students will see most:
    #   layout:        vertical / horizontal -- direction of children
    #   width / height: a number = cells; "1fr" = "fill remaining space"
    #                   (think of `fr` like flex-grow in web CSS)
    #   border:        round $accent -- rounded border in a theme color
    #                   ($accent is a *theme variable* Textual provides;
    #                   change the theme and every widget using $accent
    #                   updates automatically)
    #   padding/margin: spacing inside / outside the border
    #   display: none  -- hide the widget completely (used by .hidden)
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

    # ---- Keyboard shortcuts ------------------------------------------
    # Each tuple is (key, action_name, description). When the user
    # presses the key, Textual calls `self.action_<name>()` — note the
    # naming rule: BINDING name "menu" -> method action_menu(). The
    # description shows up in the Footer widget at the bottom.
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("m", "menu", "Menu"),
    ]

    def __init__(self) -> None:
        # Always call super().__init__() first when subclassing App so
        # Textual's own setup runs.
        super().__init__()
        self.core = load_core_module()
        self.bridge = BackendBridge(self.core)
        # `interaction_mode` is our own little state machine for what
        # the player should be doing right now: "choice" (click a
        # button), "text" (type something), "continue" (press a button
        # to advance), or "boot" (game still loading).
        self.interaction_mode = "boot"
        self.pending_options: list[str] = []
        self.game_over = False

    def compose(self) -> ComposeResult:
        # compose() is Textual's "build the screen" hook. It's a
        # *generator* — each `yield` adds a widget to the tree. The
        # `with Container(...):` form opens a container so any widgets
        # yielded inside the block become its children. This is how we
        # build a nested layout without writing a tree by hand.
        #
        # Final layout of this app:
        #   Header                  (top bar with the app title)
        #   Horizontal #body
        #     Vertical #sidebar     (Goal / Location / Status panels)
        #     Vertical #main        (the scrolling log)
        #     Vertical #actions     (prompt + buttons + input field)
        #   Footer                  (bottom bar with key hints)
        yield Header(show_clock=False)
        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                # Static: a non-interactive text label. We set initial
                # text here and call .update(...) later to change it.
                yield Static("Goal", id="goal")
                yield Static("Location", id="location")
                yield Static("Status", id="status")
            with Vertical(id="main"):
                # RichLog: a scrolling log of text. auto_scroll=True
                # means new lines push the view to the bottom. markup=
                # False means [b]...[/b] tags appear as literal text;
                # set it True to render Rich markup (we use markup on
                # the Static widgets instead).
                yield RichLog(id="log", wrap=True, markup=False, auto_scroll=True)
            with Vertical(id="actions"):
                yield Static("Starting up...", id="prompt")
                # VerticalScroll: scrollable column. We mount Buttons
                # into this container at runtime when the game asks
                # the player to choose.
                yield VerticalScroll(id="options")
                # `classes="hidden"` starts the widget invisible. We
                # use add_class / remove_class later to show/hide it
                # — the .hidden CSS rule above is what makes that work.
                yield Input(
                    placeholder="Type response and press Enter",
                    id="text_input",
                    classes="hidden",
                )
                # variant="primary" gives Buttons a highlighted color.
                # Other values: "default", "success", "warning", "error".
                yield Button(
                    "Continue",
                    id="continue_button",
                    variant="primary",
                    classes="hidden",
                )
        yield Footer()

    def on_mount(self) -> None:
        # `on_mount` is a Textual *lifecycle hook*: it runs once after
        # compose() builds the widget tree and before the user sees
        # anything. Common uses: kick off background work, set timers,
        # focus a starting widget. set_interval(seconds, callback) tells
        # Textual to call our function on a timer — here, 20 times a
        # second to drain whatever events the backend has produced.
        self.bridge.start()
        self.set_interval(0.05, self.poll_backend)

    def action_menu(self) -> None:
        # Triggered by the "m" BINDING above (the name "menu" maps to
        # this method via the action_<name> convention). If the player
        # is in a choice menu and one of the options is "Open menu",
        # we click it for them — a small keyboard shortcut into the
        # in-game menu.
        if self.interaction_mode == "choice":
            for i, label in enumerate(self.pending_options):
                if label.lower().startswith("open menu"):
                    self.bridge.responses.put(i)
                    return

    def poll_backend(self) -> None:
        # Drain every pending event in one tick. get_nowait() raises
        # queue.Empty when there's nothing left, which is how we exit.
        while True:
            try:
                event = self.bridge.events.get_nowait()
            except queue.Empty:
                break
            self.handle_backend_event(event)

    def handle_backend_event(self, event: dict[str, Any]) -> None:
        # One dispatch per event type. This is the "consumer" side of
        # the producer/consumer pattern — the backend produces events
        # of named types, this method routes them to UI updates.
        event_type = event["type"]
        if event_type == "log":
            text = event.get("text", "")
            if text.strip() or text == "":
                # query_one finds exactly one widget by selector, just
                # like document.querySelector in the browser. The second
                # argument is a type assertion: "trust me, this is a
                # RichLog" — useful so editors/type-checkers know what
                # methods are available (.write here).
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
        # Look up the three sidebar widgets and refill them with
        # formatted text built from the latest snapshot. Note `[b]...[/b]`:
        # those are *Rich markup* tags (Rich is the library Textual uses
        # for styled text). [b]bold[/b], [i]italic[/i], [red]colored[/red],
        # and many others are supported. They render as styling, not as
        # literal characters, on widgets where markup is enabled.
        goal = self.query_one("#goal", Static)
        location = self.query_one("#location", Static)
        status = self.query_one("#status", Static)

        # Static.update(text) replaces the widget's contents entirely.
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
        # remove_children() unmounts every widget inside the container
        # — a clean slate before we rebuild the menu on the next turn.
        container = self.query_one("#options", VerticalScroll)
        container.remove_children()
        self.pending_options = []

    def show_choices(self, prompt: str, options: list[str]) -> None:
        # Build a fresh button per option and *mount* them into the
        # container. `mount` is the Textual API for adding a widget to
        # the live tree — like document.appendChild in the browser.
        self.interaction_mode = "choice"
        self.pending_options = list(options)
        self.query_one("#prompt", Static).update(prompt)
        self.hide_text_input()
        self.hide_continue_button()
        container = self.query_one("#options", VerticalScroll)
        container.remove_children()
        for index, label in enumerate(options):
            # Each Button gets a unique id so on_button_pressed below
            # can tell which one was clicked just from the id.
            button = Button(f"{index + 1}. {label}", id=f"opt-{index}")
            container.mount(button)
        # query() returns *all* matches (compare query_one which expects
        # exactly one). .first() then picks the first match, and .focus()
        # moves keyboard focus there so the user can press Enter
        # immediately to pick option 1.
        first = container.query("Button").first()
        if first is not None:
            first.focus()

    def show_text_input(self, prompt: str) -> None:
        # Toggling visibility is done with CSS classes, not by destroying
        # the widget: remove_class("hidden") makes the .hidden rule no
        # longer match, so display:none stops applying. This is faster
        # than mount/unmount and preserves any state on the widget.
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
        # Add the .hidden class -> CSS display:none kicks in -> widget
        # disappears (without being destroyed).
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

    # ---- UI -> backend handoff -----------------------------------------
    # These methods are Textual *message handlers*. When a Button is
    # clicked, Textual posts a Button.Pressed message; any method named
    # `on_button_pressed` on a parent widget receives it. Same for
    # `on_input_submitted` (Input.Submitted) when the user hits Enter
    # in a text field. This is Textual's version of event listeners.
    # Each one calls `self.bridge.responses.put(...)`, which unblocks
    # whichever request_*() call is waiting on that queue.

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # event.button is the Button widget that was pressed. We stored
        # the option index in its id ("opt-3"), so we can read it back.
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
