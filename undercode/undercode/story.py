"""Load letter maps and dialogue data. No pygame, eval, or executable story files."""

import json
from pathlib import Path
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
    """An author-facing error with a filename and (for map errors) row/column."""


def require(condition, message):
    if not condition:
        raise StoryError(message)


def string(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and all(string(v) for v in value)


def check_requirement(value):
    require(
        value is None or string(value) or strings(value), "requires needs a flag or list of flags"
    )


def check_dialogue(data):
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


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf8"))
    except (ValueError, OSError) as error:
        raise StoryError(f"{path.name}: {error}") from error


def load_story(directory, character_keys, mechanics):
    """Compile every non-underscore JSON file, then check cross-level links."""
    directory = Path(directory)
    rooms, placed = {}, set()
    for path in sorted(directory.glob("*.json")):
        if path.stem.startswith("_"):
            continue
        try:
            data = read_json(path)
            require(isinstance(data, dict), "level must be a JSON object")
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
            require(isinstance(legend, dict), "legend must be a JSON object")
            for symbol, spec in legend.items():
                require(
                    len(symbol) == 1 and isinstance(spec, dict), "legend keys need one character"
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
                            spec[hook] in mechanics, f"{symbol!r}: unknown mechanic {spec[hook]!r}"
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
                        isinstance(spec.get("battle", True), bool), "battle must be true or false"
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
                    key = spec.get("id", f"{path.stem}:{symbol}:{x}:{y}")
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
            rooms[path.stem] = Room(
                path.stem,
                data["name"],
                tuple(tiles),
                tuple(people),
                tuple(exits),
                rest,
                spawns,
                tuple(objects),
            )
        except (StoryError, TypeError) as error:
            raise StoryError(f"{path.name}: {error}") from error
    require(rooms, f"{directory}: no level JSON files found")
    for key, room in rooms.items():
        for door in room.exits:
            require(
                door.destination in rooms, f"{key}.json: unknown door level {door.destination!r}"
            )
            require(
                door.landing in rooms[door.destination].spawns,
                f"{key}.json: {door.destination!r} has no spawn {door.landing!r}",
            )
    config = read_json(directory / "_world.json")
    require(
        isinstance(config, dict) and not (set(config) - {"start_level", "start_entry"}),
        "_world.json: use start_level and start_entry",
    )
    start, entry = config.get("start_level"), config.get("start_entry")
    require(isinstance(start, str) and start in rooms, "_world.json: unknown start_level")
    require(
        isinstance(entry, str) and entry in rooms[start].spawns, "_world.json: unknown start_entry"
    )
    return rooms, start, entry


def meets(session, requirement=None):
    """A flag, or a list of flags (all needed). Outcomes use spared:id / defeated:id."""
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
        paragraphs = [text] if isinstance(text, str) else text
        pages = []
        for paragraph in paragraphs:
            lines = textwrap.wrap(paragraph, width=48) or [""]
            pages.extend("\n".join(lines[i : i + 3]) for i in range(0, len(lines), 3))
        return pages

    @property
    def choosing(self):
        return self.page == len(self.pages) - 1 and bool(self.choices)

    def update(self, controls):
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
