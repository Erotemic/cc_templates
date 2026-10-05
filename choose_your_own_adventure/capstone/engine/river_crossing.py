"""Pure state machine for the wolf, goat, and cabbage river puzzle.

The game engine owns *when* this puzzle is active.  This module owns only the
small transition system itself, which makes it easy to reason about and test.

A state records which river bank the player and each passenger occupy.  A
crossing may carry at most one passenger.  Transitions that would leave the
wolf alone with the goat, or the goat alone with the cabbage, are rejected
before they mutate the game state.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal


Bank = Literal["west", "east"]
Passenger = Literal["wolf", "goat", "cabbage"]
PASSENGERS: tuple[Passenger, ...] = ("wolf", "goat", "cabbage")


def opposite(bank: Bank) -> Bank:
    return "east" if bank == "west" else "west"


@dataclass(frozen=True)
class RiverCrossingState:
    """One immutable state in the classic river-crossing puzzle."""

    player: Bank = "west"
    wolf: Bank = "west"
    goat: Bank = "west"
    cabbage: Bank = "west"

    def passenger_side(self, passenger: Passenger) -> Bank:
        return getattr(self, passenger)

    def passengers_with_player(self) -> tuple[Passenger, ...]:
        return tuple(
            passenger
            for passenger in PASSENGERS
            if self.passenger_side(passenger) == self.player
        )

    @property
    def solved(self) -> bool:
        return all(
            side == "east"
            for side in (self.player, self.wolf, self.goat, self.cabbage)
        )

    def unsafe_reason(self) -> str | None:
        """Explain an unsafe unattended bank, if one exists."""
        unattended = opposite(self.player)
        if self.wolf == self.goat == unattended:
            return "The wolf and goat cannot be left alone together."
        if self.goat == self.cabbage == unattended:
            return "The goat and cabbage cannot be left alone together."
        return None

    def try_cross(
        self, passenger: Passenger | None
    ) -> tuple["RiverCrossingState", str | None]:
        """Attempt a crossing without ever committing an unsafe state.

        Returns ``(new_state, None)`` for a legal crossing.  If the proposed
        transition violates the puzzle invariant, the original state is
        returned along with a short explanation.
        """
        if passenger is not None and self.passenger_side(passenger) != self.player:
            return self, f"The {passenger} is on the other bank."

        destination = opposite(self.player)
        updates: dict[str, Bank] = {"player": destination}
        if passenger is not None:
            updates[passenger] = destination
        candidate = replace(self, **updates)

        reason = candidate.unsafe_reason()
        if reason is not None:
            return self, reason
        return candidate, None

    def as_dict(self) -> dict[str, Bank]:
        return {
            "player": self.player,
            "wolf": self.wolf,
            "goat": self.goat,
            "cabbage": self.cabbage,
        }
