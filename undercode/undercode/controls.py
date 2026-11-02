"""Input for one update: held movement and one-shot menu/action presses."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Controls:
    x: float = 0
    y: float = 0
    menu_x: int = 0
    menu_y: int = 0
    confirm: bool = False
    cancel: bool = False

    @property
    def menu_step(self):
        return self.menu_x or self.menu_y
