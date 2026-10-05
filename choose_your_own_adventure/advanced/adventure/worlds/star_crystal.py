"""Star Crystal world: story-specific rules written as ordinary Python.

This file is intentionally where the interesting world logic lives. Students
can add rooms, choices, items, and quest conditions here without editing the
reusable engine in ``adventure/core.py``.
"""

from adventure.core import AdventureGame, Choice, Enemy, Room, World


ROOMS = {
    "village": Room(
        "village",
        "Willow Village",
        "Lanterns glow around a quiet village square.",
        {"north to the crossroads": "crossroads"},
    ),
    "crossroads": Room(
        "crossroads",
        "Crossroads",
        "Three old paths meet beneath a weathered stone marker.",
        {
            "south to the village": "village",
            "west to the forest": "forest",
            "east to the lake": "lake",
            "north to the ruins": "ruins",
        },
    ),
    "forest": Room(
        "forest",
        "Moonwood Forest",
        "Silver leaves whisper around a moss-covered shrine.",
        {"east to the crossroads": "crossroads"},
    ),
    "lake": Room(
        "lake",
        "Mirror Lake",
        "A patient fisherman sits beside a perfectly still lake.",
        {"west to the crossroads": "crossroads"},
    ),
    "ruins": Room(
        "ruins",
        "Old Ruins",
        "Broken pillars surround a tower gate. Something skitters in the dust.",
        {
            "south to the crossroads": "crossroads",
            "through the tower gate": "tower",
        },
    ),
    "tower": Room(
        "tower",
        "Star Tower",
        "At the top of the tower, blue starlight pools around a crystal pedestal.",
        {"back to the ruins": "ruins"},
    ),
}

ENEMIES = {
    "ruin_spider": Enemy("ruin_spider", "ruin spider", hp=10, attack=2),
}


def describe_extra(game: AdventureGame) -> list[str]:
    lines: list[str] = []
    location = game.player.location

    if location == "village" and not game.has_flag("quest_started"):
        lines.append("The village elder watches the northern road with concern.")
    if location == "forest" and not game.player.has("moon herb"):
        lines.append("A pale green plant grows beside the shrine.")
    if location == "lake" and not game.player.has("tower key"):
        lines.append("The fisherman turns a tiny brass key between his fingers.")
    if location == "ruins" and not game.has_flag("spider_defeated"):
        lines.append("A ruin spider guards the tower approach.")
    if location == "tower":
        lines.append("The Star Crystal is close enough to touch.")

    return lines


def get_choices(game: AdventureGame) -> list[Choice]:
    choices = game.exit_choices()
    location = game.player.location

    # Hide the tower exit until both obstacles are resolved. We do this with
    # plain list filtering instead of inventing a special LockedExit class.
    if location == "ruins":
        gate_open = game.player.has("tower key") and game.has_flag("spider_defeated")
        if not gate_open:
            choices = [choice for choice in choices if choice.action != "go:tower"]

    if location == "village":
        choices.append(Choice("talk_elder", "Talk to the village elder"))
        if game.player.hp < game.player.max_hp:
            choices.append(Choice("rest", "Rest at the inn"))

    elif location == "forest" and not game.player.has("moon herb"):
        choices.append(Choice("take_herb", "Pick the moon herb"))

    elif location == "lake" and not game.player.has("tower key"):
        choices.append(Choice("talk_fisher", "Talk to the fisherman"))

    elif location == "ruins":
        if not game.has_flag("spider_defeated"):
            choices.append(Choice("fight_spider", "Face the ruin spider"))
        if not game.player.has("tower key"):
            choices.append(Choice("inspect_gate", "Inspect the locked tower gate"))

    elif location == "tower":
        choices.append(Choice("take_crystal", "Take the Star Crystal"))

    return choices


def handle_action(game: AdventureGame, action: str) -> list[str]:
    if action == "talk_elder":
        game.set_flag("quest_started")
        return [
            "Elder: 'The Star Crystal once protected our valley.'",
            "Elder: 'The old tower is sealed. Ask around; someone may still have its key.'",
        ]

    if action == "rest":
        game.heal()
        return ["A warm meal and a quiet bed restore your health."]

    if action == "take_herb":
        game.give_item("moon herb")
        return ["You carefully pick the moon herb."]

    if action == "talk_fisher":
        if game.take_item("moon herb"):
            game.give_item("tower key")
            return [
                "Fisherman: 'That herb is exactly what I needed for my tea.'",
                "He trades you an old tower key.",
            ]
        return [
            "Fisherman: 'I can part with this old key for a moon herb from the western forest.'"
        ]

    if action == "fight_spider":
        game.start_combat("ruin_spider", return_location="crossroads")
        return ["The ruin spider lowers its fangs and rushes toward you!"]

    if action == "inspect_gate":
        return ["The tower gate is locked. Its small keyhole is still intact."]

    if action == "take_crystal":
        message = "You recovered the Star Crystal. The valley is safe!"
        game.win(message)
        return [
            "The Star Crystal lifts from its pedestal and fills the tower with blue light.",
            message,
        ]

    raise AssertionError(f"Unhandled Star Crystal action: {action}")


def on_enemy_defeated(game: AdventureGame, enemy: Enemy) -> list[str]:
    if enemy.key == "ruin_spider":
        game.set_flag("spider_defeated")
        return ["The path to the tower gate is clear."]
    return []


STAR_CRYSTAL_WORLD = World(
    title="Star Crystal Adventure",
    start_location="village",
    rooms=ROOMS,
    enemies=ENEMIES,
    describe_extra=describe_extra,
    get_choices=get_choices,
    handle_action=handle_action,
    on_enemy_defeated=on_enemy_defeated,
)


def make_star_crystal_game(player_name: str = "Tav") -> AdventureGame:
    return AdventureGame(STAR_CRYSTAL_WORLD, player_name=player_name)
