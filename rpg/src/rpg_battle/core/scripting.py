from __future__ import annotations

"""Small, read-only scripting vocabulary for student-authored move logic.

Custom move functions receive a :class:`MoveContext` and return one or more
commands.  The function can use ordinary Python control flow to decide what a
move should do, while the engine remains responsible for mutating battle state,
producing combat events, handling knockouts, and drawing animations.
"""

from dataclasses import dataclass
from typing import Literal, TypeAlias

from rpg_battle.core.models import BattleState, CombatantState

CommandTarget = Literal["targets", "user"]


@dataclass(frozen=True)
class BattlerView:
    """Read-only facts about a combatant exposed to student scripts."""

    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    magic: int
    speed: int
    statuses: frozenset[str]

    @property
    def hp_ratio(self) -> float:
        if self.max_hp <= 0:
            return 0.0
        return self.hp / self.max_hp


@dataclass(frozen=True)
class MoveContext:
    """Facts a custom move function may inspect when choosing its effects."""

    user: BattlerView
    targets: tuple[BattlerView, ...]
    round_number: int

    @property
    def target(self) -> BattlerView | None:
        """Convenience accessor for the first target, if the move has one."""

        return self.targets[0] if self.targets else None


@dataclass(frozen=True)
class Damage:
    """Deal normal engine-calculated damage using ``power``."""

    power: int
    magical: bool = False
    target: CommandTarget = "targets"


@dataclass(frozen=True)
class Heal:
    """Restore HP using the normal healing formula."""

    power: int
    target: CommandTarget = "targets"


@dataclass(frozen=True)
class AddStatus:
    """Apply a named status for a number of rounds."""

    name: str
    duration: int
    chance: float = 1.0
    target: CommandTarget = "targets"


@dataclass(frozen=True)
class ChangeStat:
    """Raise or lower one temporary combat stat."""

    stat: str
    stages: int
    chance: float = 1.0
    target: CommandTarget = "targets"


MoveCommand: TypeAlias = Damage | Heal | AddStatus | ChangeStat
MoveScriptResult: TypeAlias = MoveCommand | list[MoveCommand] | tuple[MoveCommand, ...] | None


def _view(combatant: CombatantState) -> BattlerView:
    return BattlerView(
        name=combatant.spec.name,
        hp=combatant.current_hp,
        max_hp=combatant.spec.max_hp,
        attack=combatant.spec.attack,
        defense=combatant.spec.defense,
        magic=combatant.spec.magic,
        speed=combatant.spec.speed,
        statuses=frozenset(combatant.statuses),
    )


def build_move_context(
    state: BattleState,
    actor_id: str,
    target_ids: tuple[str, ...],
) -> MoveContext:
    """Create the immutable view passed to a student-authored move function."""

    actor = state.combatants[actor_id]
    targets = tuple(state.combatants[target_id] for target_id in target_ids)
    return MoveContext(
        user=_view(actor),
        targets=tuple(_view(target) for target in targets),
        round_number=state.round_number,
    )


def normalize_commands(result: MoveScriptResult) -> tuple[MoveCommand, ...]:
    """Normalize the convenient script return forms into a tuple."""

    if result is None:
        return ()
    if isinstance(result, (Damage, Heal, AddStatus, ChangeStat)):
        return (result,)
    return tuple(result)
