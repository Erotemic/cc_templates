from __future__ import annotations

"""Small, read-only scripting vocabulary for student-authored game logic.

Custom move functions and AI strategies receive immutable views of battle state.
They return small command objects instead of mutating the engine directly. That
keeps ordinary Python control flow front-and-center while the engine remains
responsible for state changes, event generation, knockouts, and presentation.
"""

from dataclasses import dataclass, field, replace
from typing import Callable, Literal, Protocol, TypeAlias

from rpg_battle.core.effects import effective_stat
from rpg_battle.core.models import BattleState, CombatantState, TargetMode


class StudentCodeError(RuntimeError):
    """Concise error raised when student-authored behavior fails at runtime."""


class MoveLike(Protocol):
    """Structural type for the public ``Move`` object used by AI strategies."""

    @property
    def move_id(self) -> str: ...


@dataclass(frozen=True)
class BattlerView:
    """Read-only facts about a combatant exposed to student scripts.

    ``attack``, ``defense``, ``magic``, and ``speed`` are the *effective* values
    the rules engine will use right now, after temporary stages and statuses.
    The corresponding ``base_*`` fields expose the character-sheet values for
    lessons that need to compare base and effective statistics.

    A view can also be passed back as a command target. The private id is an
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
    base_attack: int | None = None
    base_defense: int | None = None
    base_magic: int | None = None
    base_speed: int | None = None

    def __post_init__(self) -> None:
        # Synthetic teaching views may only supply the effective values. In that
        # case the same values are also the best available base-stat description.
        if self.base_attack is None:
            object.__setattr__(self, "base_attack", self.attack)
        if self.base_defense is None:
            object.__setattr__(self, "base_defense", self.defense)
        if self.base_magic is None:
            object.__setattr__(self, "base_magic", self.magic)
        if self.base_speed is None:
            object.__setattr__(self, "base_speed", self.speed)

    @property
    def hp_ratio(self) -> float:
        if self.max_hp <= 0:
            return 0.0
        return self.hp / self.max_hp

    @property
    def effective_attack(self) -> int:
        return self.attack

    @property
    def effective_defense(self) -> int:
        return self.defense

    @property
    def effective_magic(self) -> int:
        return self.magic

    @property
    def effective_speed(self) -> int:
        return self.speed


CommandTarget: TypeAlias = Literal["targets", "user"] | BattlerView
VALID_COMMAND_TARGET_NAMES = frozenset({"targets", "user"})


@dataclass(frozen=True)
class MoveContext:
    """Facts a custom move function may inspect when choosing its effects."""

    user: BattlerView
    targets: tuple[BattlerView, ...]
    round_number: int
    _observer: Callable[[str, object], None] | None = field(
        default=None, repr=False, compare=False
    )

    @property
    def target(self) -> BattlerView | None:
        """Convenience accessor for the first target, if the move has one."""

        return self.targets[0] if self.targets else None

    def observe(self, label: str, value: object) -> object:
        """Record one value in teaching traces and return it unchanged.

        This is optional. A move works the same without ``observe``. It is handy
        when a lesson wants the lab to show the exact boolean a branch used.
        """

        if self._observer is not None:
            self._observer(label, value)
        return value


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
        attack=effective_stat(combatant, "attack"),
        defense=effective_stat(combatant, "defense"),
        magic=effective_stat(combatant, "magic"),
        speed=effective_stat(combatant, "speed"),
        statuses=frozenset(combatant.statuses),
        _combatant_id=combatant.combatant_id,
        base_attack=combatant.spec.attack,
        base_defense=combatant.spec.defense,
        base_magic=combatant.spec.magic,
        base_speed=combatant.spec.speed,
    )


def build_move_context(
    state: BattleState,
    actor_id: str,
    target_ids: tuple[str, ...],
    *,
    observer: Callable[[str, object], None] | None = None,
) -> MoveContext:
    """Create the immutable view passed to a student-authored move function."""

    actor = state.combatants[actor_id]
    targets = tuple(state.combatants[target_id] for target_id in target_ids)
    return MoveContext(
        user=_view(actor),
        targets=tuple(_view(target) for target in targets),
        round_number=state.round_number,
        _observer=observer,
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
        target = command.target
        if isinstance(target, str) and target not in VALID_COMMAND_TARGET_NAMES:
            problems.append(
                f"{prefix}: unknown target {target!r}; use 'user', 'targets', "
                "or a BattlerView from ctx.targets"
            )
            continue
        target_id = command_target_id(target)
        if target_id is not None and target_id not in valid_target_ids:
            problems.append(f"{prefix}: target does not belong to this move context")
    return problems


def _target_ids_from_ai_decision(
    target: BattlerView | tuple[BattlerView, ...] | Literal["auto"],
) -> tuple[str, ...] | Literal["auto"]:
    if target == "auto":
        return "auto"
    if isinstance(target, BattlerView):
        return (target._combatant_id,)
    return tuple(view._combatant_id for view in target)


def _legal_synthetic_ai_targets(
    context: TurnContext,
    target_mode: TargetMode,
) -> set[tuple[str, ...]]:
    user_id = context.user._combatant_id
    ally_ids = [ally._combatant_id for ally in context.allies]
    enemy_ids = [enemy._combatant_id for enemy in context.enemies]
    if target_mode == "self":
        return {(user_id,)}
    if target_mode == "single_enemy":
        return {(target_id,) for target_id in enemy_ids}
    if target_mode == "single_ally":
        return {(target_id,) for target_id in [user_id, *ally_ids]}
    if target_mode == "all_enemies":
        return {tuple(enemy_ids)} if enemy_ids else set()
    if target_mode == "all_allies":
        return {(user_id, *ally_ids)}
    if target_mode == "none":
        return {()}
    return set()


def smoke_test_ai_strategy(
    strategy: AIStrategy,
    *,
    user_name: str,
    available_move_ids: frozenset[str],
    move_target_modes: dict[str, TargetMode] | None = None,
    user: BattlerView | None = None,
    allies: tuple[BattlerView, ...] | None = None,
    enemies: tuple[BattlerView, ...] | None = None,
) -> list[str]:
    """Exercise a student AI strategy in high- and low-health scenarios.

    The game validator supplies views built from the authored characters so a
    strategy sees realistic HP/stat ranges instead of unrelated magic numbers.
    Synthetic views remain as a compatibility fallback for direct callers.
    """

    healthy_user = user or BattlerView(
        user_name, 50, 50, 9, 7, 8, 6, frozenset(), "strategy_user"
    )
    healthy_user = replace(healthy_user, hp=healthy_user.max_hp, statuses=frozenset())
    low_user = replace(
        healthy_user,
        hp=max(1, healthy_user.max_hp // 4),
        statuses=frozenset({"burn"}),
    )

    if allies is None:
        allies = (
            BattlerView(
                "Practice Ally", 22, 50, 7, 8, 6, 5, frozenset(), "strategy_ally"
            ),
        )
    if enemies is None:
        enemies = (
            BattlerView(
                "Practice Enemy A", 40, 40, 7, 6, 5, 5, frozenset(), "strategy_a"
            ),
            BattlerView(
                "Practice Enemy B",
                15,
                40,
                7,
                6,
                5,
                5,
                frozenset({"burn"}),
                "strategy_b",
            ),
        )

    high_enemies = tuple(
        replace(enemy, hp=enemy.max_hp, statuses=frozenset()) for enemy in enemies
    )
    low_enemies = tuple(
        replace(
            enemy,
            hp=max(1, enemy.max_hp // (2 + index)),
            statuses=frozenset({"burn"}) if index == 1 else frozenset(),
        )
        for index, enemy in enumerate(enemies)
    )
    contexts = [
        TurnContext(
            user=healthy_user,
            allies=allies,
            enemies=high_enemies,
            available_move_ids=available_move_ids,
            round_number=1,
        ),
        TurnContext(
            user=low_user,
            allies=allies,
            enemies=low_enemies,
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
            if isinstance(decision, UseMove):
                if decision.move_id not in available_move_ids:
                    problems.append(
                        f"scenario {scenario_index}: chose unknown move {decision.move_id!r}"
                    )
                    continue
                if move_target_modes is not None and decision.move_id in move_target_modes:
                    target_ids = _target_ids_from_ai_decision(decision.target)
                    if target_ids != "auto":
                        legal = _legal_synthetic_ai_targets(
                            context, move_target_modes[decision.move_id]
                        )
                        if target_ids not in legal:
                            problems.append(
                                f"scenario {scenario_index}: chose an invalid target for "
                                f"move {decision.move_id!r}"
                            )
        except Exception as exc:
            problems.append(f"scenario {scenario_index}: {type(exc).__name__}: {exc}")
    return problems


def script_source_label(script: object) -> str:
    """Return a compact file:line label for a student-authored function."""

    import inspect
    from pathlib import Path

    try:
        filename = inspect.getsourcefile(script) or inspect.getfile(script)
        _, line = inspect.getsourcelines(script)
    except (OSError, TypeError):
        return getattr(script, "__name__", "custom function")

    path = Path(filename)
    try:
        # Classroom reports are easier to read without an absolute home path.
        parts = path.parts
        marker = parts.index("student_game")
        short = Path(*parts[marker:])
    except ValueError:
        short = path
    return f"{short}:{line}"


def _synthetic_targets_for_mode(target_mode: TargetMode) -> tuple[BattlerView, ...]:
    target_a = BattlerView(
        "Practice Target A", 40, 40, 7, 6, 5, 4, frozenset(), "practice_a"
    )
    target_b = BattlerView(
        "Practice Target B", 18, 40, 7, 6, 5, 4, frozenset({"burn"}), "practice_b"
    )
    if target_mode == "none":
        return ()
    if target_mode in {"single_enemy", "single_ally"}:
        return (target_a,)
    if target_mode in {"all_enemies", "all_allies"}:
        return (target_a, target_b)
    # ``self`` is filled from the scenario's user view below.
    return ()


def smoke_test_move_script(
    script: object,
    *,
    target_mode: TargetMode = "single_enemy",
    user: BattlerView | None = None,
    targets: tuple[BattlerView, ...] | None = None,
) -> list[str]:
    """Exercise a move function with contexts matching its targeting rule.

    When the catalog supplies ``targets``, these views come from actual authored
    characters. Only the number/HP/statuses are adjusted to deliberately exercise
    useful branches.
    """

    healthy_user = user or BattlerView(
        "Practice Hero", 50, 50, 10, 8, 7, 6, frozenset(), "practice_user"
    )
    healthy_user = replace(healthy_user, hp=healthy_user.max_hp, statuses=frozenset())
    low_user = replace(
        healthy_user,
        hp=max(1, healthy_user.max_hp // 4),
        statuses=frozenset({"burn"}),
    )

    def targets_for(user_view: BattlerView, *, low: bool) -> tuple[BattlerView, ...]:
        if target_mode == "self":
            return (user_view,)
        if target_mode == "none":
            return ()
        pool = targets or _synthetic_targets_for_mode(target_mode)
        needed = 1 if target_mode in {"single_enemy", "single_ally"} else 2
        selected = pool[:needed]
        if len(selected) < needed:
            fallback = _synthetic_targets_for_mode(target_mode)
            selected = (*selected, *fallback[len(selected):needed])
        adjusted = []
        for index, target in enumerate(selected):
            if low:
                hp = max(1, target.max_hp // (2 + index))
                statuses = frozenset({"burn"}) if index == 1 else frozenset()
            else:
                hp = target.max_hp
                statuses = frozenset()
            adjusted.append(replace(target, hp=hp, statuses=statuses))
        return tuple(adjusted)

    contexts = [
        MoveContext(
            user=healthy_user,
            targets=targets_for(healthy_user, low=False),
            round_number=1,
        ),
        MoveContext(
            user=low_user,
            targets=targets_for(low_user, low=True),
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
            problems.append(f"scenario {scenario_index}: {type(exc).__name__}: {exc}")
    return problems


def describe_command_target(target: CommandTarget) -> str:
    """Return a compact student-facing target description."""

    if isinstance(target, BattlerView):
        return target.name
    return target


def describe_command(command: MoveCommand) -> str:
    """Return a compact command description without dumping opaque view ids."""

    target = describe_command_target(command.target)
    if isinstance(command, Damage):
        extra = ", magical=True" if command.magical else ""
        return f"damage(power={command.power}{extra}, target={target})"
    if isinstance(command, Heal):
        return f"heal(power={command.power}, target={target})"
    if isinstance(command, AddStatus):
        return (
            f"add_status({command.name!r}, turns={command.duration}, "
            f"chance={command.chance}, target={target})"
        )
    if isinstance(command, ChangeStat):
        return (
            f"change_stat({command.stat!r}, stages={command.stages}, "
            f"chance={command.chance}, target={target})"
        )
    return repr(command)


def describe_script_result(result: MoveScriptResult) -> str:
    """Summarize the value returned directly by a student move function."""

    if result is None:
        return "None"
    if isinstance(result, (Damage, Heal, AddStatus, ChangeStat)):
        return describe_command(result)
    if isinstance(result, (list, tuple)):
        inner = ", ".join(
            describe_command(item)
            if isinstance(item, (Damage, Heal, AddStatus, ChangeStat))
            else repr(item)
            for item in result
        )
        opening, closing = ("[", "]") if isinstance(result, list) else ("(", ")")
        return f"{opening}{inner}{closing}"
    return repr(result)
