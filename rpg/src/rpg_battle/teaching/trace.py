from __future__ import annotations

"""Small opt-in execution trace intended for classrooms and the move lab."""

from dataclasses import dataclass, field
from typing import Callable

# Core owns the optional diagnostics interface; this module owns the classroom
# collection and pretty-printing implementation.
from rpg_battle.core.trace import emit_trace, record_trace


@dataclass(frozen=True)
class TraceRecord:
    """One structured fact emitted by the real engine while resolving a move."""

    kind: str
    data: dict[str, object]


@dataclass
class TeachingTrace:
    """Collect readable execution facts and structured records.

    The terminal trace and the move lab use the same records produced by the
    rules engine. This avoids maintaining a second, teaching-only damage formula.
    """

    echo: bool = True
    writer: Callable[[str], None] = print
    lines: list[str] = field(default_factory=list)
    records: list[TraceRecord] = field(default_factory=list)

    def emit(self, message: str) -> None:
        line = f"[TEACH] {message}"
        self.lines.append(line)
        if self.echo:
            self.writer(line)

    def record(self, kind: str, *, message: str | None = None, **data: object) -> None:
        self.records.append(TraceRecord(kind=kind, data=dict(data)))
        if message is not None:
            self.emit(message)
