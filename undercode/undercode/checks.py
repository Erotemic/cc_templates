"""Opt-in content checks. Independent modes never validate the other system."""


def check_or_list(*, listed=False, world_only=False, encounters_only=False):
    """Check selected definitions and their connection, or print the available IDs."""
    rooms = None
    characters = None
    errors = []
    if not encounters_only:
        from .student_world import LEVELS, START_LEVEL, START_ENTRY
        from .overworld.maps import compile_rooms, validate_start

        rooms = compile_rooms(definitions=LEVELS)
        validate_start(rooms=rooms, room_key=START_LEVEL, spawn_name=START_ENTRY)
        if listed:
            for key, room in rooms.items():
                print(f"Level {key}: {room.name}; entries: {', '.join(room.spawns)}")
    if not world_only:
        from .encounters.content import OPPONENTS, WEAPONS, PATTERNS

        characters = {character.key for character in OPPONENTS}
        if listed:
            print("Characters:", ", ".join(sorted(characters)))
            print("Patterns:", ", ".join(PATTERNS))
        else:
            from .encounters.validate import validate_encounters

            errors.extend(
                validate_encounters(characters=OPPONENTS, weapons=WEAPONS, patterns=PATTERNS)
            )
    if rooms is not None and characters is not None:
        for room in rooms.values():
            for person in room.people:
                encounter_id = person.definition.encounter_id
                if encounter_id is not None and encounter_id not in characters:
                    errors.append(f"Room {room.key!r}: unknown encounter {encounter_id!r}")
    for error in errors:
        print("ERROR:", error)
    if not listed and not errors:
        room_count = f"{len(rooms)} rooms; " if rooms is not None else ""
        print(
            f"UnderCode content OK: {room_count}selected engines/content passed. Exercise TODOs are separate."
        )
    return int(bool(errors))
