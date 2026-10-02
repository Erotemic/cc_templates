from __future__ import annotations

"""Command-line entrypoint for launching the classroom RPG battle demo."""

import argparse
import sys

from loguru import logger

from rpg_battle.catalog import (
    ContentValidationError,
    ContentIssue,
    format_advisory_report,
    format_validation_report,
)

try:
    from student_game import CONTENT, SCENARIOS
except ContentValidationError as exc:
    CONTENT = None
    SCENARIOS = {}
    _CONTENT_ERROR = exc
else:
    _CONTENT_ERROR = None
from rpg_battle.core.models import EncounterSpec
from rpg_battle.debug import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    content = CONTENT
    parser.add_argument(
        "--encounter",
        choices=sorted(content.encounters) if content is not None else None,
        default=content.default_encounter_id if content is not None else None,
        help="Battle id from student_game",
    )
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS),
        help="Start from a deliberate lesson setup (HP, statuses, and battle)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Battle random seed. Restarting reuses this same seed.",
    )
    parser.add_argument(
        "--player-team",
        choices=sorted(content.teams) if content is not None else None,
        help="Override the player team",
    )
    parser.add_argument(
        "--enemy-team",
        choices=sorted(content.teams) if content is not None else None,
        help="Override the enemy team",
    )
    parser.add_argument(
        "--music-track",
        choices=sorted(content.music_tracks) if content is not None else None,
        help="Override the battle music",
    )
    parser.add_argument(
        "--player-limit",
        type=int,
        help="Override the player active-frontline limit",
    )
    parser.add_argument(
        "--enemy-limit",
        type=int,
        help="Override the enemy active-frontline limit",
    )
    parser.add_argument(
        "--teach",
        action="store_true",
        help="Print a readable trace when custom move/AI functions execute",
    )
    parser.add_argument(
        "--debug-traceback",
        action="store_true",
        help="Show a full traceback if student-authored runtime code crashes",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate structure and behavior functions, then exit without pygame",
    )
    return parser


def build_encounter_from_args(args: argparse.Namespace) -> EncounterSpec:
    if CONTENT is None:
        raise _CONTENT_ERROR or RuntimeError("RPG content did not load")
    if args.scenario:
        scenario = SCENARIOS[args.scenario]
        base = CONTENT.encounters[scenario.encounter_id]
    else:
        base = CONTENT.encounters.get(args.encounter, CONTENT.default_encounter)
    player_team = CONTENT.teams[args.player_team] if args.player_team else base.player_team
    enemy_team = CONTENT.teams[args.enemy_team] if args.enemy_team else base.enemy_team
    player_limit = args.player_limit if args.player_limit is not None else base.active_limits[0]
    enemy_limit = args.enemy_limit if args.enemy_limit is not None else base.active_limits[1]
    music_track_id = args.music_track or base.music_track_id or CONTENT.default_battle_track
    encounter = EncounterSpec(
        encounter_id=base.encounter_id,
        title=base.title,
        player_team=player_team,
        enemy_team=enemy_team,
        active_limits=(player_limit, enemy_limit),
        music_track_id=music_track_id,
    )
    logger.debug(
        "CLI encounter config: encounter={} player_team={} enemy_team={} limits={} music={}",
        encounter.encounter_id,
        encounter.player_team.name,
        encounter.enemy_team.name,
        encounter.active_limits,
        encounter.music_track_id,
    )
    return encounter


def main() -> None:
    args = build_parser().parse_args()
    configure_logging(default_level="WARNING" if args.teach or args.check else "INFO")
    if _CONTENT_ERROR is not None:
        print(_CONTENT_ERROR, file=sys.stderr)
        raise SystemExit(2)
    assert CONTENT is not None

    # Explicit checking is where student functions execute. Importing
    # ``student_game`` above only performed structural validation.
    issues = CONTENT.validate(include_behaviors=args.check)
    checked_scenarios = SCENARIOS.values() if args.check else (
        [SCENARIOS[args.scenario]] if args.scenario else []
    )
    if not issues:
        for scenario in checked_scenarios:
            issues.extend(ContentIssue(f'scenario "{scenario.scenario_id}"', problem)
                          for problem in scenario.validate(CONTENT))
    if issues:
        print(format_validation_report(issues), file=sys.stderr)
        raise SystemExit(2)
    if args.check:
        print(
            f"Game content looks good: {len(CONTENT.characters)} characters, "
            f"{len(CONTENT.moves)} moves, {len(CONTENT.encounters)} battles."
        )
        notes = CONTENT.advisories()
        if notes:
            print()
            print(format_advisory_report(notes))
        return

    encounter = build_encounter_from_args(args)
    scenario = SCENARIOS.get(args.scenario)
    seed = args.seed if args.seed is not None else (scenario.seed if scenario else 5)
    state_setup = scenario.apply_to_state if scenario else None

    from rpg_battle.core.scripting import StudentCodeError
    from rpg_battle.game import run_game

    try:
        run_game(
            encounter=encounter,
            content=CONTENT,
            teach=args.teach,
            seed=seed,
            state_setup=state_setup,
        )
    except StudentCodeError as exc:
        if args.debug_traceback:
            raise
        print("\nYour student-authored code stopped the battle:", file=sys.stderr)
        print(f"  {exc}", file=sys.stderr)
        print("\nRun again with --debug-traceback to see the full Python traceback.", file=sys.stderr)
        raise SystemExit(3) from None


if __name__ == "__main__":
    main()
