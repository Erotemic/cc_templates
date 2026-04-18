from __future__ import annotations

import math

import pygame

from rpg_battle.content.colors import PALETTES
from rpg_battle.content.sprites import SPRITES
from rpg_battle.render.primitives import draw_shape
from rpg_battle.render.signal_transform import apply_signal_transforms


class SpriteActor:
    def __init__(self, side: str) -> None:
        self.side = side
        self.offset = [0.0, 0.0]
        self.attack_timer = 0.0
        self.hurt_timer = 0.0
        self.flash_timer = 0.0
        self.faint = False
        self.faint_elapsed = 0.0
        self.idle_clock = 0.0

    def update(self, dt: float) -> None:
        self.idle_clock += dt
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        if self.faint:
            self.faint_elapsed += dt
            self.offset[0] *= 0.72
            self.offset[1] = min(110.0, self.offset[1] + dt * 130.0)
            return
        self.faint_elapsed = 0.0
        if self.hurt_timer > 0:
            self.offset[0] = math.sin(self.hurt_timer * 40) * 6
        elif self.attack_timer > 0:
            direction = 1 if self.side == "left" else -1
            self.offset[0] = direction * (18 * math.sin((self.attack_timer / 0.25) * math.pi))
        else:
            self.offset[0] *= 0.8
        self.offset[1] = math.sin(self.idle_clock * 2.2) * 3

    def play_attack(self) -> None:
        self.attack_timer = 0.25

    def play_hurt(self) -> None:
        self.hurt_timer = 0.3
        self.flash_timer = 0.18

    def set_faint(self, faint: bool) -> None:
        if faint and not self.faint:
            self.attack_timer = 0.0
            self.hurt_timer = 0.0
            self.flash_timer = 0.0
            self.faint_elapsed = 0.0
        elif not faint:
            self.offset[1] = 0.0
            self.faint_elapsed = 0.0
        self.faint = faint

    def ready_to_hide(self, displayed_hp: float) -> bool:
        return self.faint and displayed_hp <= 0.05 and self.faint_elapsed >= 0.9

    def _draw_x_eyes(self, surface: pygame.Surface, center: tuple[int, int], scale: float) -> None:
        eye_offset_x = int(18 * scale)
        eye_offset_y = int(14 * scale)
        eye_size = max(5, int(7 * scale))
        width = max(2, int(3 * scale))
        color = (25, 22, 34)
        for sign in (-1, 1):
            eye_center = (center[0] + sign * eye_offset_x, center[1] - eye_offset_y)
            pygame.draw.line(
                surface,
                color,
                (eye_center[0] - eye_size, eye_center[1] - eye_size),
                (eye_center[0] + eye_size, eye_center[1] + eye_size),
                width,
            )
            pygame.draw.line(
                surface,
                color,
                (eye_center[0] - eye_size, eye_center[1] + eye_size),
                (eye_center[0] + eye_size, eye_center[1] - eye_size),
                width,
            )

    def draw(
        self,
        surface: pygame.Surface,
        sprite_id: str,
        pos: tuple[int, int],
        scale: float = 1.0,
        render_transforms: dict[str, int] | None = None,
    ) -> None:
        recipe = SPRITES[sprite_id]
        palette = PALETTES[recipe["palette"]]
        center = (pos[0], pos[1])
        facing = 1 if self.side == "left" else -1
        glow = 16 if self.flash_timer > 0 else 0
        draw_center = (int(center[0] + self.offset[0]), int(center[1] + self.offset[1]))
        if glow:
            glow_surface = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*palette["accent"], 70), (110, 110), 78)
            rect = glow_surface.get_rect(center=draw_center)
            surface.blit(glow_surface, rect)
        canvas_size = max(280, int(320 * scale))
        sprite_surface = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
        local_center = (canvas_size // 2, canvas_size // 2)
        for shape in recipe["shapes"]:
            draw_shape(
                sprite_surface,
                shape,
                local_center,
                scale,
                palette,
                facing=facing,
                offset=(0.0, 0.0),
            )
        sprite_surface = apply_signal_transforms(sprite_surface, render_transforms)
        if self.faint:
            self._draw_x_eyes(sprite_surface, local_center, scale)
            angle = min(180.0, (self.faint_elapsed / 0.24) * 180.0)
            sprite_surface = pygame.transform.rotozoom(sprite_surface, angle, 1.0)
        rect = sprite_surface.get_rect(center=draw_center)
        surface.blit(sprite_surface, rect)
