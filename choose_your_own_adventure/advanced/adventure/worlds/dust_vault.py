"""Dust Vault: a different story built on exactly the same AdventureGame."""

from adventure.core import AdventureGame, Choice, Enemy, Room, World


ROOMS = {
    "airlock": Room(
        "airlock",
        "Outpost Airlock",
        "Dust rattles against the pressure doors of a tiny frontier outpost.",
        {"into the market": "market"},
    ),
    "market": Room(
        "market",
        "Scrap Market",
        "Mechanics and traders work beneath strings of salvaged lights.",
        {
            "back to the airlock": "airlock",
            "down into the service tunnels": "tunnels",
            "toward the sealed vault": "vault_door",
        },
    ),
    "tunnels": Room(
        "tunnels",
        "Service Tunnels",
        "Old power conduits vanish into the dark beneath the outpost.",
        {"up to the market": "market"},
    ),
    "vault_door": Room(
        "vault_door",
        "Dust Vault Door",
        "A steel door waits behind a dead keypad and an empty power socket.",
        {"back to the market": "market", "inside the vault": "vault"},
    ),
    "vault": Room(
        "vault",
        "Dust Vault",
        "Shelves of sealed memory cartridges surround a humming archive core.",
        {"back through the vault door": "vault_door"},
    ),
}

ENEMIES = {
    "scrap_drone": Enemy("scrap_drone", "scrap drone", hp=8, attack=2, reward_gold=3),
}


def describe_extra(game: AdventureGame) -> list[str]:
    location = game.player.location
    lines: list[str] = []

    if location == "market" and not game.player.has("vault code"):
        lines.append("A mechanic is repairing a radio beside a handwritten sign: VAULT CODES - 3 GOLD.")
    if location == "tunnels" and not game.player.has("power cell"):
        lines.append("A charged power cell glows behind a broken maintenance drone.")
    if location == "vault_door":
        if not game.player.has("vault code"):
            lines.append("The keypad still needs an access code.")
        if not game.player.has("power cell"):
            lines.append("The door's power socket is empty.")
    if location == "vault":
        lines.append("The archive core contains the lost survey maps you came to recover.")

    return lines


def get_choices(game: AdventureGame) -> list[Choice]:
    choices = game.exit_choices()
    location = game.player.location

    if location == "vault_door":
        ready = game.player.has("vault code") and game.player.has("power cell")
        if not ready:
            choices = [choice for choice in choices if choice.action != "go:vault"]

    if location == "airlock" and not game.has_flag("job_started"):
        choices.append(Choice("read_contract", "Read the recovery contract"))

    elif location == "market" and not game.player.has("vault code"):
        choices.append(Choice("buy_code", "Buy a vault code from the mechanic (3 gold)"))

    elif location == "tunnels":
        if not game.has_flag("drone_defeated"):
            choices.append(Choice("fight_drone", "Approach the sparking maintenance drone"))
        elif not game.player.has("power cell"):
            choices.append(Choice("take_cell", "Take the charged power cell"))

    elif location == "vault_door":
        choices.append(Choice("inspect_vault", "Inspect the vault door"))

    elif location == "vault":
        choices.append(Choice("recover_maps", "Recover the lost survey maps"))

    return choices


def handle_action(game: AdventureGame, action: str) -> list[str]:
    if action == "read_contract":
        game.set_flag("job_started")
        game.player.gold += 3
        return [
            "Contract: Recover the lost survey maps from the Dust Vault.",
            "The client left you 3 gold for supplies.",
        ]

    if action == "buy_code":
        if game.player.gold < 3:
            return ["Mechanic: 'Come back when you have 3 gold.'"]
        game.player.gold -= 3
        game.give_item("vault code")
        return ["The mechanic sells you a handwritten six-digit vault code."]

    if action == "fight_drone":
        game.start_combat("scrap_drone", return_location="market")
        return ["The damaged drone mistakes you for an intruder and attacks!"]

    if action == "take_cell":
        game.give_item("power cell")
        return ["You disconnect the charged power cell from the wrecked drone."]

    if action == "inspect_vault":
        missing = []
        if not game.player.has("vault code"):
            missing.append("a vault code")
        if not game.player.has("power cell"):
            missing.append("a power cell")
        if missing:
            return ["The vault still needs " + " and ".join(missing) + "."]
        return ["The keypad accepts your code and the power cell brings the lock online."]

    if action == "recover_maps":
        message = "You recovered the survey maps and completed the Dust Vault job."
        game.win(message)
        return [message]

    raise AssertionError(f"Unhandled Dust Vault action: {action}")


def on_enemy_defeated(game: AdventureGame, enemy: Enemy) -> list[str]:
    if enemy.key == "scrap_drone":
        game.set_flag("drone_defeated")
        return ["The drone powers down. The glowing power cell is now safe to remove."]
    return []


DUST_VAULT_WORLD = World(
    title="Dust Vault",
    start_location="airlock",
    rooms=ROOMS,
    enemies=ENEMIES,
    describe_extra=describe_extra,
    get_choices=get_choices,
    handle_action=handle_action,
    on_enemy_defeated=on_enemy_defeated,
)


def make_dust_vault_game(player_name: str = "Tav") -> AdventureGame:
    return AdventureGame(DUST_VAULT_WORLD, player_name=player_name)
