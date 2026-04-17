from __future__ import annotations

from rpg_battle.core.models import CombatantState


def effective_stat(battler: CombatantState, stat_name: str) -> int:
    base = getattr(battler.spec, stat_name)
    bonus = battler.temp_bonuses.get(stat_name, 0)
    value = max(1, base + bonus * 2)
    if stat_name == "attack" and "burn" in battler.statuses:
        value = max(1, int(value * 0.8))
    if stat_name == "speed" and "slow" in battler.statuses:
        value = max(1, int(value * 0.75))
    if stat_name == "magic" and "focus" in battler.statuses:
        value = max(1, int(value * 1.25))
    if stat_name == "defense" and "guarded" in battler.statuses:
        value = max(1, int(value * 1.25))
    return value
