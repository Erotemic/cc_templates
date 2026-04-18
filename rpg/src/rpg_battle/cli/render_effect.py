from __future__ import annotations

"""Preview one visual effect in an animated pygame window.

The default mode opens a small standalone window with:
- a battlefield-style animation preview
- a graph/path preview for path-based effects
- a play/pause button
- a seek bar so students can scrub through the effect math

Use ``--no-show`` to skip the window and only save a still frame.
"""

import argparse
from pathlib import Path

import pygame

from rpg_battle.cli.common import choose_from_registry, console, default_output_path
from rpg_battle.cli.render_common import init_surface, save_surface
from rpg_battle.content.effects import EFFECTS
from rpg_battle.debug import configure_logging
from rpg_battle.render.effect_builder import sample_path_points
from rpg_battle.render.effect_factory import make_effect

WINDOW_SIZE = (960, 620)
ANIM_RECT = pygame.Rect(60, 50, 840, 230)
GRAPH_RECT = pygame.Rect(60, 350, 840, 160)
CONTROLS_RECT = pygame.Rect(60, 290, 840, 42)
PLAY_BUTTON_RECT = pygame.Rect(CONTROLS_RECT.x + 12, CONTROLS_RECT.y + 6, 110, 30)
SLIDER_RECT = pygame.Rect(CONTROLS_RECT.x + 150, CONTROLS_RECT.y + 12, 720, 18)

BG = (20, 24, 32)
PANEL = (28, 30, 42)
OUTLINE = (220, 225, 242)
AXIS = (90, 96, 120)
TEXT = (230, 235, 248)
SUBTEXT = (190, 196, 220)
ACCENT = (120, 195, 255)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "effect_id", nargs="?", choices=sorted(EFFECTS), help="Effect id from content/effects.py"
    )
    parser.add_argument("--output", help="Output PNG path. Defaults to ./effect_preview.png")
    parser.add_argument(
        "--progress",
        type=float,
        default=0.5,
        help="Progress value [0,1] used for the saved preview frame",
    )
    parser.add_argument(
        "--no-show", action="store_true", help="Do not open a preview window after rendering"
    )
    return parser


def _draw_graph(surface: pygame.Surface, effect_id: str) -> None:
    spec = EFFECTS[effect_id]
    pygame.draw.rect(surface, PANEL, GRAPH_RECT, border_radius=14)
    pygame.draw.rect(surface, OUTLINE, GRAPH_RECT, 2, border_radius=14)
    font = pygame.font.Font(None, 26)
    title = font.render("Path / Graph Preview", True, TEXT)
    surface.blit(title, (GRAPH_RECT.x + 12, GRAPH_RECT.y + 10))
    graph = GRAPH_RECT.inflate(-40, -52)
    graph.y += 18
    mid_y = graph.centery
    pygame.draw.line(surface, AXIS, (graph.x, mid_y), (graph.right, mid_y), 1)
    pygame.draw.line(surface, AXIS, (graph.x, graph.top), (graph.x, graph.bottom), 1)
    if spec.path is None:
        text = font.render("This effect does not use a graph path.", True, SUBTEXT)
        surface.blit(text, text.get_rect(center=graph.center))
        return
    points = []
    max_amp = max(1.0, spec.path.amplitude)
    for x_norm, y_val in sample_path_points(spec.path):
        x = graph.x + int(graph.width * x_norm)
        y = mid_y - int((y_val / max_amp) * (graph.height * 0.42))
        points.append((x, y))
    pygame.draw.lines(surface, spec.color, False, points, max(1, spec.path.width))


def _draw_controls(surface: pygame.Surface, *, progress: float, playing: bool) -> None:
    pygame.draw.rect(surface, PANEL, CONTROLS_RECT, border_radius=14)
    pygame.draw.rect(surface, OUTLINE, CONTROLS_RECT, 2, border_radius=14)
    pygame.draw.rect(surface, (46, 52, 70), PLAY_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(surface, OUTLINE, PLAY_BUTTON_RECT, 1, border_radius=10)
    font = pygame.font.Font(None, 26)
    label = "Pause" if playing else "Play"
    surface.blit(font.render(label, True, TEXT), (PLAY_BUTTON_RECT.x + 30, PLAY_BUTTON_RECT.y + 5))

    pygame.draw.rect(surface, (46, 52, 70), SLIDER_RECT, border_radius=8)
    fill_rect = SLIDER_RECT.copy()
    fill_rect.width = max(8, int(SLIDER_RECT.width * progress))
    pygame.draw.rect(surface, ACCENT, fill_rect, border_radius=8)
    pygame.draw.rect(surface, OUTLINE, SLIDER_RECT, 1, border_radius=8)
    knob_x = SLIDER_RECT.x + int(SLIDER_RECT.width * progress)
    pygame.draw.circle(surface, TEXT, (knob_x, SLIDER_RECT.centery), 8)

    info = font.render("Space = play/pause   Drag = seek", True, SUBTEXT)
    surface.blit(info, (SLIDER_RECT.x, CONTROLS_RECT.y - 22))


def _draw_preview(
    surface: pygame.Surface, effect_id: str, progress: float, *, playing: bool
) -> None:
    surface.fill(BG)
    pygame.draw.rect(surface, PANEL, ANIM_RECT, border_radius=14)
    pygame.draw.rect(surface, OUTLINE, ANIM_RECT, 2, border_radius=14)
    font = pygame.font.Font(None, 30)
    title = font.render(f"Effect Preview: {effect_id}", True, TEXT)
    surface.blit(title, (ANIM_RECT.x + 12, ANIM_RECT.y + 10))
    start = (ANIM_RECT.x + 110, ANIM_RECT.centery + 20)
    end = (ANIM_RECT.right - 110, ANIM_RECT.centery - 6)
    pygame.draw.circle(surface, (120, 195, 255), start, 24)
    pygame.draw.circle(surface, (255, 145, 145), end, 24)
    effect = make_effect(effect_id, start, end)
    clamped = max(0.0, min(1.0, progress))
    effect.timer = effect.duration * (1.0 - clamped)
    effect.draw(surface)
    _draw_controls(surface, progress=clamped, playing=playing)
    _draw_graph(surface, effect_id)


def _slider_progress(pos: tuple[int, int]) -> float:
    return max(0.0, min(1.0, (pos[0] - SLIDER_RECT.x) / max(1, SLIDER_RECT.width)))


def _run_interactive_preview(effect_id: str, output: Path, initial_progress: float) -> None:
    screen = init_surface(*WINDOW_SIZE, headless=False)
    pygame.display.set_caption(f"Effect Preview - {effect_id}")
    clock = pygame.time.Clock()
    effect = EFFECTS[effect_id]
    progress = max(0.0, min(1.0, initial_progress))
    playing = True
    dragging = False
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in {pygame.K_ESCAPE, pygame.K_RETURN}:
                    running = False
                elif event.key == pygame.K_SPACE:
                    playing = not playing
                elif event.key == pygame.K_LEFT:
                    progress = max(0.0, progress - 0.02)
                    playing = False
                elif event.key == pygame.K_RIGHT:
                    progress = min(1.0, progress + 0.02)
                    playing = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if PLAY_BUTTON_RECT.collidepoint(event.pos):
                    playing = not playing
                elif SLIDER_RECT.collidepoint(event.pos):
                    dragging = True
                    progress = _slider_progress(event.pos)
                    playing = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                progress = _slider_progress(event.pos)
                playing = False
        if playing and effect.duration > 0:
            progress = (progress + dt / effect.duration) % 1.0
        _draw_preview(screen, effect_id, progress, playing=playing)
        pygame.display.flip()
    save_surface(screen, output)
    pygame.quit()


def main() -> None:
    configure_logging()
    args = build_parser().parse_args()
    effect_id = args.effect_id or choose_from_registry(
        "Effect Preview", sorted(EFFECTS), description="Pick a registered visual effect to inspect."
    )
    output = Path(
        args.output or default_output_path(f"{effect_id}_effect_preview.png")
    ).expanduser()
    console.print(f"[bold green]Rendering[/bold green] effect [magenta]{effect_id}[/magenta]")
    if args.no_show:
        surface = init_surface(*WINDOW_SIZE, headless=True)
        _draw_preview(surface, effect_id, args.progress, playing=False)
        save_surface(surface, output)
        pygame.quit()
        return
    _run_interactive_preview(effect_id, output.resolve(), args.progress)


if __name__ == "__main__":
    main()
