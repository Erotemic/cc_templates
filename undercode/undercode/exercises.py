"""Progress checks run STUDENT code, never teacher solutions.

Engine regression tests answer 'does the supplied engine work?'. These checks
answer 'does my implementation add the requested behavior?'. The unfinished
starter intentionally fails some checks. Alternative correct implementations
are welcome: check visible behavior rather than requiring particular source text.
"""

from .controls import Controls
from .model import Player, Session
from .sprites import VIEW_CASES


def check_facing():
    """Report each concrete direction example rather than only an overall grade."""
    from .student_overworld import choose_player_view

    results = []
    for facing, expected in VIEW_CASES:
        actual = choose_player_view(facing=facing)
        results.append((actual == expected, f"facing {facing}: {actual!r}, expected {expected!r}"))
    return results


def check_sprint():
    """Check the return values used by normal world movement, including releasing Shift."""
    from .student_overworld import movement_speed

    normal = movement_speed(controls=Controls())
    sprint = movement_speed(controls=Controls(sprint_held=True))
    return [
        (normal == 155, "normal walking returns 155 pixels/second"),
        (sprint == 230, "Shift returns 230 pixels/second"),
        (movement_speed(controls=Controls()) == normal, "releasing Shift restores walking"),
    ]


def check_healing():
    """Call the actual healing function at low, near-full and full HP."""
    from .overworld.world import World
    from .overworld.maps import compile_rooms
    from .overworld.model import Room, Spawn, Trigger
    from .student_overworld import warm_light

    rooms = compile_rooms(
        definitions={
            "lab": Room(
                name="Healing lab",
                tiles=["#####", "#@s.#", "#####"],
                legend={
                    "@": Spawn(name="start"),
                    "s": Trigger(name="Warm light", on_enter=warm_light),
                },
            )
        }
    )
    results = []
    for hp, expected, gain in ((5, 8, 3), (19, 20, 1), (20, 20, 0)):
        session = Session(player=Player(hp=hp))
        world = World(rooms=rooms, session=session, room_key="lab", spawn="start")
        obj = world.room.objects[0]
        warm_light(world=world, obj=obj)
        results.append(
            (
                session.player.hp == expected and str(gain) in world.toast,
                f"at {hp}/20 HP: heal to {expected} and report {gain} gained",
            )
        )
    return results


def check_pulse():
    """Observe warned sparks, motion, repetition and eventual completion in the real arena."""
    from .student_encounters import LanternPulse
    from .encounters.arena import Arena

    arena = Arena(pattern=LanternPulse(), player=Player(hp=10000, max_hp=10000))
    warned = moved = False
    seen = set()
    for _ in range(600):
        arena.update(seconds=1 / 60, controls=Controls())
        for bullet in arena.bullets:
            seen.add(id(bullet))
            warned = warned or bullet.warmup > 0
            moved = moved or bullet.position.x > 10
        if arena.done:
            break
    return [
        (warned, "a spark warns before becoming dangerous"),
        (moved, "a spark travels right"),
        (len(seen) > 1, "more than one spark appears"),
        (arena.done and not arena.bullets, "defense finishes with time for sparks to leave"),
    ]


def check_tactics():
    """Check the actual selector, including fresh timer instances on repeat calls."""
    from .student_encounters import choose_echo_pattern, LanternPulse, RippleLanes
    from .encounters.model import TurnContext

    first = choose_echo_pattern(
        context=TurnContext(turn=0, opponent_hp=20, opponent_max_hp=20, calm=0)
    )
    later = choose_echo_pattern(
        context=TurnContext(turn=1, opponent_hp=20, opponent_max_hp=20, calm=0)
    )
    repeat = choose_echo_pattern(
        context=TurnContext(turn=1, opponent_hp=20, opponent_max_hp=20, calm=0)
    )
    return [
        (isinstance(first, RippleLanes), "opening defense is Ripples"),
        (isinstance(later, LanternPulse), "later defense is Lantern Pulse"),
        (later is not repeat, "each selection creates a fresh pattern"),
    ]


def check_mouse():
    """Use the student's hit test on real layout records, including a scrolled menu."""
    from .student_encounters import clicked_button
    from .encounters.menu import main_buttons, option_buttons

    buttons = main_buttons()
    cases = [(None, None, "no click returns None"), ((0, 0), None, "outside buttons returns None")]
    for button in buttons:
        cases.append(
            (button.rect.center, button.index, f"click {button.label}: return index {button.index}")
        )
    first = buttons[0].rect
    cases += [
        (first.topleft, 0, "left/top edges belong to the first button"),
        ((first.right, first.centery), None, "the right edge is outside"),
        ((first.centerx, first.bottom), None, "the bottom edge is outside"),
        ((first.right + 2, first.centery), None, "the gap between buttons is outside"),
    ]
    results = []
    for position, expected, message in cases:
        actual = clicked_button(mouse_position=position, buttons=buttons)
        results.append((actual == expected, message))
    results.append(
        (
            clicked_button(mouse_position=(200, 400), buttons=[]) is None,
            "an empty button list returns None",
        )
    )
    rows = option_buttons(labels=[f"Choice {index}" for index in range(10)], selection=9)
    actual = clicked_button(mouse_position=rows[-1].rect.center, buttons=rows)
    results.append((actual == 9, "a scrolled row returns original option index 9"))
    return results


def check_piano():
    """Test the student's entire collision/note rule, without opening an audio device."""
    from .app import Game
    from .overworld.world import tile_center
    from .student_overworld import update_piano

    world = Game().world
    results = []
    # Being in the room is not enough: collision must actually select a key.
    update_piano(world=world)
    results.append((not world.tones, "away from every key: silence"))
    frequencies = (261.63, 293.66, 329.63, 349.23, 392.0, 440.0, 493.88, 523.25)
    for key, expected in zip(world.piano_keys, frequencies):
        world.tones.clear()
        world.position = tile_center(tile=key.tile)
        update_piano(world=world)
        results.append(
            (
                len(world.tones) == 1 and abs(world.tones[0].hz - expected) < 0.1,
                f"overlap {key.definition.note}: one {expected} Hz tone",
            )
        )
        world.tones.clear()
        update_piano(world=world)
        results.append((not world.tones, f"standing on {key.definition.note}: no repeated tone"))
    world.position = tile_center(tile=world.room.spawns["camp"])
    world.tones.clear()
    update_piano(world=world)
    results.append(
        (world.piano_key is None and not world.tones, "leaving clears the remembered key")
    )
    key = world.piano_keys[-1]
    world.position = tile_center(tile=key.tile)
    update_piano(world=world)
    results.append(
        (
            len(world.tones) == 1 and abs(world.tones[0].hz - 523.25) < 0.1,
            "returning to the same key plays it again",
        )
    )
    world.position = tile_center(tile=world.room.spawns["camp"])
    world.tones.clear()
    update_piano(world=world)
    first = world.piano_keys[0]
    bounds = world.tile_rect(tile=first.tile)
    world.position.x = bounds.left - 9
    world.position.y = bounds.centery
    update_piano(world=world)
    results.append((not world.tones, "body touching a key edge without overlap stays silent"))
    world.position.x += 1
    update_piano(world=world)
    results.append(
        (
            len(world.tones) == 1 and abs(world.tones[0].hz - 261.63) < 0.1,
            "body overlap plays C4 even before its center reaches the key",
        )
    )
    return results


def check_exercises(*, exercise):
    """Print actionable results and return 0 only when the chosen student's checks pass."""
    checks = {
        "facing": check_facing,
        "sprint": check_sprint,
        "healing": check_healing,
        "pulse": check_pulse,
        "tactics": check_tactics,
        "mouse": check_mouse,
        "piano": check_piano,
    }
    selected = checks if exercise == "all" else {exercise: checks[exercise]}
    failed = False
    for name, check in selected.items():
        try:
            results = check()
        except Exception as error:
            results = [(False, f"{type(error).__name__}: {error}")]
        print(f"Exercise {name}:")
        for ok, message in results:
            print(f"  {'OK' if ok else 'TRY AGAIN'}: {message}")
            failed = failed or not ok
        print(f"  {sum(ok for ok, _ in results)}/{len(results)} checks passed")
    return int(failed)
