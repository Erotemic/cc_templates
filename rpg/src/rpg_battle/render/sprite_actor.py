from __future__ import annotations

import io
from importlib import resources
import math
from pathlib import PurePosixPath

import pygame

from collections.abc import Mapping

from rpg_battle.catalog import Color, PaletteSpec, SpriteRecipe, get_default_content
from rpg_battle.render.primitives import draw_shape
from rpg_battle.render.signal_transform import apply_signal_transforms


class SpriteActor:
    def __init__(
        self,
        side: str,
        *,
        sprites: Mapping[str, SpriteRecipe] | None = None,
        palettes: Mapping[str, PaletteSpec] | None = None,
    ) -> None:
        content = None if sprites is not None and palettes is not None else get_default_content()
        self.sprites = sprites if sprites is not None else content.sprites
        self.palettes = palettes if palettes is not None else content.palettes
        self.side = side
        self.offset = [0.0, 0.0]
        self.attack_timer = 0.0
        self.hurt_timer = 0.0
        self.flash_timer = 0.0
        self.faint = False
        self.faint_elapsed = 0.0
        self.idle_clock = 0.0
        self._svg_surfaces: dict[tuple[str, str], pygame.Surface] = {}

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

    def _load_svg_surface(self, sprite_id: str, recipe: SpriteRecipe) -> pygame.Surface:
        package = str(recipe.get("package", "student_game"))
        svg_path = str(recipe["path"])
        cache_key = (package, svg_path)
        cached = self._svg_surfaces.get(cache_key)
        if cached is not None:
            return cached

        svg_bytes = resources.files(package).joinpath(*PurePosixPath(svg_path).parts).read_bytes()
        try:
            surface = pygame.image.load(io.BytesIO(svg_bytes), svg_path)
        except pygame.error as ex:
            raise RuntimeError(
                f'Could not load SVG sprite "{sprite_id}" from {svg_path!r}. '
                "This game needs a pygame/SDL_image build with SVG support."
            ) from ex
        self._svg_surfaces[cache_key] = surface
        return surface

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
        recipe = self.sprites[sprite_id]
        sprite_kind = str(recipe.get("kind", "procedural"))
        authored_scale = float(recipe.get("scale", 1.0))
        effective_scale = scale * authored_scale
        center = (pos[0], pos[1])
        facing = 1 if self.side == "left" else -1
        glow = 16 if self.flash_timer > 0 else 0
        draw_center = (int(center[0] + self.offset[0]), int(center[1] + self.offset[1]))

        if sprite_kind == "svg":
            flash_color = tuple(recipe.get("flash_color", (220, 235, 255)))
        else:
            palette = self.palettes[recipe["palette"]]
            flash_color = palette["accent"]

        if glow:
            glow_surface = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*flash_color, 70), (110, 110), 78)
            rect = glow_surface.get_rect(center=draw_center)
            surface.blit(glow_surface, rect)

        if sprite_kind == "svg":
            source_surface = self._load_svg_surface(sprite_id, recipe)
            target_width = max(1, int(round(source_surface.get_width() * effective_scale)))
            target_height = max(1, int(round(source_surface.get_height() * effective_scale)))
            sprite_surface = pygame.transform.smoothscale(
                source_surface, (target_width, target_height)
            )
            if facing < 0:
                sprite_surface = pygame.transform.flip(sprite_surface, True, False)
            local_center = (sprite_surface.get_width() // 2, sprite_surface.get_height() // 2)
        elif sprite_kind == "procedural":
            palette = self.palettes[recipe["palette"]]
            canvas_size = max(280, int(320 * max(scale, effective_scale)))
            sprite_surface = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
            local_center = (canvas_size // 2, canvas_size // 2)
            for shape in recipe["shapes"]:
                draw_shape(
                    sprite_surface,
                    shape,
                    local_center,
                    effective_scale,
                    palette,
                    facing=facing,
                    offset=(0.0, 0.0),
                )
        else:
            raise ValueError(f"Unknown sprite kind {sprite_kind!r} for {sprite_id!r}")

        sprite_surface = apply_signal_transforms(sprite_surface, render_transforms)
        if self.faint:
            # Keep the existing classroom knockout cue for both procedural and
            # vector sprites.  The scale is clamped so SVG art does not inherit
            # its large source-canvas coordinate system here.
            faint_scale = effective_scale if sprite_kind == "procedural" else max(0.7, scale * 0.8)
            self._draw_x_eyes(sprite_surface, local_center, faint_scale)
            angle = min(180.0, (self.faint_elapsed / 0.24) * 180.0)
            sprite_surface = pygame.transform.rotozoom(sprite_surface, angle, 1.0)
        rect = sprite_surface.get_rect(center=draw_center)
        surface.blit(sprite_surface, rect)

