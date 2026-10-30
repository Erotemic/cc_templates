"""A player with just enough physics to walk and jump.

We keep floating-point positions for smooth movement, but use pygame.Rect
for collisions. Horizontal and vertical collisions are handled separately.
"""

import pygame

from . import settings


class Player:
    def __init__(self, x: float, y: float) -> None:
        self.rect = pygame.Rect(round(x), round(y),
                                settings.PLAYER_WIDTH, settings.PLAYER_HEIGHT)
        self.x = float(x)
        self.y = float(y)
        self.vy = 0.0
        self.on_ground = False
        # Mission 9: remember whether the optional airborne jump was used.
        self.extra_jump_used = False

    def update(self, direction: int, jump_pressed: bool,
               solids: list[pygame.Rect], seconds: float) -> None:
        """Walk, jump, apply gravity, and stop at solid tiles."""
        if jump_pressed and self.on_ground:
            self.vy = -settings.JUMP_SPEED
            self.on_ground = False

        # Move left/right and resolve collisions with the SIDE of tiles.
        dx = direction * settings.MOVE_SPEED * seconds
        self.x += dx
        self.rect.x = round(self.x)
        for block in solids:
            if self.rect.colliderect(block):
                if dx > 0:
                    self.rect.right = block.left
                elif dx < 0:
                    self.rect.left = block.right
                self.x = float(self.rect.x)

        # With no camera, don't let the player walk out of the room.
        self.x = max(0.0, min(self.x, settings.WIDTH - self.rect.width))
        self.rect.x = round(self.x)

        # Falling is positive Y, so gravity ADDS to vy each frame.
        self.vy = min(settings.MAX_FALL_SPEED,
                      self.vy + settings.GRAVITY * seconds)
        self.y += self.vy * seconds
        self.rect.y = round(self.y)
        landed = False
        for block in solids:
            if self.rect.colliderect(block):
                if self.vy >= 0:
                    self.rect.bottom = block.top
                    landed = True
                else:
                    self.rect.top = block.bottom
                self.vy = 0.0
                self.y = float(self.rect.y)

        # If rounding produced exactly zero movement, still remember ground.
        if not landed and self.vy >= 0:
            probe = self.rect.move(0, 1)
            landed = any(probe.colliderect(block) for block in solids)
            if landed:
                self.vy = 0.0
        self.on_ground = landed
