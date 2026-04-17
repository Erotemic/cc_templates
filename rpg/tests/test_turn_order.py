import random
import unittest

from rpg_battle.core.battle_state import get_combatant, new_battle
from rpg_battle.core.effects import effective_stat
from rpg_battle.core.rules import build_round_turn_queue, make_turn_start_event


class TestTurnOrder(unittest.TestCase):
    def test_faster_combatant_goes_first(self):
        state = new_battle()
        order = build_round_turn_queue(state, random.Random(1))
        first = get_combatant(state, order[0])
        second = get_combatant(state, order[1])
        self.assertGreaterEqual(effective_stat(first, "speed"), effective_stat(second, "speed"))
        self.assertEqual(
            make_turn_start_event(state, first.combatant_id)["actor_name"], first.spec.name
        )


if __name__ == "__main__":
    unittest.main()
