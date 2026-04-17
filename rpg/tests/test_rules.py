import random
import unittest

from rpg_battle.core.actions import attack_action, skill_action, switch_action
from rpg_battle.core.battle_state import get_combatant, new_battle
from rpg_battle.core.rules import resolve_action


class TestRules(unittest.TestCase):
    def test_attack_reduces_selected_target_hp(self):
        state = new_battle()
        actor_id = state.teams[0].active_ids[0]
        target_id = state.teams[1].active_ids[0]
        target_hp = get_combatant(state, target_id).current_hp
        resolve_action(state, attack_action(actor_id, (target_id,)), random.Random(0))
        self.assertLess(get_combatant(state, target_id).current_hp, target_hp)

    def test_heal_targets_selected_ally(self):
        state = new_battle()
        healer_id = state.teams[0].active_ids[1]
        target_id = state.teams[0].active_ids[0]
        target = get_combatant(state, target_id)
        target.current_hp -= 15
        resolve_action(
            state,
            skill_action(healer_id, "healing_light", (target_id,)),
            random.Random(0),
        )
        self.assertLessEqual(target.current_hp, target.spec.max_hp)
        self.assertGreater(target.current_hp, target.spec.max_hp - 15)

    def test_switch_swaps_active_and_reserve(self):
        state = new_battle()
        actor_id = state.teams[0].active_ids[0]
        reserve_id = state.teams[0].reserve_ids[0]
        events = resolve_action(state, switch_action(actor_id, reserve_id), random.Random(0))
        self.assertIn(reserve_id, state.teams[0].active_ids)
        self.assertIn(actor_id, state.teams[0].reserve_ids)
        self.assertTrue(any(event["type"] == "switch" for event in events))

    def test_all_enemy_move_hits_both_frontliners(self):
        state = new_battle()
        actor_id = state.teams[1].active_ids[0]
        target_ids = tuple(state.teams[0].active_ids)
        before = {cid: get_combatant(state, cid).current_hp for cid in target_ids}
        events = resolve_action(
            state,
            skill_action(actor_id, "artifact_burst", target_ids),
            random.Random(0),
        )
        damage_targets = {event["target_id"] for event in events if event["type"] == "damage"}
        self.assertEqual(damage_targets, set(target_ids))
        for target_id in target_ids:
            self.assertLess(get_combatant(state, target_id).current_hp, before[target_id])


if __name__ == "__main__":
    unittest.main()
