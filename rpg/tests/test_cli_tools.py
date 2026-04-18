from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from rpg_battle.cli.render_audio import build_parser as build_audio_parser
from rpg_battle.cli.render_battle_state import build_parser as build_state_parser
from rpg_battle.cli.render_character import build_parser as build_character_parser
from rpg_battle.__main__ import build_parser as build_game_parser, build_encounter_from_args
from rpg_battle.content.teams import TEAMS
from rpg_battle.content.audio import MUSIC_TRACKS, SOUND_EFFECTS
from rpg_battle.content.characters import CHARACTERS
from rpg_battle.content.encounters import ENCOUNTERS


def test_render_character_parser_accepts_known_id() -> None:
    parser = build_character_parser()
    args = parser.parse_args(["knight"])
    assert args.character_id in CHARACTERS
    assert args.output is None


def test_render_state_parser_defaults() -> None:
    parser = build_state_parser()
    args = parser.parse_args([])
    assert args.encounter is None
    assert args.steps == 0
    assert args.dt > 0


def test_render_audio_parser_accepts_kind_and_asset() -> None:
    parser = build_audio_parser()
    args = parser.parse_args(["soft_dungeon_crawl", "--kind", "music"])
    assert args.asset_id in MUSIC_TRACKS
    assert args.kind == "music"


def test_audio_registries_are_nonempty() -> None:
    assert MUSIC_TRACKS
    assert SOUND_EFFECTS


def test_root_dev_scripts_exist() -> None:
    assert Path("render_character.py").exists()
    assert Path("render_battle_state.py").exists()
    assert Path("render_audio.py").exists()


def test_render_character_parser_accepts_no_show() -> None:
    parser = build_character_parser()
    args = parser.parse_args(["knight", "--no-show"])
    assert args.character_id == "knight"
    assert args.no_show is True


def test_render_battle_state_parser_accepts_no_show() -> None:
    parser = build_state_parser()
    args = parser.parse_args(["--no-show"])
    assert args.no_show is True


def test_render_audio_parser_accepts_no_show() -> None:
    parser = build_audio_parser()
    args = parser.parse_args(["soft_dungeon_crawl", "--kind", "music", "--no-show"])
    assert args.no_show is True


def test_game_parser_overrides_encounter_fields() -> None:
    parser = build_game_parser()
    args = parser.parse_args(
        [
            "--encounter",
            "default",
            "--player-team",
            "extra",
            "--enemy-team",
            "default_enemy",
            "--music-track",
            "boss_battle_frenzy",
            "--player-limit",
            "2",
            "--enemy-limit",
            "1",
        ]
    )
    encounter = build_encounter_from_args(args)
    assert encounter.player_team is TEAMS["extra"]
    assert encounter.enemy_team is TEAMS["default_enemy"]
    assert encounter.music_track_id == "boss_battle_frenzy"
    assert encounter.active_limits == (2, 1)
