"""All visuals are drawn with pygame shapes. No images or asset downloads."""

from __future__ import annotations

import math
import random

from . import levels, settings, student


class Painter:
    def __init__(self, pygame):
        self.pg = pygame
        self.font = pygame.font.SysFont("dejavusans", 17)
        self.small = pygame.font.SysFont("dejavusans", 13)
        self.big = pygame.font.SysFont("dejavusans", 42, bold=True)
        self.help = False
        self.trail = []
        rng = random.Random(401)
        self.stars = [(rng.randrange(settings.WIDTH), rng.randrange(360),
                       rng.choice((1, 1, 1, 2))) for _ in range(75)]

    def label(self, surface, words, xy, color=(230, 237, 252), *, small=False):
        f = self.small if small else self.font
        surface.blit(f.render(words, True, color), xy)

    def background(self, surface, game, t):
        pg = self.pg
        sky = student.SKY_COLOR
        surface.fill(sky)
        # Discrete mountain ridges give spatial depth without external art.
        room_index = list(game.rooms).index(game.room_key)
        for index, star in enumerate(self.stars):
            x, y, radius = star
            brightness = 100 + int(35 * (1 + math.sin(t * 1.7 + index)))
            pg.draw.circle(surface, (brightness, brightness + 17, min(255, brightness + 52)),
                           (x, y), radius)
        for layer, base, height, color in (
            (0, 360, 72, (31, 43, 75)),
            (1, 402, 98, (40, 55, 85)),
            (2, 461, 88, (52, 68, 96)),
        ):
            points = [(-20, settings.HEIGHT), (-20, base)]
            for x in range(-20, settings.WIDTH + 50, 54):
                wave = abs(math.sin(x * 0.011 + layer * 1.43 + room_index * 0.6))
                points.append((x, base - int(wave * height)))
            points.extend([(settings.WIDTH + 20, settings.HEIGHT)])
            pg.draw.polygon(surface, color, points)

    def tile(self, surface, col, row, symbol, game, seconds):
        pg = self.pg
        t = settings.TILE
        x, y = col * t, row * t
        r = pg.Rect(x, y, t, t)
        if symbol == "#":
            pg.draw.rect(surface, (76, 92, 121), r)
            pg.draw.rect(surface, (109, 126, 155), (x, y, t, 4))
            pg.draw.line(surface, (58, 73, 104), (x, y + 28), (x + t, y + 28), 2)
            if (col * 3 + row * 7) % 5 == 0:
                pg.draw.line(surface, (61, 77, 106), (x + 8, y + 13), (x + 17, y + 13), 2)
        elif symbol == "b" and not game.blocks[(col, row)].broken:
            pg.draw.rect(surface, (137, 105, 110), r.inflate(-2, -2), border_radius=3)
            pg.draw.line(surface, (225, 166, 139), (x + 6, y + 3), (x + 26, y + 3), 3)
            pg.draw.line(surface, (89, 66, 87), (x + 16, y + 11), (x + 21, y + 21), 2)
            pg.draw.line(surface, (89, 66, 87), (x + 21, y + 21), (x + 14, y + 27), 2)
            block = game.blocks[(col, row)]
            if block.timer:
                pg.draw.rect(surface, (255, 170, 156),
                             (x + 2, y + 27, int(28 * min(block.timer / 0.45, 1)), 3))
        elif symbol == "^":
            pg.draw.polygon(surface, (255, 124, 155),
                            [(x + 3, y + 29), (x + 12, y + 5), (x + 20, y + 29)])
            pg.draw.polygon(surface, (255, 163, 171),
                            [(x + 15, y + 28), (x + 24, y + 7), (x + 30, y + 28)])
        elif symbol == "*" and (col, row) not in game.collected_berries:
            wobble = math.sin(seconds * 3.5 + col) * 2
            cx, cy = x + 16, round(y + 17 + wobble)
            pg.draw.circle(surface, (245, 91, 150), (cx, cy), 9)
            pg.draw.circle(surface, (255, 158, 176), (cx - 3, cy - 3), 3)
            pg.draw.polygon(surface, (91, 219, 169),
                            [(cx - 3, cy - 8), (cx + 1, cy - 15), (cx + 7, cy - 10)])
        elif symbol == "R" and (col, row) not in game.used_crystals:
            cy = round(y + 16 + math.sin(seconds * 4 + col) * 3)
            pg.draw.polygon(surface, (185, 138, 255),
                            [(x + 16, cy - 13), (x + 26, cy),
                             (x + 16, cy + 13), (x + 6, cy)])
            pg.draw.polygon(surface, (235, 207, 255),
                            [(x + 16, cy - 11), (x + 16, cy + 11), (x + 8, cy)])
        elif symbol == "C":
            active = game.checkpoint[0] == x + (t - settings.PLAYER_W) / 2
            color = (139, 245, 187) if active else (119, 182, 192)
            pg.draw.line(surface, (161, 182, 205), (x + 12, y + 29), (x + 12, y + 4), 3)
            pg.draw.polygon(surface, color,
                            [(x + 13, y + 6), (x + 29, y + 10), (x + 13, y + 19)])
        elif symbol == "G":
            pg.draw.rect(surface, (95, 214, 198), (x + 4, y + 3, 24, 29),
                         width=3, border_top_left_radius=11, border_top_right_radius=11)
            pg.draw.rect(surface, (39, 78, 98), (x + 8, y + 8, 16, 24),
                         border_top_left_radius=7, border_top_right_radius=7)
            pg.draw.circle(surface, (255, 235, 170), (x + 20, y + 22), 2)
        elif symbol == "w":
            # Animated visual cue; the student chooses whether it pushes.
            for dy in (7, 15, 23):
                slide = int((seconds * 35 + dy * 3) % 24)
                pg.draw.line(surface, (104, 223, 231),
                             (x + 2 + slide // 2, y + dy),
                             (x + 6 + slide // 2, y + dy - 3), 2)

    def player(self, surface, player, seconds):
        pg = self.pg
        p = player
        px, py = int(p.x), int(p.y)
        if p.dash_time > 0:
            self.trail.append((px, py, 0.18))
        self.trail = [(x, y, ttl - 1 / 60) for x, y, ttl in self.trail if ttl > 1 / 60][-12:]
        for x, y, ttl in self.trail:
            ghost = pg.Surface((settings.PLAYER_W, settings.PLAYER_H), pg.SRCALPHA)
            pg.draw.rect(ghost, (*student.HERO_COLOR, round(90 * ttl / 0.18)),
                         ghost.get_rect(), border_radius=6)
            surface.blit(ghost, (x, y))
        scarf_direction = -p.facing
        pg.draw.polygon(surface, student.SCARF_COLOR,
                        [(px + 10, py + 8),
                         (px + 10 + 10 * scarf_direction, py + 10),
                         (px + 10 + 14 * scarf_direction,
                          py + 18 + math.sin(seconds * 8) * 2)])
        pg.draw.rect(surface, (35, 48, 78), (px - 2, py + 4, 24, 24), border_radius=7)
        pg.draw.rect(surface, student.HERO_COLOR, (px, py, 20, 23), border_radius=6)
        pg.draw.rect(surface, (255, 248, 219), (px + 3, py + 4, 14, 10), border_radius=3)
        eye_x = px + (12 if p.facing > 0 else 5)
        pg.draw.rect(surface, (44, 58, 82), (eye_x, py + 8, 3, 3))
        if p.dashes:
            pg.draw.line(surface, (152, 239, 241), (px + 5, py + 2), (px + 15, py + 2), 2)
        pg.draw.rect(surface, (55, 65, 87), (px + 2, py + 21, 6, 5), border_radius=2)
        pg.draw.rect(surface, (55, 65, 87), (px + 12, py + 21, 6, 5), border_radius=2)

    def draw(self, surface, game, seconds, *, paused=False, muted=False):
        pg = self.pg
        self.background(surface, game, seconds)
        t = settings.TILE
        for row, line in enumerate(game.room.tiles):
            for col, symbol in enumerate(line):
                if symbol in "#b^*RCGw":
                    self.tile(surface, col, row, symbol, game, seconds)
        for ledge in game.ledges:
            pg.draw.rect(surface, (124, 171, 163),
                         pg.Rect(round(ledge.x), round(ledge.y), round(ledge.w), 8),
                         border_radius=3)
            pg.draw.line(surface, (181, 235, 198),
                         (round(ledge.x) + 2, round(ledge.y) + 1),
                         (round(ledge.right) - 2, round(ledge.y) + 1), 2)
        for platform in game.platforms:
            pg.draw.rect(surface, (76, 156, 200),
                         pg.Rect(round(platform.x), round(platform.y),
                                 round(platform.w), 10), border_radius=3)
            pg.draw.line(surface, (141, 222, 246),
                         (round(platform.x) + 3, round(platform.y) + 2),
                         (round(platform.x + platform.w) - 3, round(platform.y) + 2), 2)
        self.player(surface, game.player, seconds)

        # HUD is BELOW gameplay so it cannot obscure the ground or spikes.
        pg.draw.rect(surface, (13, 22, 42),
                     (0, settings.HEIGHT, settings.WIDTH, settings.HUD_HEIGHT))
        pg.draw.line(surface, (94, 118, 158),
                     (0, settings.HEIGHT), (settings.WIDTH, settings.HEIGHT), 2)
        self.label(surface, student.GAME_TITLE, (18, settings.HEIGHT + 9),
                   (164, 232, 246))
        self.label(surface, game.room.name, (170, settings.HEIGHT + 9))
        self.label(surface, f"DASH {'READY' if game.player.dashes else 'USED'}",
                   (445, settings.HEIGHT + 9),
                   (152, 241, 201) if game.player.dashes else (239, 150, 170))
        self.label(surface, f"BERRIES {game.berries}", (612, settings.HEIGHT + 9))
        self.label(surface, game.room.hint, (18, settings.HEIGHT + 39),
                   (177, 191, 214), small=True)
        self.label(surface, f"DEATHS {game.deaths}  TIME {game.elapsed:05.1f}",
                   (546, settings.HEIGHT + 38), (173, 193, 210), small=True)
        self.label(surface, "H: help   R: restart   M: mute", (18, 9),
                   (185, 194, 220), small=True)
        if game.finished or self.help or paused:
            shade = pg.Surface((settings.WIDTH, settings.HEIGHT), pg.SRCALPHA)
            shade.fill((7, 14, 29, 211))
            surface.blit(shade, (0, 0))
            if game.finished:
                title = "SUMMIT REACHED"
                lines = ["You made it through all four rooms.",
                         "Your next challenge: invent room five.",
                         "Press R to play again.  Esc to quit."]
            elif paused:
                title = "PAUSED"
                lines = ["Press P to resume.", "H: help   M: mute   R: restart"]
            else:
                title = "HOW TO PLAY"
                lines = ["A / D or Left / Right : walk",
                         "Space or Z : jump (hold longer for a higher jump)",
                         "X or Left Shift : dash (8 directions with WASD / arrows)",
                         "Jump into a wall, then jump again to kick off.",
                         "Land to get your dash back. C flags save progress.",
                         "Spikes and gaps respawn you. R restarts this room.",
                         "M : mute    P : pause    H : close help",
                         "Edit peakshift/student.py to build the other mechanics."]
            text = self.big.render(title, True, (169, 236, 246))
            surface.blit(text, (settings.WIDTH // 2 - text.get_width() // 2, 96))
            for index, line in enumerate(lines):
                t = self.font.render(line, True, (238, 235, 243))
                surface.blit(t, (settings.WIDTH // 2 - t.get_width() // 2,
                                 173 + index * 31))
        if muted:
            self.label(surface, "MUTED", (settings.WIDTH - 61, 8), (230, 161, 176), small=True)
