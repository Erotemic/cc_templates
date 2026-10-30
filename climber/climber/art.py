"""All art is drawn with pygame shapes. No SVG, Cairo, Pillow, or asset files.

The game scene and HUD are separate: the HUD never covers the ground.
Both are drawn at fixed logical resolution, then scaled to the window.
"""

from __future__ import annotations

from math import cos, floor, pi, sin
from random import Random
from re import finditer

import pygame

from . import settings, student, world
from .engine import Enemy, Game, Pickup


SKY_TOP = (16, 22, 41)
SKY_BOTTOM = (47, 48, 79)
STONE = (67, 64, 89)
STONE_DARK = (40, 43, 66)
STONE_EDGE = (91, 87, 110)
GOLD = (255, 217, 142)
INK = (23, 26, 43)
MINT = (188, 255, 223)


def _shift(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(max(0, min(255, channel + amount)) for channel in color)


class Painter:
    """Draw a complete frame, then letterbox it in a resizable window."""

    def __init__(self) -> None:
        self.scene = pygame.Surface((settings.VIEW_WIDTH, settings.VIEW_HEIGHT))
        self.frame = pygame.Surface(settings.START_WINDOW_SIZE)
        self.font = pygame.font.Font(None, 27)
        self.small_font = pygame.font.Font(None, 21)
        self.big_font = pygame.font.Font(None, 44)
        self.background = self._make_sky()
        self.super_aura = pygame.Surface((112, 112), pygame.SRCALPHA)
        self.show_help = False
        self.audio_label = "N/A"
        self.seconds = 0.0

    @staticmethod
    def _make_sky() -> pygame.Surface:
        image = pygame.Surface((settings.VIEW_WIDTH, settings.VIEW_HEIGHT))
        for y in range(settings.VIEW_HEIGHT):
            t = y / settings.VIEW_HEIGHT
            color = tuple(round(a * (1 - t) + b * t)
                          for a, b in zip(SKY_TOP, SKY_BOTTOM))
            pygame.draw.line(image, color, (0, y), (settings.VIEW_WIDTH, y))
        rng = Random(30)
        for _ in range(160):
            x = rng.randrange(settings.VIEW_WIDTH)
            y = rng.randrange(settings.VIEW_HEIGHT)
            radius = rng.choice((1, 1, 1, 2))
            pygame.draw.circle(image, (104, 118, 153), (x, y), radius)
        pygame.draw.circle(image, (60, 65, 94), (733, 145), 73)
        pygame.draw.circle(image, (247, 222, 171), (729, 140), 54)
        pygame.draw.circle(image, (252, 235, 195), (717, 126), 41)
        return image

    def _draw_wall_bricks(self, left: int, width: int, camera: float) -> None:
        brick_w = 44
        brick_h = 33
        gap = 4
        first = floor(camera / (brick_h + gap)) - 1
        last = floor((camera + settings.VIEW_HEIGHT) / (brick_h + gap)) + 1
        for row in range(first, last + 1):
            y = round(row * (brick_h + gap) - camera)
            offset = 0 if row % 2 else brick_w // 2
            x = left + 6 - offset
            while x < left + width - 8:
                rect = pygame.Rect(x, y, brick_w, brick_h)
                clipped = rect.clip(pygame.Rect(left + 4, -10, width - 8,
                                                settings.VIEW_HEIGHT + 20))
                if clipped.width >= 14 and clipped.height >= 12:
                    pygame.draw.rect(self.scene, STONE_DARK, clipped, width=2)
                    pygame.draw.line(self.scene, (83, 79, 105),
                                     (clipped.left + 5, clipped.top + 5),
                                     (clipped.right - 5, clipped.top + 5))
                x += brick_w + gap

    def _draw_height_markers(self, game: Game) -> None:
        for tier in world.tier_numbers(game.camera_y - 120,
                                       game.camera_y + settings.VIEW_HEIGHT + 120):
            if tier % settings.MARKER_EVERY_TIERS != 0:
                continue
            sy = round(world.platform_y(tier) - game.camera_y)
            if sy < -50 or sy > settings.VIEW_HEIGHT + 10:
                continue
            plate = pygame.Rect(11, sy - 13, 78, 24)
            pygame.draw.rect(self.scene, (90, 78, 69), plate, border_radius=6)
            pygame.draw.rect(self.scene, (182, 152, 108), plate.inflate(-4, -4),
                             border_radius=4)
            label = self.small_font.render(f"{tier * 100:>4}", True, INK)
            self.scene.blit(label, (plate.x + 18, plate.y + 4))
            pygame.draw.circle(self.scene, (75, 58, 51), (plate.x + 9, plate.centery), 2)
            pygame.draw.circle(self.scene, (75, 58, 51), (plate.right - 9, plate.centery), 2)

    def _draw_tower(self, game: Game) -> None:
        canvas = self.scene
        height = settings.VIEW_HEIGHT
        camera = game.camera_y
        left_width = settings.LEFT_WALL
        right_width = settings.VIEW_WIDTH - settings.RIGHT_WALL

        pygame.draw.rect(canvas, STONE, (0, 0, left_width, height))
        pygame.draw.rect(canvas, STONE, (settings.RIGHT_WALL, 0, right_width, height))
        self._draw_wall_bricks(0, left_width, camera)
        self._draw_wall_bricks(settings.RIGHT_WALL, right_width, camera)

        # Inner trims frame the playable shaft and hide any edge bleed.
        pygame.draw.rect(canvas, (109, 104, 124),
                         (settings.LEFT_WALL - 13, 0, 13, height))
        pygame.draw.rect(canvas, (109, 104, 124),
                         (settings.RIGHT_WALL, 0, 13, height))
        pygame.draw.rect(canvas, (53, 56, 79),
                         (settings.LEFT_WALL - 5, 0, 5, height))
        pygame.draw.rect(canvas, (53, 56, 79),
                         (settings.RIGHT_WALL, 0, 5, height))
        pygame.draw.line(canvas, (133, 120, 126),
                         (settings.LEFT_WALL, 0),
                         (settings.LEFT_WALL, height), 2)
        pygame.draw.line(canvas, (133, 120, 126),
                         (settings.RIGHT_WALL, 0),
                         (settings.RIGHT_WALL, height), 2)

        for tier in world.tier_numbers(camera - 160, camera + height + 160):
            if tier % 5 != 0:
                continue
            sy = round(world.platform_y(tier) - camera)
            for x in (settings.LEFT_WALL + 3, settings.RIGHT_WALL - 25):
                pygame.draw.rect(canvas, (44, 45, 69), (x, sy - 155, 20, 138),
                                 border_radius=9)
                pygame.draw.circle(canvas, (117, 94, 93), (x + 10, sy - 24), 11)
                pygame.draw.circle(canvas, GOLD, (x + 10, sy - 24), 5)
                pygame.draw.line(canvas, (155, 119, 111),
                                 (x + 10, sy - 14), (x + 10, sy - 6), 2)

        for x in (194, 754):
            pygame.draw.line(canvas, (54, 60, 79), (x, 0), (x, height), 2)
        self._draw_height_markers(game)

    def _draw_ladders(self, game: Game) -> None:
        ladders = world.ladders_near(game.camera_y - 100,
                                     game.camera_y + settings.VIEW_HEIGHT + 100)
        for ladder in ladders:
            x = round(ladder.x)
            y1 = round(ladder.top - game.camera_y)
            y2 = round(ladder.bottom - game.camera_y)
            for rail in (x, x + ladder.width):
                pygame.draw.line(self.scene, (48, 47, 59),
                                 (rail + 2, y1), (rail + 2, y2), 6)
                pygame.draw.line(self.scene, (191, 139, 89),
                                 (rail, y1), (rail, y2), 4)
            for y in range(y1 + 10, y2 - 2, 19):
                pygame.draw.line(self.scene, (49, 42, 53),
                                 (x, y + 2), (x + ladder.width, y + 2), 6)
                pygame.draw.line(self.scene, (214, 166, 110),
                                 (x + 1, y), (x + ladder.width - 1, y), 4)

    def _draw_platform(self, platform: world.Platform, camera: float) -> None:
        x = round(platform.x)
        y = round(platform.y - camera)
        width = platform.width
        h = platform.height
        surface = self.scene
        pygame.draw.rect(surface, (29, 36, 50),
                         (x + 3, y + 7, width - 3, h + 9),
                         border_radius=5)
        pygame.draw.rect(surface, (90, 86, 91),
                         (x, y + 3, width, h), border_radius=4)
        pygame.draw.rect(surface, (152, 113, 84),
                         (x, y + 2, width, h - 4), border_radius=3)
        moving = platform.kind == "moving"
        top_color = ((104, 193, 241) if moving else student.PLATFORM_COLOR)
        pygame.draw.rect(surface, top_color,
                         (x - 2, y, width + 4, 7), border_radius=3)
        for px in range(x + 18, x + width - 10, 33):
            pygame.draw.line(surface, (99, 73, 72),
                             (px, y + 8), (px, y + h - 2), 2)
        for px in range(x + 12, x + width - 4, 37):
            pygame.draw.line(surface, _shift(top_color, 35),
                             (px, y), (px + 5, y - 5), 2)
        if moving:
            cx = x + width // 2
            pygame.draw.line(surface, (42, 65, 97),
                             (cx - 17, y + 11), (cx + 17, y + 11), 3)
            pygame.draw.polygon(surface, (42, 65, 97),
                                [(cx - 19, y + 11), (cx - 10, y + 6),
                                 (cx - 10, y + 16)])
            pygame.draw.polygon(surface, (42, 65, 97),
                                [(cx + 19, y + 11), (cx + 10, y + 6),
                                 (cx + 10, y + 16)])
        if platform.kind == "side":
            pygame.draw.circle(surface, GOLD, (x + width // 2, y - 5), 4)

    def _draw_pickup(self, pickup: Pickup, camera: float) -> None:
        if pickup.collected:
            return
        x = round(pickup.x)
        y = round(pickup.y - camera)
        if y < -30 or y > settings.VIEW_HEIGHT + 30:
            return
        rect = pygame.Rect(x, y, pickup.width, pickup.height)
        color = (255, 112, 158) if pickup.kind == "heart" else GOLD
        glow = (255, 188, 214) if pickup.kind == "heart" else (255, 240, 190)
        pygame.draw.ellipse(self.scene, _shift(color, -90), rect.inflate(10, 10), 1)
        if pickup.kind == "heart":
            cx = rect.centerx
            cy = rect.centery - 1
            pygame.draw.circle(self.scene, color, (cx - 4, cy), 4)
            pygame.draw.circle(self.scene, color, (cx + 4, cy), 4)
            pygame.draw.polygon(self.scene, color,
                                [(cx - 8, cy + 2), (cx + 8, cy + 2), (cx, cy + 12)])
        else:
            points = [(rect.centerx, rect.top), (rect.right, rect.centery),
                      (rect.centerx, rect.bottom), (rect.left, rect.centery)]
            pygame.draw.polygon(self.scene, color, points)
            pygame.draw.polygon(self.scene, glow,
                                [(rect.centerx, rect.top + 2), (rect.right - 2, rect.centery),
                                 (rect.centerx, rect.centery + 1), (rect.left + 2, rect.centery)])
        pygame.draw.line(self.scene, glow, (rect.centerx, rect.top - 6),
                         (rect.centerx, rect.top - 1), 1)
        pygame.draw.line(self.scene, glow, (rect.left - 5, rect.centery),
                         (rect.left - 1, rect.centery), 1)
        pygame.draw.line(self.scene, glow, (rect.right + 1, rect.centery),
                         (rect.right + 5, rect.centery), 1)

    def _draw_ground(self, game: Game) -> None:
        y = round(settings.GROUND_Y - game.camera_y)
        if y >= settings.VIEW_HEIGHT or y < -70:
            return
        pygame.draw.rect(self.scene, (69, 66, 83),
                         (settings.LEFT_WALL, y, settings.RIGHT_WALL - settings.LEFT_WALL,
                          settings.VIEW_HEIGHT - y))
        pygame.draw.line(self.scene, student.PLATFORM_COLOR,
                         (settings.LEFT_WALL, y), (settings.RIGHT_WALL, y), 8)
        for x in range(settings.LEFT_WALL + 18, settings.RIGHT_WALL, 50):
            pygame.draw.rect(self.scene, (50, 51, 69),
                             (x, y + 17, 38, 25), width=2)

    def _draw_enemy(self, enemy: Enemy, camera: float) -> None:
        x = round(enemy.x)
        y = round(enemy.y - camera)
        rect = pygame.Rect(x, y, enemy.width, enemy.height)
        pygame.draw.ellipse(self.scene, (32, 34, 51), rect.move(2, 4))
        pygame.draw.ellipse(self.scene, (214, 99, 144), rect)
        pygame.draw.ellipse(self.scene, (245, 149, 171),
                            (x + 4, y + 3, enemy.width - 10, 8))
        for dx in (7, 18):
            pygame.draw.circle(self.scene, (33, 39, 56), (x + dx, y + 12), 3)
            pygame.draw.circle(self.scene, (253, 241, 221),
                               (x + dx - 1, y + 11), 1)

    def _draw_super_aura(self, game: Game) -> None:
        """A small animated, world-anchored glow around the powered-up hero."""
        player = game.player
        cx = round(player.x + settings.PLAYER_WIDTH / 2)
        cy = round(player.y - game.camera_y + settings.PLAYER_HEIGHT / 2)
        layer = self.super_aura
        layer.fill((0, 0, 0, 0))
        center = (56, 56)
        pulse = sin(self.seconds * 5)
        pygame.draw.circle(layer, (88, 221, 249, 26), center, 43)
        pygame.draw.circle(layer, (118, 231, 253, 84), center,
                           32 + round(3 * pulse), 4)
        pygame.draw.circle(layer, (252, 224, 145, 215), center,
                           37 + round(2 * sin(self.seconds * 3)), 2)
        for index in range(8):
            angle = self.seconds * 1.7 + (2 * pi * index / 8)
            radius = 38 + 3 * sin(self.seconds * 4 + index)
            sx = round(center[0] + radius * cos(angle))
            sy = round(center[1] + radius * sin(angle))
            color = (255, 236, 157, 230) if index % 2 else (151, 247, 255, 220)
            pygame.draw.circle(layer, color, (sx, sy), 2 + index % 2)
        self.scene.blit(layer, (cx - 56, cy - 56))

    def _draw_player(self, game: Game) -> None:
        player = game.player
        if (not game.super_mode and player.invulnerable_time > 0
                and int(player.invulnerable_time * 12) % 2 == 0):
            return
        x = round(player.x)
        y = round(player.y - game.camera_y)
        if game.super_mode:
            self._draw_super_aura(game)
        moving = abs(player.vx) > 0 and player.on_ground
        stride = round(3 * sin(self.seconds * 17)) if moving else 0

        pygame.draw.polygon(self.scene, (48, 103, 132),
                            [(x + 8, y + 15), (x - 3, y + 32),
                             (x + 8, y + 28)])
        pygame.draw.rect(self.scene, (38, 46, 66),
                         (x + 4, y + 26, 9, 11 + stride), border_radius=2)
        pygame.draw.rect(self.scene, (38, 46, 66),
                         (x + 17, y + 26, 9, 11 - stride), border_radius=2)
        pygame.draw.rect(self.scene, student.HERO_COLOR,
                         (x + 3, y + 12, 24, 17), border_radius=5)
        pygame.draw.rect(self.scene, (237, 223, 198),
                         (x + 7, y + 5, 16, 13), border_radius=5)
        pygame.draw.circle(self.scene, (34, 40, 58), (x + 12, y + 11), 2)
        pygame.draw.circle(self.scene, (34, 40, 58), (x + 19, y + 11), 2)
        pygame.draw.arc(self.scene, (34, 40, 58), (x + 10, y + 10, 10, 8),
                        0.15, 2.95, 1)
        pygame.draw.rect(self.scene, (224, 180, 72), (x + 8, y + 2, 14, 5), 0, 2)
        pygame.draw.circle(self.scene, (255, 245, 185), (x + 15, y + 4), 3)
        pygame.draw.circle(self.scene, (255, 245, 185, ), (x + 15, y + 4), 9, 1)

    def _heckler_bubble_layout(self, game: Game):
        """Position speech RELATIVE TO THE HECKLER, not to the screen.

        Return the rectangle and (original-string-offset, line) pairs. Using
        offsets lets the full bubble size stay fixed while letters type out.
        """
        heckler = game.heckler
        if not heckler.text:
            return None

        words = list(finditer(r"\S+", heckler.text))
        if not words:
            return None
        lines = []
        start = words[0].start()
        last_end = words[0].end()
        for match in words[1:]:
            candidate = heckler.text[start:match.end()]
            if self.small_font.size(candidate)[0] > 310:
                lines.append((start, heckler.text[start:last_end]))
                start = match.start()
            last_end = match.end()
        lines.append((start, heckler.text[start:last_end]))

        max_width = max(self.small_font.size(line)[0] for _, line in lines)
        line_height = self.small_font.get_linesize()
        box = pygame.Rect(0, 0, max_width + 20,
                          line_height * len(lines) + 14)
        box.right = round(heckler.platform_x) - 12
        box.centery = round(heckler.y - game.camera_y) + 12
        return box, lines

    def _draw_heckler(self, game: Game) -> None:
        heckler = game.heckler
        shaft_x = settings.RIGHT_WALL - 58
        pygame.draw.line(self.scene, (81, 92, 116),
                         (shaft_x, 0), (shaft_x, settings.VIEW_HEIGHT), 3)
        pygame.draw.line(self.scene, (81, 92, 116),
                         (shaft_x + 32, 0), (shaft_x + 32, settings.VIEW_HEIGHT), 3)

        y = round(heckler.y - game.camera_y)
        platform = pygame.Rect(round(heckler.platform_x), round(heckler.platform_y - game.camera_y),
                               heckler.platform_width, heckler.platform_height)
        pygame.draw.rect(self.scene, (48, 56, 77), platform.move(2, 4), border_radius=4)
        pygame.draw.rect(self.scene, (112, 145, 171), platform, border_radius=4)
        pygame.draw.line(self.scene, (174, 208, 232),
                         (platform.left + 4, platform.top + 4),
                         (platform.right - 4, platform.top + 4), 2)

        x = round(heckler.x)
        pygame.draw.rect(self.scene, (63, 37, 71), (x + 4, y + 18, 18, 12), border_radius=4)
        pygame.draw.rect(self.scene, (151, 88, 168), (x + 2, y + 12, 21, 12), border_radius=5)
        pygame.draw.circle(self.scene, (235, 214, 196), (x + 13, y + 8), 8)
        pygame.draw.circle(self.scene, (40, 34, 54), (x + 10, y + 7), 1)
        pygame.draw.circle(self.scene, (40, 34, 54), (x + 16, y + 7), 1)
        pygame.draw.arc(self.scene, (40, 34, 54), (x + 9, y + 8, 8, 4), 3.2, 6.0, 1)
        pygame.draw.line(self.scene, (181, 122, 85),
                         (x + 4, y + 19), (x + 0, y + 24), 2)
        pygame.draw.line(self.scene, (181, 122, 85),
                         (x + 22, y + 19), (x + 26, y + 24), 2)

        # The bubble is transient. Its screen position is recomputed from
        # heckler.world_y - camera_y every frame, like the elevator itself.
        # No fixed top clamp: that was why the old bubble looked stuck.
        layout = self._heckler_bubble_layout(game)
        if layout is not None and -heckler.height <= y <= settings.VIEW_HEIGHT:
            box, lines = layout
            pygame.draw.rect(self.scene, (247, 238, 219), box,
                             border_radius=10)
            pygame.draw.rect(self.scene, (176, 160, 139), box,
                             width=2, border_radius=10)
            # Tail points at the speaker's face, not a screen-fixed point.
            tail_y = y + 12
            edge_y = max(box.top + 9, min(box.bottom - 9, tail_y))
            tip = (platform.left - 4, tail_y)
            pygame.draw.polygon(self.scene, (247, 238, 219),
                                [(box.right - 2, edge_y - 6), tip,
                                 (box.right - 2, edge_y + 6)])
            pygame.draw.lines(self.scene, (176, 160, 139), False,
                              [(box.right - 2, edge_y - 6), tip,
                               (box.right - 2, edge_y + 6)], 2)
            for row, (offset, line) in enumerate(lines):
                shown = max(0, min(len(line), heckler.revealed - offset))
                if shown:
                    label = self.small_font.render(line[:shown], True, INK)
                    self.scene.blit(label, (box.x + 10,
                                            box.y + 7 + row * self.small_font.get_linesize()))

    def _draw_hazard(self, game: Game) -> None:
        sy = round(game.hazard_y - game.camera_y)
        if sy < settings.VIEW_HEIGHT + 40:
            points = []
            for x in range(105, 856, 16):
                wave = sin(x * 0.035 + self.seconds * 3) * 4
                points.append((x, sy + round(wave)))
            if len(points) > 1:
                pygame.draw.lines(self.scene, (240, 124, 177), False, points, 5)
                pygame.draw.lines(self.scene, (251, 189, 198), False,
                                  [(x, y - 3) for x, y in points], 2)
            for x in range(155, 855, 96):
                y = sy + 20 + round(5 * sin(x + self.seconds * 2))
                pygame.draw.circle(self.scene, (130, 74, 116), (x, y), 7, 2)

    def _draw_hud(self, game: Game) -> None:
        top = settings.VIEW_HEIGHT
        width = settings.VIEW_WIDTH
        pygame.draw.rect(self.frame, INK,
                         (0, top, width, settings.HUD_HEIGHT))
        pygame.draw.line(self.frame, (119, 165, 165), (0, top), (width, top), 2)
        self.frame.blit(self.font.render(student.GAME_TITLE, True, (231, 237, 239)),
                        (19, top + 9))
        self.frame.blit(self.small_font.render("A/D: move    SPACE: jump    W/S: ladder*",
                                               True, (169, 182, 195)), (20, top + 38))
        altitude = max(0, round(settings.GROUND_Y - game.player.bottom))
        label = (f"HEIGHT {altitude:>5}   BEST {game.highest_tier:>3}"
                 f"   LOOT {game.pickups_collected:>2}")
        self.frame.blit(self.font.render(label, True, (255, 217, 142)),
                        (405, top + 10))
        for heart in range(game.hearts):
            x = 791 + heart * 29
            pygame.draw.circle(self.frame, (244, 120, 148), (x, top + 20), 8)
            pygame.draw.circle(self.frame, (244, 120, 148), (x + 10, top + 20), 8)
            pygame.draw.polygon(self.frame, (244, 120, 148),
                                [(x - 8, top + 24), (x + 18, top + 24),
                                 (x + 5, top + 42)])
        hint = f"H: missions   R: restart   M: sound {self.audio_label}   ESC: quit"
        self.frame.blit(self.small_font.render(hint, True, (169, 182, 195)),
                        (436, top + 44))

    def _draw_help(self) -> None:
        shade = pygame.Surface((settings.VIEW_WIDTH, settings.VIEW_HEIGHT),
                               pygame.SRCALPHA)
        shade.fill((10, 15, 31, 222))
        self.scene.blit(shade, (0, 0))
        title = self.big_font.render("EIGHT MISSIONS TO BUILD", True, GOLD)
        self.scene.blit(title, (212, 74))
        lines = [
            "1  WALL JUMP       Launch off the tower walls",
            "2  LADDERS            Climb with W / S",
            "3  ENEMIES            Make pink creatures patrol",
            "4  RISING FLOOR   Make the purple danger rise",
            "5  MOVING LEDGES Animate the blue platforms",
            "6  TOWER HEIGHTS Change the ledge spacing",
            "7  PICKUPS            Decide what treasure does",
            "8  FALL COMEBACK  Mock the player's return",
            "",
            "Bonus: edit student.heckler_line() and climber/synth.py.",
            "Start in climber/student.py. Flip if False to if True.",
            "",
            "Press M to mute music. H closes this panel.",
        ]
        for index, line in enumerate(lines):
            label = self.font.render(line, True, (235, 241, 245))
            self.scene.blit(label, (147, 132 + index * 29))

    def draw(self, game: Game, window: pygame.Surface, seconds: float) -> None:
        self.seconds += seconds
        self.scene.blit(self.background, (0, 0))
        self._draw_tower(game)
        self._draw_ladders(game)
        platforms = (world.platforms_near(
            game.camera_y - 40, game.camera_y + settings.VIEW_HEIGHT + 40)
            + game.nearby_moving_platforms())
        for platform in platforms:
            self._draw_platform(platform, game.camera_y)
        for pickup in game.nearby_pickups():
            self._draw_pickup(pickup, game.camera_y)
        self._draw_ground(game)
        for enemy in game.nearby_enemies():
            self._draw_enemy(enemy, game.camera_y)
        self._draw_player(game)
        self._draw_heckler(game)
        self._draw_hazard(game)
        if self.show_help:
            self._draw_help()
        self.frame.blit(self.scene, (0, 0))
        self._draw_hud(game)
        self._present(window)

    def _present(self, window: pygame.Surface) -> None:
        win_w, win_h = window.get_size()
        if win_w == 0 or win_h == 0:
            return
        base_w, base_h = settings.START_WINDOW_SIZE
        scale = min(win_w / base_w, win_h / base_h)
        output = (max(1, int(base_w * scale)),
                  max(1, int(base_h * scale)))
        picture = (self.frame if output == (base_w, base_h)
                   else pygame.transform.smoothscale(self.frame, output))
        window.fill((10, 13, 24))
        window.blit(picture, ((win_w - output[0]) // 2,
                              (win_h - output[1]) // 2))
        pygame.display.flip()
