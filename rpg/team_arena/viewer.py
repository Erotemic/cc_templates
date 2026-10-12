from __future__ import annotations

"""Animated spectator for pre-recorded student team-controller battles.

The viewer intentionally NEVER imports student controller files. The existing
pygame BattleScene resolves the recorded actions with the original battle
rules, using saved RNG states for identical results and attack animations.
"""

from collections import deque
import re
from typing import Callable

import pygame

from rpg_battle.audio.engine import AudioEngine
from rpg_battle.battle.battle_scene import BattleScene
from rpg_battle.render.layout import LayoutMetrics, compute_battle_layout
from rpg_battle.settings import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TEXT_COLOR

from team_arena.engine import ARENA_ID, content_for_match
from team_arena.recording import replay_choice

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
        self.stepping = False
        self.step_origin = 0
        self.current_choice = "Waiting for a decision..."
        self.current_prints: list[str] = []
        self.debug_font: pygame.font.Font | None = None
        content = content_for_match(recording["left"], None, recording["right"], None)
        super().__init__(rect, audio=audio, content=content,
                         encounter=content.encounters[ARENA_ID], seed=recording["seed"],
                         decision_provider=self._replay_decision, human_teams=frozenset())
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
        self.current_choice = "Waiting for a decision..."
        self.current_prints = []
        self.stepping = False

    def step_one_decision(self) -> None:
        """Finish exactly one new recorded action, then pause its animations."""
        self.paused = True
        if (self.session.state.outcome != "ongoing"
                or self.step_index >= len(self.recording["steps"])):
            self.stepping = False
            return
        self.stepping = True
        self.step_origin = self.step_index

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

    def _replay_decision(self, session, request):
        """Supply a recorded decision through the same scene path as any AI."""
        if self.step_index >= len(self.recording["steps"]):
            raise ValueError("Recording exhausted before the displayed battle ended")
        step = self.recording["steps"][self.step_index]
        decision = replay_choice(session, step)
        self.step_index += 1
        self.active_team = step["team"]
        if step["type"] == "action":
            self._announce_decision(step)
        return decision

    def update(self, dt: float) -> None:
        super().update(dt)
        if (self.stepping and self.step_index > self.step_origin
                and not self.event_queue and self.event_timer <= 0
                and self.current_event_timer <= 0):
            self.stepping = False

    def _announce_decision(self, step: dict) -> None:
        side = step["team"]
        name = self.recording["left"] if side == 0 else self.recording["right"]
        color = LEFT_COLOR if side == 0 else RIGHT_COLOR
        self.active_actor = step["actor_name"]
        self.last_source = self.recording["sources"][side]
        headline = (
            f"{name} / {step['actor_name']} ({step['mana_before']}/{step['max_mana']} MP): "
            f"{step['description']}"
        )
        self.console.append((headline, color))
        self.current_choice = headline
        self.current_prints = [clean_line(line) for line in step["prints"]]
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
            file = self.recording["sources"][index]
            active = index == self.active_team and self.session.state.outcome == "ongoing"
            color = LEFT_COLOR if index == 0 else RIGHT_COLOR
            if active:
                pygame.draw.rect(surface, color, panel, 3, border_radius=14)
            # Keep source ownership visible *inside* the team's header rather
            # than floating above the panel border or colliding with roster rows.
            title_width = self.title_font.size(self.session.state.teams[index].name)[0]
            source_x = panel.left + 18 + title_width + 16
            available = max(0, panel.right - 18 - source_x)
            if available >= 34:
                line = self._fit_text(header_font, file, available)
                source_label = header_font.render(
                    line, True, color if active else DIM_COLOR
                )
                surface.blit(
                    source_label,
                    source_label.get_rect(midleft=(source_x, panel.y + 23)),
                )

    def _draw_menu(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        status = "PAUSED" if self.paused else f"{self.speed:g}x"
        title = self.title_font.render(f"Controller Console [{status}]", True, TEXT_COLOR)
        surface.blit(title, (rect.x + 14, rect.y + 10))
        font = self.debug_font or self.small_font
        if self.active_team is None:
            source = "Waiting for the first turn..."
        else:
            source = f"Running: {self.last_source}"
        source = self._fit_text(font, source, rect.width - 28)
        surface.blit(font.render(source, True, DIM_COLOR), (rect.x + 14, rect.y + 43))

        # Keep the CURRENT decision and student prints on screen throughout
        # its attack animation; older lines scroll only in the history region.
        choice = self._fit_text(font, self.current_choice, rect.width - 28)
        surface.blit(font.render(choice, True, PRINT_COLOR), (rect.x + 14, rect.y + 66))
        footer_y = rect.bottom - 26
        available = max(0, (footer_y - rect.y - 96) // 21)
        pinned_count = min(3, available, len(self.current_prints))
        for index, line in enumerate(self.current_prints[-pinned_count:]
                                     if pinned_count else []):
            label = self._fit_text(font, f"print> {line}", rect.width - 28)
            surface.blit(font.render(label, True, PRINT_COLOR),
                         (rect.x + 14, rect.y + 88 + index * 21))
        history_top = rect.y + 92 + pinned_count * 21
        history_count = max(0, (footer_y - history_top) // 21)
        for index, (line, color) in enumerate(list(self.console)[-history_count:]
                                              if history_count else []):
            label = self._fit_text(font, clean_line(line), rect.width - 28)
            surface.blit(font.render(label, True, color),
                         (rect.x + 14, history_top + index * 21))
        footer = "SPACE pause  N next  R rerun code  P replay  +/- speed  ESC exit"
        label = self._fit_text(font, footer, rect.width - 28)
        surface.blit(font.render(label, True, DIM_COLOR), (rect.x + 14, footer_y))

    def _draw_turn_banner(self, surface: pygame.Surface, layout) -> None:
        super()._draw_turn_banner(surface, layout)
        # A completed tie is not a win for the right team.
        if self.session.state.outcome != "ongoing":
            if self.session.state.outcome == "draw":
                summary = "DRAW: Both teams defeated"
            else:
                winner = (self.recording["left"] if self.session.state.winner == 0
                          else self.recording["right"])
                summary = f"WINNER: {winner}"
            text = self.title_font.render(summary, True, (255, 225, 150))
            surface.blit(text, text.get_rect(center=(layout.battlefield.centerx,
                                                    layout.battlefield.y + 82)))


def watch(recording: dict, *, speed: float = 1.0,
          reload_recording: Callable[[], dict] | None = None) -> None:
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
        print("Viewer: R reload saved Python; P replay; N next turn; "
              "SPACE pause; +/- speed; ESC quit.", flush=True)
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
                        scene.stepping = False
                    elif event.key == pygame.K_n:
                        scene.step_one_decision()
                    elif event.key == pygame.K_p:
                        scene.reset()
                    elif event.key == pygame.K_r:
                        if reload_recording is None:
                            scene.reset()
                        else:
                            # Re-run student Python in the bounded worker, not
                            # in this pygame process. Keep the old scene if
                            # there is a syntax error or an endless loop.
                            scene.console.append(("Re-reading saved controller code...", DIM_COLOR))
                            scene.draw(screen)
                            pygame.display.flip()
                            try:
                                fresh = reload_recording()
                            except (RuntimeError, ValueError, OSError) as exc:
                                message = str(exc)
                                print(f"Could not rerun: {message}", flush=True)
                                lines = message.splitlines()
                                detail = next((line for line in lines if ".py, line " in line),
                                              lines[-1])
                                detail = detail.strip().replace("\\", "/").rsplit("/", 1)[-1]
                                scene.current_choice = f"ERROR: {detail}"
                                scene.current_prints = []
                                scene.console.append((scene.current_choice, RIGHT_COLOR))
                                scene.paused = True
                                scene.stepping = False
                            else:
                                old_speed = scene.speed
                                scene = ArenaBattleScene(screen.get_rect(), fresh, audio=audio)
                                scene.speed = old_speed
                                scene.console.append(("Loaded your newly saved Python code.", DIM_COLOR))
                                print("Updated controller recording loaded.", flush=True)
                    elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                        scene.speed = min(8.0, scene.speed * 2)
                    elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                        scene.speed = max(0.25, scene.speed / 2)
            if not scene.paused or scene.stepping:
                scene.update(dt * scene.speed)
            scene.draw(screen)
            pygame.display.flip()
    finally:
        audio.stop_music()
        pygame.quit()
