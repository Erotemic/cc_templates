"""Four worked defense patterns. Each instance owns its own spawn clock."""

from .arena import DefensePattern, Mode, Vec


class FallingPages(DefensePattern):
    name = "Falling pages"
    hint = "Move freely. Find the gaps between the falling pages."
    duration = 5.2

    def __init__(self, gentle=False):
        self.cooldown = 0.25
        self.speed = 90 if gentle else 115

    def update(self, arena, dt):
        self.cooldown -= dt
        while self.cooldown <= 0 and arena.elapsed < 3.4:
            gap = arena.rng.randrange(6)
            for lane in range(7):
                if lane not in (gap, gap + 1):
                    arena.spawn(
                        (lane + 0.5) * arena.width / 7,
                        5,
                        0,
                        self.speed,
                        radius=7,
                        color=(172, 220, 255),
                        warmup=0.35,
                    )
            self.cooldown += 0.65


class ClockworkHops(DefensePattern):
    name = "Clockwork hops"
    hint = "Left / Right: move. Tap Z / Space to jump over the low gears."
    mode = Mode.GRAVITY
    duration = 5.8

    def __init__(self):
        self.cooldown = 0.15
        self.wave = 0

    def update(self, arena, dt):
        self.cooldown -= dt
        while self.cooldown <= 0 and arena.elapsed < 3.6:
            from_left = self.wave % 2 == 0
            arena.spawn(
                8 if from_left else arena.width - 8,
                arena.height - 10,
                215 if from_left else -215,
                0,
                radius=8,
                color=(255, 194, 115),
                warmup=0.5,
            )
            self.wave += 1
            self.cooldown += 1.05


class ShieldWaltz(DefensePattern):
    name = "Shield waltz"
    hint = "Hold an arrow / WASD direction to face your shield toward a spark."
    mode = Mode.SHIELD
    duration = 5.6

    def __init__(self):
        self.cooldown = 0.2
        self.wave = 0

    def update(self, arena, dt):
        self.cooldown -= dt
        while self.cooldown <= 0 and arena.elapsed < 3.7:
            center = Vec(arena.width / 2, arena.height / 2)
            entrances = (
                Vec(center.x, 8),
                Vec(arena.width - 8, center.y),
                Vec(center.x, arena.height - 8),
                Vec(8, center.y),
            )
            start = entrances[self.wave % 4]
            velocity = (center - start) / 0.95
            arena.spawn(
                start.x,
                start.y,
                velocity.x,
                velocity.y,
                radius=7,
                color=(199, 169, 255),
                warmup=0.55,
            )
            self.wave += 1
            self.cooldown += 0.78


class SafeLanes(DefensePattern):
    name = "Between the lines"
    hint = "Amber lines are warnings. Step into a gap before they light up."
    duration = 5.6

    def __init__(self):
        self.cooldown = 0.2

    def update(self, arena, dt):
        self.cooldown -= dt
        while self.cooldown <= 0 and arena.elapsed < 4.1:
            lane = min(5, int(arena.soul.position.x / 100))
            # Put a reachable opening near the current player, not across the
            # entire arena. Randomness should still give the player a chance.
            gap = arena.rng.randint(max(0, lane - 2), min(4, lane + 1))
            for index in range(6):
                if index not in (gap, gap + 1):
                    arena.beam(index * 100, 0, 100, arena.height, warmup=0.85, duration=0.25)
            self.cooldown += 1.25
