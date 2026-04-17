import random
import unittest

from rpg_battle.battle.battle_controller import BattleController
from rpg_battle.core.actions import attack_action
from rpg_battle.core.battle_state import new_battle
from rpg_battle.core.rules import (
    build_round_turn_queue,
    finish_round,
    make_round_start_event,
    make_turn_start_event,
    resolve_action,
)


class TestTurnFlow(unittest.TestCase):
    def test_round_and_turn_events_are_explicit(self):
        state = new_battle()
        order = build_round_turn_queue(state, random.Random(0))
        self.assertEqual(make_round_start_event(state)["type"], "round_start")
        self.assertEqual(make_turn_start_event(state, order[0])["type"], "turn_start")

    def test_actions_resolve_one_actor_at_a_time(self):
        state = new_battle()
        actor_id = state.teams[0].active_ids[0]
        target_id = state.teams[1].active_ids[0]
        events = resolve_action(state, attack_action(actor_id, (target_id,)), random.Random(0))
        event_types = [event["type"] for event in events]
        self.assertIn("move", event_types)
        self.assertIn("damage", event_types)
        self.assertNotIn("turn_start", event_types)

    def test_finish_round_advances_round_number(self):
        state = new_battle()
        current_round = state.round_number
        finish_round(state)
        self.assertEqual(state.round_number, current_round + 1)

    def test_controller_announces_round_before_turn(self):
        controller = BattleController(seed=0)
        first_events = controller.advance_to_next_turn()
        self.assertEqual([event["type"] for event in first_events], ["round_start"])
        second_events = controller.advance_to_next_turn()
        self.assertEqual([event["type"] for event in second_events], ["turn_start"])


if __name__ == "__main__":
    unittest.main()
