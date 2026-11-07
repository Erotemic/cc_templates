"""Hand-authored climbing rooms, with open-air drops and tall rock walls.

Every character is a 32-pixel tile. All rooms are 24 columns wide but can
have DIFFERENT HEIGHTS; the camera follows the climber up the mountain.

    .  air / abyss         #  grabbable solid rock
    =  jump-through ledge  P  player spawn         G  room exit
    ^  spikes              C  checkpoint           *  optional berry
    R  dash crystal        m  moving platform       b  crumble ledge
    w  wind zone

There is no implicit floor: dots below a ledge mean a bottomless pit. When
editing a level, keep at least 15 rows so it fits the initial view. The first
four levels can be cleared with only the supplied movement code; students
need not implement any optional mission to reach the exit.
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


# Four hand-built rooms, from short cliff crossing to tall vertical ascent.

WELCOME = Room(
    name='Trailhead',
    hint='Hold C + UP to climb walls.',
    next_room='switchbacks',
    tiles=(
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '...........*.......#....',
        '............#......#....',
        '............#......#.*..',
        '............#....R.#....',
        '........==..#....b.#..G.',
        '..P..^......#..C...#####',
        '######......######......',
        '........................',
    ),
)

SWITCHBACKS = Room(
    name='Switchbacks',
    hint='Wall-jump between cliffs; use ledges.',
    next_room='divide',
    tiles=(
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '....####.........*......',
        '....####................',
        '....####.............G..',
        '....####....############',
        '....####.*..####........',
        '....####..R.####........',
        '....####....####........',
        '....####.==.####........',
        '....####....####........',
        '....####....####........',
        '....####....####........',
        '....####....####........',
        '....####..C.####........',
        '....####.==.####........',
        '....####....####........',
        '....####....####........',
        '....####....####........',
        '....####....####........',
        '....####.P..####........',
        '........####............',
        '........................',
    ),
)

DIVIDE = Room(
    name='Skybridge',
    hint='Jump + dash across the abyss.',
    next_room='ridge',
    tiles=(
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '.......*.....C.....*....',
        '............###.........',
        '..........R.###.......G.',
        '............###...mm.###',
        '............###.........',
        '..P.....==..###.........',
        '######......###.........',
        '........................',
        '........................',
    ),
)

RIDGE = Room(
    name='Lantern Ridge',
    hint='C + UP climbs; flags save progress.',
    next_room=None,
    tiles=(
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '........................',
        '..................*.....',
        '...................##.G.',
        '...................#####',
        '...................##...',
        '...................##...',
        '...................##...',
        '.................==##...',
        '...............C...##...',
        '..............###..##...',
        '..............###..##...',
        '...........*..###..##...',
        '.............w###..##...',
        '............Rw###..##...',
        '.............w###.......',
        '........C..bb.###.......',
        '.......###....###.......',
        '.......###....###.......',
        '....*..###....###.......',
        '.......###....###.......',
        '.......###....###.......',
        '.......###....###.......',
        '..P..^.###^...###.......',
        '######.###..............',
        '........................',
        '........................',
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
        if len(room.tiles) < settings.ROWS:
            raise MapError(f"Room {key!r}: expected at least {settings.ROWS} rows, found {len(room.tiles)}")
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
