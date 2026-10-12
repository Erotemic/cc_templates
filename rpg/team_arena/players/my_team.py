"""Your AI team controller. This is the first (and only) file you need to edit.

From the rpg directory, run `python arena.py` to WATCH your code fight.
Save changes, press R in the battle window, and watch the NEW decisions.
"""


def choose_action(turn):
    # This runs when EITHER of your two fighters takes a turn.
    print("My fighter:", turn.user.name, "HP:", turn.user.hp)

    # Try changing the target or when you use a learned skill instead.
    # Attack and Defend work for BOTH fighters without learning anything.
    return turn.attack(target=turn.enemies[0])
