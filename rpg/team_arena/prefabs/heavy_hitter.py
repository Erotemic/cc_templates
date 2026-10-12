"""Example 6: powerful attacks, but it never reconsider its target."""


def choose_action(turn):
    target = turn.enemies[0]
    if "arena_crush" in turn.available_move_ids:
        return turn.use("arena_crush", target=target)
    return turn.use("arena_spark", target=target)
