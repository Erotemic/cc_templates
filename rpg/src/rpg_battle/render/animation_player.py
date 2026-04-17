from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TimedPulse:
    timer: float
    duration: float

    def progress(self) -> float:
        if self.duration <= 0:
            return 1.0
        return max(0.0, 1.0 - self.timer / self.duration)
