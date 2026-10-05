"""Validation helpers for capstone world data and runtime state.

These functions are intentionally ordinary Python.  They give students a
concrete example of a production habit: validate data at system boundaries and
express state-machine assumptions as executable invariants.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .models import EQUIPMENT_SLOTS

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

SUPPORTED_FEATURE_TYPES = {"TextFeature", "ScriptedFeature"}
ACTOR_STAT_FIELDS = ("max_hp", "attack_min", "attack_max", "defense")
TRADE_REQUIRED_FIELDS = ("title", "wants_gold", "wants_items", "gives_gold", "gives_items")
RIDDLE_REQUIRED_FIELDS = (
    "question", "answers", "success_lines", "failure_lines",
    "damage_on_failure", "set_flags_on_success",
)

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

    if not isinstance(world.get("name"), str) or not world.get("name", "").strip():
        errors.append("world.name must be a non-empty string")

    for field in ("max_hp", "attack_min", "attack_max", "defense", "gold"):
        if field not in player:
            errors.append(f"player is missing required field {field!r}")
    for field in ("max_hp", "attack_min", "attack_max", "defense", "gold"):
        value = player.get(field)
        if field in player and not isinstance(value, int):
            errors.append(f"player.{field} must be an integer")
    if isinstance(player.get("max_hp"), int) and player["max_hp"] <= 0:
        errors.append("player.max_hp must be positive")
    if all(isinstance(player.get(x), int) for x in ("attack_min", "attack_max")):
        if player["attack_min"] > player["attack_max"]:
            errors.append("player.attack_min cannot exceed player.attack_max")
    if isinstance(player.get("gold"), int) and player["gold"] < 0:
        errors.append("player.gold cannot be negative")

    start = world.get("start_location")
    if start not in rooms:
        errors.append(f"start_location {start!r} is not a room")

    item_ids = set(items)
    npc_names: set[str] = set()

    for item_id, item in items.items():
        path = f"items.{item_id}"
        if not isinstance(item, dict):
            errors.append(f"{path}: item must be a dictionary")
            continue
        if not isinstance(item.get("name"), str) or not item.get("name", "").strip():
            errors.append(f"{path}: item is missing a non-empty name")
        slot = item.get("slot")
        if slot is not None and slot not in EQUIPMENT_SLOTS:
            errors.append(
                f"{path}.slot {slot!r} is invalid; expected one of {EQUIPMENT_SLOTS}"
            )
        for field in ("power_bonus", "defense_bonus", "hp_bonus", "healing"):
            if field in item and not isinstance(item[field], int):
                errors.append(f"{path}.{field} must be an integer")
        if isinstance(item.get("healing"), int) and item["healing"] < 0:
            errors.append(f"{path}.healing cannot be negative")
        flags = item.get("set_flags_on_pickup", [])
        if not isinstance(flags, list):
            errors.append(f"{path}.set_flags_on_pickup must be a list")

    def item_ref(item_id: Any, path: str) -> None:
        if item_id not in item_ids:
            errors.append(f"{path}: unknown item {item_id!r}")

    def room_ref(room_key: Any, path: str) -> None:
        if room_key not in rooms:
            errors.append(f"{path}: unknown room {room_key!r}")

    # Player references.
    player_inventory = player.get("inventory", [])
    if not isinstance(player_inventory, list):
        errors.append("player.inventory must be a list")
        player_inventory = []
    for item_id in player_inventory:
        item_ref(item_id, "player.inventory")
    inventory = list(player_inventory)

    player_equipment = player.get("equipment", {})
    if not isinstance(player_equipment, dict):
        errors.append("player.equipment must be a dictionary")
        player_equipment = {}
    for slot, item_id in player_equipment.items():
        if slot not in EQUIPMENT_SLOTS:
            errors.append(f"player.equipment has invalid slot {slot!r}")
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
        npcs = room.get("npcs", [])
        if not isinstance(npcs, list):
            errors.append(f"rooms.{room_key}.npcs must be a list")
            npcs = []
        for nindex, npc in enumerate(npcs):
            npath = f"rooms.{room_key}.npcs[{nindex}]"
            if not isinstance(npc, dict):
                errors.append(f"{npath}: NPC must be a dictionary")
                continue
            name = npc.get("name")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{npath}: NPC is missing a non-empty name")
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

        if kind == "PrintEffect" and "lines" in effect_data and not isinstance(effect_data["lines"], list):
            errors.append(f"{path}.lines must be a list")
        if kind in {"SetFlagEffect", "ClearFlagEffect"} and "flags" in effect_data and not isinstance(effect_data["flags"], list):
            errors.append(f"{path}.flags must be a list")
        if kind in {"SetBountyEffect", "ChangeBountyEffect", "DamageCharacterEffect"} and "amount" in effect_data and not isinstance(effect_data["amount"], int):
            errors.append(f"{path}.amount must be an integer")

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
        exits = room.get("exits", [])
        if not isinstance(exits, list):
            errors.append(f"rooms.{room_key}.exits must be a list")
            exits = []
        for index, exit_spec in enumerate(exits):
            path = f"rooms.{room_key}.exits[{index}]"
            if not isinstance(exit_spec, dict):
                errors.append(f"{path}: exit must be a dictionary")
                continue
            direction = exit_spec.get("direction")
            if not isinstance(direction, str) or not direction.strip():
                errors.append(f"{path}.direction must be a non-empty string")
            room_ref(exit_spec.get("destination"), f"{path}.destination")
            required_item = exit_spec.get("requires_item")
            if required_item:
                item_ref(required_item, f"{path}.requires_item")
            effect(exit_spec.get("on_attempt_effect"), f"{path}.on_attempt_effect")
            effect(exit_spec.get("on_blocked_effect"), f"{path}.on_blocked_effect")
            effect(exit_spec.get("on_success_effect"), f"{path}.on_success_effect")

        npcs = room.get("npcs", [])
        if not isinstance(npcs, list):
            npcs = []
        for nindex, npc in enumerate(npcs):
            npath = f"rooms.{room_key}.npcs[{nindex}]"
            if not isinstance(npc, dict):
                continue
            stats = npc.get("base_stats")
            if not isinstance(stats, dict):
                errors.append(f"{npath}.base_stats must be a dictionary")
                stats = {}
            for field in ACTOR_STAT_FIELDS:
                if field not in stats:
                    errors.append(f"{npath}.base_stats is missing required field {field!r}")
                elif not isinstance(stats[field], int):
                    errors.append(f"{npath}.base_stats.{field} must be an integer")
            if isinstance(stats.get("max_hp"), int) and stats["max_hp"] <= 0:
                errors.append(f"{npath}.base_stats.max_hp must be positive")
            if all(isinstance(stats.get(x), int) for x in ("attack_min", "attack_max")):
                if stats["attack_min"] > stats["attack_max"]:
                    errors.append(f"{npath}.base_stats.attack_min cannot exceed attack_max")
            if "gold" in npc and (not isinstance(npc["gold"], int) or npc["gold"] < 0):
                errors.append(f"{npath}.gold must be a non-negative integer")
            npc_inventory = npc.get("inventory", [])
            if not isinstance(npc_inventory, list):
                errors.append(f"{npath}.inventory must be a list")
                npc_inventory = []
            for item_id in npc_inventory:
                item_ref(item_id, f"{npath}.inventory")

            npc_equipment = npc.get("equipment", {})
            if not isinstance(npc_equipment, dict):
                errors.append(f"{npath}.equipment must be a dictionary")
                npc_equipment = {}
            for slot, item_id in npc_equipment.items():
                if slot not in EQUIPMENT_SLOTS:
                    errors.append(f"{npath}.equipment has invalid slot {slot!r}")
                if item_id is not None:
                    item_ref(item_id, f"{npath}.equipment.{slot}")

            topics = npc.get("dialogue_topics", [])
            if not isinstance(topics, list):
                errors.append(f"{npath}.dialogue_topics must be a list")
                topics = []
            topic_keys: set[str] = set()
            for tindex, topic in enumerate(topics):
                tpath = f"{npath}.dialogue_topics[{tindex}]"
                if not isinstance(topic, dict):
                    errors.append(f"{tpath}: dialogue topic must be a dictionary")
                    continue
                for field in ("key", "title", "lines"):
                    if field not in topic:
                        errors.append(f"{tpath}: missing required field {field!r}")
                if "title" in topic and (not isinstance(topic["title"], str) or not topic["title"].strip()):
                    errors.append(f"{tpath}.title must be a non-empty string")
                if "lines" in topic and not isinstance(topic["lines"], list):
                    errors.append(f"{tpath}.lines must be a list")
                key = topic.get("key")
                if isinstance(key, str):
                    if key in topic_keys:
                        errors.append(f"{tpath}.key duplicates dialogue key {key!r}")
                    topic_keys.add(key)
                for item_id in topic.get("required_items", []):
                    item_ref(item_id, f"{tpath}.required_items")
                effect(topic.get("outcome_effect"), f"{tpath}.outcome_effect")
            for field_name in ("trade_offers", "surrender_trade_offers"):
                offers = npc.get(field_name, [])
                if not isinstance(offers, list):
                    errors.append(f"{npath}.{field_name} must be a list")
                    continue
                for oindex, offer in enumerate(offers):
                    opath = f"{npath}.{field_name}[{oindex}]"
                    if not isinstance(offer, dict):
                        errors.append(f"{opath}: trade offer must be a dictionary")
                        continue
                    for required in TRADE_REQUIRED_FIELDS:
                        if required not in offer:
                            errors.append(f"{opath}: missing required field {required!r}")
                    for gold_field in ("wants_gold", "gives_gold"):
                        if gold_field in offer and (
                            not isinstance(offer[gold_field], int) or offer[gold_field] < 0
                        ):
                            errors.append(f"{opath}.{gold_field} must be a non-negative integer")
                    for item_field in ("wants_items", "gives_items"):
                        values = offer.get(item_field, [])
                        if not isinstance(values, list):
                            errors.append(f"{opath}.{item_field} must be a list")
                            continue
                        for item_id in values:
                            item_ref(item_id, f"{opath}.{item_field}")

            riddle = npc.get("riddle")
            if riddle is not None:
                rpath = f"{npath}.riddle"
                if not isinstance(riddle, dict):
                    errors.append(f"{rpath} must be a dictionary or None")
                else:
                    for required in RIDDLE_REQUIRED_FIELDS:
                        if required not in riddle:
                            errors.append(f"{rpath}: missing required field {required!r}")
                    if "question" in riddle and (
                        not isinstance(riddle["question"], str) or not riddle["question"].strip()
                    ):
                        errors.append(f"{rpath}.question must be a non-empty string")
                    answers = riddle.get("answers", [])
                    if not isinstance(answers, list) or not answers:
                        errors.append(f"{rpath}.answers must be a non-empty list")
                    damage = riddle.get("damage_on_failure")
                    if damage is not None and (not isinstance(damage, int) or damage < 0):
                        errors.append(f"{rpath}.damage_on_failure must be a non-negative integer")

            for item_id in npc.get("reward_items", []):
                item_ref(item_id, f"{npath}.reward_items")
            effect(npc.get("surrender_accept_effect"), f"{npath}.surrender_accept_effect")

        features = room.get("features", [])
        if not isinstance(features, list):
            errors.append(f"rooms.{room_key}.features must be a list")
            features = []
        for findex, feature in enumerate(features):
            fpath = f"rooms.{room_key}.features[{findex}]"
            if not isinstance(feature, dict):
                errors.append(f"{fpath}: feature must be a dictionary")
                continue
            if not isinstance(feature.get("name"), str) or not feature.get("name", "").strip():
                errors.append(f"{fpath}.name must be a non-empty string")
            ftype = feature.get("type")
            if ftype not in SUPPORTED_FEATURE_TYPES:
                errors.append(f"{fpath}.type: unsupported feature type {ftype!r}")
            if ftype == "TextFeature" and not isinstance(feature.get("text"), str):
                errors.append(f"{fpath}.text must be a string")
            effect(feature.get("first_effect"), f"{fpath}.first_effect")
            effect(feature.get("repeat_effect"), f"{fpath}.repeat_effect")

        choices = room.get("choices", [])
        if not isinstance(choices, list):
            errors.append(f"rooms.{room_key}.choices must be a list")
            choices = []
        for cindex, choice in enumerate(choices):
            cpath = f"rooms.{room_key}.choices[{cindex}]"
            if not isinstance(choice, dict):
                errors.append(f"{cpath}: room choice must be a dictionary")
                continue
            if not isinstance(choice.get("text"), str) or not choice.get("text", "").strip():
                errors.append(f"{cpath}.text must be a non-empty string")
            if "result" in choice and not isinstance(choice["result"], list):
                errors.append(f"{cpath}.result must be a list of lines")
            destination = choice.get("go")
            if destination:
                room_ref(destination, f"{cpath}.go")
            for item_id in choice.get("give_items", []):
                item_ref(item_id, f"{cpath}.give_items")

    story_rules = world.get("story_rules")
    if story_rules is not None:
        if not isinstance(story_rules, dict):
            errors.append("story_rules must be a dictionary")
        else:
            goals = story_rules.get("goals", [])
            if not isinstance(goals, list):
                errors.append("story_rules.goals must be a list")
            else:
                for index, goal in enumerate(goals):
                    gpath = f"story_rules.goals[{index}]"
                    if not isinstance(goal, dict):
                        errors.append(f"{gpath}: goal must be a dictionary")
                        continue
                    if not isinstance(goal.get("text"), str) or not goal.get("text", "").strip():
                        errors.append(f"{gpath}.text must be a non-empty string")
                    for field in ("required_items", "blocked_items"):
                        values = goal.get(field, [])
                        if not isinstance(values, list):
                            errors.append(f"{gpath}.{field} must be a list")
                            continue
                        for item_id in values:
                            item_ref(item_id, f"{gpath}.{field}")

            for field in ("spare_flags", "riddle_reward_items", "npc_defeat_lines"):
                mapping = story_rules.get(field, {})
                if not isinstance(mapping, dict):
                    errors.append(f"story_rules.{field} must be a dictionary")
                    continue
                for npc_name, values in mapping.items():
                    if npc_name not in npc_names:
                        errors.append(f"story_rules.{field}: unknown NPC {npc_name!r}")
                    if not isinstance(values, list):
                        errors.append(f"story_rules.{field}.{npc_name} must be a list")
                        continue
                    if field == "riddle_reward_items":
                        for item_id in values:
                            item_ref(item_id, f"story_rules.{field}.{npc_name}")

            pickup_flags = story_rules.get("item_pickup_flags", {})
            if not isinstance(pickup_flags, dict):
                errors.append("story_rules.item_pickup_flags must be a dictionary")
            else:
                for item_id, flags in pickup_flags.items():
                    item_ref(item_id, "story_rules.item_pickup_flags")
                    if not isinstance(flags, list):
                        errors.append(
                            f"story_rules.item_pickup_flags.{item_id} must be a list"
                        )

            enter_rules = story_rules.get("location_enter_once", {})
            if not isinstance(enter_rules, dict):
                errors.append("story_rules.location_enter_once must be a dictionary")
            else:
                for room_key, rule in enter_rules.items():
                    rpath = f"story_rules.location_enter_once.{room_key}"
                    room_ref(room_key, rpath)
                    if not isinstance(rule, dict):
                        errors.append(f"{rpath} must be a dictionary")
                        continue
                    if not isinstance(rule.get("flag"), str) or not rule.get("flag", "").strip():
                        errors.append(f"{rpath}.flag must be a non-empty string")
                    if not isinstance(rule.get("lines", []), list):
                        errors.append(f"{rpath}.lines must be a list")

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

    encounters = world.get("encounters", [])
    if not isinstance(encounters, list):
        errors.append("world.encounters must be a list")
        encounters = []
    for index, encounter in enumerate(encounters):
        path = f"encounters[{index}]"
        if not isinstance(encounter, dict):
            errors.append(f"{path}: encounter must be a dictionary")
            continue
        if not isinstance(encounter.get("name"), str) or not encounter.get("name", "").strip():
            errors.append(f"{path}.name must be a non-empty string")
        if not isinstance(encounter.get("locations", []), list):
            errors.append(f"{path}.locations must be a list")
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
    if {"game_won", "game_lost"} <= game.flags:
        errors.append("terminal flags game_won and game_lost cannot both be set")
    if game.player.health == 0 and not game.lost:
        errors.append("zero player HP must immediately put the game in a lost state")
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
    if game.pending_exit is not None:
        room_key, exit_index = game.pending_exit
        if room_key != game.player_location:
            errors.append("pending_exit room must match the player's current room")
        elif room_key not in game.world["rooms"]:
            errors.append(f"pending_exit refers to unknown room {room_key!r}")
        elif not isinstance(exit_index, int) or not (
            0 <= exit_index < len(game.world["rooms"][room_key].get("exits", []))
        ):
            errors.append(f"pending_exit has invalid exit index {exit_index!r}")

    if game.current_npc_name is not None and game.current_npc_name not in game.npcs:
        errors.append(f"current_npc_name {game.current_npc_name!r} is unknown")
    if game.mode in {"npc", "riddle", "surrender_decision", "loot"}:
        if game.current_npc_name is None:
            errors.append(f"mode {game.mode!r} requires current_npc_name")
    if game.mode in {"exploration", "confirm_move", "inventory"} and game.current_npc_name is not None:
        errors.append(f"mode {game.mode!r} must not retain current_npc_name")

    if game.mode in {"npc", "riddle", "surrender_decision", "loot"} and game.current_npc_name in game.npcs:
        npc_room = game.npc_rooms.get(game.current_npc_name)
        if npc_room != game.player_location:
            errors.append(
                f"mode {game.mode!r} NPC {game.current_npc_name!r} is in {npc_room!r}, "
                f"not player room {game.player_location!r}"
            )
    if game.mode == "riddle" and game.current_npc_name in game.npcs:
        npc = game.npcs[game.current_npc_name]
        if not game.npc_is_alive(npc):
            errors.append("riddle mode requires a living NPC")
        if not npc.get("riddle"):
            errors.append("riddle mode requires an NPC with a riddle")

    if game.mode == "combat":
        if game.combat_npc_name is None:
            errors.append("combat mode requires combat_npc_name")
        elif game.combat_temporary is None and game.combat_npc_name not in game.npcs:
            errors.append(f"combat NPC {game.combat_npc_name!r} is unknown")
        if game.combat_temporary is None:
            if game.current_npc_name != game.combat_npc_name:
                errors.append("persistent combat must retain the same NPC focus")
        elif game.current_npc_name is not None:
            errors.append("temporary combat must not retain a persistent NPC focus")
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
