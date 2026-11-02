"""Small shared pygame drawing tools, independent of either game system.

Every position here is in logical-screen pixels. The window adapter scales the
finished frame. These helpers read state and draw; they never advance rules.
"""

import pygame
from . import art
from .settings import GAME_TITLE, WIDTH, HEIGHT


class UI:
    """Share text measurement, panels and bars; renderers own their own screen layout."""

    def __init__(self):
        """Cache the supported default-font sizes after main.py initializes pygame.font."""
        self.fonts = {
            size: pygame.font.Font(None, size) for size in (18, 20, 22, 24, 26, 28, 32, 38, 44, 64)
        }

    def text(self, *, surface, text, position, size=24, color=art.PAPER, center=False):
        """Draw text at a pixel position and return the occupied pygame.Rect.

        size selects a cached font; color is RGB. position is the top-left by
        default, or the center when center=True. Returning the rectangle helps
        layout checks; drawing does not change any game state.
        """
        image = self.fonts[size].render(str(text), True, color)
        rect = image.get_rect(center=position) if center else image.get_rect(topleft=position)
        surface.blit(image, rect)
        return rect

    def lines(self, *, text, width, size):
        """Return text wrapped to width pixels at the selected font size.

        Keep explicit paragraph breaks and split overlong words into pieces so
        each line fits. This measures text only; it does not draw anything.
        """
        font = self.fonts[size]
        lines = []
        for paragraph in str(text).split("\n"):
            line = ""
            for word in paragraph.split():
                # Split an unusually long word instead of drawing beyond a panel.
                while font.size(word)[0] > width:
                    if line:
                        lines.append(line)
                        line = ""
                    count = 1
                    while count < len(word) and font.size(word[: count + 1])[0] <= width:
                        count += 1
                    lines.append(word[:count])
                    word = word[count:]
                candidate = (line + " " + word).strip()
                if font.size(candidate)[0] > width and line:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            lines.append(line)
        return lines

    def wrapped(self, *, surface, text, rect, size=26, color=art.PAPER):
        """Draw text inside rect, reducing font size down to 18 when needed.

        rect uses logical pixels. Wrap to its width and stop before lines leave
        its height. This is a bounded label helper; Dialogue/Encounter paginate long
        messages beforehand so the player can still read the whole conversation.
        """
        candidates = [s for s in (size, 24, 22, 20, 18) if s <= size]
        for chosen in candidates:
            lines = self.lines(text=text, width=rect.width, size=chosen)
            if len(lines) * (chosen + 4) <= rect.height:
                break
        for i, line in enumerate(lines):
            if (i + 1) * (chosen + 4) > rect.height:
                break
            self.text(
                surface=surface,
                text=line,
                position=(rect.x, rect.y + i * (chosen + 4)),
                size=chosen,
                color=color,
            )

    def panel(self, *, surface, rect, color=(25, 32, 53), border=(83, 101, 120), radius=12):
        """Draw a filled rounded rect with a border, using logical pixels and RGB colors."""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        pygame.draw.rect(surface, border, rect, 2, border_radius=radius)

    def bar(self, *, surface, rect, fraction, color):
        """Draw a progress bar in rect, clamping fraction to the visible 0..1 range."""
        pygame.draw.rect(surface, (44, 49, 69), rect, border_radius=4)
        filled = rect.copy()
        filled.width = round(rect.width * max(0, min(1, fraction)))
        if filled.width:
            pygame.draw.rect(surface, color, filled, border_radius=4)

    def header(self, *, surface, subtitle, sound):
        """Draw the game title, subtitle, global control hints, and audio status."""
        self.text(
            surface=surface, text=GAME_TITLE.upper(), position=(28, 18), size=32, color=art.MINT
        )
        self.text(surface=surface, text=subtitle, position=(29, 49), size=20, color=art.MUTED)
        self.text(
            surface=surface,
            text="F1: guide  F2: state  R: restart  Esc: quit",
            position=(610, 19),
            size=20,
            color=art.MUTED,
        )
        self.text(surface=surface, text=sound, position=(746, 47), size=18, color=art.MUTED)

    def draw_help(self, *, surface):
        """Draw the controls/help overlay; Game pauses gameplay while help_open is true."""
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((9, 13, 25, 220))
        surface.blit(veil, (0, 0))
        self.panel(surface=surface, rect=pygame.Rect(130, 126, 700, 470), border=art.MINT)
        self.text(
            surface=surface, text="YOUR WAY THROUGH", position=(164, 157), size=38, color=art.MINT
        )
        rows = [
            ("WORLD", "Arrows / WASD walk. Z / Enter talk, accept or rest. X cancels."),
            ("TECHNIQUES", "Tab in the overworld switches Focus / Three Beat strikes."),
            ("YOUR TURN", "Fight uses timing. ACT builds understanding. Cocoa heals."),
            ("ANOTHER ENDING", "ACT until the green bar fills, then choose SPARE."),
            ("DEFENSE", "Free move, jump, or face a shield. Read each pattern hint."),
            ("TRY AGAIN", "R starts a new run. Losing returns you to camp restored."),
        ]
        for i, (heading, line) in enumerate(rows):
            y = 222 + i * 51
            self.text(surface=surface, text=heading, position=(164, y), size=18, color=art.GOLD)
            self.wrapped(
                surface=surface, text=line, rect=pygame.Rect(164, y + 20, 634, 28), size=22
            )
        self.text(
            surface=surface,
            text="F1: close this guide",
            position=(480, 565),
            size=24,
            color=art.PAPER,
            center=True,
        )
