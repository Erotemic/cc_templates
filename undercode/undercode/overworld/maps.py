"""Turn letters into positions. Read compile_rooms from top to bottom.

Authors use Room and object records, so Python itself catches misspelled keyword
arguments. We check game-specific mistakes here: map shape, unknown letters,
blocked spawns, duplicate IDs, and doors pointing to missing rooms/markers.
There is no encounter import: a story-only map can run on its own.
"""

from ..dialogue import Dialogue
from .model import Room, RoomMap, Spawn, Tile, Person, Door, Sign, Item, Rest, Trigger, PlacedObject

TERRAIN = "#~.gd "


class MapError(ValueError):
    """Explain a map problem using its room key and, where possible, row/column."""


def require(*, condition, message):
    """Raise a readable error before play rather than failing during a conversation."""
    if not condition:
        raise MapError(message)


def validate_dialogue(*, dialogue, location):
    """Check the writing students can edit, including choice labels that must fit."""
    require(condition=isinstance(dialogue, Dialogue), message=f"{location}: use Dialogue(...)")
    for definition in [dialogue, *dialogue.branches]:
        paragraphs = [definition.text] if isinstance(definition.text, str) else definition.text
        require(
            condition=isinstance(paragraphs, list)
            and bool(paragraphs)
            and all(isinstance(text, str) and text.strip() for text in paragraphs),
            message=f"{location}: text needs nonempty paragraphs",
        )
        for choice in definition.choices:
            require(
                condition=0 < len(choice.label) <= 60,
                message=f"{location}: choice labels need 1 to 60 characters",
            )


def compile_rooms(*, definitions):
    """Return RoomMaps from a dictionary of Room records; never call student mechanics."""
    require(
        condition=isinstance(definitions, dict) and bool(definitions),
        message="Add at least one room to LEVELS.",
    )
    rooms = {}
    person_ids = set()
    for key, definition in definitions.items():
        location = f"Room {key!r}"
        require(condition=isinstance(definition, Room), message=f"{location}: use Room(...)")
        require(
            condition=isinstance(definition.legend, dict),
            message=f"{location}: legend must map letters to records",
        )
        rows = definition.tiles
        require(
            condition=isinstance(rows, list) and 3 <= len(rows) <= 16,
            message=f"{location}: use 3 to 16 rows",
        )
        require(
            condition=all(isinstance(row, str) for row in rows),
            message=f"{location}: each row must be a string",
        )
        width = len(rows[0])
        require(
            condition=3 <= width <= 30 and all(len(row) == width for row in rows),
            message=f"{location}: use equal-length rows, 3 to 30 columns",
        )
        objects, spawns, terrain = [], {}, []
        for row_number, row in enumerate(rows):
            ground_row = ""
            for column, letter in enumerate(row):
                position = (column, row_number)
                here = f"{location}, row {row_number + 1}, column {column + 1}"
                if letter not in definition.legend:
                    require(
                        condition=letter in TERRAIN, message=f"{here}: add {letter!r} to the legend"
                    )
                    ground_row += "g" if letter == " " else letter
                    continue
                record = definition.legend[letter]
                require(
                    condition=isinstance(
                        record, (Spawn, Tile, Person, Door, Sign, Item, Rest, Trigger)
                    ),
                    message=f"{here}: use a room object record",
                )
                require(
                    condition=isinstance(record.ground, str)
                    and record.ground in TERRAIN
                    and len(record.ground) == 1,
                    message=f"{here}: unknown ground tile",
                )
                if not isinstance(record, Tile):
                    require(
                        condition=record.ground not in "#~",
                        message=f"{here}: objects need walkable ground",
                    )
                ground_row += "D" if isinstance(record, Door) else record.ground.replace(" ", "g")
                if isinstance(record, Spawn):
                    require(
                        condition=isinstance(record.name, str) and bool(record.name),
                        message=f"{here}: name the spawn marker",
                    )
                    require(
                        condition=record.name not in spawns,
                        message=f"{here}: duplicate spawn {record.name!r}",
                    )
                    spawns[record.name] = position
                elif not isinstance(record, Tile):
                    object_id = f"{key}:{letter}:{column}:{row_number}"
                    if isinstance(record, Person):
                        object_id = record.id or object_id
                        require(
                            condition=object_id not in person_ids,
                            message=f"{here}: duplicate person ID {object_id!r}",
                        )
                        person_ids.add(object_id)
                        require(
                            condition=callable(record.portrait),
                            message=f"{here}: portrait must be a function",
                        )
                    if isinstance(record, (Person, Sign)) and record.dialogue is not None:
                        validate_dialogue(dialogue=record.dialogue, location=here)
                    if isinstance(record, Trigger):
                        require(
                            condition=callable(record.on_enter),
                            message=f"{here}: on_enter must be a function",
                        )
                    elif not isinstance(record, Door):
                        require(
                            condition=record.on_interact is None or callable(record.on_interact),
                            message=f"{here}: on_interact must be a function",
                        )
                    require(
                        condition=record.when is None or callable(record.when),
                        message=f"{here}: when must be a function",
                    )
                    objects.append(PlacedObject(key=object_id, tile=position, definition=record))
            terrain.append(ground_row)
        require(condition=bool(spawns), message=f"{location}: add a Spawn marker")
        rooms[key] = RoomMap(
            key=key, name=definition.name, tiles=tuple(terrain), objects=objects, spawns=spawns
        )
    for key, room in rooms.items():
        for obj in room.exits:
            door = obj.definition
            require(
                condition=door.destination_room in rooms,
                message=f"Room {key!r}: unknown door destination {door.destination_room!r}",
            )
            require(
                condition=door.destination_spawn in rooms[door.destination_room].spawns,
                message=f"Room {key!r}: missing spawn {door.destination_spawn!r} in {door.destination_room!r}",
            )
    return rooms


def validate_start(*, rooms, room_key, spawn_name):
    """Check an explicit start so arrival behavior does not depend on dictionary order."""
    require(condition=room_key in rooms, message=f"Unknown starting room {room_key!r}")
    require(
        condition=spawn_name in rooms[room_key].spawns,
        message=f"Room {room_key!r}: unknown starting marker {spawn_name!r}",
    )
