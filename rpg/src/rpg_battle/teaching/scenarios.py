from __future__ import annotations

"""Reusable teaching-scenario data without any shipped-game content ids."""

from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING

from rpg_battle.core.models import BattleState, StatusState

if TYPE_CHECKING:
    from rpg_battle.catalog import GameContent


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
    hp_by_character: tuple[tuple[str, int], ...] = ()
    statuses_by_character: tuple[tuple[str, tuple[str, ...]], ...] = ()

    def apply_to_state(self, state: BattleState) -> None:
        """Apply the scenario's HP/status setup to a freshly built battle."""

        hp_lookup = dict(self.hp_by_character)
        status_lookup = dict(self.statuses_by_character)
        characters = {combatant.spec.char_id: combatant.spec for combatant in state.combatants.values()}
        unknown = (hp_lookup.keys() | status_lookup.keys()) - characters.keys()
        if unknown:
            raise ValueError(f"unknown setup character(s): {', '.join(sorted(unknown))}")
        for char_id, hp in hp_lookup.items():
            if not isinstance(hp, int) or isinstance(hp, bool) or not 1 <= hp <= characters[char_id].max_hp:
                raise ValueError(f"{char_id}: starting HP must be an integer from 1 to {characters[char_id].max_hp}")
        for names in status_lookup.values():
            if any(not isinstance(name, str) or not name.strip() for name in names):
                raise ValueError("status names must be nonempty strings")
        for combatant in state.combatants.values():
            char_id = combatant.spec.char_id
            if char_id in hp_lookup:
                combatant.current_hp = hp_lookup[char_id]
            for status_name in status_lookup.get(char_id, ()):
                combatant.statuses[status_name] = StatusState(status_name, 3)

    def validate(self, content: GameContent) -> list[str]:
        """Check the lesson setup without calling any student behavior."""

        from rpg_battle.core.battle_state import new_battle
        from rpg_battle.core.targeting import get_valid_target_groups

        if self.inspect_mode not in {"move", "strategy", "simulation"}:
            return [f"unknown inspection mode {self.inspect_mode!r}"]
        if self.encounter_id not in content.encounters:
            return [f"unknown encounter {self.encounter_id!r}"]
        state = new_battle(content.encounters[self.encounter_id], content=content)
        try:
            self.apply_to_state(state)
        except ValueError as exc:
            return [str(exc)]
        if self.inspect_mode == "strategy":
            if not isinstance(self.strategy_team_index, int) or self.strategy_team_index not in {0, 1}:
                return ["strategy team index must be 0 or 1"]
        elif self.inspect_mode == "move":
            if self.move_id not in content.moves:
                return [f"unknown move {self.move_id!r}"]
            actor_id = next(
                (cid for cid in state.teams[0].active_ids
                 if state.combatants[cid].spec.char_id == self.user_char_id),
                None,
            )
            if actor_id is None:
                return [f"move user {self.user_char_id!r} is not active on the player team"]
            if self.move_id not in state.combatants[actor_id].spec.move_ids:
                return [f"{self.user_char_id!r} does not know move {self.move_id!r}"]
            groups = get_valid_target_groups(state, actor_id, content.moves[self.move_id].target_mode)
            if not (not self.target_char_ids and len(groups) == 1) and not any(
                tuple(state.combatants[cid].spec.char_id for cid in group) == self.target_char_ids
                for group in groups
            ):
                return [f"illegal targets {self.target_char_ids!r} for move {self.move_id!r}"]
        return []
