from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MenuState:
    title: str
    options: list[str]
    selected: int = 0

    def move(self, delta: int) -> None:
        if not self.options:
            self.selected = 0
            return
        self.selected = (self.selected + delta) % len(self.options)

    def current(self) -> str | None:
        if not self.options:
            return None
        return self.options[self.selected]
