"""Content diagnostics, called explicitly by main.py --check and the tests."""

import math
from .arena import Arena, Mode
from .controls import Controls
from .model import TurnContext


def validate_content(characters, weapons, patterns, rooms):
    """Return a list of content problems, or [] when the supplied registries pass.

    Check character/weapon/room data first. If valid, construct and simulate
    registered defense patterns, several character-selected patterns, and player
    strikes with no input. Catch factory/simulation errors as readable messages.
    Called explicitly by --check; this runs student code but opens no window.
    """
    errors = []
    names = [c.key for c in characters]
    if len(names) != len(set(names)):
        errors.append("Character keys must be unique.")
    if not weapons:
        errors.append("Add at least one weapon.")
    for character in characters:
        if character.max_hp <= 0 or character.calm_needed <= 0 or not character.acts:
            errors.append(f"{character.key}: positive HP/calm and at least one ACT are required.")
        if any(act.calm < 0 for act in character.acts):
            errors.append(f"{character.key}: ACT calm gains must be nonnegative.")
        if not callable(character.portrait) or not callable(character.choose_pattern):
            errors.append(f"{character.key}: portrait and choose_pattern must be functions.")
    placed = set()
    for key, room in rooms.items():
        if (
            not (3 <= len(room.tiles) <= 16)
            or not room.tiles
            or not (3 <= len(room.tiles[0]) <= 30)
            or any(len(row) != len(room.tiles[0]) for row in room.tiles)
        ):
            errors.append(f"{key}: use a rectangular map, 3..30 columns and 3..16 rows.")
            continue

        def walkable(tile):
            """Return whether tile, a (column, row) pair, is inside this room on walkable ground."""
            x, y = tile
            return (
                0 <= y < len(room.tiles)
                and 0 <= x < len(room.tiles[0])
                and room.tiles[y][x] not in "#~"
            )

        if any(ch not in "#~.gdD" for row in room.tiles for ch in row):
            errors.append(f"{key}: unknown map tile.")
        for person in room.people:
            if person.key in placed:
                errors.append(f"{key}: duplicate placement key {person.key}.")
            placed.add(person.key)
            if person.character not in names or not walkable(person.tile):
                errors.append(f"{key}: {person.key} needs a known character and walkable position.")
        if room.rest_tile and not walkable(room.rest_tile):
            errors.append(f"{key}: fountain must be on walkable ground.")
        for exit in room.exits:
            if exit.destination not in rooms or not walkable(exit.tile):
                errors.append(f"{key}: invalid exit {exit}.")
            else:
                target_room = rooms[exit.destination]
                if exit.landing not in target_room.spawns:
                    errors.append(f"{key}: missing named landing {exit.landing!r}.")
                    continue
                x, y = target_room.spawns[exit.landing]
                target = target_room.tiles
                if not (0 <= y < len(target) and 0 <= x < len(target[y])) or target[y][x] in "#~":
                    errors.append(f"{key}: exit landing must be walkable.")
    if errors:
        return errors
    factories = list(patterns.items())
    for character in characters:
        for turn in range(3):
            hp = (character.max_hp, max(1, character.max_hp // 2), 1)[turn]
            context = TurnContext(turn, hp, character.max_hp, min(turn, character.calm_needed))
            factories.append(
                (
                    f"{character.key}, turn {turn}",
                    lambda c=character, x=context: c.choose_pattern(x),
                )
            )
    for key, factory in factories:
        try:
            pattern = factory()
            if (
                not math.isfinite(pattern.duration)
                or not 0 < pattern.duration <= 60
                or not isinstance(pattern.mode, Mode)
            ):
                raise ValueError("Use a Mode and a finite duration between 0 and 60 seconds.")
            arena = Arena(pattern, hp=10000, seed=17)
            while not arena.done:
                arena.update(1 / 60, Controls())
            for bullet in arena.bullets:
                if not all(
                    math.isfinite(v) for v in (*bullet.position, *bullet.velocity, bullet.radius)
                ):
                    raise ValueError("Projectile values must be finite.")
        except Exception as error:
            errors.append(f"Pattern {key}: {type(error).__name__}: {error}")
    for weapon in weapons:
        try:
            strike = weapon.factory()
            for _ in range(600):
                strike.update(1 / 60, Controls())
                if strike.done:
                    break
            if not strike.done or not 0 <= strike.score <= 1:
                raise ValueError("A strike must finish and return a score from 0 to 1.")
        except Exception as error:
            errors.append(f"Weapon {weapon.name}: {type(error).__name__}: {error}")
    return errors
