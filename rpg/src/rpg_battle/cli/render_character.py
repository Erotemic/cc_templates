from __future__ import annotations

"""Render one or all classroom RPG character sprites to PNG preview images."""

import argparse
import math
from pathlib import Path

import pygame

from rpg_battle.cli.common import choose_from_registry, console, default_output_path
from rpg_battle.cli.render_common import init_surface, save_surface, show_surface
from rpg_battle.content.characters import CHARACTERS
from rpg_battle.debug import configure_logging
from rpg_battle.render.renderer import draw_background
from rpg_battle.render.sprite_actor import SpriteActor
from rpg_battle.settings import SCREEN_HEIGHT, SCREEN_WIDTH


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "character_id",
        nargs="?",
        help="Character id from content/characters.py. Omit when using --all.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Render a contact sheet preview of every registered character.",
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
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not open a preview window after rendering",
    )
    return parser


def _render_character(
    surface: pygame.Surface, character_id: str, center: tuple[int, int], *, side: str, scale: float
) -> None:
    actor = SpriteActor(side)
    spec = CHARACTERS[character_id]
    actor.draw(surface, spec.sprite_id, center, scale=scale)


def _render_single_character(
    character_id: str, *, output: str, side: str, scale: float, transparent: bool, no_show: bool
) -> None:
    console.print(f"[bold green]Rendering[/bold green] character [magenta]{character_id}[/magenta]")
    surface = init_surface(headless=no_show)
    if transparent:
        surface.fill((0, 0, 0, 0))
    else:
        draw_background(surface)
    _render_character(
        surface, character_id, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50), side=side, scale=scale
    )
    pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), width=2)
    font = pygame.font.Font(None, 36)
    label = font.render(CHARACTERS[character_id].name, True, (240, 240, 245))
    label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, 44))
    surface.blit(label, label_rect)
    save_surface(surface, Path(output))
    if not no_show:
        show_surface(surface, title=f"Character Preview - {CHARACTERS[character_id].name}")


def _render_all_characters(*, output: str, side: str, transparent: bool, no_show: bool) -> None:
    character_ids = sorted(CHARACTERS)
    columns = 4
    rows = max(1, math.ceil(len(character_ids) / columns))
    cell_width = 320
    cell_height = 240
    margin = 20
    top_offset = 36
    width = columns * cell_width + margin * 2
    height = rows * cell_height + margin * 2 + top_offset
    surface = init_surface(width=width, height=height, headless=no_show)
    if transparent:
        surface.fill((0, 0, 0, 0))
    else:
        draw_background(surface)
    font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 40)
    title = title_font.render("All Character Previews", True, (240, 240, 245))
    surface.blit(title, title.get_rect(midtop=(width // 2, 10)))
    for index, character_id in enumerate(character_ids):
        col = index % columns
        row = index // columns
        cell_rect = pygame.Rect(
            margin + col * cell_width,
            margin + row * cell_height + top_offset,
            cell_width,
            cell_height,
        )
        cell_surface = surface.subsurface(cell_rect)
        pygame.draw.rect(
            cell_surface, (255, 255, 255), cell_surface.get_rect(), width=1, border_radius=8
        )
        center = (cell_rect.centerx, cell_rect.top + 118)
        _render_character(surface, character_id, center, side=side, scale=1.1)
        name = CHARACTERS[character_id].name
        label = font.render(name, True, (240, 240, 245))
        label_rect = label.get_rect(midtop=(cell_rect.centerx, cell_rect.top + 8))
        surface.blit(label, label_rect)
        role = font.render(CHARACTERS[character_id].role.title(), True, (210, 214, 230))
        role_rect = role.get_rect(midbottom=(cell_rect.centerx, cell_rect.bottom - 8))
        surface.blit(role, role_rect)
    save_surface(surface, Path(output))
    if not no_show:
        show_surface(surface, title="Character Preview - All Characters")


def main() -> None:
    configure_logging()
    args = build_parser().parse_args()
    if args.all:
        output = args.output or str(default_output_path("all_characters_preview.png"))
        console.print("[bold green]Rendering[/bold green] [magenta]all characters[/magenta]")
        _render_all_characters(
            output=output,
            side=args.side,
            transparent=args.transparent,
            no_show=args.no_show,
        )
        pygame.quit()
        return

    character_ids = sorted(CHARACTERS)
    if args.character_id and args.character_id not in CHARACTERS:
        raise SystemExit(
            f"Unknown character_id: {args.character_id}. Choose from: {', '.join(character_ids)}"
        )
    character_id = args.character_id or choose_from_registry(
        "Character Preview",
        character_ids,
        description="Pick a registered character to inspect.",
    )
    output = args.output or str(default_output_path(f"{character_id}_preview.png"))
    _render_single_character(
        character_id,
        output=output,
        side=args.side,
        scale=args.scale,
        transparent=args.transparent,
        no_show=args.no_show,
    )
    pygame.quit()


if __name__ == "__main__":
    main()
