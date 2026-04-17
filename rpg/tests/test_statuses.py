import random
import unittest

from rpg_battle.core.actions import skill_action
from rpg_battle.core.battle_state import get_combatant, new_battle
from rpg_battle.core.models import StatusState
from rpg_battle.core.rules import finish_round, resolve_action


class TestStatuses(unittest.TestCase):
    def test_slow_status_can_apply(self):
        state = new_battle()
        actor_id = state.teams[0].active_ids[1]
        target_id = state.teams[1].active_ids[0]
        resolve_action(state, skill_action(actor_id, "thorn_bind", (target_id,)), random.Random(1))
        target = get_combatant(state, target_id)
        self.assertTrue("slow" in target.statuses or target.current_hp < target.spec.max_hp)

    def test_burn_ticks_at_round_end(self):
        state = new_battle()
        target_id = state.teams[0].active_ids[0]
        target = get_combatant(state, target_id)
        target.statuses["burn"] = StatusState("burn", 2)
        before = target.current_hp
        finish_round(state)
        self.assertLess(target.current_hp, before)


if __name__ == "__main__":
    unittest.main()
