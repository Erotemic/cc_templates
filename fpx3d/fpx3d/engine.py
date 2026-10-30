"""The rules and first-person physics, deliberately usable WITHOUT Panda3D.

Panda draws the game and reads the keyboard. This module answers questions:
Can I move here? Did I jump? Did I get the prism? Did I win?

The student-written functions are imported from student.py. Those functions
are normal Python: no graphics or game-engine knowledge is needed to begin.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil, cos, hypot, radians, sin
from random import Random

from . import settings, student, world


@dataclass(frozen=True)
class Controls:
    forward: float = 0.0   # -1 backward, +1 forward
    sideways: float = 0.0  # -1 left, +1 right
    sprint: bool = False
    jump_pressed: bool = False  # a KEYDOWN, not a held key


@dataclass
class Player:
    x: float = settings.START[0]
    y: float = settings.START[1]
    z: float = settings.START[2]  # FEET height, not eye height
    vz: float = 0.0
    heading: float = 0.0
    pitch: float = -5.0
    on_ground: bool = True
    hit_cooldown: float = 0.0
    bounce_cooldown: float = 0.0


@dataclass
class Drone:
    name: str
    x: float
    y: float
    z: float
    left_limit: float
    right_limit: float
    direction: int = 1
    speed: float = 2.4


@dataclass
class Lift:
    name: str
    x: float
    y: float
    z: float  # center of the lift
    left_limit: float
    right_limit: float
    direction: int = 1
    speed: float = 1.6

    @property
    def top(self) -> float:
        return self.z + 0.3


@dataclass
class Guardian:
    """A clockwork character whose decisions are student exercises.

    Students set move_x/move_y (desired movement direction), not world
    coordinates. The engine applies speed, elapsed seconds, and walls.
    """

    name: str
    x: float
    y: float
    home_x: float
    home_y: float
    detection_radius: float = 5.0
    radius: float = 0.48
    height: float = 1.75
    walk_speed: float = 1.5
    chase_speed: float = 3.0
    mode: str = "idle"    # idle, north, east, south, west
    decision_timer: float = 0.0
    move_x: float = 0.0  # Student controls: -1..+1
    move_y: float = 0.0
    chasing: bool = False
    rng: Random = field(default_factory=lambda: Random(2026), repr=False)


@dataclass
class Scanner:
    x: float = world.SCANNER_CENTER[0]
    y: float = world.SCANNER_CENTER[1]
    radius: float = world.SCANNER_RADIUS
    active: bool = False  # Student decides WHEN it switches on.
    age: float = 0.0


@dataclass
class State:
    player: Player = field(default_factory=Player)
    time_left: float = settings.TIME_LIMIT
    hearts: int = settings.MAX_HEARTS
    stamina: float = settings.STAMINA_MAX
    collected: set[str] = field(default_factory=set)
    bonus_points: int = 0
    respawn_at: tuple[float, float, float] = settings.START
    checkpoint_name: str = ""
    last_event: str = ""
    notice: str = "WASD move / mouse look / SPACE jump / H for help"
    notice_time: float = 6.0
    elapsed: float = 0.0
    won: bool = False
    lost: bool = False
    events: list[str] = field(default_factory=list)
    drones: list[Drone] = field(default_factory=lambda: [
        Drone(item.name, item.x, item.y, item.z, item.left, item.right)
        for item in world.DRONES
    ])
    lifts: list[Lift] = field(default_factory=lambda: [
        Lift(item.name, item.x, item.y, item.z, item.left, item.right)
        for item in world.LIFTS
    ])
    scanner: Scanner = field(default_factory=Scanner)
    guardians: list[Guardian] = field(default_factory=lambda: [
        Guardian(item.name, item.x, item.y, item.x, item.y, item.chase_radius)
        for item in world.GUARDIANS
    ])

    @property
    def cores_collected(self) -> int:
        return sum(item.name in self.collected for item in world.CORES)

    @property
    def cores_needed(self) -> int:
        return len(world.CORES)

    @property
    def gate_open(self) -> bool:
        return self.cores_collected == self.cores_needed

    def restart(self) -> None:
        """Start a new game in-place; the Panda scene need not be rebuilt."""
        fresh = State()
        self.__dict__.update(fresh.__dict__)


def _distance(x: float, y: float, xx: float, yy: float) -> float:
    return hypot(x - xx, y - yy)


def _announce(state: State, event: str, fallback: str, duration=3.0) -> None:
    """Notify the UI, sound system, and optional student dialogue hook."""
    state.events.append(event)
    state.last_event = event
    state.notice = student.curator_line(state, event) or fallback
    state.notice_time = duration


def _circle_touches_box(x: float, y: float, radius: float,
                        box: world.Box) -> bool:
    """Circle vs rectangle, not a square around the player's shoulders.

    The old expanded-rectangle test caught the player on corners before the
    circular body actually touched them. This is much less snag-prone.
    """
    half_w, half_d = box.width / 2, box.depth / 2
    closest_x = max(box.x - half_w, min(x, box.x + half_w))
    closest_y = max(box.y - half_d, min(y, box.y + half_d))
    return (x - closest_x)**2 + (y - closest_y)**2 < radius**2


def _blocked_at(x: float, y: float, radius: float,
                feet_z: float, body_height: float) -> bool:
    """Only room boundaries block walking; all raised ledges are one-way.

    A box can be landable without being an obstacle at shoulder height.
    This lets you pass underneath balconies and lifts instead of getting
    caught on their sides. Most decorative art is non-colliding.
    """
    limit = settings.MAP_EDGE - radius
    if abs(x) > limit + 0.000001 or abs(y) > limit + 0.000001:
        return True
    for box in world.WALK_BLOCKERS:
        if (box.top > feet_z + 0.1
                and box.bottom < feet_z + body_height - 0.1
                and _circle_touches_box(x, y, radius, box)):
            return True
    return False


def _collides_laterally(state: State, x: float, y: float) -> bool:
    """Retained for world-edit tests and for other gameplay helpers."""
    p = state.player
    return _blocked_at(x, y, settings.PLAYER_RADIUS,
                       p.z, settings.PLAYER_HEIGHT)


def _slide(x: float, y: float, dx: float, dy: float,
           *, radius: float, feet_z: float, height: float) -> tuple[float, float]:
    """Small collision-safe movement steps, sliding along boundaries.

    All entities share this helper, so students can choose enemy decisions
    without implementing collision math. The clamped starting position is
    also a recovery path if a student accidentally places the player outside
    the arena when experimenting with coordinates.
    """
    limit = settings.MAP_EDGE - radius
    x = max(-limit, min(limit, x))
    y = max(-limit, min(limit, y))
    steps = max(1, ceil(max(abs(dx), abs(dy)) / 0.20))
    for _ in range(steps):
        sx, sy = dx / steps, dy / steps
        if not _blocked_at(x + sx, y, radius, feet_z, height):
            x += sx
        if not _blocked_at(x, y + sy, radius, feet_z, height):
            y += sy
    return x, y


def _update_guardians(state: State, seconds: float) -> None:
    """Engine supplies movement/collision; student supplies the decisions."""
    for guardian in state.guardians:
        guardian.move_x = 0.0
        guardian.move_y = 0.0
        # MISSION 8 can override MISSION 7 when the player is nearby.
        guardian.chasing = bool(student.guardian_chase(
            guardian, state.player, seconds))
        if not guardian.chasing:
            student.guardian_markov(guardian, seconds)
        speed = guardian.chase_speed if guardian.chasing else guardian.walk_speed
        magnitude = hypot(guardian.move_x, guardian.move_y)
        if magnitude:
            dx = guardian.move_x / max(1, magnitude) * speed * seconds
            dy = guardian.move_y / max(1, magnitude) * speed * seconds
            guardian.x, guardian.y = _slide(
                guardian.x, guardian.y, dx, dy,
                radius=guardian.radius, feet_z=0.0,
                height=guardian.height)


def _land_on(state: State, previous_z: float, next_z: float) -> float | None:
    """Highest floor crossed while falling, including moving platforms."""
    player = state.player
    heights = []
    if previous_z >= -0.001 and next_z <= 0:
        heights.append(0.0)
    for box in world.LANDING_PLATFORMS:
        if (box.under(player.x, player.y, 0.25)
                and previous_z >= box.top - 0.025
                and next_z <= box.top):
            heights.append(box.top)
    for lift in state.lifts:
        if (_distance(player.x, player.y, lift.x, lift.y) < 1.4
                and previous_z >= lift.top - 0.025
                and next_z <= lift.top):
            heights.append(lift.top)
    return max(heights) if heights else None


def _move_player(state: State, controls: Controls, dt: float) -> None:
    p = state.player
    student.update_sprint_energy(state, controls, dt)
    sprinting = controls.sprint and state.stamina > 0
    speed = settings.SPRINT_SPEED if sprinting else settings.WALK_SPEED
    horizontal = controls.sideways
    forward = controls.forward
    length = hypot(horizontal, forward)
    if length > 1:
        horizontal /= length
        forward /= length
    a = radians(p.heading)
    dx = (horizontal * cos(a) - forward * sin(a)) * speed * dt
    dy = (horizontal * sin(a) + forward * cos(a)) * speed * dt

    for lift in state.lifts:
        standing = (p.on_ground and abs(p.z - lift.top) < 0.045
                    and _distance(p.x, p.y, lift.x, lift.y) < 1.4)
        old_x, old_y = lift.x, lift.y
        student.move_lift(lift, dt)
        if standing:
            p.x, p.y = _slide(
                p.x, p.y, lift.x - old_x, lift.y - old_y,
                radius=settings.PLAYER_RADIUS, feet_z=p.z,
                height=settings.PLAYER_HEIGHT)

    p.x, p.y = _slide(p.x, p.y, dx, dy,
                      radius=settings.PLAYER_RADIUS, feet_z=p.z,
                      height=settings.PLAYER_HEIGHT)

    if controls.jump_pressed and p.on_ground:
        p.vz = settings.JUMP_SPEED
        p.on_ground = False
        _announce(state, "jump", "Jump!", 0.45)

    previous_z = p.z
    p.vz = max(-settings.MAX_FALL_SPEED, p.vz - settings.GRAVITY * dt)
    next_z = p.z + p.vz * dt
    landed = _land_on(state, previous_z, next_z) if p.vz <= 0 else None
    if landed is not None:
        p.z = landed
        p.vz = 0.0
        p.on_ground = True
    else:
        p.z = next_z
        p.on_ground = False
    if p.z < -8:  # Defensive in case students add holes or voids.
        _respawn(state, "Watch that step!")


def _respawn(state: State, explanation: str) -> None:
    p = state.player
    p.x, p.y, p.z = state.respawn_at
    p.vz = 0
    p.on_ground = True
    p.hit_cooldown = 1.5
    _announce(state, "respawn", explanation, 3)


def recover_position(state: State) -> None:
    """Rescue key: return to a safe checkpoint without losing progress."""
    if not state.won and not state.lost:
        _respawn(state, "Returned to checkpoint. Keep exploring!")


def _hurt(state: State, reason: str) -> None:
    if state.player.hit_cooldown > 0 or state.won or state.lost:
        return
    state.player.hit_cooldown = 1.4
    state.hearts -= 1
    _announce(state, "hurt", reason, 2.2)
    if state.hearts <= 0:
        state.hearts = settings.MAX_HEARTS
        state.time_left = max(1.0, state.time_left - 10)
        _respawn(state, "Reconstructed at your checkpoint. Time penalty: 10s.")


def _check_world(state: State) -> None:
    p = state.player
    for item in world.PICKUPS:
        if item.name in state.collected:
            continue
        near = _distance(p.x, p.y, item.x, item.y) < 1.18
        same_height = abs((p.z + 1.0) - item.z) < 1.45
        if near and same_height:
            state.collected.add(item.name)
            if item.kind == "core":
                _announce(state, "core", f"{item.name} acquired!", 2.8)
                if state.gate_open:
                    _announce(state, "portal", "All six prisms! Escape through the NORTH gate.", 5)
            else:
                # The item disappears and plays a sound. The reward is a
                # GUIDED MISSION, deliberately not implemented here.
                student.bonus_reward(state, item)
                _announce(state, "bonus", "Bonus spark found! You decide its reward.")

    for pad in world.PADS:
        distance = _distance(p.x, p.y, pad.x, pad.y)
        if distance >= pad.radius:
            continue
        if pad.kind == "spring" and p.z < 0.65 and p.bounce_cooldown == 0:
            p.vz = settings.SPRING_SPEED
            p.on_ground = False
            p.bounce_cooldown = 0.7
            _announce(state, "spring", "BOOST! Try reaching the balconies.", 1.4)
        elif pad.kind == "danger" and p.z < 0.65:
            _hurt(state, "That red pad burns! Keep moving.")
        elif pad.kind == "checkpoint" and p.z < 0.65:
            if state.checkpoint_name != f"{pad.x},{pad.y}":
                old = state.checkpoint_name
                student.activate_checkpoint(state, pad)
                if state.checkpoint_name != old:
                    _announce(state, "checkpoint", "Checkpoint activated!", 2.5)

    for drone in state.drones:
        if (_distance(p.x, p.y, drone.x, drone.y) < 1.1
                and abs((p.z + 0.9) - drone.z) < 1.3):
            _hurt(state, "Sentry contact! Find another route.")

    for guardian in state.guardians:
        if (_distance(p.x, p.y, guardian.x, guardian.y)
                < settings.PLAYER_RADIUS + guardian.radius
                and p.z < guardian.height):
            _hurt(state, "Clockwork Watcher! Careful near that robot.")

    scanner = state.scanner
    if (scanner.active and _distance(p.x, p.y, scanner.x, scanner.y) < scanner.radius
            and p.z < 0.7):
        _hurt(state, "The scanner caught you!")

    if state.gate_open and _distance(p.x, p.y, *settings.EXIT[:2]) < 1.6 and p.z < 1.5:
        state.won = True
        _announce(state, "win", "VAULT CLEARED! Press R to play again.", 20)


def step(state: State, controls: Controls, seconds: float) -> None:
    """Advance by one frame. All student hooks are called from here."""
    if not 0 <= seconds <= 0.05:
        raise ValueError("Seconds must be in [0, 0.05] to keep physics stable")
    state.events.clear()
    if state.won or state.lost:
        return
    state.elapsed += seconds
    state.time_left = max(0.0, state.time_left - seconds)
    state.notice_time = max(0.0, state.notice_time - seconds)
    state.player.hit_cooldown = max(0.0, state.player.hit_cooldown - seconds)
    state.player.bounce_cooldown = max(0.0, state.player.bounce_cooldown - seconds)
    state.scanner.age += seconds
    student.update_scanner(state.scanner, seconds)
    for drone in state.drones:
        student.move_drone(drone, seconds)
    _move_player(state, controls, seconds)
    _update_guardians(state, seconds)
    _check_world(state)
    if state.time_left <= 0 and not state.won:
        state.lost = True
        _announce(state, "lose", "Time ran out! Press R to retry.", 20)


def objective_hint(state: State) -> str:
    """Compass hint for the HUD; helpful in a first-person maze."""
    p = state.player
    target = world.nearest_core(p.x, p.y, state.collected)
    if target is None:
        target_x, target_y = settings.EXIT[:2]
        name = "Exit portal"
    else:
        target_x, target_y, name = target.x, target.y, target.name
    from math import atan2, degrees
    bearing = degrees(atan2(-(target_x-p.x), target_y-p.y))
    difference = (bearing - p.heading + 180) % 360 - 180
    if abs(difference) < 35:
        direction = "AHEAD"
    elif abs(difference) > 145:
        direction = "BEHIND"
    elif difference > 0:
        direction = "LEFT"
    else:
        direction = "RIGHT"
    distance = round(hypot(target_x-p.x, target_y-p.y))
    return f"{name}: {distance}m {direction}"
