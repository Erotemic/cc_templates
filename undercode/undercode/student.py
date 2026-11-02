"""START HERE. A complete character + pattern that you can change and extend.

Try changing the colors, greeting, ACT replies, or spawn_interval. Then add
another pattern class and choose between them in choose_echo_pattern().
No engine edits are needed to add a character using this contract.
"""

import math
import pygame
from .arena import DefensePattern
from .model import Act, Character

GAME_TITLE = "UnderCode"
PLAYER_NAME = "Courier"


class RippleLanes(DefensePattern):
    name = "Ripples in the margins"
    hint = "Move through the spaces between the ripples."
    duration = 5.4

    def __init__(self):
        self.cooldown = 0.3
        self.wave = 0
        self.spawn_interval = 0.7  # TRY: .9 is calmer; .5 is busier.

    def update(self, arena, dt):
        if self.spawn_interval <= 0:
            raise ValueError("Ripple spawn_interval must be positive.")
        self.cooldown -= dt
        while self.cooldown <= 0 and arena.elapsed < 3.8:
            # The opening slides left/right instead of being completely random.
            gap = 2 + round(math.sin(self.wave * 0.9) * 2)
            for lane in range(7):
                if lane not in (gap, gap + 1):
                    arena.spawn(
                        (lane + 0.5) * arena.width / 7,
                        5,
                        0,
                        105,
                        radius=6,
                        color=(137, 235, 202),
                        warmup=0.4,
                    )
            self.wave += 1
            self.cooldown += self.spawn_interval


def draw_echo(surface, center, scale, time):
    """An original lantern spirit. Replace this with YOUR character's art."""
    x, y = center
    y += math.sin(time * 2) * 5 * scale
    rect = pygame.Rect(x - 29 * scale, y - 34 * scale, 58 * scale, 65 * scale)
    pygame.draw.rect(surface, (115, 227, 193), rect, border_radius=max(1, round(17 * scale)))
    inside = rect.inflate(-13 * scale, -13 * scale)
    pygame.draw.rect(surface, (26, 52, 59), inside, border_radius=max(1, round(12 * scale)))
    for side in (-1, 1):
        pygame.draw.circle(
            surface,
            (255, 205, 126),
            (round(x + side * 11 * scale), round(y - 3 * scale)),
            max(2, round(4 * scale)),
        )
    pygame.draw.arc(
        surface,
        (237, 235, 220),
        (x - 15 * scale, y - 51 * scale, 30 * scale, 26 * scale),
        0,
        math.pi,
        max(1, round(4 * scale)),
    )
    pygame.draw.line(
        surface,
        (237, 235, 220),
        (x - 9 * scale, y + 13 * scale),
        (x + 9 * scale, y + 13 * scale),
        max(1, round(2 * scale)),
    )


def choose_echo_pattern(context):
    # context.turn, context.enemy_hp, and context.calm are available here.
    # TRY: return another pattern after two turns or below half health.
    return RippleLanes()


ECHO = Character(
    key="echo",
    name="Echo",
    description="A lantern spirit learning to listen.",
    invitation="I made a little pattern. Want to try it? Z: yes. X: later.",
    color=(115, 227, 193),
    portrait=draw_echo,
    acts=(
        Act("Listen", "You wait. Echo finds the words they were looking for.", calm=2),
        Act("Share a story", "Your story makes their light a little warmer.", calm=1),
        Act("Make a face", "Echo makes a face right back. It is a very good face.", calm=0),
    ),
    choose_pattern=choose_echo_pattern,
    max_hp=20,
    greeting='Echo lights up the quiet observatory. "Let us make something together."',
    goodbye="Echo lends you a little light for the road. A new friend counts as progress.",
)

# Registration is ordinary Python data. Add your own keys here and place a new
# Placement in content.py. The --practice key previews a pattern immediately.
EXTRA_CHARACTERS = (ECHO,)
EXTRA_PATTERNS = {"ripples": RippleLanes}
