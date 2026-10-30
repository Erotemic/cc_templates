"""An infinite tower built from deterministic, smoothly varying noise.

Only a handful of tiers near the camera are constructed each frame.
The same tier always has the same coordinates for a given TOWER_SEED.
There is no last tier, large level file, or third-party noise dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor

from . import settings, student


@dataclass(frozen=True)
class Platform:
    x: float
    y: float
    width: int
    height: int
    tier: int
    kind: str = "main"

    @property
    def right(self) -> float:
        return self.x + self.width


@dataclass(frozen=True)
class Ladder:
    x: float
    top: float
    bottom: float
    width: int = 22


@dataclass(frozen=True)
class PickupSpec:
    x: float
    y: float
    tier: int
    kind: str = "gem"
    size: int = settings.PICKUP_SIZE


# A tiny implementation of 1D value noise. Interpolation between fixed
# random points makes the platforms wander smoothly, not teleport at random.
def _random_at(point: int, seed: int) -> float:
    number = (point * 374761393 + seed * 668265263) & 0xFFFFFFFF
    number = ((number ^ (number >> 13)) * 1274126177) & 0xFFFFFFFF
    number ^= number >> 16
    return (number / 0xFFFFFFFF) * 2 - 1


def smooth_noise(position: float, seed: int) -> float:
    left = floor(position)
    amount = position - left
    amount = amount * amount * (3 - 2 * amount)  # smoothstep
    a = _random_at(left, seed)
    b = _random_at(left + 1, seed)
    return a + (b - a) * amount


def platform_center(tier: int) -> float:
    """A reachable, gently wandering primary route up the tower.

    MISSION 6, PART 2 (optional, after student.platform_height_offset):
    1. First try changing the noise amplitude 170 or 35.
    2. Then try changing 0.12 or 0.32 (how quickly the path wanders).
    3. Compare x at tier and tier+1. Keep the gap below ~110 pixels,
       or you might generate an impossible jump.
    4. Try creating different tower regions with different patterns.
    """
    seed = student.TOWER_SEED
    first_wave = 170 * smooth_noise(tier * 0.12, seed)
    detail = 35 * smooth_noise(tier * 0.32, seed + 100)
    return 480 + first_wave + detail


def platform_y(tier: int) -> float:
    """Vertical ledge position. See MISSION 6 in student.py.

    The offset is zero by default. Keep it small (around +/-20 pixels):
    world.tier_numbers() assumes floors are close to the 100-pixel grid.
    The noise is deterministic, so revisiting tier 100 gives the same Y.
    """
    if tier == 0:
        return settings.GROUND_Y
    noise = smooth_noise(tier * 0.65, student.TOWER_SEED + 900)
    return (settings.GROUND_Y - tier * settings.TIER_HEIGHT
            + student.platform_height_offset(tier, noise))


def main_platform(tier: int) -> Platform:
    if tier < 1:
        raise ValueError("The starting ground is tier 0, not a platform")
    return Platform(
        x=platform_center(tier) - settings.PLATFORM_WIDTH / 2,
        y=platform_y(tier),
        width=settings.PLATFORM_WIDTH,
        height=settings.PLATFORM_HEIGHT,
        tier=tier,
    )


def side_platform(tier: int) -> Platform | None:
    """Optional side ledges, meant for exploration, not required to advance."""
    if tier % 4 != 0:
        return None
    main = main_platform(tier)
    direction = -1 if (tier // 4) % 2 else 1
    center = platform_center(tier) + direction * 257
    width = 118
    x = max(settings.LEFT_WALL + 18,
            min(settings.RIGHT_WALL - width - 18, center - width / 2))
    if (x < main.right + 26) and (x + width > main.x - 26):
        return None  # Avoid overlapping the guaranteed main route.
    return Platform(x, main.y + 22, width, settings.PLATFORM_HEIGHT,
                    tier, "side")


def ladder_to(tier: int) -> Ladder:
    """A ladder between consecutive floors; decoration until mission 2."""
    upper = main_platform(tier)
    lower_top = platform_y(tier - 1)
    # Extend above the ledge so DOWN works while standing on it too.
    return Ladder(upper.x + upper.width / 2 - 11,
                  upper.y - 34, lower_top + 3)


def pickup_for_tier(tier: int) -> PickupSpec | None:
    """Placed collectibles for mission 7.

    The student writes the collection behavior, but the world placement is
    already deterministic and visible. Most pickups sit over side routes so
    they invite exploration without blocking the main path upward.
    """
    if tier < 2 or tier % 5 != 3:
        return None
    platform = side_platform(tier) or main_platform(tier)
    noise = smooth_noise(tier * 0.28, student.TOWER_SEED + 1500)
    margin = 20
    usable = max(8, platform.width - 2 * margin)
    x = platform.x + margin + ((noise + 1) * 0.5) * usable
    kind = "heart" if tier % 15 == 3 else "gem"
    return PickupSpec(x=x, y=platform.y - 18, tier=tier, kind=kind)


def tier_numbers(top_y: float, bottom_y: float) -> range:
    """Return tiers in/near this world-Y interval.

    MISSION 6: small height offsets (within about 20 px) are supported by
    the extra two tiers of padding; larger offsets need a wider search.
    """
    if top_y > bottom_y:
        raise ValueError("top_y must be <= bottom_y")
    first = max(1, floor((settings.GROUND_Y - bottom_y) /
                         settings.TIER_HEIGHT) - 2)
    last = max(first, ceil((settings.GROUND_Y - top_y) /
                           settings.TIER_HEIGHT) + 2)
    return range(first, last + 1)


def platforms_near(top_y: float, bottom_y: float) -> list[Platform]:
    result = []
    for tier in tier_numbers(top_y, bottom_y):
        result.append(main_platform(tier))
        side = side_platform(tier)
        if side is not None:
            result.append(side)
    return result


def ladders_near(top_y: float, bottom_y: float) -> list[Ladder]:
    return [ladder_to(tier) for tier in tier_numbers(top_y, bottom_y)]


def pickups_near(top_y: float, bottom_y: float) -> list[PickupSpec]:
    result = []
    for tier in tier_numbers(top_y, bottom_y):
        pickup = pickup_for_tier(tier)
        if pickup is not None:
            result.append(pickup)
    return result
