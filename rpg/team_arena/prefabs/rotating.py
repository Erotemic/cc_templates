"""Example 4: use the round number to alternate between two actions."""


def choose_action(turn):
    if turn.round_number % 3 == 0:
        return turn.defend()
    target = turn.enemies[0]
    if turn.can_use("arena_crush"):
        return turn.skill("arena_crush", target=target)
    return turn.attack(target=target)
