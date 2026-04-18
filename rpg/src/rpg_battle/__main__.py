from __future__ import annotations

"""Command-line entrypoint for launching the classroom RPG battle demo."""

import argparse

from loguru import logger

from rpg_battle.content.audio import DEFAULT_BATTLE_TRACK, MUSIC_TRACKS
from rpg_battle.content.encounters import DEFAULT_ENCOUNTER, ENCOUNTERS
from rpg_battle.content.teams import TEAMS
from rpg_battle.core.models import EncounterSpec
from rpg_battle.debug import configure_logging
from rpg_battle.game import run_game


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--encounter",
        choices=sorted(ENCOUNTERS),
        default="default",
        help="Encounter preset id from content/encounters.py",
    )
    parser.add_argument(
        "--player-team",
        choices=sorted(TEAMS),
        help="Override the player team preset",
    )
    parser.add_argument(
        "--enemy-team",
        choices=sorted(TEAMS),
        help="Override the enemy team preset",
    )
    parser.add_argument(
        "--music-track",
        choices=sorted(MUSIC_TRACKS),
        help="Override the encounter music track",
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
    return parser


def build_encounter_from_args(args: argparse.Namespace) -> EncounterSpec:
    base = ENCOUNTERS.get(args.encounter, DEFAULT_ENCOUNTER)
    player_team = TEAMS[args.player_team] if args.player_team else base.player_team
    enemy_team = TEAMS[args.enemy_team] if args.enemy_team else base.enemy_team
    player_limit = args.player_limit if args.player_limit is not None else base.active_limits[0]
    enemy_limit = args.enemy_limit if args.enemy_limit is not None else base.active_limits[1]
    music_track_id = args.music_track or base.music_track_id or DEFAULT_BATTLE_TRACK
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
    args = build_parser().parse_args()
    encounter = build_encounter_from_args(args)
    run_game(encounter=encounter)


if __name__ == "__main__":
    main()
