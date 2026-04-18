from __future__ import annotations

"""Render a battle scene to inspect placement and UI layout."""

import argparse
from pathlib import Path

import pygame

from rpg_battle.debug import configure_logging

from rpg_battle.audio.engine import AudioEngine
from rpg_battle.battle.battle_scene import BattleScene
from rpg_battle.cli.common import choose_from_registry, choose_yes_no, console, default_output_path
from rpg_battle.cli.render_common import configure_headless_pygame, save_surface
from rpg_battle.content.encounters import ENCOUNTERS
from rpg_battle.settings import SCREEN_HEIGHT, SCREEN_WIDTH


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--encounter",
        choices=sorted(ENCOUNTERS),
        help="Encounter id from content/encounters.py",
    )
    parser.add_argument("--output", help="Output PNG path. Defaults to ./battle_preview.png")
    parser.add_argument(
        "--open-menu",
        action="store_true",
        help="Advance until the first player command menu is visible",
    )
    parser.add_argument(
        "--steps", type=int, default=0, help="Additional fixed updates to run before rendering"
    )
    parser.add_argument(
        "--dt", type=float, default=0.1, help="Delta time for scripted update steps"
    )
    return parser


def _advance_until_menu(scene: BattleScene, dt: float) -> None:
    for _ in range(120):
        if scene.menu_stack:
            return
        scene.update(dt)


def main() -> None:
    configure_logging()
    args = build_parser().parse_args()
    encounter_id = args.encounter or choose_from_registry(
        "Encounter Preview",
        sorted(ENCOUNTERS),
        description="Pick a registered encounter to render.",
    )
    open_menu = (
        args.open_menu
        if args.encounter is not None
        else choose_yes_no("Open the first player menu before saving?", default=False)
    )
    output = args.output or str(default_output_path("battle_preview.png"))

    console.print(f"[bold green]Rendering[/bold green] encounter [magenta]{encounter_id}[/magenta]")
    configure_headless_pygame()
    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    audio = AudioEngine()
    audio.initialize()
    audio.stop_music()
    scene = BattleScene(screen.get_rect(), audio=audio, encounter=ENCOUNTERS[encounter_id])
    if open_menu:
        _advance_until_menu(scene, args.dt)
    for _ in range(max(0, args.steps)):
        scene.update(args.dt)
    scene.draw(screen)
    save_surface(screen, Path(output))
    audio.stop_music()
    pygame.quit()


if __name__ == "__main__":
    main()
