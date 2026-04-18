from __future__ import annotations

"""Core battle data models.

The classroom project keeps reusable content definitions separate from runtime
battle instances. ``CharacterSpec`` and ``MoveSpec`` live in ``content/`` and are
safe for students to edit, while ``CombatantState`` and ``BattleState`` are the
runtime objects the engine mutates during battle.
"""

from dataclasses import dataclass, field
from typing import Literal

MoveKind = Literal["physical", "magical", "heal", "buff", "debuff", "status"]
TargetMode = Literal[
    "self",
    "single_enemy",
    "single_ally",
    "all_enemies",
    "all_allies",
    "none",
]
ActionKind = Literal["attack", "skill", "defend", "switch", "item"]
ControllerType = Literal["human", "ai"]


@dataclass(frozen=True)
class MoveEffect:
    """Describe an extra effect attached to a move.

    Effects are optional rider mechanics such as status ailments or temporary
    stat stage changes. Classroom content files usually construct these in a
    keyword-heavy style so students can read the effect at a glance.
    """

    status: str | None = None
    chance: float = 1.0
    stat: str | None = None
    stages: int = 0
    duration: int = 0


@dataclass(frozen=True)
class MoveSpec:
    """Declarative move definition loaded from ``content/moves.py``."""

    move_id: str
    name: str
    kind: MoveKind
    power: int = 0
    accuracy: float = 1.0
    target_mode: TargetMode = "single_enemy"
    animation: str = "impact"
    sound_id: str = ""
    priority: int = 0
    effects: tuple[MoveEffect, ...] = ()
    flavor: str = ""


@dataclass(frozen=True)
class CharacterSpec:
    """Reusable character template before it becomes a runtime combatant."""

    char_id: str
    name: str
    role: str
    max_hp: int
    attack: int
    defense: int
    magic: int
    speed: int
    sprite_id: str
    move_ids: tuple[str, ...]
    description: str = ""


@dataclass(frozen=True)
class InventoryEntry:
    """Describe one stack of items owned by a team.

    The current classroom project does not expose items in the battle UI yet,
    but the runtime model already knows how to carry team inventory data. A
    future item system can add item definitions in ``content/`` and thread them
    through the same action pipeline used for moves.
    """

    item_id: str
    quantity: int = 1


@dataclass(frozen=True)
class TeamSpec:
    """Describe a team roster and its preferred starting frontline.

    ``members`` lists the whole roster in reserve order. ``starting_active`` is
    optional and lets a content author choose which members begin on the field
    without pushing that detail into ``EncounterSpec``.
    """

    name: str
    members: tuple[str, ...]
    controller_type: ControllerType = "human"
    starting_active: tuple[str, ...] | None = None
    inventory: tuple[InventoryEntry, ...] = ()


@dataclass(frozen=True)
class EncounterSpec:
    """High-level battle setup that chooses teams, limits, and music."""

    encounter_id: str
    title: str
    player_team: TeamSpec
    enemy_team: TeamSpec
    active_limits: tuple[int, int] = (1, 1)
    music_track_id: str | None = None


@dataclass
class StatusState:
    """Runtime status timer applied to a combatant."""

    name: str
    duration: int


@dataclass
class CombatantState:
    """Mutable runtime battler instance created from a ``CharacterSpec``.

    ``slot_index`` records the battler's fixed battlefield position while active.
    The scene uses that value to keep units anchored to stable formation slots
    instead of collapsing the remaining party inward when someone is defeated.
    """

    combatant_id: str
    spec: CharacterSpec
    team_index: int
    current_hp: int | None = None
    statuses: dict[str, StatusState] = field(default_factory=dict)
    temp_bonuses: dict[str, int] = field(
        default_factory=lambda: {"attack": 0, "defense": 0, "magic": 0, "speed": 0}
    )
    render_transforms: dict[str, int] = field(default_factory=dict)
    defending: bool = False
    active: bool = False
    fainted: bool = False
    slot_index: int | None = None

    def __post_init__(self) -> None:
        if self.current_hp is None:
            self.current_hp = self.spec.max_hp

    @property
    def alive(self) -> bool:
        return self.current_hp > 0 and not self.fainted

    def hp_ratio(self) -> float:
        return max(0.0, min(1.0, self.current_hp / self.spec.max_hp))


@dataclass
class TeamBattleState:
    """Runtime team state tracking active and reserve combatant ids."""

    team_index: int
    name: str
    controller_type: ControllerType
    active_limit: int
    active_ids: list[str] = field(default_factory=list)
    reserve_ids: list[str] = field(default_factory=list)
    inventory: list[InventoryEntry] = field(default_factory=list)

    def defeated(self) -> bool:
        return not self.active_ids and not self.reserve_ids


@dataclass(frozen=True)
class ReplacementRequest:
    """Signal that a team has empty frontline slots that need filling."""

    team_index: int
    slots_to_fill: int = 1


@dataclass
class BattleState:
    """Top-level mutable battle state shared by rules, UI, and AI."""

    teams: list[TeamBattleState]
    combatants: dict[str, CombatantState]
    round_number: int = 1
    winner: int | None = None
    pending_replacements: list[ReplacementRequest] = field(default_factory=list)


@dataclass(frozen=True)
class BattleAction:
    """Single declared action chosen by one combatant for one turn."""

    actor_id: str
    kind: ActionKind
    move_id: str | None = None
    target_ids: tuple[str, ...] = ()
    switch_in_id: str | None = None
    item_id: str | None = None
