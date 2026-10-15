import unittest

from rpg_battle.core.battle_state import move_active_to_reserve, new_battle
from rpg_battle.core.rules import resolve_replacement


class TestReplacements(unittest.TestCase):
    def test_reserve_can_join_frontline(self):
        state = new_battle()
        reserve_id = state.teams[0].reserve_ids[0]
        move_active_to_reserve(state, state.teams[0].active_ids[0])
        events = resolve_replacement(state, 0, reserve_id)
        self.assertIn(reserve_id, state.teams[0].active_ids)
        self.assertTrue(any(event["type"] == "replacement_joined" for event in events))


if __name__ == "__main__":
    unittest.main()
