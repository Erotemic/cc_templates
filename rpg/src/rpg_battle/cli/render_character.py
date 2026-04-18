from __future__ import annotations

"""Render one classroom RPG character sprite to a PNG preview."""

import argparse
from pathlib import Path

import pygame

from rpg_battle.debug import configure_logging

from rpg_battle.cli.common import choose_from_registry, console, default_output_path
from rpg_battle.cli.render_common import init_surface, save_surface
from rpg_battle.content.characters import CHARACTERS
from rpg_battle.render.renderer import draw_background
from rpg_battle.render.sprite_actor import SpriteActor
from rpg_battle.settings import SCREEN_HEIGHT, SCREEN_WIDTH


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "character_id",
        nargs="?",
        choices=sorted(CHARACTERS),
        help="Character id from content/characters.py",
    )
    parser.add_argument("--output", help="Output PNG path. Defaults to ./<character>_preview.png")
    parser.add_argument(
        "--side", choices=("left", "right"), default="left", help="Facing side for the preview"
    )
    parser.add_argument("--scale", type=float, default=1.6, help="Preview scale for the sprite")
    parser.add_argument(
        "--transparent",
        action="store_true",
        help="Render on a transparent background instead of the battle backdrop",
    )
    return parser


def main() -> None:
    configure_logging()
    args = build_parser().parse_args()
    character_id = args.character_id or choose_from_registry(
        "Character Preview",
        sorted(CHARACTERS),
        description="Pick a registered character to inspect.",
    )
    output = args.output or str(default_output_path(f"{character_id}_preview.png"))

    console.print(f"[bold green]Rendering[/bold green] character [magenta]{character_id}[/magenta]")
    surface = init_surface()
    if args.transparent:
        surface.fill((0, 0, 0, 0))
    else:
        draw_background(surface)
    actor = SpriteActor(args.side)
    spec = CHARACTERS[character_id]
    actor.draw(
        surface, spec.sprite_id, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50), scale=args.scale
    )
    pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), width=2)
    font = pygame.font.Font(None, 36)
    label = font.render(spec.name, True, (240, 240, 245))
    label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, 44))
    surface.blit(label, label_rect)
    save_surface(surface, Path(output))
    pygame.quit()


if __name__ == "__main__":
    main()
