from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from rpg_battle.cli.render_battle_state import build_parser as build_state_parser
from rpg_battle.cli.render_character import build_parser as build_character_parser
from rpg_battle.content.characters import CHARACTERS


def test_render_character_parser_defaults() -> None:
    parser = build_character_parser()
    args = parser.parse_args(["knight"])
    assert args.character_id in CHARACTERS
    # The CLI computes the default filename after parsing so an explicit
    # --output remains distinguishable from the generated default.
    assert args.output is None


def test_render_state_parser_defaults() -> None:
    parser = build_state_parser()
    args = parser.parse_args([])
    # With no encounter on the command line, the interactive preview command
    # chooses one later. Parser tests should only assert parser-owned defaults.
    assert args.encounter is None
    assert args.output is None
    assert args.steps == 0
    assert args.dt > 0


def test_root_dev_scripts_exist() -> None:
    assert Path("render_character.py").exists()
    assert Path("render_battle_state.py").exists()
