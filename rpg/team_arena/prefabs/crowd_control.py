"""Example 5: prefer hitting a group of enemies over a single enemy."""


def choose_action(turn):
    if "arena_sweep" in turn.available_move_ids:
        return turn.skill("arena_sweep")
    if "arena_storm" in turn.available_move_ids:
        return turn.skill("arena_storm")
    return turn.attack(target=turn.enemies[0])
