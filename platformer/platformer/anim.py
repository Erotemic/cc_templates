# platformer/anim.py
import pygame


class AnimSprite(pygame.sprite.Sprite):
    def __init__(self, anims: dict[str, list[pygame.Surface]], pos, fps=10):
        super().__init__()
        self.anims = anims
        self.current = "idle"
        self.frames = self.anims[self.current]
        self.fps = fps
        self.timer = 0.0
        self.index = 0
        self.flip = False
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=pos)

    def set(self, name):
        if name != self.current:
            self.current = name
            self.frames = self.anims[self.current]
            self.index = 0
            self.timer = 0.0
            self.image = self.frames[0]

    def update(self, dt, flip=False):
        self.flip = flip
        self.timer += dt
        if self.timer >= 1.0 / self.fps:
            self.timer = 0.0
            self.index = (self.index + 1) % len(self.frames)
            frame = self.frames[self.index]
            self.image = pygame.transform.flip(frame, True, False) if self.flip else frame
