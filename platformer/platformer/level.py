"""Three starting levels, drawn with letters instead of an editor.

Each character is one 40-pixel square. Change a map, then rerun the game!

    #  solid ground or platform
    P  player start
    *  collectible star
    D  exit door (opens when all stars are collected)
    E  enemy (student can program its movement)
    ^  spring (student can program its bounce)
    B  optional boss (mission 6; level 3)
    M  movable platform (mission 10; level 2)
    S  switch (mission 11; level 2)
    .  air

MISSION 0: move one star, or change a platform in LEVEL_1.
All rows must be 24 characters wide and 15 characters tall.
Keep one P, D, E, and ^ in each level, and at least one star.
B, M, S are optional; add or remove them to experiment.
"""

# Level 1: familiar, forgiving introduction.
LEVEL_1 = (
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "............*...........",
    "...........####.........",
    ".................*......",
    ".......####....####.....",
    ".....*..................",
    "...####............####.",
    "..P.....^......E......D.",
    "########################",
)

# Level 2: a longer staircase with more horizontal distance to cover.
LEVEL_2 = (
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "..................*.....",
    ".................####...",
    "...........*............",
    ".........######.........",
    ".....*.......M..........",
    "....#####...............",
    "..P.....^..S....E.....D.",
    "########################",
)

# Level 3: zigzag upward, then return to the door.
LEVEL_3 = (
    "........................",
    "........................",
    "........................",
    "........................",
    "........................",
    "..............*.........",
    "............######......",
    "........*...............",
    ".......#####............",
    "........................",
    "............#####.......",
    "......*.................",
    ".....#####..............",
    "..P......^.......E.B..D.",
    "########################",
)

# MISSION 3 -- CREATE YOUR FOURTH LEVEL HERE:
# 1. Copy the tuple for LEVEL_3, rename it LEVEL_4, and edit the symbols.
# 2. Add LEVEL_4 to the LEVELS tuple below.
# 3. Add its name to LEVEL_NAMES in the matching position.
# The game draws the same rules and loads the new map automatically.
# Don't forget to check reachability by PLAYING your new level.
LEVELS = (LEVEL_1, LEVEL_2, LEVEL_3)
LEVEL_NAMES = ("Green Meadow", "Sunset Steps", "Cloud Castle")

# Compatibility with early lessons that refer to the single starter map.
TILES = LEVEL_1


def locations(symbol: str, tiles: tuple[str, ...] | None = None
              ) -> list[tuple[int, int]]:
    """Find (column, row) positions. Omitting tiles uses level 1."""
    if tiles is None:
        tiles = TILES
    return [(column, row)
            for row, line in enumerate(tiles)
            for column, tile in enumerate(line)
            if tile == symbol]


def check_map(tiles: tuple[str, ...] | None = None) -> None:
    """Give a readable error if a student accidentally breaks a map."""
    if tiles is None:
        tiles = TILES
    from . import settings
    if not tiles:
        raise ValueError("A level map must not be empty")
    width = len(tiles[0])
    if any(len(line) != width for line in tiles):
        raise ValueError("Every row in a level must have the same length")
    if (len(tiles), width) != (settings.HEIGHT // settings.TILE,
                               settings.WIDTH // settings.TILE):
        raise ValueError("A level must be 24 columns by 15 rows")
    valid = set(".#P*DE^BMS")
    for row, line in enumerate(tiles):
        for tile in line:
            if tile not in valid:
                raise ValueError(f"Unknown map symbol {tile!r} in row {row}")
    for symbol in ("P", "D", "E", "^"):
        if len(locations(symbol, tiles)) != 1:
            raise ValueError(f"Place exactly one {symbol!r} on each level")
    if not locations("*", tiles):
        raise ValueError("Place at least one '*' star on each level")


def check_all_maps() -> None:
    """Validate all levels (including ones students add)."""
    if len(LEVELS) != len(LEVEL_NAMES):
        raise ValueError("Each level must have one name")
    for index, tiles in enumerate(LEVELS, 1):
        try:
            check_map(tiles)
        except ValueError as error:
            raise ValueError(f"Level {index}: {error}") from error
