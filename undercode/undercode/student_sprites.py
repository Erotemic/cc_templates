"""GUIDED MISSION 1 -- Make the Courier look where they are walking.

The NORMAL game already calls choose_player_view(). No mode switch is needed.
At first the Courier always faces down. You implement the missing directions.
Run ``python main.py`` after each small change, then ``--check-sprites``.
"""


def choose_player_view(facing):
    """Return the name of the view to draw: 'up', 'down', 'left', or 'right'.

    YOUR INPUT:
      facing: (x, y), the last direction the player tried to walk.
      x < 0 is left, x > 0 is right; y < 0 is up, y > 0 is down.
      The world remembers facing when you stop. You do not need a new timer,
      position, key reader, or saved variable here.

    WALKTHROUGH:
    1. Walk LEFT in the normal game. Notice the face still looks DOWN.
       Turn on the diagnostic below; compare x and y in all four directions.
    2. Handle one direction first: ask whether x is negative. If so,
       return 'left'. Run again. Did walking left gain a new view?
    3. Add right and up cases. Positive y can use the final 'down' return.
       Test each change in the game rather than writing everything at once.
    4. Now hold two directions. Decide which axis is stronger using abs(x)
       and abs(y). Only use left/right when abs(x) > abs(y); otherwise use y.
       This makes equal-strength diagonals choose a vertical view.
    5. Keep the final 'down' fallback for (0, 0). Run --check-sprites.
       All eight cases should pass when the function is complete.

    TEST IT: walk in four directions, diagonally, then release the keys.
    Facing a wall should change the view even if the player cannot move.
    STRETCH: customize the four drawings in art.courier, or add walk frames.
    """
    x, y = facing
    if False:  # Change to True briefly; turn it off after inspecting the values.
        print("VIEW DEBUG:", "x=", round(x, 2), "y=", round(y, 2))

    # TODO 1: Return 'left', 'right', and 'up' in the appropriate cases.
    # TODO 2: Choose the stronger axis for diagonals (ties use vertical).
    return "down"  # Starter: one front view until you implement the other cases.
