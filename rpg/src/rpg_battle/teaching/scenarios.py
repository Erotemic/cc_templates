from __future__ import annotations

"""Reusable teaching-scenario data without any shipped-game content ids."""

from dataclasses import dataclass
from typing import Literal

from rpg_battle.core.models import BattleState, StatusState


@dataclass(frozen=True)
class TeachingScenario:
    """A deliberate starting state for one programming investigation.

    The engine owns this generic data structure. Individual games define their
    named scenarios in ``student_game/scenarios.py`` using their own ids.
    """

    scenario_id: str
    title: str
    description: str
    encounter_id: str
    inspect_mode: Literal["move", "strategy", "simulation"] = "move"
    strategy_team_index: int = 1
    seed: int = 5
    move_id: str | None = None
    user_char_id: str | None = None
    target_char_ids: tuple[str, ...] = ()
    user_hp: int | None = None
    target_hp: int | None = None
    target_statuses: tuple[str, ...] = ()
    hp_by_character: tuple[tuple[str, int], ...] = ()
    statuses_by_character: tuple[tuple[str, tuple[str, ...]], ...] = ()

    def apply_to_state(self, state: BattleState) -> None:
        """Apply the scenario's HP/status setup to a freshly built battle."""

        hp_lookup = dict(self.hp_by_character)
        status_lookup = dict(self.statuses_by_character)
        for combatant in state.combatants.values():
            char_id = combatant.spec.char_id
            if char_id in hp_lookup:
                combatant.current_hp = max(
                    1,
                    min(hp_lookup[char_id], combatant.spec.max_hp),
                )
            for status_name in status_lookup.get(char_id, ()):
                combatant.statuses[status_name] = StatusState(status_name, 3)
