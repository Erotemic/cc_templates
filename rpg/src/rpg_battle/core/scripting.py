from __future__ import annotations

"""Small, read-only scripting vocabulary for student-authored game logic.

Custom move functions and AI strategies receive immutable views of battle state.
They return small command objects instead of mutating the engine directly.  That
keeps ordinary Python control flow front-and-center while the engine remains
responsible for state changes, event generation, knockouts, and presentation.
"""

from dataclasses import dataclass, field
from typing import Callable, Literal, Protocol, TypeAlias

from rpg_battle.core.models import BattleState, CombatantState


class MoveLike(Protocol):
    """Structural type for the public ``Move`` object used by AI strategies."""

    @property
    def move_id(self) -> str: ...


@dataclass(frozen=True)
class BattlerView:
    """Read-only facts about a combatant exposed to student scripts.

    A view can also be passed back as a command target.  The private id is an
    opaque engine handle; students can reason about the visible facts without
    receiving the mutable ``CombatantState`` object.
    """

    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    magic: int
    speed: int
    statuses: frozenset[str]
    _combatant_id: str = field(repr=False, compare=False)

    @property
    def hp_ratio(self) -> float:
        if self.max_hp <= 0:
            return 0.0
        return self.hp / self.max_hp


CommandTarget: TypeAlias = Literal["targets", "user"] | BattlerView


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


@dataclass(frozen=True)
class UseMove:
    """AI strategy decision to use one known move."""

    move_id: str
    target: BattlerView | tuple[BattlerView, ...] | Literal["auto"] = "auto"


@dataclass(frozen=True)
class Defend:
    """AI strategy decision to defend for this turn."""


AIStrategyResult: TypeAlias = UseMove | Defend


@dataclass(frozen=True)
class TurnContext:
    """Read-only facts available to a student-authored enemy strategy."""

    user: BattlerView
    allies: tuple[BattlerView, ...]
    enemies: tuple[BattlerView, ...]
    available_move_ids: frozenset[str]
    round_number: int

    def use(
        self,
        move: MoveLike | str,
        *,
        target: BattlerView | tuple[BattlerView, ...] | None = None,
    ) -> UseMove:
        """Choose a move, optionally naming its target view(s)."""

        move_id = move if isinstance(move, str) else move.move_id
        if move_id not in self.available_move_ids:
            raise ValueError(f"{self.user.name} does not know the move {move_id!r}")
        return UseMove(move_id=move_id, target="auto" if target is None else target)

    def defend(self) -> Defend:
        """Choose the defend action."""

        return Defend()


AIStrategy: TypeAlias = Callable[[TurnContext], AIStrategyResult]


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
        _combatant_id=combatant.combatant_id,
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


def build_turn_context(state: BattleState, actor_id: str) -> TurnContext:
    """Create the immutable view passed to a student-authored AI strategy."""

    actor = state.combatants[actor_id]
    team = state.teams[actor.team_index]
    allies = tuple(
        _view(state.combatants[cid])
        for cid in team.active_ids
        if cid != actor_id and state.combatants[cid].alive
    )
    enemies = tuple(
        _view(state.combatants[cid])
        for index, other_team in enumerate(state.teams)
        if index != actor.team_index
        for cid in other_team.active_ids
        if state.combatants[cid].alive
    )
    return TurnContext(
        user=_view(actor),
        allies=allies,
        enemies=enemies,
        available_move_ids=frozenset(actor.spec.move_ids),
        round_number=state.round_number,
    )


def normalize_commands(result: MoveScriptResult) -> tuple[MoveCommand, ...]:
    """Normalize convenient script return forms and reject confusing mistakes."""

    command_types = (Damage, Heal, AddStatus, ChangeStat)
    if result is None:
        return ()
    if isinstance(result, command_types):
        return (result,)
    if not isinstance(result, (list, tuple)):
        raise TypeError(
            "move functions must return a move command, a list/tuple of move "
            f"commands, or None; received {type(result).__name__}"
        )
    commands = tuple(result)
    for index, command in enumerate(commands):
        if not isinstance(command, command_types):
            raise TypeError(
                f"move command #{index + 1} has type {type(command).__name__}; "
                "use damage(), heal(), add_status(), or change_stat()"
            )
    return commands


def command_target_id(target: CommandTarget) -> str | None:
    """Return an opaque combatant id when a command names one specific view."""

    if isinstance(target, BattlerView):
        return target._combatant_id
    return None


def validate_script_commands(
    commands: tuple[MoveCommand, ...],
    context: MoveContext,
) -> list[str]:
    """Return student-facing structural problems from one script execution."""

    problems: list[str] = []
    valid_target_ids = {
        context.user._combatant_id,
        *(view._combatant_id for view in context.targets),
    }
    for index, command in enumerate(commands, start=1):
        prefix = f"command {index}"
        if isinstance(command, (Damage, Heal)) and command.power < 0:
            problems.append(f"{prefix}: power cannot be negative")
        if isinstance(command, AddStatus):
            if command.duration <= 0:
                problems.append(f"{prefix}: status duration must be positive")
            if not 0.0 <= command.chance <= 1.0:
                problems.append(f"{prefix}: chance must be between 0.0 and 1.0")
        if isinstance(command, ChangeStat):
            if command.stat not in {"attack", "defense", "magic", "speed"}:
                problems.append(f"{prefix}: unknown stat {command.stat!r}")
            if not 0.0 <= command.chance <= 1.0:
                problems.append(f"{prefix}: chance must be between 0.0 and 1.0")
        target_id = command_target_id(command.target)
        if target_id is not None and target_id not in valid_target_ids:
            problems.append(f"{prefix}: target does not belong to this move context")
    return problems



def smoke_test_ai_strategy(
    strategy: AIStrategy,
    *,
    user_name: str,
    available_move_ids: frozenset[str],
) -> list[str]:
    """Exercise a student AI strategy in high- and low-health scenarios."""

    contexts = [
        TurnContext(
            user=BattlerView(
                user_name, 50, 50, 9, 7, 8, 6, frozenset(), "strategy_user"
            ),
            allies=(),
            enemies=(
                BattlerView(
                    "Practice Enemy A", 40, 40, 7, 6, 5, 5, frozenset(), "strategy_a"
                ),
                BattlerView(
                    "Practice Enemy B", 15, 40, 7, 6, 5, 5, frozenset({"burn"}), "strategy_b"
                ),
            ),
            available_move_ids=available_move_ids,
            round_number=1,
        ),
        TurnContext(
            user=BattlerView(
                user_name, 8, 50, 9, 7, 8, 6, frozenset(), "strategy_user"
            ),
            allies=(),
            enemies=(
                BattlerView(
                    "Practice Enemy A", 12, 40, 7, 6, 5, 5, frozenset(), "strategy_a"
                ),
            ),
            available_move_ids=available_move_ids,
            round_number=4,
        ),
    ]
    problems: list[str] = []
    for scenario_index, context in enumerate(contexts, start=1):
        try:
            decision = strategy(context)
            if not isinstance(decision, (UseMove, Defend)):
                problems.append(
                    f"scenario {scenario_index}: strategy must return "
                    f"turn.use(...) or turn.defend(); received {type(decision).__name__}"
                )
                continue
            if isinstance(decision, UseMove) and decision.move_id not in available_move_ids:
                problems.append(
                    f"scenario {scenario_index}: chose unknown move {decision.move_id!r}"
                )
        except Exception as exc:
            problems.append(
                f"scenario {scenario_index}: {type(exc).__name__}: {exc}"
            )
    return problems

def script_source_label(script: object) -> str:
    """Return a compact file:line label for a student-authored function."""

    import inspect

    try:
        filename = inspect.getsourcefile(script) or inspect.getfile(script)
        _, line = inspect.getsourcelines(script)
    except (OSError, TypeError):
        return getattr(script, "__name__", "custom function")
    from pathlib import Path

    path = Path(filename)
    try:
        # Classroom reports are easier to read without an absolute home path.
        parts = path.parts
        marker = parts.index("student_game")
        short = Path(*parts[marker:])
    except ValueError:
        short = path
    return f"{short}:{line}"


def smoke_test_move_script(script: object) -> list[str]:
    """Exercise a custom move function against a few deterministic read-only contexts."""

    contexts = [
        MoveContext(
            user=BattlerView(
                "Practice Hero", 50, 50, 10, 8, 7, 6, frozenset(), "practice_user"
            ),
            targets=(
                BattlerView(
                    "Practice Target A", 40, 40, 7, 6, 5, 4, frozenset(), "practice_a"
                ),
                BattlerView(
                    "Practice Target B", 18, 40, 7, 6, 5, 4, frozenset({"burn"}), "practice_b"
                ),
            ),
            round_number=1,
        ),
        MoveContext(
            user=BattlerView(
                "Practice Hero", 12, 50, 10, 8, 7, 6, frozenset({"burn"}), "practice_user"
            ),
            targets=(
                BattlerView(
                    "Practice Target A", 12, 40, 7, 6, 5, 4, frozenset(), "practice_a"
                ),
            ),
            round_number=4,
        ),
    ]
    problems: list[str] = []
    for scenario_index, context in enumerate(contexts, start=1):
        try:
            result = script(context)  # type: ignore[operator]
            commands = normalize_commands(result)
            for problem in validate_script_commands(commands, context):
                problems.append(f"scenario {scenario_index}: {problem}")
        except Exception as exc:  # student code should become a validation report
            problems.append(
                f"scenario {scenario_index}: {type(exc).__name__}: {exc}"
            )
    return problems
