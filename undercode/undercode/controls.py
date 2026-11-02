"""Input for one update: held movement and one-shot menu/action presses."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Controls:
    """Snapshot held movement and single-press actions for one update.

    x/y are horizontal/vertical movement amounts, usually -1, 0 or 1.
    menu_x/menu_y are direction presses, while confirm/cancel are action presses.
    Holding a key keeps movement active without repeatedly confirming a menu.
    """

    x: float = 0
    y: float = 0
    menu_x: int = 0
    menu_y: int = 0
    confirm: bool = False
    cancel: bool = False

    @property
    def menu_step(self):
        """Return a signed menu step, preferring a horizontal press if both axes changed."""
        return self.menu_x or self.menu_y
