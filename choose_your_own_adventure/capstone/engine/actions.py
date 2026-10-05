"""Interpret the scripted outcomes preserved from the original games.

Most students do not need to edit this file.  Simple new rooms and choices can
be authored entirely in a world file.  This interpreter exists so the original
Star Crystal and Dust Vault stories can keep their more elaborate outcomes
without reintroducing a class hierarchy for every possible effect.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .game import AdventureGame


def apply_effect(game: "AdventureGame", effect: dict[str, Any] | None) -> list[str]:
    if effect is None:
        return []

    kind = effect["type"]
    lines: list[str] = []

    if kind == "PrintEffect":
        return list(effect["lines"])

    if kind == "SetFlagEffect":
        game.flags.update(effect["flags"])
        game.sync_end_state()
        return []

    if kind == "ClearFlagEffect":
        for flag in effect["flags"]:
            game.flags.discard(flag)
        return []

    if kind == "SetBountyEffect":
        game.bounty = max(0, effect["amount"])
        return [f"[Bounty] Set to {game.bounty}"]

    if kind == "ChangeBountyEffect":
        game.bounty = max(0, game.bounty + effect["amount"])
        if effect.get("reason"):
            return [f"[Bounty] {effect['reason']}: {game.bounty}"]
        return [f"[Bounty] {game.bounty}"]

    if kind == "HealPlayerEffect":
        if game.player.health >= game.player_max_hp:
            return [effect["full_text"]]
        before = game.player.health
        game.player.health = min(game.player_max_hp, game.player.health + effect["amount"])
        healed = game.player.health - before
        return [effect["heal_text"], f"Recovered {healed} health."]

    if kind == "GivePlayerItemEffect":
        for item_id in effect["item_ids"]:
            lines.extend(game.give_player_item(item_id))
        return lines

    if kind == "ChangeGoldEffect":
        target = effect.get("target", "player")
        actor = game.player if target == "player" else game.find_npc(target)
        if actor is None:
            return []
        actor.gold = max(0, actor.gold + effect["amount"])
        if effect.get("reason"):
            lines.append(effect["reason"])
        elif target == "player" and effect["amount"] > 0:
            lines.append(f"You gain {effect['amount']} gold.")
        elif target == "player" and effect["amount"] < 0:
            lines.append(f"You lose {-effect['amount']} gold.")
        lines.append(f"[Gold] {actor.name} now has {actor.gold} gold")
        return lines

    if kind == "RemoveItemEffect":
        target = effect.get("target", "player")
        actor = game.player if target == "player" else game.find_npc(target)
        if actor is not None and actor.remove_item(effect["item_id"]) and effect.get("text"):
            return [effect["text"]]
        return []

    if kind == "DamageCharacterEffect":
        target = effect["target"]
        actor = game.player if target == "player" else game.find_npc(target)
        if actor is None:
            return []
        if effect.get("text"):
            lines.append(effect["text"])
        actual = game.damage_actor(actor, effect["amount"])
        lines.append(f"{actor.name} takes {actual} damage.")
        if actor is not game.player and actor.health <= 0:
            lines.extend(game.defeat_npc(target))
        return lines

    if kind == "MovePlayerEffect":
        if effect.get("text"):
            lines.append(effect["text"])
        game.player_location = effect["destination"]
        game.flags.add(f"visited:{game.player_location}")
        lines.extend(game.on_location_enter())
        encounter = game.try_encounter()
        if encounter is not None:
            lines.extend(encounter)
        return lines

    if kind == "BlockPathEffect":
        game.set_exit_blocked(effect["location_key"], effect["direction"], True, effect["reason"])
        return []

    if kind == "UnblockPathEffect":
        game.set_exit_blocked(effect["location_key"], effect["direction"], False, None)
        return []

    if kind == "ConditionalEffect":
        ok = set(effect["required_flags"]) <= game.flags
        ok = ok and not (set(effect["blocked_flags"]) & game.flags)
        ok = ok and game.player.has_items(effect["required_items"])
        branch = effect["success_effect"] if ok else effect.get("failure_effect")
        return apply_effect(game, branch)

    if kind == "ChanceEffect":
        branch = effect["success_effect"] if game.rng.random() < effect["chance"] else effect.get("failure_effect")
        return apply_effect(game, branch)

    if kind == "CompositeEffect":
        for child in effect["effects"]:
            lines.extend(apply_effect(game, child))
            if game.over:
                break
        return lines

    if kind == "EndGameEffect":
        lines.extend(effect["lines"])
        game.flags.update(effect["flags"])
        game.sync_end_state()
        if "game_won" in game.flags:
            game.ending = " ".join(effect["lines"])
        return lines

    if kind == "BranchOnBountyEffect":
        branch = effect["clean_effect"] if game.bounty <= effect["threshold"] else effect["hot_effect"]
        return apply_effect(game, branch)

    raise ValueError(f"Unsupported effect type: {kind}")
