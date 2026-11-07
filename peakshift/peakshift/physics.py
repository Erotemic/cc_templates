"""Small, readable, pygame-free platformer model.

The screen's top-left corner is (0, 0); Y grows DOWN. We resolve movement
one axis at a time, so a block can stop falling without blocking walking.
The core moves, jumps, dashes and respawns even before any student TODOs.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from . import levels, settings, student


@dataclass
class Controls:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    jump_pressed: bool = False
    jump_held: bool = False
    dash_pressed: bool = False
    grab_held: bool = False  # Hold C near rock; UP / DOWN climb or descend


@dataclass
class Rect:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    def overlaps(self, other: "Rect") -> bool:
        return (self.x < other.right and self.right > other.x
                and self.y < other.bottom and self.bottom > other.y)


@dataclass
class MovingPlatform:
    x: float
    y: float
    w: float
    left_limit: float
    right_limit: float
    speed: float = 72.0
    direction: int = 1
    delta_x: float = 0.0

    @property
    def rect(self) -> Rect:
        return Rect(self.x, self.y, self.w, 8)


@dataclass
class CrumbleBlock:
    col: int
    row: int
    timer: float = 0.0
    broken: bool = False

    @property
    def rect(self) -> Rect:
        t = settings.TILE
        return Rect(self.col * t, self.row * t, t, t)


@dataclass
class Player:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    facing: int = 1
    on_ground: bool = False
    wall_side: int = 0     # -1: wall LEFT, +1: wall RIGHT
    dashes: int = 1
    dash_time: float = 0.0
    coyote: float = 0.0
    jump_buffer: float = 0.0
    wall_lock: float = 0.0
    grip_left: float = settings.WALL_GRIP_SECONDS
    grabbing: bool = False
    jump_was_held: bool = False
    ground_platform: MovingPlatform | None = None

    @property
    def rect(self) -> Rect:
        return Rect(self.x, self.y, settings.PLAYER_W, settings.PLAYER_H)

    @property
    def right(self) -> float:
        return self.x + settings.PLAYER_W

    @property
    def bottom(self) -> float:
        return self.y + settings.PLAYER_H


class Game:
    """Public state students can inspect or update from their mission hooks."""

    def __init__(self, rooms: dict[str, levels.Room] | None = None,
                 start: str | None = None):
        self.rooms = levels.ROOMS if rooms is None else rooms
        self.start_room = levels.START_ROOM if start is None else start
        levels.validate_rooms(self.rooms, self.start_room)
        self.deaths = 0
        self.berries = 0
        self.elapsed = 0.0
        self.events: list[str] = []
        self.finished = False
        self.room_key = self.start_room
        self.room: levels.Room
        self.player: Player
        self.checkpoint: tuple[float, float]
        self.collected_berries: set[tuple[int, int]] = set()
        self.used_crystals: set[tuple[int, int]] = set()
        self.blocks: dict[tuple[int, int], CrumbleBlock] = {}
        self.platforms: list[MovingPlatform] = []
        self.ledges: list[Rect] = []
        self.load_room(self.room_key)

    @property
    def world_height(self) -> int:
        return len(self.room.tiles) * settings.TILE

    def load_room(self, key: str) -> None:
        self.room_key = key
        self.room = self.rooms[key]
        t = settings.TILE
        col, row = levels.find(self.room.tiles, "P")[0]
        position = (col * t + (t - settings.PLAYER_W) / 2,
                    (row + 1) * t - settings.PLAYER_H)
        self.checkpoint = position
        self.player = Player(*position)
        self.collected_berries = set()
        self.used_crystals = set()
        self.blocks = {
            (col, row): CrumbleBlock(col, row)
            for col, row in levels.find(self.room.tiles, "b")
        }
        self.solids = [Rect(col * t, row * t, t, t)
                       for row, line in enumerate(self.room.tiles)
                       for col, letter in enumerate(line) if letter == "#"]
        self.trigger_tiles = [(col, row, letter)
                              for row, line in enumerate(self.room.tiles)
                              for col, letter in enumerate(line)
                              if letter in "^C*RG"]
        self.wind_tiles = [Rect(col * t, row * t, t, t)
                           for col, row in levels.find(self.room.tiles, "w")]
        self.ledges = [Rect(x, y, w, 8)
                       for x, y, w in levels.one_way_runs(self.room.tiles)]
        self.platforms = [
            MovingPlatform(x=x, y=y, w=w,
                           left_limit=max(0, x - 64),
                           right_limit=min(settings.WIDTH - w, x + 64))
            for x, y, w in levels.moving_platform_runs(self.room.tiles)
        ]
        self.events.append("room")

    def die(self) -> None:
        self.deaths += 1
        self.player = Player(*self.checkpoint)
        # A death resets the room's optional mechanisms, not its checkpoint.
        self.used_crystals.clear()
        for block in self.blocks.values():
            block.timer = 0
            block.broken = False
        self.events.append("hurt")

    def restart(self) -> None:
        """R restarts the CURRENT room; a finished game starts from room 1."""
        if self.finished:
            self.finished = False
            self.deaths = 0
            self.berries = 0
            self.elapsed = 0.0
            self.load_room(self.start_room)
        else:
            self.load_room(self.room_key)

    def advance(self) -> None:
        if self.room.next_room is None:
            self.finished = True
            self.events.append("win")
        else:
            self.load_room(self.room.next_room)


def approach(value: float, target: float, amount: float) -> float:
    """Move value toward target without overshooting it."""
    if value < target:
        return min(value + amount, target)
    return max(value - amount, target)


def solid_rects(game: Game) -> list[Rect]:
    """Solid rock is fixed in each room, so reuse the collision geometry."""
    return game.solids


def _touch_wall(player: Player, blocks: list[Rect]) -> int:
    """Small sensors find a wall even when vx is zero after a collision."""
    inner_y = player.y + 3
    inner_h = settings.PLAYER_H - 6
    for side in (-1, 1):
        sx = player.x - 1.5 if side == -1 else player.right - 0.1
        sensor = Rect(sx, inner_y, 1.6, inner_h)
        if any(sensor.overlaps(block) for block in blocks):
            return side
    return 0


def _move_x(player: Player, dt: float, blocks: list[Rect]) -> None:
    old_x = player.x
    player.x += player.vx * dt
    if player.vx > 0:
        for block in blocks:
            if player.rect.overlaps(block) and old_x + settings.PLAYER_W <= block.x + 0.01:
                player.x = min(player.x, block.x - settings.PLAYER_W)
                player.vx = 0
                player.dash_time = 0
    elif player.vx < 0:
        for block in blocks:
            if player.rect.overlaps(block) and old_x >= block.right - 0.01:
                player.x = max(player.x, block.right)
                player.vx = 0
                player.dash_time = 0
    player.x = max(0.0, min(player.x, settings.WIDTH - settings.PLAYER_W))
    if player.x in (0.0, settings.WIDTH - settings.PLAYER_W):
        player.vx = 0.0


def _move_y(player: Player, dt: float, blocks: list[Rect],
            platforms: list[MovingPlatform], ledges: list[Rect]) -> bool:
    old_y = player.y
    old_bottom = player.bottom
    player.y += player.vy * dt
    landed = False
    player.ground_platform = None
    if player.vy >= 0:
        # Resolve against the TOPMOST crossed support, including platforms.
        hits: list[tuple[float, MovingPlatform | None]] = []
        for block in blocks:
            if (player.right > block.x + 0.1 and player.x < block.right - 0.1
                    and old_bottom <= block.y + 0.05 and player.bottom >= block.y):
                hits.append((block.y, None))
        for ledge in ledges:
            if (player.right > ledge.x + 0.1 and player.x < ledge.right - 0.1
                    and old_bottom <= ledge.y + 0.05 and player.bottom >= ledge.y):
                hits.append((ledge.y, None))
        for platform in platforms:
            rect = platform.rect
            if (player.right > rect.x + 0.1 and player.x < rect.right - 0.1
                    and old_bottom <= rect.y + 0.05 and player.bottom >= rect.y):
                hits.append((rect.y, platform))
        if hits:
            top, platform = min(hits, key=lambda hit: hit[0])
            player.y = top - settings.PLAYER_H
            player.vy = 0.0
            player.ground_platform = platform
            landed = True
    else:
        for block in blocks:
            if (player.right > block.x + 0.1 and player.x < block.right - 0.1
                    and old_y >= block.bottom - 0.05 and player.y <= block.bottom):
                player.y = max(player.y, block.bottom)
                player.vy = 0.0
                player.dash_time = 0
    return landed


def _touch_symbols(game: Game) -> None:
    """Handle hazards, checkpoints, berries, crystals and exits."""
    player = game.player
    t = settings.TILE
    for col, row, letter in game.trigger_tiles:
        # Spikes have a forgiving inset, unlike solid rock.
        padding = 6 if letter == "^" else 2
        rect = Rect(col * t + padding, row * t + padding,
                    t - 2 * padding, t - 2 * padding)
        if not player.rect.overlaps(rect):
            continue
        pos = (col, row)
        if letter == "^":
            game.die()
            return
        if letter == "C":
            checkpoint = (col * t + (t - settings.PLAYER_W) / 2,
                          (row + 1) * t - settings.PLAYER_H)
            if checkpoint != game.checkpoint:
                game.checkpoint = checkpoint
                game.events.append("checkpoint")
        elif letter == "*" and pos not in game.collected_berries:
            game.collected_berries.add(pos)
            student.collect_berry(game)
            game.events.append("berry")
        elif letter == "R" and pos not in game.used_crystals:
            if student.refill_dash_from_crystal(player):
                game.used_crystals.add(pos)
                game.events.append("crystal")
        elif letter == "G":
            game.advance()
            return


def _substep(game: Game, controls: Controls, dt: float) -> None:
    if game.finished:
        return
    player = game.player
    blocks = solid_rects(game)

    # Move optional platforms. They already carry you when you stand on them.
    for platform in game.platforms:
        before = platform.x
        student.move_platform(platform, dt)
        platform.delta_x = platform.x - before
    if player.on_ground and player.ground_platform is not None:
        player.x += player.ground_platform.delta_x

    if controls.jump_pressed:
        player.jump_buffer = settings.JUMP_BUFFER
        player.jump_was_held = True
    else:
        player.jump_buffer = max(0.0, player.jump_buffer - dt)
    if player.on_ground:
        player.coyote = settings.COYOTE_TIME
    else:
        player.coyote = max(0.0, player.coyote - dt)
    player.wall_lock = max(0.0, player.wall_lock - dt)

    # A buffered jump may succeed on a landing frame, too (see below).
    if player.jump_buffer > 0 and player.dash_time <= 0:
        if player.coyote > 0:
            player.vy = -settings.JUMP_SPEED
            player.on_ground = False
            player.ground_platform = None
            player.coyote = 0.0
            player.jump_buffer = 0.0
            game.events.append("jump")
        elif player.wall_side:
            player.vy = -settings.WALL_JUMP_Y
            player.vx = -player.wall_side * settings.WALL_JUMP_X
            player.facing = -player.wall_side
            player.wall_lock = settings.WALL_LOCK
            player.jump_buffer = 0.0
            game.events.append("jump")

    horizontal = int(controls.right) - int(controls.left)
    if horizontal and player.wall_lock <= 0:
        player.facing = horizontal

    # Grip a solid cliff. Climbing uses stamina; landing refills it.
    # A wall jump always wins over a grab so the player can kick away.
    player.grabbing = (controls.grab_held and player.wall_side != 0
                       and not player.on_ground and player.wall_lock <= 0
                       and player.dash_time <= 0 and player.grip_left > 0)
    if player.grabbing:
        player.grip_left = max(0.0, player.grip_left - dt)
        player.vx = 0.0

    # Exactly one dash until your next landing. Direction is sampled on press.
    if controls.dash_pressed and player.dashes > 0 and player.dash_time <= 0:
        dx = horizontal
        dy = int(controls.down) - int(controls.up)
        if dx == 0 and dy == 0:
            dx = player.facing
        magnitude = hypot(dx, dy)
        player.vx = settings.DASH_SPEED * dx / magnitude
        player.vy = settings.DASH_SPEED * dy / magnitude
        player.dash_time = settings.DASH_SECONDS
        player.dashes -= 1
        player.jump_buffer = 0.0
        player.coyote = 0.0
        player.on_ground = False
        player.ground_platform = None
        game.events.append("dash")

    if player.dash_time > 0:
        player.grabbing = False
        player.dash_time = max(0.0, player.dash_time - dt)
    else:
        if player.wall_lock <= 0 and not player.grabbing:
            target = horizontal * settings.RUN_SPEED
            accel = settings.RUN_ACCEL if player.on_ground else settings.AIR_ACCEL
            if horizontal == 0:
                accel = settings.FRICTION if player.on_ground else settings.AIR_ACCEL * 0.55
            player.vx = approach(player.vx, target, accel * dt)
        if player.grabbing:
            # Stick to the rock, or climb with up/down. No hidden magic jump.
            player.vy = (-settings.WALL_CLIMB_SPEED if controls.up
                         else settings.WALL_CLIMB_SPEED if controls.down else 0.0)
        else:
            player.vy = min(settings.MAX_FALL, player.vy + settings.GRAVITY * dt)
        leaning = (controls.right and player.wall_side == 1) or (
            controls.left and player.wall_side == -1)
        if not player.grabbing and not player.on_ground and player.wall_side and leaning and player.vy > 0:
            player.vy = min(player.vy, settings.WALL_SLIDE)
        if not player.grabbing and player.jump_was_held and not controls.jump_held and not controls.jump_pressed:
            if player.vy < 0:
                player.vy *= settings.JUMP_CUT
            player.jump_was_held = False

    # Wind changes acceleration, not teleportation; lesson hook starts at 0.
    inside_wind = any(player.rect.overlaps(wind) for wind in game.wind_tiles)
    player.vx += student.wind_acceleration(player, inside_wind) * dt
    player.vx = max(-settings.RUN_SPEED * 1.8,
                    min(settings.RUN_SPEED * 1.8, player.vx)) if player.dash_time <= 0 else player.vx

    _move_x(player, dt, blocks)
    was_grounded = player.on_ground
    active_crumble_tops = [block.rect for block in game.blocks.values()
                           if not block.broken]
    player.on_ground = _move_y(player, dt, blocks, game.platforms,
                               game.ledges + active_crumble_tops)
    if player.on_ground:
        player.grip_left = settings.WALL_GRIP_SECONDS
        player.grabbing = False
        player.dashes = 1
        player.coyote = settings.COYOTE_TIME
        if not was_grounded:
            game.events.append("land")
        if player.jump_buffer > 0:
            player.vy = -settings.JUMP_SPEED
            player.on_ground = False
            player.ground_platform = None
            player.coyote = 0.0
            player.jump_buffer = 0.0
            game.events.append("jump")
    player.wall_side = _touch_wall(player, blocks)
    if player.wall_side == 0:
        player.grabbing = False

    for block in game.blocks.values():
        support = (not block.broken and abs(player.bottom - block.rect.y) < 1.5
                   and player.right > block.rect.x + 1
                   and player.x < block.rect.right - 1)
        student.update_crumble(block, dt, support)

    if player.y > game.world_height + settings.CAMERA_OVERSCROLL:
        game.die()
        return
    _touch_symbols(game)


def update(game: Game, controls: Controls, seconds: float) -> None:
    """Advance the simulation; no window or graphics library is required.

    Large render frames are broken into small physics steps. A key PRESS is
    consumed once, not repeated on each substep. Held keys persist.
    """
    game.events.clear()
    if game.finished:
        return
    seconds = max(0.0, min(seconds, settings.MAX_FRAME))
    remaining = seconds
    first = True
    while remaining > 1e-9:
        dt = min(remaining, settings.STEP)
        inp = controls if first else Controls(
            left=controls.left, right=controls.right, up=controls.up,
            down=controls.down, jump_held=controls.jump_held,
            grab_held=controls.grab_held)
        _substep(game, inp, dt)
        if game.finished or "hurt" in game.events or "room" in game.events:
            # On a transition, don't simulate leftover time in the next room.
            break
        remaining -= dt
        first = False
    student.record_time(game, seconds)
