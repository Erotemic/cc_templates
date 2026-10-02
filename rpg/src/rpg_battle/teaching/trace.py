from __future__ import annotations

"""Small opt-in execution trace intended for classrooms and the move lab."""

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class TeachingTrace:
    """Collect readable execution facts, optionally echoing them immediately."""

    echo: bool = True
    writer: Callable[[str], None] = print
    lines: list[str] = field(default_factory=list)

    def emit(self, message: str) -> None:
        line = f"[TEACH] {message}"
        self.lines.append(line)
        if self.echo:
            self.writer(line)


def emit_trace(state: object, message: str) -> None:
    """Emit a message when a BattleState has an attached teaching trace."""

    trace = getattr(state, "teaching_trace", None)
    if trace is not None:
        trace.emit(message)
