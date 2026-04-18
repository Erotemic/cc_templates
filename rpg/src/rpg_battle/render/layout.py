from __future__ import annotations

"""Centralized battle-scene layout helpers.

The layout is deliberately computed from a few meaningful measurements instead of
scattered magic numbers. This keeps the battlefield more stable as HUD panes or
party sizes change.
"""

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class BattleLayout:
    """Concrete screen regions used by the battle scene."""

    player_panel: pygame.Rect
    enemy_panel: pygame.Rect
    battlefield: pygame.Rect
    left_region: pygame.Rect
    right_region: pygame.Rect
    banner_rect: pygame.Rect
    menu_rect: pygame.Rect
    log_rect: pygame.Rect


@dataclass(frozen=True)
class LayoutMetrics:
    """Input values that influence battle scene layout."""

    screen_width: int
    screen_height: int
    left_team_rows: int
    right_team_rows: int
    menu_options: int


TOP_MARGIN = 32
SIDE_MARGIN = 30
COLUMN_GAP = 30
BOTTOM_MARGIN = 6
HUD_GAP = 18
BANNER_HEIGHT = 44
BANNER_TOP_GAP = 10
FORMATION_SIDE_CLEARANCE = 24
FORMATION_TOP_CLEARANCE = 84
FORMATION_BOTTOM_CLEARANCE = 128


def _team_panel_height(row_count: int) -> int:
    safe_rows = max(2, row_count)
    return 62 + safe_rows * 26


def _lower_hud_height(menu_options: int) -> int:
    safe_options = max(1, menu_options)
    return max(168, 78 + safe_options * 28)


def compute_battle_layout(metrics: LayoutMetrics) -> BattleLayout:
    """Compute non-overlapping layout regions for the battle scene.

    The battlefield sits between a top roster band and a lower action/log band.
    The formation regions then reserve headroom for labels and footroom for HP
    bars so battlers are much less likely to overlap the bottom HUD.
    """

    top_panel_height = max(
        _team_panel_height(metrics.left_team_rows),
        _team_panel_height(metrics.right_team_rows),
    )
    lower_hud_height = _lower_hud_height(metrics.menu_options)

    top_panel_width = (metrics.screen_width - 2 * SIDE_MARGIN - COLUMN_GAP) // 2
    player_panel = pygame.Rect(SIDE_MARGIN, TOP_MARGIN, top_panel_width, top_panel_height)
    enemy_panel = pygame.Rect(
        metrics.screen_width - SIDE_MARGIN - top_panel_width,
        TOP_MARGIN,
        top_panel_width,
        top_panel_height,
    )

    lower_hud_top = metrics.screen_height - BOTTOM_MARGIN - lower_hud_height
    menu_width = 430
    menu_rect = pygame.Rect(SIDE_MARGIN, lower_hud_top, menu_width, lower_hud_height)
    log_rect = pygame.Rect(
        menu_rect.right + COLUMN_GAP,
        lower_hud_top,
        metrics.screen_width - SIDE_MARGIN - (menu_rect.right + COLUMN_GAP),
        lower_hud_height,
    )

    battlefield_top = top_panel_height + TOP_MARGIN + HUD_GAP
    battlefield_bottom = lower_hud_top - HUD_GAP
    battlefield = pygame.Rect(
        SIDE_MARGIN,
        battlefield_top,
        metrics.screen_width - 2 * SIDE_MARGIN,
        max(150, battlefield_bottom - battlefield_top),
    )

    banner_width = min(600, battlefield.width - 120)
    banner_rect = pygame.Rect(0, 0, banner_width, BANNER_HEIGHT)
    banner_rect.midtop = (battlefield.centerx, battlefield.y + BANNER_TOP_GAP)

    formation_top = banner_rect.bottom + FORMATION_TOP_CLEARANCE
    formation_bottom = battlefield.bottom - FORMATION_BOTTOM_CLEARANCE
    formation_height = max(72, formation_bottom - formation_top)
    left_region = pygame.Rect(
        battlefield.x + FORMATION_SIDE_CLEARANCE,
        formation_top,
        battlefield.width // 2 - FORMATION_SIDE_CLEARANCE * 2,
        formation_height,
    )
    right_region = pygame.Rect(
        battlefield.centerx + FORMATION_SIDE_CLEARANCE,
        formation_top,
        battlefield.width // 2 - FORMATION_SIDE_CLEARANCE * 2,
        formation_height,
    )

    return BattleLayout(
        player_panel=player_panel,
        enemy_panel=enemy_panel,
        battlefield=battlefield,
        left_region=left_region,
        right_region=right_region,
        banner_rect=banner_rect,
        menu_rect=menu_rect,
        log_rect=log_rect,
    )
