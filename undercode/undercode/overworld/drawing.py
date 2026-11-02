"""Draw only the overworld. Read World.update to find the rules behind this picture."""

import math
import pygame
from .. import art
from ..presentation import UI
from ..settings import WIDTH, HEIGHT
from .engine import TILE, tile_center
from .model import Rest, Sign, Item, Trigger


class WorldView(UI):
    """Translate room pixels to screen pixels, then draw the HUD and conversation."""

    def draw(self, *, surface, world, time, sound_label, technique_name):
        """Draw terrain, story objects, characters, the student-selected view, and HUD.

        Center smaller rooms in the logical viewport and translate room-pixel
        positions by that origin. Read world.player_view, chosen in World.move. Student rules run during
        the update, so drawing the same state twice cannot change the game.
        """
        self.header(surface=surface, subtitle=world.room.name, sound=sound_label)
        left = (WIDTH - len(world.room.tiles[0]) * TILE) // 2
        top = 86 + (512 - len(world.room.tiles) * TILE) // 2
        origin = pygame.Vector2(left, top)
        for row, line in enumerate(world.room.tiles):
            for column, tile in enumerate(line):
                x, y = left + column * TILE, top + row * TILE
                rect = pygame.Rect(x, y, TILE, TILE)
                variation = (column * 17 + row * 7) % 9
                if tile == "#":
                    pygame.draw.rect(surface, (24, 47, 54), rect)
                    pygame.draw.circle(
                        surface, (41 + variation, 75 + variation, 74), rect.center, 20
                    )
                    pygame.draw.circle(surface, (56, 96, 84), (x + 11, y + 9), 11)
                elif tile == "~":
                    pygame.draw.rect(surface, (39, 68, 92), rect)
                    offset = math.sin(time * 1.3 + column) * 4
                    pygame.draw.line(
                        surface,
                        (71, 107, 126),
                        (x + 5 + offset, y + 15),
                        (x + 22 + offset, y + 15),
                        2,
                    )
                elif tile == "d":
                    pygame.draw.rect(surface, (130, 105, 80), rect)
                    for dy in (5, 15, 25):
                        pygame.draw.line(surface, (84, 75, 66), (x, y + dy), (x + TILE, y + dy), 2)
                elif tile in ".D":
                    pygame.draw.rect(
                        surface, (95 + variation, 102 + variation, 106 + variation), rect
                    )
                    pygame.draw.rect(
                        surface,
                        (110 + variation, 117 + variation, 119 + variation),
                        rect.inflate(-3, -3),
                        1,
                        border_radius=4,
                    )
                    if tile == "D":
                        pygame.draw.line(surface, art.MINT, (x + 8, y + 16), (x + 24, y + 16), 3)
                else:
                    pygame.draw.rect(surface, (49 + variation, 81 + variation, 75), rect)
                    if (column + row * 3) % 9 == 0:
                        pygame.draw.line(
                            surface, (83, 118, 94), (x + 10, y + 24), (x + 12, y + 18), 2
                        )
                        pygame.draw.line(
                            surface, (83, 118, 94), (x + 12, y + 24), (x + 16, y + 19), 2
                        )
        # Lamps are deterministic decoration: drawing consumes no encounter RNG.
        for x, y in ((48, 132), (912, 132), (48, 552), (912, 552)):
            pygame.draw.line(surface, (46, 43, 52), (x, y), (x, y + 35), 4)
            pygame.draw.rect(surface, art.GOLD, (x - 7, y - 7, 14, 18), border_radius=4)
            pygame.draw.line(surface, art.PAPER, (x - 3, y - 3), (x - 3, y + 4), 2)
        for obj in world.visible_objects():
            point = tile_center(tile=obj.tile) + origin
            if isinstance(obj.definition, Rest):
                pygame.draw.ellipse(surface, (39, 62, 73), (point.x - 20, point.y - 5, 40, 20))
                pygame.draw.ellipse(
                    surface, (110, 179, 170), (point.x - 16, point.y - 8, 32, 15), 3
                )
                art.star(
                    surface=surface,
                    center=(point.x, point.y - 14),
                    radius=10 + math.sin(time * 3),
                    color=art.GOLD,
                )
            elif isinstance(obj.definition, Sign):
                pygame.draw.line(surface, art.GOLD, point, point + (0, 13), 4)
                self.panel(
                    surface=surface, rect=pygame.Rect(point.x - 13, point.y - 14, 26, 22), radius=3
                )
                self.text(
                    surface=surface,
                    text="?",
                    position=(point.x, point.y - 4),
                    size=22,
                    color=art.PAPER,
                    center=True,
                )
            elif isinstance(obj.definition, Item):
                art.star(
                    surface=surface,
                    center=point + (0, math.sin(time * 3) * 3),
                    radius=11,
                    color=art.GOLD,
                )
            elif isinstance(obj.definition, Trigger):
                pygame.draw.ellipse(surface, art.MINT, (point.x - 12, point.y + 2, 24, 8), 2)
        for person in sorted(world.room.people, key=lambda p: p.tile[1]):
            character = person.definition
            point = tile_center(tile=person.tile) + origin + (0, -5)
            pygame.draw.ellipse(surface, (29, 51, 58), (point.x - 18, point.y + 12, 36, 12))
            character.portrait(surface=surface, center=point, scale=0.4, time=time)
            self.text(
                surface=surface,
                text=character.name,
                position=(point.x, point.y + 34),
                size=18,
                color=art.PAPER,
                center=True,
            )
            if person.key in world.session.resolved:
                art.star(
                    surface=surface, center=(point.x + 23, point.y - 23), radius=6, color=art.MINT
                )
        art.courier(
            surface=surface,
            center=world.position + origin,
            time=world.walk_time,
            walking=world.moving,
            view=world.player_view,
        )
        nearby = world.interactable()
        if nearby and not world.talking and not world.dialogue:
            point = tile_center(tile=nearby.tile) + origin + (0, -44)
            self.panel(
                surface=surface,
                rect=pygame.Rect(point.x - 38, point.y - 13, 76, 25),
                border=art.MINT,
                radius=7,
            )
            self.text(
                surface=surface,
                text="Z: use",
                position=point,
                size=18,
                color=art.PAPER,
                center=True,
            )
        hud = pygame.Rect(20, 615, 920, 86)
        self.panel(surface=surface, rect=hud)
        if world.talking:
            person = world.talking
            character = person.definition
            self.text(
                surface=surface,
                text=character.name,
                position=(36, 625),
                size=24,
                color=art.MINT,
            )
            self.wrapped(
                surface=surface,
                text=world.conversation_text(person=person),
                rect=pygame.Rect(170, 625, 745, 61),
                size=24,
            )
        else:
            player = world.session.player
            self.text(
                surface=surface, text=player.name, position=(37, 627), size=24, color=art.CORAL
            )
            self.text(
                surface=surface, text=f"HP {player.hp}/{player.max_hp}", position=(37, 657), size=22
            )
            self.bar(
                surface=surface,
                rect=pygame.Rect(144, 658, 130, 13),
                fraction=player.hp / player.max_hp,
                color=art.CORAL,
            )
            self.text(
                surface=surface,
                text=f"{len(world.session.resolved)}/{world.encounter_count} encounters",
                position=(310, 627),
                size=22,
                color=art.MINT,
            )
            self.text(
                surface=surface,
                text="Tab: " + technique_name,
                position=(310, 657),
                size=20,
                color=art.MUTED,
            )
            message = (
                world.toast
                if world.toast_time
                else "Arrows / WASD: walk. Z: talk / rest. Find the north path."
            )
            self.wrapped(
                surface=surface,
                text=message,
                rect=pygame.Rect(552, 627, 365, 59),
                size=20,
                color=art.PAPER,
            )

        if world.dialogue:
            self.draw_story(surface=surface, dialogue=world.dialogue)

    def draw_story(self, *, surface, dialogue):
        """Draw a paged world conversation and at most three choices around its selection.

        Read Dialogue state only; its update method commits choices/flags.
        Dim the world and keep text, choices, and navigation hints in separate areas.
        """
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((12, 16, 30, 155))
        surface.blit(veil, (0, 0))
        self.panel(surface=surface, rect=pygame.Rect(92, 365, 776, 337), border=art.MINT)
        self.text(surface=surface, text=dialogue.name, position=(112, 382), size=28, color=art.MINT)
        self.wrapped(
            surface=surface,
            text=dialogue.pages[dialogue.page],
            rect=pygame.Rect(112, 420, 732, 94),
            size=26,
        )
        if dialogue.choosing:
            start = max(0, dialogue.selection - 2)
            for index in range(start, min(start + 3, len(dialogue.choices))):
                y = 521 + (index - start) * 48
                chosen = index == dialogue.selection
                rect = pygame.Rect(112, y, 732, 46)
                if chosen:
                    self.panel(surface=surface, rect=rect, border=art.GOLD, radius=5)
                self.wrapped(
                    surface=surface,
                    text=dialogue.choices[index].label,
                    rect=pygame.Rect(130, y + 2, 694, 44),
                    size=22,
                    color=art.GOLD if chosen else art.PAPER,
                )
            hint = f"Arrows: choose  {dialogue.selection + 1}/{len(dialogue.choices)}   Z: select   X: close"
        else:
            hint = f"Page {dialogue.page + 1}/{len(dialogue.pages)}   Z: continue   X: close"
        self.text(surface=surface, text=hint, position=(112, 680), size=18, color=art.MUTED)
