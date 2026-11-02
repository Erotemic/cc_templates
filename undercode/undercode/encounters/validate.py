"""Check encounter definitions independently of maps. Simulations run only on request."""

import math
from .arena import Arena, Mode
from .model import TurnContext
from ..model import Player
from ..controls import Controls


def validate_encounters(*, characters, weapons, patterns):
    """Return readable errors; simulate new pattern/strike instances without a window."""
    errors = []
    keys = [character.key for character in characters]
    if len(set(keys)) != len(keys):
        errors.append("Opponent keys must be unique.")
    if not weapons:
        errors.append("Add at least one weapon.")
    factories = list(patterns.items())
    for character in characters:
        if character.max_hp <= 0 or character.calm_needed <= 0 or not character.acts:
            errors.append(f"{character.key}: need positive HP/understanding and at least one ACT.")
        if any(act.calm < 0 for act in character.acts):
            errors.append(f"{character.key}: ACT understanding gains must be nonnegative.")
        if not callable(character.portrait) or not callable(character.choose_pattern):
            errors.append(f"{character.key}: portrait and choose_pattern must be functions.")
        for turn in range(3):
            context = TurnContext(
                turn=turn,
                opponent_hp=max(1, character.max_hp // (turn + 1)),
                opponent_max_hp=character.max_hp,
                calm=min(turn, character.calm_needed),
            )

            # Bind this particular opponent/context now; the loop will run later.
            def make_pattern(character=character, context=context):
                """Create one fresh pattern for a representative turn."""
                return character.choose_pattern(context=context)

            factories.append((f"{character.key}, turn {turn}", make_pattern))
    if errors:
        return errors
    for key, factory in factories:
        try:
            pattern = factory()
            if (
                not math.isfinite(pattern.duration)
                or not 0 < pattern.duration <= 60
                or not isinstance(pattern.mode, Mode)
            ):
                raise ValueError("Use a Mode and a finite duration between 0 and 60 seconds.")
            arena = Arena(pattern=pattern, player=Player(hp=10000, max_hp=10000), seed=17)
            while not arena.done:
                arena.update(seconds=1 / 60, controls=Controls())
            for bullet in arena.bullets:
                if not all(
                    math.isfinite(value)
                    for value in (*bullet.position, *bullet.velocity, bullet.radius)
                ):
                    raise ValueError("Projectile values must be finite.")
        except Exception as error:
            errors.append(f"Pattern {key}: {type(error).__name__}: {error}")
    for weapon in weapons:
        try:
            strike = weapon.factory()
            for _ in range(600):
                strike.update(seconds=1 / 60, controls=Controls())
                if strike.done:
                    break
            if not strike.done or not 0 <= strike.score <= 1:
                raise ValueError("A strike must finish with a score between 0 and 1.")
        except Exception as error:
            errors.append(f"Weapon {weapon.name}: {type(error).__name__}: {error}")
    return errors
