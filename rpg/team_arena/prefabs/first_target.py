"""Example 1: a one-line action. Good for understanding return values."""


def choose_action(turn):
    return turn.use("arena_tap", target=turn.enemies[0])
