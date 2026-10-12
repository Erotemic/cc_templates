"""Example 1: a one-line action. Good for understanding return values."""


def choose_action(turn):
    return turn.attack(target=turn.enemies[0])
