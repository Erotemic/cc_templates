"""Example 5: prefer hitting a group of enemies over a single enemy."""


def choose_action(turn):
    if turn.can_use("arena_sweep"):
        return turn.skill("arena_sweep")
    if turn.can_use("arena_storm"):
        return turn.skill("arena_storm")
    return turn.attack(target=turn.enemies[0])
