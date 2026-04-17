from __future__ import annotations

"""High-level battle controller.

The controller serializes the battle into clear presentation steps:

1. announce the round
2. announce whose turn it is
3. collect an action from the human or AI controller
4. resolve that single action
5. handle replacements
6. continue to the next actor
"""

import random

from loguru import logger

from rpg_battle.content.encounters import DEFAULT_ENCOUNTER
from rpg_battle.core.ai import choose_ai_action, choose_ai_replacement
from rpg_battle.core.battle_state import get_combatant, new_battle
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
)


class BattleController:
    """Coordinate battle-state progression and controller decisions."""

    def __init__(self, encounter: EncounterSpec = DEFAULT_ENCOUNTER, seed: int = 0) -> None:
        self.encounter = encounter
        self.rng = random.Random(seed)
        self.state: BattleState = new_battle(encounter)
        self.pending_turn_order: list[str] = []
        self.current_actor_id: str | None = None
        self.round_announced = False
        logger.debug(
            "BattleController initialized with seed={} encounter={}",
            seed,
            encounter.encounter_id,
        )

    def restart(self) -> None:
        logger.info("Restarting battle controller")
        self.state = new_battle(self.encounter)
        self.pending_turn_order = []
        self.current_actor_id = None
        self.round_announced = False

    def current_actor(self):
        if self.current_actor_id is None:
            return None
        return get_combatant(self.state, self.current_actor_id)

    def player_can_act(self) -> bool:
        actor = self.current_actor()
        return (
            actor is not None
            and actor.team_index == 0
            and self.state.winner is None
            and not self.player_needs_replacement()
        )

    def enemy_should_act(self) -> bool:
        actor = self.current_actor()
        return actor is not None and actor.team_index == 1 and self.state.winner is None

    def player_needs_replacement(self) -> bool:
        return any(request.team_index == 0 for request in self.state.pending_replacements)

    def player_replacement_targets(self) -> list[str]:
        return legal_replacement_targets(self.state, 0)

    def switch_targets_for_current_actor(self) -> list[str]:
        if self.current_actor_id is None:
            return []
        return legal_switch_targets(self.state, self.current_actor_id)

    def resolve_player_replacement(self, combatant_id: str) -> list[dict]:
        logger.info("Resolving player replacement with {}", combatant_id)
        return resolve_replacement(self.state, 0, combatant_id)

    def advance_to_next_turn(self) -> list[dict]:
        if self.state.winner is not None or self.current_actor_id is not None:
            return []

        if self.state.pending_replacements:
            first_request = self.state.pending_replacements[0]
            if first_request.team_index == 0:
                logger.debug("Waiting for player replacement")
                return []
            replacement_id = choose_ai_replacement(self.state, first_request.team_index)
            if replacement_id is None:
                return []
            logger.info(
                "AI replacement for team {} -> {}",
                first_request.team_index,
                replacement_id,
            )
            return resolve_replacement(self.state, first_request.team_index, replacement_id)

        if not self.pending_turn_order:
            if not self.round_announced:
                reset_defending_flags(self.state)
                self.pending_turn_order = build_round_turn_queue(self.state, self.rng)
                self.round_announced = True
                logger.info(
                    "Starting round {} with order {}",
                    self.state.round_number,
                    self.pending_turn_order,
                )
                return [make_round_start_event(self.state)]
            round_events = finish_round(self.state)
            self.round_announced = False
            self.pending_turn_order = []
            if round_events:
                logger.info(
                    "Finished round {}",
                    self.state.round_number - (1 if self.state.winner is None else 0),
                )
            return round_events

        while self.pending_turn_order:
            actor_id = self.pending_turn_order.pop(0)
            actor = get_combatant(self.state, actor_id)
            if not actor.alive or not actor.active:
                logger.debug("Skipping inactive actor {}", actor_id)
                continue
            self.current_actor_id = actor_id
            logger.info("It is now {}'s turn", actor.spec.name)
            return [make_turn_start_event(self.state, actor_id)]
        return []

    def resolve_current_player_action(self, player_action: BattleAction) -> list[dict]:
        if not self.player_can_act() or self.current_actor_id is None:
            return []
        logger.info("Resolving player action: {}", player_action)
        events = resolve_action(self.state, player_action, self.rng)
        self.current_actor_id = None
        return events

    def resolve_current_enemy_action(self) -> list[dict]:
        if not self.enemy_should_act() or self.current_actor_id is None:
            return []
        enemy_action = choose_ai_action(self.state, self.current_actor_id, self.rng)
        logger.info("Resolving enemy action: {}", enemy_action)
        events = resolve_action(self.state, enemy_action, self.rng)
        self.current_actor_id = None
        return events
