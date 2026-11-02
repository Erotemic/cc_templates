"""Student task: choose a different view for each walking direction.

Run: python main.py --sprite-task
Check your work: python main.py --check-sprites
The normal game uses the completed reference in sprites.py.
"""


def choose_player_view(facing):
    x, y = facing
    # Worked example: positive y means DOWN on a screen.
    if abs(y) >= abs(x) and y > 0:
        return "down"
    # TODO: handle UP, LEFT and RIGHT. Return one of these strings:
    # "up", "down", "left", "right".
    # Challenge: choose the strongest axis when moving diagonally.
    return "down"
