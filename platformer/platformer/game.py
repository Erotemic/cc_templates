"""The raw pygame loop for Little Platformer.

Read main() for keyboard input and Game.step() for gameplay rules.
Optional guided missions can add a following camera, boss, and transitions;
with untouched student.py the original three-level game still runs.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from math import cos, pi, sin

import pygame

from . import level, settings, sound, student
from .sprites import Player


JUMP_KEYS = (pygame.K_SPACE, pygame.K_x, pygame.K_UP, pygame.K_w)


def tile_rect(column: int, row: int) -> pygame.Rect:
    size = settings.TILE
    return pygame.Rect(column * size, row * size, size, size)


@dataclass
class Enemy:
    x: float
    y: float
    left_limit: float
    right_limit: float
    direction: int = 1
    speed: float = 65.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), 30, 28)


@dataclass
class MovingLedge:
    """Mission 10: blue platform with student-controlled horizontal motion."""

    x: float
    y: float
    left_limit: float
    right_limit: float
    direction: int = 1
    speed: float = 60.0
    width: int = 100
    height: int = 12

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)


@dataclass
class Boss:
    """Mission 6: a visible character awaiting student-created combat."""

    x: float
    y: float
    health: int = 3
    active: bool = False
    hit_cooldown: float = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), 50, 58)


class Game:
    """One room at a time, with optional student-created mechanics."""

    def __init__(self) -> None:
        level.check_all_maps()
        self.font = pygame.font.Font(None, 25)
        self.big_font = pygame.font.Font(None, 58)
        self.events: list[str] = []  # Names of sounds to play this frame.
        self.scene = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        self.won = False
        self.load_level(0)

    def load_level(self, index: int) -> None:
        """Build a new room from its ASCII map. Stars reset for that room."""
        self.level_index = index
        self.won = False
        tiles = level.LEVELS[index]
        self.solids = [tile_rect(col, row)
                       for col, row in level.locations("#", tiles)]
        self.stars = [tile_rect(col, row).inflate(-18, -18)
                      for col, row in level.locations("*", tiles)]
        self.total_stars = len(self.stars)
        self.door = tile_rect(*level.locations("D", tiles)[0])
        self.pad = tile_rect(*level.locations("^", tiles)[0])
        spawn = tile_rect(*level.locations("P", tiles)[0])
        self.start = (spawn.x + 6, spawn.y + 5)
        self.player = Player(*self.start)
        enemy_tile = tile_rect(*level.locations("E", tiles)[0])
        self.enemy = Enemy(
            x=float(enemy_tile.x + 5),
            y=float(enemy_tile.bottom - 28),
            left_limit=float(enemy_tile.x - 70),
            right_limit=float(enemy_tile.x + 95),
        )
        # Mission 6: a static boss until the student programs its behavior.
        boss_tiles = level.locations("B", tiles)
        if boss_tiles:
            marker = tile_rect(*boss_tiles[0])
            self.boss = Boss(float(marker.x - 5), float(marker.bottom - 58))
        else:
            self.boss = None
        # Mission 10: the blue platform is stationary until its student hook.
        self.ledges = []
        for column, row in level.locations("M", tiles):
            marker = tile_rect(column, row)
            x = float(marker.x)
            self.ledges.append(MovingLedge(
                x=x, y=float(marker.y + 24),
                left_limit=max(0.0, x - 75),
                right_limit=min(settings.WIDTH - 100.0, x + 75),
            ))
        # Mission 11: the switch and reward are prepared but inactive.
        switches = level.locations("S", tiles)
        self.switch = tile_rect(*switches[0]) if switches else None
        self.switch_pressed = False
        self.bonus_star = tile_rect(13, 9).inflate(-18, -18)
        # Mission 4: text is only shown if the student returns a line.
        self.speech_text = ""
        self.speech_seconds = 0.0
        # Mission 5: zero transition duration means immediate level changes.
        self.transition_to = None
        self.transition_elapsed = 0.0
        self.message = (f"Level {index + 1}: {level.LEVEL_NAMES[index]}! "
                        f"Find {self.total_stars} stars.")
        self.message_seconds = 3.0
        self.time = 0.0
        self.sky = self._build_background(index)

    def restart(self) -> None:
        """R repeats the current room, or returns to level 1 after winning."""
        if self.won:
            self.won = False
            self.load_level(0)
        else:
            self.load_level(self.level_index)

    @property
    def collected(self) -> int:
        return self.total_stars - len(self.stars)

    def _say(self, event: str) -> None:
        """Mission 4: let student.py choose speech for star/hurt events."""
        line = student.hero_speech(event, self)
        if line:
            self.speech_text = str(line)
            self.speech_seconds = 1.5

    def _advance_level(self) -> None:
        """Mission 5: optionally defer loading until an animation completes."""
        next_index = self.level_index + 1
        self.events.append("level")
        if student.TRANSITION_SECONDS > 0:
            self.transition_to = next_index
            self.transition_elapsed = 0.0
        else:
            self.load_level(next_index)

    def step(self, direction: int, jump_pressed: bool, seconds: float) -> None:
        """Advance one frame, connecting the guided student hooks."""
        self.events.clear()
        seconds = max(0.0, min(seconds, 0.05))
        if self.won:
            return
        self.time += seconds
        self.message_seconds = max(0.0, self.message_seconds - seconds)
        self.speech_seconds = max(0.0, self.speech_seconds - seconds)

        if self.transition_to is not None:
            # We keep drawing the old level during the student's animation.
            self.transition_elapsed += seconds
            if self.transition_elapsed >= student.TRANSITION_SECONDS:
                self.load_level(self.transition_to)
            return

        # Mission 9: the student implements a once-per-airtime bonus jump.
        was_grounded = self.player.on_ground
        extra_jump = student.try_double_jump(self.player, jump_pressed)

        # Mission 10: platforms move BEFORE the player physics, and a player
        # already on top of one is carried by the same horizontal distance.
        for platform in self.ledges:
            rect = platform.rect
            riding = (self.player.on_ground
                      and self.player.rect.bottom == rect.top
                      and self.player.rect.right > rect.left
                      and self.player.rect.left < rect.right)
            previous_x = platform.x
            student.move_platform(platform, seconds)
            if riding:
                self.player.x += platform.x - previous_x
                self.player.rect.x = round(self.player.x)

        solids = self.solids + [ledge.rect for ledge in self.ledges]
        self.player.update(direction, jump_pressed, solids, seconds)
        if (jump_pressed and was_grounded) or extra_jump:
            self.events.append("jump")

        # Guided mission 1: the student supplies the spring launch velocity.
        pad_top = self.pad.bottom - 12
        pad_contact = pygame.Rect(self.pad.x, pad_top - 4, self.pad.w, 16)
        if self.player.on_ground and self.player.rect.colliderect(pad_contact):
            student.bounce_from_pad(self.player)
            if self.player.vy < 0 and not self.player.on_ground:
                self.events.append("bounce")

        # Guided mission 2: the student writes the enemy's patrol movement.
        student.move_enemy(self.enemy, seconds)
        if self.player.rect.colliderect(self.enemy.rect):
            self.player = Player(*self.start)
            self.message = "Ouch! Try jumping over the creature."
            self.message_seconds = 1.5
            self.events.append("hurt")
            self._say("hurt")
            return

        # Mission 6: a boss waits in level 3 for the student's combat rules.
        if self.boss is not None:
            self.boss.hit_cooldown = max(0.0, self.boss.hit_cooldown - seconds)
            student.update_boss(self.boss, self, seconds)

        # Mission 11: touching the switch invokes the student's one-time event.
        if self.switch is not None and self.player.rect.colliderect(self.switch):
            student.activate_switch(self)

        for star in self.stars[:]:
            if self.player.rect.colliderect(star):
                self.stars.remove(star)
                self.message = "Nice! Keep exploring."
                self.message_seconds = 1.0
                self.events.append("star")
                self._say("star")

        if self.player.rect.colliderect(self.door):
            if self.stars:
                self.message = f"Find {len(self.stars)} more star(s)!"
                self.message_seconds = 1.0
            elif self.boss is not None and self.boss.active and self.boss.health > 0:
                self.message = "Defeat the boss to unlock the door!"
                self.message_seconds = 1.0
            elif self.level_index < len(level.LEVELS) - 1:
                self._advance_level()
            else:
                self.won = True
                self.events.append("win")

    @staticmethod
    def _build_background(index: int) -> pygame.Surface:
        """Cycle the palettes so a student's fourth level also renders."""
        colors = (
            ((34, 61, 113), (72, 124, 161), (77, 111, 132), (59, 95, 126)),
            ((84, 47, 97), (191, 123, 110), (132, 79, 117), (99, 66, 111)),
            ((36, 96, 153), (139, 191, 211), (112, 156, 177), (85, 133, 164)),
        )
        top, bottom, far_hill, near_hill = colors[index % len(colors)]
        surface = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        for y in range(settings.HEIGHT):
            t = y / settings.HEIGHT
            color = tuple(round(a * (1 - t) + b * t)
                          for a, b in zip(top, bottom))
            pygame.draw.line(surface, color, (0, y), (settings.WIDTH, y))
        pygame.draw.polygon(surface, far_hill,
                            [(0, 560), (160, 385), (310, 560),
                             (490, 350), (690, 560), (960, 390), (960, 600), (0, 600)])
        pygame.draw.polygon(surface, near_hill,
                            [(0, 600), (200, 480), (350, 600),
                             (610, 455), (800, 600), (960, 535), (960, 600)])
        cloud = (184, 205, 216) if index != 1 else (234, 184, 173)
        for x, y in ((110, 120), (420, 65), (780, 140)):
            for dx, dy, radius in ((0, 0, 27), (25, -10, 22), (48, 0, 26)):
                pygame.draw.circle(surface, cloud,
                                   (x + dx, y + dy), radius)
        return surface

    def draw(self, window: pygame.Surface) -> None:
        """Draw world shapes, apply optional camera, then draw a fixed HUD."""
        screen = self.scene
        screen.blit(self.sky, (0, 0))
        for block in self.solids:
            pygame.draw.rect(screen, settings.EARTH, block)
            pygame.draw.rect(screen, (77, 60, 76), block.inflate(-8, -8), 1)
            pygame.draw.rect(screen, settings.GRASS,
                             (block.x, block.y, block.w, 7))

        # Decorative spring, ready for the student's behavior.
        pygame.draw.rect(screen, (226, 119, 70),
                         (self.pad.x + 3, self.pad.bottom - 11,
                          self.pad.w - 6, 10), border_radius=4)
        pygame.draw.polygon(screen, (255, 224, 143),
                            [(self.pad.centerx, self.pad.bottom - 23),
                             (self.pad.centerx - 8, self.pad.bottom - 14),
                             (self.pad.centerx + 8, self.pad.bottom - 14)])

        # Mission 10: visible blue ledges even before they start moving.
        for ledge in self.ledges:
            rect = ledge.rect
            pygame.draw.rect(screen, (43, 67, 93), rect.move(2, 4), border_radius=4)
            pygame.draw.rect(screen, (87, 189, 232), rect, border_radius=4)
            pygame.draw.line(screen, (225, 244, 255),
                             (rect.left + 5, rect.top + 3),
                             (rect.right - 5, rect.top + 3), 2)

        # Mission 11: red while idle, green after the student's action.
        if self.switch is not None:
            color = (104, 214, 158) if self.switch_pressed else (234, 124, 119)
            center = self.switch.center
            pygame.draw.rect(screen, (52, 57, 79),
                             self.switch.inflate(-14, -12), border_radius=6)
            pygame.draw.circle(screen, color, center, 9)
            pygame.draw.circle(screen, (246, 240, 224), center, 3)

        for star in self.stars:
            cx, cy = star.center
            glow = 1 + round(2 * sin(self.time * 5 + cx))
            radius = 13 + glow
            points = []
            for point in range(10):
                angle = -pi / 2 + point * pi / 5
                distance = radius if point % 2 == 0 else radius / 2
                points.append((round(cx + cos(angle) * distance),
                               round(cy + sin(angle) * distance)))
            pygame.draw.polygon(screen, (129, 91, 75),
                                [(x + 2, y + 3) for x, y in points])
            pygame.draw.polygon(screen, settings.GOLD, points)
            pygame.draw.circle(screen, (255, 246, 195), (cx - 3, cy - 3), 3)

        # Blue when locked, green when all stars are collected.
        door_color = (117, 224, 170) if not self.stars else (97, 139, 181)
        pygame.draw.rect(screen, (42, 48, 74), self.door.inflate(8, 6),
                         border_radius=9)
        pygame.draw.rect(screen, door_color, self.door.inflate(-6, 0),
                         border_radius=8)
        pygame.draw.circle(screen, settings.GOLD,
                           (self.door.right - 9, self.door.centery), 3)

        enemy = self.enemy.rect
        pygame.draw.ellipse(screen, (104, 57, 128), enemy)
        pygame.draw.circle(screen, (243, 230, 245),
                           (enemy.x + 10, enemy.y + 11), 4)
        pygame.draw.circle(screen, (243, 230, 245),
                           (enemy.x + 21, enemy.y + 11), 4)
        pygame.draw.circle(screen, (41, 37, 61),
                           (enemy.x + 11, enemy.y + 12), 2)
        pygame.draw.circle(screen, (41, 37, 61),
                           (enemy.x + 22, enemy.y + 12), 2)

        # Mission 6: big stationary boss, ready for student-written combat.
        if self.boss is not None and self.boss.health > 0:
            boss = self.boss.rect
            body_color = ((174, 105, 196) if not self.boss.active
                          else (215, 89, 115))
            pygame.draw.rect(screen, (55, 39, 71), boss.move(3, 4),
                             border_radius=10)
            pygame.draw.rect(screen, body_color, boss, border_radius=10)
            pygame.draw.polygon(screen, (251, 210, 112),
                                [(boss.x + 6, boss.y + 2), (boss.x + 10, boss.y - 12),
                                 (boss.centerx, boss.y - 2),
                                 (boss.right - 10, boss.y - 12),
                                 (boss.right - 6, boss.y + 2)])
            for eye_x in (boss.x + 15, boss.x + 34):
                pygame.draw.circle(screen, (255, 242, 226), (eye_x, boss.y + 21), 5)
                pygame.draw.circle(screen, (44, 36, 62), (eye_x, boss.y + 22), 2)
            if self.boss.active:
                for heart in range(self.boss.health):
                    pygame.draw.circle(screen, (255, 124, 154),
                                       (boss.x + heart * 15 + 10, boss.y - 23), 5)

        # Friendly robot: simple shapes that the student can redraw.
        hero = self.player.rect
        pygame.draw.rect(screen, (44, 62, 86),
                         hero.move(0, 3), border_radius=6)
        pygame.draw.rect(screen, student.HERO_COLOR,
                         hero.inflate(-4, -4), border_radius=6)
        pygame.draw.rect(screen, (237, 235, 210),
                         (hero.x + 6, hero.y + 7, hero.w - 12, 12),
                         border_radius=4)
        for eye_x in (hero.x + 11, hero.x + 18):
            pygame.draw.circle(screen, (35, 53, 73), (eye_x, hero.y + 13), 2)
        pygame.draw.line(screen, (245, 201, 117),
                         (hero.centerx, hero.top), (hero.centerx, hero.top - 5), 2)
        pygame.draw.circle(screen, (245, 201, 117),
                           (hero.centerx, hero.top - 6), 3)

        # Mission 4: position the speech bubble in WORLD coordinates so a
        # following camera carries it along with the player's character.
        if self.speech_seconds > 0 and self.speech_text:
            text = self.font.render(self.speech_text, True, (35, 44, 61))
            bubble = text.get_rect().inflate(20, 14)
            bubble.midbottom = (hero.centerx, hero.top - 9)
            bubble.left = max(6, min(bubble.left, settings.WIDTH - bubble.width - 6))
            bubble.top = max(48, bubble.top)
            pygame.draw.rect(screen, (251, 242, 215), bubble, border_radius=9)
            pygame.draw.polygon(screen, (251, 242, 215),
                                [(hero.centerx - 6, bubble.bottom - 2),
                                 (hero.centerx + 6, bubble.bottom - 2),
                                 (hero.centerx, hero.top - 3)])
            screen.blit(text, (bubble.x + 10, bubble.y + 7))

        self._present_camera(window)
        # The HUD lives outside the world/camera transform.
        screen = window
        font = self.font
        big = self.big_font
        pygame.draw.rect(screen, (25, 40, 63), (0, 0, settings.WIDTH, 42))
        status = (f"LEVEL {self.level_index + 1}/{len(level.LEVELS)}  "
                  f"{level.LEVEL_NAMES[self.level_index]}   "
                  f"STARS {self.collected}/{self.total_stars}")
        screen.blit(font.render(status, True, settings.TEXT), (16, 12))
        keys = "A/D: MOVE   SPACE/X: JUMP   M: MUTE   R: RESTART"
        screen.blit(font.render(keys, True, settings.TEXT), (475, 12))
        if self.message_seconds > 0 and not self.won:
            hint = font.render(self.message, True, settings.TEXT)
            screen.blit(hint, (settings.WIDTH // 2 - hint.get_width() // 2, 63))
        if self.won:
            banner = pygame.Surface((settings.WIDTH, 120), pygame.SRCALPHA)
            banner.fill((20, 37, 56, 222))
            screen.blit(banner, (0, 203))
            title = big.render(f"ALL {len(level.LEVELS)} LEVELS CLEAR!",
                               True, settings.GOLD)
            screen.blit(title, (settings.WIDTH // 2 - title.get_width() // 2, 214))
            again = font.render("Press R to play again from level 1", True,
                                settings.TEXT)
            screen.blit(again, (settings.WIDTH // 2 - again.get_width() // 2, 283))

        # Mission 5: students draw an animated overlay on the finished frame.
        if self.transition_to is not None:
            length = max(0.001, student.TRANSITION_SECONDS)
            progress = min(1.0, self.transition_elapsed / length)
            name = level.LEVEL_NAMES[self.transition_to]
            student.draw_transition(window, progress, name)

    def _present_camera(self, window: pygame.Surface) -> None:
        """Mission 8: crop around a student-chosen center, keeping HUD fixed."""
        cx, cy, zoom = student.camera_view(self.player)
        zoom = max(1.0, min(2.5, float(zoom)))
        width = round(settings.WIDTH / zoom)
        height = round(settings.HEIGHT / zoom)
        left = max(0, min(settings.WIDTH - width, round(cx - width / 2)))
        top = max(0, min(settings.HEIGHT - height, round(cy - height / 2)))
        viewport = pygame.Rect(left, top, width, height)
        if zoom == 1.0:
            window.blit(self.scene, (0, 0))
        else:
            # Crop BEFORE scaling: don't build a huge full-level image.
            visible = self.scene.subsurface(viewport)
            scaled = pygame.transform.smoothscale(
                visible, (settings.WIDTH, settings.HEIGHT))
            window.blit(scaled, (0, 0))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A tiny pygame platformer")
    parser.add_argument("--frames", type=int, default=0,
                        help="Quit after N frames (for smoke testing)")
    parser.add_argument("--screenshot", help="Save the final frame as PNG")
    args = parser.parse_args(argv)
    if args.frames < 0:
        parser.error("--frames cannot be negative")

    # Ask SDL for the same 16-bit stereo format that sound.py generates.
    pygame.mixer.pre_init(frequency=sound.SAMPLE_RATE, size=-16,
                          channels=2, buffer=512)
    pygame.init()
    audio = None
    try:
        screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption(student.GAME_TITLE)
        clock = pygame.time.Clock()
        game = Game()
        audio = sound.SoundBoard(pygame)
        running = True
        frame = 0
        while running:
            seconds = min(clock.tick(settings.FPS) / 1000.0, 0.05)
            jump_pressed = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in JUMP_KEYS:
                        jump_pressed = True
                    elif event.key == pygame.K_r:
                        game.restart()
                    elif event.key == pygame.K_m:
                        audio.toggle_mute()
            if not running:
                break
            keys = pygame.key.get_pressed()
            direction = int(bool(keys[pygame.K_RIGHT] or keys[pygame.K_d])) - int(
                bool(keys[pygame.K_LEFT] or keys[pygame.K_a]))
            game.step(direction, jump_pressed, seconds)
            audio.set_level(game.level_index)  # Mission 7: change the soundtrack.
            audio.play(game.events)
            game.draw(screen)
            pygame.display.flip()
            frame += 1
            if args.frames and frame >= args.frames:
                running = False
        if args.screenshot:
            pygame.image.save(screen, args.screenshot)
        return 0
    finally:
        if audio is not None:
            audio.close()
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())
