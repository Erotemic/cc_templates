from __future__ import annotations

"""Per-fighter mana, shared by human, AI, and scripted actions.

Attack recovers a little mana, Defend recovers more. Skills spend their
specified cost, even when the resulting move misses. There is no passive
regeneration, and switching preserves each fighter's remaining mana.
"""

from rpg_battle.core.models import CombatantState

ATTACK_MANA_RECOVERY = 3
DEFEND_MANA_RECOVERY = 7


def change_mana(
    actor: CombatantState, amount: int, events: list[dict], *, source: str
) -> int:
    """Apply a bounded mana change and emit an exact state-delta event."""
    before = actor.current_mana
    after = max(0, min(actor.spec.max_mana, before + amount))
    actor.current_mana = after
    delta = after - before
    if delta:
        action = "spends" if delta < 0 else "recovers"
        events.append({
            "type": "mana", "team": actor.team_index,
            "actor_id": actor.combatant_id, "actor_name": actor.spec.name,
            "mana_before": before, "mana_after": after, "amount": delta,
            "source": source,
            "text": f"{actor.spec.name} {action} {abs(delta)} MP ({source}).",
        })
    return delta
