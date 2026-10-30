"""Simple platformer physics. No pygame import: easy to run and test.

The player uses a position (x, y) and a velocity (vx, vy). Y grows DOWN.
The collision engine only lands on TOPS of platforms. Tower side walls are
solid, so they can eventually be used for wall jumps.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import settings, student, world

# All dialogue timing is in seconds. No pygame is needed to test it.
SPEECH_CHARACTER_TIME = 0.038
SPEECH_LINGER_TIME = 1.85
SPEECH_GAP_TIME = 0.85


@dataclass(frozen=True)
class Controls:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    jump_pressed: bool = False


@dataclass
class Player:
    x: float = 466.0
    y: float = settings.GROUND_Y - settings.PLAYER_HEIGHT
    vx: float = 0.0
    vy: float = 0.0
    on_ground: bool = True
    climbing: bool = False
    wall_side: int = 0
    wall_push_time: float = 0.0
    invulnerable_time: float = 0.0

    @property
    def right(self) -> float:
        return self.x + settings.PLAYER_WIDTH

    @property
    def bottom(self) -> float:
        return self.y + settings.PLAYER_HEIGHT


@dataclass
class Enemy:
    x: float
    y: float
    left_limit: float
    right_limit: float
    tier: int
    width: int = 26
    height: int = 25
    speed: float = 65.0
    direction: int = 1


@dataclass
class MovingPlatform:
    """A blue platform. Its position is mutable for student mission 5."""

    x: float
    y: float
    left_limit: float
    right_limit: float
    tier: int
    width: int = 110
    height: int = settings.PLATFORM_HEIGHT
    speed: float = 55.0
    direction: int = 1
    kind: str = "moving"

    @property
    def right(self) -> float:
        return self.x + self.width


@dataclass
class Pickup:
    """Placed treasure. Mission 7 decides what collecting one does."""

    x: float
    y: float
    tier: int
    kind: str = "gem"
    width: int = settings.PICKUP_SIZE
    height: int = settings.PICKUP_SIZE
    collected: bool = False

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height


@dataclass
class Heckler:
    """A taunting spectator who rides a lift slightly above the player."""

    x: float = settings.RIGHT_WALL - 52
    y: float = settings.GROUND_Y - settings.PLAYER_HEIGHT - settings.HECKLER_OFFSET
    width: int = 28
    height: int = 34
    platform_width: int = 54
    platform_height: int = 16
    climb_speed: float = 190.0
    # Speech state is independent of drawing and audio. The painter displays
    # only the revealed letters; the speech engine decides when to hide it.
    text: str = ""
    revealed: int = 0
    typing_time: float = 0.0
    linger_time: float = 0.0
    gap_time: float = 0.0
    last_line: str = ""
    # The engine can hold a student-generated event until the current line
    # has finished speaking. Students do not need to manage speech timing.
    queued_comeback: str = ""

    @property
    def platform_x(self) -> float:
        return self.x - 13

    @property
    def platform_y(self) -> float:
        return self.y + self.height - 2


@dataclass
class Game:
    player: Player = field(default_factory=Player)
    camera_y: float = settings.GROUND_Y - settings.VIEW_HEIGHT + 85
    hazard_y: float = settings.GROUND_Y + 32
    hearts: int = 3
    super_mode: bool = False
    failures: int = 0
    highest_tier: int = 0
    pickups_collected: int = 0
    # MISSION 8: these are empty memory slots for the student's state machine.
    # The ENGINE does NOT detect falls or returns. See student.py.
    peak_player_y: float = settings.GROUND_Y - settings.PLAYER_HEIGHT
    comeback_peak_y: float = settings.GROUND_Y - settings.PLAYER_HEIGHT
    comeback_pending: bool = False
    fall_count: int = 0
    enemies: dict[int, Enemy] = field(default_factory=dict)
    moving_platforms: dict[int, MovingPlatform] = field(default_factory=dict)
    pickups: dict[int, Pickup] = field(default_factory=dict)
    heckler: Heckler = field(default_factory=Heckler)
    events: list[str] = field(default_factory=list)  # Sounds for the pygame loop.

    def reset(self) -> None:
        """Return to the ground after hitting the danger floor or losing HP."""
        failures = self.failures + 1
        self.player = Player()
        self.camera_y = settings.GROUND_Y - settings.VIEW_HEIGHT + 85
        self.hazard_y = settings.GROUND_Y + 32
        self.hearts = 3
        self.pickups_collected = 0
        self.peak_player_y = self.player.y
        self.comeback_peak_y = self.player.y
        self.comeback_pending = False
        self.fall_count = 0
        self.enemies.clear()
        self.moving_platforms.clear()
        self.pickups.clear()
        self.heckler = Heckler()
        self.failures = failures
        self.events.append("reset")

    def nearby_enemies(self) -> list[Enemy]:
        """Spawn/cull enemies near the camera so memory doesn't grow forever."""
        visible = world.tier_numbers(self.camera_y - 150,
                                     self.camera_y + settings.VIEW_HEIGHT + 150)
        active = set(visible)
        self.enemies = {n: enemy for n, enemy in self.enemies.items()
                        if n in active}
        for tier in visible:
            if tier % 6 != 0 or tier in self.enemies:
                continue
            platform = world.main_platform(tier)
            enemy = Enemy(
                x=platform.x + 14,
                y=platform.y - 25,
                left_limit=platform.x + 8,
                right_limit=platform.right - 26 - 8,
                tier=tier,
            )
            self.enemies[tier] = enemy
        return list(self.enemies.values())

    def nearby_moving_platforms(self) -> list[MovingPlatform]:
        """Spawn/cull mission-5 platforms as the camera climbs.

        They begin stationary. Collisions, artwork and player-carrying are
        already implemented so students can focus on movement in student.py.
        They are optional side ledges; the main tower remains reachable.
        """
        visible = world.tier_numbers(self.camera_y - 150,
                                     self.camera_y + settings.VIEW_HEIGHT + 150)
        active = set(visible)
        self.moving_platforms = {
            tier: platform for tier, platform in self.moving_platforms.items()
            if tier in active
        }
        for tier in visible:
            if tier % 6 != 2 or tier in self.moving_platforms:
                continue
            main = world.main_platform(tier)
            width = 110
            place_right = (tier // 6) % 2 == 0
            side = world.side_platform(tier)
            if side is not None:
                place_right = side.x < main.x
            desired_x = (main.right + 42 if place_right
                         else main.x - width - 42)
            x = max(settings.LEFT_WALL + 28,
                    min(settings.RIGHT_WALL - width - 28, desired_x))
            left = max(settings.LEFT_WALL + 24, x - 48)
            right = min(settings.RIGHT_WALL - width - 24, x + 48)
            self.moving_platforms[tier] = MovingPlatform(
                x=x, y=main.y + 38, left_limit=left,
                right_limit=right, tier=tier,
            )
        return list(self.moving_platforms.values())

    def nearby_pickups(self) -> list[Pickup]:
        """Spawn/cull pickups near the camera.

        Pickups are pre-placed by the world. Mission 7 only defines their
        collection behavior, not their positions.
        """
        visible = world.tier_numbers(self.camera_y - 150,
                                     self.camera_y + settings.VIEW_HEIGHT + 150)
        active = set(visible)
        self.pickups = {
            tier: pickup for tier, pickup in self.pickups.items()
            if tier in active
        }
        for tier in visible:
            if tier in self.pickups:
                continue
            spec = world.pickup_for_tier(tier)
            if spec is None:
                continue
            self.pickups[tier] = Pickup(
                x=spec.x - spec.size / 2,
                y=spec.y - spec.size / 2,
                tier=spec.tier,
                kind=spec.kind,
                width=spec.size,
                height=spec.size,
            )
        return list(self.pickups.values())


def _overlaps(a_left: float, a_right: float,
              b_left: float, b_right: float) -> bool:
    return a_left < b_right and a_right > b_left


def _touching_ladder(player: Player, ladder: world.Ladder) -> bool:
    return (_overlaps(player.x + 6, player.right - 6,
                      ladder.x, ladder.x + ladder.width)
            and player.y < ladder.bottom and player.bottom > ladder.top)


def _touching_pickup(player: Player, pickup: Pickup) -> bool:
    return (_overlaps(player.x, player.right, pickup.x, pickup.right)
            and player.y < pickup.bottom and player.bottom > pickup.y)


def _start_heckler_speech(game: Game, line: str) -> None:
    """Start a new, self-closing typewriter bubble on the elevator."""
    heckler = game.heckler
    heckler.text = line
    heckler.revealed = 1  # An immediate first letter makes the response clear.
    heckler.typing_time = 0.0
    heckler.linger_time = SPEECH_LINGER_TIME
    if line[0].isalnum():
        game.events.append("heckler_mumble_1")


def _advance_heckler_speech(game: Game, seconds: float) -> None:
    """Reveal characters, emit a few little mumble sounds, then close."""
    heckler = game.heckler
    if not heckler.text:
        heckler.gap_time = max(0.0, heckler.gap_time - seconds)
        return

    if heckler.revealed < len(heckler.text):
        heckler.typing_time += seconds
        while (heckler.typing_time >= SPEECH_CHARACTER_TIME
               and heckler.revealed < len(heckler.text)):
            heckler.typing_time -= SPEECH_CHARACTER_TIME
            index = heckler.revealed
            heckler.revealed += 1
            # Sound only every third letter to avoid an irritating buzz.
            if heckler.text[index].isalnum() and index % 3 == 0:
                game.events.append(f"heckler_mumble_{(index // 3) % 3 + 1}")
        return

    heckler.linger_time -= seconds
    if heckler.linger_time <= 0:
        heckler.text = ""
        heckler.revealed = 0
        heckler.typing_time = 0.0
        heckler.gap_time = SPEECH_GAP_TIME


def _update_heckler(game: Game, seconds: float) -> None:
    """Move the elevator and play speech events generated by the student.

    MISSION 8: the student, not the engine, detects a fall, remembers it,
    and decides when the player has returned. The speech system only
    receives a line to say; it doesn't decide what gameplay event occurred.
    """
    heckler = game.heckler
    target_y = game.player.y - settings.HECKLER_OFFSET
    if target_y < heckler.y:
        climb = heckler.climb_speed * seconds
        heckler.y = max(target_y, heckler.y - climb)

    # Run this on EVERY frame, including while speaking. An event can
    # happen during a sentence; queue it until the bubble becomes free.
    comeback_line = student.update_heckler_comeback(game, heckler)
    if comeback_line:
        heckler.queued_comeback = comeback_line

    _advance_heckler_speech(game, seconds)
    if heckler.text or heckler.gap_time > 0:
        return

    if heckler.queued_comeback:
        line = heckler.queued_comeback
        heckler.queued_comeback = ""
        _start_heckler_speech(game, line)
        return

    line = student.heckler_line(game, heckler) or ""
    if line and line != heckler.last_line:
        heckler.last_line = line
        _start_heckler_speech(game, line)

def update(game: Game, controls: Controls, seconds: float) -> None:
    """Advance the game by one frame, invoking the student missions."""
    if not 0 <= seconds <= 0.05:
        raise ValueError("Frame time must be between 0 and 0.05 seconds")

    game.events.clear()
    player = game.player
    player.invulnerable_time = max(0, player.invulnerable_time - seconds)
    player.wall_push_time = max(0, player.wall_push_time - seconds)

    nearby_ladders = world.ladders_near(player.y - 40, player.bottom + 40)
    touching_ladder = any(_touching_ladder(player, ladder)
                          for ladder in nearby_ladders)
    student.update_ladder_state(player, controls, touching_ladder)
    if not touching_ladder:
        player.climbing = False

    if controls.jump_pressed:
        if player.on_ground or player.climbing or game.super_mode:
            # Super mode permits another jump even while already airborne.
            player.vy = -settings.JUMP_SPEED
            player.on_ground = False
            player.climbing = False
            game.events.append("jump")
        elif student.try_wall_jump(player, controls.jump_pressed):
            player.wall_push_time = max(player.wall_push_time, 0.16)
            game.events.append("jump")

    moving_platforms = game.nearby_moving_platforms()
    for platform in moving_platforms:
        riding = (player.on_ground and not controls.jump_pressed
                  and abs(player.bottom - platform.y) < 1.0
                  and _overlaps(player.x, player.right,
                                platform.x, platform.right))
        old_x = platform.x
        student.move_platform(platform, seconds)
        if riding:
            player.x += platform.x - old_x

    if player.wall_push_time <= 0:
        direction = int(controls.right) - int(controls.left)
        player.vx = direction * settings.RUN_SPEED
    player.x += player.vx * seconds
    player.wall_side = 0
    if player.x <= settings.LEFT_WALL:
        player.x = settings.LEFT_WALL
        player.wall_side = -1
    elif player.right >= settings.RIGHT_WALL:
        player.x = settings.RIGHT_WALL - settings.PLAYER_WIDTH
        player.wall_side = 1

    was_on_ground = player.on_ground
    old_bottom = player.bottom
    if player.climbing:
        player.vy = (int(controls.down) - int(controls.up)) * settings.CLIMB_SPEED
    else:
        player.vy = min(settings.MAX_FALL_SPEED,
                        player.vy + settings.GRAVITY * seconds)
    player.y += player.vy * seconds
    player.on_ground = False

    if not player.climbing and player.vy >= 0:
        possible = [settings.GROUND_Y]
        for platform in (world.platforms_near(old_bottom - 30,
                                              player.bottom + 30)
                         + moving_platforms):
            if _overlaps(player.x, player.right,
                         platform.x, platform.right):
                possible.append(platform.y)
        landed_on = [top for top in possible
                     if old_bottom <= top + 0.001 and player.bottom >= top]
        if landed_on:
            player.y = min(landed_on) - settings.PLAYER_HEIGHT
            player.vy = 0
            player.on_ground = True
            if not was_on_ground:
                game.events.append("land")

    top_screen_limit = 210
    bottom_screen_limit = settings.VIEW_HEIGHT - 105
    if player.y - game.camera_y < top_screen_limit:
        game.camera_y = player.y - top_screen_limit
    elif player.y - game.camera_y > bottom_screen_limit:
        base_camera = settings.GROUND_Y - settings.VIEW_HEIGHT + 85
        game.camera_y = min(base_camera, player.y - bottom_screen_limit)

    new_tier = max(0, int((settings.GROUND_Y - player.y)
                          // settings.TIER_HEIGHT))
    if new_tier // 10 > game.highest_tier // 10:
        game.events.append("milestone")
    game.highest_tier = max(game.highest_tier, new_tier)

    _update_heckler(game, seconds)

    for pickup in game.nearby_pickups():
        if pickup.collected:
            continue
        if _touching_pickup(player, pickup):
            was_collected = pickup.collected
            student.collect_pickup(game, pickup)
            if pickup.collected and not was_collected:
                game.events.append("pickup")

    enemies = game.nearby_enemies()
    for enemy in enemies:
        student.move_enemy(enemy, seconds)
        if (not game.super_mode
                and player.invulnerable_time <= 0
                and _overlaps(player.x, player.right,
                              enemy.x, enemy.x + enemy.width)
                and player.y < enemy.y + enemy.height
                and player.bottom > enemy.y):
            game.hearts -= 1
            game.events.append("hurt")
            player.invulnerable_time = 1.4
            player.vy = -310
            if game.hearts <= 0:
                game.reset()
                return

    student.move_rising_floor(game, seconds)
    if not game.super_mode and player.bottom > game.hazard_y:
        game.reset()
