"""Validation helpers for capstone world data and runtime state.

These functions are intentionally ordinary Python.  They give students a
concrete example of a production habit: validate data at system boundaries and
express state-machine assumptions as executable invariants.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .game import AdventureGame


VALID_MODES = {
    "exploration",
    "confirm_move",
    "npc",
    "riddle",
    "inventory",
    "combat",
    "surrender_decision",
    "loot",
}

SUPPORTED_EFFECTS = {
    "PrintEffect",
    "SetFlagEffect",
    "ClearFlagEffect",
    "SetBountyEffect",
    "ChangeBountyEffect",
    "HealPlayerEffect",
    "GivePlayerItemEffect",
    "ChangeGoldEffect",
    "RemoveItemEffect",
    "DamageCharacterEffect",
    "MovePlayerEffect",
    "BlockPathEffect",
    "UnblockPathEffect",
    "ConditionalEffect",
    "ChanceEffect",
    "CompositeEffect",
    "EndGameEffect",
    "BranchOnBountyEffect",
}

SUPPORTED_ENCOUNTER_HANDLERS = {
    "handle_guard_confrontation",
    "handle_forest_spider_encounter",
    "handle_station_patrol",
    "handle_glass_maw",
    "handle_rafe_offer",
}

EFFECT_REQUIRED_FIELDS = {
    "PrintEffect": ("lines",),
    "SetFlagEffect": ("flags",),
    "ClearFlagEffect": ("flags",),
    "SetBountyEffect": ("amount",),
    "ChangeBountyEffect": ("amount",),
    "HealPlayerEffect": ("amount", "heal_text", "full_text"),
    "GivePlayerItemEffect": ("item_ids",),
    "ChangeGoldEffect": ("amount",),
    "RemoveItemEffect": ("item_id",),
    "DamageCharacterEffect": ("target", "amount"),
    "MovePlayerEffect": ("destination",),
    "BlockPathEffect": ("location_key", "direction", "reason"),
    "UnblockPathEffect": ("location_key", "direction"),
    "ConditionalEffect": (
        "required_flags",
        "blocked_flags",
        "required_items",
        "success_effect",
    ),
    "ChanceEffect": ("chance", "success_effect"),
    "CompositeEffect": ("effects",),
    "EndGameEffect": ("lines", "flags"),
    "BranchOnBountyEffect": ("threshold", "clean_effect", "hot_effect"),
}


def validate_world(world: dict[str, Any]) -> list[str]:
    """Return human-readable problems in a world-data dictionary."""
    errors: list[str] = []
    rooms = world.get("rooms")
    items = world.get("items")
    player = world.get("player")
    if not isinstance(rooms, dict) or not rooms:
        return ["world.rooms must be a non-empty dictionary"]
    if not isinstance(items, dict):
        errors.append("world.items must be a dictionary")
        items = {}
    if not isinstance(player, dict):
        errors.append("world.player must be a dictionary")
        player = {}

    for field in ("max_hp", "attack_min", "attack_max", "defense", "gold"):
        if field not in player:
            errors.append(f"player is missing required field {field!r}")

    start = world.get("start_location")
    if start not in rooms:
        errors.append(f"start_location {start!r} is not a room")

    item_ids = set(items)
    npc_names: set[str] = set()

    for item_id, item in items.items():
        if not isinstance(item, dict):
            errors.append(f"items.{item_id}: item must be a dictionary")
        elif not item.get("name"):
            errors.append(f"items.{item_id}: item is missing a name")

    def item_ref(item_id: Any, path: str) -> None:
        if item_id not in item_ids:
            errors.append(f"{path}: unknown item {item_id!r}")

    def room_ref(room_key: Any, path: str) -> None:
        if room_key not in rooms:
            errors.append(f"{path}: unknown room {room_key!r}")

    # Player references.
    for item_id in player.get("inventory", []):
        item_ref(item_id, "player.inventory")
    inventory = list(player.get("inventory", []))
    for slot, item_id in player.get("equipment", {}).items():
        if item_id is None:
            continue
        item_ref(item_id, f"player.equipment.{slot}")
        if item_id not in inventory:
            errors.append(
                f"player.equipment.{slot}: {item_id!r} is equipped but not in player.inventory"
            )

    # First collect NPC names so effect targets can refer forward.
    for room_key, room in rooms.items():
        if not isinstance(room, dict):
            errors.append(f"rooms.{room_key}: room must be a dictionary")
            continue
        for npc in room.get("npcs", []):
            name = npc.get("name")
            if not name:
                errors.append(f"rooms.{room_key}.npcs: NPC is missing a name")
            elif name in npc_names:
                errors.append(f"duplicate NPC name {name!r}")
            else:
                npc_names.add(name)

    def effect(effect_data: Any, path: str) -> None:
        if effect_data is None:
            return
        if not isinstance(effect_data, dict):
            errors.append(f"{path}: effect must be a dictionary or None")
            return
        kind = effect_data.get("type")
        if kind not in SUPPORTED_EFFECTS:
            errors.append(f"{path}: unsupported effect type {kind!r}")
            return
        for field in EFFECT_REQUIRED_FIELDS[kind]:
            if field not in effect_data:
                errors.append(f"{path}: {kind} is missing required field {field!r}")

        if kind == "GivePlayerItemEffect":
            for item_id in effect_data.get("item_ids", []):
                item_ref(item_id, f"{path}.item_ids")
        elif kind == "RemoveItemEffect":
            item_ref(effect_data.get("item_id"), f"{path}.item_id")
            target = effect_data.get("target", "player")
            if target != "player" and target not in npc_names:
                errors.append(f"{path}.target: unknown actor {target!r}")
        elif kind in {"ChangeGoldEffect", "DamageCharacterEffect"}:
            target = effect_data.get("target", "player")
            if target != "player" and target not in npc_names:
                errors.append(f"{path}.target: unknown actor {target!r}")
        elif kind == "MovePlayerEffect":
            room_ref(effect_data.get("destination"), f"{path}.destination")
        elif kind in {"BlockPathEffect", "UnblockPathEffect"}:
            location_key = effect_data.get("location_key")
            room_ref(location_key, f"{path}.location_key")
            if location_key in rooms:
                direction = effect_data.get("direction")
                if not any(
                    exit_spec.get("direction") == direction
                    for exit_spec in rooms[location_key].get("exits", [])
                ):
                    errors.append(
                        f"{path}.direction: room {location_key!r} has no exit {direction!r}"
                    )
        elif kind == "ConditionalEffect":
            for item_id in effect_data.get("required_items", []):
                item_ref(item_id, f"{path}.required_items")
            effect(effect_data.get("success_effect"), f"{path}.success_effect")
            effect(effect_data.get("failure_effect"), f"{path}.failure_effect")
        elif kind == "ChanceEffect":
            chance = effect_data.get("chance")
            if not isinstance(chance, (int, float)) or not 0 <= chance <= 1:
                errors.append(f"{path}.chance must be between 0 and 1")
            effect(effect_data.get("success_effect"), f"{path}.success_effect")
            effect(effect_data.get("failure_effect"), f"{path}.failure_effect")
        elif kind == "CompositeEffect":
            for index, child in enumerate(effect_data.get("effects", [])):
                effect(child, f"{path}.effects[{index}]")
        elif kind == "BranchOnBountyEffect":
            effect(effect_data.get("clean_effect"), f"{path}.clean_effect")
            effect(effect_data.get("hot_effect"), f"{path}.hot_effect")

    for room_key, room in rooms.items():
        if not isinstance(room, dict):
            continue
        if not room.get("name"):
            errors.append(f"rooms.{room_key}: room is missing a name")
        if "description" not in room:
            errors.append(f"rooms.{room_key}: room is missing a description")
        for item_id in room.get("items", []):
            item_ref(item_id, f"rooms.{room_key}.items")
        for index, exit_spec in enumerate(room.get("exits", [])):
            path = f"rooms.{room_key}.exits[{index}]"
            room_ref(exit_spec.get("destination"), f"{path}.destination")
            required_item = exit_spec.get("requires_item")
            if required_item:
                item_ref(required_item, f"{path}.requires_item")
            effect(exit_spec.get("on_attempt_effect"), f"{path}.on_attempt_effect")
            effect(exit_spec.get("on_blocked_effect"), f"{path}.on_blocked_effect")
            effect(exit_spec.get("on_success_effect"), f"{path}.on_success_effect")

        for nindex, npc in enumerate(room.get("npcs", [])):
            npath = f"rooms.{room_key}.npcs[{nindex}]"
            for item_id in npc.get("inventory", []):
                item_ref(item_id, f"{npath}.inventory")
            for slot, item_id in npc.get("equipment", {}).items():
                if item_id is not None:
                    item_ref(item_id, f"{npath}.equipment.{slot}")
            for tindex, topic in enumerate(npc.get("dialogue_topics", [])):
                for item_id in topic.get("required_items", []):
                    item_ref(item_id, f"{npath}.dialogue_topics[{tindex}].required_items")
                effect(
                    topic.get("outcome_effect"),
                    f"{npath}.dialogue_topics[{tindex}].outcome_effect",
                )
            for oindex, offer in enumerate(npc.get("trade_offers", [])):
                for field in ("wants_items", "gives_items"):
                    for item_id in offer.get(field, []):
                        item_ref(item_id, f"{npath}.trade_offers[{oindex}].{field}")
            for oindex, offer in enumerate(npc.get("surrender_trade_offers", [])):
                for field in ("wants_items", "gives_items"):
                    for item_id in offer.get(field, []):
                        item_ref(item_id, f"{npath}.surrender_trade_offers[{oindex}].{field}")
            effect(npc.get("surrender_accept_effect"), f"{npath}.surrender_accept_effect")

        for findex, feature in enumerate(room.get("features", [])):
            fpath = f"rooms.{room_key}.features[{findex}]"
            effect(feature.get("first_effect"), f"{fpath}.first_effect")
            effect(feature.get("repeat_effect"), f"{fpath}.repeat_effect")

        for cindex, choice in enumerate(room.get("choices", [])):
            cpath = f"rooms.{room_key}.choices[{cindex}]"
            destination = choice.get("go")
            if destination:
                room_ref(destination, f"{cpath}.go")
            for item_id in choice.get("give_items", []):
                item_ref(item_id, f"{cpath}.give_items")

    river = world.get("river_crossing")
    if river is not None:
        if not isinstance(river, dict):
            errors.append("river_crossing must be a mapping")
        else:
            for field in ("west_room", "east_room"):
                room_ref(river.get(field), f"river_crossing.{field}")
            if river.get("west_room") == river.get("east_room"):
                errors.append("river_crossing west_room and east_room must differ")
            for field in ("active_flag", "complete_flag"):
                if not river.get(field):
                    errors.append(f"river_crossing.{field} must be a non-empty flag name")
            reward_gold = river.get("reward_gold", 0)
            if not isinstance(reward_gold, int) or reward_gold < 0:
                errors.append("river_crossing.reward_gold must be a non-negative integer")

    for index, encounter in enumerate(world.get("encounters", [])):
        path = f"encounters[{index}]"
        for room_key in encounter.get("locations", []):
            room_ref(room_key, f"{path}.locations")
        chance = encounter.get("chance")
        if not isinstance(chance, (int, float)) or not 0 <= chance <= 1:
            errors.append(f"{path}.chance must be between 0 and 1")
        handler = encounter.get("handler")
        if handler not in SUPPORTED_ENCOUNTER_HANDLERS:
            errors.append(f"{path}.handler: unsupported handler {handler!r}")

    return errors


def assert_valid_world(world: dict[str, Any]) -> None:
    errors = validate_world(world)
    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"Invalid adventure world:\n{details}")


def validate_state(game: "AdventureGame") -> list[str]:
    """Return violations of runtime state-machine invariants."""
    errors: list[str] = []
    if game.player_location not in game.world["rooms"]:
        errors.append(f"player is in unknown room {game.player_location!r}")
    if game.mode not in VALID_MODES:
        errors.append(f"unknown mode {game.mode!r}")
    if game.won and game.lost:
        errors.append("game cannot be both won and lost")
    if game.player.gold < 0:
        errors.append("player gold is negative")
    if game.bounty < 0:
        errors.append("bounty is negative")
    if not 0 <= game.player.health <= game.player_max_hp:
        errors.append(
            f"player health {game.player.health} is outside 0..{game.player_max_hp}"
        )

    if (game.mode == "confirm_move") != (game.pending_exit is not None):
        errors.append("pending_exit must exist exactly while mode == 'confirm_move'")

    if game.current_npc_name is not None and game.current_npc_name not in game.npcs:
        errors.append(f"current_npc_name {game.current_npc_name!r} is unknown")
    if game.mode in {"npc", "riddle", "surrender_decision", "loot"}:
        if game.current_npc_name is None:
            errors.append(f"mode {game.mode!r} requires current_npc_name")
    if game.mode in {"exploration", "confirm_move", "inventory"} and game.current_npc_name is not None:
        errors.append(f"mode {game.mode!r} must not retain current_npc_name")

    if game.mode == "combat":
        if game.combat_npc_name is None:
            errors.append("combat mode requires combat_npc_name")
        elif game.combat_temporary is None and game.combat_npc_name not in game.npcs:
            errors.append(f"combat NPC {game.combat_npc_name!r} is unknown")
    elif game.combat_npc_name is not None or game.combat_temporary is not None:
        errors.append("combat-only context leaked outside combat mode")

    if game.mode == "surrender_decision" and game.current_npc_name in game.npcs:
        if not game.npcs[game.current_npc_name].get("surrendered"):
            errors.append("surrender_decision requires an NPC that has surrendered")
    if game.mode == "loot" and game.current_npc_name in game.npcs:
        if not game.npcs[game.current_npc_name].get("defeated"):
            errors.append("loot mode requires a defeated NPC")

    if game.river_delivery_active:
        state = game.river_state
        reason = state.unsafe_reason()
        if reason is not None:
            errors.append(f"river crossing entered unsafe state: {reason}")
        if game.player_location in game.river_rooms:
            expected_room = game.river_config[f"{state.player}_room"]
            if game.player_location != expected_room:
                errors.append(
                    "river crossing player bank disagrees with current river room"
                )

    for slot, item_id in game.player.equipment.items():
        if item_id is None:
            continue
        if item_id not in game.items:
            errors.append(f"player equipment slot {slot!r} contains unknown item {item_id!r}")
        elif item_id not in game.player.inventory:
            errors.append(
                f"player equipment slot {slot!r} uses {item_id!r} but inventory has no copy"
            )

    for name, npc in game.npcs.items():
        actor = game._npc_actor(npc)
        max_hp = game.actor_max_hp(actor)
        if not 0 <= actor.health <= max_hp:
            errors.append(f"NPC {name!r} health {actor.health} is outside 0..{max_hp}")
        if npc.get("defeated") and actor.health != 0:
            errors.append(f"defeated NPC {name!r} still has {actor.health} HP")
        if actor.health == 0 and not npc.get("defeated") and game.combat_npc_name != name:
            errors.append(f"NPC {name!r} has 0 HP but is not marked defeated")

    return errors


def assert_valid_state(game: "AdventureGame") -> None:
    errors = validate_state(game)
    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise AssertionError(f"Invalid adventure state:\n{details}")
