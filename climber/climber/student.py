"""GUIDED MISSIONS -- the game tells you exactly where to write code.

Start here. The game ALREADY calls each function below at the right time.
Your job is to replace its TODO with a small piece of Python. You do not
need to understand the whole project to finish a mission.

A good experiment:
  1. Run ``python main.py`` and find the unfinished feature.
  2. Choose ONE mission. Read its explanation of the inputs and outputs.
  3. Change ``if False:`` to ``if True:`` to see its diagnostic prints.
  4. Predict what should happen, write a few lines, and run the game again.
  5. Check the success example. Turn the diagnostic back off.

Useful Python ideas:
  * ``if ...:`` asks a yes/no question. Indent what should happen when true.
  * ``=`` changes a variable. ``==`` asks whether two values are equal.
  * ``return True`` or ``return False`` sends an answer to the engine.
  * ``seconds`` is the time since the previous frame. Multiply speed by it.
  * Y increases DOWN: negative vertical velocity means moving UP.
  * ``game`` stores information about the whole run; ``player`` is the hero.

The challenges in ``challenge.py`` are DIFFERENT: they give you only a goal
and a few concepts. YOU must figure out where to put the code for those.
"""

# FIRST FIVE MINUTES: change these values and launch the game again.
GAME_TITLE = "INFINITY CLIMBER"  # Rename the game!
HERO_COLOR = (80, 224, 234)  # Red, green, blue: each number is 0-255.
PLATFORM_COLOR = (122, 193, 151)
TOWER_SEED = 17  # A different whole number creates a different tower.
MUSIC_VOLUME = 0.25  # 0.0 = silent, 1.0 = loud. Press M to mute in-game.


def try_wall_jump(player, jump_pressed):
    """MISSION 1 -- Wall jump off the left or right tower wall.

    YOUR INPUTS:
      jump_pressed: True when the jump key was pressed THIS frame.
      player.on_ground: True if the player is standing on something.
      player.wall_side: -1 at the left wall, +1 at the right, 0 elsewhere.
      player.vx: sideways speed; player.vy: vertical speed.

    WALKTHROUGH:
    1. Jump into a side wall, hold toward the wall, then press jump again.
       Watch the diagnostic values: wall_side should be -1 or +1.
    2. Create an ``if`` asking ALL THREE questions:
         Was jump pressed? Are we NOT on the ground? Are we touching a wall?
       For the last question, ``player.wall_side != 0`` means touching.
    3. Inside that ``if``, change player.vy to a NEGATIVE value (try -690).
    4. Push AWAY from the wall. The sign of ``-player.wall_side`` gives
       the opposite direction; multiply it by about 360 for player.vx.
    5. Return True INSIDE your successful branch. Otherwise return False.
       This matters: the engine uses True to preserve the sideways push.

    TEST IT: jump off BOTH walls. Pressing jump in the middle of the air
    should do nothing. Jumping normally from the ground should still work.
    STRETCH: grant one extra midair jump after a successful wall jump.
    """
    if False and jump_pressed:
        print("WALL DEBUG:", "wall_side=", player.wall_side,
              "on_ground=", player.on_ground, "vy=", round(player.vy))

    # TODO 1: Add an if statement with the three conditions.
    # TODO 2: Inside it, assign player.vy and player.vx, then return True.
    return False  # Nothing happened yet; keep this for unsuccessful attempts.


def update_ladder_state(player, controls, touching_ladder):
    """MISSION 2 -- Make W and S climb ladders instead of falling.

    YOUR INPUTS:
      touching_ladder: a True/False collision check the engine already did.
      controls.up: W or Up Arrow is held.
      controls.down: S or Down Arrow is held.
      player.climbing: the True/False state YOU must set.

    WALKTHROUGH:
    1. Stand under or beside a visible ladder and turn on the diagnostic.
       Compare touching_ladder when close and when far away.
    2. Think of the start rule: a player can climb only if touching a
       ladder AND holding an up/down key. (Use ``and`` and ``or``.)
    3. Set player.climbing to True when that condition is met.
    4. Set player.climbing to False otherwise. A plain ``else:`` is fine.
    5. You do NOT need to move the player vertically here. The engine
       already does that whenever player.climbing is True.

    TEST IT: W climbs upward, S climbs downward; W without a ladder does
    nothing. Walking away from the ladder makes you fall again.
    STRETCH: once you grab a ladder, hang on without holding W or S.
    """
    if False and (controls.up or controls.down):
        print("LADDER DEBUG:", "touching=", touching_ladder,
              "up=", controls.up, "down=", controls.down,
              "climbing=", player.climbing)

    # TODO 1: Make an if/else for touching_ladder and the movement keys.
    # TODO 2: Set player.climbing to True in one branch, False in the other.
    player.climbing = False  # Starter: ladders are decorations for now.


def move_enemy(enemy, seconds):
    """MISSION 3 -- Make a pink enemy patrol from left to right and back.

    YOUR INPUTS:
      enemy.x: its current horizontal position (this is what you change).
      enemy.direction: +1 goes right, -1 goes left.
      enemy.speed: distance per SECOND, not per frame.
      enemy.left_limit / enemy.right_limit: where its x is allowed to go.
      seconds: duration of this frame (about 0.017 at 60 FPS).

    WALKTHROUGH:
    1. Turn on the diagnostic and look at x, speed, and direction.
    2. Move x every frame: enemy.x += enemy.direction * enemy.speed * seconds
       First try ONLY this line. What happens after a few seconds?
    3. If enemy.x >= enemy.right_limit, set direction to -1 (turn left).
    4. If enemy.x <= enemy.left_limit, set direction to +1 (turn right).
    5. If it moved past a limit, also put it exactly on that limit.
       This is called CLAMPING; it prevents drift and edge jitter.

    TEST IT: it reverses at both ends, never leaves its platform, and
    still moves at about the same rate even when FPS changes.
    STRETCH: have the creature pause at an edge before turning around.
    """
    if False:
        print("ENEMY DEBUG:", "x=", round(enemy.x),
              "direction=", enemy.direction, "seconds=", round(seconds, 3))

    # TODO: change enemy.x, then check both limits and reverse direction.
    pass  # Python's way to say "I haven't added code here yet."


def move_rising_floor(game, seconds):
    """MISSION 4 -- Make the purple danger rise below the player.

    YOUR INPUTS:
      game.hazard_y: world Y position of the dangerous purple line.
      game.player.bottom: Y of the player's feet.
      seconds: elapsed time this frame.

    WALKTHROUGH:
    1. Turn on the diagnostic. A SMALLER world Y is HIGHER in the tower.
    2. Try subtracting 20 * seconds from game.hazard_y on every frame.
       This moves the line up at 20 pixels per second, not per frame.
    3. Play for a few seconds, then stand still. What happens when the
       line passes the player's feet? The engine already handles the reset.
    4. Experiment with the speed. Choose a value that feels fair.
    5. OPTIONAL rubber-band version: calculate the gap between the
       player's feet and the line. Change speed based on that gap.

    TEST IT: the danger advances while time passes, and touching it
    restarts the run. The player should have a chance to escape.
    STRETCH: make the line speed up after a milestone or pause at checkpoints.
    """
    if False:
        print("FLOOR DEBUG:", "hazard_y=", round(game.hazard_y),
              "player_y=", round(game.player.y))

    # TODO: update game.hazard_y using seconds.
    pass  # Starter: the danger does not rise until you add this.


def move_platform(platform, seconds):
    """MISSION 5 -- Make the blue platforms glide left and right.

    The platform is ALREADY drawn and solid. The engine also carries the
    player if its x changes while they are standing on it.

    YOUR INPUTS:
      platform.x: left edge of the platform; THIS is what you change.
      platform.speed: pixels per second; platform.direction: +1 or -1.
      platform.left_limit / platform.right_limit: allowed range for x.

    WALKTHROUGH:
    1. Find a blue ledge with arrows (the first is near tower tier 2).
    2. Turn on the print. Notice x and its two limits.
    3. Try moving x by platform.direction * platform.speed * seconds.
       Run the game with just that line: does it stop at the edge?
    4. On reaching the right limit, set direction to -1 and clamp x.
    5. On reaching the left limit, set direction to +1 and clamp x.
    6. Stand on it and RELEASE the movement keys. You should ride along.

    TEST IT: it stays inside its limits, turns at both ends, and carries
    the player. Jumping off should stop the automatic horizontal carrying.
    STRETCH: pause at the ends, change speed, or try vertical platforms.
    """
    if False:
        print("PLATFORM DEBUG:", "tier=", platform.tier,
              "x=", round(platform.x), "left=", round(platform.left_limit),
              "right=", round(platform.right_limit),
              "direction=", platform.direction)

    # TODO: update platform.x, clamp to the limits, and change direction.
    pass


def platform_height_offset(tier, noise):
    """MISSION 6 -- Give tower ledges DIFFERENT heights using noise.

    YOUR INPUTS:
      tier: which ledge is being generated (1, 2, 3, ... forever).
      noise: a reproducible number between about -1 and +1.
    YOUR OUTPUT: return the height OFFSET for this tier, in pixels.
      0.0 means the normal height; a negative number raises the ledge.

    WALKTHROUGH:
    1. Turn on the diagnostic for the first eight tiers. Look at noise.
    2. Right now the function returns 0.0. That puts every ledge exactly
       100 pixels above the previous one.
    3. Try returning 16 * noise. Look for different vertical gaps.
    4. Test jumps between neighboring ledges. You can jump around 159 px
       vertically, so keep height changes fairly small (about +/-20 px).
    5. Visit a tier, move far away, and come back. It MUST be at the same
       place every time. Don't use random.random() here on each call.
    6. Want more? Explore horizontal platform placement and side routes in
       the tower generator. Keep at least one reachable path upward.

    TEST IT: gaps vary without creating impossible jumps or shifting old
    ledges when the camera moves. Even tier 1,000,000 should generate quickly.
    STRETCH: give the tower regions with different but repeatable patterns.
    """
    if False and tier <= 8:
        print("HEIGHT DEBUG:", "tier=", tier, "noise=", round(noise, 2))

    # TODO: return a small multiple of noise instead of 0.0.
    return 0.0


def collect_pickup(game, pickup):
    """MISSION 7 -- Decide what happens when the player touches treasure.

    Placement, collision detection, art, and sound are ALREADY working.
    This function runs while the player overlaps an uncollected pickup.

    YOUR INPUTS:
      pickup.collected: True means the item has been taken and disappears.
      pickup.kind: e.g. "gem" or "heart".
      game.pickups_collected: number shown in the HUD.
      game.hearts: health; normally between 0 and 3.

    WALKTHROUGH:
    1. Turn on the print, climb to an item, and touch it. Notice that the
       debug message may repeat. Why doesn't the item disappear yet?
    2. Set pickup.collected to True. This stops it from being collected
       again and makes the drawing code stop showing it.
    3. Increase game.pickups_collected by 1. (``+= 1`` is a shortcut.)
    4. Try giving a reward: game.hearts = min(3, game.hearts + 1)
       Why do we use min(3, ...)?
    5. OPTIONAL: choose rewards using pickup.kind.

    TEST IT: one collision gives exactly one reward, even if you keep
    standing in the same place. The item vanishes and the counter changes.
    STRETCH: make several different collectibles with different rules.
    """
    if False:
        print("PICKUP DEBUG:", "tier=", pickup.tier,
              "kind=", pickup.kind, "already=", pickup.collected,
              "count=", game.pickups_collected)

    # TODO: mark collected, increase the count, and choose a reward.
    pass


def heckler_line(game, heckler):
    """BONUS -- Change the elevator heckler's regular dialogue.

    This function already WORKS. It returns a string (text to say) based
    on the player's progress. The engine handles typing and mumble sounds.

    Try changing ONE phrase first. Then add an ``if`` that checks a game
    value such as highest_tier, failures, or pickups_collected. Conditions
    are checked TOP TO BOTTOM: the first matching ``return`` wins.

    TEST IT: a different line appears after the event you chose, but
    it doesn't reappear continuously while the player stands still.
    """
    if game.failures >= 3:
        return "Gravity still undefeated."
    if game.highest_tier >= 30:
        return "Thirty floors? I am shocked."
    if game.highest_tier >= 20:
        return "Twenty down. A tiny warm-up."
    if game.highest_tier >= 10:
        return "Wow, 10! Only ALL of them to go!"
    if game.pickups_collected >= 3:
        return "Treasure first, victory later?"
    return "I ride. You climb."


def update_heckler_comeback(game, heckler):
    """MISSION 8 -- REMEMBER a fall, then react when the player returns.

    This function runs EVERY FRAME. YOU own both detection and reaction.
    The engine does NOT secretly detect a fall or a reunion for you.

    MEMORY PROVIDED BY THE ENGINE (you must update these fields):
      game.peak_player_y: highest Y reached so far (smaller = higher).
      game.comeback_pending: True means a fall is remembered.
      game.comeback_peak_y: where the player must return after a fall.
      game.fall_count: number of significant falls detected.

    PART A -- DETECT NOW AND SAVE STATE:
    1. Update peak_player_y to the smaller of the previous peak and the
       player's current Y. (Python hint: min(..., ...).)
    2. Find the DROP by subtracting peak_player_y from game.player.y.
    3. If the drop is >= 180 AND comeback_pending is False, remember it:
       set comeback_pending True, save the peak into comeback_peak_y,
       and add 1 to fall_count. This should happen only ONCE per fall.
    4. Test a big fall without returning. Pending should stay True, and
       the heckler must NOT say "You're back" yet.

    PART B -- WAIT AND REACT LATER:
    5. On later frames, check if comeback_pending is True AND the player
       climbed back near the remembered height:
           game.player.y <= game.comeback_peak_y + 35
       You can also require being near heckler.y (the elevator's height).
    6. When both are true, set comeback_pending False (consume the memory)
       and return heckler_comeback_line(game, heckler). The engine will
       type and voice whatever string you returned.
    7. Return None on all frames when no new dialogue should be triggered.

    TEST IT THREE WAYS:
      - Jump normally: no remembered fall and no comeback line.
      - Fall two or more floors: pending becomes True, no speech yet.
      - Climb back up: one comeback line, then silence until another fall.

    WHY: an ``if`` checks what's true NOW; a saved flag remembers something
    that happened BEFORE. Clearing it prevents repeated triggers.
    """
    if False:
        print("COMEBACK DEBUG:",
              "player_y=", round(game.player.y),
              "peak_y=", round(game.peak_player_y),
              "pending=", game.comeback_pending,
              "remembered_y=", round(game.comeback_peak_y),
              "heckler_y=", round(heckler.y),
              "falls=", game.fall_count)

    # TODO A: update peak_player_y; detect a large drop and save a flag.
    # TODO B: only when the player returns, CLEAR the flag and return a line.
    return None  # Default: no new dialogue event this frame.


def heckler_comeback_line(game, heckler):
    """BONUS -- Write the joke spoken AFTER completing mission 8.

    This does not create the event! Only update_heckler_comeback() can
    decide when the heckler should say this. Change the string below or
    branch on game.fall_count to mock the second, third, etc. comeback.
    """
    return "You're back? Did you enjoy the express route down?"
