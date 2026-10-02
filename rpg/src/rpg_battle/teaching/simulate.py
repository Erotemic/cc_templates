from __future__ import annotations

"""Headless battle experiments for teaching loops, randomness, and statistics."""

import argparse
from collections import Counter
from dataclasses import dataclass
from statistics import mean
from typing import Callable, Mapping

from loguru import logger

from rpg_battle.battle.battle_controller import BattleController
from rpg_battle.catalog import ContentValidationError, GameContent
from rpg_battle.core.ai import choose_ai_action, choose_ai_replacement
from rpg_battle.core.models import BattleState
from rpg_battle.core.rules import resolve_action, resolve_replacement
from rpg_battle.teaching.scenarios import TeachingScenario


@dataclass(frozen=True)
class SimulationResult:
    winner: int | None
    rounds: int
    remaining_hp: tuple[int, int]
    damage_dealt: tuple[int, int]
    events: tuple[dict, ...]


def simulate_once(
    content: GameContent,
    encounter_id: str,
    *,
    seed: int = 0,
    max_steps: int = 2000,
    state_setup: Callable[[BattleState], None] | None = None,
) -> SimulationResult:
    """Run both teams under AI control without opening pygame."""

    encounter = content.encounters[encounter_id]
    controller = BattleController(encounter=encounter, seed=seed, content=content)
    if state_setup is not None:
        state_setup(controller.state)
    events: list[dict] = []

    for _ in range(max_steps):
        if controller.state.winner is not None:
            break

        advanced = controller.advance_to_next_turn()
        events.extend(advanced)

        if controller.state.pending_replacements:
            request = controller.state.pending_replacements[0]
            replacement_id = choose_ai_replacement(controller.state, request.team_index)
            if replacement_id is None:
                continue
            events.extend(
                resolve_replacement(controller.state, request.team_index, replacement_id)
            )
            continue

        actor_id = controller.current_actor_id
        if actor_id is None:
            continue
        action = choose_ai_action(controller.state, actor_id, controller.rng)
        events.extend(resolve_action(controller.state, action, controller.rng))
        controller.current_actor_id = None
    else:
        raise RuntimeError(
            f"simulation exceeded {max_steps} steps; this may indicate a battle-flow bug"
        )

    remaining_hp = []
    for team_index in range(2):
        remaining_hp.append(
            sum(
                combatant.current_hp
                for combatant in controller.state.combatants.values()
                if combatant.team_index == team_index
            )
        )

    damage_dealt = [0, 0]
    for event in events:
        if event.get("type") != "damage":
            continue
        actor_id = event.get("actor_id")
        if actor_id in controller.state.combatants:
            team_index = controller.state.combatants[actor_id].team_index
            damage_dealt[team_index] += int(event.get("amount", 0))

    return SimulationResult(
        winner=controller.state.winner,
        rounds=controller.state.round_number,
        remaining_hp=(remaining_hp[0], remaining_hp[1]),
        damage_dealt=(damage_dealt[0], damage_dealt[1]),
        events=tuple(events),
    )


def simulate_many(
    content: GameContent,
    encounter_id: str,
    *,
    runs: int = 100,
    seed: int = 0,
    state_setup: Callable[[BattleState], None] | None = None,
) -> list[SimulationResult]:
    return [
        simulate_once(
            content,
            encounter_id,
            seed=seed + index,
            state_setup=state_setup,
        )
        for index in range(runs)
    ]


def build_parser(
    content: GameContent,
    scenarios: Mapping[str, TeachingScenario] | None = None,
) -> argparse.ArgumentParser:
    scenarios = scenarios or {}
    parser = argparse.ArgumentParser(
        description="Run many RPG battles headlessly and summarize what happened."
    )
    parser.add_argument(
        "--encounter",
        default="workshop" if "workshop" in content.encounters else content.default_encounter_id,
        choices=sorted(content.encounters),
    )
    if scenarios:
        parser.add_argument(
            "--scenario",
            choices=sorted(scenarios),
            help="Use a named lesson setup instead of a plain encounter",
        )
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--seed", type=int)
    return parser


def _policy_name(team) -> str:
    if team.strategy is not None:
        return getattr(team.strategy, "__name__", "custom strategy")
    return "built-in heuristic AI"


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
    args = build_parser(content, scenarios).parse_args()
    if args.runs <= 0:
        raise SystemExit("--runs must be positive")

    scenario = scenarios.get(getattr(args, "scenario", None))
    encounter_id = scenario.encounter_id if scenario else args.encounter
    seed = args.seed if args.seed is not None else (scenario.seed if scenario else 0)
    state_setup = scenario.apply_to_state if scenario else None

    results = simulate_many(
        content,
        encounter_id,
        runs=args.runs,
        seed=seed,
        state_setup=state_setup,
    )
    encounter = content.encounters[encounter_id]
    win_counts = Counter(result.winner for result in results)
    move_counts = Counter(
        event.get("move_name")
        for result in results
        for event in result.events
        if event.get("type") == "move"
    )
    script_power_counts = Counter(
        (event.get("move_name"), event.get("command_power"))
        for result in results
        for event in result.events
        if event.get("scripted") and event.get("type") in {"damage", "heal"}
    )

    print(f"{encounter.title}: {args.runs} deterministic-seed battle simulations")
    print(f"seed range: {seed} .. {seed + args.runs - 1}")
    if scenario:
        print(f"scenario: {scenario.title}")
    print(f"player policy: {_policy_name(encounter.player_team)}")
    print(f"enemy policy:  {_policy_name(encounter.enemy_team)}")
    print()
    print(f"{encounter.player_team.name} wins: {win_counts.get(0, 0)}")
    print(f"{encounter.enemy_team.name} wins: {win_counts.get(1, 0)}")
    print(f"unfinished: {win_counts.get(None, 0)}")
    print(f"average rounds: {mean(result.rounds for result in results):.2f}")
    print(
        "average remaining HP: "
        f"{encounter.player_team.name}="
        f"{mean(result.remaining_hp[0] for result in results):.1f}, "
        f"{encounter.enemy_team.name}="
        f"{mean(result.remaining_hp[1] for result in results):.1f}"
    )
    print(
        "average damage dealt: "
        f"{encounter.player_team.name}="
        f"{mean(result.damage_dealt[0] for result in results):.1f}, "
        f"{encounter.enemy_team.name}="
        f"{mean(result.damage_dealt[1] for result in results):.1f}"
    )

    if move_counts:
        print("\nMost-used moves:")
        for move_name, count in move_counts.most_common(8):
            print(f"  {move_name}: {count}")

    if script_power_counts:
        print("\nScripted command branches (move / command power):")
        for (move_name, power), count in script_power_counts.most_common():
            print(f"  {move_name} / power {power}: {count}")

    print(
        "\nReusing the same seed range makes the experiment repeatable, but code "
        "changes can consume randomness differently, so compare outcomes rather "
        "than assuming every individual random draw stays aligned."
    )


if __name__ == "__main__":
    main()
