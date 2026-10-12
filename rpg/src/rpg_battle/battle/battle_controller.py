from __future__ import annotations

"""Legacy UI conveniences; battle progression lives in :mod:`battle.session`.

New game modes should use ``BattleSession`` and ``DecisionRequest`` directly.
This thin adapter preserves the older workshop/controller API without keeping
another independent turn driver or a second implementation of substitutions.
"""

from rpg_battle.battle.session import BattleSession
from rpg_battle.core.ai import choose_ai_action, choose_ai_replacement
from rpg_battle.core.models import BattleAction


class BattleController(BattleSession):
    """Backwards-compatible facade over the authoritative ``BattleSession``."""

    def player_can_act(self) -> bool:
        request = self.request
        return request is not None and request.kind == "action" and request.team_index == 0

    def enemy_should_act(self) -> bool:
        request = self.request
        return request is not None and request.kind == "action" and request.team_index == 1

    def player_needs_replacement(self) -> bool:
        request = self.request
        return request is not None and request.kind == "replacement" and request.team_index == 0

    def player_replacement_targets(self) -> list[str]:
        request = self.request
        return list(request.choices) if self.player_needs_replacement() else []

    def resolve_player_replacement(self, combatant_id: str) -> list[dict]:
        if not self.player_needs_replacement():
            raise ValueError("No player replacement is pending")
        return self.submit_replacement(combatant_id)

    def advance_to_next_turn(self) -> list[dict]:
        request = self.request
        if request is not None and request.kind == "replacement" and request.team_index == 1:
            choice = choose_ai_replacement(self.state, request.team_index)
            if choice is None:
                return []
            return self.submit_replacement(choice)
        return list(self.next_step().events)

    def resolve_current_player_action(self, action: BattleAction) -> list[dict]:
        return self.submit_action(action) if self.player_can_act() else []

    def resolve_current_enemy_action(self) -> list[dict]:
        if not self.enemy_should_act() or self.current_actor_id is None:
            return []
        action = choose_ai_action(self.state, self.current_actor_id, self.rng)
        return self.submit_action(action)
