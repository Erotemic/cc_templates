import unittest

from rpg_battle.core.ai import choose_ai_action
from rpg_battle.core.battle_state import new_battle


class TestAI(unittest.TestCase):
    def test_ai_returns_action_for_active_enemy(self):
        state = new_battle()
        actor_id = state.teams[1].active_ids[0]
        action = choose_ai_action(state, actor_id)
        self.assertEqual(action.actor_id, actor_id)
        self.assertIn(action.kind, {"attack", "skill", "defend", "switch"})


if __name__ == "__main__":
    unittest.main()
