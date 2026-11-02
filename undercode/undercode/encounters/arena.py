"""Defense physics and the small API that student patterns use.

Patterns decide WHAT to spawn. Arena handles movement, collisions, health and
invulnerability. Positions are local to the arena, independent of screen size.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
import math
import random
import pygame
from ..controls import Controls

Vec = pygame.Vector2


class Mode(Enum):
    """Choose defense controls: free movement, gravity with jumping, or a fixed shield."""

    FREE = auto()
    GRAVITY = auto()
    SHIELD = auto()


@dataclass(kw_only=True)
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


@dataclass(kw_only=True)
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


@dataclass(kw_only=True)
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
    # Project the circle center onto the motion line. Restrict that fraction
    # to 0..1 so the closest point stays on the segment, not beyond its ends.
    fraction = (
        0 if length_squared == 0 else max(0, min(1, (center - start).dot(delta) / length_squared))
    )
    return (start + delta * fraction - center).length_squared() <= radius * radius


class DefensePattern:
    """Define an enemy defense; subclass this in student_encounters.py.

    A new instance owns each turn's timers. Set name, hint, mode and duration
    (seconds), then implement update(arena, seconds) to create hazards. Arena handles
    movement, collisions and HP; patterns use its spawn/beam methods and rng.
    """

    name = "Untitled pattern"
    hint = "Move with the arrow keys or WASD."
    mode = Mode.FREE
    duration = 5.0

    def update(self, *, arena: "Arena", seconds: float):
        """Create or schedule hazards for the elapsed seconds of this defense.

        Subclasses must implement this method. Use arena-local pixels and
        arena.rng for repeatable randomness; keep cooldowns on self. This base
        method raises NotImplementedError to identify an unfinished subclass.
        """
        raise NotImplementedError


class Arena:
    """Simulate one defense in a local 600 by 196 pixel playfield.

    Own the soul, hazards and seeded RNG. Borrow the shared Player for HP;
    no health value is copied between engines. Patterns create
    hazards; View translates local positions into window positions.
    """

    width = 600
    height = 196

    def __init__(self, *, pattern, player, seed=0):
        """Create a defense with a fresh pattern, starting HP, and random seed.

        Check the pattern's duration/mode, then choose its initial soul position.
        No keyboard, display, or audio device is opened by this constructor.
        """
        if not math.isfinite(pattern.duration) or pattern.duration <= 0:
            raise ValueError("Pattern duration must be finite and positive.")
        if not isinstance(pattern.mode, Mode):
            raise ValueError("Pattern mode must be Mode.FREE, Mode.GRAVITY, or Mode.SHIELD.")
        self.pattern = pattern
        self.player = player
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
        self.soul = Soul(position=start, grounded=pattern.mode == Mode.GRAVITY)

    @property
    def hp(self):
        """Read the shared player's HP; this is a forwarding property, not another copy."""
        return self.player.hp

    @hp.setter
    def hp(self, value):
        """Keep existing hazard rules readable while assigning the shared player directly."""
        self.player.hp = value

    @property
    def done(self):
        """Return whether time ran out or the player has no HP left."""
        return self.elapsed >= self.pattern.duration or self.hp <= 0

    def spawn(self, *, x, y, vx, vy, radius=6, damage=2, color=(255, 188, 112), warmup=0):
        """Append a warned circular projectile; return None.

        x/y are arena-local pixels; vx/vy are pixels per second. radius is in
        pixels, damage is nonnegative integer HP, and warmup is seconds before
        motion/damage. color is an RGB tuple. Invalid geometry raises ValueError.
        Example: arena.spawn(x=8, y=98, vx=160, vy=0, warmup=0.5) warns, then moves right.
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
        self.bullets.append(
            Bullet(
                position=Vec(x, y),
                velocity=Vec(vx, vy),
                radius=radius,
                damage=damage,
                color=color,
                warmup=warmup,
            )
        )

    def beam(self, *, x, y, width, height, warmup=0.8, duration=0.3):
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
        self.beams.append(
            Beam(rect=pygame.Rect(x, y, width, height), warmup=warmup, duration=duration)
        )

    def hurt(self, *, damage):
        """Subtract damage HP unless the soul is temporarily invulnerable.

        A successful hit clamps HP at zero, increments hits, grants 0.7 seconds
        of protection, and queues a hurt sound. It does not end Encounter itself.
        """
        if self.soul.invulnerable > 0:
            return
        self.hp = max(0, self.hp - damage)
        self.hits += 1
        self.soul.invulnerable = 0.7
        self.cues.append("hurt")

    def move_soul(self, *, seconds: float, controls: Controls):
        """Apply Controls for the elapsed seconds using the pattern's movement mode.

        Free movement normalizes diagonals; gravity allows grounded confirm
        presses to jump; shield mode changes facing without moving the soul.
        Clamp the soul inside the local playfield after movement.
        """
        soul = self.soul
        if self.pattern.mode == Mode.SHIELD:
            if controls.move_x or controls.move_y:
                if abs(controls.move_x) > abs(controls.move_y):
                    soul.facing = Vec(1 if controls.move_x > 0 else -1, 0)
                else:
                    soul.facing = Vec(0, 1 if controls.move_y > 0 else -1)
        elif self.pattern.mode == Mode.GRAVITY:
            soul.position.x += controls.move_x * 200 * seconds
            if controls.confirm_pressed and soul.grounded:
                soul.vertical_speed = -290
                soul.grounded = False
                self.cues.append("jump")
            soul.vertical_speed += 820 * seconds
            soul.position.y += soul.vertical_speed * seconds
            floor = self.height - soul.radius - 2
            if soul.position.y >= floor:
                soul.position.y = floor
                soul.vertical_speed = 0
                soul.grounded = True
        else:
            move = Vec(controls.move_x, controls.move_y)
            if move.length_squared() > 1:
                move.normalize_ip()
            soul.position += move * 180 * seconds
        soul.position.x = max(soul.radius, min(self.width - soul.radius, soul.position.x))
        soul.position.y = max(soul.radius, min(self.height - soul.radius, soul.position.y))

    def update(self, *, seconds: float, controls: Controls):
        """Advance controls, the student pattern, hazards, and collisions by the elapsed seconds.

        Reject negative/nonfinite seconds and stop at the pattern's time limit.
        Warnings consume time before bullets move or hurt; shield blocks remove
        incoming bullets. Check swept collisions so fast bullets cannot skip
        the soul. Remove expired hazards and keep sound names in cues.
        """
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("Elapsed seconds must be finite and nonnegative.")
        if self.done:
            return
        seconds = min(seconds, self.pattern.duration - self.elapsed)
        self.elapsed += seconds
        self.soul.invulnerable = max(0, self.soul.invulnerable - seconds)
        self.soul.guard_flash = max(0, self.soul.guard_flash - seconds)
        self.move_soul(seconds=seconds, controls=controls)
        self.pattern.update(arena=self, seconds=seconds)
        self.advance_bullets(seconds=seconds)
        self.advance_beams(seconds=seconds)

    def advance_bullets(self, *, seconds):
        """Warn, move, block/hit, and keep surviving bullets in that order.

        A bullet crossing the player between frames still hits: test its whole
        movement segment. The shield checks approach direction first, and a
        successful block removes the bullet before a body collision is tested.
        """
        survivors = []
        for bullet in self.bullets:
            moving_time = max(0, seconds - bullet.warmup)
            bullet.warmup = max(0, bullet.warmup - seconds)
            old = bullet.position.copy()
            bullet.position += bullet.velocity * moving_time
            if bullet.warmup > 0:
                survivors.append(bullet)
                continue
            toward = old - self.soul.position
            # Normalized dot product is the cosine of the approach angle.
            # A value above 0.72 puts the incoming spark near the shield front.
            blocking = (
                self.pattern.mode == Mode.SHIELD
                and toward.length_squared() > 0
                and toward.normalize().dot(self.soul.facing) > 0.72
            )
            if blocking and segment_hits_circle(
                start=old, end=bullet.position, center=self.soul.position, radius=29 + bullet.radius
            ):
                self.blocks += 1
                self.soul.guard_flash = 0.18
                self.cues.append("block")
                continue
            if segment_hits_circle(
                start=old,
                end=bullet.position,
                center=self.soul.position,
                radius=self.soul.radius + bullet.radius,
            ):
                self.hurt(damage=bullet.damage)
                continue
            if (
                -80 <= bullet.position.x <= self.width + 80
                and -80 <= bullet.position.y <= self.height + 80
            ):
                survivors.append(bullet)
        self.bullets = survivors

    def advance_beams(self, *, seconds):
        """Age warnings, damage only during the active interval, then remove expired beams."""
        for beam in self.beams:
            beam.age += seconds
            if beam.active:
                x = max(beam.rect.left, min(beam.rect.right, self.soul.position.x))
                y = max(beam.rect.top, min(beam.rect.bottom, self.soul.position.y))
                if (Vec(x, y) - self.soul.position).length_squared() <= self.soul.radius**2:
                    self.hurt(damage=beam.damage)
        self.beams = [b for b in self.beams if b.age < b.warmup + b.duration]
