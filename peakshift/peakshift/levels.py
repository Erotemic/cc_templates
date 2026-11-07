"""Authored, readable levels: edit the letters, not a procedural generator.

Each character is a 32-pixel tile. Rooms have 24 columns and 15 rows.

    .  empty space           #  solid rock
    =  jump-through ledge    P  player spawn          G  exit to next room
    ^  spikes (danger)       C  checkpoint (respawn here)
    *  optional berry        R  dash-refill crystal (student mission)
    m  moving platform (student makes it move; solid from above already)
    b  crumble ledge (student makes it crumble; solid from above)
    w  wind (student makes it push; decorative until implemented)

Adjacent 'm' cells on one row form one horizontal moving platform.
The exit needs no key or berries: students can finish every room immediately.
For a new room, copy a Room below, choose a unique key, and connect an exit.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import settings


@dataclass(frozen=True)
class Room:
    name: str
    tiles: tuple[str, ...]
    hint: str
    next_room: str | None


# Each ledge and obstacle is placed intentionally. No random generation.
# Room 1: easy jumps with optional pickup and a dormant crumble shortcut.
WELCOME = Room(
    name="Trailhead",
    hint="A / D: move   SPACE: jump   X or SHIFT: dash",
    next_room="switchbacks",
    tiles=(
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "............*...........",
        "..........====..........",
        ".....*..........b.......",
        "..P......^^...........G.",
        "########################",
    ),
)

# Room 2: staggered ledges; wall slides and wall jumps are already playable.
SWITCHBACKS = Room(
    name="Switchbacks",
    hint="Push into a wall to slide. Jump again to kick away.",
    next_room="divide",
    tiles=(
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "....................*.G.",
        ".................======.",
        "..............R.........",
        "#..........======.......",
        "#....*..................",
        "#....======.............",
        "#.P.........^^..........",
        "########################",
    ),
)

# Room 3: a real void makes the midair dash useful (not just a speed boost).
DIVIDE = Room(
    name="Skybridge",
    hint="Jump toward the gap, then dash through the air. C saves progress.",
    next_room="ridge",
    tiles=(
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        "..................*.....",
        "................mmmm....",
        "........................",
        ".....R..........C.......",
        "..P..................G..",
        "#########......#########",
    ),
)

# Room 4: short ascent + optional wind, berries, and breakable tiles.
RIDGE = Room(
    name="Lantern Ridge",
    hint="Dash comes back on landing. Checkpoints survive your falls.",
    next_room=None,
    tiles=(
        "........................",
        "........................",
        "........................",
        "........................",
        "........................",
        ".....................*.G",
        "..................=====.",
        ".................w......",
        ".............======.....",
        ".........C..............",
        "......bbbbbb............",
        "....*...................",
        "....====................",
        "..P..........^^.........",
        "########################",
    ),
)

# Explicit graph: a room may lead wherever you choose (like UnderCode doors).
ROOMS: dict[str, Room] = {
    "trailhead": WELCOME,
    "switchbacks": SWITCHBACKS,
    "divide": DIVIDE,
    "ridge": RIDGE,
}
START_ROOM = "trailhead"


class MapError(ValueError):
    """A student-friendly message pointing to the broken map."""


def find(tiles: tuple[str, ...], symbol: str) -> list[tuple[int, int]]:
    """Return (column, row) for each matching symbol."""
    return [(column, row) for row, line in enumerate(tiles)
            for column, letter in enumerate(line) if letter == symbol]


def validate_rooms(rooms: dict[str, Room] | None = None,
                   start_room: str | None = None) -> None:
    """Explain typos before the main loop starts, with room/row/column."""
    if rooms is None:
        rooms = ROOMS
    if start_room is None:
        start_room = START_ROOM
    if not rooms or start_room not in rooms:
        raise MapError(f"Starting room {start_room!r} does not exist")
    for key, room in rooms.items():
        if len(room.tiles) != settings.ROWS:
            raise MapError(f"Room {key!r}: expected {settings.ROWS} rows, found {len(room.tiles)}")
        for row_index, line in enumerate(room.tiles):
            if len(line) != settings.COLS:
                raise MapError(f"Room {key!r}, row {row_index + 1}: expected "
                               f"{settings.COLS} columns, found {len(line)}")
            for col_index, symbol in enumerate(line):
                if symbol not in ".#=PG^C*Rmbw":
                    raise MapError(f"Room {key!r}, row {row_index + 1}, "
                                   f"column {col_index + 1}: unknown {symbol!r}")
        for marker in ("P", "G"):
            count = len(find(room.tiles, marker))
            if count != 1:
                raise MapError(f"Room {key!r}: place exactly one {marker} (found {count})")
        if room.next_room is not None and room.next_room not in rooms:
            raise MapError(f"Room {key!r}: next_room {room.next_room!r} does not exist")
        if not room.name.strip():
            raise MapError(f"Room {key!r}: add a name")


def tile_runs(tiles: tuple[str, ...], marker: str):
    """Group neighboring tiles into (x, y, width) rectangles."""
    for row_index, line in enumerate(tiles):
        col = 0
        while col < len(line):
            if line[col] != marker:
                col += 1
                continue
            start = col
            while col < len(line) and line[col] == marker:
                col += 1
            yield start * settings.TILE, row_index * settings.TILE, (col - start) * settings.TILE


def moving_platform_runs(tiles: tuple[str, ...]):
    """Find each moving bridge made of adjacent m tiles."""
    return tile_runs(tiles, "m")


def one_way_runs(tiles: tuple[str, ...]):
    """Find each static jump-through ledge made of adjacent = tiles."""
    return tile_runs(tiles, "=")
