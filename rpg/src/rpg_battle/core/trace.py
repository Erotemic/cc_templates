from __future__ import annotations

"""Optional observation port for combat rules.

The core only knows the two methods of a trace sink. Student-facing lab
infrastructure may provide a sink, but core must not import teaching modules.
"""

from typing import Protocol


class TraceSink(Protocol):
    def emit(self, message: str) -> None: ...

    def record(self, kind: str, *, message: str | None = None, **data: object) -> None: ...


def emit_trace(state: object, message: str) -> None:
    trace = getattr(state, "teaching_trace", None)
    if trace is not None:
        trace.emit(message)


def record_trace(state: object, kind: str, *, message: str | None = None,
                 **data: object) -> None:
    trace = getattr(state, "teaching_trace", None)
    if trace is not None:
        trace.record(kind, message=message, **data)
