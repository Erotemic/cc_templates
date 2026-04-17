from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class LogEntry:
    """One line in the on-screen battle log."""

    text: str
    color: tuple[int, int, int]
    emphasis: bool = False


class CombatLog:
    """Append-only combat log used by the battle HUD.

    The newest line is appended to the right side of the deque and is drawn at
    the bottom of the log panel so it reads like terminal output.
    """

    def __init__(self, max_lines: int = 8) -> None:
        self.lines: deque[LogEntry] = deque(maxlen=max_lines)

    def add(
        self,
        text: str,
        color: tuple[int, int, int] = (236, 236, 242),
        emphasis: bool = False,
    ) -> None:
        """Append a new line to the end of the battle log."""
        if text:
            self.lines.append(LogEntry(text=text, color=color, emphasis=emphasis))

    def latest(self) -> list[LogEntry]:
        """Return log entries in chronological order."""
        return list(self.lines)
