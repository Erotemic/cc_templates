#!/usr/bin/env python3
"""Show one decision traveling through the real RPG battle session.

Run from rpg/: python trace_turn.py --seed 3 --decisions 2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from loguru import logger

from rpg_battle.battle.session import BattleSession
from rpg_battle.core.ai import choose_ai_action, choose_ai_replacement
from student_game import CONTENT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encounter", default=CONTENT.default_encounter_id,
                        choices=sorted(CONTENT.encounters))
    parser.add_argument("--seed", type=int, default=3)
    parser.add_argument("--decisions", type=int, default=1)
    args = parser.parse_args()
    if args.decisions <= 0:
        parser.error("--decisions must be positive")
    logger.remove()
    session = BattleSession(CONTENT.encounters[args.encounter], args.seed, content=CONTENT)
    print(f"Session: {session.encounter.title} (seed={args.seed})")
    decided = 0
    while not session.finished and decided < args.decisions:
        transition = session.next_step()
        for event in transition.events:
            print(f"  event: {event['type']} — {event.get('text', '')}")
        request = transition.request
        if request is None:
            continue
        print(f"  request: {request.kind}, team={request.team_index}, "
              f"actor={request.actor_id}, reserves={list(request.choices)}")
        if request.kind == "replacement":
            choice = choose_ai_replacement(session.state, request.team_index)
        else:
            assert request.actor_id is not None
            choice = choose_ai_action(session.state, request.actor_id, session.rng)
        if choice is None:
            raise RuntimeError(f"No choice for {request!r}")
        print(f"  decision: {choice!r}")
        for event in session.submit(choice):
            print(f"  event: {event['type']} — {event.get('text', '')}")
        decided += 1
    print(f"After {decided} decisions: outcome={session.state.outcome}, "
          f"round={session.state.round_number}, next={session.request}")


if __name__ == "__main__":
    main()
