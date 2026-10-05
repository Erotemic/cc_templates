#!/usr/bin/env python3
"""Drive capstone games without a UI and continuously check their state.

This is useful both as a developer tool and as a teaching example.  A real game
can be exercised thousands of times without clicking through menus, while the
same invariants used by the test suite are checked after every transition.

Examples
--------
python capstone/simulate.py --world both --runs 25 --steps 250
python capstone/simulate.py --world star --runs 1 --steps 80 --trace
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import random

from art.catalog import choose_art
from engine.game import AdventureGame
from engine.validation import assert_valid_state
from worlds.dust_vault import WORLD_DATA as DUST_VAULT
from worlds.star_crystal import WORLD_DATA as STAR_CRYSTAL


@dataclass
class SimulationResult:
    world: str
    runs: int = 0
    actions: int = 0
    wins: int = 0
    losses: int = 0
    unfinished: int = 0
    transitions: Counter[tuple[str, str]] = field(default_factory=Counter)

    def absorb(self, game: AdventureGame, actions: int) -> None:
        self.runs += 1
        self.actions += actions
        if game.won:
            self.wins += 1
        elif game.lost:
            self.losses += 1
        else:
            self.unfinished += 1


def _resolve_riddle(game: AdventureGame, rng: random.Random) -> list[str]:
    npc = game.npcs[game.current_npc_name]
    # Mix success and failure so both riddle transitions are exercised.
    answer = npc["riddle"]["answers"][0] if rng.random() < 0.65 else "wrong answer"
    return game.submit_riddle_answer(answer)


def drive_random_game(
    world: dict,
    *,
    seed: int,
    steps: int,
    trace: bool = False,
) -> tuple[AdventureGame, Counter[tuple[str, str]], int]:
    """Run one deterministic random walk through a game."""
    game = AdventureGame(world, seed=seed)
    rng = random.Random(seed ^ 0xC0FFEE)
    transitions: Counter[tuple[str, str]] = Counter()

    assert_valid_state(game)
    for step in range(steps):
        if game.over:
            return game, transitions, step

        before = game.mode
        if game.mode == "riddle":
            lines = _resolve_riddle(game, rng)
            action_label = "<riddle answer>"
        else:
            choices = game.choices()
            if not choices:
                raise AssertionError(
                    f"non-terminal game has no choices: mode={game.mode!r}, "
                    f"room={game.player_location!r}"
                )
            choice = rng.choice(choices)
            action_label = choice.action
            lines = game.apply(choice.action)

        after = game.mode
        transitions[(before, after)] += 1
        assert_valid_state(game)
        # Presentation must also be able to observe every state without
        # mutating it or throwing an exception.
        choose_art(game.snapshot(), "\n".join(lines))

        if trace:
            summary = " | ".join(line for line in lines if line)
            print(
                f"{step:03d} {before:>18} -> {after:<18} "
                f"{action_label:<28} {summary[:100]}"
            )

    return game, transitions, steps


def simulate_world(
    label: str,
    world: dict,
    *,
    runs: int,
    steps: int,
    seed: int,
    trace: bool = False,
) -> SimulationResult:
    result = SimulationResult(world=label)
    for offset in range(runs):
        game, transitions, actions = drive_random_game(
            world,
            seed=seed + offset,
            steps=steps,
            trace=trace and offset == 0,
        )
        result.transitions.update(transitions)
        result.absorb(game, actions)
    return result


def _print_result(result: SimulationResult) -> None:
    print(
        f"{result.world}: runs={result.runs} actions={result.actions} "
        f"wins={result.wins} losses={result.losses} unfinished={result.unfinished}"
    )
    common = result.transitions.most_common(8)
    if common:
        print("  common transitions:")
        for (before, after), count in common:
            print(f"    {before:>18} -> {after:<18} {count}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", choices=("star", "dust", "both"), default="both")
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--steps", type=int, default=250)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args(argv)

    worlds = []
    if args.world in {"star", "both"}:
        worlds.append(("Star Crystal", STAR_CRYSTAL))
    if args.world in {"dust", "both"}:
        worlds.append(("Dust Vault", DUST_VAULT))

    for label, world in worlds:
        result = simulate_world(
            label,
            world,
            runs=args.runs,
            steps=args.steps,
            seed=args.seed,
            trace=args.trace,
        )
        _print_result(result)


if __name__ == "__main__":
    main()
