"""Defense physics and the small API that student patterns use.

Patterns decide WHAT to spawn. Arena handles movement, collisions, health and
invulnerability. Positions are local to the arena, independent of screen size.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
import math
import random
import pygame
from .controls import Controls

Vec = pygame.Vector2


class Mode(Enum):
    """Choose defense controls: free movement, gravity with jumping, or a fixed shield."""

    FREE = auto()
    GRAVITY = auto()
    SHIELD = auto()


@dataclass
class Bullet:
    """Store one circular projectile in arena-local pixels.

    velocity is pixels per second. During warmup (seconds), the projectile
    warns without moving or damaging; damage is HP lost on a successful hit.
    """

    position: Vec
    velocity: Vec
    radius: float = 6
    damage: int = 2
    color: tuple[int, int, int] = (255, 188, 112)
    warmup: float = 0


@dataclass
class Beam:
    """Store a rectangular hazard that warns, becomes dangerous, then expires.

    rect uses arena-local pixels. age, warmup and duration are seconds;
    Arena.update advances age and removes the beam after its active interval.
    """

    rect: pygame.Rect
    warmup: float = 0.8
    duration: float = 0.3
    age: float = 0
    damage: int = 2

    @property
    def active(self):
        """Return whether the beam is past its warning and inside its damage interval."""
        return self.warmup <= self.age < self.warmup + self.duration


@dataclass
class Soul:
    """Store the player-controlled marker during one defense.

    position/radius use arena pixels; vertical_speed is pixels per second.
    facing is a direction vector for shield mode. invulnerable and guard_flash
    are seconds remaining on damage protection and the visual block effect.
    """

    position: Vec
    radius: float = 7
    vertical_speed: float = 0
    grounded: bool = False
    facing: Vec = field(default_factory=lambda: Vec(0, -1))
    invulnerable: float = 0
    guard_flash: float = 0


def segment_hits_circle(start, end, center, radius):
    """Return whether a moving point's segment reaches a circle.

    start/end/center are vectors in the same coordinate system; radius is a
    distance in pixels. Testing the whole segment catches fast projectiles
    that pass through the player between two frames.
    """
    delta = end - start
    length_squared = delta.length_squared()
    fraction = (
        0 if length_squared == 0 else max(0, min(1, (center - start).dot(delta) / length_squared))
    )
    return (start + delta * fraction - center).length_squared() <= radius * radius


class DefensePattern:
    """Define an enemy defense; subclass this in student.py.

    A new instance owns each turn's timers. Set name, hint, mode and duration
    (seconds), then implement update(arena, dt) to create hazards. Arena handles
    movement, collisions and HP; patterns use its spawn/beam methods and rng.
    """

    name = "Untitled pattern"
    hint = "Move with the arrow keys or WASD."
    mode = Mode.FREE
    duration = 5.0

    def update(self, arena: "Arena", dt: float):
        """Create or schedule hazards for dt seconds of this defense.

        Subclasses must implement this method. Use arena-local pixels and
        arena.rng for repeatable randomness; keep cooldowns on self. This base
        method raises NotImplementedError to identify an unfinished subclass.
        """
        raise NotImplementedError


class Arena:
    """Simulate one defense in a local 600 by 196 pixel playfield.

    Own the soul, projectiles, beams, seeded RNG and temporary HP. Battle copies
    HP back to Player and drains cues after each update. Patterns create
    hazards; View translates local positions into window positions.
    """

    width = 600
    height = 196

    def __init__(self, pattern, hp, seed=0):
        """Create a defense with a fresh pattern, starting HP, and random seed.

        Check the pattern's duration/mode, then choose its initial soul position.
        No keyboard, display, or audio device is opened by this constructor.
        """
        if not math.isfinite(pattern.duration) or pattern.duration <= 0:
            raise ValueError("Pattern duration must be finite and positive.")
        if not isinstance(pattern.mode, Mode):
            raise ValueError("Pattern mode must be Mode.FREE, Mode.GRAVITY, or Mode.SHIELD.")
        self.pattern = pattern
        self.hp = hp
        self.rng = random.Random(seed)
        self.elapsed = 0.0
        self.bullets: list[Bullet] = []
        self.beams: list[Beam] = []
        self.cues: list[str] = []
        self.hits = 0
        self.blocks = 0
        start = Vec(self.width / 2, self.height * 0.72)
        if pattern.mode == Mode.GRAVITY:
            start.y = self.height - 9
        elif pattern.mode == Mode.SHIELD:
            start.y = self.height / 2
        self.soul = Soul(start, grounded=pattern.mode == Mode.GRAVITY)

    @property
    def done(self):
        """Return whether time ran out or the player has no HP left."""
        return self.elapsed >= self.pattern.duration or self.hp <= 0

    def spawn(self, x, y, vx, vy, radius=6, damage=2, color=(255, 188, 112), warmup=0):
        """Append a warned circular projectile; return None.

        x/y are arena-local pixels; vx/vy are pixels per second. radius is in
        pixels, damage is nonnegative integer HP, and warmup is seconds before
        motion/damage. color is an RGB tuple. Invalid geometry raises ValueError.
        Example: arena.spawn(8, 98, 160, 0, warmup=0.5) warns, then moves right.
        """
        if (
            not all(math.isfinite(v) for v in (x, y, vx, vy, radius, warmup))
            or radius <= 0
            or warmup < 0
            or not isinstance(damage, int)
            or damage < 0
        ):
            raise ValueError(
                "Bullets need finite coordinates, a positive radius, and nonnegative warmup/damage."
            )
        self.bullets.append(Bullet(Vec(x, y), Vec(vx, vy), radius, damage, color, warmup))

    def beam(self, x, y, width, height, warmup=0.8, duration=0.3):
        """Append a rectangular hazard that warns before briefly damaging.

        x/y/width/height use arena-local pixels. warmup and duration are seconds;
        duration and dimensions must be positive. Invalid geometry/timing raises
        ValueError. Arena advances and removes the beam; this method returns None.
        """
        if (
            not all(math.isfinite(v) for v in (x, y, width, height, warmup, duration))
            or min(width, height, duration) <= 0
            or warmup < 0
        ):
            raise ValueError(
                "Beams need finite geometry, positive dimensions/duration, and nonnegative warmup."
            )
        self.beams.append(Beam(pygame.Rect(x, y, width, height), warmup, duration))

    def hurt(self, damage):
        """Subtract damage HP unless the soul is temporarily invulnerable.

        A successful hit clamps HP at zero, increments hits, grants 0.7 seconds
        of protection, and queues a hurt sound. It does not end Battle itself.
        """
        if self.soul.invulnerable > 0:
            return
        self.hp = max(0, self.hp - damage)
        self.hits += 1
        self.soul.invulnerable = 0.7
        self.cues.append("hurt")

    def move_soul(self, dt: float, controls: Controls):
        """Apply Controls for dt seconds using the pattern's movement mode.

        Free movement normalizes diagonals; gravity allows grounded confirm
        presses to jump; shield mode changes facing without moving the soul.
        Clamp the soul inside the local playfield after movement.
        """
        soul = self.soul
        if self.pattern.mode == Mode.SHIELD:
            if controls.x or controls.y:
                if abs(controls.x) > abs(controls.y):
                    soul.facing = Vec(1 if controls.x > 0 else -1, 0)
                else:
                    soul.facing = Vec(0, 1 if controls.y > 0 else -1)
        elif self.pattern.mode == Mode.GRAVITY:
            soul.position.x += controls.x * 200 * dt
            if controls.confirm and soul.grounded:
                soul.vertical_speed = -290
                soul.grounded = False
                self.cues.append("jump")
            soul.vertical_speed += 820 * dt
            soul.position.y += soul.vertical_speed * dt
            floor = self.height - soul.radius - 2
            if soul.position.y >= floor:
                soul.position.y = floor
                soul.vertical_speed = 0
                soul.grounded = True
        else:
            move = Vec(controls.x, controls.y)
            if move.length_squared() > 1:
                move.normalize_ip()
            soul.position += move * 180 * dt
        soul.position.x = max(soul.radius, min(self.width - soul.radius, soul.position.x))
        soul.position.y = max(soul.radius, min(self.height - soul.radius, soul.position.y))

    def update(self, dt: float, controls: Controls):
        """Advance controls, the student pattern, hazards, and collisions by dt seconds.

        Reject negative/nonfinite dt and stop at the pattern's time limit.
        Warnings consume time before bullets move or hurt; shield blocks remove
        incoming bullets. Check swept collisions so fast bullets cannot skip
        the soul. Remove expired hazards and keep sound names in cues.
        """
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("Elapsed seconds must be finite and nonnegative.")
        if self.done:
            return
        dt = min(dt, self.pattern.duration - self.elapsed)
        self.elapsed += dt
        self.soul.invulnerable = max(0, self.soul.invulnerable - dt)
        self.soul.guard_flash = max(0, self.soul.guard_flash - dt)
        self.move_soul(dt, controls)
        self.pattern.update(self, dt)
        survivors = []
        for bullet in self.bullets:
            moving_time = max(0, dt - bullet.warmup)
            bullet.warmup = max(0, bullet.warmup - dt)
            old = bullet.position.copy()
            bullet.position += bullet.velocity * moving_time
            if bullet.warmup > 0:
                survivors.append(bullet)
                continue
            toward = old - self.soul.position
            blocking = (
                self.pattern.mode == Mode.SHIELD
                and toward.length_squared() > 0
                and toward.normalize().dot(self.soul.facing) > 0.72
            )
            if blocking and segment_hits_circle(
                old, bullet.position, self.soul.position, 29 + bullet.radius
            ):
                self.blocks += 1
                self.soul.guard_flash = 0.18
                self.cues.append("block")
                continue
            if segment_hits_circle(
                old, bullet.position, self.soul.position, self.soul.radius + bullet.radius
            ):
                self.hurt(bullet.damage)
                continue
            if (
                -80 <= bullet.position.x <= self.width + 80
                and -80 <= bullet.position.y <= self.height + 80
            ):
                survivors.append(bullet)
        self.bullets = survivors
        for beam in self.beams:
            beam.age += dt
            if beam.active:
                x = max(beam.rect.left, min(beam.rect.right, self.soul.position.x))
                y = max(beam.rect.top, min(beam.rect.bottom, self.soul.position.y))
                if (Vec(x, y) - self.soul.position).length_squared() <= self.soul.radius**2:
                    self.hurt(beam.damage)
        self.beams = [b for b in self.beams if b.age < b.warmup + b.duration]
