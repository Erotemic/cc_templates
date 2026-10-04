from __future__ import annotations

from pathlib import Path

import pygame

from rpg_battle.render.svg_support import load_svg_surface


def _load_svg(path: Path) -> pygame.Surface:
    if not pygame.get_init():
        pygame.init()
    surface = load_svg_surface(path.read_bytes(), path.name)
    assert surface.get_width() > 0
    assert surface.get_height() > 0
    return surface


def test_native_pygame_svg_loader_handles_path_only_fixture() -> None:
    svg_path = Path(__file__).resolve().parent / 'data' / 'path_only_smoke.svg'
    surface = _load_svg(svg_path)
    assert surface.get_size() == (160, 160)


def test_native_pygame_svg_loader_handles_path_rich_reference() -> None:
    svg_path = Path(__file__).resolve().parent / 'data' / 'space_pirate_paths_reference.svg'
    surface = _load_svg(svg_path)
    assert surface.get_width() >= 200
    assert surface.get_height() >= 200


def test_native_pygame_svg_loader_handles_runtime_space_pirate_asset() -> None:
    svg_path = Path(__file__).resolve().parents[1] / 'student_game' / 'assets' / 'sprites' / 'space_pirate.svg'
    surface = _load_svg(svg_path)
    assert surface.get_width() >= 200
    assert surface.get_height() >= 200


def test_native_pygame_svg_loader_handles_runtime_moon_mage_asset() -> None:
    svg_path = Path(__file__).resolve().parents[1] / 'student_game' / 'assets' / 'sprites' / 'moon_mage.svg'
    surface = _load_svg(svg_path)
    assert surface.get_width() >= 200
    assert surface.get_height() >= 200
