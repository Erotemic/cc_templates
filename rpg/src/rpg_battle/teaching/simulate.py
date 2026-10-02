from __future__ import annotations

"""Headless battle experiments for teaching loops, randomness, and statistics."""

import argparse
from collections import Counter
from dataclasses import dataclass
from statistics import mean

from loguru import logger

from rpg_battle.battle.battle_controller import BattleController
from rpg_battle.catalog import ContentValidationError, GameContent
from rpg_battle.core.ai import choose_ai_action, choose_ai_replacement
from rpg_battle.core.rules import resolve_action, resolve_replacement


@dataclass(frozen=True)
class SimulationResult:
    winner: int | None
    rounds: int
    events: tuple[dict, ...]


def simulate_once(
    content: GameContent,
    encounter_id: str,
    *,
    seed: int = 0,
    max_steps: int = 2000,
) -> SimulationResult:
    """Run both teams under AI control without opening pygame."""

    encounter = content.encounters[encounter_id]
    controller = BattleController(encounter=encounter, seed=seed, content=content)
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

    return SimulationResult(
        winner=controller.state.winner,
        rounds=controller.state.round_number,
        events=tuple(events),
    )


def simulate_many(
    content: GameContent,
    encounter_id: str,
    *,
    runs: int = 100,
    seed: int = 0,
) -> list[SimulationResult]:
    return [simulate_once(content, encounter_id, seed=seed + index) for index in range(runs)]


def build_parser(content: GameContent) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run many RPG battles headlessly and summarize what happened."
    )
    parser.add_argument(
        "--encounter",
        default="workshop" if "workshop" in content.encounters else content.default_encounter_id,
        choices=sorted(content.encounters),
    )
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
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
    args = build_parser(content).parse_args()
    if args.runs <= 0:
        raise SystemExit("--runs must be positive")

    results = simulate_many(content, args.encounter, runs=args.runs, seed=args.seed)
    encounter = content.encounters[args.encounter]
    win_counts = Counter(result.winner for result in results)
    move_counts = Counter(
        event.get("move_name")
        for result in results
        for event in result.events
        if event.get("type") == "move"
    )

    print(f"{encounter.title}: {args.runs} deterministic-seed battle simulations")
    print(f"seed range: {args.seed} .. {args.seed + args.runs - 1}")
    print()
    print(f"{encounter.player_team.name} wins: {win_counts.get(0, 0)}")
    print(f"{encounter.enemy_team.name} wins: {win_counts.get(1, 0)}")
    print(f"unfinished: {win_counts.get(None, 0)}")
    print(f"average rounds: {mean(result.rounds for result in results):.2f}")

    if move_counts:
        print("\nMost-used moves:")
        for move_name, count in move_counts.most_common(8):
            print(f"  {move_name}: {count}")


if __name__ == "__main__":
    main()
