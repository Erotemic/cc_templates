"""Validate Python story definitions, compile letter maps, and manage conversations."""

import textwrap
from .model import Exit, Outcome, Placement, Room, StoryObject

TERRAIN = "#~.gd "
KINDS = {"tile", "spawn", "character", "door", "sign", "item", "rest", "trigger"}
COMMON = {"kind", "tile", "id", "name", "requires", "locked_text", "on_interact", "on_enter"}
DIALOGUE = {"text", "choices", "branches", "set_flags"}
FIELDS = {
    "tile": set(),
    "spawn": set(),
    "character": {"character", "battle"} | DIALOGUE,
    "door": {"to", "entry"},
    "sign": DIALOGUE,
    "item": {"flag"} | DIALOGUE,
    "rest": set(),
    "trigger": set(),
}


class StoryError(ValueError):
    """An author-facing error with a level key and (for map errors) row/column."""


def require(condition, message):
    """Raise StoryError with message when an author-facing content check fails."""
    if not condition:
        raise StoryError(message)


def string(value):
    """Return whether value is a string containing at least one non-whitespace character."""
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    """Return whether value is a list of nonempty strings; an empty list is allowed."""
    return isinstance(value, list) and all(string(v) for v in value)


def check_requirement(value):
    """Validate that requires is absent, one flag string, or a list of flag strings."""
    require(
        value is None or string(value) or strings(value), "requires needs a flag or list of flags"
    )


def check_dialogue(data):
    """Validate text, choice labels, completion flags, and conditional branches.

    data is a Python dictionary returned by the story-building helpers. Raise StoryError for unsupported fields/types;
    recurse through replies and branches without executing dialogue or setting flags.
    """
    if "text" in data:
        require(
            string(data["text"]) or (strings(data["text"]) and data["text"]),
            "text needs a nonempty string or list of strings",
        )
    require(strings(data.get("set_flags", [])), "set_flags needs a list of flag names")
    choices = data.get("choices", [])
    require(isinstance(choices, list), "choices needs a list")
    for choice in choices:
        require(
            isinstance(choice, dict) and string(choice.get("label")), "each choice needs a label"
        )
        require(len(choice["label"]) <= 60, "keep choice labels at most 60 characters")
        require(
            not (set(choice) - {"label", "text", "set_flags", "requires"}), "unknown choice field"
        )
        check_requirement(choice.get("requires"))
        check_dialogue(choice)
    branches = data.get("branches", [])
    require(isinstance(branches, list), "branches needs a list")
    for branch in branches:
        require(isinstance(branch, dict) and "requires" in branch, "each branch needs requires")
        require(
            not (set(branch) - {"text", "choices", "set_flags", "requires"}), "unknown branch field"
        )
        check_requirement(branch["requires"])
        check_dialogue(branch)


def build_story(levels, start_level, start_entry, character_keys):
    """Compile registered Python level dictionaries and validate their links.

    levels maps keys to definitions built with building.level. The explicit
    registry and starting marker live in student_world.py; character_keys comes
    from the battle cast. Return (rooms_by_key, start_level, start_entry).
    Raise StoryError with a level key for invalid maps, legends or links.
    This reads definitions only; it never runs interaction callbacks.
    """
    require(isinstance(levels, dict) and levels, "LEVELS needs a nonempty dictionary")
    rooms, placed = {}, set()
    for level_key, data in levels.items():
        require(string(level_key), "level keys must be nonempty strings")
        try:
            require(isinstance(data, dict), "level must be a dictionary from level(...)")
            require(not (set(data) - {"name", "map", "legend"}), "unknown level field")
            require(string(data.get("name")), "give the level a name")
            rows, legend = data.get("map"), data.get("legend", {})
            require(isinstance(rows, list) and 3 <= len(rows) <= 16, "map needs 3 to 16 rows")
            require(all(isinstance(row, str) for row in rows), "map rows must be strings")
            width = len(rows[0])
            require(
                3 <= width <= 30 and all(len(row) == width for row in rows),
                "map needs equal-length rows, 3 to 30 columns",
            )
            require(isinstance(legend, dict), "legend must be a dictionary")
            for symbol, spec in legend.items():
                require(
                    isinstance(symbol, str) and len(symbol) == 1 and isinstance(spec, dict),
                    "legend keys need one character and values need object definitions",
                )
                kind = spec.get("kind")
                require(
                    isinstance(kind, str) and kind in KINDS, f"{symbol!r}: unknown kind {kind!r}"
                )
                require(
                    not (set(spec) - COMMON - FIELDS[kind]),
                    f"{symbol!r}: unknown field(s): {set(spec) - COMMON - FIELDS[kind]}",
                )
                require(
                    isinstance(spec.get("tile", "."), str)
                    and spec.get("tile", ".") in TERRAIN
                    and len(spec.get("tile", ".")) == 1,
                    f"{symbol!r}: tile must be one of {TERRAIN!r}",
                )
                require(
                    kind == "tile" or spec.get("tile", ".") not in "#~",
                    f"{symbol!r}: objects need walkable ground",
                )
                if "id" in spec:
                    require(string(spec["id"]), f"{symbol!r}: id must be a nonempty string")
                if "name" in spec:
                    require(string(spec["name"]), f"{symbol!r}: name must be a nonempty string")
                check_requirement(spec.get("requires"))
                if "locked_text" in spec:
                    require(string(spec["locked_text"]), "locked_text needs a string")
                check_dialogue(spec)
                for hook in ("on_enter", "on_interact"):
                    if hook in spec:
                        require(
                            callable(spec[hook]),
                            f"{symbol!r}: {hook} needs a Python function, without parentheses",
                        )
                        require(
                            (hook == "on_enter" and kind == "trigger")
                            or (
                                hook == "on_interact"
                                and kind in {"character", "sign", "item", "rest"}
                            ),
                            f"{hook} is not supported for {kind}",
                        )
                if kind == "character":
                    require(
                        spec.get("character") in character_keys, f"{symbol!r}: unknown character"
                    )
                    require(
                        isinstance(spec.get("battle", True), bool), "battle must be True or False"
                    )
                if kind == "door":
                    require(
                        string(spec.get("to")) and string(spec.get("entry")),
                        f"{symbol!r}: doors need to and entry",
                    )
                if kind == "spawn":
                    require(string(spec.get("id")), f"{symbol!r}: spawn needs an id")
                if kind == "item":
                    require(string(spec.get("flag")), f"{symbol!r}: item needs a flag")
                if kind == "tile":
                    require("tile" in spec, f"{symbol!r}: tile kind needs a tile")
            tiles, people, exits, objects, spawns = [], [], [], [], {}
            for y, row in enumerate(rows):
                output = ""
                for x, symbol in enumerate(row):
                    location = f"row {y + 1}, column {x + 1} ({symbol!r})"
                    if symbol not in legend:
                        require(symbol in TERRAIN, f"{location}: add this symbol to the legend")
                        output += "g" if symbol == " " else symbol
                        continue
                    spec = legend[symbol]
                    kind = spec["kind"]
                    tile = (x, y)
                    output += "D" if kind == "door" else spec.get("tile", ".").replace(" ", "g")
                    key = spec.get("id", f"{level_key}:{symbol}:{x}:{y}")
                    if kind == "spawn":
                        require(key not in spawns, f"{location}: duplicate spawn id {key!r}")
                        spawns[key] = tile
                    elif kind == "character":
                        require(key not in placed, f"{location}: duplicate character id {key!r}")
                        placed.add(key)
                        people.append(Placement(key, spec["character"], tile, spec))
                    elif kind == "door":
                        exits.append(Exit(tile, spec["to"], spec["entry"], spec))
                    elif kind != "tile":
                        objects.append(StoryObject(key, kind, tile, spec))
                tiles.append(output)
            require(spawns, "add at least one spawn marker to the map and legend")
            rest = next((obj.tile for obj in objects if obj.kind == "rest"), None)
            rooms[level_key] = Room(
                level_key,
                data["name"],
                tuple(tiles),
                tuple(people),
                tuple(exits),
                rest,
                spawns,
                tuple(objects),
            )
        except (StoryError, TypeError) as error:
            raise StoryError(f"{level_key}: {error}") from error
    for key, room in rooms.items():
        for door in room.exits:
            require(door.destination in rooms, f"{key}: unknown door level {door.destination!r}")
            require(
                door.landing in rooms[door.destination].spawns,
                f"{key}: {door.destination!r} has no spawn {door.landing!r}",
            )
    require(
        isinstance(start_level, str) and start_level in rooms,
        "student_world.py: unknown START_LEVEL",
    )
    require(
        isinstance(start_entry, str) and start_entry in rooms[start_level].spawns,
        "student_world.py: unknown START_ENTRY",
    )
    return rooms, start_level, start_entry


def meets(session, requirement=None):
    """Return whether session satisfies every required story fact.

    requirement can be None, a flag string, or a list of strings (all required).
    Ordinary names check session.flags. 'spared:id' and 'defeated:id' instead
    check the remembered battle outcome for that character placement ID.
    This reads progress without changing it or evaluating Python expressions.
    """
    if requirement is None:
        return True
    requirements = [requirement] if isinstance(requirement, str) else requirement
    for flag in requirements:
        if flag.startswith(("spared:", "defeated:")):
            outcome, key = flag.split(":", 1)
            if (
                session.resolved.get(key)
                != {"spared": Outcome.SPARED, "defeated": Outcome.DEFEATED}[outcome]
            ):
                return False
        elif flag not in session.flags:
            return False
    return True


class Dialogue:
    """Paged story plus optional choices. Movement pauses while this is open."""

    def __init__(self, name, data, session):
        """Open speaker name's conversation using Python story data and shared session.

        Use the first matching branch, or the default dialogue. Prepare pages
        and available choices now; commit flags later when the player confirms.
        """
        self.name, self.session = name, session
        branch = next((b for b in data.get("branches", []) if meets(session, b["requires"])), None)
        self.data = branch or data
        self.pages = self.paginate(self.data.get("text", "..."))
        self.page = 0
        self.choices = [
            c for c in self.data.get("choices", []) if meets(session, c.get("requires"))
        ]
        self.selection = 0
        self.finished = False
        self.cancelled = False

    @staticmethod
    def paginate(text):
        """Return three-line pages from a text string or list of paragraphs.

        Wrap at 48 characters and keep paragraph boundaries as page boundaries.
        No pygame font or display is needed to prepare dialogue.
        """
        paragraphs = [text] if isinstance(text, str) else text
        pages = []
        for paragraph in paragraphs:
            lines = textwrap.wrap(paragraph, width=48) or [""]
            pages.extend("\n".join(lines[i : i + 3]) for i in range(0, len(lines), 3))
        return pages

    @property
    def choosing(self):
        """Return whether the last page is open and there are choices to select."""
        return self.page == len(self.pages) - 1 and bool(self.choices)

    def update(self, controls):
        """Apply one frame's menu/confirm/cancel presses to this conversation.

        Confirm advances a page or commits a choice's flags and opens its reply.
        Confirming the final page commits dialogue completion flags and finishes.
        Cancel closes without completion flags; an already committed choice is
        kept. World reads finished/cancelled to resume walking or offer a battle.
        """
        if controls.cancel:
            self.finished = self.cancelled = True
            return
        if self.choosing:
            self.selection = (self.selection + controls.menu_step) % len(self.choices)
        if not controls.confirm:
            return
        if self.page + 1 < len(self.pages):
            self.page += 1
        elif self.choices:
            choice = self.choices[self.selection]
            # Choosing is the commit point; cancelling its reply does not undo a choice.
            self.session.flags.update(choice.get("set_flags", []))
            self.pages = self.paginate(choice.get("text", "..."))
            self.page, self.choices = 0, []
        else:
            self.session.flags.update(self.data.get("set_flags", []))
            self.finished = True
