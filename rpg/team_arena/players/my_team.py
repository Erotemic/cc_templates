"""My Team: the student starter controller. Edit only this function first.

Play it:       python arena.py battle my_team first_target --log
Improve it:    python arena.py challenge my_team
The same function controls BOTH of your team's characters. They have different
moves; check turn.available_move_ids before trying a character-specific move.
"""


def choose_action(turn):
    # Choose one action for the character whose turn it is.
    # Start by changing the target, then try a conditional or a different move.
    return turn.use("arena_tap", target=turn.enemies[0])
