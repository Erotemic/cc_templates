"""Example 5: prefer hitting a group of enemies over a single enemy."""


def choose_action(turn):
    if "arena_sweep" in turn.available_move_ids:
        return turn.use("arena_sweep")
    if "arena_storm" in turn.available_move_ids:
        return turn.use("arena_storm")
    return turn.use("arena_tap", target=turn.enemies[0])
