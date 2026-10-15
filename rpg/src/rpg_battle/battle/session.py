from __future__ import annotations

"""The single state machine for battle turns, independent of who makes decisions.

A session advances through automatic round/turn events until it needs one
``DecisionRequest``. The caller (pygame, AI, teaching simulator, or replay)
submits either a ``BattleAction`` or a reserve combatant ID. Only core rules
modify combat state; the session owns the turn queue and decision order.

One ``next_step()`` advances at most one automatic phase. This preserves event
order for animation: round announcements cannot be skipped by fast controllers.
"""

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TYPE_CHECKING

from loguru import logger

from rpg_battle.core.battle_state import get_combatant, is_active, new_battle
from rpg_battle.core.models import BattleAction, BattleState, EncounterSpec
from rpg_battle.core.rules import (
    build_round_turn_queue,
    finish_round,
    legal_replacement_targets,
    legal_switch_targets,
    make_round_start_event,
    make_turn_start_event,
    reset_defending_flags,
    resolve_action,
    resolve_replacement,
    validate_action,
)

if TYPE_CHECKING:
    from rpg_battle.catalog import GameContent
    from rpg_battle.core.trace import TraceSink


@dataclass(frozen=True)
class DecisionRequest:
    """What the engine needs, not which implementation should supply it.

    For an action ``actor_id`` is the active fighter. For a replacement,
    ``choices`` contains the living reserves allowed to enter the field.
    """

    kind: Literal["action", "replacement"]
    team_index: int
    actor_id: str | None = None
    choices: tuple[str, ...] = ()


@dataclass(frozen=True)
class SessionStep:
    """One automatic transition and the decision now waiting, if any."""

    events: tuple[dict, ...]
    request: DecisionRequest | None


class BattleSession:
    """One authoritative battle lifecycle shared by every controller type.

    The session does not import AI, pygame, student code, or the replay viewer.
    ``BattleState`` holds turn order and actor selection, so inspecting the
    state reveals what decision is pending at any point in a round.
    """

    def __init__(
        self,
        encounter: EncounterSpec | None = None,
        seed: int = 0,
        *,
        content: GameContent | None = None,
        teaching_trace: "TraceSink | None" = None,
        state_setup: Callable[[BattleState], None] | None = None,
    ) -> None:
        if content is None:
            from rpg_battle.catalog import get_default_content
            content = get_default_content()
        self.content = content
        self.encounter = encounter or self.content.default_encounter
        self.seed = seed
        self.rng = random.Random(seed)
        self.teaching_trace = teaching_trace
        self.state_setup = state_setup
        self.state: BattleState
        self.restart()

    def restart(self) -> None:
        self.rng = random.Random(self.seed)
        self.state = new_battle(
            self.encounter, content=self.content, teaching_trace=self.teaching_trace
        )
        if self.state_setup is not None:
            self.state_setup(self.state)
        self.state.pending_turn_order.clear()
        self.state.current_actor_id = None
        self.state.round_announced = False

    @property
    def finished(self) -> bool:
        return self.state.outcome != "ongoing"

    @property
    def current_actor_id(self) -> str | None:
        return self.state.current_actor_id

    @current_actor_id.setter
    def current_actor_id(self, value: str | None) -> None:
        # Supports existing debugging/teaching fixtures. Normal code never
        # assigns this: next_step() selects the next actor.
        self.state.current_actor_id = value

    @property
    def pending_turn_order(self) -> list[str]:
        return self.state.pending_turn_order

    @property
    def round_announced(self) -> bool:
        return self.state.round_announced

    def current_actor(self):
        actor_id = self.current_actor_id
        return get_combatant(self.state, actor_id) if actor_id is not None else None

    @property
    def request(self) -> DecisionRequest | None:
        """Return the waiting decision without advancing or consuming RNG."""
        if self.finished:
            return None
        if self.state.pending_replacements:
            team_index = self.state.pending_replacements[0].team_index
            return DecisionRequest(
                "replacement", team_index,
                choices=tuple(legal_replacement_targets(self.state, team_index)),
            )
        actor = self.current_actor()
        if actor is not None:
            return DecisionRequest("action", actor.team_index, actor.combatant_id)
        return None

    def next_step(self) -> SessionStep:
        """Emit one automatic transition, or expose a request to the caller.

        Repeated calls while a request waits are idempotent. Never auto-select
        an AI action or replacement: policy belongs to the caller.
        """
        request = self.request
        if self.finished or request is not None:
            return SessionStep((), request)

        if not self.state.pending_turn_order:
            if not self.state.round_announced:
                reset_defending_flags(self.state)
                self.state.pending_turn_order = build_round_turn_queue(self.state, self.rng)
                self.state.round_announced = True
                logger.debug("Round {} order: {}", self.state.round_number,
                             self.state.pending_turn_order)
                return SessionStep((make_round_start_event(self.state),), self.request)
            events = finish_round(self.state)
            self.state.round_announced = False
            return SessionStep(tuple(events), self.request)

        while self.state.pending_turn_order:
            actor_id = self.state.pending_turn_order.pop(0)
            actor = get_combatant(self.state, actor_id)
            if not actor.alive or not is_active(self.state, actor_id):
                continue
            self.state.current_actor_id = actor_id
            return SessionStep((make_turn_start_event(self.state, actor_id),), self.request)
        return SessionStep((), self.request)

    def submit_action(self, action: BattleAction) -> list[dict]:
        request = self.request
        if request is None or request.kind != "action":
            raise ValueError("No fighter is waiting for an action")
        if action.actor_id != request.actor_id:
            raise ValueError(
                f"Wrong acting fighter: expected {request.actor_id!r}, "
                f"got {action.actor_id!r}"
            )
        # Explicit validation before any RNG/state mutation; malformed choices
        # must never silently consume a turn.
        action = validate_action(self.state, action)
        events = resolve_action(self.state, action, self.rng)
        self.state.current_actor_id = None
        return events

    def submit_replacement(self, combatant_id: str) -> list[dict]:
        request = self.request
        if request is None or request.kind != "replacement":
            raise ValueError("No team is waiting for a replacement")
        if combatant_id not in request.choices:
            raise ValueError(
                f"Illegal replacement {combatant_id!r} for team {request.team_index}; "
                f"choose from {request.choices!r}"
            )
        return resolve_replacement(self.state, request.team_index, combatant_id)

    def submit(self, decision: BattleAction | str) -> list[dict]:
        """Submit a decision of the kind currently requested by the engine."""
        request = self.request
        if request is None:
            raise ValueError("The battle is not waiting for a decision")
        if request.kind == "action":
            if not isinstance(decision, BattleAction):
                raise TypeError("An action request requires a BattleAction")
            return self.submit_action(decision)
        if not isinstance(decision, str):
            raise TypeError("A replacement request requires a reserve fighter ID")
        return self.submit_replacement(decision)

    def switch_targets_for_current_actor(self) -> list[str]:
        if self.current_actor_id is None:
            return []
        return legal_switch_targets(self.state, self.current_actor_id)
