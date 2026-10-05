from __future__ import annotations

from collections.abc import Mapping
from importlib import resources
from pathlib import PurePosixPath

import pygame

from rpg_battle.catalog import CharacterMotionSpec, PaletteSpec, SpriteRecipe, get_default_content
from rpg_battle.render.primitives import draw_shape
from rpg_battle.render.signal_transform import apply_signal_transforms
from rpg_battle.render.sprite_animation import select_frame, state_visual, state_visual_duration
from rpg_battle.render.sprite_motion import (
    evaluate_character_motion,
    motion_duration,
)
from rpg_battle.render.svg_support import load_svg_surface


class SpriteActor:
    """Runtime presentation state for one battler.

    The actor owns clocks and semantic presentation state (idle, attack, hurt,
    faint). The actual motion recipes live in game presentation data, while the
    artwork can be a still frame or a frame-by-frame animation.
    """

    def __init__(
        self,
        side: str,
        *,
        sprites: Mapping[str, SpriteRecipe] | None = None,
        palettes: Mapping[str, PaletteSpec] | None = None,
        character_motion: CharacterMotionSpec | None = None,
    ) -> None:
        have_everything = (
            sprites is not None and palettes is not None and character_motion is not None
        )
        content = None if have_everything else get_default_content()
        self.sprites = sprites if sprites is not None else content.sprites
        self.palettes = palettes if palettes is not None else content.palettes
        self.character_motion = (
            character_motion
            if character_motion is not None
            else content.presentation.character_motion
        )
        self.side = side
        self.attack_timer = 0.0
        self.attack_duration = 0.0
        self.hurt_timer = 0.0
        self.hurt_duration = 0.0
        self.flash_timer = 0.0
        self.faint = False
        self.faint_elapsed = 0.0
        self.faint_duration = motion_duration(self.character_motion["faint"])
        self.idle_clock = 0.0
        self._svg_surfaces: dict[tuple[str, str], pygame.Surface] = {}
        self._preview_state: str | None = None
        self._preview_elapsed = 0.0

    def update(self, dt: float) -> None:
        self.idle_clock += dt
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.flash_timer = max(0.0, self.flash_timer - dt)
        if self.faint:
            self.faint_elapsed += dt
        else:
            self.faint_elapsed = 0.0
        if self._preview_state is not None:
            self._preview_elapsed += dt

    def _duration_for(self, sprite_id: str | None, state: str) -> float:
        motion_time = motion_duration(self.character_motion[state])
        visual_time = 0.0
        if sprite_id is not None:
            visual_time = state_visual_duration(self.sprites[sprite_id], state)
        return max(motion_time, visual_time)

    def play_attack(self, sprite_id: str | None = None) -> None:
        self.attack_duration = self._duration_for(sprite_id, "attack")
        self.attack_timer = self.attack_duration

    def play_hurt(self, sprite_id: str | None = None) -> None:
        self.hurt_duration = self._duration_for(sprite_id, "hurt")
        self.hurt_timer = self.hurt_duration
        self.flash_timer = 0.18

    def set_faint(self, faint: bool, sprite_id: str | None = None) -> None:
        if faint and not self.faint:
            self.attack_timer = 0.0
            self.hurt_timer = 0.0
            self.flash_timer = 0.0
            self.faint_elapsed = 0.0
            self.faint_duration = self._duration_for(sprite_id, "faint")
        elif not faint:
            self.faint_elapsed = 0.0
        self.faint = faint

    def set_preview_state(self, state: str, elapsed: float = 0.0) -> None:
        """Force one presentation state for the character preview tool."""

        if state not in {"idle", "attack", "hurt", "faint"}:
            raise ValueError(f"Unknown preview state {state!r}")
        self._preview_state = state
        self._preview_elapsed = max(0.0, elapsed)
        self.idle_clock = max(self.idle_clock, self._preview_elapsed)

    def clear_preview_state(self) -> None:
        self._preview_state = None
        self._preview_elapsed = 0.0

    def ready_to_hide(self, displayed_hp: float) -> bool:
        return (
            self.faint
            and displayed_hp <= 0.05
            and self.faint_elapsed >= self.faint_duration
        )

    def _state_and_elapsed(self) -> tuple[str, float]:
        if self._preview_state is not None:
            return self._preview_state, self._preview_elapsed
        if self.faint:
            return "faint", self.faint_elapsed
        if self.hurt_timer > 0:
            return "hurt", max(0.0, self.hurt_duration - self.hurt_timer)
        if self.attack_timer > 0:
            return "attack", max(0.0, self.attack_duration - self.attack_timer)
        return "idle", self.idle_clock

    def _load_svg_surface(self, sprite_id: str, recipe: SpriteRecipe) -> pygame.Surface:
        package = str(recipe.get("package", "student_game"))
        svg_path = str(recipe["path"])
        cache_key = (package, svg_path)
        cached = self._svg_surfaces.get(cache_key)
        if cached is not None:
            return cached

        svg_bytes = resources.files(package).joinpath(*PurePosixPath(svg_path).parts).read_bytes()
        surface = load_svg_surface(svg_bytes, svg_path)
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

    def _resolve_frame(
        self, sprite_recipe: SpriteRecipe, state: str, elapsed: float
    ) -> tuple[SpriteRecipe, float, tuple[int, int, int] | None]:
        art_scale = 1.0
        art_flash_color = None
        if sprite_recipe.get("kind") == "character_art":
            art_scale = float(sprite_recipe.get("scale", 1.0))
            flash_value = sprite_recipe.get("flash_color")
            if flash_value is not None:
                art_flash_color = tuple(flash_value)
        visual = state_visual(sprite_recipe, state)
        return select_frame(visual, elapsed), art_scale, art_flash_color

    def draw(
        self,
        surface: pygame.Surface,
        sprite_id: str,
        pos: tuple[int, int],
        scale: float = 1.0,
        render_transforms: dict[str, int] | None = None,
    ) -> None:
        sprite_recipe = self.sprites[sprite_id]
        state, state_elapsed = self._state_and_elapsed()
        frame_recipe, art_scale, art_flash_color = self._resolve_frame(
            sprite_recipe, state, state_elapsed
        )
        frame_kind = str(frame_recipe.get("kind", "procedural"))
        frame_scale = float(frame_recipe.get("scale", 1.0))
        effective_scale = scale * art_scale * frame_scale
        center = (pos[0], pos[1])
        facing = 1 if self.side == "left" else -1

        motion = evaluate_character_motion(
            self.character_motion,
            state=state,
            idle_elapsed=self.idle_clock,
            state_elapsed=state_elapsed,
            side=self.side,
        )
        draw_center = (int(center[0] + motion.x), int(center[1] + motion.y))

        if art_flash_color is not None:
            flash_color = art_flash_color
        elif frame_kind == "svg":
            flash_color = tuple(frame_recipe.get("flash_color", (220, 235, 255)))
        else:
            palette = self.palettes[frame_recipe["palette"]]
            flash_color = palette["accent"]

        if self.flash_timer > 0:
            glow_surface = pygame.Surface((220, 220), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*flash_color, 70), (110, 110), 78)
            rect = glow_surface.get_rect(center=draw_center)
            surface.blit(glow_surface, rect)

        if frame_kind == "svg":
            source_surface = self._load_svg_surface(sprite_id, frame_recipe)
            target_width = max(1, int(round(source_surface.get_width() * effective_scale)))
            target_height = max(1, int(round(source_surface.get_height() * effective_scale)))
            sprite_surface = pygame.transform.smoothscale(
                source_surface, (target_width, target_height)
            )
            if facing < 0:
                sprite_surface = pygame.transform.flip(sprite_surface, True, False)
            local_center = (sprite_surface.get_width() // 2, sprite_surface.get_height() // 2)
        elif frame_kind == "procedural":
            palette = self.palettes[frame_recipe["palette"]]
            canvas_size = max(280, int(320 * max(scale, effective_scale)))
            sprite_surface = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
            local_center = (canvas_size // 2, canvas_size // 2)
            for shape in frame_recipe["shapes"]:
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
            raise ValueError(f"Unknown sprite frame kind {frame_kind!r} for {sprite_id!r}")

        sprite_surface = apply_signal_transforms(sprite_surface, render_transforms)
        if motion.show_x_eyes:
            eye_scale = effective_scale if frame_kind == "procedural" else max(0.7, scale * 0.8)
            self._draw_x_eyes(sprite_surface, local_center, eye_scale)
        if motion.rotation:
            sprite_surface = pygame.transform.rotozoom(sprite_surface, motion.rotation, 1.0)
        rect = sprite_surface.get_rect(center=draw_center)
        surface.blit(sprite_surface, rect)
