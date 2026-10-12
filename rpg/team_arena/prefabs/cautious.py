"""Example 3: change your mind using a conditional."""


def choose_action(turn):
    if turn.user.hp_ratio < 0.30:
        return turn.defend()
    return turn.attack(target=turn.enemies[0])
