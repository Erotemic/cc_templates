"""Player attack mini-games. Add another Strike and give a Weapon its factory.

A strike consumes seconds and confirm presses, then exposes a score in [0, 1].
Rendering reads the same normalized cursor/targets; it does not decide damage.
"""

from dataclasses import dataclass
from .controls import Controls


def clamp(value, low=0.0, high=1.0):
    """Return value restricted to the inclusive low..high range; default to 0..1."""
    return max(low, min(high, value))


@dataclass(frozen=True)
class StrikeView:
    """Describe a timing mini-game for the renderer without exposing its rules.

    cursor and targets are normalized positions, where 0 is the bar's left edge
    and 1 its right edge. window is a target half-width in those same units;
    marks stores (cursor_position, accuracy) pairs from accepted presses.
    """

    title: str
    instruction: str
    cursor: float
    targets: tuple[float, ...]
    window: float
    marks: tuple[tuple[float, float], ...]


class Strike:
    """Define a player timing mini-game without applying battle damage.

    Subclasses update done and score (0..1), and return a StrikeView for drawing.
    Battle owns damage calculation and uses a fresh strike from Weapon.factory.
    """

    done = False
    score = 0.0

    def update(self, dt: float, controls: Controls):
        """Consume dt seconds and this frame's Controls; update done and score.

        Subclasses must finish eventually even without input. This base method
        raises NotImplementedError; implement it before registering a new Weapon.
        """
        raise NotImplementedError

    def view(self) -> StrikeView:
        """Return a StrikeView snapshot without changing the mini-game.

        Subclasses implement this for View.draw_strike. Calling it repeatedly
        must not advance time, award points, or consume random numbers.
        """
        raise NotImplementedError


class TimingStrike(Strike):
    """Score one confirm press by its distance from the moving bar's center."""

    def __init__(self):
        """Start a fresh 1.45-second sweep with no input mark and zero score."""
        self.elapsed = 0.0
        self.duration = 1.45
        self.done = False
        self.score = 0.0
        self.mark = None

    def update(self, dt, controls):
        """Move the cursor with dt seconds; finish on confirm or timeout.

        A press nearer the center earns a higher 0..1 score. No press earns
        zero, and calls after completion leave the result unchanged.
        """
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
        """Return the current normalized cursor, center target, and optional press mark."""
        return StrikeView(
            "FOCUS STRIKE",
            "Z / Enter: stop the cursor near the center",
            clamp(self.elapsed / self.duration),
            (0.5,),
            0.09,
            () if self.mark is None else (self.mark,),
        )


class RhythmStrike(Strike):
    """Average accuracy across three beats, accepting each target at most once."""

    def __init__(self):
        """Start a 2.4-second sweep with three targets and no recorded hits."""
        self.elapsed = 0.0
        self.duration = 2.4
        self.targets = (0.25, 0.5, 0.75)
        self.window = 0.09
        self.hits = {}
        self.marks = []
        self.done = False
        self.score = 0.0

    def update(self, dt, controls):
        """Advance by dt seconds and try to match confirm to the nearest unused beat.

        Accept hits only inside that beat's timing window. Average their scores
        over all three beats; finish when time expires or all beats are hit.
        """
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
        """Return a drawing snapshot containing the three targets and accepted hit marks."""
        return StrikeView(
            "THREE BEAT STRIKE",
            "Z / Enter: tap once on each of the three beats",
            clamp(self.elapsed / self.duration),
            self.targets,
            self.window,
            tuple(self.marks),
        )
