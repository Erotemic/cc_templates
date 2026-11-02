"""Player attack mini-games. Add another Strike and give a Weapon its factory.

A strike consumes seconds and confirm presses, then exposes a score in [0, 1].
Rendering reads the same normalized cursor/targets; it does not decide damage.
"""

from dataclasses import dataclass
from .controls import Controls


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


@dataclass(frozen=True)
class StrikeView:
    title: str
    instruction: str
    cursor: float
    targets: tuple[float, ...]
    window: float
    marks: tuple[tuple[float, float], ...]


class Strike:
    """Small extension contract: update, score/done, and a presentation snapshot."""

    done = False
    score = 0.0

    def update(self, dt: float, controls: Controls):
        raise NotImplementedError

    def view(self) -> StrikeView:
        raise NotImplementedError


class TimingStrike(Strike):
    def __init__(self):
        self.elapsed = 0.0
        self.duration = 1.45
        self.done = False
        self.score = 0.0
        self.mark = None

    def update(self, dt, controls):
        if self.done:
            return
        self.elapsed += dt
        cursor = clamp(self.elapsed / self.duration)
        if controls.confirm:
            self.score = clamp(1 - abs(cursor - 0.5) / 0.35)
            self.mark = (cursor, self.score)
            self.done = True
        elif self.elapsed >= self.duration:
            self.mark = (1.0, 0.0)
            self.done = True

    def view(self):
        return StrikeView(
            "FOCUS STRIKE",
            "Z / Enter: stop the cursor near the center",
            clamp(self.elapsed / self.duration),
            (0.5,),
            0.09,
            () if self.mark is None else (self.mark,),
        )


class RhythmStrike(Strike):
    def __init__(self):
        self.elapsed = 0.0
        self.duration = 2.4
        self.targets = (0.25, 0.5, 0.75)
        self.window = 0.09
        self.hits = {}
        self.marks = []
        self.done = False
        self.score = 0.0

    def update(self, dt, controls):
        if self.done:
            return
        self.elapsed += dt
        cursor = clamp(self.elapsed / self.duration)
        if controls.confirm:
            available = [i for i in range(3) if i not in self.hits]
            if available:
                index = min(available, key=lambda i: abs(cursor - self.targets[i]))
                distance = abs(cursor - self.targets[index])
                if distance <= self.window:
                    accuracy = clamp(1 - distance / self.window)
                    self.hits[index] = accuracy
                    self.marks.append((cursor, accuracy))
        self.score = sum(self.hits.values()) / 3
        self.done = self.elapsed >= self.duration or len(self.hits) == 3

    def view(self):
        return StrikeView(
            "THREE BEAT STRIKE",
            "Z / Enter: tap once on each of the three beats",
            clamp(self.elapsed / self.duration),
            self.targets,
            self.window,
            tuple(self.marks),
        )
