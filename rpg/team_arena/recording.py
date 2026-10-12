from __future__ import annotations

"""Record decisions and student prints for deterministic graphical playback.

The *same* simulate_once() drives normal experiments and these recordings.
Student Python runs only in a timeout-limited worker, never in pygame. That
isolates accidental hangs; it is not a security boundary for untrusted code.
"""

from contextlib import redirect_stdout
from dataclasses import asdict
import random
from typing import Any

from rpg_battle.battle.battle_controller import BattleController
from rpg_battle.core.ai import choose_ai_action
from rpg_battle.core.battle_state import get_combatant
from rpg_battle.core.models import BattleAction
from rpg_battle.core.rules import resolve_action, resolve_replacement
from rpg_battle.teaching.simulate import simulate_once

from team_arena.engine import ARENA_ID, content_for_match

RECORD_VERSION = 2
PRINT_LIMIT = 3600


class LimitedOutput:
    """Capture a bounded amount of print output from one controller turn."""

    def __init__(self, limit: int = PRINT_LIMIT) -> None:
        self.parts: list[str] = []
        self.remaining = limit
        self.truncated = False

    def write(self, value: str) -> int:
        value = str(value)
        kept = value[: self.remaining]
        if kept:
            self.parts.append(kept)
        self.remaining -= len(kept)
        self.truncated |= len(value) > len(kept)
        return len(value)

    def flush(self) -> None:
        pass

    def lines(self) -> list[str]:
        lines = "".join(self.parts).splitlines()
        if self.truncated:
            lines.append("[print output truncated]")
        return lines


def rng_to_data(rng: random.Random) -> list[Any]:
    """Serialize a random generator only when a controller has consumed RNG."""
    version, integers, gaussian = rng.getstate()
    return [version, list(integers), gaussian]


def restore_rng(rng: random.Random, state: list[Any]) -> None:
    rng.setstate((int(state[0]), tuple(int(i) for i in state[1]), state[2]))


def action_from_data(data: dict[str, Any]) -> BattleAction:
    return BattleAction(
        actor_id=data["actor_id"], kind=data["kind"], move_id=data.get("move_id"),
        target_ids=tuple(data.get("target_ids") or ()),
        switch_in_id=data.get("switch_in_id"), item_id=data.get("item_id"),
    )


def format_action(state, action: BattleAction) -> str:
    if action.kind == "defend":
        return "Defend"
    if action.kind == "switch":
        return "Switch"
    if action.kind == "item":
        return "Item"
    name = ("Attack" if action.kind == "attack" else
            state.content.moves[action.move_id].name if action.move_id else action.kind.title())
    targets = [get_combatant(state, i).spec.name for i in action.target_ids]
    if targets:
        name += " -> " + ", ".join(targets)
    return name


def _source_name(name: str) -> str:
    from team_arena.cli import BUILTIN, ROOT, source_for
    if name == BUILTIN:
        return "src/rpg_battle/core/ai.py (engine heuristic)"
    file = source_for(name)
    try:
        return str(file.relative_to(ROOT))
    except ValueError:
        # Tests and instructors can redirect student files to a separate folder.
        return str(file)


def record_match(left_name: str, right_name: str, *, seed: int = 0,
                 max_steps: int = 300) -> dict[str, Any]:
    """Record legal moves and prints using the canonical simulation loop."""
    from team_arena.cli import controller_for

    content = content_for_match(left_name, controller_for(left_name),
                                right_name, controller_for(right_name))
    record: dict[str, Any] = {
        "version": RECORD_VERSION, "left": left_name, "right": right_name,
        "sources": [_source_name(left_name), _source_name(right_name)],
        "seed": seed, "steps": [],
    }

    def choose_and_record(controller: BattleController, actor_id: str) -> BattleAction:
        actor = get_combatant(controller.state, actor_id)
        before = controller.rng.getstate()
        output = LimitedOutput()
        with redirect_stdout(output):
            action = choose_ai_action(controller.state, actor_id, controller.rng)
        step = {
            "type": "action", "actor_id": actor_id, "actor_name": actor.spec.name,
            "team": actor.team_index, "round": controller.state.round_number,
            "action": asdict(action), "description": format_action(controller.state, action),
            "prints": output.lines(),
        }
        # The spectator advances the same seed-local RNG between turns. Save
        # a checkpoint ONLY if the choice itself consumed RNG (engine AI).
        # This removes ~6 KB per decision for deterministic student prefabs.
        if controller.rng.getstate() != before:
            step["rng_state"] = rng_to_data(controller.rng)
        record["steps"].append(step)
        return action

    def record_replacement(controller: BattleController, team: int, replacement: str) -> None:
        record["steps"].append({
            "type": "replacement", "team": team, "replacement_id": replacement,
        })

    saved_random = random.getstate()
    try:
        random.seed(seed)
        result = simulate_once(
            content, ARENA_ID, seed=seed, max_steps=max_steps,
            action_choice=choose_and_record, on_replacement=record_replacement,
        )
    finally:
        random.setstate(saved_random)

    if result.winner is None:
        raise RuntimeError(
            f"Battle did not finish in {max_steps} steps. "
            "Try an attacking move, or increase --max-steps."
        )
    record["winner"] = result.winner
    record["rounds"] = result.rounds
    record["remaining_hp"] = list(result.remaining_hp)
    return record


def apply_replay_step(controller: BattleController, step: dict[str, Any]) -> list[dict]:
    """Apply a prerecorded choice without importing any student module."""
    if step["type"] == "replacement":
        request = controller.state.pending_replacements[0]
        if request.team_index != step["team"]:
            raise ValueError("Replay replacement team diverged")
        return resolve_replacement(controller.state, request.team_index, step["replacement_id"])
    if step["type"] != "action":
        raise ValueError(f"Unknown replay step type {step['type']!r}")
    if controller.current_actor_id != step["actor_id"]:
        raise ValueError(
            f"Replay diverged: expected {step['actor_id']}, "
            f"now acting {controller.current_actor_id}"
        )
    action = action_from_data(step["action"])
    if "rng_state" in step:
        restore_rng(controller.rng, step["rng_state"])
    events = resolve_action(controller.state, action, controller.rng)
    controller.current_actor_id = None
    return events


def verify_replay(record: dict[str, Any]) -> tuple[int | None, int, tuple[int, int]]:
    """Headless roundtrip verification without running student code."""
    if record["version"] != RECORD_VERSION:
        raise ValueError("Unknown arena recording version")
    content = content_for_match(record["left"], None, record["right"], None)
    controller = BattleController(
        encounter=content.encounters[ARENA_ID], seed=record["seed"], content=content,
    )
    index = 0
    max_ticks = max(20, 5 * len(record["steps"]) + 20)
    for _ in range(max_ticks):
        if controller.state.winner is not None:
            break
        if controller.state.pending_replacements or controller.current_actor_id:
            if index >= len(record["steps"]):
                raise ValueError("Recording ran out of decisions")
            apply_replay_step(controller, record["steps"][index])
            index += 1
        else:
            controller.advance_to_next_turn()
    if index != len(record["steps"]):
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
