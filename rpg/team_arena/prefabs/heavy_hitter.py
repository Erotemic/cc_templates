"""Example 6: powerful attacks, but it never reconsider its target."""


def choose_action(turn):
    target = turn.enemies[0]
    if turn.can_use("arena_crush"):
        return turn.skill("arena_crush", target=target)
    if turn.can_use("arena_spark"):
        return turn.skill("arena_spark", target=target)
    return turn.attack(target=target)
