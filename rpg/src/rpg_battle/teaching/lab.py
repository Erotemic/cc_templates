from __future__ import annotations

"""Deterministic command-line laboratory for inspecting one move."""

import argparse
import inspect
import random

from loguru import logger
from dataclasses import dataclass

from rpg_battle.catalog import ContentValidationError, GameContent
from rpg_battle.core.actions import skill_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.models import EncounterSpec, StatusState, TeamSpec
from rpg_battle.core.rules import resolve_action
from rpg_battle.core.targeting import get_valid_target_groups
from rpg_battle.teaching.trace import TeachingTrace


@dataclass(frozen=True)
class MoveLabResult:
    """Useful structured facts from one deterministic move experiment."""

    seed: int
    actor_before: int
    actor_after: int
    target_names: dict[str, str]
    targets_before: dict[str, int]
    targets_after: dict[str, int]
    events: list[dict]
    trace_lines: list[str]


def _default_targets(content: GameContent, move_id: str) -> list[str]:
    move = content.moves[move_id]
    preferred = [char_id for char_id in ("spirit", "guardian") if char_id in content.characters]
    if not preferred:
        preferred = [char_id for char_id in content.characters if char_id != "workshop_hero"]
    if move.target_mode in {"all_enemies", "all_allies"}:
        return preferred[:2] or list(content.characters)[:2]
    return preferred[:1] or list(content.characters)[:1]


def _apply_status_specs(state, target_ids: list[str], specs: list[str]) -> None:
    """Apply CLI status specs such as ``burn`` or ``2:burn`` before the move."""

    for spec in specs:
        if ":" in spec:
            index_text, status_name = spec.split(":", 1)
            try:
                index = int(index_text) - 1
            except ValueError as exc:
                raise ValueError(
                    f"target status {spec!r} must look like 'burn' or '2:burn'"
                ) from exc
            if not 0 <= index < len(target_ids):
                raise ValueError(
                    f"target status {spec!r} names target {index + 1}, but only "
                    f"{len(target_ids)} target(s) are active"
                )
            selected = [target_ids[index]]
        else:
            status_name = spec
            selected = target_ids
        for target_id in selected:
            state.combatants[target_id].statuses[status_name] = StatusState(status_name, 3)


def run_move_lab(
    content: GameContent,
    move_id: str,
    *,
    user_char_id: str,
    target_char_ids: list[str],
    user_hp: int | None = None,
    target_hp: int | None = None,
    target_statuses: list[str] | None = None,
    round_number: int = 1,
    seed: int = 0,
) -> MoveLabResult:
    """Run one move through the real rules engine with deterministic inputs."""

    if move_id not in content.moves:
        raise KeyError(f"unknown move {move_id!r}")
    if user_char_id not in content.characters:
        raise KeyError(f"unknown character {user_char_id!r}")
    unknown_targets = [char_id for char_id in target_char_ids if char_id not in content.characters]
    if unknown_targets:
        raise KeyError(f"unknown target character(s): {', '.join(unknown_targets)}")

    move = content.moves[move_id]
    player = TeamSpec(
        name="Move Lab User",
        members=(user_char_id,),
        starting_active=(user_char_id,),
    )
    enemy = TeamSpec(
        name="Move Lab Targets",
        members=tuple(target_char_ids),
        controller_type="ai",
        starting_active=tuple(target_char_ids),
    )
    encounter = EncounterSpec(
        encounter_id="move_lab",
        title="Move Lab",
        player_team=player,
        enemy_team=enemy,
        active_limits=(1, len(target_char_ids)),
        music_track_id=None,
    )
    trace = TeachingTrace(echo=False)
    state = new_battle(encounter, content=content, teaching_trace=trace)
    state.round_number = round_number
    actor_id = state.teams[0].active_ids[0]
    target_ids = list(state.teams[1].active_ids)
    actor = state.combatants[actor_id]
    if user_hp is not None:
        actor.current_hp = max(0, min(user_hp, actor.spec.max_hp))
    if target_hp is not None:
        for target_id in target_ids:
            target = state.combatants[target_id]
            target.current_hp = max(0, min(target_hp, target.spec.max_hp))
    _apply_status_specs(state, target_ids, target_statuses or [])

    groups = get_valid_target_groups(state, actor_id, move.target_mode)
    selected_targets = tuple(groups[0]) if groups else ()
    actor_before = actor.current_hp
    targets_before = {target_id: state.combatants[target_id].current_hp for target_id in target_ids}
    events = resolve_action(
        state,
        skill_action(actor_id, move_id, target_ids=selected_targets),
        random.Random(seed),
    )
    return MoveLabResult(
        seed=seed,
        actor_before=actor_before,
        actor_after=actor.current_hp,
        target_names={target_id: state.combatants[target_id].spec.name for target_id in target_ids},
        targets_before=targets_before,
        targets_after={
            target_id: state.combatants[target_id].current_hp for target_id in target_ids
        },
        events=events,
        trace_lines=list(trace.lines),
    )


def _print_script(move) -> None:
    if move.script is None:
        print("\nThis is a declarative move; it does not have a custom Python action function.")
        return
    print("\nPython function being called:\n")
    try:
        source = inspect.getsource(move.script)
    except (OSError, TypeError):
        source = f"<source unavailable for {move.script!r}>"
    for line in source.rstrip().splitlines():
        print(f"    {line}")


def _print_result(content: GameContent, move_id: str, result: MoveLabResult) -> None:
    move = content.moves[move_id]
    print(f"\n{move.name} experiment")
    print("=" * (len(move.name) + 11))
    print(f"seed: {result.seed}")
    print(f"user HP: {result.actor_before} -> {result.actor_after}")
    for target_id, before in result.targets_before.items():
        target_name = result.target_names[target_id]
        print(f"target {target_name} HP: {before} -> {result.targets_after[target_id]}")

    if result.trace_lines:
        print("\nExecution trace:")
        for line in result.trace_lines:
            print(f"  {line}")

    interesting = [
        event
        for event in result.events
        if event.get("type") in {"move", "damage", "heal", "status", "stat", "miss", "ko"}
    ]
    print("\nEngine events:")
    for event in interesting:
        text = event.get("text") or repr(event)
        print(f"  [{event.get('type')}] {text}")


def build_parser(content: GameContent) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one RPG move deterministically and inspect what the engine does."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List moves available to the lab")
    list_parser.add_argument(
        "--scripted",
        action="store_true",
        help="Show only moves with Python action functions",
    )

    move_parser = subparsers.add_parser("move", help="Run one move experiment")
    move_parser.add_argument(
        "move_id",
        nargs="?",
        default="workshop_power_strike",
        choices=sorted(content.moves),
    )
    move_parser.add_argument(
        "--user",
        default=(
            "workshop_hero"
            if "workshop_hero" in content.characters
            else next(iter(content.characters))
        ),
        choices=sorted(content.characters),
        help="Character whose stats are used by the move",
    )
    move_parser.add_argument(
        "--target",
        action="append",
        choices=sorted(content.characters),
        help="Target character; repeat for multi-target experiments",
    )
    move_parser.add_argument("--user-hp", type=int, help="Set the user's starting HP")
    move_parser.add_argument("--target-hp", type=int, help="Set every target's starting HP")
    move_parser.add_argument(
        "--target-status",
        action="append",
        default=[],
        metavar="[N:]STATUS",
        help="Apply a status before the move, e.g. burn or 2:burn",
    )
    move_parser.add_argument("--round", type=int, default=1, dest="round_number")
    move_parser.add_argument("--seed", type=int, default=0)
    return parser


def main(content: GameContent | None = None) -> None:
    logger.remove()
    if content is None:
        try:
            from student_game import CONTENT
        except ContentValidationError as exc:
            print(exc)
            raise SystemExit(2) from None
        content = CONTENT
    parser = build_parser(content)
    args = parser.parse_args()
    if args.command == "list":
        for move_id, move in content.moves.items():
            if args.scripted and move.script is None:
                continue
            suffix = " [Python function]" if move.script is not None else ""
            print(f"{move_id:28} {move.name}{suffix}")
        return

    move = content.moves[args.move_id]
    _print_script(move)
    target_char_ids = args.target or _default_targets(content, args.move_id)
    try:
        result = run_move_lab(
            content,
            args.move_id,
            user_char_id=args.user,
            target_char_ids=target_char_ids,
            user_hp=args.user_hp,
            target_hp=args.target_hp,
            target_statuses=args.target_status,
            round_number=args.round_number,
            seed=args.seed,
        )
    except (KeyError, ValueError) as exc:
        parser.error(str(exc))
    _print_result(content, args.move_id, result)


if __name__ == "__main__":
    main()
