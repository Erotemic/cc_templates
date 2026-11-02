"""Describe encounter buttons once, for both drawing and mouse hit testing.

Rects use the logical 960 by 720 picture, not the resized desktop window.
A Button's index identifies an action/option; its position on a scrolled menu
may differ. This is layout data, not a widget framework or a place to choose actions.
"""

from dataclasses import dataclass
import pygame


ACTION_LABELS = ("FIGHT", "ACT", "ITEM", "SPARE")


@dataclass(frozen=True, kw_only=True)
class Button:
    """A label, a logical-pixel rectangle, and the corresponding menu option index."""

    label: str
    rect: pygame.Rect
    index: int


def main_buttons():
    """Return FIGHT / ACT / ITEM / SPARE rectangles, in their keyboard menu order."""
    buttons = []
    for index, label in enumerate(ACTION_LABELS):
        buttons.append(
            Button(label=label, rect=pygame.Rect(104 + index * 190, 604, 176, 62), index=index)
        )
    return buttons


def option_buttons(*, labels, selection):
    """Describe up to four visible submenu rows, preserving each original option index."""
    start = max(0, min(selection - 2, len(labels) - 4))
    buttons = []
    for row, label in enumerate(labels[start : start + 4]):
        buttons.append(
            Button(label=label, rect=pygame.Rect(124, 374 + row * 32, 712, 30), index=start + row)
        )
    return buttons
