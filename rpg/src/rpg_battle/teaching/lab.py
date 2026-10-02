from __future__ import annotations

"""Deterministic command-line laboratory for explaining real RPG execution."""

import argparse
from dataclasses import dataclass
import inspect
import random
from typing import Mapping

from loguru import logger

from rpg_battle.catalog import ContentValidationError, GameContent
from rpg_battle.core.actions import skill_action
from rpg_battle.core.ai import choose_ai_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.models import BattleState, EncounterSpec, StatusState, TeamSpec
from rpg_battle.core.scripting import StudentCodeError
from rpg_battle.core.rules import resolve_action
from rpg_battle.core.targeting import get_valid_target_groups
from rpg_battle.teaching.scenarios import TeachingScenario
from rpg_battle.teaching.trace import TeachingTrace, TraceRecord


@dataclass(frozen=True)
class MoveLabResult:
    """Structured facts from one deterministic move experiment."""

    seed: int
    actor_name: str
    actor_before: int
    actor_after: int
    actor_max_hp: int
    actor_attack: int
    actor_base_attack: int
    actor_magic: int
    actor_base_magic: int
    target_names: dict[str, str]
    target_statuses: dict[str, tuple[str, ...]]
    targets_before: dict[str, int]
    targets_after: dict[str, int]
    events: list[dict]
    trace_lines: list[str]
    trace_records: list[TraceRecord]


def _default_targets(content: GameContent, move_id: str, user_char_id: str) -> list[str]:
    move = content.moves[move_id]
    preferred = [
        char_id
        for char_id in ("spirit", "guardian", "ranger", "druid")
        if char_id in content.characters and char_id != user_char_id
    ]
    if not preferred:
        preferred = [char_id for char_id in content.characters if char_id != user_char_id]
    if move.target_mode in {"self", "none"}:
        return []
    count = 2 if move.target_mode == "all_enemies" else 1
    return preferred[:count]


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


def _combatant_id_for_char(state, team_index: int, char_id: str) -> str:
    for combatant_id in state.teams[team_index].active_ids:
        if state.combatants[combatant_id].spec.char_id == char_id:
            return combatant_id
    raise ValueError(f"character {char_id!r} is not active in the move lab")


def _build_move_lab_state(
    content: GameContent,
    move_id: str,
    user_char_id: str,
    target_char_ids: list[str],
    trace: TeachingTrace,
):
    move = content.moves[move_id]
    if len(set(target_char_ids)) != len(target_char_ids):
        raise ValueError("repeat targets are not supported in the move lab")
    if user_char_id in target_char_ids and move.target_mode not in {"self", "single_ally", "all_allies"}:
        raise ValueError("choose a different target character from the move user")

    dummy_id = next(
        (char_id for char_id in content.characters if char_id not in {user_char_id, *target_char_ids}),
        user_char_id,
    )

    if move.target_mode in {"single_ally", "all_allies"}:
        player_members = (user_char_id, *(cid for cid in target_char_ids if cid != user_char_id))
        player = TeamSpec(
            name="Move Lab Allies",
            members=player_members,
            starting_active=player_members,
        )
        enemy = TeamSpec(
            name="Move Lab Dummy",
            members=(dummy_id,),
            controller_type="ai",
            starting_active=(dummy_id,),
        )
        encounter = EncounterSpec(
            encounter_id="move_lab",
            title="Move Lab",
            player_team=player,
            enemy_team=enemy,
            active_limits=(len(player_members), 1),
            music_track_id=None,
        )
        state = new_battle(encounter, content=content, teaching_trace=trace)
        actor_id = _combatant_id_for_char(state, 0, user_char_id)
        requested_target_ids = [
            _combatant_id_for_char(state, 0, char_id) for char_id in target_char_ids
        ]
    else:
        player = TeamSpec(
            name="Move Lab User",
            members=(user_char_id,),
            starting_active=(user_char_id,),
        )
        enemy_members = tuple(target_char_ids) or (dummy_id,)
        enemy = TeamSpec(
            name="Move Lab Targets",
            members=enemy_members,
            controller_type="ai",
            starting_active=enemy_members,
        )
        encounter = EncounterSpec(
            encounter_id="move_lab",
            title="Move Lab",
            player_team=player,
            enemy_team=enemy,
            active_limits=(1, len(enemy_members)),
            music_track_id=None,
        )
        state = new_battle(encounter, content=content, teaching_trace=trace)
        actor_id = state.teams[0].active_ids[0]
        requested_target_ids = [
            _combatant_id_for_char(state, 1, char_id) for char_id in target_char_ids
        ]

    if move.target_mode == "self":
        selected_targets = (actor_id,)
        requested_target_ids = [actor_id]
    elif move.target_mode == "none":
        selected_targets = ()
        requested_target_ids = []
    elif move.target_mode == "all_allies":
        selected_targets = tuple(state.teams[0].active_ids)
        requested_target_ids = list(selected_targets)
    elif move.target_mode == "all_enemies":
        selected_targets = tuple(requested_target_ids)
    elif move.target_mode in {"single_ally", "single_enemy"}:
        if len(requested_target_ids) != 1:
            raise ValueError(
                f"{move.name} requires exactly one target; received {len(requested_target_ids)}"
            )
        selected_targets = (requested_target_ids[0],)
    else:
        selected_targets = tuple(requested_target_ids)

    return state, actor_id, requested_target_ids, selected_targets


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

    trace = TeachingTrace(echo=False)
    state, actor_id, requested_target_ids, selected_targets = _build_move_lab_state(
        content,
        move_id,
        user_char_id,
        target_char_ids,
        trace,
    )
    state.round_number = round_number
    actor = state.combatants[actor_id]
    if user_hp is not None:
        actor.current_hp = max(1, min(user_hp, actor.spec.max_hp))
    if target_hp is not None:
        for target_id in requested_target_ids:
            target = state.combatants[target_id]
            target.current_hp = max(1, min(target_hp, target.spec.max_hp))
    _apply_status_specs(state, requested_target_ids, target_statuses or [])

    return _resolve_move_lab(state, move_id, actor_id, requested_target_ids, selected_targets, seed)


def run_move_scenario(content: GameContent, scenario: TeachingScenario) -> MoveLabResult:
    """Inspect a move using exactly the same encounter/setup used for play."""

    problems = scenario.validate(content)
    if problems:
        raise ValueError(f"scenario {scenario.scenario_id!r}: " + "; ".join(problems))
    if scenario.move_id is None or scenario.user_char_id is None:
        raise ValueError(f"scenario {scenario.scenario_id!r} has no move experiment")
    trace = TeachingTrace(echo=False)
    state = new_battle(
        content.encounters[scenario.encounter_id], content=content, teaching_trace=trace
    )
    scenario.apply_to_state(state)
    actor_id = _combatant_id_for_char(state, 0, scenario.user_char_id)
    move = content.moves[scenario.move_id]
    groups = get_valid_target_groups(state, actor_id, move.target_mode)
    selected_targets = next(
        (tuple(group) for group in groups
         if tuple(state.combatants[cid].spec.char_id for cid in group) == scenario.target_char_ids),
        None,
    )
    if not scenario.target_char_ids and len(groups) == 1:
        selected_targets = tuple(groups[0])
    if selected_targets is None:
        raise ValueError(f"scenario {scenario.scenario_id!r} selects illegal targets for {move.name}")
    return _resolve_move_lab(
        state, scenario.move_id, actor_id, list(selected_targets), selected_targets, scenario.seed
    )


def _resolve_move_lab(
    state: BattleState,
    move_id: str,
    actor_id: str,
    requested_target_ids: list[str],
    selected_targets: tuple[str, ...],
    seed: int,
) -> MoveLabResult:
    actor = state.combatants[actor_id]
    trace = state.teaching_trace

    from rpg_battle.core.effects import effective_stat

    actor_before = actor.current_hp
    actor_input_attack = effective_stat(actor, "attack")
    actor_input_magic = effective_stat(actor, "magic")
    actor_input_base_attack = actor.spec.attack
    actor_input_base_magic = actor.spec.magic
    targets_before = {
        target_id: state.combatants[target_id].current_hp for target_id in requested_target_ids
    }
    target_status_snapshot = {
        target_id: tuple(sorted(state.combatants[target_id].statuses))
        for target_id in requested_target_ids
    }
    events = resolve_action(
        state,
        skill_action(actor_id, move_id, target_ids=selected_targets),
        random.Random(seed),
    )
    return MoveLabResult(
        seed=seed,
        actor_name=actor.spec.name,
        actor_before=actor_before,
        actor_after=actor.current_hp,
        actor_max_hp=actor.spec.max_hp,
        actor_attack=actor_input_attack,
        actor_base_attack=actor_input_base_attack,
        actor_magic=actor_input_magic,
        actor_base_magic=actor_input_base_magic,
        target_names={
            target_id: state.combatants[target_id].spec.name for target_id in requested_target_ids
        },
        target_statuses=target_status_snapshot,
        targets_before=targets_before,
        targets_after={
            target_id: state.combatants[target_id].current_hp for target_id in requested_target_ids
        },
        events=events,
        trace_lines=list(trace.lines) if trace else [],
        trace_records=list(trace.records) if trace else [],
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


def _records(result: MoveLabResult, kind: str) -> list[TraceRecord]:
    return [record for record in result.trace_records if record.kind == kind]


def _print_result(content: GameContent, move_id: str, result: MoveLabResult) -> None:
    move = content.moves[move_id]
    print(f"\n{move.name} experiment")
    print("=" * (len(move.name) + 11))
    print(f"seed: {result.seed}")

    print("\n1. Input")
    ratio = result.actor_before / result.actor_max_hp
    print(
        f"   {result.actor_name}: HP {result.actor_before}/{result.actor_max_hp} "
        f"-> ratio {ratio:.3f}"
    )
    print(
        f"   effective attack={result.actor_attack} (base {result.actor_base_attack}); "
        f"effective magic={result.actor_magic} (base {result.actor_base_magic})"
    )
    for target_id, before in result.targets_before.items():
        statuses = result.target_statuses[target_id]
        status_text = ", ".join(statuses) if statuses else "none"
        print(
            f"   target {result.target_names[target_id]}: HP {before}; statuses: {status_text}"
        )

    observations = _records(result, "observation")
    if observations:
        print("\n2. Values/conditions observed by the function")
        for record in observations:
            print(f"   {record.data['label']} -> {record.data['value']}")

    returns = _records(result, "script_return")
    normalized = _records(result, "normalized_commands")
    if returns:
        print("\n3. Function return")
        print(f"   original return value: {returns[-1].data['result']}")
        if normalized:
            print("   commands the engine will execute:")
            for command in normalized[-1].data["commands"]:
                print(f"     - {command}")

    calculations = [
        record
        for record in result.trace_records
        if record.kind in {"damage_calculation", "heal_calculation"}
    ]
    if calculations:
        print("\n4. Engine calculation (recorded by the real rules engine)")
        for record in calculations:
            data = record.data
            if record.kind == "damage_calculation":
                print(f"   target: {data['target_name']}")
                print(
                    "     base = power "
                    f"{data['power']} + {data['attack_stat_name']} {data['attack_stat']} * 1.4 "
                    f"- defense {data['defense_stat']} * 0.8 = {data['base']:.2f}"
                )
                print(
                    f"     variance = {data['variance']:.3f}; "
                    f"guard multiplier = {data['guard_multiplier']:.1f}; "
                    f"damage = {data['damage']}"
                )
            else:
                print(
                    f"   {data['target_name']}: power {data['power']} + "
                    f"effective magic {data['magic']} -> requested {data['requested']}; "
                    f"restored {data['amount']}"
                )

    commands = _records(result, "script_command")
    if len(commands) > 1:
        print("\n   Loop/command trace")
        for record in commands:
            data = record.data
            names = [
                result.target_names.get(target_id, result.actor_name)
                for target_id in data["target_ids"]
            ]
            print(
                f"     command {data['command_index']}: {data['command_type']} "
                f"-> {', '.join(names) or 'no target'}"
            )

    print("\n5. Result")
    print(f"   user HP: {result.actor_before} -> {result.actor_after}")
    for target_id, before in result.targets_before.items():
        target_name = result.target_names[target_id]
        print(f"   {target_name} HP: {before} -> {result.targets_after[target_id]}")

    interesting = [
        event
        for event in result.events
        if event.get("type") in {"move", "damage", "heal", "status", "stat", "miss", "ko"}
    ]
    if interesting:
        print("\n   Battle events")
        for event in interesting:
            text = event.get("text") or repr(event)
            print(f"     [{event.get('type')}] {text}")


def run_strategy_scenario(
    content: GameContent,
    scenario: TeachingScenario,
) -> None:
    encounter = content.encounters[scenario.encounter_id]
    trace = TeachingTrace(echo=False)
    state = new_battle(encounter, content=content, teaching_trace=trace)
    scenario.apply_to_state(state)
    team = state.teams[scenario.strategy_team_index]
    actor_id = team.active_ids[0]
    context_facts = [
        state.combatants[cid]
        for index, other_team in enumerate(state.teams)
        if index != scenario.strategy_team_index
        for cid in other_team.active_ids
    ]
    action = choose_ai_action(state, actor_id, random.Random(scenario.seed))
    actor = state.combatants[actor_id]
    print(f"\n{scenario.title}")
    print("=" * len(scenario.title))
    print(scenario.description)
    print(f"\nStrategy actor: {actor.spec.name} HP {actor.current_hp}/{actor.spec.max_hp}")
    print("Visible enemies:")
    for enemy in context_facts:
        print(
            f"  {enemy.spec.name}: HP {enemy.current_hp}/{enemy.spec.max_hp} "
            f"ratio={enemy.current_hp / enemy.spec.max_hp:.3f}"
        )
    print("\nStrategy chose:")
    if action.kind == "skill" and action.move_id is not None:
        move_name = content.moves[action.move_id].name
        target_names = [state.combatants[target_id].spec.name for target_id in action.target_ids]
        target_text = ", ".join(target_names) if target_names else "automatic target"
        print(f"  use {move_name} -> {target_text}")
    elif action.kind == "defend":
        print("  defend")
    else:
        print(f"  {action.kind}")


def build_parser(
    content: GameContent,
    scenarios: Mapping[str, TeachingScenario] | None = None,
) -> argparse.ArgumentParser:
    scenarios = scenarios or {}
    parser = argparse.ArgumentParser(
        description="Run deterministic RPG experiments and inspect what the real engine does."
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
    move_parser.add_argument("--debug-traceback", action="store_true")

    if scenarios:
        scenario_parser = subparsers.add_parser(
            "scenario", help="Run one deliberate classroom scenario"
        )
        scenario_parser.add_argument("scenario_id", choices=sorted(scenarios))
        scenario_parser.add_argument("--seed", type=int)
        scenario_parser.add_argument("--debug-traceback", action="store_true")
    return parser


def main(
    content: GameContent | None = None,
    scenarios: Mapping[str, TeachingScenario] | None = None,
) -> None:
    logger.remove()
    if content is None:
        try:
            from student_game import CONTENT, SCENARIOS
        except ContentValidationError as exc:
            print(exc)
            raise SystemExit(2) from None
        content = CONTENT
        scenarios = SCENARIOS
    scenarios = scenarios or {}
    parser = build_parser(content, scenarios)
    args = parser.parse_args()
    try:
        _run_command(content, scenarios, parser, args)
    except StudentCodeError as exc:
        if getattr(args, "debug_traceback", False):
            raise
        parser.exit(3, f"\nYour student-authored code stopped the experiment:\n  {exc}\n"
                      "Run again with --debug-traceback to see the full Python traceback.\n")
    except (KeyError, ValueError) as exc:
        parser.error(str(exc))


def _run_command(content, scenarios, parser, args) -> None:
    if args.command == "list":
        for move_id, move in content.moves.items():
            if args.scripted and move.script is None:
                continue
            suffix = " [Python function]" if move.script is not None else ""
            print(f"{move_id:28} {move.name}{suffix}")
        return

    if args.command == "scenario":
        scenario = scenarios[args.scenario_id]
        problems = scenario.validate(content)
        if problems:
            parser.error(f"scenario {scenario.scenario_id!r}: " + "; ".join(problems))
        if args.seed is not None:
            from dataclasses import replace

            scenario = replace(scenario, seed=args.seed)
        print(f"\nScenario: {scenario.title}\n{scenario.description}")
        print(
            f"Play the same setup with:\n  python main.py --scenario {scenario.scenario_id} "
            f"--seed {scenario.seed}"
        )
        if scenario.inspect_mode == "strategy":
            run_strategy_scenario(content, scenario)
            return
        if scenario.inspect_mode == "simulation":
            from rpg_battle.teaching.simulate import simulate_once

            result = simulate_once(
                content,
                scenario.encounter_id,
                seed=scenario.seed,
                state_setup=scenario.apply_to_state,
            )
            print(
                f"\nOne deterministic simulation: winner={result.winner}, "
                f"rounds={result.rounds}, remaining HP={result.remaining_hp}"
            )
            return
        if scenario.move_id is None or scenario.user_char_id is None:
            parser.error(f"scenario {scenario.scenario_id!r} has no move experiment")
        move = content.moves[scenario.move_id]
        _print_script(move)
        result = run_move_scenario(content, scenario)
        _print_result(content, scenario.move_id, result)
        return

    move = content.moves[args.move_id]
    _print_script(move)
    target_char_ids = args.target or _default_targets(content, args.move_id, args.user)
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
