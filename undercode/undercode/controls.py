"""Separate held directions from one-frame button presses.

main.py's window adapter creates one Controls record per frame. An arrow held
for ten frames keeps move_x/move_y active ten times. Confirm is True only in
the frame of its KEYDOWN, so holding Z cannot make ten menu choices.
"""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Controls:
    """Input for one frame: held movement, single presses, and an optional click.

    mouse_click is the saved left-button press in logical-screen pixels, not
    the current pointer location or a continuously held button. None means no
    click this frame. The window adapter has already rejected letterbox margins.
    """

    move_x: float = 0
    move_y: float = 0
    menu_x: int = 0
    menu_y: int = 0
    confirm_pressed: bool = False
    cancel_pressed: bool = False
    sprint_held: bool = False
    mouse_click: tuple[float, float] | None = None  # One left press, in logical pixels.

    @property
    def menu_step(self):
        """Return one signed menu step; prefer horizontal when both arrows changed."""
        if self.menu_x:
            return self.menu_x
        return self.menu_y
