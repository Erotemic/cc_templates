from __future__ import annotations

"""Record real battle-engine decisions for safe, deterministic visual playback.

Only the subprocess recorder imports and executes student controller functions.
The pygame viewer reads the actions and captured prints without executing student
code.  This is fault isolation for classroom mistakes, not a security sandbox.
"""

from contextlib import redirect_stdout
from dataclasses import asdict
import random
from typing import Any

from rpg_battle.battle.battle_controller import BattleController
from rpg_battle.core.ai import choose_ai_action, choose_ai_replacement
from rpg_battle.core.battle_state import get_combatant
from rpg_battle.core.models import BattleAction
from rpg_battle.core.rules import resolve_action, resolve_replacement

from team_arena.engine import ARENA_ID, content_for_match

RECORD_VERSION = 1
PRINT_LIMIT = 3600


class LimitedOutput:
    """Capture student print() calls without allowing unlimited output memory."""

    def __init__(self, limit: int = PRINT_LIMIT) -> None:
        self.limit = limit
        self.parts: list[str] = []
        self.remaining = limit
        self.truncated = False

    def write(self, value: str) -> int:
        value = str(value)
        size = len(value)
        kept = value[: self.remaining]
        if kept:
            self.parts.append(kept)
            self.remaining -= len(kept)
        if size > len(kept):
            self.truncated = True
        return size

    def flush(self) -> None:
        pass

    def lines(self) -> list[str]:
        content = "".join(self.parts)
        lines = content.splitlines()
        if self.truncated:
            lines.append("[print output truncated]")
        return lines


def rng_to_data(rng: random.Random) -> list[Any]:
    """Use JSON-compatible RNG state so the replay draws the SAME outcomes."""
    version, integers, gaussian = rng.getstate()
    return [version, list(integers), gaussian]


def restore_rng(rng: random.Random, state: list[Any]) -> None:
    rng.setstate((int(state[0]), tuple(int(i) for i in state[1]), state[2]))


def action_from_data(data: dict[str, Any]) -> BattleAction:
    return BattleAction(
        actor_id=data["actor_id"],
        kind=data["kind"],
        move_id=data.get("move_id"),
        target_ids=tuple(data.get("target_ids") or ()),
        switch_in_id=data.get("switch_in_id"),
        item_id=data.get("item_id"),
    )


def format_action(state, action: BattleAction) -> str:
    if action.kind == "defend":
        return "Defend"
    if action.kind == "switch":
        return "Switch"
    if action.kind == "item":
        return "Item"
    name = state.content.moves[action.move_id].name if action.move_id else action.kind.title()
    targets = [get_combatant(state, i).spec.name for i in action.target_ids]
    if targets:
        name += " -> " + ", ".join(targets)
    return name


def _source_name(name: str) -> str:
    from team_arena.cli import BUILTIN, ROOT, source_for
    if name == BUILTIN:
        return "src/rpg_battle/core/ai.py (engine heuristic)"
    return str(source_for(name).relative_to(ROOT))


def record_match(left_name: str, right_name: str, *, seed: int = 0,
                 max_steps: int = 300) -> dict[str, Any]:
    """Play one match to completion while recording exact legal actions/prints.

    Do not call this in the pygame process: student code can be slow or contain
    accidental loops. `arena.py watch` runs it in a subprocess with a timeout.
    """
    from team_arena.cli import controller_for

    if max_steps <= 0:
        raise ValueError("max_steps must be positive")
    content = content_for_match(left_name, controller_for(left_name),
                                right_name, controller_for(right_name))
    encounter = content.encounters[ARENA_ID]
    controller = BattleController(encounter=encounter, seed=seed, content=content)
    record = {
        "version": RECORD_VERSION,
        "left": left_name,
        "right": right_name,
        "sources": [_source_name(left_name), _source_name(right_name)],
        "seed": seed,
        "steps": [],
    }
    saved_random = random.getstate()
    try:
        random.seed(seed)
        for _ in range(max_steps):
            if controller.state.winner is not None:
                break
            if controller.state.pending_replacements:
                request = controller.state.pending_replacements[0]
                replacement = choose_ai_replacement(controller.state, request.team_index)
                if replacement is None:
                    raise RuntimeError("No legal replacement in recorded arena match")
                record["steps"].append({
                    "type": "replacement", "team": request.team_index,
                    "replacement_id": replacement,
                })
                resolve_replacement(controller.state, request.team_index, replacement)
                continue
            controller.advance_to_next_turn()
            actor_id = controller.current_actor_id
            if actor_id is None:
                continue
            actor = get_combatant(controller.state, actor_id)
            output = LimitedOutput()
            with redirect_stdout(output):
                action = choose_ai_action(controller.state, actor_id, controller.rng)
            # Record after any random decisions and before any combat dice rolls.
            record["steps"].append({
                "type": "action",
                "actor_id": actor_id,
                "actor_name": actor.spec.name,
                "team": actor.team_index,
                "round": controller.state.round_number,
                "action": asdict(action),
                "description": format_action(controller.state, action),
                "rng_state": rng_to_data(controller.rng),
                "prints": output.lines(),
            })
            resolve_action(controller.state, action, controller.rng)
            controller.current_actor_id = None
        else:
            if controller.state.winner is None:
                raise RuntimeError(
                    f"Battle did not finish within {max_steps} simulation steps; "
                    "increase --max-steps or change the controllers."
                )
    finally:
        random.setstate(saved_random)
    record["winner"] = controller.state.winner
    record["rounds"] = controller.state.round_number
    record["remaining_hp"] = [
        sum(c.current_hp for c in controller.state.combatants.values()
            if c.team_index == index)
        for index in (0, 1)
    ]
    return record


def apply_replay_step(controller: BattleController, record: dict[str, Any]) -> list[dict]:
    """Apply one prerecorded choice to a waiting BattleController (no student code)."""
    if record["type"] == "replacement":
        request = controller.state.pending_replacements[0]
        if request.team_index != record["team"]:
            raise ValueError("Replay replacement team diverged")
        return resolve_replacement(
            controller.state, request.team_index, record["replacement_id"]
        )
    if record["type"] != "action":
        raise ValueError(f"Unknown replay step type {record['type']!r}")
    if controller.current_actor_id != record["actor_id"]:
        raise ValueError(
            f"Replay diverged: expected {record['actor_id']}, "
            f"now acting {controller.current_actor_id}"
        )
    action = action_from_data(record["action"])
    restore_rng(controller.rng, record["rng_state"])
    events = resolve_action(controller.state, action, controller.rng)
    controller.current_actor_id = None
    return events


def verify_replay(record: dict[str, Any]) -> tuple[int | None, int, tuple[int, int]]:
    """Pure headless verification that recorded actions replay without AI code."""
    if record["version"] != RECORD_VERSION:
        raise ValueError("Unknown arena recording version")
    content = content_for_match(record["left"], None, record["right"], None)
    controller = BattleController(
        encounter=content.encounters[ARENA_ID], seed=record["seed"], content=content
    )
    step_index = 0
    max_ticks = max(20, 5 * len(record["steps"]) + 20)
    for _ in range(max_ticks):
        if controller.state.winner is not None:
            break
        if controller.state.pending_replacements or controller.current_actor_id:
            if step_index >= len(record["steps"]):
                raise ValueError("Recording ran out of decisions")
            apply_replay_step(controller, record["steps"][step_index])
            step_index += 1
        else:
            controller.advance_to_next_turn()
    if step_index != len(record["steps"]):
        raise ValueError("Recording has unused decisions")
    hp = tuple(
        sum(c.current_hp for c in controller.state.combatants.values()
            if c.team_index == i) for i in (0, 1)
    )
    actual = (controller.state.winner, controller.state.round_number, hp)
    expected = (record["winner"], record["rounds"], tuple(record["remaining_hp"]))
    if actual != expected:
        raise ValueError(f"Replay does not match recorded battle: {actual} != {expected}")
    return actual
