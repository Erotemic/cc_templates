"""OVERWORLD LEARNING ROUTE -- facing, sprinting, and one-time interactions.

The NORMAL game already calls choose_player_view(). No mode switch is needed.
Read overworld/engine.py alongside these functions; F2 shows current state.
At first the Courier always faces down. You implement the missing directions.
Run ``python main.py --overworld`` after each change. Check one task with
``--check-exercise facing`` (or sprint/healing). Checks run YOUR code.
"""


def choose_player_view(*, facing):
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


def movement_speed(*, controls):
    """MISSION 2 -- Hold Shift to sprint. This return value is used by World.move.

    READ THE ENGINE FIRST:
      Find 'movement = direction * speed * seconds' in overworld/engine.py.
      direction chooses where; speed chooses pixels/second; seconds chooses time.
      Multiplying these gives distance for this frame, not a teleport amount.

    YOUR INPUT: controls.sprint_held is True while either Shift key is held.
    PREDICT: should releasing Shift restore normal speed on the very next frame?
    BUILD: return 230 when sprint_held is True; keep 155 as the normal fallback.
    OBSERVE: temporarily enable the print below. Do not add another key reader.
    TEST: cover more distance with Shift, release it, and try diagonal movement.
    EXPLAIN: why must this function return speed rather than modify position?
    TRANSFER: design a stamina limit in the world engine; where should it live?
    """
    if False and controls.sprint_held:
        print("SPRINT DEBUG: Shift is held")
    # TODO: check the held input and return the sprint speed.
    return 155


def warm_light(*, world, obj):
    """MISSION 3 -- Heal on entry, and report the actual HP returned.

    YOUR INPUTS:
      world.session.player: the shared Player, with hp, max_hp, and heal(amount=...).
      player.heal(amount) changes HP, clamps it, and RETURNS the actual gain.
      world.tell(text=...): show a short message in the world HUD.
      obj.definition.name: this story object's name, from its map legend.

    WALKTHROUGH:
    1. Enter the oval. Turn on the diagnostic to see HP before the effect.
    2. Store world.session.player in a variable named player.
    3. Call player.heal(amount=3) and store its returned value in healed.
       Do not assign hp = 3: that would replace health instead of adding it.
    4. Show a message with world.tell(...). Include healed in an f-string:
       f"The light restores {healed} HP." is an example expression.
    5. Test at full HP and low HP. For a temporary low-HP experiment, add
       player.hp = 5 BEFORE the heal call, test once, then REMOVE that line.
       You can also visit after taking damage in an encounter.

    TEST IT: at 5/20 HP, entry gives 8/20. Staying still gives no extra heals.
    Leave and re-enter for 11/20. At 19/20, report 1 healed; at 20/20 report 0.
    STRETCH: require a story flag, charge a snack, or heal only once per run.
    """
    if False:
        print("LIGHT DEBUG:", obj.definition.name, "HP=", world.session.player.hp)

    # TODO: heal by 3, keep the actual gain, then show it with world.tell().
    pass
