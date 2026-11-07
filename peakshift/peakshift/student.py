"""START HERE: seven guided missions, all in one student-owned file.

Every function below is already CALLED from the game. You can work on the
missions independently and in any order. The starter remains playable.

    1. Predict what your edit should do.
    2. Change 'if False:' to 'if True:' to observe the inputs (then undo it).
    3. Write a small piece of Python where the TODO points.
    4. Play again and check your prediction.

You do NOT have to implement gravity, collisions, the camera, or the main
loop first. When you're ready, investigate those files anyway!
"""

# MISSION 0: Rename and recolor the game. RGB numbers range from 0 to 255.
GAME_TITLE = "PEAKSHIFT"
HERO_COLOR = (255, 218, 121)
SCARF_COLOR = (255, 112, 151)
SKY_COLOR = (19, 27, 52)


def collect_berry(game):
    """MISSION 1 (variables) -- Score one point for every berry collected.

    The collision engine calls this ONCE when you touch a new pink berry.
    INPUT: game.berries is your score so far (it starts at zero).

    1. Touch a berry; it disappears, but the score remains 0.
    2. Enable the diagnostic. What is game.berries before collecting?
    3. Add one to game.berries. Hint: game.berries += 1
    4. Collect two berries and check the HUD. Replay the room to retry.

    STRETCH: award 10 points instead of 1, or count the entire campaign.
    """
    if False:
        print("BERRY DEBUG: previous score", game.berries)
    # TODO(student): Increase game.berries here.
    pass


def refill_dash_from_crystal(player):
    """MISSION 2 (if/return) -- Purple crystals refill one air dash.

    INPUT: player.dashes is 0 after a dash and 1 when a dash is available.
    OUTPUT: return True ONLY when the crystal actually refilled a dash.

    1. Jump and dash through the glowing crystal in Switchbacks or Skybridge.
    2. Enable the diagnostic and observe dashes before the touch.
    3. If player.dashes == 0, set it to 1 and return True.
    4. Otherwise return False. The engine will only consume a crystal
       when you return True, so a full-dash player can save it for later.

    TEST: dash -> crystal -> dash works. A full dash skips the crystal.
    STRETCH: give a player two dashes, and change the UI to match.
    """
    if False:
        print("CRYSTAL DEBUG: dashes", player.dashes)
    # TODO(student): Add your if here and return True when it succeeds.
    return False


def move_platform(platform, seconds):
    """MISSION 3 (arithmetic/conditions) -- Make blue ledges patrol.

    The engine already draws these and carries a hero who lands on them.
    INPUTS: platform.x, direction (+1/-1), speed, left_limit, right_limit.
    seconds: real time this step (around 0.008 seconds).

    1. Find the blue bridge in Skybridge; it is stationary at first.
    2. Move it: platform.x += platform.speed * platform.direction * seconds
    3. If x is beyond right_limit, set x to that limit and direction = -1.
    4. If x is below left_limit, set x to that limit and direction = +1.
    5. Verify you can stand on it while it moves, and ride along.

    STRETCH: slow down at each edge, or vary the speed by room.
    """
    if False:
        print("PLATFORM DEBUG:", platform.x, platform.direction, seconds)
    # TODO(student): Update position, clamp, reverse at limits.
    pass


def update_crumble(block, seconds, standing):
    """MISSION 4 (timers) -- Make brown tiles break after you stand on them.

    INPUTS: block.timer (starts 0), block.broken (starts False),
    standing (True if the hero's feet are on top), seconds.
    The collision engine already stops using blocks once broken is True.

    1. Stand on a brown 'b' ledge in Lantern Ridge.
    2. If standing, increase block.timer by seconds.
    3. If block.timer > 0.45, set block.broken = True.
    4. If the hero leaves before it breaks, decide whether the timer
       should pause or return to 0. Either choice is a game-design rule.

    STRETCH: respawn the block after 2 seconds. Avoid trapping the hero.
    """
    if False and standing:
        print("CRUMBLE DEBUG:", block.timer, block.broken)
    # TODO(student): Increment the timer and change block.broken.
    pass


def wind_acceleration(player, inside_wind):
    """MISSION 5 (functions) -- Make a turquoise wind tile push right.

    INPUTS: inside_wind is True when the player overlaps a 'w' tile.
    OUTPUT: horizontal acceleration (pixels per second per second).

    1. Find the 'w' tile in Lantern Ridge. Right now it is harmless.
    2. If inside_wind: return 700.0
    3. Otherwise return 0.0. The physics engine multiplies by seconds.
    4. Compare jumping through the wind from either side.

    STRETCH: make wind push toward the room's exit instead of always right.
    """
    if False and inside_wind:
        print("WIND DEBUG: x", round(player.x), "vx", round(player.vx))
    # TODO(student): Return a push only when inside_wind is True.
    return 0.0


def record_time(game, seconds):
    """MISSION 6 (accumulators) -- Build a speedrun clock.

    INPUTS: game.elapsed (starts at 0), seconds (time since last frame).
    The HUD already displays elapsed time; it stays at 0 until this mission.

    1. Add seconds to game.elapsed each time this function is called.
    2. Test at 30 FPS and 60 FPS; does the timer keep correct time?
    3. How could you subtract time when a player dies?

    STRETCH: track a personal best per level using a dictionary.
    """
    if False:
        print("TIMER DEBUG:", round(game.elapsed, 2), round(seconds, 4))
    # TODO(student): Accumulate seconds in game.elapsed.
    pass


# MISSION 7 is in levels.py rather than here: author a new Room with P and G,
# add it to ROOMS, and connect RIDGE.next_room to your room's dictionary key.
# The map validator will tell you which row or letter needs fixing.
