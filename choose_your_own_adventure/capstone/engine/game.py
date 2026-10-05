"""Reusable engine for the full capstone adventures.

The public shape stays intentionally small::

    game.describe() -> list[str]
    game.choices()  -> list[Choice]
    game.apply(action) -> list[str]

The large original stories are data in ``capstone/worlds``.  A student can add
an ordinary room and ordinary room choices there without learning combat,
trading, riddles, encounter routing, or the effect interpreter first.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import random
from typing import Any

from .actions import apply_effect
from .models import Actor, Choice
from .validation import assert_valid_world


class AdventureGame:
    def __init__(self, world_data: dict[str, Any], player_name: str = "Tav", *, seed: int = 0):
        self.world = deepcopy(world_data)
        assert_valid_world(self.world)
        self.rng = random.Random(seed)
        p = self.world["player"]
        self.player = Actor(
            name=player_name,
            max_hp=p["max_hp"],
            attack_min=p["attack_min"],
            attack_max=p["attack_max"],
            defense=p["defense"],
            gold=p["gold"],
            inventory=list(p.get("inventory", [])),
            equipment=dict(p.get("equipment", {"weapon": None, "armor": None, "charm": None})),
        )
        self.player_location = self.world["start_location"]
        self.flags = set(p.get("flags", []))
        self.bounty = 0
        self.mode = "exploration"
        self.current_npc_name: str | None = None
        self.combat_npc_name: str | None = None
        self.combat_temporary: dict[str, Any] | None = None
        self.player_defending = False
        self.enemy_defending = False
        self.pending_exit: tuple[str, int] | None = None
        self.won = False
        self.lost = False
        self.ending = ""
        self._index_npcs()
        self.on_location_enter()

    def _index_npcs(self) -> None:
        self.npcs: dict[str, dict[str, Any]] = {}
        self.npc_rooms: dict[str, str] = {}
        for room_key, room in self.world["rooms"].items():
            for npc in room.get("npcs", []):
                self.npcs[npc["name"]] = npc
                self.npc_rooms[npc["name"]] = room_key

    @property
    def over(self) -> bool:
        return self.won or self.lost

    @property
    def room(self) -> dict[str, Any]:
        return self.world["rooms"][self.player_location]

    @property
    def items(self) -> dict[str, dict[str, Any]]:
        return self.world["items"]

    @property
    def equipped_items(self) -> list[dict[str, Any]]:
        return [self.items[item_id] for item_id in self.player.equipment.values() if item_id]

    @property
    def player_max_hp(self) -> int:
        return self.player.max_hp + sum(item.get("hp_bonus", 0) for item in self.equipped_items)

    @property
    def player_defense(self) -> int:
        return self.player.defense + sum(item.get("defense_bonus", 0) for item in self.equipped_items)

    @property
    def player_attack_range(self) -> tuple[int, int]:
        bonus = sum(item.get("power_bonus", 0) for item in self.equipped_items)
        return self.player.attack_min + bonus, self.player.attack_max + bonus

    def item_name(self, item_id: str | None) -> str:
        return "empty" if item_id is None else self.items[item_id]["name"]

    def find_npc(self, name: str) -> Actor | None:
        spec = self.npcs.get(name)
        if spec is None:
            return None
        return self._npc_actor(spec)

    def _npc_actor(self, spec: dict[str, Any]) -> Actor:
        actor = spec.get("_actor")
        if actor is None:
            stats = spec["base_stats"]
            actor = Actor(
                name=spec["name"],
                max_hp=stats["max_hp"],
                attack_min=stats["attack_min"],
                attack_max=stats["attack_max"],
                defense=stats["defense"],
                health=spec.get("health", stats["max_hp"]),
                gold=spec.get("gold", 0),
                inventory=list(spec.get("inventory", [])),
                equipment=dict(spec.get("equipment", {"weapon": None, "armor": None, "charm": None})),
            )
            spec["_actor"] = actor
        return actor

    def npc_is_alive(self, npc: dict[str, Any]) -> bool:
        """Return whether an NPC can still take living-character actions."""
        return not npc.get("defeated", False) and self._npc_actor(npc).health > 0

    def npc_has_loot(self, npc: dict[str, Any]) -> bool:
        actor = self._npc_actor(npc)
        return bool(npc.get("defeated")) and (bool(actor.inventory) or actor.gold > 0)

    def goal_text(self) -> str:
        """Return the current player-facing objective for any frontend."""
        if "jailed" in self.flags:
            return "Serve your time and get back on your feet."

        source = self.world.get("source_version")
        if source == "version4.py":
            if "quest_started" not in self.flags:
                return "Talk to Elder Mira."
            if "has_star_crystal" in self.flags and "game_won" not in self.flags:
                return "Return the Star Crystal to Elder Mira."
            if "game_won" in self.flags:
                return "The valley has been saved."
            return "Explore the valley and recover the Star Crystal."

        if source == "version8.py":
            if "act1_started" not in self.flags:
                return "Talk to Rafe Mercer and get briefed on the lift."
            if "act2_started" not in self.flags and "has_payroll_shard" not in self.flags:
                return "Break into the Black Archive and steal the payroll shard."
            if "act2_started" not in self.flags:
                return "Reach the extraction skiff and see how the job shakes out."
            if "found_locator" not in self.flags:
                return "Search Relay Ridge for a locator chart to the buried site."
            if not self.player.has_item("vault_cipher"):
                return "Reach Drill Site Theta and secure the vault cipher."
            if "has_grave_core" not in self.flags:
                return "Descend through Burial Crater and reach the vault heart."
            if "game_won" in self.flags:
                if "ending_corporate" in self.flags:
                    return "You sold the vault and bought yourself a future."
                if "ending_broadcast" in self.flags:
                    return "The truth is out, and the scramble has begun."
                if "ending_bury" in self.flags:
                    return "The vault is buried again."
            return "Decide what to do with the grave core before the cutters close in."

        return "Explore."

    def snapshot(self) -> dict[str, Any]:
        """Return UI-ready state without giving the UI gameplay authority."""
        attack_low, attack_high = self.player_attack_range
        inventory_counts = Counter(self.item_name(item_id) for item_id in self.player.inventory)
        active_npcs = [
            npc["name"]
            for npc in self.room.get("npcs", [])
            if self.npc_is_alive(npc)
        ]

        focus_name: str | None = None
        focus_state: str | None = None
        focus_mood: str | None = None
        if self.mode == "combat":
            spec = self.current_combat_spec()
            actor = self.current_combat_actor()
            focus_name = spec["name"]
            focus_state = "dead" if actor.health <= 0 else "alive"
            focus_mood = "hostile"
        elif self.current_npc_name:
            spec = self.npcs.get(self.current_npc_name)
            if spec is not None:
                actor = self._npc_actor(spec)
                focus_name = spec["name"]
                focus_state = "dead" if actor.health <= 0 or spec.get("defeated") else "alive"
                focus_mood = self.npc_mood(spec)

        return {
            "world": self.world["name"],
            "source_version": self.world.get("source_version"),
            "goal": self.goal_text(),
            "mode": self.mode,
            "location_key": self.player_location,
            "location": self.room["name"],
            "description": self.room["description"],
            "items": [self.item_name(item_id) for item_id in self.room.get("items", [])],
            "npcs": active_npcs,
            "features": [feature["name"] for feature in self.room.get("features", [])],
            "health": self.player.health,
            "max_health": self.player_max_hp,
            "attack": (attack_low, attack_high),
            "defense": self.player_defense,
            "gold": self.player.gold,
            "bounty": self.bounty,
            "equipment": {slot: self.item_name(item_id) for slot, item_id in self.player.equipment.items()},
            "inventory": sorted(inventory_counts.items()),
            "flags": sorted(self.flags),
            "focus_npc_name": focus_name,
            "focus_npc_state": focus_state,
            "focus_npc_mood": focus_mood,
            "over": self.over,
            "won": self.won,
            "ending": self.ending,
        }

    def text_prompt(self) -> str | None:
        """Return the free-text prompt required by the current mode, if any."""
        if self.mode == "riddle" and self.current_npc_name:
            npc = self.npcs[self.current_npc_name]
            riddle = npc.get("riddle")
            if riddle:
                return riddle["question"]
        return None

    def describe(self) -> list[str]:
        if self.over:
            return [self.ending or ("You win." if self.won else "Game over.")]
        if self.mode == "combat":
            npc = self.current_combat_spec()
            actor = self.current_combat_actor()
            return [
                f"Combat - {npc['name']}",
                npc.get("description", ""),
                f"Your HP: {self.player.health}/{self.player_max_hp}",
                f"{npc['name']} HP: {actor.health}/{self.actor_max_hp(actor)}",
                f"Gold: {self.player.gold}    Bounty: {self.bounty}",
            ]
        if self.mode == "surrender_decision" and self.current_npc_name:
            npc = self.npcs[self.current_npc_name]
            return [
                f"{npc['name']} surrenders",
                "They have stopped fighting. Decide whether to spare or kill them.",
            ]
        if self.mode == "loot" and self.current_npc_name:
            npc = self.npcs[self.current_npc_name]
            actor = self._npc_actor(npc)
            lines = [f"Looting {npc['name']}"]
            if actor.inventory:
                lines.extend(f"- {self.item_name(item_id)}" for item_id in actor.inventory)
            else:
                lines.append("- nothing remains")
            return lines
        if self.mode == "npc" and self.current_npc_name:
            npc = self.npcs[self.current_npc_name]
            actor = self._npc_actor(npc)
            return [npc["name"], npc.get("description", ""), f"Mood: {self.npc_mood(npc)}", f"HP: {actor.health}/{self.actor_max_hp(actor)}"]
        if self.mode == "inventory":
            lines = [
                "Inventory / Loadout",
                f"HP: {self.player.health}/{self.player_max_hp}    Gold: {self.player.gold}",
                "Equipment: " + ", ".join(f"{slot}={self.item_name(item)}" for slot, item in self.player.equipment.items()),
            ]
            if self.player.inventory:
                lines.extend(f"- {self.item_name(item)}" for item in self.player.inventory)
            else:
                lines.append("- empty")
            return lines

        lines = [
            f"{self.world['name']} - {self.room['name']}",
            self.room["description"],
            f"HP: {self.player.health}/{self.player_max_hp}    Gold: {self.player.gold}    Bounty: {self.bounty}",
        ]
        if self.room.get("items"):
            lines.append("Items here: " + ", ".join(self.item_name(x) for x in self.room["items"]))
        active_npcs = [n["name"] for n in self.room.get("npcs", []) if self.npc_is_alive(n)]
        if active_npcs:
            lines.append("People / creatures here: " + ", ".join(active_npcs))
        if self.room.get("features"):
            lines.append("Notable features: " + ", ".join(f["name"] for f in self.room["features"]))
        return lines

    def choices(self) -> list[Choice]:
        if self.over:
            return []
        if self.mode == "riddle":
            return []
        if self.mode == "confirm_move":
            return [Choice("move:confirm", "Continue"), Choice("move:cancel", "Do not risk it")]
        if self.mode == "surrender_decision":
            return [
                Choice("surrender:spare", "Spare them"),
                Choice("surrender:kill", "Kill them"),
            ]
        if self.mode == "loot" and self.current_npc_name:
            actor = self._npc_actor(self.npcs[self.current_npc_name])
            result: list[Choice] = []
            seen: set[str] = set()
            for item_id in actor.inventory:
                if item_id in seen:
                    continue
                seen.add(item_id)
                count = actor.inventory.count(item_id)
                suffix = f" x{count}" if count > 1 else ""
                result.append(Choice(f"loot:item:{item_id}", f"Take {self.item_name(item_id)}{suffix}"))
            result.append(Choice("loot:done", "Done looting"))
            return result
        if self.mode == "combat":
            result = [Choice("combat:attack", "Attack"), Choice("combat:defend", "Defend")]
            for item_id in self.consumables(self.player):
                result.append(Choice(f"combat:item:{item_id}", f"Use {self.item_name(item_id)}"))
            result += [Choice("combat:run", "Run"), Choice("combat:surrender", "Surrender")]
            return result
        if self.mode == "inventory":
            result: list[Choice] = []
            seen: set[str] = set()
            for item_id in self.player.inventory:
                if item_id in seen:
                    continue
                seen.add(item_id)
                item = self.items[item_id]
                if item.get("slot") and self.player.equipment.get(item["slot"]) != item_id:
                    result.append(Choice(f"equip:{item_id}", f"Equip {item['name']} ({item['slot']})"))
                if item.get("healing", 0) and self.player.health < self.player_max_hp:
                    result.append(Choice(f"use:{item_id}", f"Use {item['name']}"))
            for slot, item_id in self.player.equipment.items():
                if item_id:
                    result.append(Choice(f"unequip:{slot}", f"Unequip {slot}: {self.item_name(item_id)}"))
            result.append(Choice("inventory:back", "Back"))
            return result
        if self.mode == "npc" and self.current_npc_name:
            return self.npc_choices(self.npcs[self.current_npc_name])

        result: list[Choice] = []
        jailed = "jailed" in self.flags and self.player_location == "jail"
        if not jailed:
            for index, exit_spec in enumerate(self.room.get("exits", [])):
                destination = self.world["rooms"][exit_spec["destination"]]
                text = f"Go {exit_spec['direction']} to {destination['name']}"
                if self.exit_is_blocked(exit_spec):
                    text += " [blocked]"
                elif exit_spec.get("warning_text"):
                    text += " [risky]"
                result.append(Choice(f"move:{index}", text))
            for item_id in self.room.get("items", []):
                result.append(Choice(f"take:{item_id}", f"Take {self.item_name(item_id)}"))
            for index, npc in enumerate(self.room.get("npcs", [])):
                if self.npc_is_alive(npc):
                    result.append(Choice(f"npc:{index}", f"Approach {npc['name']}"))
                elif self.npc_has_loot(npc):
                    result.append(Choice(f"npc:{index}", f"Inspect the remains of {npc['name']}"))
        for index, feature in enumerate(self.room.get("features", [])):
            result.append(Choice(f"feature:{index}", f"{feature.get('verb', 'Inspect')} {feature['name']}"))
        for index, spec in enumerate(self.room.get("choices", [])):
            if self.simple_choice_available(spec):
                result.append(Choice(f"roomchoice:{index}", spec["text"]))
        if not jailed:
            result.append(Choice("inventory", "Open inventory / equipment"))
        return result

    def apply(self, action: str) -> list[str]:
        legal = {choice.action for choice in self.choices()}
        if action not in legal:
            raise ValueError(f"Action is not legal right now: {action!r}")

        if self.mode == "confirm_move":
            if action == "move:cancel":
                self.mode = "exploration"
                self.pending_exit = None
                lines = ["You decide not to risk it."]
            else:
                room_key, index = self.pending_exit
                self.mode = "exploration"
                self.pending_exit = None
                lines = self.finish_move(room_key, index)
        elif self.mode == "surrender_decision":
            lines = self.apply_surrender_decision(action)
        elif self.mode == "loot":
            lines = self.apply_loot(action)
        elif self.mode == "combat":
            lines = self.apply_combat(action)
        elif self.mode == "inventory":
            lines = self.apply_inventory(action)
        elif self.mode == "npc" and self.current_npc_name:
            lines = self.apply_npc(action)
        elif action == "inventory":
            self.mode = "inventory"
            lines = []
        elif action.startswith("move:"):
            lines = self.begin_move(int(action.split(":", 1)[1]))
        elif action.startswith("take:"):
            lines = self.take_item(action.split(":", 1)[1])
        elif action.startswith("npc:"):
            npc = self.room["npcs"][int(action.split(":", 1)[1])]
            self.current_npc_name = npc["name"]
            if self.npc_is_alive(npc) and npc.get("hostile"):
                self.start_combat(npc["name"])
                lines = [f"{npc['name']} attacks!"]
            else:
                self.mode = "npc"
                lines = []
        elif action.startswith("feature:"):
            lines = self.use_feature(int(action.split(":", 1)[1]))
        elif action.startswith("roomchoice:"):
            lines = self.apply_simple_choice(
                self.room["choices"][int(action.split(":", 1)[1])]
            )
        else:
            raise AssertionError(action)

        return self._finish_player_action(lines)

    def _finish_player_action(self, lines: list[str]) -> list[str]:
        """Run reactions that the original games checked between turns.

        The old engine reevaluated encounter rules at the start of every
        exploration turn, not only when the player crossed into a new room.
        Keeping that boundary matters for consequences such as a village guard
        confronting a wanted player after a crime, and for Dust Vault patrols.
        """
        if self.mode == "exploration" and not self.over:
            encounter = self.try_encounter()
            if encounter is not None:
                lines.extend(encounter)
        return lines

    def npc_choices(self, npc: dict[str, Any]) -> list[Choice]:
        result: list[Choice] = []
        if not self.npc_is_alive(npc):
            if self.npc_has_loot(npc):
                result.append(Choice("npc:loot", f"Loot {npc['name']}"))
            result.append(Choice("npc:leave", "Step away"))
            return result

        for index, topic in enumerate(npc.get("dialogue_topics", [])):
            if self.topic_available(npc, topic):
                result.append(Choice(f"talk:{index}", topic["title"]))
        for index, offer in enumerate(npc.get("trade_offers", [])):
            if self.trade_available(npc, index, offer):
                result.append(Choice(f"trade:{index}", offer["title"]))
        if npc.get("riddle") and not npc.get("riddle_solved", False):
            # The original asked for free text.  The console runner recognizes
            # this action and prompts without exposing the accepted answers.
            result.append(Choice("riddle", "Accept the riddle / challenge"))
        result.append(Choice("npc:attack", f"Attack {npc['name']}"))
        result.append(Choice("npc:leave", "Step away"))
        return result

    def apply_npc(self, action: str) -> list[str]:
        npc = self.npcs[self.current_npc_name]
        actor = self._npc_actor(npc)
        if action == "npc:leave":
            self.mode = "exploration"
            self.current_npc_name = None
            return []
        if action == "npc:attack":
            lines: list[str] = []
            if not npc.get("hostile") and not npc.get("defeated"):
                tags = set(npc.get("tags", []))
                if tags & {"guard", "law"}:
                    self.bounty += 75
                    lines.append(f"[Bounty] Assaulting guard {npc['name']}: {self.bounty}")
                elif npc.get("aggression", 0) < 50:
                    self.bounty += 25
                    lines.append(f"[Bounty] Assaulting {npc['name']}: {self.bounty}")
            npc["hostile"] = True
            npc["aggression"] = max(70, npc.get("aggression", 0))
            self.start_combat(npc["name"])
            return lines
        if action == "npc:loot":
            lines = []
            if actor.gold:
                lines.append(f"You take {actor.gold} gold.")
                self.player.gold += actor.gold
                actor.gold = 0
            if actor.inventory:
                self.mode = "loot"
                return lines
            return lines or ["Nothing remains."]
        if action == "riddle":
            self.mode = "riddle"
            return list(npc["riddle"].get("intro_lines", [])) + [npc["riddle"]["question"]]
        if action.startswith("talk:"):
            topic = npc["dialogue_topics"][int(action.split(":", 1)[1])]
            lines = [f"{npc['name']}: {line}" for line in topic["lines"]]
            lines.extend(apply_effect(self, topic.get("outcome_effect")))
            if topic.get("once"):
                npc.setdefault("used_topics", []).append(topic["key"])
            self.sync_end_state()
            return lines
        if action.startswith("trade:"):
            return self.do_trade(npc, int(action.split(":", 1)[1]))
        raise AssertionError(action)

    def apply_loot(self, action: str) -> list[str]:
        npc = self.npcs[self.current_npc_name]
        actor = self._npc_actor(npc)
        if action == "loot:done":
            self.mode = "npc"
            return []
        if not action.startswith("loot:item:"):
            raise AssertionError(action)
        item_id = action.split(":", 2)[2]
        if not self.remove_actor_item(actor, item_id):
            return ["That item is no longer there."]
        lines = self.give_player_item(item_id)
        if not actor.inventory:
            self.mode = "npc"
        return lines

    def apply_surrender_decision(self, action: str) -> list[str]:
        npc = self.npcs[self.current_npc_name]
        name = npc["name"]
        if action == "surrender:spare":
            if name == "Bandit Nox":
                self.flags.add("bandit_spared")
            self.mode = "npc" if npc.get("persistent", True) else "exploration"
            if self.mode == "exploration":
                self.current_npc_name = None
            return [f"You spare {name}."]
        if action == "surrender:kill":
            actor = self._npc_actor(npc)
            actor.health = 0
            lines = self.defeat_npc(name)
            if npc.get("persistent", True):
                self.mode = "npc"
            else:
                self.mode = "exploration"
                self.current_npc_name = None
            return lines
        raise AssertionError(action)

    def submit_riddle_answer(self, answer: str) -> list[str]:
        if self.mode != "riddle" or not self.current_npc_name:
            raise ValueError("No riddle is waiting for an answer.")
        npc = self.npcs[self.current_npc_name]
        riddle = npc["riddle"]
        lines: list[str] = []
        if answer.strip().lower() in {x.lower() for x in riddle["answers"]}:
            lines.extend(f"{npc['name']}: {line}" for line in riddle["success_lines"])
            npc["riddle_solved"] = True
            self.flags.update(riddle["set_flags_on_success"])
            # The original authored data stores these rewards on the guardian,
            # but the old interaction engine never exposed a nonviolent way to
            # take them after passing the riddle.  Preserve the intended story
            # path rather than forcing students to murder a guardian who just
            # said the prize may be taken.
            intended_reward = {
                "Tower Guardian": "star_crystal",
                "Custodian Echo": "grave_core",
            }.get(npc["name"])
            actor = self._npc_actor(npc)
            if intended_reward and actor.has_item(intended_reward):
                self.remove_actor_item(actor, intended_reward)
                lines.extend(self.give_player_item(intended_reward))
        else:
            lines.extend(f"{npc['name']}: {line}" for line in riddle["failure_lines"])
            if riddle["damage_on_failure"]:
                actual = self.damage_actor(self.player, riddle["damage_on_failure"])
                lines.append(f"You take {actual} damage.")
                if self.player.health <= 0:
                    self.lost = True
                    self.ending = "You collapse from your injuries. The adventure ends here."
        self.mode = "npc"
        return lines

    def topic_available(self, npc: dict[str, Any], topic: dict[str, Any]) -> bool:
        if not self.npc_is_alive(npc):
            return False
        if topic.get("once") and topic["key"] in npc.get("used_topics", []):
            return False
        if not set(topic.get("required_flags", [])) <= self.flags:
            return False
        if set(topic.get("blocked_flags", [])) & self.flags:
            return False
        return self.player.has_items(topic.get("required_items", []))

    def trade_available(self, npc: dict[str, Any], index: int, offer: dict[str, Any]) -> bool:
        actor = self._npc_actor(npc)
        if not self.npc_is_alive(npc):
            return False
        if not offer.get("repeatable") and index in set(npc.get("completed_trades", [])):
            return False
        if not set(offer.get("required_flags", [])) <= self.flags:
            return False
        if set(offer.get("blocked_flags", [])) & self.flags:
            return False
        if actor.gold < offer.get("gives_gold", 0):
            return False
        if not actor.has_items(offer.get("gives_items", [])):
            return False
        if npc.get("surrendered"):
            return True
        return npc.get("willingness_to_trade", 0) >= 30 and not npc.get("hostile", False)

    def do_trade(self, npc: dict[str, Any], index: int) -> list[str]:
        offer = npc["trade_offers"][index]
        actor = self._npc_actor(npc)
        if self.player.gold < offer["wants_gold"]:
            return [f"{npc['name']}: Come back when you have {offer['wants_gold']} gold."]
        if not self.player.has_items(offer["wants_items"]):
            names = ", ".join(self.item_name(x) for x in offer["wants_items"])
            return [f"{npc['name']}: Come back when you have: {names}."]
        if actor.gold < offer["gives_gold"] or not actor.has_items(offer["gives_items"]):
            return [f"{npc['name']}: I cannot complete that trade right now."]
        self.player.gold -= offer["wants_gold"]
        actor.gold += offer["wants_gold"]
        actor.gold -= offer["gives_gold"]
        self.player.gold += offer["gives_gold"]
        self.remove_actor_items(self.player, offer["wants_items"])
        for item_id in offer["wants_items"]:
            actor.add_item(item_id)
        self.remove_actor_items(actor, offer["gives_items"])
        lines = []
        for item_id in offer["gives_items"]:
            lines.extend(self.give_player_item(item_id))
        if not offer.get("repeatable"):
            npc.setdefault("completed_trades", []).append(index)
        lines.append(f"{npc['name']}: A fair trade.")
        return lines

    def begin_move(self, index: int) -> list[str]:
        exit_spec = self.room["exits"][index]
        lines = apply_effect(self, exit_spec.get("on_attempt_effect"))
        if self.over:
            return lines
        if self.exit_is_blocked(exit_spec):
            lines.append(exit_spec.get("blocked_text") or "That path is blocked.")
            lines.extend(apply_effect(self, exit_spec.get("on_blocked_effect")))
            return lines
        if exit_spec.get("warning_text"):
            lines.append(exit_spec["warning_text"])
            self.pending_exit = (self.player_location, index)
            self.mode = "confirm_move"
            return lines
        lines.extend(self.finish_move(self.player_location, index))
        return lines

    def finish_move(self, room_key: str, index: int) -> list[str]:
        exit_spec = self.world["rooms"][room_key]["exits"][index]
        self.player_location = exit_spec["destination"]
        self.flags.add(f"visited:{self.player_location}")
        lines = apply_effect(self, exit_spec.get("on_success_effect"))
        if not self.over:
            lines.extend(self.on_location_enter())
        return lines

    def exit_is_blocked(self, exit_spec: dict[str, Any]) -> bool:
        if exit_spec.get("blocked"):
            return True
        required_item = exit_spec.get("requires_item")
        if required_item and not self.player.has_item(required_item):
            return True
        required_flag = exit_spec.get("requires_flag")
        if required_flag and required_flag not in self.flags:
            return True
        return False

    def set_exit_blocked(self, room_key: str, direction: str, blocked: bool, reason: str | None) -> None:
        # Match the original World's find_exit(): scripted path effects target
        # the first exit with this label. This matters when a world deliberately
        # contains multiple exits that share a direction name.
        for exit_spec in self.world["rooms"][room_key]["exits"]:
            if exit_spec["direction"] == direction:
                exit_spec["blocked"] = blocked
                if reason is not None:
                    exit_spec["blocked_text"] = reason
                return

    def take_item(self, item_id: str) -> list[str]:
        if item_id not in self.room.get("items", []):
            return ["That item is no longer here."]
        self.room["items"].remove(item_id)
        return self.give_player_item(item_id)

    def give_player_item(self, item_id: str) -> list[str]:
        self.player.add_item(item_id)
        item = self.items[item_id]
        self.flags.update(item.get("set_flags_on_pickup", []))
        self.on_item_picked_up(item_id)
        lines = [f"[Inventory] You got: {item['name']}"]
        if item.get("description"):
            lines.append(item["description"])
        return lines

    def remove_actor_item(self, actor: Actor, item_id: str) -> bool:
        """Remove one item while preserving equipment-derived HP invariants."""
        if not actor.remove_item(item_id):
            return False
        max_hp = self.player_max_hp if actor is self.player else self.actor_max_hp(actor)
        actor.health = min(actor.health, max_hp)
        return True

    def remove_actor_items(self, actor: Actor, item_ids: list[str]) -> bool:
        if not actor.has_items(item_ids):
            return False
        for item_id in item_ids:
            self.remove_actor_item(actor, item_id)
        return True

    def use_feature(self, index: int) -> list[str]:
        feature = self.room["features"][index]
        if feature["type"] == "TextFeature":
            return [feature["text"]]
        if not set(feature.get("required_flags", [])) <= self.flags:
            return [feature.get("blocked_text", "Nothing happens.")]
        once_flag = feature.get("once_flag")
        if once_flag and once_flag in self.flags:
            repeat = feature.get("repeat_effect")
            return apply_effect(self, repeat) if repeat else ["Nothing more happens."]
        lines = apply_effect(self, feature.get("first_effect"))
        if once_flag:
            self.flags.add(once_flag)
        elif feature.get("repeat_effect") and not self.over:
            lines.extend(apply_effect(self, feature["repeat_effect"]))
        return lines

    def simple_choice_available(self, spec: dict[str, Any]) -> bool:
        if not set(spec.get("requires_flags", [])) <= self.flags:
            return False
        if set(spec.get("blocked_flags", [])) & self.flags:
            return False
        once_flag = spec.get("once_flag")
        return not once_flag or once_flag not in self.flags

    def apply_simple_choice(self, spec: dict[str, Any]) -> list[str]:
        """Apply a beginner-friendly room choice record.

        Minimal useful example::

            {"text": "Look under the bunk", "result": ["You find a note."]}

        Optional keys include ``go``, ``give_items``, ``set_flags``,
        ``requires_flags``, ``blocked_flags``, and ``once_flag``.
        """
        lines = list(spec.get("result", []))
        for item_id in spec.get("give_items", []):
            lines.extend(self.give_player_item(item_id))
        self.flags.update(spec.get("set_flags", []))
        if spec.get("once_flag"):
            self.flags.add(spec["once_flag"])
        if spec.get("go"):
            self.player_location = spec["go"]
            self.flags.add(f"visited:{self.player_location}")
            lines.extend(self.on_location_enter())
        return lines

    def apply_inventory(self, action: str) -> list[str]:
        if action == "inventory:back":
            self.mode = "exploration"
            return []
        if action.startswith("equip:"):
            item_id = action.split(":", 1)[1]
            item = self.items[item_id]
            slot = item["slot"]
            previous = self.player.equipment.get(slot)
            self.player.equipment[slot] = item_id
            self.player.health = min(self.player.health, self.player_max_hp)
            if previous:
                return [f"Equipped {item['name']}, replacing {self.item_name(previous)}."]
            return [f"Equipped {item['name']} in {slot} slot."]
        if action.startswith("unequip:"):
            slot = action.split(":", 1)[1]
            current = self.player.equipment[slot]
            self.player.equipment[slot] = None
            self.player.health = min(self.player.health, self.player_max_hp)
            return [f"Unequipped {self.item_name(current)}."]
        if action.startswith("use:"):
            item_id = action.split(":", 1)[1]
            return self.use_consumable(self.player, item_id)
        raise AssertionError(action)

    def consumables(self, actor: Actor) -> list[str]:
        max_hp = self.player_max_hp if actor is self.player else self.actor_max_hp(actor)
        if actor.health >= max_hp:
            return []
        result = []
        seen = set()
        for item_id in actor.inventory:
            if item_id not in seen and self.items[item_id].get("healing", 0) > 0:
                result.append(item_id)
                seen.add(item_id)
        return result

    def use_consumable(self, actor: Actor, item_id: str) -> list[str]:
        if item_id not in actor.inventory:
            return ["Item not in inventory."]
        item = self.items[item_id]
        if item.get("healing", 0) <= 0:
            return [f"{item['name']} is not a healing item."]
        max_hp = self.player_max_hp if actor is self.player else self.actor_max_hp(actor)
        if actor.health >= max_hp:
            return [f"{actor.name} is already at full health."]
        self.remove_actor_item(actor, item_id)
        before = actor.health
        actor.health = min(max_hp, actor.health + item["healing"])
        return [f"Used {item['name']}. Restored {actor.health - before} HP."]

    def actor_max_hp(self, actor: Actor) -> int:
        bonus = sum(self.items[item_id].get("hp_bonus", 0) for item_id in actor.equipment.values() if item_id)
        return actor.max_hp + bonus

    def actor_defense(self, actor: Actor) -> int:
        bonus = sum(self.items[item_id].get("defense_bonus", 0) for item_id in actor.equipment.values() if item_id)
        return actor.defense + bonus

    def actor_attack_range(self, actor: Actor) -> tuple[int, int]:
        bonus = sum(self.items[item_id].get("power_bonus", 0) for item_id in actor.equipment.values() if item_id)
        return actor.attack_min + bonus, actor.attack_max + bonus

    def damage_actor(self, actor: Actor, raw_damage: int) -> int:
        defense = self.player_defense if actor is self.player else self.actor_defense(actor)
        actual = max(1, raw_damage - defense)
        actor.health = max(0, actor.health - actual)
        if actor is self.player and actor.health <= 0:
            self.lost = True
            if not self.ending:
                self.ending = "You collapse from your injuries. The adventure ends here."
        return actual

    def start_combat(self, npc_name: str, *, temporary: dict[str, Any] | None = None) -> None:
        self.current_npc_name = npc_name if temporary is None else None
        self.combat_npc_name = npc_name
        self.combat_temporary = temporary
        self.mode = "combat"
        self.player_defending = False
        self.enemy_defending = False

    def current_combat_spec(self) -> dict[str, Any]:
        return self.combat_temporary if self.combat_temporary is not None else self.npcs[self.combat_npc_name]

    def current_combat_actor(self) -> Actor:
        spec = self.current_combat_spec()
        return self._npc_actor(spec)

    def apply_combat(self, action: str) -> list[str]:
        npc = self.current_combat_spec()
        enemy = self._npc_actor(npc)
        lines: list[str] = []

        if action == "combat:defend":
            self.player_defending = True
            lines.append("You brace for the next attack.")
        elif action.startswith("combat:item:"):
            lines.extend(self.use_consumable(self.player, action.split(":", 2)[2]))
        elif action == "combat:run":
            if self.rng.random() < 0.5:
                if npc.get("surrendered"):
                    npc["hostile"] = False
                self.end_combat()
                return ["You escape successfully!"]
            lines.append("You try to run, but the enemy cuts you off!")
        elif action == "combat:surrender":
            accepted, surrender_lines = self.player_surrender(npc)
            lines.extend(surrender_lines)
            if accepted:
                return lines
        elif action == "combat:attack":
            low, high = self.player_attack_range
            raw = self.rng.randint(low, high)
            if self.enemy_defending:
                raw = max(1, raw // 2)
                self.enemy_defending = False
            actual = self.damage_actor(enemy, raw)
            lines.append(f"You hit {npc['name']} for {actual} damage.")
            surrender_lines = self.maybe_enemy_surrender(npc)
            if surrender_lines is not None:
                lines.extend(surrender_lines)
                return lines
            if enemy.health <= 0:
                lines.extend(self.defeat_current_enemy())
                return lines

        if enemy.health > 0 and npc.get("hostile", True):
            consumables = self.consumables(enemy)
            hp_ratio = enemy.health / max(1, self.actor_max_hp(enemy))
            if consumables and hp_ratio <= 0.35 and self.rng.random() < 0.60:
                lines.extend(f"{npc['name']}: {line}" for line in self.use_consumable(enemy, consumables[0]))
            elif npc.get("aggression", 0) < 35 and self.rng.random() < 0.25:
                self.enemy_defending = True
                lines.append(f"{npc['name']} takes a guarded stance.")
            else:
                low, high = self.actor_attack_range(enemy)
                raw = self.rng.randint(low, high)
                if self.player_defending:
                    raw = max(1, raw // 2)
                    self.player_defending = False
                actual = self.damage_actor(self.player, raw)
                lines.append(f"{npc['name']} hits you for {actual} damage.")
                if self.player.health <= 0:
                    self.end_combat()
        return lines

    def maybe_enemy_surrender(self, npc: dict[str, Any]) -> list[str] | None:
        enemy = self._npc_actor(npc)
        ratio_limit = npc.get("surrender_at_ratio")
        if npc.get("surrendered") or ratio_limit is None or enemy.health <= 0:
            return None
        if enemy.health / max(1, self.actor_max_hp(enemy)) > ratio_limit:
            return None
        npc["surrendered"] = True
        if npc.get("peaceful_after_surrender", True):
            npc["hostile"] = False
        npc["willingness_to_trade"] = max(npc.get("willingness_to_trade", 0), 80)
        npc["trade_offers"].extend(deepcopy(npc.get("surrender_trade_offers", [])))
        self.combat_npc_name = None
        self.combat_temporary = None
        self.player_defending = False
        self.enemy_defending = False
        self.mode = "surrender_decision"
        self.current_npc_name = npc["name"]
        return [f"{npc['name']}: {line}" for line in npc.get("surrender_lines", [])] + [f"{npc['name']} surrenders."]

    def player_surrender(self, npc: dict[str, Any]) -> tuple[bool, list[str]]:
        enemy = self._npc_actor(npc)
        tags = set(npc.get("tags", []))
        accepts = enemy.health > 0 and (bool(tags & {"guard", "law"}) or npc.get("surrendered") or npc.get("aggression", 0) < 90 or npc.get("willingness_to_trade", 0) > 40)
        if not accepts:
            lines = npc.get("surrender_reject_lines") or ["No. This ends here."]
            npc["hostile"] = True
            return False, [f"{npc['name']}: {line}" for line in lines]
        lines = [f"{npc['name']}: {line}" for line in (npc.get("surrender_accept_lines") or ["Drop your guard and back away slowly."])]
        npc["hostile"] = False
        if npc.get("surrender_accept_effect"):
            lines.extend(apply_effect(self, npc["surrender_accept_effect"]))
        else:
            if npc.get("aggression", 0) >= 70:
                if self.player.gold > 0:
                    stolen = min(self.player.gold, max(5, self.player.gold // 2))
                    self.player.gold -= stolen
                    enemy.gold += stolen
                    lines.append(f"{npc['name']} takes {stolen} gold from you.")
                elif self.player.inventory:
                    item_id = self.rng.choice(self.player.inventory)
                    self.remove_actor_item(self.player, item_id)
                    lines.append(f"{npc['name']} takes: {self.item_name(item_id)}")
        self.end_combat()
        return True, lines

    def defeat_current_enemy(self) -> list[str]:
        npc = self.current_combat_spec()
        if self.combat_temporary is not None:
            enemy = self._npc_actor(npc)
            lines = list(npc.get("defeat_lines", []))
            if npc.get("reward_gold"):
                self.player.gold += npc["reward_gold"]
                lines.append(f"You gain {npc['reward_gold']} gold.")
            self.end_combat()
            return lines
        lines = self.defeat_npc(npc["name"])
        self.end_combat(to_npc=bool(npc.get("persistent", True)), npc_name=npc["name"])
        return lines

    def defeat_npc(self, name: str) -> list[str]:
        npc = self.npcs[name]
        if npc.get("defeated"):
            return []
        actor = self._npc_actor(npc)
        npc["defeated"] = True
        npc["hostile"] = False
        actor.health = 0
        lines: list[str] = []
        tags = set(npc.get("tags", []))
        if npc.get("surrendered"):
            self.bounty += 100
            lines.append(f"[Bounty] Killing surrendering {name}: {self.bounty}")
        elif tags & {"guard", "law"}:
            self.bounty += 150
            lines.append(f"[Bounty] Killing guard {name}: {self.bounty}")
        elif npc.get("aggression", 0) < 50:
            self.bounty += 40
            lines.append(f"[Bounty] Killing non-hostile {name}: {self.bounty}")
        lines.extend(npc.get("defeat_lines", []))
        for item_id in npc.get("reward_items", []):
            lines.extend(self.give_player_item(item_id))
        if npc.get("reward_gold", 0):
            self.player.gold += npc["reward_gold"]
            lines.append(f"You gain {npc['reward_gold']} gold.")
        self.flags.update(npc.get("reward_flags", []))
        lines.extend(self.on_npc_defeated(npc))
        return lines

    def end_combat(self, *, to_npc: bool = False, npc_name: str | None = None) -> None:
        self.combat_npc_name = None
        self.combat_temporary = None
        self.player_defending = False
        self.enemy_defending = False
        if to_npc and npc_name:
            self.mode = "npc"
            self.current_npc_name = npc_name
        else:
            self.mode = "exploration"
            self.current_npc_name = None

    def npc_mood(self, npc: dict[str, Any]) -> str:
        if npc.get("defeated"):
            return "defeated"
        if npc.get("surrendered"):
            return "surrendered"
        if npc.get("hostile"):
            return "hostile"
        if npc.get("willingness_to_trade", 0) >= 70:
            return "open to trade"
        if npc.get("aggression", 0) >= 60:
            return "dangerous"
        return "neutral"

    def sync_end_state(self) -> None:
        if "game_won" in self.flags:
            self.won = True
            self.lost = False
            if not self.ending:
                self.ending = "You completed the adventure."
        elif "game_lost" in self.flags:
            self.lost = True
            self.won = False
            if not self.ending:
                self.ending = "The adventure ends here."

    def on_item_picked_up(self, item_id: str) -> None:
        source = self.world.get("source_version")
        if source == "version4.py" and item_id == "star_crystal":
            self.flags.add("has_star_crystal")
        if source == "version8.py":
            if item_id == "grave_core":
                self.flags.add("act3_started")
            if item_id == "payroll_shard":
                self.flags.add("has_payroll_shard")

    def on_npc_defeated(self, npc: dict[str, Any]) -> list[str]:
        if self.world.get("source_version") == "version4.py" and npc["name"] == "Crystal Spider":
            return ["The crystal web tears apart, revealing a safer route through the cave."]
        return []

    def on_location_enter(self) -> list[str]:
        source = self.world.get("source_version")
        lines: list[str] = []
        if source == "version4.py" and self.player_location == "tower_top" and "first_tower_visit" not in self.flags:
            self.flags.add("first_tower_visit")
            lines.append("The air grows brighter and heavier at the same time. Something ancient is waiting here.")
        if source == "version8.py":
            messages = {
                "survey_pad": ("survey_pad_intro", "The survey world is all hard light and harder silence. If there is an artifact here, the company buried it where only desperate people would keep digging."),
                "crash_gully": ("crash_gully_intro", "Your crew is gone. The planet is not. Somewhere out under all this dust is the same buried thing they were willing to strand you over."),
                "vault": ("vault_intro", "The buried chamber is too large to have been built for one drill team or one claim. Whatever this place was, frontier companies only found its grave, not its beginning."),
            }
            if self.player_location in messages:
                flag, text = messages[self.player_location]
                if flag not in self.flags:
                    self.flags.add(flag)
                    lines.append(text)
        return lines

    def try_encounter(self) -> list[str] | None:
        if self.mode != "exploration":
            return None
        lines: list[str] = []
        for rule in self.world.get("encounters", []):
            if self.player_location not in rule["locations"]:
                continue
            if rule.get("once_flag") and rule["once_flag"] in self.flags:
                continue
            if not set(rule.get("required_flags", [])) <= self.flags:
                continue
            if set(rule.get("blocked_flags", [])) & self.flags:
                continue
            if not self.encounter_predicate(rule["name"]):
                continue
            if self.rng.random() > rule["chance"]:
                continue
            encounter_lines, triggered = self.run_encounter_handler(rule["handler"])
            lines.extend(encounter_lines)
            if triggered and rule.get("once_flag"):
                self.flags.add(rule["once_flag"])
            # The original world kept checking later rules when a handler
            # reported a non-consuming event (for example Rafe's radio offer).
            if triggered:
                return lines
        return lines or None

    def encounter_predicate(self, name: str) -> bool:
        if name == "guard_confrontation":
            guard = self.npcs.get("Guard Halwen")
            return self.bounty > 0 and guard is not None and self.npc_is_alive(guard)
        if name == "forest_small_spider":
            return self.player.health > 0
        if name == "service_patrol":
            return self.bounty > 0
        if name == "glass_maw":
            return self.player.health > 0
        return True

    def run_encounter_handler(self, handler: str) -> tuple[list[str], bool]:
        if handler == "handle_guard_confrontation":
            guard = self.npcs.get("Guard Halwen")
            if guard is None or not self.npc_is_alive(guard):
                return [], False
            guard["hostile"] = True
            self.start_combat("Guard Halwen")
            return [f"Guard Halwen: You have a bounty of {self.bounty} gold on your head. Stand down."], True
        if handler == "handle_forest_spider_encounter":
            temp = self.make_temp_npc(
                "Small Spider", 10, 3, 5, 0,
                "A skittering spider drops from a branch, startled by your movement.",
                aggression=80, reward_gold=8,
                defeat_lines=["The small spider curls up and goes still among the leaves."],
            )
            self.start_combat("Small Spider", temporary=temp)
            return ["A small spider drops from the branches and rushes toward you!"], True
        if handler == "handle_station_patrol":
            temp = self.make_temp_npc(
                "Patrol Drone", 18, 4, 7, 1,
                "A station patrol drone skims out of a wall cradle with your heat profile already painted red.",
                aggression=85, reward_gold=6,
                defeat_lines=["The patrol drone tumbles across the deck, sparks bleeding from its lens."],
            )
            self.start_combat("Patrol Drone", temporary=temp)
            return ["A patrol drone finds your trail and sweeps the corridor with a stunner arc."], True
        if handler == "handle_glass_maw":
            temp = self.make_temp_npc(
                "Glass Maw", 20, 5, 8, 1,
                "A low-slung dust predator lunges out from beneath the fused shelves.",
                aggression=90, reward_gold=7,
                defeat_lines=["The glass maw shudders once and slides back into stillness."],
            )
            self.start_combat("Glass Maw", temporary=temp)
            return ["A dust predator erupts from the mineral shelves and cuts off your retreat."], True
        if handler == "handle_rafe_offer":
            self.flags.add("act3_started")
            # The original handler returned False (so exploration could
            # continue) but EncounterRule only set once_flag after True, which
            # made the landing-beacon ending unreachable.  Record the intended
            # one-time signal explicitly while preserving the non-consuming
            # encounter behavior.
            self.flags.add("rafe_offer_heard")
            return ["Rafe's cutter hails you from above the plateau. He knows you made it inside, and now he wants the grave core brought to the landing beacon for payment and extraction."], False
        raise ValueError(handler)

    def make_temp_npc(self, name: str, hp: int, attack_min: int, attack_max: int, defense: int, description: str, *, aggression: int, reward_gold: int, defeat_lines: list[str]) -> dict[str, Any]:
        return {
            "name": name,
            "description": description,
            "base_stats": {"max_hp": hp, "attack_min": attack_min, "attack_max": attack_max, "defense": defense},
            "health": hp,
            "gold": 0,
            "inventory": [],
            "equipment": {"weapon": None, "armor": None, "charm": None},
            "tags": ["encounter"],
            "aggression": aggression,
            "courage": 50,
            "willingness_to_trade": 0,
            "hostile": True,
            "surrender_at_ratio": None,
            "surrender_reject_lines": ["No."],
            "defeat_lines": defeat_lines,
            "reward_gold": reward_gold,
            "persistent": False,
        }
