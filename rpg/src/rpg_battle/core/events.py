from __future__ import annotations

from typing import Any


def make_event(event_type: str, **payload: Any) -> dict[str, Any]:
    payload["type"] = event_type
    return payload
