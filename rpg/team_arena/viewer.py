from __future__ import annotations

"""Animated spectator for pre-recorded student team-controller battles.

The viewer intentionally NEVER imports student controller files. The existing
pygame BattleScene resolves the recorded actions with the original battle
rules, using saved RNG states for identical results and attack animations.
"""

from collections import deque
import re

import pygame

from rpg_battle.audio.engine import AudioEngine
from rpg_battle.battle.battle_scene import BattleScene
from rpg_battle.render.layout import LayoutMetrics, compute_battle_layout
from rpg_battle.settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TEXT_COLOR

from team_arena.engine import ARENA_ID, content_for_match
from team_arena.recording import apply_replay_step

LEFT_COLOR = (140, 210, 255)
RIGHT_COLOR = (255, 185, 154)
PRINT_COLOR = (230, 238, 178)
DIM_COLOR = (170, 183, 205)
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def clean_line(text: str) -> str:
    """Show literal print output, without terminal control sequences in the UI."""
    text = ANSI_ESCAPE.sub("", text)
    return "".join(ch if ch.isprintable() else " " for ch in text)


class ArenaBattleScene(BattleScene):
    """Reuse full RPG sprite, effects, health-bar, battle-log animations."""

    def __init__(self, rect: pygame.Rect, recording: dict, *, audio: AudioEngine) -> None:
        self.recording = recording
        self.step_index = 0
        self.active_team: int | None = None
        self.active_actor = ""
        self.last_source = ""
        self.console: deque[tuple[str, tuple[int, int, int]]] = deque(maxlen=180)
        self.speed = 1.0
        self.paused = False
        self.debug_font: pygame.font.Font | None = None
        content = content_for_match(recording["left"], None, recording["right"], None)
        super().__init__(rect, audio=audio, content=content,
                         encounter=content.encounters[ARENA_ID], seed=recording["seed"])
        self.debug_font = pygame.font.Font(None, 20)
        self.console.append(("Add print(...) inside choose_action(turn).", DIM_COLOR))

    def reset(self) -> None:
        super().reset()
        self.step_index = 0
        self.active_team = None
        self.active_actor = ""
        self.last_source = ""
        self.console.clear()
        self.console.append(("Replaying the same recorded decisions.", DIM_COLOR))

    def _layout(self):
        # The ordinary menu region becomes a taller, readable controller console.
        return compute_battle_layout(LayoutMetrics(
            screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT,
            left_team_rows=len(self._team_roster(0)),
            right_team_rows=len(self._team_roster(1)),
            menu_options=5,
        ))

    def _handle_battle_event(self, event: dict) -> None:
        if event["type"] == "turn_start" and event.get("team") in (0, 1):
            self.active_team = event["team"]
        super()._handle_battle_event(event)

    def update(self, dt: float) -> None:
        # Intercept BOTH teams before the stock scene asks for human input on
        # the left or decides with its default AI on the right.
        if (self.controller.state.winner is None
                and not self.event_queue
                and self.event_timer <= 0
                and self.current_event_timer <= 0
                and (self.controller.current_actor_id is not None
                     or self.controller.state.pending_replacements)):
            if self.step_index >= len(self.recording["steps"]):
                raise ValueError("Recording exhausted before the displayed battle ended")
            step = self.recording["steps"][self.step_index]
            self.event_queue = apply_replay_step(self.controller, step)
            self.step_index += 1
            self.active_team = step["team"]
            if step["type"] == "action":
                self._announce_decision(step)
        super().update(dt)

    def _announce_decision(self, step: dict) -> None:
        side = step["team"]
        name = self.recording["left"] if side == 0 else self.recording["right"]
        color = LEFT_COLOR if side == 0 else RIGHT_COLOR
        self.active_actor = step["actor_name"]
        self.last_source = self.recording["sources"][side]
        headline = f"{name} / {step['actor_name']}: {step['description']}"
        self.console.append((headline, color))
        print(f"[{name} | {self.last_source} | round {step['round']} | {step['actor_name']}]", flush=True)
        for line in step["prints"]:
            visible = clean_line(line)
            self.console.append((f"print> {visible}", PRINT_COLOR))
            print(f"  print> {visible}", flush=True)
        print(f"  -> {step['description']}", flush=True)

    def _draw_hud(self, surface: pygame.Surface, layout) -> None:
        super()._draw_hud(surface, layout)
        header_font = self.debug_font or self.small_font
        panels = (layout.player_panel, layout.enemy_panel)
        for index, panel in enumerate(panels):
            name = self.recording["left"] if index == 0 else self.recording["right"]
            file = self.recording["sources"][index]
            active = index == self.active_team and self.controller.state.winner is None
            color = LEFT_COLOR if index == 0 else RIGHT_COLOR
            if active:
                pygame.draw.rect(surface, color, panel, 3, border_radius=14)
            label = f"{'> ' if active else ''}{name}  -  {file}"
            line = self._fit_text(header_font, label, panel.width - 12)
            surface.blit(header_font.render(line, True, color if active else DIM_COLOR),
                         (panel.x + 6, 8))

    def _draw_menu(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        status = "PAUSED" if self.paused else f"{self.speed:g}x"
        title = self.title_font.render(f"Controller Console  [{status}]", True, TEXT_COLOR)
        surface.blit(title, (rect.x + 14, rect.y + 10))
        subtitle_font = self.debug_font or self.small_font
        if self.active_team is None:
            source = "Waiting for the first turn..."
        else:
            source = f"Running: {self.last_source}"
        source = self._fit_text(subtitle_font, source, rect.width - 28)
        surface.blit(subtitle_font.render(source, True, DIM_COLOR),
                     (rect.x + 14, rect.y + 46))
        font = self.debug_font or self.small_font
        line_height = 21
        output_top = rect.y + 73
        footer_y = rect.bottom - 26
        count = max(1, (footer_y - output_top) // line_height)
        for index, (line, color) in enumerate(list(self.console)[-count:]):
            display = self._fit_text(font, clean_line(line), rect.width - 26)
            surface.blit(font.render(display, True, color),
                         (rect.x + 14, output_top + index * line_height))
        footer = "SPACE pause  +/- speed  R replay  ESC close"
        label = self._fit_text(font, footer, rect.width - 28)
        surface.blit(font.render(label, True, DIM_COLOR), (rect.x + 14, footer_y))

    def _draw_turn_banner(self, surface: pygame.Surface, layout) -> None:
        super()._draw_turn_banner(surface, layout)
        # Winner is explicit even after the battle banner fades out.
        if self.controller.state.winner is not None:
            winner = (self.recording["left"] if self.controller.state.winner == 0
                      else self.recording["right"])
            text = self.title_font.render(f"WINNER: {winner}", True, (255, 225, 150))
            surface.blit(text, text.get_rect(center=(layout.battlefield.centerx,
                                                    layout.battlefield.y + 82)))


def watch(recording: dict, *, speed: float = 1.0) -> None:
    """Open the existing animated RPG scene in spectator mode."""
    pygame.init()
    content = content_for_match(recording["left"], None, recording["right"], None)
    audio = AudioEngine(content)
    try:
        audio.initialize()
        title = f"Algorithm Arena: {recording['left']} vs {recording['right']}"
        pygame.display.set_caption(title)
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        scene = ArenaBattleScene(screen.get_rect(), recording, audio=audio)
        scene.speed = speed
        print("Viewer: SPACE pause; +/- speed; R replay; ESC quit.", flush=True)
        running = True
        while running:
            dt = min(0.1, clock.tick(FPS) / 1000.0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        scene.paused = not scene.paused
                    elif event.key == pygame.K_r:
                        scene.reset()
                    elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                        scene.speed = min(8.0, scene.speed * 2)
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        scene.speed = max(0.25, scene.speed / 2)
            if not scene.paused:
                scene.update(dt * scene.speed)
            scene.draw(screen)
            pygame.display.flip()
    finally:
        audio.stop_music()
        pygame.quit()
