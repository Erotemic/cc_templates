"""Draw only encounters: menus, timing sequences, and the local defense arena.

The engine owns phases, scores and HP. Drawing calls no student rules and never
consumes the pattern RNG. It can be used without importing a single room.
"""

import math
import pygame
from .. import art
from ..presentation import UI
from .arena import Mode
from .encounter import Phase
from .menu import main_buttons, option_buttons

ARENA_RECT = pygame.Rect(180, 332, 600, 196)
MESSAGE_RECT = pygame.Rect(104, 322, 752, 216)


class EncounterView(UI):
    """Translate encounter state to a picture; UI supplies only shared primitives."""

    def draw(self, *, surface, encounter, time, sound_label):
        """Draw the opponent, progress bars, current encounter phase, and action buttons.

        Delegate timing attacks and defenses to their renderers. Other phases
        show paged messages or menus, scrolling ACT choices when needed.
        """
        character = encounter.opponent
        self.header(surface=surface, subtitle=character.description, sound=sound_label)
        # A quiet stage, separate from the decision/defense area below.
        pygame.draw.circle(surface, (31, 39, 61), (480, 178), 99)
        pygame.draw.circle(surface, (57, 67, 92), (480, 178), 99, 1)
        for i in range(18):
            x = 90 + (i * 137) % 790
            y = 102 + (i * 43) % 173
            art.star(
                surface=surface,
                center=(x, y),
                radius=2 + math.sin(time + i) * 0.6,
                color=(98, 111, 137),
            )
        shake = math.sin(time * 65) * encounter.portrait_flash * 10
        character.portrait(surface=surface, center=(480 + shake, 179), scale=1.28, time=time)
        self.text(
            surface=surface,
            text=character.name,
            position=(480, 263),
            size=32,
            color=character.color,
            center=True,
        )
        self.bar(
            surface=surface,
            rect=pygame.Rect(264, 301, 190, 7),
            fraction=encounter.opponent_hp / character.max_hp,
            color=art.CORAL,
        )
        self.bar(
            surface=surface,
            rect=pygame.Rect(506, 301, 190, 7),
            fraction=encounter.calm / character.calm_needed,
            color=art.MINT,
        )
        self.text(
            surface=surface,
            text=f"HP {encounter.opponent_hp}/{character.max_hp}",
            position=(264, 282),
            size=18,
            color=art.MUTED,
        )
        self.text(
            surface=surface,
            text="READY TO SPARE" if encounter.spare_ready else "UNDERSTANDING",
            position=(506, 282),
            size=18,
            color=art.MINT if encounter.spare_ready else art.MUTED,
        )
        if encounter.phase == Phase.DEFEND:
            self.draw_arena(surface=surface, arena=encounter.arena, time=time)
        elif encounter.phase == Phase.ATTACK:
            self.draw_strike(surface=surface, strike=encounter.strike)
        else:
            self.panel(surface=surface, rect=MESSAGE_RECT, border=(112, 129, 147))
            if encounter.phase in (Phase.MESSAGE, Phase.FINISHED):
                self.text(
                    surface=surface,
                    text="A REPLY" if encounter.outcome is None else "UNTIL NEXT TIME",
                    position=(124, 338),
                    size=20,
                    color=art.MINT,
                )
                self.wrapped(
                    surface=surface,
                    text=encounter.current_message
                    if encounter.phase == Phase.FINISHED
                    else encounter.visible_message,
                    rect=pygame.Rect(126, 372, 708, 119),
                    size=28,
                )
                page = (
                    f"  {encounter.page + 1}/{len(encounter.pages)}"
                    if len(encounter.pages) > 1
                    else ""
                )
                self.text(
                    surface=surface,
                    text="R: restart this encounter   Esc: quit"
                    if encounter.phase == Phase.FINISHED
                    else "Z / Enter: continue    X: reveal text" + page,
                    position=(126, 507),
                    size=20,
                    color=art.MUTED,
                )
            elif encounter.phase == Phase.MENU:
                line = f"{character.name} is listening. What will you do?"
                if encounter.spare_ready:
                    line = f"{character.name} has lowered their guard. You can SPARE them."
                self.wrapped(
                    surface=surface, text=line, rect=pygame.Rect(126, 353, 708, 85), size=28
                )
                self.text(
                    surface=surface,
                    text="Choose with arrows / WASD. Confirm with Z / Enter.",
                    position=(126, 477),
                    size=22,
                    color=art.MUTED,
                )
                self.text(
                    surface=surface,
                    text=f"Technique: {encounter.weapon.name}",
                    position=(126, 508),
                    size=20,
                    color=art.GOLD,
                )
            else:
                self.text(
                    surface=surface,
                    text={
                        Phase.ACT: "FIND A CONNECTION",
                        Phase.ITEM: "YOUR SATCHEL",
                        Phase.MERCY: "ANOTHER WAY THROUGH",
                    }.get(encounter.phase, ""),
                    position=(126, 338),
                    size=20,
                    color=art.MINT,
                )
                options = encounter.options()
                if len(options) > 4:
                    self.text(
                        surface=surface,
                        text=f"{encounter.selection + 1} / {len(options)}",
                        position=(762, 338),
                        size=18,
                        color=art.MUTED,
                    )
                for button in option_buttons(labels=options, selection=encounter.selection):
                    selected = button.index == encounter.selection
                    self.panel(
                        surface=surface,
                        rect=button.rect,
                        border=art.GOLD if selected else (55, 65, 82),
                        radius=4,
                    )
                    if selected:
                        art.soul(
                            surface=surface,
                            center=(135, button.rect.y + 14),
                            color=art.CORAL,
                            radius=6,
                        )
                    self.text(
                        surface=surface,
                        text=button.label,
                        position=(155, button.rect.y + 4),
                        size=26,
                        color=art.GOLD if selected else art.PAPER,
                    )
                self.text(
                    surface=surface,
                    text="Up / Down: choose    Z: confirm    X: back",
                    position=(126, 507),
                    size=20,
                    color=art.MUTED,
                )
        player = encounter.player
        self.text(
            surface=surface, text=player.name.upper(), position=(106, 558), size=24, color=art.PAPER
        )
        self.text(surface=surface, text="HP", position=(300, 559), size=22, color=art.MUTED)
        self.bar(
            surface=surface,
            rect=pygame.Rect(337, 562, 205, 17),
            fraction=player.hp / player.max_hp,
            color=art.CORAL,
        )
        self.text(
            surface=surface,
            text=f"{player.hp:02d} / {player.max_hp:02d}",
            position=(557, 557),
            size=26,
            color=art.PAPER,
        )
        self.text(
            surface=surface,
            text=f"Cocoa: {player.snacks}",
            position=(725, 559),
            size=22,
            color=art.GOLD,
        )
        for button in main_buttons():
            rect = button.rect
            selected = encounter.phase == Phase.MENU and button.index == encounter.selection
            ready = button.label == "SPARE" and encounter.spare_ready
            color = art.GOLD if selected else art.MINT if ready else (89, 103, 125)
            self.panel(
                surface=surface,
                rect=rect,
                color=(42, 47, 61) if selected else (24, 29, 47),
                border=color,
                radius=8,
            )
            self.text(
                surface=surface,
                text=button.label,
                position=rect.center,
                size=28,
                color=color,
                center=True,
            )
        self.text(
            surface=surface,
            text="Move during defense. Read the pattern hint. Every encounter has more than one ending.",
            position=(480, 694),
            size=20,
            color=art.MUTED,
            center=True,
        )

    def draw_strike(self, *, surface, strike):
        """Render a timing mini-game using its read-only StrikeView snapshot.

        Translate normalized cursor/target positions to the on-screen bar.
        Drawing targets and recorded presses never awards accuracy or damage.
        """
        view = strike.view()
        self.panel(surface=surface, rect=MESSAGE_RECT, border=art.GOLD)
        self.text(surface=surface, text=view.title, position=(126, 338), size=22, color=art.GOLD)
        self.text(surface=surface, text=view.instruction, position=(126, 373), size=24)
        bar = pygame.Rect(146, 433, 668, 40)
        pygame.draw.rect(surface, (48, 58, 75), bar, border_radius=6)
        for target in view.targets:
            region = pygame.Rect(
                bar.x + (target - view.window) * bar.w, bar.y, view.window * 2 * bar.w, bar.h
            )
            pygame.draw.rect(surface, (57, 112, 101), region, border_radius=4)
            pygame.draw.line(
                surface,
                art.MINT,
                (bar.x + target * bar.w, bar.top),
                (bar.x + target * bar.w, bar.bottom),
                3,
            )
        x = bar.x + view.cursor * bar.w
        pygame.draw.line(surface, art.PAPER, (x, bar.top - 9), (x, bar.bottom + 9), 4)
        for position, score in view.marks:
            art.star(
                surface=surface,
                center=(bar.x + position * bar.w, bar.centery),
                radius=8,
                color=art.GOLD if score > 0.5 else art.CORAL,
            )
        self.text(
            surface=surface,
            text="Let the cursor meet the light.",
            position=(480, 508),
            size=20,
            color=art.MUTED,
            center=True,
        )

    def draw_arena(self, *, surface, arena, time):
        """Draw the arena's soul, shield, warnings, projectiles, and remaining time.

        Translate local arena pixels into ARENA_RECT and clip hazards there,
        keeping hints outside. time is elapsed animation seconds, not an update
        request; Arena owns motion, warning lifetimes, blocking and damage.
        """
        rect = ARENA_RECT
        pygame.draw.rect(surface, (11, 18, 34), rect)
        # Clip all hazards to the playfield; hints and health stay outside it.
        previous_clip = surface.get_clip()
        surface.set_clip(rect)
        for x in range(0, arena.width, 30):
            pygame.draw.line(
                surface, (21, 32, 48), (rect.x + x, rect.y), (rect.x + x, rect.bottom), 1
            )
        for beam in arena.beams:
            region = beam.rect.move(rect.topleft)
            if beam.active:
                pygame.draw.rect(surface, art.CORAL, region)
                pygame.draw.rect(surface, art.PAPER, region.inflate(-8, 0))
            else:
                pygame.draw.rect(surface, (61, 47, 48), region)
                pygame.draw.rect(surface, art.GOLD, region, 1)
                for y in range(region.top + 6, region.bottom, 18):
                    pygame.draw.line(
                        surface, art.GOLD, (region.left + 4, y), (region.right - 4, y), 1
                    )
        if arena.pattern.mode == Mode.GRAVITY:
            pygame.draw.line(
                surface, art.GOLD, (rect.left, rect.bottom - 2), (rect.right, rect.bottom - 2), 2
            )
        for bullet in arena.bullets:
            center = bullet.position + rect.topleft
            if bullet.warmup > 0:
                pygame.draw.circle(
                    surface,
                    bullet.color,
                    (round(center.x), round(center.y)),
                    round(bullet.radius + 5),
                    1,
                )
                art.star(surface=surface, center=center, radius=3, color=bullet.color)
            else:
                pygame.draw.circle(
                    surface, bullet.color, (round(center.x), round(center.y)), round(bullet.radius)
                )
                pygame.draw.circle(
                    surface, art.PAPER, (round(center.x - 2), round(center.y - 2)), 2
                )
        soul = arena.soul
        point = soul.position + rect.topleft
        if arena.pattern.mode == Mode.SHIELD:
            color = art.PAPER if soul.guard_flash else art.MINT
            facing = soul.facing
            side = pygame.Vector2(-facing.y, facing.x)
            a, b = point + facing * 25 + side * 15, point + facing * 25 - side * 15
            pygame.draw.line(surface, color, a, b, 6)
            pygame.draw.line(surface, (44, 89, 88), point, point + facing * 15, 2)
        if not soul.invulnerable or int(time * 12) % 2 == 0:
            art.soul(surface=surface, center=point, color=art.CORAL, radius=soul.radius)
        surface.set_clip(previous_clip)
        pygame.draw.rect(surface, art.PAPER, rect.inflate(6, 6), 3, border_radius=4)
        self.text(
            surface=surface,
            text=arena.pattern.name.upper(),
            position=(104, 310),
            size=18,
            color=art.GOLD,
        )
        # Mode title fits above the box, hint is below, away from moving hazards.
        self.wrapped(
            surface=surface,
            text=arena.pattern.hint,
            rect=pygame.Rect(104, 535, 752, 24),
            size=18,
            color=art.MINT,
        )
        remaining = max(0, arena.pattern.duration - arena.elapsed)
        self.text(
            surface=surface, text=f"{remaining:.1f}s", position=(812, 333), size=20, color=art.GOLD
        )
