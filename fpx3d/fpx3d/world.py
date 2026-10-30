"""The level is DATA, independent of Panda3D and easy to inspect.

Students can add a core or move a hazard simply by changing a number.
The 3D painter reads this data; the physics engine reads the SAME data.
That prevents invisible walls and mismatched collision coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random

from . import settings

Color = tuple[float, float, float, float]


@dataclass(frozen=True)
class Box:
    name: str
    x: float
    y: float
    z: float  # center of the box
    width: float
    depth: float
    height: float
    color: Color
    solid: bool = True
    blocks_walking: bool = False  # Only room walls block lateral movement.

    @property
    def top(self) -> float:
        return self.z + self.height / 2

    @property
    def bottom(self) -> float:
        return self.z - self.height / 2

    def under(self, x: float, y: float, margin: float = 0.0) -> bool:
        return (abs(x - self.x) <= self.width / 2 + margin
                and abs(y - self.y) <= self.depth / 2 + margin)


@dataclass(frozen=True)
class Pickup:
    name: str
    x: float
    y: float
    z: float  # center of the spinning gem
    kind: str  # 'core' opens the exit; 'bonus' is for a student exercise
    tint: Color


@dataclass(frozen=True)
class Pad:
    x: float
    y: float
    radius: float
    kind: str  # spring, danger, checkpoint


@dataclass(frozen=True)
class DroneStart:
    name: str
    x: float
    y: float
    z: float
    left: float
    right: float


@dataclass(frozen=True)
class LiftStart:
    name: str
    x: float
    y: float
    z: float  # top surface is z + 0.3
    left: float
    right: float


@dataclass(frozen=True)
class GuardianStart:
    """A visible robot character whose brain belongs to the student."""

    name: str
    x: float
    y: float
    chase_radius: float = 5.0


# Six required crystals on the ground, with a safe and predictable route.
# These are spread through three colored neighborhoods so searching matters.
CORES = (
    Pickup("Dawn prism", 0, -12, 1.25, "core", (1.0, 0.80, 0.40, 1)),
    Pickup("Copper prism", -11, -6, 1.25, "core", (1.0, 0.59, 0.41, 1)),
    Pickup("Ocean prism", 11, -3, 1.25, "core", (0.38, 0.87, 1.0, 1)),
    Pickup("Moss prism", -11, 6, 1.25, "core", (0.47, 1.0, 0.61, 1)),
    Pickup("Violet prism", 10, 8, 1.25, "core", (0.81, 0.58, 1.0, 1)),
    Pickup("Final prism", 0, 13, 1.25, "core", (1.0, 0.91, 0.46, 1)),
)

# These are optional. The engine makes them disappear on contact, but the
# STUDENT decides what reward they give in student.bonus_reward().
BONUSES = (
    Pickup("High ledge", -14.5, 9, 3.2, "bonus", (1.0, 0.91, 0.42, 1)),
    Pickup("Lookout", 13.5, 11, 3.3, "bonus", (1.0, 0.91, 0.42, 1)),
    Pickup("South garden", 15, -14, 1.25, "bonus", (1.0, 0.91, 0.42, 1)),
)
PICKUPS = CORES + BONUSES

PADS = (
    Pad(-9, 9, 1.25, "spring"),
    Pad(9, 11, 1.25, "spring"),
    Pad(-4.5, -4.0, 1.6, "danger"),
    Pad(5.4, 5.6, 1.65, "danger"),
    Pad(-13, 0, 1.4, "checkpoint"),
    Pad(12, 3, 1.4, "checkpoint"),
)

# Drones and scanner are present visually but stationary/inactive until the
# student implements their behavior. They can still be touched or inspected.
DRONES = (
    DroneStart("Copper sentry", -13, -3.0, 1.15, -17, -8),
    DroneStart("Azure sentry", 13, 6, 1.15, 8, 17),
)
LIFTS = (
    # High enough to pass underneath; the platform can still carry you.
    LiftStart("Garden slider", -12, 12, 2.05, -15, -8),
)

# A friendly-looking robot sentry near the beginning of the vault. It is
# deliberately stationary until the student writes its decision-making.
GUARDIANS = (
    GuardianStart("Clockwork Watcher", 6.5, -11.5, chase_radius=5.0),
)

SCANNER_CENTER = (0.0, 5.5)
SCANNER_RADIUS = 2.8


def make_boxes() -> tuple[Box, ...]:
    """Return a static environment with open central paths and side routes.

    Walkable space should FEEL open. Only the four outside walls stop
    sideways motion. Raised boxes are one-way landing platforms: the player
    may move beneath them without snagging on their sides. Decorative props
    never prevent movement. Art and physics still share these box specs.
    """
    c = {
        "floor": (0.13, 0.18, 0.29, 1),
        "wall": (0.19, 0.24, 0.36, 1),
        "slate": (0.30, 0.39, 0.51, 1),
        "gold": (0.87, 0.66, 0.31, 1),
        "path": (0.19, 0.36, 0.45, 1),
        "moss": (0.20, 0.48, 0.38, 1),
        "blue": (0.27, 0.53, 0.67, 1),
        "violet": (0.47, 0.36, 0.66, 1),
    }
    boxes = [
        Box("ground", 0, 0, -0.5, 42, 42, 1, c["floor"]),
        Box("north wall", 0, 21, 2.2, 42, 1, 4.4, c["wall"], blocks_walking=True),
        Box("south wall", 0, -21, 2.2, 42, 1, 4.4, c["wall"], blocks_walking=True),
        Box("east wall", 21, 0, 2.2, 1, 42, 4.4, c["wall"], blocks_walking=True),
        Box("west wall", -21, 0, 2.2, 1, 42, 4.4, c["wall"], blocks_walking=True),
        # A continuous lit route down the center, with side branches.
        Box("central walkway", 0, -1, 0.025, 4.0, 36, 0.05, c["path"], False),
        Box("left branch 1", -6, -6, 0.028, 12, 1.7, 0.05, c["moss"], False),
        Box("right branch 1", 6, -3, 0.028, 12, 1.7, 0.05, c["blue"], False),
        Box("left branch 2", -6, 6, 0.028, 12, 1.7, 0.05, c["moss"], False),
        Box("right branch 2", 6, 9, 0.028, 12, 1.7, 0.05, c["violet"], False),
        # Two destination balcony platforms for optional exploration.
        Box("moss balcony", -14.5, 9, 2.10, 5.0, 5.0, 0.3, c["moss"]),
        Box("azure balcony", 13.5, 11, 2.10, 5.0, 5.0, 0.3, c["blue"]),
        Box("moss crate step", -17.5, 9, 0.50, 2, 2.2, 1.0, c["slate"]),
        Box("azure crate step", 17.2, 11, 0.52, 2, 2.2, 1.04, c["slate"]),
    ]
    # Arch columns sit against the walls, not in side routes. The high
    # crossbeams are decoration; they cannot trap a first-person camera.
    for idx, y in enumerate((-8.5, 3, 13.8)):
        tone = (c["gold"], c["blue"], c["violet"])[idx]
        boxes.extend((
            Box(f"arch {idx} left", -20.3, y, 2.5, 1, 1.3, 5, c["slate"], False),
            Box(f"arch {idx} right", 20.3, y, 2.5, 1, 1.3, 5, c["slate"], False),
            Box(f"arch {idx} bridge", 0, y, 5.05, 41, 1.35, 0.75, tone, False),
        ))
    # Corner towers and their distinctive colored caps help navigation.
    caps = (c["gold"], c["blue"], c["moss"], c["violet"])
    for index, (x, y) in enumerate(((-20.7, -20.7), (20.7, -20.7),
                                    (-20.7, 20.7), (20.7, 20.7))):
        boxes.extend((
            Box(f"corner tower {index}", x, y, 3.1, 2, 2, 6.2, c["slate"]),
            Box(f"tower cap {index}", x, y, 6.4, 2.6, 2.6, 0.5, caps[index]),
        ))
    # Many small visual details, deterministic and not part of physics.
    rng = Random(2026)
    for i in range(48):
        x = rng.uniform(-19, 19)
        y = rng.uniform(-18, 18)
        if abs(x) < 6 or any((x-p.x)**2 + (y-p.y)**2 < 6 for p in PICKUPS):
            continue
        tone = c["moss"] if y < 3 else c["violet"]
        boxes.append(Box(f"lantern plinth {i}", x, y, 0.26,
                         0.6, 0.6, 0.52, tone, False))
        boxes.append(Box(f"lantern glow {i}", x, y, 0.66,
                         0.36, 0.36, 0.36, c["gold"], False))
    # Raised pedestal + portal frame at the north end. Walk through its gap.
    boxes.extend((
        Box("portal left", -2.6, 17, 1.9, 0.55, 1, 3.8, c["slate"]),
        Box("portal right", 2.6, 17, 1.9, 0.55, 1, 3.8, c["slate"]),
        Box("portal arch", 0, 17, 3.95, 5.75, 1.0, 0.45, c["gold"]),
        Box("portal step", 0, 17, 0.055, 3, 2.5, 0.11, c["gold"], False),
    ))
    return tuple(boxes)


BOXES = make_boxes()
SOLIDS = tuple(box for box in BOXES if box.solid)
# Explicit, very small collision set. Interior architecture is not a maze.
WALK_BLOCKERS = tuple(box for box in BOXES if box.blocks_walking)
LANDING_PLATFORMS = tuple(box for box in SOLIDS if box.top > 0.1)


def nearest_core(x: float, y: float, collected: set[str]) -> Pickup | None:
    """Used for the HUD objective arrow: give the closest missing prism."""
    remaining = [p for p in CORES if p.name not in collected]
    return min(remaining, key=lambda p: (p.x-x)**2 + (p.y-y)**2) if remaining else None
