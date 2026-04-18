from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from rpg_battle.content.characters import CHARACTERS
from rpg_battle.content.encounters import ENCOUNTERS
from rpg_battle.dev.render_character import build_parser as build_character_parser
from rpg_battle.dev.render_battle_state import build_parser as build_state_parser


def test_render_character_parser_defaults() -> None:
    parser = build_character_parser()
    args = parser.parse_args(["knight"])
    assert args.character_id in CHARACTERS
    assert args.output.endswith(".png")


def test_render_state_parser_defaults() -> None:
    parser = build_state_parser()
    args = parser.parse_args([])
    assert args.encounter in ENCOUNTERS
    assert args.output.endswith(".png")


def test_root_dev_scripts_exist() -> None:
    assert Path("render_character.py").exists()
    assert Path("render_battle_state.py").exists()
