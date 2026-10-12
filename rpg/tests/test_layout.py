import pytest

from rpg_battle.render.layout import (
    LayoutMetrics,
    compute_battle_layout,
    team_roster_row_layout,
)


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


from rpg_battle.render.formation import formation_slots
import pygame


def test_two_unit_left_formation_has_clear_spread() -> None:
    slots = formation_slots(pygame.Rect(0, 0, 400, 300), "left", 2)
    assert len(slots) == 2
    assert slots[0].x < slots[1].x
    assert slots[0].y < slots[1].y
    assert (slots[1].x - slots[0].x) >= 140
    assert (slots[1].y - slots[0].y) >= 120


def test_three_unit_left_formation_is_staggered_and_spread() -> None:
    slots = formation_slots(pygame.Rect(0, 0, 400, 300), "left", 3)
    assert len(slots) == 3
    assert slots[0].x < slots[1].x < slots[2].x
    assert slots[0].y < slots[1].y < slots[2].y
    assert (slots[1].x - slots[0].x) >= 90
    assert (slots[2].x - slots[1].x) >= 110
    assert (slots[1].y - slots[0].y) >= 90
    assert (slots[2].y - slots[1].y) >= 70


def test_three_unit_right_formation_is_mirrored() -> None:
    slots = formation_slots(pygame.Rect(0, 0, 400, 300), "right", 3)
    assert len(slots) == 3
    assert slots[0].x > slots[1].x > slots[2].x
    assert slots[0].y < slots[1].y < slots[2].y


def test_layout_reserves_readable_formation_height() -> None:
    layout = compute_battle_layout(
        LayoutMetrics(
            screen_width=1120,
            screen_height=700,
            left_team_rows=2,
            right_team_rows=2,
            menu_options=5,
        )
    )
    assert layout.left_region.height >= 140
    assert layout.right_region.height >= 140
    assert layout.left_region.bottom <= layout.battlefield.bottom
    assert layout.right_region.bottom <= layout.battlefield.bottom


@pytest.mark.parametrize('left_count,right_count', [
    (1, 1), (2, 3), (3, 2), (3, 3), (4, 2), (4, 4), (5, 3),
])
def test_team_roster_rows_fit_inside_both_cards(left_count: int, right_count: int) -> None:
    """All fighter rows must stay inside the top card, including 3+ fighters."""

    layout = compute_battle_layout(
        LayoutMetrics(1120, 700, left_count, right_count, 5)
    )
    assert layout.player_panel.bottom < layout.banner_rect.top
    assert layout.enemy_panel.bottom < layout.banner_rect.top

    for panel, count in (
        (layout.player_panel, left_count),
        (layout.enemy_panel, right_count),
    ):
        previous_bottom = 0
        for index in range(count):
            row = team_roster_row_layout(panel, index)
            assert panel.contains(row.row)
            assert row.row.contains(row.name)
            assert row.row.contains(row.hp)
            assert row.row.contains(row.mp)
            assert row.name.right < row.hp.left
            assert row.hp.right < row.mp.left
            assert row.mp.right == row.row.right
            assert row.row.top >= previous_bottom
            previous_bottom = row.row.bottom
        assert previous_bottom <= panel.bottom - 8


def test_unequal_rosters_use_same_header_height() -> None:
    layout = compute_battle_layout(LayoutMetrics(1120, 700, 3, 2, 5))
    assert layout.player_panel.bottom == layout.enemy_panel.bottom
    assert team_roster_row_layout(layout.player_panel, 2).row.bottom < layout.player_panel.bottom


@pytest.mark.parametrize('party_size', [3, 4])
def test_large_active_formation_keeps_meters_above_bottom_hud(party_size: int) -> None:
    """The lowest fighter footer must remain in the battlefield at 700px tall."""

    layout = compute_battle_layout(LayoutMetrics(1120, 700, party_size, party_size, 5))
    for region, side in ((layout.left_region, 'left'), (layout.right_region, 'right')):
        for slot in formation_slots(region, side, party_size):
            # The battlefield widget starts at y + 62 * scale and contains
            # two 14px meters, a 4px gap, and 10px of padding.
            footer_bottom = slot.y + 62 * slot.scale + 42
            assert footer_bottom <= layout.battlefield.bottom
