from __future__ import annotations

"""Core battle data models.

The engine keeps normalized content specifications separate from runtime battle
instances. Students normally author friendly ``Character`` and ``Move`` objects in
``student_game/``; :mod:`rpg_battle.api` compiles them into the specs here.
``CombatantState`` and ``BattleState`` are the mutable runtime objects.
"""

from dataclasses import dataclass, field
from typing import Callable, Literal, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from rpg_battle.core.scripting import AIStrategy, MoveContext, MoveScriptResult
    from rpg_battle.core.trace import TraceSink

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
    stat stage changes. The student authoring API constructs these in a
    keyword-heavy style so students can read the effect at a glance.
    """

    status: str | None = None
    chance: float = 1.0
    stat: str | None = None
    stages: int = 0
    duration: int = 0


@dataclass(frozen=True)
class MoveSpec:
    """Normalized declarative move definition consumed by the engine."""

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
    script: Callable[["MoveContext"], "MoveScriptResult"] | None = None
    mana_cost: int = 0


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
    max_mana: int = 0


@dataclass(frozen=True)
class CombatContent:
    """Only the definitions combat rules need; no art/audio/renderer objects.

    A complete ``GameContent`` can supply these three collections without
    making the combat state retain presentation catalogs or importing pygame.
    """

    characters: Mapping[str, CharacterSpec]
    moves: Mapping[str, MoveSpec]
    basic_attack_move_id: str


@dataclass(frozen=True)
class InventoryEntry:
    """Describe one stack of items owned by a team.

    The current classroom project does not expose items in the battle UI yet,
    but the runtime model already knows how to carry team inventory data. A
    future item system can add student-facing item definitions and thread them
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
    strategy: "AIStrategy | None" = None


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
    """Mutable resources and status for one fighter.

    Placement belongs exclusively to ``TeamBattleState.active_slots``. Living
    versus knocked out is derived from HP, rather than stored in a second flag.
    """

    combatant_id: str
    spec: CharacterSpec
    team_index: int
    current_hp: int | None = None
    current_mana: int | None = None
    statuses: dict[str, StatusState] = field(default_factory=dict)
    temp_bonuses: dict[str, int] = field(
        default_factory=lambda: {"attack": 0, "defense": 0, "magic": 0, "speed": 0}
    )
    render_transforms: dict[str, int] = field(default_factory=dict)
    defending: bool = False

    def __post_init__(self) -> None:
        if self.current_hp is None:
            self.current_hp = self.spec.max_hp
        if self.current_mana is None:
            self.current_mana = self.spec.max_mana
        if not 0 <= self.current_mana <= self.spec.max_mana:
            raise ValueError("Current mana must be between zero and max mana")

    @property
    def alive(self) -> bool:
        return self.current_hp > 0

    def hp_ratio(self) -> float:
        return max(0.0, min(1.0, self.current_hp / self.spec.max_hp))


@dataclass
class TeamBattleState:
    """Roster order and battlefield placement are the only membership state.

    ``roster_ids`` includes *all* original fighters, including defeated ones.
    ``active_slots`` has exactly ``active_limit`` positions; empty slots remain
    empty until explicitly replaced. The derived ``active_ids`` and
    ``reserve_ids`` compatibility views must not be mutated. ``reserve_ids``
    includes unfielded KO fighters; use ``living_reserve_ids(state, team_index)``
    to request a fighter who can actually enter battle.
    """

    team_index: int
    name: str
    controller_type: ControllerType
    active_limit: int
    roster_ids: list[str] = field(default_factory=list)
    active_slots: list[str | None] = field(default_factory=list)
    inventory: list[InventoryEntry] = field(default_factory=list)
    strategy: "AIStrategy | None" = None

    @property
    def active_ids(self) -> list[str]:
        """Current frontline, in fixed slot order (derived snapshot)."""
        return [cid for cid in self.active_slots if cid is not None]

    @property
    def reserve_ids(self) -> list[str]:
        """Unfielded roster in selection order (may include knocked-out IDs)."""
        occupied = set(self.active_ids)
        return [cid for cid in self.roster_ids if cid not in occupied]


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
    content: CombatContent | None = None
    round_number: int = 1
    winner: int | None = None
    outcome: Literal["ongoing", "victory", "draw"] = "ongoing"
    pending_replacements: list[ReplacementRequest] = field(default_factory=list)
    # Session phase is battle state, not UI/AI controller state.
    pending_turn_order: list[str] = field(default_factory=list)
    current_actor_id: str | None = None
    round_announced: bool = False
    teaching_trace: "TraceSink | None" = None


@dataclass(frozen=True)
class BattleAction:
    """Single declared action chosen by one combatant for one turn."""

    actor_id: str
    kind: ActionKind
    move_id: str | None = None
    target_ids: tuple[str, ...] = ()
    switch_in_id: str | None = None
    item_id: str | None = None
