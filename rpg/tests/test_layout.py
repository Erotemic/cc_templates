from rpg_battle.render.layout import LayoutMetrics, compute_battle_layout


def test_layout_keeps_battlefield_between_hud_bands() -> None:
    layout = compute_battle_layout(
        LayoutMetrics(
            screen_width=1120,
            screen_height=700,
            left_team_rows=3,
            right_team_rows=3,
            menu_options=4,
        )
    )
    assert layout.battlefield.top >= layout.player_panel.bottom
    assert layout.battlefield.top >= layout.enemy_panel.bottom
    assert layout.battlefield.bottom <= layout.menu_rect.top
    assert layout.battlefield.bottom <= layout.log_rect.top


def test_layout_regions_stay_inside_battlefield() -> None:
    layout = compute_battle_layout(
        LayoutMetrics(
            screen_width=1120,
            screen_height=700,
            left_team_rows=4,
            right_team_rows=4,
            menu_options=6,
        )
    )
    assert layout.battlefield.contains(layout.left_region)
    assert layout.battlefield.contains(layout.right_region)
    assert layout.battlefield.contains(layout.banner_rect)


def test_layout_controls_anchor_stays_on_screen() -> None:
    layout = compute_battle_layout(
        LayoutMetrics(
            screen_width=1120,
            screen_height=700,
            left_team_rows=3,
            right_team_rows=3,
            menu_options=4,
        )
    )
    x, y = layout.controls_anchor
    assert 0 < x < 1120
    assert layout.menu_rect.bottom < y < 700


from rpg_battle.render.formation import formation_slots
import pygame


def test_three_unit_left_formation_is_staggered_and_spread() -> None:
    slots = formation_slots(pygame.Rect(0, 0, 400, 300), "left", 3)
    assert len(slots) == 3
    assert slots[0].x < slots[1].x < slots[2].x
    assert slots[0].y < slots[1].y < slots[2].y
    assert (slots[1].y - slots[0].y) >= 55
    assert (slots[2].y - slots[1].y) >= 55


def test_three_unit_right_formation_is_mirrored() -> None:
    slots = formation_slots(pygame.Rect(0, 0, 400, 300), "right", 3)
    assert len(slots) == 3
    assert slots[0].x > slots[1].x > slots[2].x
    assert slots[0].y < slots[1].y < slots[2].y
