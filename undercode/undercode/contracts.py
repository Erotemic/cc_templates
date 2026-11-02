"""The small messages connecting two otherwise independent game systems.

An overworld neighbor requests an encounter by ID. After its closing dialogue,
the encounter returns a result. Only Game acts on these messages. Neither
engine needs to know the other's classes, menus, map layout, or renderer.
"""

from dataclasses import dataclass
from enum import Enum, auto


class Outcome(Enum):
    """Describe how an encounter ended; leaving and losing are different events."""

    SPARED = auto()
    DEFEATED = auto()
    LEFT = auto()
    LOST = auto()


@dataclass(frozen=True, kw_only=True)
class EncounterRequest:
    """Ask Game to run encounter_id on behalf of one particular overworld person."""

    encounter_id: str
    person_id: str


@dataclass(frozen=True, kw_only=True)
class EncounterResult:
    """Return an outcome after the final message has been read."""

    outcome: Outcome
    opponent_name: str


@dataclass(frozen=True, kw_only=True)
class RoomRequest:
    """Ask the coordinator to cover an overworld room change with a fade."""

    destination_room: str
    destination_spawn: str


@dataclass(frozen=True, kw_only=True)
class ToneRequest:
    """Ask the audio adapter for a frequency in Hz and a duration in seconds."""

    hz: float
    duration: float = 0.4
