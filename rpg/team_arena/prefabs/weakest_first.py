"""Example 2: choose an enemy by looking through a collection."""


def choose_action(turn):
    target = turn.enemies[0]
    for enemy in turn.enemies[1:]:
        if enemy.hp < target.hp:
            target = enemy
    return turn.use("arena_tap", target=target)
