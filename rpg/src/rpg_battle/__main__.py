from __future__ import annotations

"""Command-line entrypoint for launching the classroom RPG battle demo."""

import argparse
import sys

from loguru import logger

from rpg_battle.catalog import ContentValidationError

try:
    from student_game import CONTENT
except ContentValidationError as exc:
    CONTENT = None
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
        help="Battle id from student_game/battles.py",
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
        "--check",
        action="store_true",
        help="Validate game content and exit without opening pygame",
    )
    return parser


def build_encounter_from_args(args: argparse.Namespace) -> EncounterSpec:
    if CONTENT is None:
        raise _CONTENT_ERROR or RuntimeError("RPG content did not load")
    base = CONTENT.encounters.get(args.encounter, CONTENT.default_encounter)
    player_team = CONTENT.teams[args.player_team] if args.player_team else base.player_team
    enemy_team = CONTENT.teams[args.enemy_team] if args.enemy_team else base.enemy_team
    player_limit = args.player_limit if args.player_limit is not None else base.active_limits[0]
    enemy_limit = args.enemy_limit if args.enemy_limit is not None else base.active_limits[1]
    music_track_id = (
        args.music_track or base.music_track_id or CONTENT.default_battle_track
    )
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
    configure_logging()
    if _CONTENT_ERROR is not None:
        print(_CONTENT_ERROR, file=sys.stderr)
        raise SystemExit(2)
    assert CONTENT is not None
    args = build_parser().parse_args()
    issues = CONTENT.validate()
    if issues:
        # Normally student_game/catalog.py catches these while compiling. Keeping this
        # check here makes CLI overrides and future relaxed loading modes safe.
        CONTENT.require_valid()
    if args.check:
        print(
            f"Game content looks good: {len(CONTENT.characters)} characters, "
            f"{len(CONTENT.moves)} moves, {len(CONTENT.encounters)} battles."
        )
        return
    encounter = build_encounter_from_args(args)
    from rpg_battle.game import run_game

    run_game(encounter=encounter, content=CONTENT)


if __name__ == "__main__":
    main()
